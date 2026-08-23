#!/usr/bin/env python3
"""Vocabulary denylist gate — fail if any tracked file carries a banned term.

The banned vocabulary is private-deployment identity that must never appear in
this open repository: the pre-rename repo/service names, the private
deployment's name for the human principal (the neutral term is "operator"),
personal identifiers, absolute home paths, and session-header markers.

Deliberately NOT banned (allowed product concepts the patterns below must not
match): "role playbook", "docs/handoffs", "docs/closeouts",
"docs/design-reviews", and the bare word "bus".

Terms are assembled from string fragments so this file never contains a banned
term verbatim — the scan therefore covers every tracked file, this one
included, with no self-exemption.

NUL-safe: files are read and scanned as raw bytes (a NUL byte hides a file
from some grep builds; it cannot hide one from this scan).

Exit 0 = clean; 1 = banned term(s) found; 2 = setup error.
Usage: python3 scripts/check-denylist.py   (run from anywhere inside the repo)
"""
import re
import subprocess
import sys


def j(*parts: str) -> str:
    """Assemble a term from fragments (keeps this file scan-clean)."""
    return "".join(parts)


# Case-sensitive whole words.
WORDS_CS = [
    j("BO", "SS"),
    j("Ha", "med"),
]

# Case-insensitive substrings.
SUBSTR_CI = [
    j("hame", "ddk"),
    j("esmi", "ley"),
    j("satt", "ari"),
    j("mythical", "-project"),
    j("agent", "-playbooks"),
    j("agent", "-skills"),
    j("agent", "-remote-mcp"),
    j("agent", "-local-mcp"),
    j("agent", "-daemon"),
    j("agent", "-web"),
    j("mythical", "-server"),
    j("mythical", "-bus"),
    j("mythical-asg", "ard"),
    j("asg", "ard"),
    j("de", "-net"),
    j("de", "net"),
    j("saas", "-draft"),
    j("mythical", "-master-plan"),
    j("/Us", "ers/"),
    j("Claude", "-Session:"),
]

PATTERNS = (
    [(re.compile(rb"\b" + re.escape(w.encode()) + rb"\b"), w) for w in WORDS_CS]
    + [(re.compile(re.escape(s.encode()), re.IGNORECASE), s) for s in SUBSTR_CI]
)


def tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z"], capture_output=True, check=True
    ).stdout
    return [p.decode() for p in out.split(b"\0") if p]


def main() -> int:
    try:
        files = tracked_files()
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"DENYLIST-CHECK: cannot list tracked files: {e}", file=sys.stderr)
        return 2

    hits = 0
    for path in files:
        try:
            data = open(path, "rb").read()
        except (IsADirectoryError, FileNotFoundError):
            continue  # submodule pointer or racing deletion
        for lineno, line in enumerate(data.split(b"\n"), 1):
            for pattern, term in PATTERNS:
                if pattern.search(line):
                    hits += 1
                    print(f"DENYLIST-CHECK FAIL {path}:{lineno}: banned term "
                          f"'{term}'", file=sys.stderr)

    if hits:
        print(f"DENYLIST-CHECK: {hits} banned hit(s).", file=sys.stderr)
        return 1
    print(f"denylist check OK ({len(files)} tracked files, 0 banned hits)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
