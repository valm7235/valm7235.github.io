#!/usr/bin/env python3
"""
Bot Telegram pour HF Spaces (port 7860 partagé avec kimi-proxy).
Mode WEBHOOK : Telegram pousse vers /webhook/{secret}.

Supporte : texte, vocaux (transcription Google), fichiers, photos.
Réponse inline en ~10-35s. Fallback GitHub Actions si > 50s.
"""
import asyncio
import base64
import hashlib
import json
import logging
import os
import re
import subprocess

import httpx
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
GITHUB_REPO = os.environ.get("GITHUB_REPO", "valm7235/claudecode-CLI-kimi")
TELEGRAM_RELAY_REPO = os.environ.get("TELEGRAM_RELAY_REPO", "")  # repo with telegram-relay.yml
HF_TOKEN = os.environ.get("HF_TOKEN", "")
HF_SPACE = "vmu7235/claudecode-kimi"
HF_SPACE_URL = "https://vmu7235-claudecode-kimi.hf.space"
HF_GIT = f"https://vmu7235:{HF_TOKEN}@huggingface.co/spaces/{HF_SPACE}" if HF_TOKEN else \
          "https://huggingface.co/spaces/vmu7235/claudecode-kimi"
SESSIONS_FILE = "/data/sessions.json"
WORK_DIR = "/data/workspace"
INLINE_TIMEOUT = 50.0
SUBPROCESS_TIMEOUT = 180  # fallback run_claude (sans transcript)
TRANSCRIPT_TIMEOUT = 600  # max 10 min avec live transcript (Popen)
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

# Verrous par chat_id : empêche 2 subprocess concurrents pour le même utilisateur
# (sinon corruption de session + double appel Kimi → quota gaspillé)
_chat_locks: dict[int, asyncio.Lock] = {}

def _get_chat_lock(chat_id: int) -> asyncio.Lock:
    if chat_id not in _chat_locks:
        _chat_locks[chat_id] = asyncio.Lock()
    return _chat_locks[chat_id]

WEBHOOK_SECRET = hashlib.sha256(TELEGRAM_TOKEN.encode()).hexdigest()[:32] if TELEGRAM_TOKEN else "no-token"

CLAUDE_ENV = {
    **os.environ,
    "ANTHROPIC_BASE_URL": "http://localhost:7860",
    "ANTHROPIC_API_KEY": "kimi-proxy-key",
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
    "HOME": "/home/claudebot",
    "PATH": "/usr/local/bin:/usr/bin:/bin",
    "HF_SPACE": HF_SPACE,
    "HF_SPACE_URL": HF_SPACE_URL,
    "HF_GIT": HF_GIT,
    "GITHUB_REPO": GITHUB_REPO,
    "BOT_WORK_DIR": WORK_DIR,
    "BOT_REPO_DIR": "/data/repo",
}

os.makedirs(WORK_DIR, exist_ok=True)


