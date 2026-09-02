---
name: coordination-wip-handoff
description: |
  Execute the WIP-handoff procedure. Worker side: when STOP-on-degraded
  fires, a structural blocker surfaces, or a cross-model review cap-hit
  occurs mid-dispatch, compose + audit +
  (rhythm-permitting) publish a WIP-handoff record so a fresh session
  can resume. Lead side: validate an incoming WIP-handoff against the
  8-section body shape, then publish the Acknowledgment record.
assumes:
  - |
    The Worker invokes this skill to run §"Worker emit procedure" — on
    Claude Code via the native Skill tool (see worker-agent.claude.md
    §"Allowed skills"), or on Codex CLI by reading this file via
    functions.exec_command and executing §"Worker emit procedure"
    using the Codex tool mapping in worker-agent.codex.md
    §"WIP-handoff under context-degraded STOP or structural blocker".
    Which host a role is bound to is set by the deployment; the body
    shape, authority boundary, held-A/C STOP, and rhythm-gating
    semantics are platform-agnostic and bind both paths identically.
    Both lanes call the same `coordination.*` MCP tools.
  - |
    The Lead invokes §"Lead receive procedure" — on Claude Code via
    the native Skill tool (see lead-agent.claude.md §"Allowed skills"),
    or on Codex CLI by reading this file via functions.exec_command and
    executing the lead-receive procedure using the Codex tool mapping
    in lead-agent.codex.md §"Allowed skills" + §"WIP-handoff
    reception". The 8-section body shape and acknowledgment-record
    contract bind both paths identically.
  - |
    The Reviewer role does NOT invoke this skill — WIP-handoffs are a
    worker-side procedure (the lead side is intake/acknowledgment, not
    emit).
  - |
    A role newly bound to a different host must re-verify its
    invocation path against these assumptions before relying on it.
rhythm-gating:
  - |
    This skill STOPS execution at the held-A/C boundary. The publish
    step (`coordination.publish_artefact` + the `coordination.deliver`
    wake) only runs when the calling playbook's §"Authority-rhythm
    interaction" authorizes it (option B by default; option A or option
    C only with explicit rhythm-independent WIP-handoff authorization in
    the dispatch).
  - |
    This skill does NOT decide which rhythm applies. The caller decides;
    the skill executes within the decided rhythm.
---

# coordination-wip-handoff

Execution procedure for WIP-handoffs: worker emit side and lead receive side. The two halves share the 8-section body shape as a single source of truth.

## What this skill does

Carries the *procedure* for WIP-handoffs — composing the 8-section body, capturing the worker's working-tree state, publishing the record with `coordination.publish_artefact`, waking the lead with `coordination.deliver`, and the lead-side reception + acknowledgment record. Carries the canonical 8-section body shape against which incoming handoffs are validated.

This skill does NOT carry trigger decisions, authority rhythms, CRITICAL hard-block semantics, scope-discovery routing, or any decision about whether a STOP is warranted. Those live in the calling playbook (`worker-agent.md` and `lead-agent.md` and their overlays).

## Authority boundary (read first)

This skill is procedural. It executes; it does NOT decide.

Concretely:

- **The held-A/C STOP boundary is a positive obligation in this skill.** When the calling rhythm is option A awaiting green-light, or option C queued for cycle batch, both absent explicit rhythm-independent publication authorization in the dispatch, the §"Worker emit procedure" STOPS at the canonical "HELD A/C BOUNDARY" marker and returns control to the caller. The publish step (`coordination.publish_artefact` + the `coordination.deliver` wake) runs only when the calling playbook's §"Authority-rhythm interaction" authorizes it.
- **The publish decision is the caller's, not the skill's.** Under option B (or A/C with explicit rhythm-independent authorization in the dispatch), the caller authorizes the full sequence and the skill runs end-to-end. Under held A/C, the caller resumes the skill at the publish step when the green-light or cycle batch arrives.
- **The skill does NOT carry CRITICAL-finding override authority.** Reviewer-issued CRITICAL findings are operator-only override and stay in the playbook. If a CRITICAL finding interacts with a WIP-handoff in flight, the playbook's authority section governs; the skill does not silently absorb the override.
- **The skill does NOT carry the trigger entry test.** "Entry test — when to exercise the STOP-on-degraded clause" lives in `worker-agent.md`; the entry test is the playbook's call, not the skill's.

