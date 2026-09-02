---
name: good-night
description: >-
  The format of the good-night continuity handoff — the durable `handoff`-kind
  coordination record `good-morning` consumes. Every retiring session is
  guaranteed one: the system scribe writes it from the session record on the
  session's behalf, unless the session chooses to publish its own first (then
  the scribe stands down). This skill defines the record's shape — deterministic
  successor token, exact pickup point, strategic thread, ordered reading chain,
  verified branch/git/local state, coordination state, classified open work,
  preserved decisions, reconcile checks, and candidate next moves — and carries
  the optional self-publish procedure (`coordination.publish_artefact`).
  Procedural only: current role/user/dispatcher instructions decide whether the
  agent may publish, route, spawn, stop, continue, or change scope.
assumes:
  - |
    The deployment runs the system scribe, which guarantees every retiring
    session a handoff written on its behalf from the session record. No role
    is obliged to self-publish; the optional self-publish procedure applies
    only where the active contract permits publishing.
  - |
    Self-publish, where permitted, uses the same `coordination.publish_artefact`
    tool composed per session by the deployment. The template here is normative
    for a SELF-published handoff; a scribe-written one is the same record kind to
    the same successor token, but the runtime owns its body and sets no structured
    git fields, so a consumer distinguishes them by the daemon-set `origin`.
---

# good-night

`good-night` defines the continuity handoff format: a compact, verifiable
resume point for the next session in the seat. The output is not a status
report to a human, not a memory dump, and not a role contract. It is the
artifact a cold `good-morning` should consume first.