def _setup_bot_workspace():
    """Write CLAUDE.md self-knowledge + configure git for claudebot."""
    hf_git_url = HF_GIT
    gh_token = GITHUB_TOKEN
    gh_repo = GITHUB_REPO

    claude_md = f"""# 🤖 Tu es Claude Code CLI — Bot Telegram hébergé sur HuggingFace

## Identité
- **Rôle** : Assistant IA accessible via Telegram, propulsé par Claude Code CLI
- **Modèle LLM** : claude-sonnet-4-6 (proxié vers Kimi K2.5 de Moonshot AI)
- **Interface** : Bot Telegram @claudecodeclicloud (webhook)

---

## Où tu es hébergé
| Ressource | Valeur |
|-----------|--------|
| HuggingFace Space | `{HF_SPACE}` |
| URL publique | `{HF_SPACE_URL}` |
| Git HF (pour te modifier) | `{hf_git_url}` |
| GitHub relay | `https://github.com/{gh_repo}` |
| Webhook Telegram | `{HF_SPACE_URL}/webhook/{WEBHOOK_SECRET[:8]}...` |

---

## Architecture complète

```
[Utilisateur Telegram]
       │ message texte/vocal/fichier
       ▼
[HuggingFace Space :7860]  ← Docker container (python:3.11-slim)
       │ POST /webhook/{{secret}}
       ▼
[kimi-proxy.py + telegram_bot.py]  ← FastAPI, user=claudebot
       │ subprocess (stdin=DEVNULL, cwd=/data/workspace)
       ▼
[Claude Code CLI]  ← @anthropic-ai/claude-code (npm global)
       │ Anthropic API → ANTHROPIC_BASE_URL=http://localhost:7860
       ▼
[kimi-proxy.py /v1/messages]  ← Proxy Anthropic→OpenAI format
       │ POST https://api.moonshot.ai/v1/chat/completions
       ▼
[Kimi K2.5 API]  ← modèle Moonshot AI
       │ réponse texte
       ▼
[Telegram API]  ← envoi au chat utilisateur
```

---

## Fichiers importants (dans le container)
| Fichier | Rôle |
|---------|------|
| `/app/telegram_bot.py` | Bot Telegram, webhook, gestion sessions, run_claude() |
| `/app/kimi-proxy.py` | Proxy Anthropic→Kimi, conversion formats, port 7860 |
| `/app/watcher.py` | Watchdog supervisord |
| `/app/supervisord.conf` | Configuration des processus |
| `/app/Dockerfile` | Image Docker |
| `/data/sessions.json` | Sessions Telegram persistantes (par chat_id) |
| `/data/workspace/` | Ton répertoire de travail (WORK_DIR) |
| `/data/repo/` | Clone du repo HF (pour auto-modifications) |
| `/home/claudebot/.claude/settings.json` | Permissions Claude CLI |
| `/home/claudebot/.claude/skills/` | 28 skills markdown |

---

## Variables d'environnement disponibles
```bash
ANTHROPIC_BASE_URL=http://localhost:7860    # proxy Kimi local
ANTHROPIC_API_KEY=kimi-proxy-key           # clé du proxy
KIMI_API_KEY=<secret HF>                   # clé Moonshot AI
TELEGRAM_TOKEN=<secret HF>                 # token bot Telegram
GITHUB_TOKEN=<secret HF>                   # token GitHub relay
HF_TOKEN=<secret HF>                       # token HuggingFace
HF_SPACE={HF_SPACE}
HF_SPACE_URL={HF_SPACE_URL}
HF_GIT={hf_git_url}
GITHUB_REPO={gh_repo}
BOT_REPO_DIR=/data/repo
```

---

## Comment te modifier toi-même (auto-modification)

### Étape 1 — Cloner le repo HF (une seule fois)
```bash
git clone {hf_git_url} /data/repo
cd /data/repo
git config user.email "claudebot@hf.space"
git config user.name "Claude Code Bot"
```

### Étape 2 — Modifier les fichiers
```bash
# Exemple: modifier kimi-proxy.py
nano /data/repo/kimi-proxy.py
# ou
Edit /data/repo/kimi-proxy.py
```

### Étape 3 — Commit et push (déclenche un rebuild HF automatique)
```bash
cd /data/repo
git add -A
git -c commit.gpgsign=false commit -m "fix: description de la modification"
git push origin main
# HuggingFace rebuild en 3-5 minutes
```

### Étape 4 — Vérifier le déploiement
```bash
curl -s {HF_SPACE_URL}/health
# doit retourner: {{"status":"ok","proxy":"Kimi K2.5","port":7860}}
```

---

## Modifier le repo GitHub relay
```bash
git clone https://{gh_token}@github.com/{gh_repo} /data/gh-repo
cd /data/gh-repo
# ... modifications ...
git -c commit.gpgsign=false commit -m "feat: ..."
git push origin main
```

---

## Commandes supervisord (gestion des processus)
```bash
supervisorctl status           # état des processus
supervisorctl restart all      # redémarrer tout
supervisorctl restart kimi-proxy  # redémarrer le proxy/bot
```

---

## Limites importantes
- `--dangerously-skip-permissions` : interdit en root → tu tournes comme `claudebot` (OK)
- `/data/` : **persistant** entre restarts et rebuilds
- `/app/` : **réinitialisé** au rebuild (depuis le repo HF)
- DNS `api.telegram.org` : parfois saturé en HF Space → bypass via IPs connues
- Kimi K2.5 : reasoning interne obligatoire → min 2048 max_tokens

---

## Répertoire de travail actuel
- `{WORK_DIR}` (WORK_DIR) — tu lis/écris ici par défaut
- Repo HF cloné : `/data/repo/` (à créer si besoin avec git clone ci-dessus)
"""

    claude_md_path = os.path.join(WORK_DIR, "CLAUDE.md")
    try:
        with open(claude_md_path, "w") as f:
            f.write(claude_md)
        logger.info(f"CLAUDE.md written to {claude_md_path}")
    except Exception as e:
        logger.warning(f"Could not write CLAUDE.md: {e}")

    # Configure git credentials for claudebot
    gitconfig = f"""[user]
    name = Claude Code Bot
    email = claudebot@hf.space
[credential]
    helper = store
[safe]
    directory = *
[commit]
    gpgsign = false
"""
    try:
        with open("/home/claudebot/.gitconfig", "w") as f:
            f.write(gitconfig)
        cred_line = f"https://vmu7235:{HF_TOKEN}@huggingface.co\n"
        if gh_token:
            cred_line += f"https://{gh_token}@github.com\n"
        with open("/home/claudebot/.git-credentials", "w") as f:
            f.write(cred_line)
        os.chmod("/home/claudebot/.git-credentials", 0o600)
        logger.info("Git credentials configured for claudebot")
    except Exception as e:
        logger.warning(f"Could not write git config: {e}")


_setup_bot_workspace()

router = APIRouter()

TG_API = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
TG_FILE = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}"

# IPs Telegram connues (bypass DNS si api.telegram.org ne se résout pas)
_TG_IPS = ["149.154.175.52", "149.154.167.50", "91.108.56.130", "149.154.175.100"]
_tg_ip_cache: str = ""


def _get_tg_ip() -> str:
    """Résout api.telegram.org ou retourne une IP connue fonctionnelle."""
    global _tg_ip_cache
    if _tg_ip_cache:
        return _tg_ip_cache
    import socket as _s
    for ip in [None] + _TG_IPS:
        try:
            if ip is None:
                ip = _s.gethostbyname("api.telegram.org")
            with _s.create_connection((ip, 443), timeout=5):
                _tg_ip_cache = ip
                logger.info(f"Telegram IP: {ip}")
                return ip
        except Exception:
            continue
    _tg_ip_cache = _TG_IPS[0]
    return _tg_ip_cache


def _tg_raw_get(path: str, timeout: int = 20) -> bytes:
    """GET HTTPS sur api.telegram.org via IP directe (bypass DNS)."""
    import socket as _s, ssl as _ssl
    ip = _get_tg_ip()
    ctx = _ssl.create_default_context()
    req = f"GET {path} HTTP/1.1\r\nHost: api.telegram.org\r\nConnection: close\r\n\r\n".encode()
    with _s.create_connection((ip, 443), timeout=timeout) as sock:
        sock.settimeout(timeout)
        with ctx.wrap_socket(sock, server_hostname="api.telegram.org") as ssock:
            ssock.sendall(req)
            buf = b""
            while True:
                try:
                    chunk = ssock.recv(65536)
                    if not chunk:
                        break
                    buf += chunk
                except _ssl.SSLError:
                    break
    _, _, body = buf.partition(b"\r\n\r\n")
    return body


