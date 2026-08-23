---
name: plan-execution
description: |
  How to execute an implementation plan inside a dispatched task brief —
  load and critique the plan before starting, work its steps within the
  isolated worktree + feature branch, map review checkpoints onto the
  framework's close-out / WIP-handoff / rhythm STOP points, and stop
  rather than guess when blocked. Procedural only: the plan content and
  the dispatch decision are the dispatcher's (this skill does not plan —
  that is `implementation-planning`); WHICH authority rhythm gates the
  irreversibles is the invoking playbook's. This skill is the disciplined
  HOW of carrying a brief to a reviewable branch.
assumes:
  - |
    Execution happens within a dispatched brief, in the session's own
    worktree on its own feature branch (`worktree-management`,
    `branch-lifecycle`). The plan was produced upstream
    (`implementation-planning`); this skill does NOT re-plan.
  - |
    Claude Code roles execute via `Bash` + the native edit tools and
    invoke checkpoint skills via the Skill tool; Codex roles via
    `functions.exec_command` / `functions.apply_patch` and by reading the
    checkpoint skills. The critique-before-start, stop-don't-guess, and
    checkpoint-mapping discipline is platform-agnostic.
---

# plan-execution

The procedure for turning a dispatched implementation plan into a reviewed
feature branch. It executes the plan's steps faithfully, surfaces checkpoints at
the framework's existing STOP points, and stops-and-routes when blocked instead
of inventing its way past a gap. It does **not** create the plan — that is
`implementation-planning` upstream — and it does not decide its own authority
rhythm.

## Authority boundary (read first)

- **The plan and the dispatch decision are not the executor's.** The executor
  works within the brief; a disagreement with the plan is routed back as a
  clarification, not resolved unilaterally.
- **STOP-on-blocker routes upward as an artefact, not a chat aside.** When a
  blocker or context-degradation STOP fires, the executor writes a WIP-handoff to
  the lead (`agent:coordination-wip-handoff`) — a chat-only "I'm stuck" reaches no idle
  dispatcher (`agent:routed-comms`).
- **The authority rhythm gates the irreversibles, and it is the invoking
  playbook's call.** Whether the close-out is itself a STOP point (rhythm A) or the
  post-close-out push + review-ready sequence runs continuously (rhythm B) is
  decided in the brief, not here (`ROLES.md` §"Authority rhythms"). The merge to
  `main` is the lead's regardless — not part of this worker sequence
  (`branch-lifecycle` §"Merge to main").

## §"Load and critique the plan/brief"

1. Read the plan / brief in full before touching code.
2. Critique it: are there gaps, contradictions, undefined symbols, or steps you
   cannot start? Check it against the actual codebase, not just for internal
   consistency.
3. **If you have concerns** — route a clarification bounce to the dispatcher:
   publish a `clarification` record
   (`coordination.publish_artefact {kind:"clarification", to:<dispatcher>, body:…}`)
   and `coordination.deliver` its id to the dispatcher, then STOP; do not start on a
   plan you cannot execute (`agent:routed-comms` §"Bounce-back"). Publishing a
   clarification bounce is administrative routing, permitted regardless of the
   work-authority rhythm.
4. **If no concerns** — set up the isolated worktree + branch
   (`worktree-management`, `branch-lifecycle`), confirm a clean baseline, and
   proceed.

## §"Execute within the brief"

Work the plan's steps in order, on the feature branch:

- Follow each step as written (a good plan is bite-sized: write the failing test,
  run it red, implement minimally, run it green, commit). Do not skip the
  verifications the plan specifies.
- Stay in scope. The brief's in/out-of-scope boundary holds; a discovered
  adjacent improvement is surfaced (close-out / scope-discovery), not absorbed.
- Never start implementation directly on `main`/`master`; work on the dispatched
  feature branch (`branch-lifecycle`).

## §"Checkpoints and STOP points"

Map review checkpoints onto the framework's existing STOP machinery rather than
inventing ad-hoc pauses:

- **Pre-commit cross-model (Gate 2.2).** Before committing the diff, run the
  cross-model adversarial pass on the real diff in your worktree
  (`agent:cross-model-review`); fold findings to CLEAN or surface a capped-iteration
  STOP.
- **Functional verification.** Before any "done/passing" claim, confirm it with
  fresh evidence (`verification-completion`).
- **Rhythm STOP.** Under rhythm A the close-out is a STOP point — write it (it
  reports the branch + immutable SHA), await the green-light, then push the branch
  per `branch-lifecycle`. Under B/D-semi-auto the sequence is continuous; under C
  it queues for the cycle batch. The merge to `main` is the lead's — not part of
  this worker sequence (`branch-lifecycle` §"Merge to main").
- **Degradation / structural-blocker STOP.** When the playbook's STOP-on-degraded
  entry test fires (the test that decides whether the STOP is warranted lives in
  the playbook, not here), or a precondition the brief assumed is missing, emit a
  WIP-handoff so a fresh session can resume (`agent:coordination-wip-handoff` executes
  the STOP procedure once the playbook's trigger has fired).

**Signals to route per the playbook's STOP / clarification protocol — do not
guess past them:** a missing dependency, a repeatedly-failing verification, an
unclear instruction, or a plan gap that blocks starting. Route via a routed
artefact per the protocol; do not fabricate the absent state.

## §"Complete via the branch + close-out flow"

After all steps are done and verified:

- Report `Branch: <name> @ <SHA>` (the immutable `rev-parse` SHA) in the close-out
  routed to the lead, and push the branch per the rhythm — per the canonical
  contract in `branch-lifecycle` §"Report the branch in the close-out": the
  close-out reports the SHA; the branch is review-ready once that SHA is on the
  remote (immediate under B/D-semi-auto, after the rhythm-gated push under A/C).
  Do not imply push-before-report — the reported SHA is captured at close-out, the
  push may follow under A/C.
- The gate roles review against that SHA once it is pushed; the lead owns the
  merge. Do not self-merge to `main`.

## What this skill does NOT do

- Does NOT create or re-plan the implementation (`implementation-planning`).
- Does NOT decide the authority rhythm or whether to merge (playbook + lead).
- Does NOT carry the worktree, branch, cross-model, or WIP-handoff mechanics
  (those skills own them) — it sequences them.
- Does NOT route blockers via chat to a human partner — blockers are routed
  artefacts to the dispatcher.
