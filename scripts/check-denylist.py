#!/usr/bin/env python3
"""Vocabulary denylist gate — fail if any tracked file carries a banned term.

The banned vocabulary is private-deployment identity that must never appear in
this open repository. The terms themselves are NOT in this file, or anywhere in
the tree: they arrive through the environment, from the organisation's Actions
secrets —

  DOCS_DENY_PATTERN     case-insensitive extended regex (the main list)
  DOCS_DENY_PATTERN_CS  case-sensitive extended regex (all-caps monikers,
                        session-header markers, home paths)
  DOCS_DENY_PROBE       one term per line that DOCS_DENY_PATTERN must match
  DOCS_DENY_PROBE_CS    one term per line that DOCS_DENY_PATTERN_CS must match

The probes are the self-test: a pattern that no longer matches a term it is
supposed to cover fails the run loudly instead of passing every file silently.
Nothing here ever prints a pattern or a probe — only pass/fail, a file:line,
and a probe index.

Deliberately NOT banned (product concepts of this repo that the main pattern
may name for other repositories): "role playbook", "docs/handoffs",
"docs/closeouts", "docs/design-reviews". A match whose matched text is exactly
one of those is exempt; the same word anywhere else in a line still fails.

NUL-safe: files are read and scanned as raw bytes (a NUL byte hides a file
from some grep builds; it cannot hide one from this scan). Covers every
tracked file, this one included — there is nothing here to exempt.

Exit 0 = clean; 1 = banned term(s) found or self-test failed; 2 = setup error
(a required secret is unset — fail closed). Set DENYLIST_SKIP_SECRETS=1 to
run without secrets (fork pull requests, where secrets are unavailable);
the run then reports the skip and exits 0, and maintainer review covers it.

Usage: python3 scripts/check-denylist.py   (run from anywhere inside the repo)
"""
from __future__ import annotations

import os
import re
import subprocess
import sys

ALLOWED_CONCEPTS = {
    "role playbook",
    "docs/handoffs",
    "docs/closeouts",
    "docs/design-reviews",
}


def tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files", "-z"], capture_output=True, check=True
    ).stdout
    return [p.decode() for p in out.split(b"\0") if p]


def compile_or_die(name: str, flags: int) -> re.Pattern[bytes]:
    raw = os.environ.get(name, "")
    if not raw.strip():
        print(f"DENYLIST-CHECK: {name} is unset or empty — failing closed",
              file=sys.stderr)
        sys.exit(2)
    try:
        return re.compile(raw.encode(), flags)
    except re.error as e:
        print(f"DENYLIST-CHECK: {name} is not a usable pattern ({e.msg})",
              file=sys.stderr)
        sys.exit(2)


def self_test(name: str, rx: re.Pattern[bytes], probe_var: str) -> None:
    probes = [p for p in os.environ.get(probe_var, "").splitlines() if p.strip()]
    if not probes:
        print(f"DENYLIST-CHECK: {probe_var} holds no probes — failing closed",
              file=sys.stderr)
        sys.exit(2)
    for i, p in enumerate(probes, 1):
        if not rx.search(p.encode()):
            print(f"DENYLIST-CHECK: self-test failed — {name} does not cover "
                  f"probe #{i}; the gate is weaker than declared",
                  file=sys.stderr)
            sys.exit(1)
    print(f"self-test OK: {name} covers {len(probes)} probe(s)")


def main() -> int:
    if os.environ.get("DENYLIST_SKIP_SECRETS") == "1":
        print("denylist check SKIPPED: secrets unavailable (fork pull request); "
              "maintainer review covers this lane")
        return 0

    ci = compile_or_die("DOCS_DENY_PATTERN", re.IGNORECASE)
    cs = compile_or_die("DOCS_DENY_PATTERN_CS", 0)
    self_test("DOCS_DENY_PATTERN", ci, "DOCS_DENY_PROBE")
    self_test("DOCS_DENY_PATTERN_CS", cs, "DOCS_DENY_PROBE_CS")

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
            for rx in (ci, cs):
                for m in rx.finditer(line):
                    if m.group(0).decode("utf-8", "replace").lower() in ALLOWED_CONCEPTS:
                        continue
                    hits += 1
                    print(f"DENYLIST-CHECK FAIL {path}:{lineno}: banned term "
                          f"(redacted; line is {len(line)} bytes)", file=sys.stderr)
                    break

    if hits:
        print(f"DENYLIST-CHECK: {hits} banned hit(s).", file=sys.stderr)
        return 1
    print(f"denylist check OK ({len(files)} tracked files, 0 banned hits)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
