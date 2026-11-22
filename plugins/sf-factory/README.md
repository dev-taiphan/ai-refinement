# sf-factory: GitHub issues to pull requests

Builds GitHub issues labeled `factory` into PRs with a pipeline of Claude
subagents: intake → spec → build → gate → review → approve. The approver merges
what it is confident about and hands the rest to a human.

## Requirements

- Claude Code 2.1.257 or later
- `python3` 3.10+ on PATH (on Windows, a real Python; `/sf-factory:init` can
  point the scripts at `python` instead)
- `gh`, authenticated with push and label access to the repo
- Git Bash on Windows (the scripts and `checks.sh` run under bash)

## Use

In each repo, once:

```
/sf-factory:init
```

It copies `factory/` into the repo, fills `factory/checks.sh` with the repo's
checks, adds the factory notes to `AGENTS.md`, updates `.gitignore` and
`.gitattributes`, creates the GitHub labels and commits. Push that commit to the
default branch.

Then:

```
/sf-factory:factory run        every open issue labeled `factory`
/sf-factory:factory run 12     one issue
/sf-factory:factory <anything> ask, give feedback, file a feature
```

Dashboard: `cd factory && python3 -m http.server`, then open
http://localhost:8000/dashboard.html.

## Layout

```
skills/factory/SKILL.md   the orchestrator
skills/init/SKILL.md      per-repo installer
agents/                   intake, spec-writer, builder, reviewer-code, -security, -ux, -ui, approver
templates/factory/        copied into each repo by init: config, checks.sh, bin/job, gate, route, dashboard
```

## Design notes

- The plugin ships no hooks. The builder runs `checks.sh` itself before it
  finishes, and the gate runs it again after.
- The orchestrator spawns agents as `sf-factory:<agent>`.
- Project-specific tailoring goes in the repo's `AGENTS.md` instead of editing
  the agents, which are shared across repos.
