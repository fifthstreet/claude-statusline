# claude-statusline

A richer status line for [Claude Code](https://claude.com/claude-code), written in
dependency-free Python (no `jq` required — several machines I use don't have it installed).

Shows, in one line:

- git branch (when the working directory is a repo)
- model name + effort level
- context window usage bar, percent, and token counts
- 5-hour and 7-day rate-limit headroom, with reset times
- prompt-cache hit rate
- session cost so far
- current local time

Example:

```
⎇ main | Sonnet 5 (high) | Ctx [#---------] 7% (68.6K/1.0M) | 5h 77% left (resets 6:00AM) | 7d 6% left (resets Mon 10AM) | Cache 95% | $0.27 | 2:19AM
```

Percentages are color-coded green/yellow/red at the 50%/80% used thresholds.

## Requirements

- `python` or `python3` on `PATH` (stdlib only — no pip installs)
- `git` on `PATH` if you want the branch segment (silently skipped otherwise)

## Install

```bash
git clone https://github.com/fifthstreet/claude-statusline.git
cd claude-statusline
bash install.sh
```

This copies the two scripts into `~/.claude/` and sets `statusLine` in
`~/.claude/settings.json` to run them. Start a new Claude Code session to see it.

## Manual install

Copy `statusline-command.py` and `statusline-command.sh` into `~/.claude/`, then add this to
`~/.claude/settings.json`:

```json
"statusLine": {
  "type": "command",
  "command": "bash ~/.claude/statusline-command.sh"
}
```

## Files

- `statusline-command.py` — all the logic; reads the statusline JSON payload on stdin
- `statusline-command.sh` — thin wrapper Claude Code actually invokes
- `install.sh` — copies both into `~/.claude` and patches `settings.json`
