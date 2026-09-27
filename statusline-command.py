#!/usr/bin/env python
"""Claude Code statusline: model/effort, context usage, 5h & 7d rate limits,
prompt-cache hit rate, session cost, git branch, local time.

Reads the statusline JSON payload on stdin (see Claude Code docs for schema).
Deliberately dependency-free (stdlib only) since `jq` is not installed here.
"""
import json
import subprocess
import sys
from datetime import datetime

RESET = "\033[0m"
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
GRAY = "\033[90m"
MAGENTA = "\033[35m"


def color_for(pct):
    if pct is None:
        return GRAY
    if pct >= 80:
        return RED
    if pct >= 50:
        return YELLOW
    return GREEN


def bar(pct, width=10):
    if pct is None:
        return "-" * width
    filled = max(0, min(width, round(pct / 100 * width)))
    return "#" * filled + "-" * (width - filled)


def abbr(n):
    if n is None:
        return "?"
    n = float(n)
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(int(n))


def local_time(epoch):
    if epoch is None:
        return None
    try:
        return datetime.fromtimestamp(epoch)
    except Exception:
        return None


def git_branch(cwd):
    if not cwd:
        return None
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=cwd, capture_output=True, text=True, timeout=1,
        )
        if out.returncode == 0:
            branch = out.stdout.strip()
            return branch or None
    except Exception:
        pass
    return None


def main():
    # Windows console/pipe stdout often defaults to a non-UTF-8 codepage
    # (e.g. cp1252), which would raise on any non-ASCII character below.
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

    try:
        data = json.load(sys.stdin)
    except Exception:
        print(f"{GRAY}statusline: bad input{RESET}")
        return

    segments = []

    branch = git_branch(data.get("workspace", {}).get("current_dir") or data.get("cwd"))
    if branch:
        segments.append(f"{MAGENTA}git:{branch}{RESET}")

    model = (data.get("model") or {}).get("display_name", "?")
    effort = (data.get("effort") or {}).get("level")
    model_str = f"{model} ({effort})" if effort else model
    segments.append(f"{CYAN}{model_str}{RESET}")

    ctx = data.get("context_window") or {}
    used_pct = ctx.get("used_percentage")
    used_tok = ctx.get("total_input_tokens")
    total_tok = ctx.get("context_window_size")
    if used_pct is not None:
        c = color_for(used_pct)
        segments.append(
            f"{c}Ctx [{bar(used_pct)}] {used_pct}% ({abbr(used_tok)}/{abbr(total_tok)}){RESET}"
        )
    else:
        segments.append(f"{GRAY}Ctx n/a{RESET}")

    rl = data.get("rate_limits") or {}
    five = rl.get("five_hour") or {}
    five_used = five.get("used_percentage")
    if five_used is not None:
        left = max(0, round(100 - five_used))
        reset_dt = local_time(five.get("resets_at"))
        reset_str = reset_dt.strftime("%I:%M%p").lstrip("0") if reset_dt else ""
        suffix = f" (resets {reset_str})" if reset_str else ""
        segments.append(f"{color_for(five_used)}5h {left}% left{suffix}{RESET}")

    week = rl.get("seven_day") or {}
    week_used = week.get("used_percentage")
    if week_used is not None:
        left = max(0, round(100 - week_used))
        reset_dt = local_time(week.get("resets_at"))
        reset_str = reset_dt.strftime("%a %I%p").lstrip("0") if reset_dt else ""
        suffix = f" (resets {reset_str})" if reset_str else ""
        segments.append(f"{color_for(week_used)}7d {left}% left{suffix}{RESET}")

    cache = data.get("prompt_cache") or {}
    hit_ratio = cache.get("hit_ratio")
    if hit_ratio is not None:
        pct = round(hit_ratio * 100)
        segments.append(f"{GRAY}Cache {pct}%{RESET}")

    cost = (data.get("cost") or {}).get("total_cost_usd")
    if cost is not None:
        segments.append(f"{GRAY}${cost:.2f}{RESET}")

    segments.append(f"{GRAY}{datetime.now().strftime('%I:%M%p').lstrip('0')}{RESET}")

    sys.stdout.write(" | ".join(segments) + "\n")


if __name__ == "__main__":
    main()