def _tg_post_sync(method: str, payload: dict, timeout: int = 15) -> dict:
    """POST to Telegram API. Essaie httpx (DNS standard) puis raw socket avec rotation IP."""
    import json as _json

    # Méthode 1 : httpx (préféré, gère DNS+SSL+keep-alive proprement)
    try:
        with httpx.Client(timeout=timeout, verify=True) as client:
            r = client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/{method}",
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            return r.json()
    except Exception as e1:
        logger.debug(f"_tg_post_sync httpx fail: {type(e1).__name__}: {str(e1)[:100]}")

    # Méthode 2 : raw socket avec rotation IP (bypass DNS si saturé)
    import socket as _s, ssl as _ssl
    global _tg_ip_cache
    body = _json.dumps(payload).encode()
    req = (
        f"POST /bot{TELEGRAM_TOKEN}/{method} HTTP/1.1\r\n"
        f"Host: api.telegram.org\r\n"
        f"Content-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: close\r\n\r\n"
    ).encode() + body

    candidates = []
    if _tg_ip_cache:
        candidates.append(_tg_ip_cache)
    for ip in _TG_IPS:
        if ip not in candidates:
            candidates.append(ip)

    last_err = "no IP worked"
    for ip in candidates:
        try:
            ctx = _ssl.create_default_context()
            with _s.create_connection((ip, 443), timeout=timeout) as sock:
                sock.settimeout(timeout)
                with ctx.wrap_socket(sock, server_hostname="api.telegram.org") as ssock:
                    ssock.sendall(req)
                    buf = b""
                    while True:
                        try:
                            chunk = ssock.recv(65536)
                            if not chunk:
                                break
                            buf += chunk
                        except _ssl.SSLError:
                            break
            _, _, resp_body = buf.partition(b"\r\n\r\n")
            try:
                result = _json.loads(resp_body)
                _tg_ip_cache = ip  # cache l'IP qui fonctionne
                return result
            except Exception as ep:
                last_err = f"parse error from {ip}: {ep}"
                continue
        except Exception as e:
            last_err = f"{ip}: {type(e).__name__}: {str(e)[:80]}"
            # Si c'est l'IP cachée qui échoue, on l'invalide
            if ip == _tg_ip_cache:
                _tg_ip_cache = ""
            continue

    return {"ok": False, "description": last_err}


def _split_message(text: str, limit: int = 4000) -> list[str]:
    """Split long text into Telegram-sized chunks, preferring line breaks."""
    if len(text) <= limit:
        return [text]
    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        # Find last newline within limit
        cut = text.rfind('\n', 0, limit)
        if cut < limit // 2:
            cut = limit
        chunks.append(text[:cut])
        text = text[cut:].lstrip('\n')
    return chunks


def _send_typing_sync(chat_id: int) -> None:
    """Envoie l'action 'typing...' en fire-and-forget (3s d'animation côté Telegram)."""
    if not TELEGRAM_TOKEN:
        return
    try:
        _tg_raw_get(f"/bot{TELEGRAM_TOKEN}/sendChatAction?chat_id={chat_id}&action=typing", timeout=5)
    except Exception as e:
        logger.debug(f"sendChatAction failed (non-bloquant): {e}")


async def send_typing(chat_id: int) -> None:
    """Async wrapper non-bloquant pour le typing indicator."""
    loop = asyncio.get_event_loop()
    try:
        await asyncio.wait_for(
            loop.run_in_executor(None, lambda: _send_typing_sync(chat_id)),
            timeout=5.0
        )
    except Exception:
        pass


# ─── Sessions ─────────────────────────────────────────────────────────────────

def load_sessions() -> dict:
    if os.path.exists(SESSIONS_FILE):
        try:
            with open(SESSIONS_FILE) as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_session(chat_id: int, session_id: str):
    sessions = load_sessions()
    sessions[str(chat_id)] = session_id
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f)


def get_session(chat_id: int) -> str | None:
    return load_sessions().get(str(chat_id))


def delete_session(chat_id: int):
    sessions = load_sessions()
    sessions.pop(str(chat_id), None)
    with open(SESSIONS_FILE, "w") as f:
        json.dump(sessions, f)


# ─── Téléchargement fichiers Telegram (via httpx — SSL fiable) ────────────────

def _download_file_sync(file_id: str, filename: str) -> str | None:
    """Télécharge un fichier Telegram via bypass DNS (IPs directes). Retourne chemin local ou None."""
    import json as _json
    try:
        # 1. getFile via raw socket (bypass DNS)
        token_path = f"/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}"
        body = _tg_raw_get(token_path, timeout=20)
        data = _json.loads(body)
        if not data.get("ok"):
            logger.error(f"getFile failed: {data.get('description', data)}")
            return None
        file_info = data["result"]
        if file_info.get("file_size", 0) > MAX_FILE_SIZE:
            logger.warning(f"File too large: {file_info.get('file_size')} bytes")
            return None

        # 2. Chemin local
        safe = "".join(c for c in filename if c.isalnum() or c in "._- ")[:100] or "file"
        local_path = os.path.join(WORK_DIR, safe)

        # 3. Télécharge le contenu via raw socket
        dl_path = f"/file/bot{TELEGRAM_TOKEN}/{file_info['file_path']}"
        content = _tg_raw_get(dl_path, timeout=60)
        with open(local_path, "wb") as f:
            f.write(content)

        logger.info(f"Downloaded: {filename} → {local_path} ({len(content)} bytes)")
        return local_path

    except Exception as e:
        logger.error(f"Download error for {filename}: {e}", exc_info=True)
        # Reset IP cache pour forcer re-résolution au prochain essai
        global _tg_ip_cache
        _tg_ip_cache = ""
        return None


