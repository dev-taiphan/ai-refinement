# sf: software factory (Claude Code plugin)

Builds GitHub issues labeled `factory` into PRs with a pipeline of Claude
subagents: intake → spec → build → gate → review → approve.
**Hướng dẫn tiếng Việt đầy đủ (cài đặt và sử dụng): [HUONG-DAN.md](HUONG-DAN.md).**

Works in the Claude Code terminal (TUI), the VS Code extension and local
sessions of the Claude Code desktop app. Not in cloud or WSL sessions.

## Requirements

- Claude Code 2.1.257 or later
- `python3` 3.10+ on PATH (on Windows, a real Python, not the Store alias)
- `gh`, authenticated with push and label access to the repo
- Git Bash on Windows (the scripts and `checks.sh` run under bash)

## Install

From GitHub, after pushing this folder to a repo:

```
/plugin marketplace add <owner>/<repo>
/plugin install sf@ai-factory
```

From a local folder:

```
/plugin marketplace add ./path/to/ai-factory-plugin
/plugin install sf@ai-factory
```

To try it for one session without installing: `claude --plugin-dir ./path/to/ai-factory-plugin`.

## Use

In each repo, once:

```
/sf:init
```

It copies `factory/` into the repo, fills `factory/checks.sh` with the repo's
checks, adds the factory notes to `AGENTS.md`, updates `.gitignore`, creates
the GitHub labels and commits. Push that commit to the default branch.

Then:

```
/sf:factory run        every open issue labeled `factory`
/sf:factory run 12     one issue
/sf:factory <anything> ask, give feedback, file a feature
```

Dashboard: `cd factory && python3 -m http.server`, then open
http://localhost:8000/dashboard.html.

## Analyse local tickets

No GitHub, no code changes, no init needed. Put a ticket in
`.issues/<ticket>/ticket.md` (plus any screenshots or notes in the same
folder), then:

```
/sf:analyze 123              one ticket
/sf:analyze 123 <notes>      with extra instructions
/sf:analyze                  every ticket not analysed yet or changed since
```

The analysis lands in `.issues/<ticket>/output/`:

```
00-summary.md              overall result, index, inconsistencies, open questions
01-assessment.md           GO / NEEDS-INFO / NO-GO, scope, risk, codebase map
02-impact-analysis.md      files, dependents, contracts, migration
03-data-flow.md            flows today and after (mermaid), models, trust boundaries
04-tech-spec.md            acceptance criteria and design
05-implementation-plan.md  ordered steps by file
06-test-plan.md            test cases mapped to acceptance criteria
07-security.md             risks and requirements
```

Every claim about existing code is cited as `path:line`;
`scripts/check_refs.py` checks each citation against the repo, the authors
fix broken ones, and the reviewer confirms the citations mean what's claimed.
A rerun keeps the previous analysis as `output-<timestamp>/`.

## Layout

```
.claude-plugin/plugin.json        manifest
.claude-plugin/marketplace.json   this folder is also its own marketplace
skills/factory/SKILL.md           the orchestrator
skills/init/SKILL.md              per-repo installer
skills/analyze/SKILL.md           local ticket analysis
agents/                           factory: intake, spec-writer, builder, 4 reviewers, approver
                                  analysis: ticket-analyst, impact-analyst, dataflow-analyst,
                                  security-analyst, tech-spec-writer, test-planner, analysis-reviewer
scripts/check_refs.py             checks every `path:line` citation in an analysis
templates/factory/                copied into each repo by init
```

## Design notes

- The plugin ships no hooks: the directory accepts command hooks only from
  verified organizations. The builder runs `checks.sh` itself before it
  finishes, and the gate runs it again after.
- The orchestrator spawns agents as `sf:<agent>`.
- Project-specific tailoring goes in the repo's `AGENTS.md` instead of editing
  the agents, which are shared across repos.
