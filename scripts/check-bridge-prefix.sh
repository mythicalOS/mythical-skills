#!/usr/bin/env bash
# check-bridge-prefix.sh — fail if any tracked file names the RETIRED bridge
# MCP server prefix.
#
# The coordination bridge is registered under exactly ONE server key, so a tool
# name built on the retired prefix resolves to nothing: a permission string or a
# documented tool name carrying it is a false promise, not a compatibility
# window. Skills ship onto deployments that only know the current name, so the
# retired prefix must never re-enter shipped content once one bridge name
# exists.
#
# The prefix is assembled from two string fragments, so this file never
# contains it verbatim and needs no self-exemption — the scan covers every
# tracked file, this one included (the check-denylist.py idiom).
#
# Reads EVERY tracked file with `grep -a` over a NUL-delimited `git ls-files`
# list: `-a` cannot be defeated by a NUL byte, and `-z` cannot be defeated by a
# newline in a path.
#
# Read-only. Exit 0 = clean; 1 = hit(s); 2 = usage/setup error.
# Usage: scripts/check-bridge-prefix.sh [repo-root]   (default: this repo)
#        scripts/check-bridge-prefix.sh --selftest
set -uo pipefail

GREP=/usr/bin/grep
[ -x "$GREP" ] || GREP=grep

# The retired prefix, assembled from fragments.
PREFIX="mcp__""mythical__"

SELFTEST_TMP=""
cleanup_selftest() { [ -n "$SELFTEST_TMP" ] && rm -rf "$SELFTEST_TMP"; }

selftest() {
  local tmp seeded out rc
  tmp="$(mktemp -d)" || return 2
  SELFTEST_TMP="$tmp"
  trap cleanup_selftest EXIT

  # Stage a copy of this repo's tracked files as a standalone git repo.
  local root
  root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  mkdir -p "$tmp/clean"
  ( cd "$root" && git ls-files -z ) | while IFS= read -r -d '' f; do
    mkdir -p "$tmp/clean/$(dirname "$f")"
    cp "$root/$f" "$tmp/clean/$f" 2>/dev/null || true
  done
  ( cd "$tmp/clean" && git init -q . && git add -A ) >/dev/null 2>&1 || {
    echo "SELFTEST FAIL: could not stage a temp repo" >&2; return 1; }

  # 1. The assembled prefix is the one we mean to ban. Seeding the fixture from
  #    $PREFIX alone would be circular — any typo would be self-consistent — so
  #    the shape is pinned against INDEPENDENT fragments here.
  local head mid
  head="${PREFIX%%__*}"
  mid="${PREFIX#*__}"; mid="${mid%__}"
  if [ "$head" != "mcp" ] || [ "$mid" != "myth""ical" ] \
     || [ "${PREFIX: -2}" != "__" ] || [ "${#PREFIX}" -ne 15 ]; then
    echo "SELFTEST FAIL: assembled prefix is not the retired bridge server name" >&2
    return 1
  fi

  # 2. The unseeded copy is clean.
  if ! bash "${BASH_SOURCE[0]}" "$tmp/clean" >/dev/null 2>&1; then
    echo "SELFTEST FAIL: unseeded staged copy did not pass" >&2
    bash "${BASH_SOURCE[0]}" "$tmp/clean" >&2
    return 1
  fi

  # 3. One seeded line in a real skill file fails, naming that file:line.
  seeded="$tmp/clean/skills/routed-comms/SKILL.md"
  [ -f "$seeded" ] || { echo "SELFTEST FAIL: fixture file missing: $seeded" >&2; return 1; }
  printf '%s\n' "call ${PREFIX}coordination_publish to route it" >> "$seeded"
  out="$(bash "${BASH_SOURCE[0]}" "$tmp/clean" 2>&1)"; rc=$?
  if [ "$rc" -ne 1 ]; then
    echo "SELFTEST FAIL: seeded copy exited $rc, expected 1" >&2
    printf '%s\n' "$out" >&2; return 1
  fi
  if ! printf '%s' "$out" | "$GREP" -q "skills/routed-comms/SKILL.md:"; then
    echo "SELFTEST FAIL: seeded hit did not name skills/routed-comms/SKILL.md:<line>" >&2
    printf '%s\n' "$out" >&2; return 1
  fi

  echo "selftest OK (3 cases)"
  return 0
}

if [ "${1:-}" = "--selftest" ]; then
  selftest
  exit $?
fi

ROOT="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
if [ ! -d "$ROOT" ]; then
  echo "BRIDGE-PREFIX-CHECK: not a directory: $ROOT" >&2
  exit 2
fi

cd "$ROOT" || exit 2
if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "BRIDGE-PREFIX-CHECK: not a git repository: $ROOT" >&2
  exit 2
fi

hits=0
count=0
while IFS= read -r -d '' f; do
  count=$((count + 1))
  [ -f "$f" ] || continue        # submodule pointer or racing deletion
  while IFS= read -r line; do
    hits=$((hits + 1))
    echo "BRIDGE-PREFIX FAIL $f:$line" >&2
  done < <("$GREP" -a -n -- "$PREFIX" "$f" 2>/dev/null)
done < <(git ls-files -z)

if [ "$hits" -gt 0 ]; then
  echo "BRIDGE-PREFIX-CHECK: $hits hit(s) of the retired bridge server prefix." >&2
  exit 1
fi
echo "bridge-prefix check OK ($count tracked files, 0 hits)"
exit 0