def _transcribe_ogg(ogg_path: str) -> tuple[str, str]:
    """
    Convertit OGG Opus → WAV, transcrit via Google Speech Recognition.
    Retourne (texte_transcrit, message_erreur).
    """
    wav_path = ogg_path.rsplit(".", 1)[0] + ".wav"
    try:
        from pydub import AudioSegment
        logger.info(f"Converting {ogg_path} to WAV...")
        AudioSegment.from_file(ogg_path).export(wav_path, format="wav")
        logger.info(f"Conversion OK → {wav_path}")
    except Exception as e:
        logger.error(f"pydub conversion error: {e}", exc_info=True)
        return "", f"Conversion audio échouée: {e}"

    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
        logger.info("Calling Google Speech Recognition...")
    except Exception as e:
        logger.error(f"SR init error: {e}", exc_info=True)
        return "", f"Init Speech Recognition échoué: {e}"

    # Essaie français, puis anglais, puis auto
    for lang in ["fr-FR", "en-US", None]:
        try:
            if lang:
                text = recognizer.recognize_google(audio_data, language=lang)
            else:
                text = recognizer.recognize_google(audio_data)
            logger.info(f"Transcription OK ({lang}): '{text[:80]}'")
            for f in [wav_path, ogg_path]:
                try: os.remove(f)
                except: pass
            return text.strip(), ""
        except sr.UnknownValueError:
            logger.warning(f"No speech detected for lang={lang}")
            continue
        except sr.RequestError as e:
            logger.error(f"Google SR request error: {e}")
            return "", f"Google Speech Recognition indisponible: {e}"
        except Exception as e:
            logger.error(f"SR error lang={lang}: {e}")
            continue

    for f in [wav_path, ogg_path]:
        try: os.remove(f)
        except: pass
    return "", "Aucune parole détectée. Parle plus clairement et plus fort."


def _download_and_transcribe(file_id: str) -> tuple[str, str]:
    """Télécharge un vocal Telegram et le transcrit. Retourne (texte, erreur)."""
    logger.info(f"Downloading voice file_id={file_id}")
    local_path = _download_file_sync(file_id, "voice.oga")
    if not local_path:
        return "", "Téléchargement du vocal échoué (vérifier la connexion au serveur Telegram)."
    return _transcribe_ogg(local_path)


# ─── Claude CLI ───────────────────────────────────────────────────────────────

def find_claude() -> str:
    import shutil
    return shutil.which("claude", path="/usr/local/bin:/usr/bin:/bin") or "claude"


def clean_response(text: str) -> str:
    """Retire les descriptions d'outils [Tool X: {...}] du texte de réponse."""
    if not text:
        return ""
    lines = text.split('\n')
    cleaned = [line for line in lines if not re.match(r'^\s*\[Tool \w+:', line)]
    return '\n'.join(cleaned).strip()


def parse_claude_stdout(stdout: str, fallback_session: str | None) -> tuple[str, str | None]:
    """Extrait (result, session_id) depuis stdout de Claude CLI (stream-json ou json)."""
    lines = [l.strip() for l in stdout.strip().split('\n') if l.strip().startswith('{')]
    # Priorité: ligne avec type=result (event final)
    for line in reversed(lines):
        try:
            data = json.loads(line)
            if data.get('type') == 'result' and 'result' in data:
                return clean_response(data['result'].strip()), data.get('session_id', fallback_session)
        except json.JSONDecodeError:
            continue
    # Fallback: toute ligne avec 'result'
    for line in reversed(lines):
        try:
            data = json.loads(line)
            if 'result' in data and data.get('type') != 'tool':
                return clean_response(data['result'].strip()), data.get('session_id', fallback_session)
        except json.JSONDecodeError:
            continue
    return clean_response(stdout.strip()), fallback_session


_API_ERROR_PATTERNS = [
    # (regex à chercher dans stdout/stderr, message user-friendly)
    (re.compile(r"exceeded_current_quota_error|insufficient[_ ]balance", re.I),
     "💳 Le compte Moonshot AI (Kimi) n'a plus de crédit. Recharge sur https://platform.moonshot.cn ou patiente."),
    (re.compile(r"rate.?limit|429", re.I),
     "⏳ Limite de requêtes Moonshot atteinte. Réessaie dans 30-60 secondes."),
    (re.compile(r"\b401\b|invalid[_ ]api[_ ]key|unauthorized", re.I),
     "🔑 Clé API Moonshot invalide. Vérifie le secret KIMI_API_KEY."),
    (re.compile(r"\b502\b|\b503\b|\b504\b|server.?error|service.?unavailable", re.I),
     "🛠️ Moonshot AI est temporairement indisponible. Réessaie dans 1-2 minutes."),
    (re.compile(r"context_length|too.?many.?tokens|maximum.?context", re.I),
     "📏 Conversation trop longue. Envoie /reset pour repartir à zéro."),
]


def _friendly_api_error(raw: str) -> str | None:
    """Transforme un dump JSON d'erreur Claude CLI en message lisible (ou None si non reconnu)."""
    for pattern, friendly in _API_ERROR_PATTERNS:
        if pattern.search(raw):
            return friendly
    return None


