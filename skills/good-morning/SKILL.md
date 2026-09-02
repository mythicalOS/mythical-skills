---
name: good-morning
description: >-
  Recalibrate a fresh or resumed agent from durable continuity. Use at session
  start after reading the active role/repository instructions and before doing
  work or asking where things were left. First list matching `good-night`
  handoff records via `coordination.list_artefacts {kind:"handoff"}` by successor
  token (`<slug>-next` or `<role>-next`), read the newest unsuperseded handoff for
  each live workstream with `coordination.read_artefact`, follow only its
  `Reading Order`, verify dated claims against the current tree, settle each
  consumed record (`coordination.settle_artefact {id}`) so the store can
  reclaim it, and produce a concise pickup orientation. The handoff may be
  self-published by the predecessor or scribe-written on its behalf — same
  artefact, same verification. Use degraded
  reconstruction only when no matching handoff exists. Procedural only: current
  role/user/dispatcher instructions decide whether to act, write, commit,
  publish a branch, request a landing, route, spawn, stop, or change scope.
assumes:
  - |
    Both harness lanes call the same `coordination.*` tools (`list_artefacts`,
    `read_artefact`, `settle_artefact`), composed per session by the
    deployment; the mechanics are platform-agnostic.
  - |
    A predecessor's handoff may be self-published or scribe-written on its
    behalf — same record kind, same verification either way. No matching
    record at all is the degraded-reconstruction path, not an error.
---

# good-morning

Use `good-morning` to wake into a seat without relying on a human or teammate to
reconstruct context. The handoff is the first source, not the final truth: it
tells you what to verify and where to read next.

Every retired session is guaranteed a `good-night` handoff: the predecessor
either published its own before retiring, or the system scribe wrote one on
its behalf from the session record. The record's `Authored` provenance line
says which, and the daemon-set `origin: "scribe"` field says it independently —
prefer the field, since a session cannot set it.

**Verify both the same way; do not expect both to look the same.** A
self-published handoff follows `agent:good-night`'s template and carries the
structured `branch` / `head_sha` fields. A scribe-written one is the same record
kind to the same successor token, but its body is the runtime's own and degrades
to a minimal form under pressure, and it sets **no** structured git fields. So
treat this template's canonical sections and those fields as **present-if-there**,
never as required: a scribe handoff missing them is valid, not damaged, and its
git facts — if any — are in the body. Read what is there and verify it against
the tree, exactly as you would either way.

## Core rules

- **Handoff first.** List handoff records
  (`coordination.list_artefacts {kind:"handoff"}`) before broader docs, git
  history, memory, project scans, or teammate threads.
- **Minimum context.** Read the handoff and the files it names. Widen only when a
  load-bearing claim cannot be verified from that chain.
- **Dated claims.** Treat every handoff status as true-at-write-time only.
- **Settle what you consume.** After successfully consuming a handoff, settle
  it (`coordination.settle_artefact {id}`) so the store can reclaim the
  record. A failed settle is a warning to report, never a blocker.
- **Authority stays external.** This skill restores context; it does not grant
  permission to continue, publish a branch, request a landing, route, spawn, stop,
  or widen scope.
- **Surface deltas before acting.** The first useful output is what the handoff
  said, what is true now, what changed, and what remains open.

## Contract with `good-night`

The record's shape is defined once, in `agent:good-night` — §"Contract with
`good-morning`" for the wire contract (record kind and addressing, successor
tokens, provenance) and §"Handoff template" for the canonical sections and
status labels. That file is the single source; this skill consumes what it
defines and adds only the consumer-side terms:

- **Settlement is the consumer's step:** after successfully consuming a handoff,
  call `coordination.settle_artefact {id}` so the store can reclaim the record
  (procedure step 5). Settle only records you actually consumed.
