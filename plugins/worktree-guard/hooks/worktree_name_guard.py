#!/usr/bin/env python3
"""PreToolUse guard for EnterWorktree.

Claude Code has no setting for worktree naming: omit `name` and it invents
`zealous-noether-b3d7e1`, then derives the branch from it. This hook forces an
explicit, task-derived slug, and refuses to silently resume a worktree that
already exists (EnterWorktree reuses a same-named worktree without saying so).

Contract: PreToolUse JSON on stdin, permission decision JSON on stdout.
Installed as a plugin, this applies to every repository on the machine.
"""
import json
import os
import re
import sys

SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+){1,5}$")
# Shape of Claude Code's own generated name: <adjective>-<surname>-<6 hex>
GENERATED = re.compile(r"^[a-z]+-[a-z]+-[0-9a-f]{6}$")
VAGUE = {
    "fix", "bug", "bugfix", "work", "task", "wip", "tmp", "temp", "test",
    "tests", "change", "changes", "update", "updates", "feature", "patch",
    "stuff", "misc", "new", "branch", "worktree",
}
MIN_LEN, MAX_LEN = 6, 48

RULE = (
    "Name it after the work, as a kebab-case slug of 2-5 concrete words "
    "(<area>-<what-changes>), e.g. `search-empty-state`, "
    "`upload-retry-backoff`, `retire-legacy-importer`. The branch is "
    "derived from this name, so getting it right here keeps the directory and "
    "the branch in sync."
)


def deny(reason):
    json.dump({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }, sys.stdout)
    sys.exit(0)


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # Never block on a malformed payload.

    if payload.get("tool_name") != "EnterWorktree":
        sys.exit(0)

    tool_input = payload.get("tool_input") or {}
    if tool_input.get("path"):
        sys.exit(0)  # Entering an existing worktree by path is explicit already.

    name = (tool_input.get("name") or "").strip()

    if not name:
        deny(
            "EnterWorktree was called without `name`, so Claude Code would "
            "generate a random one like `zealous-noether-b3d7e1` and derive "
            "the branch from it. " + RULE
        )

    if GENERATED.match(name):
        deny(
            f"`{name}` looks like a generated placeholder, not a description of "
            "the work. " + RULE
        )

    if not SLUG.match(name) or not (MIN_LEN <= len(name) <= MAX_LEN):
        deny(
            f"`{name}` is not a valid worktree slug. Use lowercase letters, "
            f"digits and single dashes, 2-5 words, {MIN_LEN}-{MAX_LEN} chars. "
            + RULE
        )

    if all(part in VAGUE for part in name.split("-")):
        deny(
            f"`{name}` says nothing about the task. " + RULE
        )

    cwd = payload.get("cwd") or os.getcwd()
    existing = os.path.join(cwd, ".claude", "worktrees", name)
    if os.path.exists(existing):
        deny(
            f"A worktree named `{name}` already exists at {existing}. "
            "EnterWorktree would silently resume it, inheriting its branch and "
            "uncommitted changes. Pick a distinct name for new work, or pass "
            f"`path: \"{existing}\"` if you deliberately mean to continue that one."
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
