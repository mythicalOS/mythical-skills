---
name: routed-comms
description: |
  Mechanics of routed communication between agent sessions — publishing a durable
  coordination record with `coordination.publish_artefact`, resolving and waking
  the live recipient with `coordination.resolve_recipient` + `coordination.deliver`,
  the artefact `kind` enum + recipient `to` token, reading inbound records with
  `coordination.list_artefacts` + `coordination.read_artefact`, the bounce-back routing procedure,
  and delivery-failure handling. The published record is the durable artefact + the
  address; waking the recipient is a separate `coordination.deliver` call (a
  published record alone wakes no one). Procedural only: routing AUTHORITY (who may
  address whom, "never relay via the operator", presence-in-chat ≠ dispatcher) lives
  in `ROLES.md` §"Cross-role principle — completion includes the counterpart" → Reach
  and in the role playbooks. This skill is the HOW, never the whether-or-to-whom.
assumes:
  - |
    Claude Code roles read/invoke this via the native Skill tool or `Read`;
    Codex roles read this file via `functions.exec_command`. Both lanes call the
    same `coordination.*` MCP tools, composed per session by the daemon; the
    mechanics are platform-agnostic and the tool names are identical on both.
  - |
    The CTO consults this as a read-reference for recipient resolution when
    relaying — reading a doc, not a Skill-tool invocation, so it does not
    relax the CTO's no-autonomous-skill rule (`cto-agent.*.md` §"Allowed
    skills").
---

# Routed comms — inter-session artefact + wake mechanics

Routed comms have two halves. The **record + address**: publish a durable
coordination record with `coordination.publish_artefact {kind, to, body}` — the
daemon appends the record to your project's coordination store, mints its **id**,
and returns `{id, kind, created_at}`. That record is the durable handoff, and its
`to` token plus the daemon-minted id are how it is addressed. The **wake**: call
`coordination.deliver {to, body, class}` carrying that id — the doorbell that pulls
an idle recipient back. **The published record alone wakes no one**; without the
`deliver` the record just sits in the store until the recipient happens to list it.
A `deliver` whose `to` the daemon cannot resolve to a **live** session is refused
(`UNKNOWN_RECIPIENT`) — the daemon is authoritative, so a mistyped or dead recipient
fails closed at the call instead of becoming a silent dead-letter. This skill is the
HOW. *Whether* an artefact must be routed, and *to whom*, is authority — `ROLES.md`
§"Cross-role principle — completion includes the counterpart" → Reach, plus each
role's dispatcher rules. Reaching a non-recipient in chat (the operator watching
your session) instead of routing is the **user-mediated-relay anti-pattern**; the
bases own that rule, not this skill.

## 1. Artefact kind + recipient token

Publish the record with `coordination.publish_artefact {kind, to, body}`:

- **`kind`** is one of the frozen coordination kinds — the record type the daemon
  stores and the recipient filters on. An unknown kind is refused (`INVALID_KIND`):
  `handoff · dispatch · acknowledgment · task · closeout · merge_closeout ·
  clarification · addendum · wip_handoff · risk_triage · design_review ·
  test_strategy · code_review`.
- **`to`** is the recipient token that addresses the record. For a live routed
  handoff it is the recipient's canonical address as returned by
  `coordination.resolve_recipient` (§2). It MAY also be a **discovery token**
  (`<role>-next`, `<slug>-next`) that need not be live — that is how a `good-night`
  handoff or an initial hand-to-a-not-yet-running-seat is addressed (§5). The daemon
  binds the **author** from your session (never an input), so there is no sender
  segment to encode and no way to address a record as if from someone else.
