#!/usr/bin/env bash
# check-project-agnostic.sh — fail if any SKILL.md carries consuming-project or
# deployment-host-binding facts.
#
# Skills ship with the framework onto ANY target repo, so they must keep the
# framework vocabulary (roles, rhythms, gates, routing, bus) but must NOT assert
# a single host/deployment ("Reviewer is Codex-only in this project", "runs on
# Claude", "start-agent.sh spawns claude only") or carry internal dev-milestone
# tags ("added in Phase 4", "Take 3 §C.1"). A host-binding assertion is not only
# project-leakage — it is a FALSE invariant for the next deployment that wires
# roles differently. Enforces skill-authoring §"Brand-free + project-agnostic".
#
# Read-only. Exit 0 = clean; 1 = violation(s); 2 = usage/setup error.
# Usage: scripts/check-project-agnostic.sh [skills-dir]   (default: ../skills next to this script)
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# --selftest: regression cases for the endpoint gate, on scratch fixtures.
if [ "${1:-}" = "--selftest" ]; then
  TMP="$(mktemp -d)"
  trap 'rm -rf "$TMP"' EXIT
  mk() { mkdir -p "$TMP/$1/skills/s1"; printf '%s\n' "$2" > "$TMP/$1/skills/s1/SKILL.md"; }
  mk clean 'plain procedure text, no bindings'
  mk url 'curl -sS -X POST http://127.0.0.1:7800/review/run'
  mk urlok 'curl -sS -X POST "${AGENT_REVIEW_URL:-http://127.0.0.1:7800/review/run}"'
  mk urlsneak 'curl -sS http://127.0.0.2:9/x -H "X-Note: ${UNRELATED}"'
  mk url6 'probe http://[::1]:7800/livez for liveness'
  mk url6exp 'probe http://[0:0:0:0:0:0:0:1]:7800/livez for liveness'
  mk url6mapped 'probe http://[::ffff:127.0.0.1]:7800/livez for liveness'
  mk urlnest 'curl "${AGENT_REVIEW_URL:-${MYTHICAL_SCHEME}http://127.0.0.1:7800/review/run}"'
  mk urlcond 'curl "${ENABLE_LOCAL:+http://127.0.0.1:7800/review/run}"'
  mk urlbroken 'curl "${AGENT_REVIEW_URL:-http://127.0.0.1:7800/review/run"'
  pathological="$(printf '${A:-x}%.0s' $(seq 1 40))"'${B:-http://127.0.0.1:7800/x}'
  mk urlcap "curl $pathological"
  if ! "$0" "$TMP/clean/skills" >/dev/null 2>&1; then
    echo "SELFTEST FAIL: clean fixture did not pass" >&2; exit 1
  fi
  out="$("$0" "$TMP/url/skills" 2>&1)"; rc=$?
  if [ "$rc" -ne 1 ] || ! printf '%s' "$out" | grep -q "literal deployment endpoint"; then
    echo "SELFTEST FAIL: bare literal endpoint did not fail with its diagnostic" >&2
    printf '%s\n' "$out" >&2; exit 1
  fi
  if ! "$0" "$TMP/urlok/skills" >/dev/null 2>&1; then
    echo "SELFTEST FAIL: env-override endpoint fixture did not pass" >&2; exit 1
  fi
  out="$("$0" "$TMP/urlsneak/skills" 2>&1)"; rc=$?
  if [ "$rc" -ne 1 ] || ! printf '%s' "$out" | grep -q "literal deployment endpoint"; then
    echo "SELFTEST FAIL: bare endpoint with unrelated \${...} on the line was not flagged" >&2
    printf '%s\n' "$out" >&2; exit 1
  fi
  out="$("$0" "$TMP/url6/skills" 2>&1)"; rc=$?
  if [ "$rc" -ne 1 ] || ! printf '%s' "$out" | grep -q "literal deployment endpoint"; then
    echo "SELFTEST FAIL: IPv6 loopback endpoint was not flagged" >&2
    printf '%s\n' "$out" >&2; exit 1
  fi
  for six in url6exp url6mapped; do
    out="$("$0" "$TMP/$six/skills" 2>&1)"; rc=$?
    if [ "$rc" -ne 1 ] || ! printf '%s' "$out" | grep -q "literal deployment endpoint"; then
      echo "SELFTEST FAIL: $six IPv6 literal endpoint was not flagged" >&2
      printf '%s\n' "$out" >&2; exit 1
    fi
  done
  if ! "$0" "$TMP/urlnest/skills" >/dev/null 2>&1; then
    echo "SELFTEST FAIL: nested \${...} fallback was falsely flagged" >&2; exit 1
  fi
  out="$("$0" "$TMP/urlcond/skills" 2>&1)"; rc=$?
  if [ "$rc" -ne 1 ] || ! printf '%s' "$out" | grep -q "literal deployment endpoint"; then
    echo "SELFTEST FAIL: conditional \${X:+...} endpoint was not flagged" >&2
    printf '%s\n' "$out" >&2; exit 1
  fi
  out="$("$0" "$TMP/urlbroken/skills" 2>&1)"; rc=$?
  if [ "$rc" -ne 1 ] || ! printf '%s' "$out" | grep -q "literal deployment endpoint"; then
    echo "SELFTEST FAIL: unterminated fallback endpoint was not flagged" >&2
    printf '%s\n' "$out" >&2; exit 1
  fi
  out="$("$0" "$TMP/urlcap/skills" 2>&1)"; rc=$?
  if [ "$rc" -ne 1 ] || ! printf '%s' "$out" | grep -q "literal deployment endpoint"; then
    echo "SELFTEST FAIL: over-cap expansion line was not fail-closed" >&2
    printf '%s\n' "$out" >&2; exit 1
  fi
  echo "selftest OK (11 cases)"
  exit 0
