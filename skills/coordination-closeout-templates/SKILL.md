---
name: coordination-closeout-templates
description: |
  Literal output templates for coordination artefacts — the worker close-out
  shape, the merge-close-out skeleton, the 5-line TL;DR with its rhythm-
  conditional Commits field, the lead's gate close-out record, and the per-role
  status block. Template/format only: WHICH artefact is mandatory WHEN, every
  STOP attached to an artefact, and the authority-rhythm branch logic stay in
  the role playbooks (worker §"Authority-rhythm interaction", lead gate
  sections). Populate the template under authority the playbook has already
  granted.
assumes:
  - |
    Claude roles read/invoke this via the native Skill tool or `Read`; Codex
    roles read it via `functions.exec_command`. Templates are platform-agnostic
    text; the role playbook decides when to emit each and under which rhythm.
---

# Coordination close-out & status templates

These are the literal shapes. The rule for WHEN each is mandatory, the STOP
conditions, and the authority-rhythm branch (option A/B/C/D) live in the role
playbooks — this skill never decides them.

**Policy-layer verification convention:** if the work being closed out touched the role-policy layer or any GENERATED contract / allowed-skills / authority-matrix block, the close-out's verification section must report the playbook repository's policy validator and its render-freshness check — both green, cited by their actual command names from that repository's own docs — as evidence the policy↔rendering lockstep holds.

## Worker regular close-out