def run_claude(user_message: str, session_id: str | None, _retried: bool = False) -> tuple[str, str | None]:
    cmd = [find_claude(), "--print", "--dangerously-skip-permissions",
           "--model", "claude-sonnet-4-6", "--output-format", "json"]
    if session_id:
        cmd += ["--resume", session_id]
    cmd.append(user_message)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                stdin=subprocess.DEVNULL,
                                timeout=SUBPROCESS_TIMEOUT, cwd=WORK_DIR, env=CLAUDE_ENV)
    except subprocess.TimeoutExpired:
        logger.warning(f"Claude CLI timeout après {SUBPROCESS_TIMEOUT}s (session={session_id})")
        return (f"⏰ Réponse trop longue (>{SUBPROCESS_TIMEOUT}s). "
                "Essaie une question plus simple ou /reset.", session_id)

    raw = result.stdout.strip() or result.stderr.strip()

    # Auto-reset MUST come before returncode check: Claude exits non-zero on 400 API errors
    if session_id and not _retried and (
        "tool_call_id" in raw or "reasoning_content" in raw
        or ("api_error_status" in raw and "400" in raw)
    ):
        logger.warning(f"Session {session_id}: corrupt tool history (400), auto-resetting")
        text, new_session = run_claude(user_message, None, _retried=True)
        # Préfixe pour informer l'utilisateur
        return f"🔄 (session redémarrée)\n\n{text}", new_session

    if result.returncode != 0:
        friendly = _friendly_api_error(raw)
        if friendly:
            return friendly, session_id
        # Sinon, extraire juste le message d'erreur principal sans le JSON brut
        snippet = raw[:300].replace("\n", " ")
        return f"⚠️ Erreur Claude CLI: {snippet}", session_id

    text, new_session = parse_claude_stdout(result.stdout, session_id)
    if not text:
        logger.warning(f"Empty result after parsing. Raw stdout[:200]: {result.stdout[:200]}")
        # Si le stdout contient une erreur API connue, montrer un message clair
        friendly = _friendly_api_error(result.stdout)
        text = friendly or "⚠️ Réponse vide. Réessaie ou envoie /reset."
    return text, new_session


# ─── GitHub relay (fallback si > 50s) ─────────────────────────────────────────

async def relay_to_telegram(chat_id: int, text: str):
    """Send message via GitHub Actions relay (bypasses HF Space TLS block on Telegram IPs)."""
    if not GITHUB_TOKEN:
        logger.error("GITHUB_TOKEN absent — impossible de relayer")
        return

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            if TELEGRAM_RELAY_REPO:
                # New relay: repository_dispatch on valm7235/valm7235.github.io
                resp = await client.post(
                    f"https://api.github.com/repos/{TELEGRAM_RELAY_REPO}/dispatches",
                    headers={"Authorization": f"token {GITHUB_TOKEN}",
                             "Accept": "application/vnd.github+json",
                             "X-GitHub-Api-Version": "2022-11-28"},
                    json={"event_type": "tg-send", "client_payload": {
                        "method": "sendMessage", "chat_id": chat_id, "text": text, "parse_mode": "HTML",
                    }},
                )
            else:
                # Legacy: workflow_dispatch on claudecode-CLI-kimi/send-telegram.yml
                text_b64 = base64.b64encode(text.encode()).decode()
                resp = await client.post(
                    f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/send-telegram.yml/dispatches",
                    headers={"Authorization": f"token {GITHUB_TOKEN}",
                             "Accept": "application/vnd.github.v3+json"},
                    json={"ref": "main", "inputs": {"chat_id": str(chat_id), "text_b64": text_b64}},
                )
        logger.info(f"GitHub relay → chat={chat_id} status={resp.status_code}")
    except Exception as e:
        logger.error(f"GitHub relay failed: {e}")


def run_claude_popen(
    user_message: str,
    session_id: str | None,
    status: dict,
    _retried: bool = False,
) -> tuple[str, str | None]:
    """Claude CLI via Popen + stream-json — met à jour status{} en temps réel pour le live transcript."""
    cmd = [find_claude(), "--print", "--dangerously-skip-permissions",
           "--model", "claude-sonnet-4-6", "--output-format", "stream-json"]
    if session_id:
        cmd += ["--resume", session_id]
    cmd.append(user_message)

    status.update({"step": "starting", "tool": "", "cmd": "", "session_short": ""})

    result_text = ""
    out_session = session_id
    raw_lines: list[str] = []
    deadline = __import__("time").time() + TRANSCRIPT_TIMEOUT

    try:
        proc = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL, text=True,
            cwd=WORK_DIR, env=CLAUDE_ENV,
        )
    except Exception as e:
        return f"⚠️ Impossible de lancer Claude CLI: {e}", session_id

    try:
        while True:
            if __import__("time").time() > deadline:
                proc.kill()
                status["step"] = "timeout"
                return (
                    f"⏰ Tâche trop longue (>{TRANSCRIPT_TIMEOUT}s). "
                    "Essaie une question plus simple ou /reset.", session_id,
                )

            line = proc.stdout.readline()
            if not line and proc.poll() is not None:
                break
            if not line:
                continue

            line = line.strip()
            if not line:
                continue
            raw_lines.append(line)

            try:
                ev = json.loads(line)
                etype = ev.get("type", "")

                if etype == "system":
                    out_session = ev.get("session_id", session_id) or session_id
                    status["session_short"] = (out_session or "")[:8]
                    status["step"] = "started"

                elif etype == "assistant":
                    for block in ev.get("message", {}).get("content", []):
                        btype = block.get("type", "")
                        if btype == "text" and block.get("text"):
                            status["step"] = "writing"
                        elif btype == "tool_use":
                            _update_status_for_tool(status, block.get("name", ""), block.get("input", {}))

                elif etype == "tool_use":
                    _update_status_for_tool(status, ev.get("name", ""), ev.get("input", {}))

                elif etype == "result":
                    result_text = ev.get("result", "")
                    out_session = ev.get("session_id", out_session) or out_session
                    status["step"] = "done"

            except json.JSONDecodeError:
                pass

        proc.wait(timeout=30)

    except Exception as e:
        logger.error(f"run_claude_popen inner error: {e}")
        proc.kill()
    finally:
        try:
            proc.stdout.close()
            proc.stderr.close()
        except Exception:
            pass

    raw_all = "\n".join(raw_lines)

    # Auto-reset: corrupt session (400 error avec tool history)
    if session_id and not _retried and (
        "tool_call_id" in raw_all or "reasoning_content" in raw_all
        or ("api_error_status" in raw_all and "400" in raw_all)
    ):
        logger.warning(f"Popen: session {session_id} corrupt → auto-reset")
        status["step"] = "reset"
        text, new_sess = run_claude_popen(user_message, None, status, _retried=True)
        return f"🔄 (session redémarrée)\n\n{text}", new_sess

    if proc.returncode != 0 and not result_text:
        stderr_data = ""
        try:
            stderr_data = proc.stderr.read(500) if not proc.stderr.closed else ""
        except Exception:
            pass
        raw_combined = raw_all or stderr_data
        friendly = _friendly_api_error(raw_combined)
        if friendly:
            return friendly, out_session
        return f"⚠️ Erreur CLI (code {proc.returncode}): {raw_combined[:300]}", out_session

    if not result_text:
        result_text, out_session = parse_claude_stdout(raw_all, out_session)

    result_text = clean_response(result_text or "")
    if not result_text:
        friendly = _friendly_api_error(raw_all)
        result_text = friendly or "⚠️ Réponse vide. Réessaie ou /reset."

    return result_text, out_session