## Body shape — 8 mandatory sections (canonical, single source of truth)

A WIP-handoff is degraded and gets bounced by the lead if any of the eight sections is missing or carries a placeholder. Each section is load-bearing for downstream validation; the body shape is identical across worker-emit and lead-validate sides.

1. **Status table.** Files touched (uncommitted draft state), line counts, what compiles vs what doesn't, test status, harness state at STOP (quality grade, tool-call count, loop-detection signals if any), working-tree state capture status.
2. **File inventory (uncommitted, draft state).** What's on disk that the fresh session will inherit; what's committed in THIS session (typically: nothing — the handoff is a coordination record, not a commit).
3. **Unresolved imports / blockers (verbatim).** Compiler errors, unresolved test fixtures, missing dependency contracts — raw output. Helps fresh session triage immediately.
4. **Working-tree state capture.** `git status --short` of the product worktree captured at STOP (verbatim): what draft files are uncommitted, distinguishing yours from any sibling-worker uncommitted state visible in the tree (so the fresh session knows what is NOT yours). Section #4 is a *state record* of the working tree — `coordination.publish_artefact` writes the record daemon-side, so a WIP-handoff cannot bundle product code by construction. **The record MUST carry the captured `git status` output in section #4 — not a placeholder.** A section #4 that says "capture will run later" or an unedited placeholder is degraded; bounce back.
5. **Why STOP was the right call.** Honest framing: was it harness-degradation, structural blocker, cross-model review cap-hit, or a combination? Cite the specific authorization source — for the harness-degradation path, the dispatch's STOP-on-degraded clause; for the structural-blocker path, the missing precondition (brief assumed X / contract Y / dependency Z; name what's actually absent); for the cap-hit path, the profile cap reached without convergence. For a combination, cite each.
6. **Fresh-session resume instructions.** Numbered sequence the next session executes: what to read first (this handoff + original task brief + new artifacts the dependency-resolver produced); what to verify (typecheck, test pass, contract symbols on disk); what commit clusters to use; explicit `git status --short` / `git diff` checkpoints on the product worktree; branch-publication (`git.push_branch`) + merge-close-out sequence.
7. **Self-attribution check.** What files this session DID and DID NOT touch; confirms the working-tree state the fresh session will inherit.
8. **STOP.**

**Record kind:** `wip_handoff` — published via `coordination.publish_artefact {kind:"wip_handoff", to:<lead>, body:<the 8 sections>}` (see §"Worker emit procedure" step 3). The daemon mints the id; there is no filename. The record's `kind` is what distinguishes it at a glance from a regular `closeout` and a `merge_closeout`.

**In-session until published.** The worker composes the body in-session and `coordination.publish_artefact` performs the durable write (temp + fsync + no-clobber `link` CAS + dir-fsync) daemon-side. The body is either **held in-session** (held A/C, not yet published) or **published** — there is no on-disk intermediate for the lead to read early, and the presence registry / record store are daemon-private, never in the worker's tree.

## Worker emit procedure

Invoked by `worker-agent` (Claude overlay via the native Skill tool, or Codex overlay via `functions.exec_command` reading this file plus the documented Codex tool mapping — see worker-agent.codex.md §"WIP-handoff under context-degraded STOP or structural blocker") when any of these WIP-handoff triggers fires:

- **Harness-degradation path:** the dispatch's STOP-on-degraded clause is active AND the entry test in `worker-agent.md` §"Entry test — when to exercise the STOP-on-degraded clause" passes (that section is authoritative for the firing bar — gated on the objective context-quality grade reaching WARNING-or-worse, with subjective proxies corroborating only; this skill does not re-derive it).
- **Structural-blocker path:** a precondition the brief assumed satisfied turns out to be missing; continued execution would require fabricating absent precondition state. Self-authorizing — the missing precondition IS the authorization, named in body section #5.
- **Cross-model review cap-hit path:** the pre-commit cross-model review loop hit its profile cap (lightweight 3 / standard 8 / high-risk 12) without converging to CLEAN. Self-authorizing — the cap is a structural STOP; surface it for lead disposition (continue-with-revised-profile / re-scope / hand to human reviewer) in body section #5.

