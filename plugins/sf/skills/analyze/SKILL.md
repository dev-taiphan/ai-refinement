---
name: analyze
description: Analyse local tickets against the codebase without writing code. Use when the user types /sf:analyze, /sf:analyze <ticket>, or asks to analyse a ticket in .issues/<ticket>/ticket.md. Writes assessment, impact analysis, data flow, tech spec, implementation plan, test plan, security review and a summary to .issues/<ticket>/output/.
---

# Analyze

You orchestrate the analysis of local tickets. A ticket is a folder
`.issues/<ticket>/` in the repo root holding `ticket.md` and optionally other
files (screenshots, logs, notes). The analysis goes to
`.issues/<ticket>/output/`. Nothing else changes: no code, no branches, no
commits, no GitHub. You never write the documents yourself; the agents do, and
every claim they make is tied to the codebase with `path:line` citations that
a script checks.

```
/sf:analyze                    every ticket that has no analysis yet or changed since
/sf:analyze <ticket>           one ticket, e.g. 123 or PROJ-42
/sf:analyze <ticket> <notes>   one ticket, with extra instructions for the analysts
```

## Setup

- `<repo>` is `git rev-parse --show-toplevel`, or the current directory if it
  isn't a git repo. Every path below is under it.
- With no ticket given, list the folders in `<repo>/.issues/` that hold a
  `ticket.md` and either have no `output/00-summary.md` or whose `ticket.md`
  is newer than it. Show the list, then analyse them one at a time.
- With a ticket given, check `<repo>/.issues/<ticket>/ticket.md` exists. If it
  doesn't, list the tickets that do exist and stop.
- If `output/` already holds files, rename it to `output-<YYYYMMDD-HHMMSS>/`
  (its modification time) so the earlier analysis is kept, then start fresh.
  Create `output/`.

## Spawning agents

Spawn each agent with the Agent tool, in the background, with
`subagent_type` `sf:<name>` and no `model` (their frontmatter
sets it). Every prompt starts with the ticket header:

```
Ticket: <ticket>. Ticket folder: <repo>/.issues/<ticket>/. Output folder: <repo>/.issues/<ticket>/output/. Repo root: <repo>.
```

If the user gave notes, add `Notes from the user: <their notes, verbatim>` on
the next line. Never paste ticket text into a prompt; the agents read it from
the file.

Each agent replies with one line. You're notified when it finishes. While
agents run, don't poll: end your turn with a one-line status. Report one line
per step, e.g. `123: assessment GO (risk medium, ui, api) → impact, data flow, security`.

## Steps

1. **Assess.** Spawn `ticket-analyst`. Read its reply (the `VERDICT:` line).
   - `NO-GO`: go to step 5.
   - `GO` or `NEEDS-INFO`: go on. NEEDS-INFO analyses continue on the
     assessment's stated assumptions.
2. **Analyse.** Spawn `impact-analyst`, `dataflow-analyst` and
   `security-analyst` in one message, so they run in parallel. Wait for all
   three.
3. **Design.** Spawn `tech-spec-writer`. If it replies `SPEC: blocked`, go to
   step 5.
4. **Test.** Spawn `test-planner`.
5. **Check references.** Spawn `ref-checker` with the header. It replies
   `REFS: PASS` or `REFS: FAIL` followed by one `FAIL` line per problem.

   On `REFS: FAIL`, group the `FAIL` lines by document and spawn each
   document's author again, in one message, with the header and:
   `Your document <file> has broken code references. Fix only these, by reading the code and citing the right lines, and leave the rest of the document as it is:` followed by its `FAIL` lines.
   Authors: 01 `ticket-analyst`, 02 `impact-analyst`, 03 `dataflow-analyst`,
   04 and 05 `tech-spec-writer`, 06 `test-planner`, 07 `security-analyst`.
   Then spawn `ref-checker` once more. Don't loop further.
6. **Review.** Spawn `analysis-reviewer` with the header and
   `Reference check: <the checker's last reply, with any FAIL lines>`.
7. **Report.** Print the first two lines of `00-summary.md`, its `## Summary`
   bullets, the open questions if any, and the path of the output folder.

Analyse one ticket at a time. When several are queued, start the next after
step 7.

## Documents

```
output/00-summary.md              analysis-reviewer: overall result, index, issues, open questions
output/01-assessment.md           ticket-analyst: verdict, scope, risk, surfaces, codebase map
output/02-impact-analysis.md      impact-analyst: files, dependents, contracts, migration
output/03-data-flow.md            dataflow-analyst: flows today and after, models, trust boundaries
output/04-tech-spec.md            tech-spec-writer: acceptance criteria and design
output/05-implementation-plan.md  tech-spec-writer: ordered steps by file
output/06-test-plan.md            test-planner: cases mapped to acceptance criteria
output/07-security.md             security-analyst: risks and requirements
```

## Questions about an analysis

When the user asks about a ticket's analysis rather than running one, answer
from its `output/` documents, reading them in full as needed, and cite them.
This plugin only analyses; it never changes code. To build from an analysis,
the user can follow `05-implementation-plan.md` step by step, or, with the
`sf-factory` plugin installed, file the ticket as a GitHub issue labeled
`factory` and run `/sf-factory:factory run <n>`.