def _update_status_for_tool(status: dict, tool_name: str, tool_input: dict) -> None:
    """Déduit l'étape de traitement depuis le nom d'un outil Claude CLI."""
    name_lower = tool_name.lower()
    if "websearch" in name_lower:
        status["step"] = "websearch"
        status["tool"] = tool_name
        status["cmd"] = tool_input.get("query", "")[:80]
    elif "webfetch" in name_lower:
        status["step"] = "webfetch"
        status["tool"] = tool_name
        status["cmd"] = tool_input.get("url", "")[:80]
    elif "bash" in name_lower or "shell" in name_lower:
        status["step"] = "shell"
        status["tool"] = tool_name
        status["cmd"] = tool_input.get("command", "")[:80]
    elif "write" in name_lower or "edit" in name_lower or "read" in name_lower:
        status["step"] = "file"
        status["tool"] = tool_name
        status["cmd"] = tool_input.get("file_path", "") or tool_input.get("path", "")
        status["cmd"] = status["cmd"][:80]
    elif "todo" in name_lower:
        status["step"] = "planning"
        status["tool"] = tool_name
        status["cmd"] = ""
    else:
        status["step"] = "tool"
        status["tool"] = tool_name
        status["cmd"] = ""


class LiveTranscript:
    """Gère un message Telegram qui est édité en direct pendant l'exécution de Claude CLI."""

    _STATUS_ICON = {
        "init": "🔵", "starting": "🔵", "started": "🔵",
        "writing": "🟡", "tool": "🔧", "planning": "🗒",
        "websearch": "🌐", "webfetch": "🌐", "shell": "⚙️",
        "file": "📄", "reset": "🔄", "done": "✅", "timeout": "⏰",
        "error": "❌",
    }

    def __init__(self, chat_id: int, loop):
        self.chat_id = chat_id
        self._loop = loop
        self.msg_id: int | None = None
        self.start = __import__("time").time()
        self._last_edit = 0.0
        self._last_text = ""
        self._min_interval = 3.0  # secondes entre deux éditions

    def _post(self, method: str, payload: dict) -> dict:
        try:
            return _tg_post_sync(method, payload, timeout=12)
        except Exception as e:
            logger.debug(f"TG {method} failed: {e}")
            return {"ok": False, "description": str(e)}

    async def _post_async(self, method: str, payload: dict) -> dict:
        return await self._loop.run_in_executor(None, lambda: self._post(method, payload))

    async def send_initial(self) -> bool:
        r = await self._post_async("sendMessage", {
            "chat_id": self.chat_id,
            "text": "🔵 Reçu — préparation Claude Code…",
        })
        if r.get("ok"):
            self.msg_id = r.get("result", {}).get("message_id")
            self._last_text = "🔵 Reçu — préparation Claude Code…"
            return True
        logger.warning(f"send_initial failed: {r}")
        return False

    def _build_status(self, status: dict) -> str:
        import time as _t
        elapsed = int(_t.time() - self.start)
        step = status.get("step", "init")
        sid = status.get("session_short", "")
        cmd = status.get("cmd", "")
        tool = status.get("tool", "")
        icon = self._STATUS_ICON.get(step, "🟡")

        lines = []
        if step in ("init", "starting"):
            lines.append(f"{icon} Préparation Claude Code…")
        elif step == "started":
            lines.append(f"{icon} Claude Code démarré…")
        elif step == "writing":
            lines.append(f"{icon} Claude Code rédige la réponse…")
        elif step == "websearch":
            lines.append(f"{icon} Recherche web en cours…")
            if cmd:
                lines.append(f"  🔍 {cmd[:80]}")
        elif step == "webfetch":
            lines.append(f"{icon} Lecture page web…")
            if cmd:
                lines.append(f"  🔗 {cmd[:80]}")
        elif step == "shell":
            lines.append(f"{icon} Shell en cours…")
            if cmd:
                lines.append(f"  $ {cmd[:80]}")
        elif step == "file":
            lines.append(f"{icon} Fichier : {cmd[:60] or '...'}")
        elif step == "planning":
            lines.append(f"{icon} Planification…")
        elif step == "tool":
            lines.append(f"{icon} Outil : {tool or 'inconnu'}")
        elif step == "reset":
            lines.append(f"{icon} Réinitialisation session…")
        else:
            lines.append(f"🟡 Claude Code travaille…")

        if sid:
            lines.append(f"  Session : {sid}…")
        lines.append(f"  ⏱ {elapsed}s")
        if elapsed > 50:
            lines.append("  ⏳ Tâche longue — traitement en arrière-plan")
        return "\n".join(lines)

    async def update(self, status: dict, force: bool = False) -> bool:
        import time as _t
        now = _t.time()
        if not force and (now - self._last_edit) < self._min_interval:
            return False
        text = self._build_status(status)
        if text == self._last_text and not force:
            return False
        if not self.msg_id:
            return False
        r = await self._post_async("editMessageText", {
            "chat_id": self.chat_id, "message_id": self.msg_id, "text": text,
        })
        if r.get("ok"):
            self._last_text = text
            self._last_edit = now
            return True
        desc = r.get("description", "")
        if "not modified" in desc.lower():
            self._last_edit = now
        return False

    async def update_text(self, text: str) -> bool:
        """Édite le message avec un texte arbitraire (status intermédiaire)."""
        if not self.msg_id:
            return False
        r = await self._post_async("editMessageText", {
            "chat_id": self.chat_id, "message_id": self.msg_id, "text": text,
        })
        if r.get("ok"):
            self._last_text = text
            return True
        return False

    async def finish(self, result: str, elapsed: int) -> None:
        header = f"✅ Terminé en {elapsed}s\n\n"
        full = header + result
        if len(full) <= 4096:
            if self.msg_id:
                r = await self._post_async("editMessageText", {
                    "chat_id": self.chat_id, "message_id": self.msg_id, "text": full,
                })
                if r.get("ok"):
                    return
            await self._post_async("sendMessage", {"chat_id": self.chat_id, "text": full})
        else:
            # Edite le message de statut avec l'en-tête, puis envoie la réponse en morceaux
            if self.msg_id:
                await self._post_async("editMessageText", {
                    "chat_id": self.chat_id, "message_id": self.msg_id,
                    "text": f"✅ Terminé en {elapsed}s (réponse complète ci-dessous)",
                })
            chunks = _split_message(result, 4000)
            for i, chunk in enumerate(chunks):
                prefix = f"[{i+1}/{len(chunks)}]\n" if len(chunks) > 1 else ""
                await self._post_async("sendMessage", {
                    "chat_id": self.chat_id, "text": prefix + chunk,
                })

    async def error(self, error_msg: str) -> None:
        text = (
            f"❌ Erreur\n"
            f"Cause: {error_msg[:300]}\n"
            f"Action: /reset ou réessaie"
        )
        if self.msg_id:
            r = await self._post_async("editMessageText", {
                "chat_id": self.chat_id, "message_id": self.msg_id, "text": text,
            })
            if r.get("ok"):
                return
        await self._post_async("sendMessage", {"chat_id": self.chat_id, "text": text})