Publish as a `closeout` record
(`coordination.publish_artefact {kind:"closeout", to:<recipient>, body:…}`;
addressing: `agent:routed-comms`). Body sections: status table · file
inventory · test results · per-fixture observations (if relevant) · open
questions · rejected findings · **Pre-commit cross-model review** record (the cross-model gate's outcome — tool + version + cross-model pairing, round-by-round trajectory, total findings, severity breakdown, final verdict, deferred-with-rationale; per `worker-agent.md` §"Transparency obligation", required at standard / high-risk) · **authority-rhythm-conditional terminal line**
(the line itself is per `worker-agent.md` §"Authority-rhythm interaction": STOP
under A; continuous-commit under B; queued under C; "Routed to Lead; proceeding
on the Lead's word…" under D).

## Pre-commit cross-model review

The close-out's cross-model gate record: tool + version + cross-model pairing, round-by-round
trajectory, total findings + severity breakdown, final verdict, and any deferred-with-rationale.
Required at standard / high-risk (per `worker-agent.md` §"Transparency obligation"); downstream
readers (lead, reviewer, PM) consume this record rather than re-running the loop.

## 5-line TL;DR (chat) + rhythm-conditional Commits

```
Close-out published: <record id>
Commits: <rhythm-conditional — see below>
TL;DR (3-4 lines): <what landed, key numbers, what was deferred, STOP signal>
```

(`Commits:` still lists the *product-code* SHAs the close-out describes — product
code is committed locally and published to the remote with `git.push_branch` as
before; only the close-out artefact itself moved from a `docs/` file to a
coordination record.)

Rhythm-conditional `Commits:` field:
- **Option A:** `none — awaiting green-light before commit + branch publication`
- **Option B:** `<sha-list of all commits the close-out describes>`
- **Option C:** `none — queued for cycle batch`
- **Option D:** `<sha-list of all commits the close-out describes>` (or `none — held by dispatch STOP-condition`)

## Mandatory merge close-out

**A landing is requested, not executed.** Only the **lead** may request one, and
only the daemon performs it (`agent:branch-lifecycle` §"Merge to main"):

```text
git.request_landing {sha: "<candidate SHA>", task_record_id: "<task record id>",
                     repo: "<repo-name>", branch: "<branch>"}
  → {landing_id, status, reason?}
```

**The `merge_closeout` record is written by the daemon, not by you.** On — and
only on — the `landed` transition, the daemon publishes it: authored by the
daemon, correlated (`re`) to the `task` record the landing completed, carrying
the candidate SHA, the landing commit (`head_sha`), the branch and the
repository. It is written exactly once per landing. **No session publishes a
`merge_closeout`, for any outcome.**

**Where each fact lives matters, because most of them are NOT in the body.** The
record's **body is the review summary** the daemon composed from the gate
verdicts. Everything below rides as a **structured field**, which is where you
read it from — do not grep the body for it, and do not expect a line saying
`status landed`, because none is written:

| what you want | where it is |
| --- | --- |
| the task this landing completed | `re` — the `task` record's id |
| the commit every gate verdict cited | `candidate_sha` |
| the landing commit on the integration branch | `head_sha` |
| the integration branch | `branch` |
| the repository | `repo` |
| the review summary | the body |
| the landing's own id and status | **not on this record** — they are the `{landing_id, status}` your `git.request_landing` call returned |

Read the record; do not author it, and do not reconstruct it in prose.

**And do not read the record's mere EXISTENCE as proof that a landing happened.**
"No session publishes a `merge_closeout`" above is a rule this framework imposes on
roles, not a thing the wire prevents: `merge_closeout` is in the caller-selectable
kind set, so a session CAN publish one, and the daemon stamps that record with the
CALLER's role like any other. **The authoritative answer is the `{status}` your own
`git.request_landing` returned** — only `landed` means it merged. When you are
reading a close-out you did not request yourself, check the daemon provenance the
daemon stamped (author role `daemon`) and that `re`, `candidate_sha` and `repo`
match the landing you mean, rather than trusting the kind alone. A record whose
kind says `merge_closeout` is a claim; the stamped author and the returned status
are the evidence.

What that leaves you, as the lead who requested it:

- **Cite the `landing_id`** — not a merge command and not a SHA alone — wherever
  you report the close (your gate close-out record, your chat TL;DR), together
  with the authority the landing ran under (`<A: operator green-lit at step <N> |
  B: pre-authorized | C: batch | D: CTO green-path authorized (or CTO-relayed
  operator reply)>`).
- **Only `landed` produces a merge close-out**, and only from the daemon. Every
  other status produces none — not from the daemon and not from you, and none of
  them is itself evidence of a remote change. A `refused` landing changed nothing
  on the remote and needs no record beyond your own reporting. When a `failed` one
  left the remote changed, publish a `clarification` naming the `landing_id`, the
  status and the `reason` the daemon gave, and let an operator reconcile it.
- **Local branch cleanup is not part of this record.** Removing the worktree and
  deleting the local branch after a landing is ordinary lead reporting
  (`agent:branch-lifecycle` §"Cleanup"); the merged remote branch is not deleted
  at all.

## Lead gate close-out record

Written by the lead when closing a gate (Gate 1 architect feasibility, Gate 2
QA-floor + reviewer security/compliance, etc.). Records the disposition so the
gate decision is auditable. The authority — which findings are operator-only
override, when a floor reduction is permitted, the rhythm-conditional escalation
routing — lives in `lead-agent.md` §"Dispatching review roles" / §"Risk-triage
gate"; this is only the record shape.

```markdown
# Gate <id> close-out — <phase/component> (<YYYY-MM-DD>, lead <lead-id>)

**Gate:** <Gate 1 (architect) | Gate 2 (QA + reviewer) | ...>
**Verdicts (record ids):** architect <id/—> · QA <id/—> · reviewer <id/—>
**Floor reconciliation:** <QA-floor satisfied | reduction acknowledged with rationale: <…> | re-dispatched QA | n/a>
**Overrides (with acknowledgment):** <none | HIGH/MEDIUM/LOW item <X> overridden, acknowledged in this record | CRITICAL → operator-only, see risk-triage <id>>
**Authority rhythm:** <A | B | C | D> — <who authorized the gate-clearing action>
**Disposition:** <gate cleared → next phase | held → reason + routing | escalated → risk-triage <id>>
```

## Per-role status block

Every substantive response from a review/recon role includes a `## 📊 Status`
block. The shape is shared; the field-set is role-specific:

- **architect:** Phase (intake | reconnaissance | review | delivering) · Input shape · Subject · Dimensions covered · Open unknowns · Blockers.
- **qa:** Phase (intake | reconnaissance | strategy | delivering) · Subject · Dimensions covered · Open unknowns · Blockers. (+ `🔖 metanote:` when relevant.)
- **explorer:** Phase (breadth pass | checkpoint | deep pass | delivering) · Active focus · Coverage (covered vs outstanding) · Open threads · Blockers. (+ `🔖 metanote:`.)
- **reviewer (in-progress):** Phase · Diff (branch + range) · Surfaces in progress (OWASP `covered / total-applicable` · GDPR `covered / total-applicable` · project regime) · Findings (CRITICAL/HIGH/MEDIUM/LOW/INFO counts) · Open dialogues.
- **reviewer (delivered):** `## 📊 Status — Delivered` · Verdict (block | accept with required fixes | accept with advisories | accept) · Artefact (record id) · Findings (counts) · Load-bearing finding · Worker dialogue (resolved / outstanding) · Unknowns.

For the review roles that emit a separate **Delivered** block (architect, QA,
explorer, reviewer), the delivered variant swaps `Phase` for `## 📊 Status —
Delivered` and reports the terminal verdict/output reference (record id for a routed verdict, or a durable-doc path)/coverage. Surface counts
are always `covered / total-applicable` (never a hardcoded denominator — the
applicable total is per-dispatch from the trigger matrix).
