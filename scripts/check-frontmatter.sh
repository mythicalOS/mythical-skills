#!/usr/bin/env bash
# check-frontmatter.sh — schema-lint every skill's YAML frontmatter.
#
# The frontmatter is each skill's machine-readable face: the fields are few and
# CLOSED on purpose (`name`, `description`, `assumes` — all three required).
# This lint pins that contract:
#
#   - frontmatter block present, at byte 0, properly terminated
#   - top-level keys: exactly the closed set, no unknowns (a typo'd key like
#     `asumes:` would otherwise be silently ignored forever), no duplicates
#   - `name`: bare kebab-case scalar equal to the skill's directory name
#   - `description`: non-empty (inline scalar or block with indented content)
#   - `assumes`: a list with at least one non-empty item
#   - NUL-safe: files are read as bytes; a NUL byte fails loudly instead of
#     hiding the file from line tools
#
# It grants nothing and authorizes nothing — same posture as SKILLS-INDEX.
# Parsing is deliberately stdlib-regex over the block, not a YAML engine: the
# closed schema is simple enough to pin exactly, and CI needs no extra deps.
#
# Exit 0 = clean; 1 = findings; 2 = setup error.
# Usage: scripts/check-frontmatter.sh [--root <dir>] [--selftest]
set -euo pipefail
cd "$(dirname "$0")/.."

