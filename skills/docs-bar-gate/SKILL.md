---
name: docs-bar-gate
description: |
  The cheap recurring tripwire that catches documentation drift while it is
  still one line in one file. Carries the four surfaces a drift check has to
  cover (banned terms in content, banned terms in commit messages, the
  status-header convention on newly added internal docs, and
  template-derived copies against their canonical), the scan-floor mechanism
  that keeps each run incremental and cheap, the anti-false-positive rules
  that keep it from being switched off, and the finding format. Minutes, not
  hours; read-only; report-only, with a `PASS` costing one line. Procedural
  only: WHAT the banned terms are, WHICH trees are public-facing, WHICH
  files are exempt, and WHETHER any finding gets fixed are the project's
  documentation policy and the invoking role's contract — this skill is the
  HOW of looking, never the fixing and never the bar.
assumes:
  - |
    A project-level documentation policy exists and is readable. This gate
    derives its terms, its status-header convention and its exemption list
    from that file at run time — never from a copy embedded here, and never
    from memory. If the policy changed since the last run, the gate re-reads
    it and the new bar applies from this run forward. Where no such policy
    exists, the gate does not apply: report "policy absent — gate not
    applicable" as the run's one-line record and stop; never improvise a bar
    or scan against a remembered one.
  - |
    Claude roles read/invoke this via the native Skill tool or `Read` and
    run the scans through `Bash`; Codex roles read it via
    `functions.exec_command` and run the same commands there. Neither path
    writes to a scanned tree — the only artefact either produces is the
    report, and the record of the sha that was scanned.
  - |
    The gate assumes a prior consolidation established the baseline. On a
    corpus that has never been brought under the bar it will report
    hundreds of findings and be useless as a tripwire; run the consolidation
    pipeline first (`agent:docs-governance`) and then use this to hold the
    line.
authority-boundary:
  - |
    REPORT-ONLY. The gate ends at a list of findings. It does not redact a
    string, move a misplaced file, stamp a missing header, or re-sync a
    drifted template — even when the fix is one obvious line. Whether and
    when each finding is fixed is a separate decision, and folding the fix
    into the check destroys the thing that makes a tripwire cheap enough to
    run often.
  - |
    READ-ONLY on every scanned tree. No commits, no branches, no worktrees,
    no `--fix` mode. The gate may write exactly one thing: its own record.
  - |
    The gate does NOT adjudicate the bar. A string it flags that the policy
    permits is a gate defect to be reported as such, not a violation to be
    argued; a string the policy bans is a violation even when it looks
    harmless in context. Where the gate and the policy disagree, the policy
    wins.
---

# docs-bar-gate

The HOW of a five-minute recurring check that a documentation corpus is still inside the bar
somebody already established. It exists because the alternative to catching drift early is
catching it during a consolidation pass, which costs orders of magnitude more and arrives after
the drift has been copied into three other files.

Run it after any wave of agent work that touched documentation, before a release, or on a
schedule. It is read-only and report-only by construction.

## Authority boundary (read first)

- **Report, never fix.** Every finding leaves this gate as a line of text. The fix is a separate
  decision made by someone with the authority and the context to make it.
- **The policy is the bar, not this file.** Terms, exemptions and conventions are read from the
  project's documentation policy at run time.
- **A false positive is more expensive than a miss.** A gate that flags exempt files gets ignored,
  and an ignored gate catches nothing. Honor the policy's exemption list precisely.

## §"Load the bar"

Read the project's documentation policy (conventionally something like
`docs/DOCUMENTATION-POLICY.md`) and take from it, this run:

- the **banned-terms alternation** for public-facing trees, and its **keep-list** — names that are
  legitimately public and are not findings;
- the set of **public-facing trees** in scope;
- the **status-header convention** and, critically, its **closed list of exempt classes**;
- any **canonical templates** whose derived copies are supposed to stay in sync.

Never scan against a remembered list or one pasted into a runbook. A stale copy of the bar
produces both false positives and, worse, silent gaps where the policy has since tightened.

## §"Scan the public-facing trees"

Content **and** commit messages. The message half is the one people forget, and it is the half
that cannot be corrected after publication without rewriting history.

```sh
DENY='<the alternation from the policy, verbatim>'
LAST='<sha recorded by the previous run>'      # the scan floor
REV=$(git rev-parse HEAD)                      # the sha this run will record

# content, pinned to REV — -a is mandatory
git grep -anE "$DENY" "$REV" -- "<public-facing paths from the policy>"

# messages: capture first, check git's own status, then scan.
# mktemp, never a predictable path; the subshell scopes the trap so it removes
# exactly what this block created and cannot clobber an ambient EXIT trap.
# Producer failure propagates out; grep's "no match" (exit 1) is converted so a
# clean run does not read as a failure.
( MSGS=$(mktemp "${TMPDIR:-/tmp}/bar-gate-msgs.XXXXXX") || exit 1
  trap 'rm -f "$MSGS"' EXIT
  git log --format='%H%n%B' "$LAST".."$REV" > "$MSGS" || exit 1
  grep -anE "$DENY" "$MSGS" || [ $? -eq 1 ]
) || exit 1
```

- **Scan `REV`, not the working tree.** Bare `git grep` reads the working tree, so an
  uncommitted edit would make the record describe a tree that is not the sha it names. Pin the
  scan to the revision you are about to record.
- **Never pipe `git log` straight into `grep`.** A stale or missing floor ref makes `git log`
  fail and print nothing, and the scanner then reports its ordinary no-match status — a clean
  PASS over zero input. Capture, check the status, then scan.