**Who writes it.** Every retired session is guaranteed a good-night handoff.
By default the **system scribe** writes it on the retiring session's behalf,
from the session record. A session may instead choose to **publish its own**
handoff before retiring — if it does, the scribe stands down. Self-publishing
is a choice, not an obligation: there is no duty to fire a good-night before
stopping, and a session that retires abruptly still leaves a handoff behind
(the scribe's). Both paths produce a `handoff`-kind record for the same
successor, and the record's `Authored` provenance line states which path produced
it — but they are not byte-for-byte the same artefact: this skill's template is
normative for the self-publish path, while the scribe's body and fields are the
runtime's (§"Addressing").

## Core rules

These bind whoever authors the handoff — the scribe or a self-publishing
session:

- **Optimize for pickup, not completeness.** Lead with `PICK UP HERE` and a
  short reading chain. Do not summarize the whole project.
- **Write a dated index.** Anchor claims to paths, SHAs, commands, session state,
  or routed records so the successor can verify what changed after shutdown.
- **Classify open work.** Keep `Held for authority`, `Blocked`, and `Deferred`
  separate; they require different behavior.
- **Expose local dependencies.** Name dirty, unstaged, uncommitted, unpublished,
  unrouted, and local-only state plainly.
- **Preserve state, not authority.** Candidate next moves are hypotheses for the
  successor to verify under current instructions, never orders.
- **Self-publish early or not at all.** If you choose to publish your own
  handoff, do it while context is still good enough to verify your own claims.
  A late self-published handoff based on degraded memory is worse than none —
  it looks authoritative — and "none" is safe: the scribe writes from the
  session record, not from your memory.

## Contract with `good-morning`

`good-morning` consumes what this format describes. This section and
§"Handoff template" are the pair's **single source** — `agent:good-morning`
references them rather than restating the contract.

- **Where:** a `handoff`-kind coordination record — self-published via
  `coordination.publish_artefact {kind:"handoff", to:<slug>-next, branch:…,
  head_sha:…, body:…}`, or scribe-written as the same record KIND to the same
  successor token (not the same fields or body — see below); the daemon
  mints its id and stores it durably. No `docs/` file, no filename grammar.
  `branch` and `head_sha` are **structured fields on the record**, not only body
  prose (§"Handoff template" → *Publish it with its structured fields set*).
- **Successor token (`to`):** `<slug>-next` for same-seat continuation, or
  `<role>-next` when any fresh instance of the role may inherit.
- **Provenance:** the body's `Authored` line states whether the record was
  self-published or scribe-written on the session's behalf, and the daemon-set
  `origin: "scribe"` field says so independently of any body text — prefer the
  field, since a session cannot set it. `good-morning` verifies dated claims the
  same way on both paths, but must **not** require this template's canonical
  sections or the structured git fields on a scribe-written record: it may carry
  neither (§"Addressing").
- **Settlement:** after successfully consuming the handoff, the successor
  settles it (`coordination.settle_artefact {id}`) so the store can reclaim
  the record. Settlement is the consumer's step, not the author's.
- **Discovery, not wake:** `-next` is a discovery token, not a live recipient. Do
  not route or wake a successor that does not exist yet. If a live teammate must
  act now, publish the separate routed record required by the active role contract
  and `coordination.deliver` its id. (`agent:routed-comms` owns live wake-routing
  and the no-dead-letter guarantee; the `-next` discovery name is this skill's own.)
- **Canonical sections and status labels:** exactly those in §"Handoff template"
  below — the template is normative, not illustrative.

## Addressing

On the self-publish path, the session publishes with
`coordination.publish_artefact {kind:"handoff", to:<successor-token>,
branch:<branch>, head_sha:<full-SHA>, body:…}` — you supply the successor `to`,
the two structured git fields, and the body; everything else (the author, the
id, the timestamps) is the daemon's. `branch` is omitted on a detached HEAD;
`head_sha` is omitted only when `HEAD` resolves to nothing at all
(§"Handoff template"). A
scribe-written handoff is system-written from the session record on the retired
session's behalf; the result is the same `handoff`-kind record, addressed to the
same successor token, for the same continuity purpose. **It is NOT the same
record in its fields or its body, and a successor must not assume it is:** a
scribe-written handoff carries `kind`, `from`, `to`, `project`, `body` and a
`scribe` origin marker, and sets **neither `branch` nor `head_sha`** — whatever
git facts it preserves live in the body. Its body is the runtime's own shape, and
degrades to a minimal form under pressure, so a successor that requires the
canonical sections of this template will not find them in every valid scribe
handoff.

**Tell the two apart by `origin`, never by a missing field.** `coordination.read_artefact`
surfaces `origin: "scribe"` on scribe-written records and omits it on
seat-published ones, and a session cannot set it — `publish_artefact` has no such
input, so it is trustworthy. A missing `head_sha` is NOT the discriminator: a
self-published handoff legitimately omits it when `HEAD` resolves to nothing
(above). Read `origin` to know who wrote it; read a missing `head_sha` as exactly
what it is — no structured commit data on this record.

Token rules:

- The **author** is never an input: on the self-publish path it is your session
  slug, socket-bound by the daemon (`coordination.whoami` reports it); on the
  scribe path the `Authored` line names the retired session as the
  on-behalf-of author.
- `<successor-token>` (the `to`) is `<slug>-next` when the same identity
  should resume, or `<role>-next` when any fresh instance of the role may inherit.
  A discovery token: it need not resolve to a live session.
- A workstream tag, when genuinely parallel threads exist, goes in the body's
  title / `Strategic Thread`. Prefer one roll-up handoff per seat; split only for
  genuinely parallel threads.

If replacing an earlier handoff for the same workstream, publish a new record and
name the superseded record id in `Supersedes:` in the body metadata. Do not mutate
continuity history unless current instructions explicitly require an in-place
correction.

## Self-publish procedure (optional)

A session that chooses to publish its own handoff before retiring follows this
path. Skipping it is always safe — the scribe then writes the handoff from the
session record.

1. **Check authority.** Confirm current instructions permit publishing a durable
   handoff record. Route, spawn, stop, or continue only if separately authorized.
2. **Identify the seat.** Establish current slug, role, project, and successor
   token from `coordination.whoami`.
3. **Freeze ground truth.** Capture date, branch, `HEAD`, relevant upstream
   state, `git status --short`, and any relevant live-session state from
   `coordination.list_sessions`.
4. **Verify before writing.** Re-check each load-bearing status claim against
   files, commits, command output, routed records, or `coordination.list_sessions`
   state. Do not write remembered state as fact. (This is the self-publisher's
   bar; on the scribe path the `Verification Snapshot` is filled from
   system-collected facts in the session record, not from agent claims.)
5. **Write from the template.** Keep section names verbatim. Put the next
   concrete pickup action in `PICK UP HERE` and the durable why in
   `Strategic Thread`.
6. **Classify open threads.** Use the canonical labels exactly:
   `Done`, `In flight`, `Held for authority`, `Blocked`, `Deferred`.
7. **Preserve what to keep.** Name decisions, constraints, norms, and conclusions
   the successor should not relitigate.
8. **Label next moves as candidates.** They are hypotheses to verify under the
   successor's current instructions, not standing orders.
9. **Persist only as authorized.** A published handoff record is durable
   daemon-side and readable by any live session in the project via
   `coordination.read_artefact`. The record captures *state*, not the *work*: any
   uncommitted product-code state, or commits not yet published to the remote,
   stays local — state the exact path and reason so the successor inherits it
   knowingly.

## Handoff template

Use this shape. Omit a placeholder only when it is genuinely not applicable; do
not rename headers.

**Publish it with its structured fields set.** The branch and the HEAD sha are
not only header prose — they are first-class fields on the record. Pass them to
`coordination.publish_artefact` alongside the body:

```text
coordination.publish_artefact {kind: "handoff", to: "<successor-token>",
                               branch: "<branch>", head_sha: "<full-SHA>",
                               body: "<the template below>"}
```

`head_sha` is the full object id (40- or 64-hex) read fresh from
`git rev-parse HEAD` — never abbreviated, never remembered; `branch` is the
branch that sha sits on. Carry **exactly** the values the `Branch / HEAD:` header
line carries: a field that disagrees with the body is a defect, and a malformed
value is refused (`INVALID_FIELD`) rather than silently stored. Setting them is
what lets a successor find the handoff by branch or commit without parsing
prose. On a detached HEAD there is no branch but there is still a commit: omit
`branch`, keep `head_sha`, and say so in the header line. Omit `head_sha` too only
when `HEAD` resolves to nothing at all (an unborn branch, no commit yet) — never
invent a placeholder for either.

```markdown
# Good-night handoff - <author> -> <successor> - <workstream>

**From:** <author-token> (<role>)
**To:** <successor-token>
**Authored:** <self-published | system scribe, from the session record on behalf of <author-token>>
**Project:** <project>
**Date written:** <YYYY-MM-DD>
**Branch / HEAD:** <branch> @ <sha>
**Working tree:** <clean | dirty; list paths>
**Authority / dispatch context:** <rhythm, dispatcher, direct request, or none>
**Identity source:** <coordination.whoami session_id | session record | launch prompt | other>
**Supersedes:** <superseded record id or none>

## PICK UP HERE

<One short paragraph naming the live thread, the first file to read, and the
first state claim to verify.>

## Strategic Thread

<One sentence: what this work is about and why it matters.>

## Reading Order

1. `<path>` - <why this is first>
2. `<path>` - <why this is second>
3. `<path>` - <only if needed>

## Current State

- Done: <verified completed facts, with paths/SHAs>
- In flight: <unfinished work and where it lives>
- Held for authority: <decision needed, owner, and path>
- Blocked: <blocked item, blocker, and path>
- Deferred: <not blocked; just not started>

## Verification Snapshot

- `<command or evidence>` -> <result>
- `<command or evidence>` -> <result>

## Changed Files And Local State

- Branch: `<branch>`
- Commit(s): `<sha>` - <meaning>
- Uncommitted files: <none or explicit list>
- Unpublished work: <none or explicit list — committed locally, not yet on the remote>
- Local-only context: <none or exact note>

## Coordination State

- Live / stale / unknown sessions: <relevant sessions + `list_sessions` state>
- Routed records awaiting pickup: <record ids or none>
- Successor pickup: discovery-only; no wake sent
- Live teammate routes/wakes: <record ids and delivered/not sent/not applicable>
- Liveness caveat: <anything the successor must re-check>

## What To Keep

- <Decision, constraint, norm, or conclusion not to relitigate>

## Open Risks And Reconcile Checks

- <status claim the next agent must verify> - <how to verify> - <risk/status>
- <known stale-risk, conflict, or external dependency>

## Candidate Next Moves

1. <candidate action to verify under current instructions; not authority>

## Do Not Assume

- <thing that looked true at shutdown but may no longer be true>
- <thing this handoff explicitly does not authorize>
```

## Quality bar

A useful `good-night` is:

- **Addressable:** the successor `to` token tells `good-morning` who it is for.
- **Provenance-honest:** the `Authored` line says who wrote it — the session
  itself, or the scribe on the session's behalf.
- **Minimal:** it points to the shortest reading chain, not the whole project.
- **Verifiable:** claims cite files, SHAs, commands, session state, or records
  (the verification bar per path is §"Self-publish procedure" step 4).
- **Current-at-write-time:** it records live state, not remembered state.
- **Classification-clean:** done, in-flight, held, blocked, and deferred work
  are distinct.
- **Authority-clean:** candidate moves are not permission grants.
- **Durability-honest:** committed / published-to-the-remote / local-only state
  is reported exactly.

## Done when

A fresh successor can run `good-morning` against the handoff, recover the
seat-level thread, reconcile it against current state, and continue under its
own authority with no human re-explanation. If a human would still need to
supply missing state, the handoff is not done.

## Anti-patterns

- Writing to the human/operator instead of to the successor.
- Omitting `PICK UP HERE`, or burying the real next step.
- Saying "all green" without paths, SHAs, checks, or artefacts.
- Hiding dirty, uncommitted, unpublished, unrouted, or local-only work.
- Dumping a broad project summary instead of a reading chain.
- Calling deferred work blocked, or held-for-authority work free.
- Treating candidate next moves as orders.
- Waking (`coordination.deliver`) a `-next` successor token instead of publishing
  it for discovery.
- Self-publishing after context quality is too degraded to verify your own
  claims — stand down and let the scribe write from the session record instead.
- Treating self-publication as a duty owed before every stop; the guarantee is
  the scribe's, not the agent's.

## Distinct from

- **WIP handoff** (`agent:coordination-wip-handoff`): transfers one in-flight dispatch; `good-night` is seat-level continuity and may point to WIP handoffs.
- **Closeout** (`agent:coordination-closeout-templates`): records completed work at a gate; `good-night` records where the seat is stopping, open threads included.
- **Role contract:** defines authority; `good-night` records state, never the successor's permissions.

## Host neutrality

Keep this base procedure host-neutral. Use the current platform's tools for
inspection and writing, but only within the authority granted by active
instructions.