**Distinct path — competence / domain-fit decline (NOT a WIP-handoff cause).** A seat declining a unit it is not ramped for (wrong domain for the surface's blast-radius — see `worker-agent.md` §"Competence / domain-fit decline — a reroute, not a degradation STOP") is a **reroute to a domain-ramped seat**, decided at **intake** (before work starts) and routed to the lead as a recommendation (the missing-field-bounce transport, `agent:routed-comms`) — **not** one of this skill's WIP-handoff causes. It is content-based and valid at any context grade, including a healthy one; do not conflate it with the harness-degradation path or force it into the WIP-handoff body shape.

The trigger decisions stay in `worker-agent.md`; this skill executes only once the trigger has fired.

### Run end-to-end under option B, OR option A/C with explicit rhythm-independent WIP-handoff authorization in the dispatch

Under held option A (no rhythm-independent authorization) or queued option C (no publish-authorization), run steps 0–2 only, then STOP at the HELD A/C BOUNDARY marker, emit the held body's TL;DR to chat (the operator surface — held A/C sends NO `coordination.deliver` wake to the lead), and resume at step 3 when green-light arrives (option A) or the cycle batch fires (option C).

- **(0) Compose the 8-section body in-session.** Write all 8 sections as the record body; section #4 starts as a placeholder until step 2 fills it.
- **(1) Re-read the composed body** for sync-paste / stale-reference artefacts before it goes anywhere.
- **(2) Capture working-tree state into section #4.** Run `git status --short` in the product worktree and paste the verbatim output into section #4 — what draft files are uncommitted (yours vs a sibling worker's) so the fresh session knows exactly what it inherits:

  ```bash
  # In the product worktree that holds the draft code:
  git -C "$AGENT_WORKTREE_PATH" status --short   # capture verbatim into section #4
  ```

  The handoff is a coordination record the daemon writes, not a commit — nothing is added, committed, or pushed here.

```text
# ============================================================================
# HELD A/C BOUNDARY — under held option A or queued option C without explicit
# publish-authorization, STOP HERE. The 8-section body is complete and held
# in-session (nothing published yet, no wake sent). Chat-message the lead with
# the TL;DR so it knows a mid-stream STOP exists. Resume at step (3) when the
# green-light (option A) or cycle batch (option C) fires. Under option B (or
# A/C with rhythm-independent authorization), continue.
#
# This STOP boundary is a skill obligation, not the skill's decision. The
# rhythm is the caller's. See worker-agent.md §"Authority-rhythm interaction".
# ============================================================================
```

- **(3) Publish the record.** `coordination.publish_artefact {kind:"wip_handoff", to:<lead-slug>, body:<the 8 sections>}` → `{id, kind, created_at}`. The daemon does the durable write and mints the id; a returned id survives a crash. Body ≤ 256 KiB, else `BODY_TOO_LARGE`.
- **(4) Wake the lead.** `coordination.deliver {to:<lead-slug>, body:"<id> — WIP-handoff, STOP <cause>", class:"asap"}`. The published record alone wakes no one; the `deliver` is the doorbell. Resolve the lead first (`coordination.resolve_recipient {to}`); a non-live lead is refused (`UNKNOWN_RECIPIENT`) rather than silently dead-lettered.

If `git status --short` shows product-code state you did not expect (a sibling worker's untracked files, sync-tool artefacts), note it in section #4 so the fresh session can tell it apart — do NOT paste product code into the record body. The record carries only the 8-section handoff; the draft code stays on disk in the worktree, inherited by the fresh session as-is. After publishing you `coordination.deliver` the id to the lead — the wake that brings it to the artefact; per `lead-agent.md` §"Channel notification timing", a missed doorbell still resolves on the lead's next `coordination.list_artefacts`, so it converges to "lead has the artefact."

### Chat-emit TL;DR (rhythm-conditional, matches the publish state)

The TL;DR's location-line and Record field reflect the WIP-handoff's actual state at TL;DR-emission time, so timing differs by rhythm.

- **Held rhythms (option A awaiting green-light, option C queued — both absent rhythm-independent authorization):** emit TL;DR via chat **as soon as step 2 completes and the 8-section body is held in-session**, BEFORE step 3 runs. The body is held (not published) and no wake has been sent, so no doorbell fires until publish. Chat TL;DR is the lead's only signal that a mid-stream STOP exists.
- **Option B, or A/C with explicit rhythm-independent publication authority:** emit TL;DR **AFTER step 4 completes** (publish + deliver). The TL;DR's required fields can't be populated truthfully before step 3 — the Record field needs the daemon-minted id (post-publish). The `deliver` wake is sent as step 4, so chat TL;DR + deliver wake converge.

Format:

```
WIP-handoff <location-line — rhythm-conditional, see below>
Record: <rhythm-conditional — see below>
TL;DR (3-4 lines):
- STOP cause: <context-grade degradation | structural blocker | cross-model review cap-hit | combination>
- Work state: <0 deliverables | N files draft-saved on disk, 0 committed | etc>
- Fresh session resume: read this handoff + original task brief + ...
STOP. No merge-close-out for this dispatch yet; it is written when the lead's landing for the completed work reaches `landed`.
```

**Rhythm-conditional `<location-line>`** (under held rhythms the body is held in-session, NOT published, and no wake has been sent; chat-emitted TL;DR is the lead's only signal):

- **Option A** without rhythm-independent authorization: `held in-session — publish to a wip_handoff record pending green-light`
- **Option B**, or any rhythm with explicit rhythm-independent WIP-handoff authorization: `published: wip_handoff record <id> (deliver wake sent)`
- **Option C** without rhythm-independent authorization: `held in-session — publish to a wip_handoff record queued for cycle batch`

**Rhythm-conditional `Record:` field:**

- **Option A** without rhythm-independent authorization: `none — awaiting green-light before publish`
- **Option B**, or any rhythm with explicit rhythm-independent WIP-handoff authorization: `<id of the published wip_handoff record>`
- **Option C** without rhythm-independent authorization: `none — queued for cycle batch`

### What stays out of the published record

- Own draft code (stays uncommitted on disk for the fresh session to inherit).
- Sibling-worker uncommitted state.
- Session-local / daemon-owned state (the presence registry and coordination records live daemon-side and are never in your tree; `.mcp.json`, IDE scratch).

Only the 8-section body goes in the record — `coordination.publish_artefact` writes it daemon-side. Pre-commit discipline (per `worker-agent.md` §"Pre-commit shared-index audit") still governs your *product-code* commits; under shared-checkout conditions a sibling worker's uncommitted state may be present in the working tree — section #2's `git status` capture surfaces anything that drifted into your tree so the fresh session can tell it apart.

## Lead receive procedure

Invoked by `lead-agent` (via its host overlay) when a WIP-handoff intake fires. Two intake paths depending on the worker's authority rhythm:

- **Published-path intake (option B, or option A/C with rhythm-independent publication authorization).** The worker's `coordination.publish_artefact` lands the `wip_handoff` record in the store, then the worker `coordination.deliver`s you its id; that deliver wake (injected at your next message boundary or when you go idle, per class) is the intake signal. Read the record with `coordination.read_artefact {id}`.
- **Held/queued chat-intake (option A awaiting green-light, option C queued for cycle batch — both absent rhythm-independent authorization).** The worker holds the composed body in-session, not yet published, and sends **no** `coordination.deliver` wake during the await period. The worker emits a TL;DR to chat naming the STOP (surfaced on the operator surface, since held A/C fires no wake); when that TL;DR reaches you via the operator, treat it as the intake signal. The TL;DR is a 3–4-line summary, **not** the 8-section body — the body is held in-session and is not a record yet, so full-body validation (step 2) waits until the worker publishes on your green-light (option A) or at cycle batch (option C).

Do NOT wait for a `coordination.deliver` wake on a held/queued handoff — none arrives until the worker publishes.

### Reception steps (apply to both intake paths; use the path the intake signal cited)

1. **Read the WIP-handoff.** On the published-path intake, `coordination.read_artefact {id}` from the delivered id and verify content freshness (recent `created_at`, coherent body) rather than a stale paste. On held/queued intake, read the worker's chat TL;DR for situational awareness only — the full 8-section body is held in-session and is not yet a record, so you validate it (step 2) against the published record once the worker publishes it on your acknowledgment. A sync-paste failure can produce an empty/placeholder body; verifying body shape before processing avoids the silent-empty-body failure mode.

2. **Validate body shape against the 8-section minimum** (see §"Body shape" above). A handoff missing ANY of the eight sections is degraded — bounce back to the worker with an acknowledgment record that enumerates the missing sections (what went wrong). Section #4 carrying a placeholder ("capture will run later" or unedited template text) also triggers the bounce.

3. **Respond with an Acknowledgment record, not a chat-only reply.** Publish a short `acknowledgment` record — `coordination.publish_artefact {kind:"acknowledgment", to:<worker-slug>, body:…}` — and `coordination.deliver` its id to the worker, that:
   - (a) confirms STOP was correct on its grounds;
   - (b) names structural or environmental cause that triggered it;
   - (c) instructs on next action (await dependency, dispatch fresh session, re-scope);
   - (d) under held/queued chat-intake, the acknowledgment's publication-authorization semantics diverge by rhythm:
     - **Option A:** the acknowledgment carries explicit green-light authorizing the worker to publish the `wip_handoff` record immediately. The worker's `coordination.deliver` wake fires after it publishes.
     - **Option C:** the acknowledgment confirms receipt and queue placement only — does NOT authorize immediate publication. The body stays held in-session until the cycle-batch authorization fires at cycle close.

   The record IS the coordination artefact; chat-only acknowledgment leaves no audit trail and is anti-pattern.

4. **Lead either:** (a) surfaces a fresh-session option to the operator under the operator-authority override pattern when the remaining scope is bounded-mechanical (the spawn decision is the operator's; lead provides the candidate session brief and the rationale); (b) waits for dependency resolution if a structural blocker is the cause; (c) re-scopes the dispatch if the structural error is in the dispatch design; (d) on a cross-model review cap-hit, dispositions per `lead-agent.md` — continue under a revised profile, re-scope, or hand to a human reviewer.

5. **The merge-close-out for the original dispatch is written when the lead's landing for the completed work reaches `landed`** — NOT when the WIP-handoff lands, and not by any session (the daemon authors it, `agent:coordination-closeout-templates` §"Mandatory merge close-out"). The cycle is not closed until the merged code ships. Track in the lead's status block: cycle is mid-stream, not closed.

### Distinct from related artefacts

- **Regular close-out** (`closeout` kind): work complete, lead reviews. WIP-handoff is the opposite — work paused.
- **Merge close-out** (`merge_closeout` kind): the daemon's record that a requested landing reached `landed`. No session writes one, and a WIP-handoff does not produce one.
- **Pre-merge gate STOP** (regular discipline): the worker stops at a gate the lead specified, publishes a normal close-out with open questions, awaits green-light. WIP-handoff is for harness-degradation / structural-blocker / cross-model-review-cap-hit STOP, not for designed gate stops.

## What this skill does NOT do

A closing reminder for both procedure halves:

- Does NOT decide whether a STOP is warranted (worker playbook entry test).
- Does NOT decide the authority rhythm (worker playbook §"Authority-rhythm interaction").
- Does NOT decide whether to publish under held A/C (caller decides; skill resumes at the publish step only when caller authorizes).
- Does NOT carry CRITICAL-finding override authority (reviewer playbook + operator-only escalation).
- Does NOT carry scope-discovery routing (lead playbook §"Scope-discovery feedback to PM").
- Does NOT replace the lead's read of the handoff against the dispatch's specific authority context.

The skill is procedural infrastructure. The decisions are the playbooks'.