MODE="check"
ROOT_DIR="$PWD"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --selftest) MODE="selftest"; shift ;;
    --root)
      [[ $# -ge 2 ]] || { echo "usage: $0 [--root <dir>] [--selftest]" >&2; exit 2; }
      ROOT_DIR="$2"; shift 2 ;;
    *) echo "usage: $0 [--root <dir>] [--selftest]" >&2; exit 2 ;;
  esac
done

PY=$(mktemp -t check-frontmatter.XXXXXX.py)
trap 'rm -f "$PY"' EXIT
cat > "$PY" <<'PYEOF'
import glob, os, re, sys

root = sys.argv[1]
REQUIRED = ("name", "description", "assumes")
# authority-boundary and rhythm-gating are the corpus's existing boundary/STOP
# contract fields — optional, but when present they must be non-empty lists
# like `assumes`. They state constraints; they never grant anything.
LIST_FIELDS = ("assumes", "authority-boundary", "rhythm-gating")
ALLOWED = set(REQUIRED) | set(LIST_FIELDS)
findings = []

paths = sorted(glob.glob(os.path.join(root, "skills", "*", "SKILL.md")))
if not paths:
    print("FRONTMATTER-CHECK: no skills/*/SKILL.md found", file=sys.stderr)
    sys.exit(2)

for path in paths:
    skill = os.path.basename(os.path.dirname(path))
    with open(path, "rb") as f:
        data = f.read()
    if b"\x00" in data:
        findings.append(f"{skill}: NUL byte in SKILL.md (would hide the file from line tools)")
        continue
    text = data.decode("utf-8", errors="replace")

    m = re.match(r"\A---\n(.*?\n)---\n", text, re.S)
    if not m:
        findings.append(f"{skill}: missing frontmatter (file must open with a '---' block)")
        continue
    block = m.group(1)
    lines = block.split("\n")

    # Tabs in YAML indentation are malformed and would also break this
    # parser's space-based indent arithmetic — reject them outright.
    if any(re.match(r"[ ]*\t", line) for line in lines):
        findings.append(f"{skill}: tab indentation in frontmatter (YAML requires spaces)")
        continue

    def inline_kind(v):
        """Classify an inline value:
        'content' | 'block' | 'empty' | 'malformed' | 'flow'.
        A '#...' value is a YAML comment (null value). A block-scalar header
        may carry only whitespace + a comment after the indicator ('> # note'
        is a header; '| x' and '|x' are malformed). A '['/'{' opener is a flow
        collection — the wrong TYPE for every field here. A value with no word
        character at all ('""', '\\'\\'', punctuation) carries no content."""
        if not v:
            return "empty"
        if v.startswith("#"):
            return "empty"
        if re.fullmatch(r"(null|Null|NULL|~)(\s+#.*)?", v):
            return "empty"  # YAML null aliases (± trailing comment) carry no content
        bm = re.match(r"[|>][+-]?(?:\s+(.*))?$", v)
        if bm:
            rest = (bm.group(1) or "").strip()
            return "block" if not rest or rest.startswith("#") else "malformed"
        if re.match(r"[|>][+-]?\S", v):
            return "malformed"
        if v[0] in "[{":
            return "flow"
        if not re.search(r"\w", v):
            return "empty"
        return "content"

    def non_comment(line):
        s = line.strip()
        return bool(s) and not s.startswith("#")

    def mapping_shaped(text):
        """True when a value opens as a YAML mapping key — quoted, unquoted,
        ASCII or not. A fully-quoted scalar (the colon INSIDE the quotes,
        nothing but the quoted string as the value) is NOT mapping-shaped:
        that is the documented escape hatch for colon-bearing item text.
        Unquoted text containing ':' + space/EOL IS a mapping in YAML even
        with a multi-word key, so it is flagged as one."""
        if text == "?" or text.startswith("? "):
            return True  # YAML's explicit-key indicator opens a mapping entry
        if re.match(r'"(?:[^"\\]|\\.)*"\s*:(\s|$)', text):
            return True
        # Single-quoted keys may contain YAML's doubled-quote escape ('') —
        # `[^']*` alone would stop at the first inner quote and miss the key.
        if re.match(r"'(?:[^']|'')*'\s*:(\s|$)", text):
            return True
        if not text.startswith(('"', "'")) and re.search(r":(\s|$)", text):
            return True
        return False

    # Top-level keys are unindented `key:` lines; everything else in the block
    # must be indented continuation/list content.
    keys = []
    for i, line in enumerate(lines):
        if not line or line.startswith((" ", "\t")):
            continue
        km = re.match(r"([A-Za-z_][A-Za-z0-9_-]*):(.*)$", line)
        if km:
            keys.append((km.group(1), km.group(2).strip(), i))
        else:
            findings.append(f"{skill}: unparseable unindented frontmatter line: {line!r}")

    names = [k for k, _, _ in keys]
    for k in sorted(set(names)):
        if names.count(k) > 1:
            findings.append(f"{skill}: duplicate top-level key '{k}'")
    for k in names:
        if k not in ALLOWED:
            findings.append(f"{skill}: unknown top-level key '{k}' (allowed: {', '.join(sorted(ALLOWED))})")
    for k in REQUIRED:
        if k not in names:
            findings.append(f"{skill}: missing required key '{k}'")

    def body_lines(start):
        """Indented lines belonging to the key at line index `start`."""
        out = []
        for line in lines[start + 1:]:
            if line and not line.startswith((" ", "\t")):
                break
            out.append(line)
        return out

    for k, inline, i in keys:
        if k == "name":
            if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", inline or ""):
                findings.append(f"{skill}: name must be a bare kebab-case scalar, got {inline!r}")
            elif inline != skill:
                findings.append(f"{skill}: name '{inline}' does not match its directory")
            if any(line.strip() for line in body_lines(i)):
                findings.append(f"{skill}: name must be a single bare scalar (indented continuation found)")
        elif k == "description":
            kind = inline_kind(inline)
            if kind == "malformed":
                findings.append(f"{skill}: description has a malformed block indicator: {inline!r}")
            elif kind == "flow":
                findings.append(f"{skill}: description must be a plain or block scalar, got a flow collection: {inline!r}")
            elif kind == "content":
                pass  # non-empty inline scalar
            elif kind == "block":
                if not any(non_comment(line) for line in body_lines(i)):
                    findings.append(f"{skill}: description is empty")
            else:  # empty inline value
                # The supported grammar for multi-line scalars is a block
                # indicator, full stop. A bare 'description:' with a mapping/
                # sequence body is the wrong TYPE; a bare one with plain-text
                # continuations is valid YAML but outside the grammar this
                # schema supports — both fail, with truthful diagnostics.
                body = body_lines(i)
                content = [line for line in body if non_comment(line)]
                if content:
                    c0 = content[0].strip()
                    if re.match(r"-(\s|$)", c0) or mapping_shaped(c0):
                        findings.append(f"{skill}: description must be a scalar — the indented body parses as a nested structure (wrong type)")
                    else:
                        findings.append(f"{skill}: multi-line description must use a block indicator ('|' or '>-'); bare 'description:' continuations are outside the supported grammar")
                else:
                    findings.append(f"{skill}: description is empty")
        elif k in LIST_FIELDS:
            kind = inline_kind(inline)
            if kind in ("content", "malformed"):
                findings.append(f"{skill}: {k} must be a list, got inline scalar {inline!r}")
                continue
            if kind == "flow":
                findings.append(f"{skill}: {k} must be a block-style list, got a flow collection: {inline!r}")
                continue
            body = body_lines(i)
            dash_re = re.compile(r"^(\s+)-(?:\s+(.*))?$")
            items = []
            for j, line in enumerate(body):
                dm = dash_re.match(line)
                if dm:
                    items.append((j, len(dm.group(1)), (dm.group(2) or "").strip()))
            if not items:
                findings.append(f"{skill}: {k} must be a non-empty list of items")
            # An item is empty when the dash carries no real content (nothing,
            # a comment, or a bare block indicator) AND no deeper-indented
            # non-comment content follows before the next same-or-outer line.
            for j, dash_indent, after in items:
                # `- key: value` is a MAPPING item, not a scalar — the wrong
                # type, whether the key is quoted, unquoted, ASCII or not. A
                # fully-quoted scalar ('- "Note: x"') is the escape hatch for
                # legitimate colon-bearing item text.
                if mapping_shaped(after):
                    findings.append(f"{skill}: {k} list item must be a scalar, got a mapping: {after!r}")
                    continue
                after_kind = inline_kind(after)
                if after_kind == "content":
                    continue
                if after_kind == "malformed":
                    findings.append(f"{skill}: {k} list item has a malformed block indicator: {after!r}")
                    continue
                if after_kind == "flow":
                    findings.append(f"{skill}: {k} list item must be a block scalar or plain text, got a flow collection: {after!r}")
                    continue
                has_content = False
                first_content = None
                for nxt in body[j + 1:]:
                    if not nxt.strip():
                        continue
                    if not non_comment(nxt):
                        continue  # comments are void in YAML: they neither
                        # terminate the item (whatever their indent) nor count
                    ind = len(nxt) - len(nxt.lstrip())
                    if ind <= dash_indent:
                        break
                    has_content = True
                    first_content = nxt
                    break
                if not has_content:
                    findings.append(f"{skill}: {k} contains an empty list item")
                elif after_kind == "empty" and (
                        re.match(r"-(\s|$)", first_content.strip())
                        or mapping_shaped(first_content.strip())):
                    # A bare dash whose body opens mapping/sequence-shaped is a
                    # nested structure, not a scalar item. (A block indicator
                    # makes the body scalar text, so this applies only to the
                    # indicator-less case.)
                    findings.append(f"{skill}: {k} list item must be a scalar, got a nested structure: {first_content.strip()!r}")

findings = list(dict.fromkeys(findings))
if findings:
    for f in findings:
        print(f"FRONTMATTER-CHECK FAIL: {f}", file=sys.stderr)
    print(f"FRONTMATTER-CHECK: {len(findings)} finding(s).", file=sys.stderr)
    sys.exit(1)
print(f"frontmatter check OK ({len(paths)} skills; closed key set: {', '.join(sorted(ALLOWED))})")
PYEOF

run_check() { python3 "$PY" "$1"; }

if [[ "$MODE" == "check" ]]; then
  run_check "$ROOT_DIR"
  exit $?
fi

# ---------------------------------------------------------------------------
# --selftest: prove each failure mode on scratch copies; the repo is untouched.
# ---------------------------------------------------------------------------
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"; rm -f "$PY"' EXIT
stage() {
  rm -rf "$TMP/repo"
  mkdir -p "$TMP/repo"
  cp -R skills "$TMP/repo/skills"
}
expect() {  # expect <name> <want-exit> [<required-diagnostic-pattern>]
  # The pattern pins WHICH check fired — mandatory for every failure case so a
  # case can never pass on an unrelated crash's exit 1.
  local name="$1" want="$2" pat="${3:-}" got=0 out
  if [[ "$want" != 0 && -z "$pat" ]]; then
    echo "SELFTEST FAIL: $name — failure cases must assert a diagnostic pattern" >&2; exit 1
  fi
  out=$(run_check "$TMP/repo" 2>&1) || got=$?
  if [[ "$got" != "$want" ]]; then
    echo "SELFTEST FAIL: $name — exit $got, wanted $want" >&2
    echo "$out" >&2; exit 1
  fi
  if [[ -n "$pat" ]] && ! /usr/bin/grep -qF "$pat" <<<"$out"; then
    echo "SELFTEST FAIL: $name — diagnostic '$pat' not found in output" >&2
    echo "$out" >&2; exit 1
  fi
  echo "selftest ok: $name"
}

stage; expect "clean copy passes" 0

stage
python3 - "$TMP/repo/skills/remember/SKILL.md" <<'MEOF'
import re, sys
p = sys.argv[1]; t = open(p).read()
open(p, "w").write(t.replace("name: remember", "name: remembre", 1))
MEOF
expect "name/directory mismatch fails" 1 "does not match its directory"

stage
python3 - "$TMP/repo/skills/remember/SKILL.md" <<'MEOF'
import re, sys
p = sys.argv[1]; t = open(p).read()
open(p, "w").write(t.replace("assumes:", "asumes:", 1))
MEOF
expect "typo'd key fails as unknown AND missing" 1 "unknown top-level key 'asumes'"

stage
python3 - "$TMP/repo/skills/routed-comms/SKILL.md" <<'MEOF'
import re, sys
p = sys.argv[1]; t = open(p).read()
m = re.match(r"\A---\n(.*?\n)---\n", t, re.S)
block = re.sub(r"^assumes:.*", "", m.group(1), flags=re.S | re.M)  # drop assumes to end of block
open(p, "w").write("---\n" + block + "---\n" + t[m.end():])
MEOF
expect "missing assumes fails" 1 "missing required key 'assumes'"

stage
python3 - "$TMP/repo/skills/remember/SKILL.md" <<'MEOF'
import sys
p = sys.argv[1]; t = open(p).read()
open(p, "w").write(t[4:])  # strip the opening "---\n"
MEOF
expect "missing frontmatter fails" 1 "missing frontmatter"

stage
python3 - "$TMP/repo/skills/remember/SKILL.md" <<'MEOF'
import sys
p = sys.argv[1]; data = open(p, "rb").read()
open(p, "wb").write(data + b"\x00")
MEOF
expect "NUL byte fails loudly" 1 "NUL byte"

# A YAML-null list item disguised as content: `- # comment` and a bare `- |`
# with only a comment beneath must both read as EMPTY items.
stage
python3 - "$TMP/repo/skills/remember/SKILL.md" <<'MEOF'
import sys
p = sys.argv[1]; t = open(p).read()
open(p, "w").write(t.replace("assumes:\n", "assumes:\n  - # says nothing\n", 1))
MEOF
expect "comment-only list item fails" 1 "contains an empty list item"

stage
python3 - "$TMP/repo/skills/remember/SKILL.md" <<'MEOF'
import sys
p = sys.argv[1]; t = open(p).read()
open(p, "w").write(t.replace("assumes:\n  - |", "assumes:\n\t- |", 1))
MEOF
expect "tab indentation fails" 1 "tab indentation"

# A block-scalar header whose only trailing text is a comment ('> # nothing')
# is an EMPTY value, not content — for description and for a list item alike.
stage
mkdir -p "$TMP/repo/skills/synthetic"
printf -- '---\nname: synthetic\ndescription: > # nothing\nassumes:\n  - |\n    real content\n---\n\n# synthetic\n' > "$TMP/repo/skills/synthetic/SKILL.md"
expect "comment-after-indicator description fails" 1 "description is empty"

stage
mkdir -p "$TMP/repo/skills/synthetic"
printf -- '---\nname: synthetic\ndescription: real text\nassumes:\n  - | # nothing\n---\n\n# synthetic\n' > "$TMP/repo/skills/synthetic/SKILL.md"
expect "comment-after-indicator list item fails" 1 "contains an empty list item"

# One diagnostic-pinned case per remaining checker branch, each on a synthetic
# skill whose only defect is the one under test.
synth() {  # synth <frontmatter body>
  stage
  mkdir -p "$TMP/repo/skills/synthetic"
  printf -- '---\n%s\n---\n\n# synthetic\n' "$1" > "$TMP/repo/skills/synthetic/SKILL.md"
}
GOOD_TAIL='description: real text
assumes:
  - |
    real content'

synth "name: synthetic
name: synthetic
$GOOD_TAIL"
expect "duplicate top-level key fails" 1 "duplicate top-level key 'name'"

synth "name: Synthetic_X
$GOOD_TAIL"
expect "non-kebab name fails" 1 "bare kebab-case scalar"

synth "name: synthetic
  stray continuation
$GOOD_TAIL"
expect "name continuation fails" 1 "indented continuation"

synth "name: synthetic
weird bare line
$GOOD_TAIL"
expect "unparseable unindented line fails" 1 "unparseable unindented frontmatter line"

synth "name: synthetic
description: |x
assumes:
  - |
    real content"
expect "malformed description indicator fails" 1 "malformed block indicator"

synth "name: synthetic
description: []
assumes:
  - |
    real content"
expect "flow-collection description fails" 1 "flow collection"

synth "name: synthetic
description:
  nested: mapping
assumes:
  - |
    real content"
expect "mapping-typed description fails" 1 "parses as a nested structure"

synth "name: synthetic
description: real text
assumes: just text"
expect "inline-scalar list field fails" 1 "must be a list, got inline scalar"

synth "name: synthetic
description: real text
assumes: [\"x\"]"
expect "flow-collection list field fails" 1 "block-style list"

synth "name: synthetic
description: real text
assumes:
  - []"
expect "flow-collection list item fails" 1 "got a flow collection"

synth "name: synthetic
description: real text
assumes:
  - |x"
expect "malformed list-item indicator fails" 1 "malformed block indicator"

synth "name: synthetic
description: real text
assumes:"
expect "empty list field fails" 1 "non-empty list of items"

synth "name: synthetic
description:
assumes:
  - |
    real content"
expect "bare empty description fails" 1 "description is empty"

synth "name: synthetic
description:
  plain continuation text
assumes:
  - |
    real content"
expect "bare-key plain continuation fails (grammar restriction)" 1 "must use a block indicator"

synth "name: synthetic
description: real text
assumes:
  - nested: mapping"
expect "mapping-shaped inline list item fails" 1 "got a mapping"

synth "name: synthetic
description: real text
assumes:
  -
    nested: mapping"
expect "mapping body under a bare dash fails" 1 "got a nested structure"

synth "name: synthetic
description: null
assumes:
  - |
    real content"
expect "null description fails" 1 "description is empty"

synth "name: synthetic
description: real text
assumes:
  - null"
expect "null list item fails" 1 "contains an empty list item"

synth "name: synthetic
description: null # annotated null is still null
assumes:
  - |
    real content"
expect "comment-suffixed null description fails" 1 "description is empty"

synth "name: synthetic
description: real text
assumes:
  -
  # comment at dash indent must not end the item
    nested: mapping"
expect "comment-before-mapping item fails as nested structure" 1 "got a nested structure"

synth "name: synthetic
description: real text
assumes:
  - \"key\": value"
expect "quoted-key mapping item fails" 1 "got a mapping"

synth "name: synthetic
description: real text
assumes:
  - ключ: value"
expect "non-ASCII-key mapping item fails" 1 "got a mapping"

synth "name: synthetic
description: real text
assumes:
  - \"Note: quoted colon text is a scalar\""
expect "fully-quoted colon-bearing item passes (escape hatch)" 0

synth "name: synthetic
description: real text
assumes:
  - 'can''t': value"
expect "escaped single-quoted mapping key fails" 1 "got a mapping"

synth "name: synthetic
description: real text
assumes:
  - ? key
    : value"
expect "explicit-key mapping item fails" 1 "got a mapping"

echo "selftest OK (35 cases)"