fi

SKILLS_DIR="${1:-$ROOT/skills}"
[ -d "$SKILLS_DIR" ] || { echo "AGNOSTIC-CHECK: skills dir not found: $SKILLS_DIR" >&2; exit 2; }

# Host-binding / single-deployment assertions forbidden in shipped skills.
# (No backticks in the pattern — keep it shell-quoting-safe.)
HOST_RE='in this project|Codex-only|Claude-only|runs on Claude|runs on Codex|start-agent\.sh spawns|spawns claude only|spawns codex only'

# Internal build-history milestone tags — meaningless to a consumer. Targeted to
# dev-history PHRASINGS so a skill's OWN "Phase N" structure (e.g. an investigation
# phase, a PM dialogue phase) is never flagged.
MILESTONE_RE='(added|extracted|introduced|landed|formalized|implemented|wired) in Phase [0-9]|in Phase [0-9]+ alongside|per Take [0-9]|Take [0-9]+ §'

# A literal loopback/host endpoint is a single-deployment binding UNLESS it
# sits inside a ${VAR:-...} deployment-override fallback ON THE SAME LINE —
# a bare URL bakes one deployment's port map into content that ships anywhere.
# The check STRIPS well-formed ${VAR:-...} spans first, so an unrelated ${...}
# elsewhere on the line cannot exempt a bare URL. Covers the whole 127/8
# range, localhost, 0.0.0.0, and IPv6 loopback; keep any fallback on one line.
# The bracketed branch flags ANY IPv6 literal host, not just ::1 — expanded
# loopback ([0:0:0:0:0:0:0:1]), IPv4-mapped ([::ffff:127.0.0.1]), and every
# other literal v6 host are equally single-deployment bindings (documentation
# examples belong on example.com, not a literal address).
URL_RE='https?://(127\.[0-9]+\.[0-9]+\.[0-9]+|localhost|0\.0\.0\.0|\[[0-9A-Fa-f:.]+\])([:/]|$)'

