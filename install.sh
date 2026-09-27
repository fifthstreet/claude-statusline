#!/usr/bin/env bash
# Installs the statusline scripts into ~/.claude and wires up settings.json.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
SETTINGS="$CLAUDE_DIR/settings.json"

mkdir -p "$CLAUDE_DIR"
cp "$SCRIPT_DIR/statusline-command.py" "$CLAUDE_DIR/statusline-command.py"
cp "$SCRIPT_DIR/statusline-command.sh" "$CLAUDE_DIR/statusline-command.sh"
chmod +x "$CLAUDE_DIR/statusline-command.sh" "$CLAUDE_DIR/statusline-command.py"

echo "Copied statusline scripts into $CLAUDE_DIR"

if command -v python >/dev/null 2>&1 || command -v python3 >/dev/null 2>&1; then
  echo "python found on PATH — good."
else
  echo "WARNING: no python/python3 found on PATH. The statusline needs it." >&2
fi

if [ -f "$SETTINGS" ] && command -v python >/dev/null 2>&1; then
  python - "$SETTINGS" <<'PYEOF'
import json, sys
path = sys.argv[1]
with open(path) as f:
    cfg = json.load(f)
cfg["statusLine"] = {"type": "command", "command": "bash ~/.claude/statusline-command.sh"}
with open(path, "w") as f:
    json.dump(cfg, f, indent=2)
    f.write("\n")
print(f"Updated statusLine entry in {path}")
PYEOF
else
  echo "No existing $SETTINGS found (or no python) — add this manually:"
  echo '  "statusLine": { "type": "command", "command": "bash ~/.claude/statusline-command.sh" }'
fi

echo "Done. Restart Claude Code / start a new session to see the statusline."
