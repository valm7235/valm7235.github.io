#!/bin/bash
# Hook SessionStart — réinstalle les outils du CLI Windows dans le conteneur web.
# Idempotent : ne réinstalle que ce qui manque (le cache du conteneur fait le reste).
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# 1. Binaires npm globaux : marp, playwright-mcp, chrome-devtools-mcp
if ! command -v marp >/dev/null 2>&1 || ! command -v playwright-mcp >/dev/null 2>&1 || ! command -v chrome-devtools-mcp >/dev/null 2>&1; then
  npm install -g @marp-team/marp-cli @playwright/mcp chrome-devtools-mcp
fi

# 2. Navigateurs (PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers, mis en cache)
BROWSERS_DIR="${PLAYWRIGHT_BROWSERS_PATH:-/opt/pw-browsers}"
if ! ls "$BROWSERS_DIR"/chromium-*/chrome-linux*/chrome >/dev/null 2>&1; then
  playwright install chromium
fi
if ! ls "$BROWSERS_DIR"/chromium_headless_shell-* >/dev/null 2>&1; then
  npx -y @playwright/mcp install-browser chrome-for-testing
fi

# 3. Lien stable vers le binaire Chromium pour chrome-devtools-mcp (.mcp.json)
CHROME_BIN=$(ls -d "$BROWSERS_DIR"/chromium-*/chrome-linux*/chrome 2>/dev/null | sort -V | tail -1)
if [ -n "$CHROME_BIN" ]; then
  ln -sf "$CHROME_BIN" /usr/local/bin/chromium-stable
fi

echo "session-start: marp=$(command -v marp), playwright-mcp=$(command -v playwright-mcp), chrome-devtools-mcp=$(command -v chrome-devtools-mcp), chromium=$(readlink -f /usr/local/bin/chromium-stable 2>/dev/null || echo absent)"
