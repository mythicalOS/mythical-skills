---
name: docs-governance
description: |
  The staged pipeline for bringing a multi-repository documentation corpus
  under a public/private split, and the disciplines that make its gates
  worth believing. Carries the per-file disposition vocabulary and the
  ledger shapes, the read-only/write separation between stages, the
  scan-and-review exit gates, the add-date stratification technique for
  dating a corpus nobody documented, and the operational lessons behind each
  gate (prove a gate fires before trusting its PASS; an absence proved with
  a bare `grep` is not proved; gates run on final state, never on the diff).
  Procedural only: WHAT the bar contains, WHICH trees are public-facing, and
  WHETHER anything may be published are the project's documentation policy
  and its publication checklist — this skill is the HOW of executing against
  them and never the authority that sets them.
assumes:
  - |
    A project-level documentation policy either exists or is authored as
    stage 1. Every later stage consumes it as its contract; a pipeline run
    without one produces dispositions nobody can adjudicate. This skill
    describes the policy's required faces, never its contents — the
    project's own file is the only source for the banned terms, the allowed
    genres, and the placement map.
  - |
    Claude roles read/invoke this via the native Skill tool or `Read`, run
    git and scanners through `Bash`, fan the read-only audits out to
    subagents, and write through the native edit tools. Codex roles read it
    via `functions.exec_command`, run the same commands there, and write via
    `functions.apply_patch`. The stage boundaries, ledger shapes and gates
    are platform-agnostic and bind both paths identically.
  - |
    Publication itself is out of scope. This pipeline prepares a tree and
    proves what it does and does not contain; the decision to make a
    repository public, and the checklist that gates it, live elsewhere.
authority-boundary:
  - |
    Stages 2 and 6 are READ-ONLY and report-only. The audit produces
    dispositions, not edits; the verifier produces a record, not a fix. A
    verifier that repairs what it finds has destroyed the independence that
    made its verdict worth anything — it reports, and the finding is routed
    for a separate pass.
  - |
    This skill does NOT decide the bar. Which strings are banned, which
    document genres are publishable, and where each internal artefact kind
    lives are the project's documentation policy's authority. Where a
    disposition and the policy disagree, the policy wins and the ledger row
    is wrong.
  - |
    A delivered coordination artefact is a record of what was delivered.
    This pipeline does not edit one — not to add a status header, not to
    correct wording. When a ledger row asks for an edit the policy exempts,
    the correct outcome is a documented refusal recorded in the commit
    message, not compliance.
  - |
    Publication authority is not granted here. Landing a remediation branch,
    rewriting published history, and flipping a repository's visibility are
    decisions the invoking role's contract and the project's publication
    checklist own. The pipeline's terminal output is a verified branch and a
    verification record.
---

# docs-governance

The HOW of taking a documentation corpus that grew without a bar — typically across an internal
coordination repository plus several product repositories, some already public and some going
public — and bringing it under one. Six stages, each with a hard output the next one consumes.
The pipeline's value is not in any single stage but in the fact that the last stage can
reconstruct the first five from evidence.

Use it when auditing or consolidating a repository family's documentation against a
public/private split, when preparing a repository's `docs/` for publication, or when recovering
a documentation corpus after a period of untracked agent writing.

## Authority boundary (read first)

- **The bar is not this skill's to set.** The project's documentation policy owns the banned
  terms, the publishable genres and the placement map. This skill executes against it.
- **Two stages never write.** The audit (stage 2) and the verification (stage 6) are read-only.
  Their output is a ledger and a record.
- **Publication is a one-way door and is decided elsewhere.** Once a tree is public, every string
  in it and in every commit message is retrievable forever; scrubbing afterwards does not retract
  it. That is why the pipeline exists, and also why it stops short of the flip itself.
- **A documented refusal is a correct outcome.** A ledger is a proposal. A stage that declines a
  proposed action because the policy forbids it, and says so where a verifier will find it, has
  succeeded.