- **`-a` always.** Many `grep` implementations — and any wrapper injecting `-I` — treat a file
  containing a NUL byte as binary and skip it silently: no notice, a no-match exit status, no
  output. Status and output agree, so the result is a self-consistent wrong negative
  indistinguishable from a genuinely clean tree, and the file may render perfectly normally in
  an editor because a NUL commonly displays as blank. An absence proved with a bare `grep` is
  not proved. Two corollaries: never hunt for NUL bytes with a shell-quoted NUL escape — the
  shell strips the NUL, leaving an *empty* pattern that matches every line of every non-empty
  file, a catastrophic false finding on a clean tree; count bytes with a byte-level reader
  instead. And where an absence is **load-bearing** — a verification, not this recurring
  tripwire — make a byte-level reader the primary scanner with the shell `grep -a` as an
  independent second implementation, and report that the two agreed; that escalation arises in
  the consolidation pipeline's independent verification (`agent:docs-governance` stage 6), and
  this gate's own scans stay `grep -a` / `git grep -a`.
- **Prove the gate fires before believing a PASS.** Once per run, confirm `$DENY` matches a
  known-bad string in a scratch file outside every scanned repository (`mktemp` it, remove it
  when done — same trap discipline as the message capture), using the plain form —
  `grep -aniE "$DENY" <scratch>` — since the repository-aware `git grep` cannot see an untracked
  file. Then confirm the path arguments select a non-empty file set
  (`git ls-tree -r --name-only "$REV" -- "<paths>" | wc -l`). Zero hits from an untested pattern,
  or from a path argument that matches nothing, is indistinguishable from a clean tree.
- **Report raw counts, then apply the keep-list.** State the unfiltered hit count and the filtered
  one. When the raw count is already zero, say so — a zero that never depended on an exclusion
  judgement is a stronger result than one that did.
- **A tree that is its own repository is scanned inside that repository.** Repository-scoped
  tools (`git grep`, `git ls-tree`, `git log`) do not cross into nested repositories — from a
  parent checkout, a nested repo's files select **zero paths**, which the non-empty-file-set
  check above will surface as an untrustworthy result rather than a PASS. Run the scan with the
  nested repository as the working repository (`git -C <path> …`), pin to *its* HEAD, and record
  **one floor sha per repository** — a single parent-repo sha cannot serve as the floor for a
  tree that versions independently.
- **Record the sha you scanned.** `REV` is the next run's floor. Without it the message scan
  either re-reports old history or silently skips a range.

Scan the whole tree, not the diff: a string introduced before the floor and never removed is
still published.

The scanner disciplines above — prove the gate fires, capture-then-scan, `-a` always — are
**single-sourced here**: the consolidation pipeline (`agent:docs-governance`) binds every scan
it runs to this section rather than restating them.

## §"Check status headers on newly added internal docs"

For files **added since the floor** in the internal corpus, and for any the run touched:

- the status line sits directly under the H1, before any prose — check the position, not merely
  the presence, since the convention's value is that a reader meets it first;
- the value is inside the policy's closed vocabulary;
- every field the convention requires is present — including the `Updated:` date, which records
  when the *document* last changed rather than when the work it describes happened, and which is
  the field most often dropped because it is the one that needs maintaining;
- any `superseded` document carries the mandatory `Superseded-by:` pointing at a path that exists;
- the file is not in one of the policy's exempt classes. Exempt files are **not** findings, and a
  gate that reports them will be switched off within two runs.

## §"Check template-derived copies against their canonical"

Where a file is replicated across repositories from one canonical template — a shared
`docs/README.md` is the usual case — compare each copy's leading section against the template's.
Drift here is invisible to the term scan and to the header check, and it is asymmetric: usually
the template was corrected and the copies were not, so the shipped copies keep instructing readers
to do the thing the fixed template now warns against.

Report **which side moved** and since when, not merely that they differ. "Six copies carry the
pre-correction wording of item 6; the template was fixed on <date>" is actionable; "template drift
detected" is not.

## §"Report the findings"

One line per finding: `file:line` · the matched string or the missing element · the rule it
violates, cited by the policy's section. Group by repository. Nothing else — no remediation plan,
no severity debate, no patch.

```
<repo>/docs/<file>.md:41  "<matched term>"        policy §<n> banned terms
<repo>/docs/<file>.md:1   missing status header   policy §<n> status convention
<repo>/docs/README.md:69  pre-correction wording  template drift (template fixed <date>)
```

**Zero findings is a one-line record**, and that brevity is the point — a passing run that costs a
paragraph will stop being run. Record: date · trees scanned · scan floor sha · new floor sha ·
`PASS`.

## §"Keeping it cheap"

The gate's whole value is that it is cheap enough to run without deliberation. Defend that:

- **Bound the scope** to the policy's public-facing paths and to commits since the floor.
- **Do not investigate.** A finding is reported at the line it appears; tracing how it got there
  is the follow-up's job.
- **Do not grow it into the pipeline.** If a run is taking hours or producing a triage backlog,
  that is the signal that the corpus needs a consolidation pass, not that the gate needs more
  features. Report that conclusion and hand off to `agent:docs-governance`.

## What this skill does NOT do

- Does NOT fix anything — no redactions, no moves, no stamped headers, no template re-sync.
- Does NOT define the bar, the exemptions, or which trees are public-facing.
- Does NOT commit, branch, or publish anything to a remote; the only thing it
  writes is its own record.
- Does NOT replace the pre-publication proof gates a publication checklist owns, and a `PASS`
  here is not a publication clearance.
- Does NOT perform the full corpus consolidation — that is `agent:docs-governance`.