- **`body`** is the artefact payload (≤ 256 KiB; over → `BODY_TOO_LARGE`).
- **The structured fields — the ones a machine reads.** Optional in the schema,
  not optional in effect: `re` (the record or landing this one answers),
  `branch` / `head_sha` / `repo` (the state it was written against), and — on a
  verdict kind — **`verdict`** (`green` or `reject`) and **`candidate_sha`** (the
  exact commit reviewed). Put the fact in the field, not only in the prose; a
  consumer reads the field.

  **On a verdict kind, `verdict` and `candidate_sha` are the two that are
  silently expensive to omit.** The daemon derives a landing gate from
  `design_review` + architect, `code_review` + reviewer, and `test_strategy` +
  qa — from those fields, **never by parsing the body**. A verdict published
  without them is stored, delivered, and read by a human exactly as normal, and
  produces **no gate at all**, and nothing in your own publishing session says
  anything is wrong. The architect and reviewer gates are REQUIRED, so a lost one
  refuses the landing later — late, but loud, which is the only reason the
  omission gets found at all.

  **The `test_strategy` + qa row is a seam, not a live gate.** The daemon maps it
  to a conditional `qa-pass`, but a QA session is strategy-only under its own role
  contract and issues no verdict, so that gate is normally unlit and its absence
  refuses nothing. Read the row as capacity the runtime already has, not as an
  instruction: whether QA may put a verdict on a strategy is a role-contract
  question, and the answer today is no. A `verdict: green` line in the body is not
  a substitute — that rule was
  deliberately withdrawn, because a gate derived from caller-authored prose is a
  gate any session can write for itself.

  **`repo` behaves differently, and the difference is the point: omitting it
  never fails silently.** Three cases, all of them either correct or loud —
  *multi-repository*: on a verdict kind carrying a `candidate_sha` it is REFUSED
  at the call (`INVALID_FIELD`), because guessing would attribute a review to the
  wrong repository. *Single-repository*: the daemon fills in the primary
  repository and stores it explicitly, so a later reader never re-derives it.
  *No repository configured*: a verdict carrying a `candidate_sha` is refused —
  the daemon will not record a review of a commit it cannot attest was published
  anywhere — while every other record is stored repo-less, honestly. So `repo`
  either works or tells you, which is exactly why the other two deserve the care:
  "the record published fine" proves nothing about them.

`publish_artefact` returns a daemon-minted **`id`**; that id is the address you carry
in the wake (§3) and in any later reference to the record. The daemon owns the id and the
durable write (temp + fsync + no-clobber `link` + dir-fsync before it acks, so a
returned id survives a crash). The `<role>-to-<role>` pairs named inline in playbooks
(`pm-to-lead`, `lead-to-pm`, …) denote the **role-pair**; at runtime `to` resolves to
the live recipient address.

Which kind carries what (the routed content each record type holds):

| Kind | Carries |
| --- | --- |
| `closeout` / `clarification` / `wip_handoff` / `addendum` | worker/lead close-out trail |
| `handoff` / `dispatch` / `acknowledgment` | dispatch + continuity handoffs |
| `risk_triage` | lead→apex risk triage |
| `design_review` / `test_strategy` / `code_review` | review-role verdicts |
| `task` | task brief (recipient-addressed) |
| `merge_closeout` | merge close-out |

**Sibling namespaces on the same bridge.** `coordination.*` is the routing
surface, and it is not the only namespace the daemon composes for a session. Two
others carry work that used to be done by hand, and this skill owns neither:

- **`workitems.*`** — `workitems.list {}` / `workitems.get {id}`, **read-only**
  for agents. A work item's lifecycle is driven by the coordination records you
  publish here (a `task` record opens it; a `merge_closeout` carries it to
  merged), so there is no agent-side write tool.
- **`git.*`** — `git.push_branch {repo?, branch, sha}` publishes a feature branch
  to the shared remote (**worker or lead** only), and `git.request_landing
  {sha, task_record_id, repo?, branch?}` asks the daemon to land a reviewed
  candidate (**lead** only). Sessions hold no remote credential; the daemon owns
  the remote. The mechanics are `agent:branch-lifecycle`, and which role may call
  which tool is the daemon's decision, not a claim a session makes.

The two interlock with the records: `git.request_landing` names the `task` record
its landing completes, and the `merge_closeout` the daemon publishes when that
landing succeeds correlates back to the same record id.

## 2. Resolving + confirming the recipient

The daemon is the sole authority on who is live. The presence registry is
daemon-private — the session cannot read it — so identity and peers come only from
the tools:

- **Your own identity** (slug / role / project / session): `coordination.whoami {}` →
  `{slug, role, project, session_id}`. It returns your project directly; there is no
  path or environment derivation to do.
- **Peers and their live state**: `coordination.list_sessions {role?,
  include_terminal?}` → `{sessions:[{slug, role, state, started_at, session_id}]}`.
  `state` is daemon-authoritative and folds presence and liveness into three tiers:
  `known` (a durable ledger entry, any lifecycle state — surfaced only under
  `include_terminal:true` if terminal), `running` (resolves to a non-terminal
  session), and `wake-ready` (the daemon can inject a wake **now** — a true
  can-the-session-receive-a-wake signal, not merely "a process exists"). `role?`
  filters within your project.
- **One recipient's canonical address**: `coordination.resolve_recipient {to}` →
  `{ok:true, to}` on a live match, or `{ok:false, code:UNKNOWN_RECIPIENT}` when `to`
  matches no live peer in your project (the refusal names near-matches, never a
  silent accept). It folds the `to` token and fails **closed** — an unreadable/absent
  recipient set is a refusal,
  never a silent pass-through.

