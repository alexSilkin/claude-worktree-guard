#!/bin/sh
# Launch worktree_name_guard.py with whichever Python 3 actually runs.
#
# `python3` alone is not portable: on Windows it is usually the Microsoft Store
# alias, which exists on PATH but only prints "Python was not found" and exits
# non-zero. Claude Code treats that as a non-blocking hook error, so the guard
# would be silently skipped. Probe each candidate before handing it stdin.
dir=$(dirname "$0")
for py in python3 python py; do
    if "$py" -c "import sys; sys.exit(sys.version_info < (3,))" </dev/null >/dev/null 2>&1; then
        exec "$py" "$dir/worktree_name_guard.py"
    fi
done
echo "worktree-guard: no working Python 3 found; EnterWorktree is unguarded." >&2
exit 0