async def handle_with_transcript(chat_id: int, msg: dict, prepared_prompt: str | None = None):
    """Background task : traite un message Telegram avec live transcript.

    Remplace à la fois l'inline path et le relay GitHub : on envoie les
    updates nous-mêmes via Telegram API, en éditant un seul message.
    """
    import time as _t
    loop = asyncio.get_event_loop()
    chat_lock = _get_chat_lock(chat_id)

    transcript = LiveTranscript(chat_id, loop)
    tg_ok = await transcript.send_initial()
    if not tg_ok:
        # Telegram HTTPS bloqué (HF Space DPI) — fallback relay GitHub Actions
        logger.warning(f"send_initial failed chat={chat_id} — relay fallback activé")
        prompt = prepared_prompt or msg.get("text", "").strip()
        session_id = get_session(chat_id)
        future = loop.run_in_executor(None, lambda: run_claude_popen(prompt, session_id, {}))
        asyncio.create_task(_wait_and_relay(chat_id, future, session_id))
        return
    status: dict = {"step": "init"}
    prompt = prepared_prompt or msg.get("text", "").strip()

    try:
        # ── Téléchargement/transcription media ──
        if msg.get("voice") and not prepared_prompt:
            await transcript.update_text("📎 Téléchargement vocal en cours…")
            file_id = msg["voice"]["file_id"]
            try:
                transcribed, error = await asyncio.wait_for(
                    loop.run_in_executor(None, lambda: _download_and_transcribe(file_id)),
                    timeout=35.0,
                )
            except asyncio.TimeoutError:
                await transcript.error("Téléchargement vocal trop long. Réessaie avec un vocal plus court.")
                return
            if not transcribed:
                await transcript.error(f"Transcription échouée: {error}")
                return
            await transcript.update_text(f"🎤 Transcrit: {transcribed[:100]}…\n🔵 Traitement…")
            prompt = f"[🎤 Message vocal]: {transcribed}"

        elif msg.get("document") and not prepared_prompt:
            doc = msg["document"]
            file_id, filename = doc["file_id"], doc.get("file_name", "fichier")
            if doc.get("file_size", 0) > MAX_FILE_SIZE:
                await transcript.error(f"Fichier trop grand (max 20 MB).")
                return
            await transcript.update_text("📎 Téléchargement fichier…")
            local = await loop.run_in_executor(None, lambda: _download_file_sync(file_id, filename))
            if not local:
                await transcript.error("Impossible de télécharger le fichier.")
                return
            caption = msg.get("caption", "").strip()
            prompt = f"{caption or 'Analyse ce fichier et explique son contenu.'}\n\nFichier: {local}"

        elif msg.get("photo") and not prepared_prompt:
            photo = msg["photo"][-1]
            file_id = photo["file_id"]
            await transcript.update_text("🖼 Téléchargement photo…")
            local = await loop.run_in_executor(None, lambda: _download_file_sync(file_id, "photo.jpg"))
            if not local:
                await transcript.error("Impossible de télécharger la photo.")
                return
            caption = msg.get("caption", "").strip()
            prompt = f"{caption or 'Décris cette image en détail.'}\n\nImage: {local}"

        elif msg.get("audio") and not prepared_prompt:
            audio = msg["audio"]
            file_id, filename = audio["file_id"], audio.get("file_name", "audio.mp3")
            await transcript.update_text("🎵 Téléchargement audio…")
            local = await loop.run_in_executor(None, lambda: _download_file_sync(file_id, filename))
            if not local:
                await transcript.error("Impossible de télécharger l'audio.")
                return
            caption = msg.get("caption", "").strip()
            prompt = f"{caption or 'Fichier audio reçu.'}\n\nFichier: {local}"

        if not prompt:
            await transcript.error("Message vide ou non supporté.")
            return

        # ── Claude CLI avec live transcript (Popen + stream-json) ──
        session_id = get_session(chat_id)
        status["step"] = "starting"

        future = loop.run_in_executor(
            None, lambda: run_claude_popen(prompt, session_id, status)
        )

        # Boucle: édite le message toutes les 3s pendant que Claude travaille
        while not future.done():
            await transcript.update(status)
            await asyncio.sleep(2)

        result_text, new_session = await future
        elapsed = int(_t.time() - transcript.start)

        if new_session and new_session != session_id:
            save_session(chat_id, new_session)

        await transcript.finish(result_text, elapsed)

    except Exception as e:
        logger.error(f"handle_with_transcript: {e}", exc_info=True)
        await transcript.error(str(e)[:300])
    finally:
        if chat_lock.locked():
            try:
                chat_lock.release()
            except RuntimeError:
                pass


