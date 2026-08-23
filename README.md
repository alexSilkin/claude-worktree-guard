# worktree-guard

Claude Code has no setting for worktree naming. Call `EnterWorktree` without a
`name` and it generates one — `zealous-noether-b3d7e1` — then derives the
branch from it. After thirty of those, nothing on disk says which directory holds
which work:

```
quirky-torvalds-8f21ac    -> claude/export-csv-pagination-3d90fe
zealous-noether-b3d7e1    -> claude/gallant-mccarthy-27fa10
lucid-hopper-5c2e90       -> claude/oauth-token-refresh-4b09de
```

The mismatches come later: renaming a branch when you open the PR does not rename
the directory, which is frozen at creation.

There is a second, quieter failure. `EnterWorktree` *resumes* a worktree whose
name already exists rather than creating one, and reports it only as
`Resuming existing worktree at:`. You inherit that worktree's branch and its
uncommitted changes without being asked.

This plugin makes both impossible.

## What it does

A `PreToolUse` hook on `EnterWorktree` denies the call, with the reason attached,
when the name is:

| Case | Example | Why |
|---|---|---|
| missing | `{}` | Claude Code would generate a random one |
| generated-looking | `zealous-noether-b3d7e1` | describes nothing |
| malformed | `SearchEmpty`, `search` | not a 2–5 word kebab slug |
| vacuous | `fix-stuff`, `wip-tmp` | says nothing about the task |
| colliding | a name already in `.claude/worktrees/` | would silently resume it |

A denial is not a failure — the reason goes back to Claude, which retries with a
real name.

Passing through untouched: `EnterWorktree` with `path` (entering an existing
worktree is already explicit), every other tool, and any malformed hook payload
(it fails open rather than wedging the session).

## The naming rule

A kebab-case slug of 2–5 concrete words, `<area>-<what-changes>`, derived from
the task:

```
search-empty-state
upload-retry-backoff
retire-legacy-importer
```

The directory becomes `.claude/worktrees/<name>` and the branch becomes
`claude/<name>`. One slug, one meaning, both places — which is why it has to be
right at creation.

## Install

```bash
claude plugin marketplace add alexSilkin/claude-worktree-guard
claude plugin install worktree-guard@silkin-tools
```

Per machine. A project's `.claude/settings.json` cannot register a marketplace
for you — `extraKnownMarketplaces` is read only from managed and flag settings —
so this step does not automate away.

## Scope

The hook is the floor, not the standard: a name that passes the regex but does
not describe the work still fails review. Pair it with a rule in `AGENTS.md` /
`CLAUDE.md` stating the convention in prose, which also reaches Codex — it reads
`AGENTS.md` natively, and has no worktree tool for a hook to intercept anyway.
