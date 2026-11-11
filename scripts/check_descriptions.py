#!/usr/bin/env python3
"""check_descriptions.py -- keep the always-loaded `description` front matter short.

    python3 scripts/check_descriptions.py              # check skills/, agents/, commands/
    python3 scripts/check_descriptions.py --selftest   # offline; also runs the repository check

Every skill, agent and command `description` is loaded into the context of every session (Claude Code and
Codex), so its length is paid on every turn. Target: <= ~300 characters (what it does + when to use it,
keeping the trigger keywords); this check fails above LIMIT = 350, or when a description is missing.
Prints the total, which is the always-loaded cost in characters.
"""
from __future__ import annotations

import glob
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIMIT = 350
PATTERNS = ["skills/*/SKILL.md", "agents/*.md", "commands/*.md"]


def description(text: str) -> str | None:
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    if not m:
        return None
    d = re.search(r"^description:[ \t]*(.*(?:\n[ \t]+.*)*)", m.group(1), re.M)
    return re.sub(r"\s+", " ", d.group(1)).strip().strip('"\'') if d else None


def run(root: str = ROOT, out=sys.stdout) -> int:
    bad, total, n = 0, 0, 0
    for pat in PATTERNS:
        for p in sorted(glob.glob(os.path.join(root, pat))):
            rel = os.path.relpath(p, root)
            d = description(open(p, encoding="utf-8").read())
            n += 1
            if not d:
                print(f"FAIL {rel}: no description", file=out); bad += 1
                continue
            total += len(d)
            if len(d) > LIMIT:
                print(f"FAIL {rel}: description is {len(d)} chars (limit {LIMIT}, target ~300)", file=out); bad += 1
    print(f"checked {n} descriptions, {total} chars always loaded: {bad} problem(s)", file=out)
    return 1 if bad else 0


def selftest() -> int:
    assert description("---\nname: x\ndescription: short one\n---\nbody") == "short one"
    assert description("---\ndescription: a\n  continued\nmodel: inherit\n---\n") == "a continued"
    assert description("no front matter") is None
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "skills", "s"))
        os.makedirs(os.path.join(tmp, "agents"))
        open(os.path.join(tmp, "skills", "s", "SKILL.md"), "w").write("---\nname: s\ndescription: ok\n---\n")
        open(os.path.join(tmp, "agents", "a.md"), "w").write("---\nname: a\ndescription: " + "x" * 351 + "\n---\n")
        sink = open(os.devnull, "w")
        assert run(tmp, sink) == 1
        open(os.path.join(tmp, "agents", "a.md"), "w").write("---\nname: a\ndescription: " + "x" * 300 + "\n---\n")
        assert run(tmp, sink) == 0
        open(os.path.join(tmp, "agents", "b.md"), "w").write("---\nname: b\n---\n")
        assert run(tmp, sink) == 1
    print("selftest: synthetic checks passed; repository:")
    return run()


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    return selftest() if "--selftest" in argv else run()


if __name__ == "__main__":
    sys.exit(main())