async def _wait_and_relay(chat_id: int, future, session_id: str | None):
    """Attend que le subprocess Claude finisse et envoie le résultat via le relay GitHub.

    IMPORTANT : on RÉUTILISE le future déjà lancé (au lieu de démarrer un 2e subprocess
    comme avant). Évite double consommation de quota Kimi + corruption de session.
    """
    try:
        response, new_session_id = await future
        if new_session_id and new_session_id != session_id:
            save_session(chat_id, new_session_id)
        await relay_to_telegram(chat_id, response or "❌ Pas de réponse.")
    except Exception as e:
        logger.error(f"_wait_and_relay error: {e}", exc_info=True)
        await relay_to_telegram(chat_id, f"❌ Erreur interne: {str(e)[:200]}")
    finally:
        # Libère le verrou du chat (cas timeout fallback)
        lock = _chat_locks.get(chat_id)
        if lock and lock.locked():
            try:
                lock.release()
            except RuntimeError:
                pass


# ─── Webhook ──────────────────────────────────────────────────────────────────

@router.post("/webhook/{secret}")
async def webhook(secret: str, request: Request):
    if secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    update = await request.json()
    msg = update.get("message") or update.get("edited_message")
    if not msg:
        return JSONResponse({"ok": True})

    chat_id = msg["chat"]["id"]
    text = msg.get("text", "").strip()
    has_media = any(msg.get(k) for k in ["voice", "document", "photo", "audio"])
    logger.info(f"Webhook: chat={chat_id} text={bool(text)} media={has_media}")

    # ── Commandes : réponse directe (pas de transcript) ──
    if text.startswith(("/start", "/reset")):
        delete_session(chat_id)
        return JSONResponse({
            "method": "sendMessage", "chat_id": chat_id,
            "text": "🔄 Nouvelle session. Claude Code (Kimi K2.5) est prêt !\n"
                    "📎 Envoie fichiers, 🎤 vocaux ou du texte.",
        })

    if text.startswith("/help"):
        return JSONResponse({
            "method": "sendMessage", "chat_id": chat_id,
            "text": (
                "💡 Utilisation :\n"
                "• Texte → réponse IA (live transcript)\n"
                "• 🎤 Vocal → transcrit puis répondu\n"
                "• 📎 Fichier → analysé par Claude CLI\n"
                "• 🖼️ Photo → analysée\n"
                "/reset — Nouvelle session\n"
                "/help — Cette aide"
            ),
        })

    if not text and not has_media:
        return JSONResponse({"ok": True})

    # ── Mutex : refuse un 2e message si le précédent est encore en cours ──
    chat_lock = _get_chat_lock(chat_id)
    if chat_lock.locked():
        logger.warning(f"chat={chat_id} busy — refusing concurrent message")
        return JSONResponse({
            "method": "sendMessage", "chat_id": chat_id,
            "text": "🔄 Je traite encore ton message précédent. Patiente quelques secondes...",
        })

    # Acquiert le lock AVANT de lancer le background task.
    # handle_with_transcript le libère dans son bloc finally.
    await chat_lock.acquire()

    # Fire background task : live transcript + Claude CLI + Telegram edits
    asyncio.create_task(handle_with_transcript(chat_id, msg, prepared_prompt=text or None))

    # Retourne immédiatement — Telegram n'attendra pas
    return JSONResponse({"ok": True})


@router.get("/webhook/setup")
async def setup_webhook(request: Request):
    space_host = os.environ.get("SPACE_HOST", "")
    if space_host and not space_host.startswith("http"):
        space_host = f"https://{space_host}"
    if not space_host:
        return {"error": "SPACE_HOST not set"}
    webhook_url = f"{space_host}/webhook/{WEBHOOK_SECRET}"
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.post(
            f"{TG_API}/setWebhook",
            json={"url": webhook_url, "drop_pending_updates": True}
        )
    return {"webhook_url": webhook_url, "telegram_response": r.json()}


@router.get("/webhook/info")
async def webhook_info():
    async with httpx.AsyncClient(timeout=20) as client:
        r = await client.get(f"{TG_API}/getWebhookInfo")
    return r.json()


@router.get("/webhook/secret")
async def get_secret():
    return {"webhook_path": f"/webhook/{WEBHOOK_SECRET}"}
