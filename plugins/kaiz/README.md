# kaiz: ticket analysis for Claude Code

`/kaiz:analyze` reads a ticket from your repo, studies the code it touches, and
writes a set of design documents next to it. Every claim about existing code is
cited as `path:line`, and a checker agent confirms each citation points at a
real file and line. The plugin never changes your code, never runs a build, and
needs no GitHub access.

## Use

Put a ticket in `.issues/<ticket>/ticket.md`, with any screenshots or notes in
the same folder, then run:

```
/kaiz:analyze 123              one ticket
/kaiz:analyze 123 <notes>      with extra instructions for the analysts
/kaiz:analyze                  every ticket not analysed yet or changed since
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
08-performance.md          hot paths, costs, budgets, how to measure
approval.md                your decision, written by /kaiz:approve
```

A rerun keeps the previous analysis as `output-<timestamp>/`. Documents are
written in the language the ticket is written in.

## Approve a plan

The analysis proposes; you decide. `/kaiz:approve` shows a short brief (verdict,
risk, size, security and performance ratings, the proposed solution, open
questions) and records your decision in `output/approval.md`:

```
/kaiz:approve 123                          approve
/kaiz:approve 123 <conditions>             approve with conditions
/kaiz:approve 123 reject <reason>          request changes
/kaiz:approve 123 status                   show the decision on file
```

It refuses to approve a ticket whose analysis is `STOPPED` or whose verdict is
NO-GO, and asks you to confirm when the analysis has gaps, open questions, a
`high` security or performance rating, or is older than the ticket. A rerun of
`/kaiz:analyze` moves the old decision with the old analysis, so a new analysis
needs a new decision. It changes no code.

## How it stays tied to your code

1. Each analyst must read the code before citing it, and lists what it only
   inferred under **Assumptions**.
2. `ref-checker` verifies every `path:line` citation exists; authors fix broken
   ones once.
3. `analysis-reviewer` re-reads the most important citations and checks the
   documents agree: the plan changes the files the impact analysis lists, every
   acceptance criterion has a test, every security and performance requirement
   is planned.

## Agents

`ticket-analyst`, `impact-analyst`, `dataflow-analyst`, `security-analyst`,
`performance-analyst`, `tech-spec-writer`, `test-planner`, `ref-checker`,
`analysis-reviewer`. They only read your repo and write files under
`.issues/<ticket>/output/`.
