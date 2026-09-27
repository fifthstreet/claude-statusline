#!/usr/bin/env bash
# Claude Code statusline. Logic lives in statusline-command.py (jq isn't
# installed in this environment, so we use python instead).
python "$(dirname "${BASH_SOURCE[0]}")/statusline-command.py"
