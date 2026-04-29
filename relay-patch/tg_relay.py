"""
Patch pour telegram_bot.py — relay GitHub Actions quand HF Space bloque Telegram HTTPS.

INSTRUCTIONS :
  1. Copier ce fichier dans le repo claudecode-CLI-kimi (même dossier que telegram_bot.py)
  2. Dans telegram_bot.py, remplacer _tg_post_sync() par la version ci-dessous
  3. Ajouter les imports manquants en haut du fichier si nécessaire :
       import uuid as _uuid_mod
       from tg_relay import gh_relay_send   # ← ajouter cet import
  4. Ajouter les secrets HF Space :
       GH_RELAY_TOKEN  = PAT GitHub avec scope "repo" sur valm7235/valm7235.github.io
       GH_RELAY_REPO   = valm7235/valm7235.github.io

FONCTIONNEMENT :
  - Le bot appelle GitHub API (accessible depuis HF Space) pour déclencher un workflow
  - GitHub Actions envoie le message Telegram (GH peut joindre Telegram, pas HF Space)
  - Le workflow écrit le résultat dans relay-results/{uuid}.json dans le repo
  - Le bot poll ce fichier (~30-60s) pour récupérer le vrai message_id
  - Timeout 90s → fallback fire-and-forget (message envoyé mais message_id inconnu)
"""

import os
import json
import time
import base64
import uuid as _uuid_mod
import urllib.request
import urllib.error
import logging

log = logging.getLogger(__name__)

_GH_RELAY_TOKEN = os.environ.get("GH_RELAY_TOKEN", "")
_GH_RELAY_REPO  = os.environ.get("GH_RELAY_REPO", "valm7235/valm7235.github.io")
_GH_API         = "https://api.github.com"


def _gh_request(url: str, data: dict | None = None, method: str = "GET") -> dict:
    """Appel GitHub API avec le relay token."""
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode() if data else None,
        headers={
            "Authorization": f"Bearer {_GH_RELAY_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method=method,
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode()) if resp.length != 0 else {}


def _gh_dispatch(payload: dict) -> bool:
    """Déclenche le workflow telegram-relay via repository_dispatch."""
    url = f"{_GH_API}/repos/{_GH_RELAY_REPO}/dispatches"
    try:
        _gh_request(url, {"event_type": "tg-send", "client_payload": payload}, "POST")
        return True
    except Exception as exc:
        log.warning("gh_dispatch failed: %s", exc)
        return False


def _gh_poll_result(relay_uuid: str, timeout: float = 90.0) -> dict | None:
    """Poll relay-results/{uuid}.json jusqu'à ce que le résultat soit disponible."""
    deadline = time.monotonic() + timeout
    url = f"{_GH_API}/repos/{_GH_RELAY_REPO}/contents/relay-results/{relay_uuid}.json"
    while time.monotonic() < deadline:
        time.sleep(5)
        try:
            result = _gh_request(url)
            content = json.loads(base64.b64decode(result["content"]).decode())
            # Nettoyer le fichier résultat (best-effort)
            try:
                _gh_request(
                    url,
                    {"message": f"cleanup {relay_uuid[:8]}", "sha": result["sha"]},
                    "DELETE",
                )
            except Exception:
                pass
            return content
        except urllib.error.HTTPError as exc:
            if exc.code != 404:
                log.debug("poll error %s: %s", relay_uuid[:8], exc)
        except Exception as exc:
            log.debug("poll error %s: %s", relay_uuid[:8], exc)
    log.warning("relay timeout for %s", relay_uuid[:8])
    return None


def gh_relay_send(
    method: str,
    chat_id: int,
    text: str = "",
    message_id: int | None = None,
    parse_mode: str = "HTML",
) -> dict:
    """
    Remplace _tg_post_sync() : envoie via GitHub Actions relay.

    Retourne {'ok': True, 'result': {'message_id': <int>}} si succès.
    Retourne {'ok': False, 'description': '...'} si échec.
    """
    if not _GH_RELAY_TOKEN:
        return {"ok": False, "description": "GH_RELAY_TOKEN not configured"}

    relay_uuid = str(_uuid_mod.uuid4())
    payload = {
        "uuid": relay_uuid,
        "method": method,
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }
    if message_id is not None:
        payload["message_id"] = message_id

    log.info("gh_relay_send %s chat=%s uuid=%s", method, chat_id, relay_uuid[:8])

    if not _gh_dispatch(payload):
        return {"ok": False, "description": "GitHub dispatch failed"}

    result = _gh_poll_result(relay_uuid)
    if result is None:
        # Fire-and-forget : le message sera quand même envoyé mais on n'a pas le message_id
        log.warning("relay poll timeout for %s — continuing without message_id", relay_uuid[:8])
        return {"ok": True, "result": {"message_id": 0}, "_relay_timeout": True}

    if result.get("ok"):
        return {"ok": True, "result": {"message_id": result.get("message_id", 0)}}
    return {"ok": False, "description": result.get("error", "relay failed")}
