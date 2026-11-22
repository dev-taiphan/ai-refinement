# sf: ticket analysis for Claude Code

`/sf:analyze` reads a ticket from your repo, studies the code it touches, and
writes a set of design documents next to it. Every claim about existing code is
cited as `path:line`, and a checker agent confirms each citation points at a
real file and line. The plugin never changes your code, never runs a build, and
needs no GitHub access.

## Use

Put a ticket in `.issues/<ticket>/ticket.md`, with any screenshots or notes in
the same folder, then run:

```
/sf:analyze 123              one ticket
/sf:analyze 123 <notes>      with extra instructions for the analysts
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

A rerun keeps the previous analysis as `output-<timestamp>/`. Documents are
written in the language the ticket is written in.

## How it stays tied to your code

1. Each analyst must read the code before citing it, and lists what it only
   inferred under **Assumptions**.
2. `ref-checker` verifies every `path:line` citation exists; authors fix broken
   ones once.
3. `analysis-reviewer` re-reads the most important citations and checks the
   documents agree: the plan changes the files the impact analysis lists, every
   acceptance criterion has a test, every security requirement is planned.

## Agents

`ticket-analyst`, `impact-analyst`, `dataflow-analyst`, `security-analyst`,
`tech-spec-writer`, `test-planner`, `ref-checker`, `analysis-reviewer`. They
only read your repo and write files under `.issues/<ticket>/output/`.
