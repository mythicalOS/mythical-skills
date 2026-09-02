---
name: design-exploration
description: |
  How to turn a raw idea into a refined, approved design through Socratic
  dialogue — explore context, ask one clarifying question at a time, offer
  2-3 approaches with a recommendation, present the design in
  complexity-scaled sections for approval, self-review the written spec,
  then route it onward. The dialogue counterpart is the human stakeholder
  (the operator), reached per the invoking role's upward routing. Procedural only:
  WHETHER a piece of work needs design exploration, and WHO owns the scope
  it produces, are the invoking role's decision; this skill is the HOW of
  the refinement, and it ends by routing the design on — it does NOT flow
  into implementation by the same agent.
assumes:
  - |
    The Socratic counterpart is the human stakeholder (the operator), reached per
    the invoking role's routing — the planning role routes upward to the operator;
    under rhythm D the apex-proxy role communicates with the operator. The design
    that results routes ONWARD to the next role (master-plan emission or a
    dispatch), not into same-agent implementation.
  - |
    Claude Code roles converse in chat with an operator-direct stakeholder and
    write the design via the native edit tools; Codex roles via
    `functions.apply_patch`. The one-question-at-a-time, approaches-then-
    recommendation, and approve-each-section discipline is platform-agnostic.
---

# design-exploration

The procedure for refining an idea into a design the stakeholder has approved.
Understand the context, narrow the idea through focused questions, surface
alternatives, and present a design scaled to its complexity — then **route the
approved design onward** to the role that turns it into scope or a dispatch. This
skill is the dialogue; it deliberately stops short of implementation.

## Authority boundary (read first)

- **WHETHER to explore is the invoking role's decision, not this skill's
  reflex.** This skill carries the HOW of the refinement; the playbook decides
  when a piece of work warrants it.
- **The counterpart is the human stakeholder (the operator), reached per the role's
  routing** — the planning role routes upward; under rhythm D the apex-proxy
  communicates with the operator. Approval comes from that stakeholder, in chat for an
  operator-direct exchange.
- **The terminal state is a routed design, not code.** The refined, approved
  design routes onward — to master-plan emission (`agent:pm-master-plan-template`) or to
  a dispatch the lead shapes — and is then planned and built by the *downstream*
  roles (`implementation-planning`, `plan-execution`). This skill does not invoke
  an implementation skill, scaffold, or write production code; the framework
  distributes that arc across roles.

## §"Explore context first"

Before questions, understand the current state: read the relevant files, docs,
and recent history. Assess scope early — if the idea is really several
independent subsystems, say so and help decompose it into pieces (what they are,
how they relate, what order) before refining the first one. Each piece earns its
own design → scope → build cycle.

## §"Clarify one question at a time"

For an appropriately-scoped idea, ask questions one at a time to refine it:

- One question per message; if a topic needs more, break it into multiple
  questions.
- Prefer multiple-choice when it fits; open-ended is fine otherwise.
- Focus on purpose, constraints, and success criteria — not premature detail.

## §"Offer approaches with a recommendation"

Once you understand the problem, propose 2-3 approaches with their trade-offs.
Lead with your recommended option and the reasoning for it. Rank them; do not
present a flat menu.

## §"Present the design for approval"

Present the design in sections scaled to their complexity (a few sentences when
straightforward; more when nuanced). Confirm each section before moving on. Cover
architecture, components, data flow, error handling, and testing.

**Design for isolation + clarity:** break the system into units with one clear
purpose, well-defined interfaces, and independent testability. For each unit you
should be able to answer: what it does, how it is used, what it depends on. If you
cannot understand a unit without reading its internals, or cannot change its
internals without breaking consumers, the boundaries need work. In an existing
codebase, follow established patterns and include only targeted, in-scope
improvements — no unrelated refactoring.

Apply YAGNI ruthlessly; go back and re-clarify whenever something stops making
sense.

## §"Self-review then route onward"

After the stakeholder approves, write the design to the role's design/spec
location, then review it with fresh eyes:

1. **Placeholders** — any "TBD"/"TODO"/vague requirement? Fix inline.
2. **Internal consistency** — do sections contradict; does the architecture match
   the feature descriptions?
3. **Scope** — is this one buildable unit, or does it still need decomposition?
4. **Ambiguity** — could a requirement be read two ways? Pick one; make it
   explicit.

**The checklist is the floor, not necessarily the terminal gate.** It always
runs and needs nothing beyond reading. Whether the design then gets an
*independent* pass is the invoking playbook's call, not this skill's: when that
playbook's §"Cross-model validation of load-bearing output" classifies the
design as load-bearing, run the pass per `agent:cross-model-review` after the
checklist and fold findings in before routing — that skill resolves the
deployment's configured review binding itself (the `review mode:` bootstrap
line: the cross-model CLI, or the fresh-context ephemeral reviewer). A role
whose playbook has no such section keeps the self-review floor plus its own
review gates. This skill decides neither the depth nor the mechanism.

Then **route the design onward** to the next role per the invoking playbook —
master-plan emission, or a dispatch the lead shapes. Do not transition into
implementation yourself.

## What this skill does NOT do

- Does NOT decide whether work needs design exploration (invoking role's call).
- Does NOT own the scope the design becomes (PM scope; `agent:pm-master-plan-template`).
- Does NOT flow into implementation by the same agent — it routes the design on.
- Does NOT carry a visual/browser companion or any tool-specific ceremony.