## §"Stage 1 — author the bar first"

Nothing downstream is adjudicable without a written policy. If one exists, locate it and confirm
it carries all five faces below; extend it in place rather than forking a second bar. If none
exists, write it first — as one file with stable §-anchors, because every later stage cites it.

The five faces a usable policy must have:

1. **A banned-terms list for public-facing trees**, checked in **file content and in commit
   messages**. Express it as one alternation the scanner can consume verbatim. It must also state
   what to **keep**: names that are legitimately public are not violations, and a list that omits
   the keep-side produces an over-scrubbed tree and a stream of false findings.
2. **A prose-claim gate** — no present-tense claims about unshipped things. Do not describe an
   undeployed service as running; do not document an endpoint, flag or field that is not in the
   tree, however imminent; do not upgrade a hedge; never infer, approximate or fabricate a
   measured number. Applied continuously while authoring, not only as a pre-publication sweep.
3. **The allowed public genres** — an explicit list (install and configuration, usage guides,
   architecture as shipped, API and field reference, troubleshooting, changelog,
   contribution-facing docs, and an index). A document that is not one of them probably belongs
   on the internal side.
4. **A placement map** — for each internal artefact kind, the one directory it lives in. The rule
   this map exists to close: *work performed inside a sub-repository still records its
   coordination artefacts on the internal side.* Dispatch location does not change artefact
   location, and the working directory invites the mistake. A mapped directory that does not
   exist yet is still the right home — create it because the map names it, never because a
   document seemed to want a new one.
5. **A status-header convention for internal docs**, so staleness cannot read as currency:

   ```
   **Status:** live | delivered | superseded | historical | obsolete
   **Superseded-by:** <path>        (required when superseded)
   **Updated:** YYYY-MM-DD
   ```

   Fix the position — directly under the H1, before any prose — so a later scan can verify by
   position rather than by mere presence. Close the vocabulary, and define each value. Name the
   **exempt classes as a closed list**; an open-ended exemption is how a convention dissolves.

Two distinctions worth writing into the policy explicitly, because every later stage depends on
them:

- **Placement failure vs content failure.** A document of the wrong *kind* is moved, not
  rewritten into compliance. A document of the right kind carrying a forbidden *string* is
  redacted in place, not relocated. Confusing them produces both an over-full internal corpus and
  an under-cleaned public one.
- **Secrets are nobody's to absorb.** A key, token or credential is removed and rotated — never
  relocated to the internal side. An internal hostname or identifier may legitimately live
  internally; a credential may not live anywhere.

**Output:** one policy file, and a shared template for any file that will be replicated across
repositories (a per-repository `docs/README.md`, for instance).

## §"Stage 2 — audit the public-facing trees"

Read-only, one agent per repository, in parallel. No edits in this stage at all — an audit that
starts fixing loses the disposition record that stage 6 reconciles against.

Give every in-scope file exactly one disposition, with evidence:

| Disposition | Means | Evidence required |
|---|---|---|
| `KEEP` | Passes the bar as it stands | The genre it satisfies |
| `REWRITE` | Right genre, wrong strings or wrong tense; stays (possibly renamed) | `file:line` of each offending string |
| `EVACUATE` | Wrong genre entirely; belongs on the internal side | The genre rule it fails, plus its mapped internal home |
| `DELETE` | Superseded or duplicated by a sibling that survives, or genuinely worthless | The surviving sibling's path |

Disciplines that decide whether the ledger is usable:

- **No silent sampling.** Every file in scope gets a row. A sampled audit cannot be reconciled,
  and a gap in the ledger is indistinguishable from a file nobody looked at.
- **Flag sole copies.** Mark each row whose content exists nowhere else. That flag is the only
  thing that makes stage 3's evacuation safe.
- **Audit beyond the named directory.** Root and package-level READMEs, and any other
  public-facing file the brief did not enumerate, are published just as permanently. The extra
  scan is cheap; the miss is not.
