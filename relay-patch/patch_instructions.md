# Patch telegram_bot.py — GitHub Actions Relay

## Contexte

HF Space bloque TLS vers les IPs Telegram (149.154.x.x, 91.108.x.x).
TCP ouvert mais SSL handshake timeout. Fix : router les messages via GitHub Actions.

## Fichiers à modifier

### 1. Ajouter `tg_relay.py` au repo `claudecode-CLI-kimi`

Copier le fichier `relay-patch/tg_relay.py` à la racine du repo (même niveau que `telegram_bot.py`).

### 2. Modifier `telegram_bot.py`

#### A. Ajouter l'import (après les autres imports)

```python
from tg_relay import gh_relay_send
```

#### B. Remplacer `_tg_post_sync` (trouver la fonction et remplacer son corps)

Localiser la fonction `_tg_post_sync` dans `telegram_bot.py`.
Remplacer son corps par :

```python
def _tg_post_sync(method: str, params: dict, timeout: int = 65) -> dict:
    """Envoie un message Telegram. Essaie relay GitHub si direct échoue."""
    chat_id    = params.get("chat_id")
    text       = params.get("text", params.get("caption", ""))
    message_id = params.get("message_id")
    parse_mode = params.get("parse_mode", "HTML")

    # Tenter le relay GitHub Actions (contourne le blocage TLS de HF Space)
    result = gh_relay_send(
        method=method,
        chat_id=chat_id,
        text=text,
        message_id=message_id,
        parse_mode=parse_mode,
    )
    if result.get("ok"):
        if result.get("_relay_timeout"):
            log.warning("_tg_post_sync relay timeout — message en transit (message_id inconnu)")
        return result

    # Fallback : essai direct (pour environnements sans blocage TLS)
    log.warning("gh_relay_send failed (%s), trying direct...", result.get("description"))
    # ... garder ici l'ancienne logique httpx/socket si souhaité ...
    return result
```

**Note :** Si le corps original de `_tg_post_sync` contient de la logique IP/socket complexe,
conserver cette logique dans le bloc `# Fallback` ci-dessus comme deuxième tentative.

### 3. Ajouter les secrets HF Space

Sur https://huggingface.co/spaces/vmu7235/claudecode-kimi/settings (onglet Variables) :

| Variable       | Valeur                                                   |
|----------------|----------------------------------------------------------|
| `GH_RELAY_TOKEN` | PAT GitHub avec scope `repo` sur `valm7235/valm7235.github.io` |
| `GH_RELAY_REPO`  | `valm7235/valm7235.github.io` (optionnel, c'est le défaut) |

### 4. Ajouter `TELEGRAM_BOT_TOKEN` dans les secrets du repo GitHub

Sur https://github.com/valm7235/valm7235.github.io/settings/secrets/actions :

| Secret             | Valeur                        |
|--------------------|-------------------------------|
| `TELEGRAM_BOT_TOKEN` | Token du bot Telegram (@BotFather) |

## Test après déploiement

```bash
SPACE="https://vmu7235-claudecode-kimi.hf.space"
curl -s -X POST "$SPACE/webhook/353df9984fff91cca94e597e37bfa0fc" \
  -H "Content-Type: application/json" \
  -d '{"update_id":99011,"message":{"message_id":2,"chat":{"id":999888,"type":"private"},"from":{"id":999888,"is_bot":false,"first_name":"Test"},"date":1745836801,"text":"salut"}}'

# Attendre ~60-90s puis vérifier logs :
sleep 90 && curl -s "$SPACE/debug/logs" | python3 -c "
import sys, json
d = json.load(sys.stdin)
lines = [l for l in d.get('proxy','').split('\n')
         if any(k in l for k in ['gh_relay','relay','chat=999888','message_id','send_initial'])]
print('\n'.join(lines[-20:]))
"
```

## Latence attendue

- `sendMessage` initial : ~30-60s (démarrage GitHub Actions)
- `editMessageText` (live transcript) : idem ~30-60s par update
- Fire-and-forget si timeout 90s : message envoyé mais message_id inconnu → pas de live edit

## Pour améliorer la latence (futur)

Déployer un Cloudflare Worker qui proxifie les appels à `api.telegram.org`.
Le Worker répond synchroniquement (<100ms). HF Space peut le joindre (Cloudflare IP).