# skill-authoring is the doctrine that NAMES the forbidden host-binding forms as
# examples; exempt it from the host-binding pattern only (still milestone-checked).
HOST_EXEMPT="skill-authoring"

fail=0
count=0
while IFS= read -r f; do
  count=$((count + 1))
  name="$(basename "$(dirname "$f")")"

  if [ "$name" != "$HOST_EXEMPT" ]; then
    if hits="$(grep -nEi "$HOST_RE" "$f")"; then
      echo "AGNOSTIC-CHECK FAIL [$name] host-binding / single-deployment assertion:" >&2
      printf '%s\n' "$hits" | sed 's/^/    /' >&2
      fail=1
    fi
  fi

  if hits="$(grep -nE "$MILESTONE_RE" "$f")"; then
    echo "AGNOSTIC-CHECK FAIL [$name] internal dev-milestone tag:" >&2
    printf '%s\n' "$hits" | sed 's/^/    /' >&2
    fail=1
  fi

  # URL_RE rides in via the environment, NOT `awk -v` — -v assignment
  # escape-processes backslashes (turning `\[::1\]` into a character class and
  # `\.` into any-char), silently corrupting the pattern. Exempt spans are
  # removed by a BRACE-AWARE scan, not a regex — `[^}]*` would stop at the
  # inner `}` of a nested fallback like ${URL:-${SCHEME}http://...} and
  # falsely flag it. ONLY genuine `${IDENT:-...}` fallback spans exempt: other
  # expansion forms (`:+`, `:?`, bare `${X}`) stay visible, since e.g.
  # `${FLAG:+http://127.0.0.1:7800}` still conditionally emits a hard-coded
  # endpoint. An UNTERMINATED fallback keeps the rest of the line verbatim
  # (conservative: its URL stays flagged, and the scan stays linear).
  # Complexity bound: at most 32 expansions per line participate in exemption.
  # Beyond that (an adversarial or degenerate line no real skill carries) the
  # line gets NO exemption — fail-closed, and the scan stays linear without a
  # per-character state machine.
  if hits="$(URL_RE="$URL_RE" awk '{
        line = $0; out = ""; i = 1; n = length(line)
        tmp = line
        if (gsub(/\$\{/, "&", tmp) > 32) {
          if (line ~ ENVIRON["URL_RE"]) print NR ": " $0
          next
        }
        while (i <= n) {
          rest = substr(line, i)
          p = index(rest, "${")
          if (p == 0) { out = out rest; break }
          out = out substr(rest, 1, p - 1)
          i = i + p - 1
          if (match(substr(line, i + 2), /^[A-Za-z_][A-Za-z0-9_]*:-/)) {
            depth = 1; j = i + 2
            while (j <= n && depth > 0) {
              c = substr(line, j, 1)
              if (c == "{") depth++
              else if (c == "}") depth--
              j++
            }
            if (depth == 0) { i = j; continue }
            out = out substr(line, i); break
          }
          out = out "${"; i += 2
        }
        if (out ~ ENVIRON["URL_RE"]) print NR ": " $0
      }' "$f")" && [ -n "$hits" ]; then
    echo "AGNOSTIC-CHECK FAIL [$name] literal deployment endpoint outside a \${VAR:-...} override (fallback must be on the same line):" >&2
    printf '%s\n' "$hits" | sed 's/^/    /' >&2
    fail=1
  fi
done < <(find "$SKILLS_DIR" -name SKILL.md | sort)

if [ "$fail" -eq 0 ]; then
  echo "project-agnostic check OK ($count skills; host-binding + milestone clean)"
else
  echo "AGNOSTIC-CHECK: fix the flagged skills — keep framework vocabulary, drop the deployment/host/milestone specifics. See skill-authoring §\"Brand-free + project-agnostic\"." >&2
fi
exit "$fail"
