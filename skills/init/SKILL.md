---
name: init
description: Install the software factory into the current repo. Use when the user types /sf:init, or asks to set up or install the factory in this project. Copies factory/ (scripts, config, checks, dashboard), fills checks.sh, updates AGENTS.md and .gitignore, and creates the GitHub labels.
---

# Install the software factory into this repo

The plugin already provides the `factory` skill, the eight agents and the
builder's gate hook. What each repo needs is its own `factory/` folder: the
scripts find the repo from their own location, and `checks.sh` and
`config.json` are repo-specific. Work in the repo root
(`git rev-parse --show-toplevel`).

The templates are in `${CLAUDE_PLUGIN_ROOT}/templates/factory/`.

## 0. Check the project

Stop and tell the user if any of these fail:

- It's a git repo with an `origin` on GitHub, and `gh auth status` shows a user
  who can push to it and manage its labels.
- Its default branch (`gh repo view --json defaultBranchRef`) exists on
  `origin`.
- `claude --version` is 2.1.257 or later (the intake agent runs on Fable).
- `python3 --version` is 3.10 or later. The scripts use only the standard
  library. Check `python3` itself runs a real Python, not the Microsoft Store
  alias; if only `python` works, step 1 gives the fix.
- `factory/` doesn't exist yet. If it does, show the user what's there and ask
  before overwriting.

## 1. Copy

```bash
cp -R "${CLAUDE_PLUGIN_ROOT}/templates/factory" factory
chmod +x factory/checks.sh factory/bin/job factory/bin/gate factory/bin/route
```

On Windows `chmod` doesn't record the executable bit in git; step 4 sets it in
the index.

The scripts start with `#!/usr/bin/env python3`. If `python3` doesn't run a real
Python but `python` does (the Microsoft Store alias on Windows), point them at
`python` instead:

```bash
sed -i '1s|python3|python|' factory/bin/job factory/bin/gate factory/bin/route
```

Keep their line endings as LF: a CRLF in the first line breaks the shebang.
Append these lines to the repo's `.gitattributes` (create it if missing):

```gitattributes
factory/checks.sh text eol=lf
factory/bin/* text eol=lf
```

## 2. Adapt

**`factory/checks.sh`.** Replace the placeholder with the project's real
checks: install dependencies if a fresh worktree needs them, then lint,
typecheck, tests and build, whichever the project has. Find them in
`AGENTS.md`, `CLAUDE.md`, `package.json` scripts, `Makefile`, `pyproject.toml`
and CI config. The script runs with a job's worktree as its working directory.
It must be non-interactive, must not rewrite files (no `--fix`, no
`--update-snapshots`), and must exit non-zero on any failure. Keep
`set -euo pipefail`.

**`factory/config.json`.**

- `base_branch`: the default branch.
- `merge_method`: `merge`, `squash` or `rebase`, one the repo allows
  (`gh api repos/{owner}/{repo} --jq '{allow_merge_commit, allow_squash_merge, allow_rebase_merge}'`).
- `protected_paths`: keep the two factory entries and don't add the project's
  tests. Features legitimately change existing tests, and a protected test
  blocks the job with no way through. The code reviewer catches weakened or
  special-cased tests instead. Add a path only when no job should ever change
  it. They are fnmatch patterns, so `*` also matches `/`.
- `ports`: move `base` if the project already uses ports 5100–5199.
- Leave `concurrency`, `max_rounds`, `routing`, `surface_reviewers` and
  `prices_usd_per_mtok` as they are unless the user asks.

**`AGENTS.md`** (or `CLAUDE.md`, whichever the project uses; create `AGENTS.md`
if neither exists). Every factory agent reads it. The agents ship with the
plugin and are shared by every repo, so this file is where the project's
specifics go. Make sure it says:

- how to set up a fresh checkout (install dependencies, env files to copy);
- how to start the dev server on a given port, if the project has one;
- the validation commands, matching `factory/checks.sh`.

Then add this section, filling the bullets from what you learn about the repo:

```markdown
## Software factory

`/sf:factory run` builds every open GitHub issue labeled
`factory` through intake → spec → build → gate → review → approve, one PR per
issue. State is in `factory/jobs/` (gitignored); `factory/bin/job` is its only
writer. Checks: `factory/checks.sh`. Dashboard: `cd factory && python3 -m
http.server`, then open http://localhost:8000/dashboard.html.

Each job works in its own git worktree, a full checkout of the repo at
`.worktrees/<job-id>` (gitignored). A tool run from the repo root that doesn't
read `.gitignore` sees those copies too; exclude `.worktrees/` in its config.

### Notes for the factory agents

- What this project is for (intake uses this to decide what belongs): ...
- Security hot spots (auth, data access rules, payment and webhook code, where
  user input meets queries or HTML): ...
- Design tokens, theme and shared components live in: ...
- The kinds of users the app has: ...
- Always escalate to a human (approver), in addition to its defaults: ...
```

Leave out a bullet that doesn't apply (no UI, for example).

**`.gitignore`.** Append these two lines:

```gitignore
/factory/jobs/
/.worktrees/
```

Ignore only these two paths, never `factory/`: the rest of `factory/` is part
of the project and gets committed.

**Labels.** Create them on GitHub (skip any that already exist):

```bash
gh label create factory --color 5319E7 --description "Build this with the software factory"
gh label create factory:needs-info --color FBCA04 --description "The factory asked the author a question"
gh label create factory:needs-human --color D93F0B --description "The factory needs a human decision on the PR"
```

## 3. Verify

1. In the repo root, on the current branch, `bash factory/checks.sh` exits 0.
   If it fails there, the factory can never pass a job: fix the script (not the
   project) or tell the user what's broken.
2. `factory/bin/job queue` runs without an error.
3. `python3 -m json.tool factory/config.json` succeeds.
4. `git check-ignore factory/jobs/x .worktrees/x` prints both paths, and
   `git status --porcelain --untracked-files=all` lists the files in `factory/`
   as committable.

## 4. Hand over

Stay on the branch the user is on: don't create or check out another branch.
Stage the install with explicit paths, mark the scripts executable in the
index, commit it with a one-line message, and show the user the diff:

```bash
git add factory AGENTS.md .gitignore .gitattributes   # plus CLAUDE.md if you edited it
git update-index --chmod=+x factory/checks.sh factory/bin/job factory/bin/gate factory/bin/route
``` Ask before pushing: the factory branches every job from
`origin/<base_branch>`, so the install must be on that branch there before the
first run.

Then tell the user, in a few lines:

- Label one or two small issues `factory`, then run
  `/sf:factory run` from the repo root.
- Every job ends as a PR. The approver merges what it approves; the rest wait
  labeled `factory:needs-human`. Approve one by merging it on GitHub, or tell
  the factory what to change with `/sf:factory <anything>`.
- Intake runs on Fable, once per issue. Depending on their plan, Fable can
  bill to usage credits rather than the plan's included usage.
- To start carefully, set `concurrency` to 1 in `factory/config.json` and read
  every PR until they trust it.