- **Cite, do not summarize.** "Contains internal references" is not evidence. The line is.

**Output:** a per-repository disposition ledger, every in-scope file present, each row carrying
its evidence.

## §"Stage 3 — remediate behind a gate"

One worktree and one branch per repository, so the audit's parallelism carries into remediation
without cross-contamination. Land on a dedicated branch, never on the default branch: stage 6
verifies pushed refs, and a shared default branch moves underneath it.

Apply the dispositions, then:

- **Preserve before deleting.** An evacuated sole copy is written to a staging location **outside
  every repository's tree** and hash-verified there *before* the deletion commit. Copy, verify,
  then delete — delete-then-recover is not a plan.
- **Rename toward the reader.** A `REWRITE` row often needs a de-jargonised filename as well as
  de-jargonised prose; internal identifiers hide in paths as readily as in bodies.

The exit gate, all three arms required:

1. **The banned-terms scan, on the final tree and on every commit message the branch adds** —
   not on the diff, and not only on the files you touched. Use `-a` (see §"Operational lessons").
   Report raw hit counts *before* any keep-list filtering, so a zero does not depend on an
   exclusion judgement.

   ```sh
   DENY='<the alternation from the policy, verbatim>'
   REV='<the commit whose sha you will report>'
   BASE='<the branch point>'

   # tree, pinned to that revision
   git grep -anE "$DENY" "$REV" -- "<public-facing paths from the policy>"

   # messages: capture first, check git's own status, then scan (subshell scopes the trap;
   # producer failure propagates out, grep's "no match" does not)
   ( MSGS=$(mktemp "${TMPDIR:-/tmp}/stage3-msgs.XXXXXX") || exit 1
     trap 'rm -f "$MSGS"' EXIT
     git log --format='%B' "$BASE".."$REV" > "$MSGS" || exit 1
     grep -anE "$DENY" "$MSGS" || [ $? -eq 1 ]
   ) || exit 1
   ```

   Both lines are shaped to close failure modes owned by the scanner disciplines in
   `agent:docs-bar-gate` §"Scan the public-facing trees": the tree scan pins to a revision
   rather than the working tree, and the message scan captures first and checks `git log`'s
   own exit status before scanning — a failed producer must never read as a clean PASS.

2. **The faces of the bar a term list cannot see.** A denylist catches names it was told about.
   It does not catch a credential (which looks like any other random string), an internal
   hostname or identifier nobody thought to list, personal data, or a present-tense claim about
   something unshipped. Walk every changed file against the policy's remaining content gates
   deliberately — this arm is a reading, not a scan, and skipping it is how a clean scan comes to
   be mistaken for a clean tree.

   A key, token or credential found here is **removed and rotated**, never merely deleted from
   the tip: it is already in the branch's history, and it is never relocated to the internal side
   either.

3. **Cross-model review until clean** (`agent:cross-model-review`). Target the two failure modes
   a self-review misses here: a string the author has stopped seeing, and a claim that reads as
   shipped because the author knows it is nearly shipped.

**Commit messages are files.** They are published exactly as permanently, are not covered by a
tree-scanning CI gate, and cannot be edited after publication without rewriting history. Describe
provenance neutrally ("ported from an internal mirror", "as directed by the maintainer"), name no
person, and carry no internal path or identifier. **Never enumerate the banned terms verbatim in
a scrub commit's own message** — that writes the leak straight back into the history being
cleaned. Describe the substitution abstractly, then re-scan the new HEAD.

**Output:** one pushed branch per repository, each with a recorded sha, a zero-hit scan over its
final tree and messages, and a clean cross-model verdict.

## §"Stage 4 — inventory the internal corpus"

The internal side has the opposite failure mode: not leakage, but staleness that reads as
current. The inventory is what makes stage 5 mechanical.