Resolution is **project-scoped**: the daemon only ever resolves peers in your own
project; a cross-project `to` is refused (`CROSS_PROJECT_REFUSED`).

## 3. The wake

`coordination.deliver {to, body, class, expectReply?, inReplyTo?}` → `{id, status}`
is the doorbell. Publishing the record wakes no one; the `deliver` is what pulls an
idle recipient back to the artefact.

- **`to`** MUST resolve to a **live (wake-ready)** recipient in your project → else
  `UNKNOWN_RECIPIENT`. (Unlike `publish_artefact.to`, a `deliver` cannot target a
  non-live discovery token — a wake with no one to wake is refused, not
  dead-lettered.)
- **`body`** carries the pointer — normally the `id` returned by `publish_artefact`
  plus a one-line summary (≤ 16 KiB; over → `BODY_TOO_LARGE`). The recipient reads
  the full record with `coordination.read_artefact {id}`.
- **`class ∈ {asap, on-done}`** — `asap` injects at the recipient's next message
  boundary even mid-run; `on-done` holds until the recipient goes idle.
- `expectReply?` / `inReplyTo?` link a reply to its original; an `inReplyTo` that
  names no known original in the store is refused (`INVALID_REPLY_LINK`).

`status` is `queued` (persisted before ack; delivery is at-least-once). The sequence
for a routed handoff is therefore: `publish_artefact` → carry the returned id →
`deliver` that id to the resolved recipient.

## 4. Reading inbound artefacts

To pick up what has been routed to you, read off the daemon socket — no git, no merge:

- `coordination.list_artefacts {kind?, since?}` → `{artefacts:[{id, kind, from, to,
  created_at}]}` — metadata-only discovery over your project's records; filter by
  `kind` and/or an ISO-8601 `since` lower bound.
- `coordination.read_artefact {id}` → `{id, kind, from, to, created_at, body}` — the
  full record. An id that is not in your project reads as `NOT_FOUND` (no
  cross-project probe).

A `deliver` wake normally hands you the id directly; `list_artefacts` is for sweeping
what is addressed to you when you were not woken for each record.

## 5. Discovery tokens vs live wakes (the not-yet-running-seat case)

`resolve_recipient`/`deliver` refuse an unknown or non-live `to`, so a wake can
never be addressed to a name that resolves to no one.

For the **initial hand to a seat that is not running yet** (the classic initial
PM→lead handoff, or any `good-night` continuity handoff), publish with a **discovery
token** and send **no** wake: `coordination.publish_artefact {kind:"handoff",
to:"lead-next", body:…}`. Starting that seat is a launcher/human action; when it comes
up, its `good-morning` finds the record via `coordination.list_artefacts` on the
successor token — discovery, not wake. Every *mid-flight* delivery to an
already-running seat resolves the live recipient (§2) and carries a real `deliver`
wake.

## 6. Bounce-back as a routing mechanic

A missing-field / missing-intent / scope-clarification bounce is itself a routed
artefact, not a chat message: when the dispatcher is a routed (idle) session, publish
a `clarification` record addressed to the dispatcher
(`coordination.publish_artefact {kind:"clarification", to:<dispatcher>, body:…}`),
`coordination.deliver` its returned id to the dispatcher, and STOP. **Publishing the
bounce is administrative routing — the transport, not a work deliverable — so it is
permitted regardless of the (possibly-missing or unclear) work-authority rhythm**, the
same precedent as the architect's `needs clarification (intake)` artefact. A chat-only
bounce reaches the user, not the idle dispatcher. (An operator-direct dispatcher present in
chat may receive a chat bounce, or a chat *pointer* to the record — never the payload
to an idle session.)

## 7. Delivery-failure handling

Under the daemon lane routing fails **loudly**, not silently: `deliver` returns a
typed error rather than dead-lettering.

1. **Before waking, resolve the recipient** with `coordination.resolve_recipient {to}`
   (or confirm `coordination.list_sessions` reports the seat `running`/`wake-ready`).
   A recipient that is not live is refused up front — you never route to a dead session.
2. **On `UNKNOWN_RECIPIENT` from `deliver`**, the `to` names no live peer (the session
   may have rotated to a new instance, or exited). Re-check `coordination.list_sessions`
   for the current live seat and re-`deliver`. If no live recipient session exists,
   surface the routing failure to the dispatcher/apex rather than treating the record
   as delivered.
3. The published record is durable regardless — a failed wake never loses the artefact;
   it stays in the store for the recipient to `coordination.list_artefacts` / `coordination.read_artefact` once
   live.
