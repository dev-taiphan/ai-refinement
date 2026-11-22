#!/usr/bin/env python3
"""Check that an analysis is grounded in the codebase.

Usage:
  check_refs.py <output-dir> <repo-root>

Every inline code span of the form `path:LINE` or `path:START-END` in the
output-dir's *.md files must name a file under repo-root that has those lines.
Every document except 00-summary.md must cite at least one such reference.
Spans inside fenced code blocks are not checked.

Prints one `FAIL <doc>: <problem>` line per problem, then `REFS: PASS` or
`REFS: FAIL`. Exits 0 on PASS, 1 on FAIL, 2 on bad usage.
"""

import re
import sys
from pathlib import Path

FENCE = re.compile(r"^(```|~~~).*?^\1", re.S | re.M)
SPAN = re.compile(r"`([^`\n]+)`")
REF = re.compile(r"^(?P<path>[^\s:`*?<>|\"]+):(?P<start>\d+)(?:-(?P<end>\d+))?$")
EXEMPT = {"00-summary.md"}


def looks_like_path(path):
    return "/" in path or "\\" in path or re.search(r"\.[A-Za-z0-9]+$", path)


def check(output_dir, repo):
    problems, total, docs = [], 0, 0
    line_counts = {}
    for doc in sorted(output_dir.glob("*.md")):
        docs += 1
        text = FENCE.sub("", doc.read_text(encoding="utf-8", errors="replace"))
        found = 0
        for span in SPAN.findall(text):
            m = REF.match(span.strip())
            if not m or not looks_like_path(m["path"]):
                continue
            found += 1
            rel = m["path"].replace("\\", "/").removeprefix("./")
            start = int(m["start"])
            end = int(m["end"] or start)
            target = (repo / rel).resolve()
            if repo not in target.parents and target != repo:
                problems.append(f"{doc.name}: `{span}` is outside the repo")
                continue
            if not target.is_file():
                problems.append(f"{doc.name}: `{span}` names a file that doesn't exist")
                continue
            if target not in line_counts:
                line_counts[target] = len(target.read_text(encoding="utf-8", errors="replace").splitlines())
            n = line_counts[target]
            if start < 1 or end < start or end > n:
                problems.append(f"{doc.name}: `{span}` is out of range ({rel} has {n} lines)")
        total += found
        if found == 0 and doc.name not in EXEMPT:
            problems.append(f"{doc.name}: cites no code as `path:line`")
    return problems, total, docs


def main(argv):
    if len(argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(2)
    output_dir, repo = Path(argv[0]), Path(argv[1]).resolve()
    if not output_dir.is_dir():
        print(f"check_refs: {output_dir} is not a directory", file=sys.stderr)
        sys.exit(2)
    problems, total, docs = check(output_dir, repo)
    for p in problems:
        print(f"FAIL {p}")
    if problems:
        print(f"REFS: FAIL ({len(problems)} problems, {total} references in {docs} documents)")
        sys.exit(1)
    print(f"REFS: PASS ({total} references in {docs} documents)")


if __name__ == "__main__":
    main(sys.argv[1:])