**Stratify by git ADD date, and find the era boundaries from history rather than from memory.**
Filenames lie, mtimes lie, and recollection of "when we started doing it that way" is the least
reliable input available:

```sh
git log --diff-filter=A --follow --date=short --format='%ad %cd' -1 -- "<path>"
```

Emit **both** dates and choose deliberately which one your eras are made of; they answer
different questions and they diverge exactly when it matters most. `%ad` is the **author** date —
when the change was written — and it survives an ordinary rebase or cherry-pick. `%cd` is the
**committer** date — when the addition entered *this* history — and it does not. Era
stratification usually wants `%ad`, because an era is about which conventions were in force when
the document was written. But a corpus that was imported or filter-rewritten wholesale shows
committer dates clustered at the import while author dates stay spread out, and that divergence
is itself the signal that one of the two is misleading you. Where the two agree, either will do;
where they disagree, say which you used.

`--follow` carries its own caveat: rename detection is a heuristic, so a file that arrived by
rename or copy may date from its current path rather than from its origin, and `--follow` accepts
only one path at a time. Treat any single file's add-date as evidence, not proof — read an era
boundary only where many files agree, and corroborate a surprising one against something
independent (a tag, a release, a directory's first appearance).

Aggregate those dates across the corpus and let the distribution show where conventions actually
changed — where a naming grammar starts or stops, where a directory begins filling. Those
discontinuities are the era boundaries, and they decide which files are settled history (read as
of their date, never reconciled against current state, never backfilled) and which are live.

Classify every file: `LIVE` · `DELIVERED` · `SUPERSEDED-by <path>` · `OBSOLETE` · `MISFILED`.

**Verify every delivery claim against code and git state, never against the document's own
prose.** A document asserting that something shipped is evidence of nothing; the merge, the tag,
the released version, the tree are the evidence. This is the single highest-yield check in the
stage, and the one most often skipped because the prose is right there.

**Every in-scope file gets a row — no silent sampling.** Row shape: path · add-date · era ·
class · proposed action · evidence.

**Mark the ledger a PROPOSAL, in the file, in those words.** Its action column records what was
proposed, not what happened. Stage 6 reconciles proposals to observed outcomes, and a ledger that
reads as a record of completed work turns every honest refusal into an apparent miss.

**Output:** one ledger covering the internal corpus, plus the era boundaries it was stratified
by.

## §"Stage 5 — apply"

Mechanical execution of the stage-4 ledger.

- **Status headers**, at the position the convention fixes, and only on non-exempt files.
  Flagging an exempt file is worse than missing one: false positives train readers to ignore the
  convention.
- **Moves with inbound-link repair.** Sweep for citations by **full path and by bare basename** —
  a path-only sweep misses every citation that names the file alone, and those are the majority
  in prose. Check relative links from sibling directories too, since a move changes their depth.
- **Supersession chains collapsed to their true terminal successor.** If A is superseded by B and
  B by C, then A's `Superseded-by:` names **C**. Walk each chain to its end before stamping, or
  readers land on a stale hop and conclude the convention is unreliable.
- **Archive pre-rewrite originals when history may later be rewritten.** Store byte-identical
  frozen copies with a README stating that they are verbatim originals, that they carry no status
  header, and that they must not be given one. Verify the copies by hash against their sources —
  a re-rendered "original" is not one. State the archive's coverage honestly, including which
  repositories it deliberately does not cover and why.
- **Refuse in writing.** When applying a row would violate the policy — most often because the
  target is an exempt or delivered artefact — decline, and record the reason in the commit
  message so stage 6 can distinguish a refusal from an omission. Settle on **one** rationale per
  decision: a commit message and an in-file note giving two different reasons for the same
  refusal will be read as a contradiction even when both are true.

**Output:** an internal-side branch whose diff accounts for every ledger row, either as an
applied action or as a recorded refusal.

## §"Stage 6 — verify independently"

A fresh agent that did none of the prior work, re-deriving every claim from evidence rather than
from the delivery's own ledgers. Read-only throughout except for the record it writes.

- **Work from the PUSHED refs.** Require the delivery to name, per repository, the **remote, the
  branch, the base branch and the sha** — "the head" is ambiguous wherever more than one branch
  exists, and the message range cannot be resolved without a base. Then resolve and scan the
  fetched objects themselves:

  ```sh
  CLAIMED='<the full sha the delivery claims>'

  git fetch '<remote>' '<branch>' || exit 1      # a failed fetch must stop the run...
  ACTUAL=$(git rev-parse FETCH_HEAD) || exit 1   # ...or the stale FETCH_HEAD gets scanned
  [ "$ACTUAL" = "$CLAIMED" ] || { echo "MISMATCH: $ACTUAL != $CLAIMED"; exit 1; }

  git grep -anE "$DENY" "$ACTUAL" -- "<public-facing paths from the policy>"
  git ls-tree -r --name-only "$ACTUAL" -- "<public-facing paths from the policy>" | wc -l
  # byte-level PRIMARY scan vs the shell SECOND implementation, one shared metric (MATCHING
  # LINES — what `grep -n` lists), both captured fail-closed and compared as integers; any
  # disagreement or NUL is itself a finding. Enumeration happens INSIDE python (check=True
  # over `ls-tree -r -z`, byte-safe paths) so a failed listing raises instead of feeding an
  # empty scan; only BLOB entries are read — a gitlink (submodule) entry is counted and
  # reported, never cat-file'd (git grep skips gitlinks, so the totals stay comparable).
  BYTE_OUT=$(DENY="$DENY" REV="$ACTUAL" PATHSPEC="<public-facing paths from the policy>" python3 -c 'import os,re,subprocess as sp; rev=os.environ["REV"]; pat=re.compile(os.environ["DENY"].encode()); rec=[(e.split(b"\t",1)[0].split(),e.split(b"\t",1)[1]) for e in sp.run(["git","ls-tree","-r","-z",rev,"--",os.environ["PATHSPEC"]],capture_output=True,check=True).stdout.split(b"\x00") if e]; blobs=[sp.run(["git","cat-file","blob",rev.encode()+b":"+p],capture_output=True,check=True).stdout for meta,p in rec if meta[1]==b"blob"]; print(sum(sum(1 for l in b.split(b"\n") if pat.search(l)) for b in blobs), sum(b"\x00" in b for b in blobs), len(blobs), sum(1 for meta,p in rec if meta[1]!=b"blob"))') || exit 1
  # the SECOND implementation's integer, computed wholly inside python: a shell variable
  # cannot carry the -z output (command substitution strips NUL bytes), and running git grep
  # as a checked subprocess keeps a scanner failure (exit >1) from ever reading as a count
  SECOND=$(DENY="$DENY" REV="$ACTUAL" PATHSPEC="<public-facing paths from the policy>" python3 -c 'import os,re,sys,subprocess as sp; r=sp.run(["git","grep","-zcE",os.environ["DENY"],os.environ["REV"],"--",os.environ["PATHSPEC"]],capture_output=True); sys.exit(9) if r.returncode not in (0,1) else None; print(sum(int(c) for c in re.findall(rb"\x00(\d+)\n", r.stdout)))') || exit 1
  set -- $BYTE_OUT   # $1=matching lines  $2=NUL files  $3=blobs read  $4=gitlinks skipped
  [ "$1" -eq "$SECOND" ] || { echo "SCANNER DISAGREEMENT: byte=$1 grep=$SECOND"; exit 1; }
  [ "$2" -eq 0 ] || { echo "NUL-bearing file(s): $2 — absence proof invalid"; exit 1; }
  echo "BYTE: $1 matching line(s), $2 NUL file(s), $3 blob(s) read, $4 gitlink(s) skipped"

  # the base branch, fetched in its own right — never a local tracking ref
  git fetch '<remote>' '<base-branch>' || exit 1
  BASE_TIP=$(git rev-parse FETCH_HEAD) || exit 1
  BASE=$(git merge-base "$ACTUAL" "$BASE_TIP") || exit 1

  git log --oneline "$BASE".."$ACTUAL" | wc -l   # commit count, for the record
  # subshell scopes the trap to exactly this capture; producer/scanner FAILURE propagates
  # out of it, while grep's "no match" (exit 1) is converted — a clean scan is not a failure
  ( MSGS=$(mktemp "${TMPDIR:-/tmp}/verify-msgs.XXXXXX") || exit 1
    trap 'rm -f "$MSGS"' EXIT
    git log --format='%B' "$BASE".."$ACTUAL" > "$MSGS" || exit 1
    grep -anE "$DENY" "$MSGS" || [ $? -eq 1 ]     # the match listing (evidence detail)
    B_OUT=$(DENY="$DENY" python3 -c 'import os,re,sys; pat=re.compile(os.environ["DENY"].encode()); d=sys.stdin.buffer.read(); print(sum(1 for l in d.split(b"\n") if pat.search(l)), 1 if b"\x00" in d else 0)' < "$MSGS") || exit 1
    G=$(grep -acE "$DENY" "$MSGS"); s=$?; [ "$s" -le 1 ] || exit 1
    set -- $B_OUT   # $1=matching lines  $2=NUL flag
    [ "$1" -eq "$G" ] || { echo "SCANNER DISAGREEMENT (messages): byte=$1 grep=$G"; exit 1; }
    [ "$2" -eq 0 ] || { echo "NUL present in captured messages — absence proof invalid"; exit 1; }
    echo "BYTE-MSGS: $1 matching line(s)"
  ) || exit 1
  ```

  **Regex semantics across the two scanners.** Python's `re` and the shell scanners' ERE agree
  for the alternation-of-literal-terms shape the policy mandates for its denylist; where a
  policy pattern uses an ERE construct `re` lacks (or vice versa), adapt the pattern for the
  byte scan and record the adaptation in the verification record — never silently compare
  scans that ran different patterns. `PATHSPEC` above carries one pathspec; append further
  ones to the `ls-tree` argument list the same way.

  **Fetch the base branch too.** An explicit-branch fetch updates only the branch it names, so a
  `<remote>/<base-branch>` remote-tracking ref is local state this run never refreshed — possibly
  absent, possibly months stale — and resolving the range against it contradicts the rule above.
  Fetch the base branch in its own right and take the merge-base from that fetch. Capture
  `ACTUAL` before the second fetch: each fetch overwrites `FETCH_HEAD`.

  **Re-scan the messages, not only the tree.** A message is published as permanently as a file
  and is not covered by a tree-scanning CI gate, so a term that survives only in a commit message
  survives a tree-only verification untouched. **Resolve the base yourself** rather than accepting
  the one the delivery names — a supplied base can exclude exactly the commit that carries the
  leak. Report the commit count and, where the branch is short, the subjects themselves; a reader
  can then see what was scanned rather than trusting that something was.

  **Fail closed at both steps.** An unguarded `git fetch` that fails leaves behind whatever
  `FETCH_HEAD` the previous fetch wrote, and everything after it then scans a stale object while
  looking exactly like a successful verification. And a sha equality asserted in a comment is not
  a check — compare it in the shell and stop on mismatch. Expand an abbreviated claimed sha to
  full form first: comparing an abbreviation against a full sha as strings always mismatches, and
  that invites someone to "fix" the test by loosening it.

  Report the resolved sha alongside the claimed one even when they match. Never verify a local
  checkout or a local branch name: either can hold uncommitted, unpushed or stale state that no
  one else can see, and a verification that passes against something the reader cannot fetch has
  proved nothing.
- **Reconcile every ledger row to an observed outcome.** A row whose outcome cannot be observed
  in the tree or the diff is a finding — including rows the branch declined, which reconcile to
  the refusal and its commit. Corroborate arithmetically where possible: the ledger's counts of
  moves and deletes should predict the diff's rename and delete counts, and any shortfall should
  be exactly the documented refusals.
- **Prefer the stronger check when it is affordable.** If the brief asks for a sample and a full
  sweep costs little more, run the sweep, say that you ran it instead, and report both if the
  sample was also requested. Note explicitly when a coverage extension went beyond the brief.
- **Prove absences.** An absence proved with a bare `grep` is not proved
  (`agent:docs-bar-gate` §"Scan the public-facing trees"), and in this stage **every absence
  check is load-bearing** — the verification exists to be believed. So for each one: run a
  byte-level reader as the PRIMARY scanner, run the shell `grep -a` as the independent second
  implementation, report that the two agreed, and additionally verify the scanned files are
  byte-clean (no NUL bytes, valid encoding) so the zeros mean what they appear to mean.
- **Report raw counts before filtering.** If no match of any kind was produced, say so — a zero
  that never needed a keep-list filter is stronger than one that did.
- **Check the protected trees were not touched**: whatever the policy declares writer-owned,
  append-only, or out of scope should show zero files in the diff, and that should be stated as a
  check rather than assumed.

The verification record's shape: **scope and method** (which refs, which worktree, which
merge-base, what scanner discipline) · **per-area check tables with results** · **reconciliation**
of each ledger · **known open follow-ups** carried forward · **observations** that are loose ends
rather than defects · **verdict**. Then, and only then, land.