- **Discovery, not wake:** `-next` is a discovery token, not a live recipient. Do
  not wait for a `coordination.deliver` wake from a successor that did not exist
  when the handoff was written. (`agent:routed-comms` owns live wake-routing and
  the no-dead-letter guarantee; the `-next` discovery name is `good-night`'s own.)

## Procedure

### 0. Load current instructions

Read the active role, repository, and task instructions first. They define who
you are and what you may do. `good-morning` only recovers prior state.

### 1. Establish identity

Determine the current seat from the best available source:

1. `coordination.whoami {}` → `{slug, role, project, session_id}`, the
   daemon-authoritative identity, when the coordination socket is present.
2. The launch prompt or active task instructions, when `whoami` is unavailable.
3. An explicit uncertainty note, when identity remains ambiguous.

Record the current slug/session identity, role, project, current date, and — from
`coordination.list_sessions` — whether the seat is live (`running`/`wake-ready`).
Do not infer your identity from old handoff prose before checking current sources.

### 2. Find matching handoff records

List `handoff`-kind records (`coordination.list_artefacts {kind:"handoff"}`)
before reading any other continuity source. Match the record's `to` token against
the current identity or role, most specific first:

1. `to: <current-slug>-next`, a `good-night` body
2. `to: <current-role>-next`, a `good-night` body
3. `to: <current-slug>-next` of a `good-night`, `continuity`, `retire`, or
   `handoff` thread
4. `to: <current-role>-next` of a `good-night`, `continuity`, `retire`, or
   `handoff` thread
5. Any `handoff` record whose `to` is `<current-slug>-next` or
   `<current-role>-next`

Order by `created_at` (newest first). Read a candidate with
`coordination.read_artefact {id}` and honor `Supersedes:`:

- If a newer handoff supersedes an older one, consume the newer record and read the
  superseded record only for history when needed.
- If multiple unsuperseded records match different workstream tags or clearly
  distinct threads, consume all of them.
- If multiple unsuperseded records appear to describe the same workstream, consume
  the newest one and flag that older records should probably have been superseded.

Do not list `task`/`closeout` records, scan all `docs/**`, git history, or
memory before this search is complete.

### 3. Consume the handoff

Read each selected handoff fully. **Branch on who wrote it — the daemon-set
`origin` field, not the body's prose.**

- **Self-published** (no `origin`): the `agent:good-night` template is normative.
  Extract the sections by name, then follow its `Reading Order` exactly until you
  can state the live thread.
- **Scribe-written** (`origin: "scribe"`): the body is the runtime's own shape and
  degrades to a minimal form — a valid one may carry little more than
  `PICK UP HERE` and a git snapshot, with **no `Reading Order` and none of the
  canonical sections**. Take what is there; follow `Reading Order` only if it is
  present. A missing section on this path is not a damaged handoff and is not a
  reason to bounce or re-derive — treat it as the runtime writing less, and
  recover the rest by verifying against the tree as below.

Either way, stop once you can state the live thread, unless verification requires
a cited file or command.

Preserve status distinctions. Do not collapse `Held for authority`, `Blocked`,
and `Deferred`; they imply different next actions.

### 4. Reconcile with current state

Verify load-bearing claims narrowly:

- Does the handoff's branch and `HEAD` match current branch and `HEAD`?
- Did local `HEAD` or `origin` move after the handoff was written?
- Does `git status --short` match the handoff's working-tree claim?
- Do cited files, commits, plans, and routed records
  (`coordination.read_artefact {id}`) still exist?
- Did another session complete, supersede, or invalidate any candidate next move?
- Are live-agent claims still true? Check `coordination.list_sessions` state
  (`running`/`wake-ready`) when relevant; a `known` ledger entry alone is not
  proof of liveness.
- Are `Held for authority`, `Blocked`, `Deferred`, `In flight`, and `Done` items
  still classified correctly?
- Is any dirty, local-only, uncommitted, or unpublished state still present and
  relevant?

If a claim cannot be verified with narrow checks, say so. Widen only as much as
needed to answer the verification question.

### 5. Settle the consumed record(s)

For each handoff you actually consumed, call
`coordination.settle_artefact {id}` with the consumed record's id so the store
can reclaim it. Do this after consumption succeeds, before or alongside the
pickup orientation.

- Settle only what you consumed. Superseded records read for history, and
  records belonging to another seat, are not yours to settle.
- **A failed settle is a warning, not a blocker.** Report it in the
  orientation's `Settled:` line and continue the pickup; do not retry-loop or
  halt on it.

### 6. Produce the pickup orientation

Before substantive work, emit a concise orientation:

```text
Handoff(s): <record id(s) + authored-by (self | scribe), or none found - degraded mode>
Settled: <record id(s) settled | settle failed for <id> (warning; continuing)>
Thread(s): <one-line strategic thread per handoff>
Pickup point: <PICK UP HERE summary>
Verified now: <facts checked against current tree>
Changed since: <none or exact deltas, including other-session work>
Open items: <Done / In flight / Held for authority / Blocked / Deferred>
Keep: <preserved decisions or constraints not to relitigate>
Candidate next move: <candidate under current instructions, not authority>
Authority check: <authorized to continue | unclear; needs question | not authorized>
```

Then continue only if current instructions authorize continuation. If authority,
scope, or routing is unclear, ask the smallest direct question after reporting
the orientation.

## Degraded mode

Enter degraded mode only after no matching handoff exists for the current slug or
role. Finding none is not necessarily an upstream failure: a genuinely fresh
seat has no predecessor, and an earlier wake may already have consumed and
settled the record (settled records are reclaimable). Reconstruct in this
order:

1. Broader `handoff` records (`coordination.list_artefacts {kind:"handoff"}`) that
   miss the successor-token pattern.
2. Recent coordination records (`coordination.list_artefacts`, any kind) whose
   `from` is the current slug, predecessor slug, or role, newest first.
3. Task briefs, closeouts, or review records (`coordination.read_artefact`), and
   plan docs, only when named by those artefacts or needed to identify the live
   thread.
4. `git log` for recent commits by the current identity, role, or predecessor.
5. Auto-memory or session memory as supporting signal only, never as authority
   over committed artefacts.

Report explicitly that no matching `good-night` handoff was found and list the
sources used. If current instructions authorize it, publish the `good-night`
handoff record the next wake should have had.

## Done when

Recalibration is complete when you can state which handoff records were
consumed and settled (naming any settle failure as a warning), what each thread
was, what changed since shutdown, which facts were verified against current
state, what remains done/in-flight/held/blocked/deferred, what decisions to
keep, and the candidate next move under current instructions.

## Anti-patterns

- Reconstructing from all of `docs/**` before listing handoff records.
- Waiting for a `coordination.deliver` wake from a `-next` successor token.
- Trusting the handoff's status block as current truth.
- Treating candidate next moves as authority.
- Ignoring dirty, uncommitted, unpublished, or local-only state named by the
  handoff.
- Confusing predecessor-authored continuity with unrelated teammate work.
- Re-reading the whole project when the handoff provides a reading chain.
- Asking "where were we?" before exhausting the handoff-first path.
- Discounting a scribe-authored handoff, or skipping its verification because
  the facts were "system-collected" — dated claims are dated claims.
- Leaving consumed handoffs unsettled, or the reverse: halting the pickup
  because a settle call failed (warn and continue).

## Distinct from

- **WIP handoff** (`agent:coordination-wip-handoff`): resumes one in-flight dispatch; `good-morning` resumes the whole seat.
- **Closeout** (`agent:coordination-closeout-templates`): records completed work at a gate; `good-morning` recovers an in-progress thread with open items intact.
- **Role contract:** defines authority; `good-morning` restores context only.

## Host neutrality

Keep this base procedure host-neutral. Use the current platform's read-only tools
for inspection, and write only when the active role/user/dispatcher instructions
authorize writing.