## §"Operational lessons"

Cheap to state, expensive to relearn. Each one has produced a wrong answer that looked right.

The **scanner disciplines** are single-sourced in `agent:docs-bar-gate` §"Scan the
public-facing trees" and bind every scan in this pipeline identically: **prove the gate fires
before trusting its PASS** (test the pattern against a known-bad scratch file with the plain
`grep -aniE` form, AND confirm the path arguments select a non-empty file set — the two halves
fail differently); **never let a failed producing command read as a passing gate** (capture,
check its own exit status, then scan); and **`-a` always** — a file containing a NUL byte is
otherwise skipped silently as a self-consistent wrong negative, and a shell-quoted NUL escape
is an *empty* pattern that matches everything, so count bytes with a byte-level reader instead.
The pipeline's own lessons:

- **Gates run on final state.** Whatever partial work, crash, rerun or fix preceded it, the gate
  is scanned on the final tree and the full message set — never on the diff, never on only the
  files this pass touched. A file cleaned in commit 3 and re-dirtied in commit 7 passes a
  diff-scoped gate.
- **After a crashed fan-out, survey before building.** Enumerate the worktrees, branches and
  commits that already exist, and **read the diffs** of any partial edits before extending them.
  Resuming on top of an unverified partial edit is how a half-applied disposition ships, and the
  plan is not evidence of what was done.
- **When a brief's count and its enumeration disagree, follow the enumeration and say so.** Do
  not silently pick one. Report the discrepancy in the deliverable; the count is the more common
  error, but the point is that the reader gets to know.
- **Report a PENDING verdict precisely.** An inferred verdict is the worst thing a gate can
  produce — worse than an honest "not determined", because it is believed.

## What this skill does NOT do

- Does NOT decide the bar's contents — the project's documentation policy is the authority for
  banned terms, publishable genres and placement.
- Does NOT decide whether a repository becomes public, and does NOT run the publication
  checklist's own proof gates.
- Does NOT grant push, merge or history-rewrite authority; those stay with the invoking role's
  contract.
- Does NOT edit delivered coordination artefacts, in any stage, for any reason.
- Does NOT replace the recurring drift check — for the cheap periodic tripwire that keeps a
  corpus from needing this pipeline again, see `agent:docs-bar-gate`.
