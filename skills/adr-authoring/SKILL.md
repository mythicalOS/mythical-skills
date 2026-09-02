---
name: adr-authoring
description: |
  How to record a crystallized architecture decision as a durable
  Architecture Decision Record at `<repo>/docs/adr/NNNN-<slug>.md` — the
  three-gate qualification test (hard to reverse / surprising without
  context / real trade-off), sequential number allocation, the record
  template (Status / Tier / Context / Decision / Consequences /
  Considered alternatives), evidence citation back to the verdict or
  directive that carries the decision, and supersession mechanics
  (append-only corpus; a reversal is a NEW ADR that flips the old one's
  Status). Procedural only: WHETHER a decision warrants an ADR, WHEN the
  emission mandate fires, and WHO owns which tier (technical = the
  architecture-review role per architect-agent.md §"Decision records
  (ADRs)"; strategic = the apex role per cto-agent.md §"Strategic
  decision records (ADRs)") live in the invoking playbooks; this skill
  is the HOW of writing the record. It records decisions already made —
  it never makes, re-makes, or re-litigates one.
assumes:
  - |
    The decision being recorded has ALREADY been taken by its rightful
    authority — an architecture-review verdict, an operator-resolved strategic
    question, or a standing organisation-level technology mandate. The
    ADR is the durable record of that act, not the act itself. If no
    decision has crystallized, there is nothing to record and this skill
    does not apply.
  - |
    Two tiers share one corpus and one number sequence. Technical-tier
    ADRs are emitted by the architecture-review role alongside its
    verdict artefact; strategic-tier ADRs are emitted by the apex role
    when a strategic-technology question is resolved (operator decision
    relayed) or a standing organisation-level mandate is taken. The tier
    is a field on the record, not a separate directory.
  - |
    Claude Code roles author via the native edit tools and scan the
    number sequence via `Glob`/`Bash` `ls`; Codex roles via
    `functions.apply_patch` and `functions.exec_command`. Template,
    numbering, and supersession mechanics are platform-agnostic.
---

# adr-authoring

The procedure for writing an Architecture Decision Record once the invoking
playbook's mandate has fired. An ADR answers one question for a future reader:
*what was decided here, by whom, on what evidence, and why — so nobody re-derives
or accidentally "fixes" it.* It is deliberately small: the evaluation lives in
the artefact that made the decision (the review verdict, the directive, the
handoff); the ADR cites that evidence and records the commitment.

## Authority boundary (read first)

- **WHETHER and WHEN to emit is the invoking playbook's mandate, not this
  skill's reflex.** The architecture-review playbook mandates a technical-tier
  ADR when a verdict crystallizes a qualifying decision; the apex playbook
  mandates a strategic-tier ADR when a strategic resolution or standing mandate
  lands. This skill carries the qualification *test* and the writing *craft*.
- **The decision itself is upstream and closed.** The ADR records; it does not
  re-open. If writing the record surfaces doubt about the decision, that doubt
  routes upward through the invoking role's escalation channel — the record is
  not the venue for re-litigation.
- **The record's authority is its evidence link.** An ADR that cites no
  deciding artefact (verdict record id + SHA, directive/handoff record id, or an
  explicit operator/chat decision reference) is an opinion, not a record — do not emit it.

## §"Qualify the decision" — the three-gate test

This test is the qualification *instrument* the invoking playbooks bind their
emission mandates to — the decision to emit (or not) is theirs, made by applying
it. Their mandates fire only when all three hold:

1. **Hard to reverse** — undoing it later has a real cost (schema, public API,
   vendor lock-in, protocol, deployment topology, boundary commitments).
2. **Surprising without context** — a future reader would look at the result
   and wonder "why on earth is it this way?"
3. **A real trade-off** — genuine alternatives existed and one was chosen for
   specific reasons.

If reversal is cheap, you'll just reverse it. If nothing surprises, nobody will
wonder. If there was no alternative, "we did the obvious thing" needs no record.

**What typically qualifies:**

- **Architectural shape** — repo topology, event-sourced vs CRUD, sync vs async
  spine, process/daemon split.
- **Integration patterns between components** — events vs synchronous calls,
  queue vs direct write, who wakes whom.
- **Technology choices carrying lock-in** — database, message bus, auth
  provider, runtime, deployment target. Not every library; the ones that take a
  quarter to swap out.
- **Boundary and ownership decisions** — which component owns which data,
  reference-by-ID rules. The explicit no-s are as valuable as the yes-s.
- **Deliberate deviations from the obvious path** — anything a reasonable
  reader would assume the opposite of. These stop the next contributor from
  "fixing" what was deliberate.
- **Constraints invisible in the code** — compliance bans, contractual latency
  bounds, sovereignty requirements.
- **Non-obvious rejections** — an alternative that was seriously evaluated and
  rejected for subtle reasons will be proposed again unless the rejection is
  recorded.

**What does not qualify** (per the owning playbooks' boundaries): routine
library picks, reversible internals, decisions fully explained by their own
code, product scope/priority calls (the planning role's plan and PRD own
those), and visual/design-system decisions (the design-system artefact owns
those, with its own supersession discipline).

## §"Allocate the number"

ADRs live flat in `<repo>/docs/adr/` of the repo the decision governs, named
`NNNN-<slug>.md` (four digits, zero-padded, kebab-case slug). Create the
directory lazily with the first record.

- Scan for the highest existing `NNNN` and increment by one. Claude: `Glob`
  `docs/adr/*.md` or `Bash` `ls docs/adr/`; Codex: `functions.exec_command`
  `ls docs/adr/`.
- **Concurrency guard:** sessions run in parallel and both tiers share one
  sequence — re-scan immediately before commit; on collision, renumber your
  file to the next free number in the same commit.
- **Numbers are provisional until landed on the shared mainline.** A local
  commit does not reserve a number: under held-publication rhythms another session can
  land the same `NNNN` first. Whoever lands the commit re-checks `docs/adr/`
  uniqueness against the landing branch at landing time; on collision the
  emitting role renumbers the record AND its back-references (e.g. the verdict
  or relay artefact that names the ADR path) before it lands. Numbers are
  identity, so a collision must never land.
- Numbers are never reused, including for superseded or deprecated records.

## §"Write the record" — template

Section names are deterministic; do not rename per project. Keep the whole
record short — the value is *that* the decision and its why are recorded, not
section word-count. `Consequences` and `Considered alternatives` are included
only when they carry non-obvious content.

```markdown
# ADR-NNNN — <short active-voice title of the decision>

**Status:** proposed | accepted | deprecated | superseded by ADR-NNNN
**Tier:** technical | strategic
**Owner role:** <emitting role + session id>
**Decided by:** <the deciding authority — verdict, the operator, standing mandate>
**Date:** YYYY-MM-DD
**Evidence:** <deciding artefact — a verdict/directive record id, or a durable-doc
path; + commit SHA when the decision references landed code (omit the SHA when the
code has not landed at write time)>

## Context
<1–3 sentences: the forces and constraints that made this a real decision.>

## Decision
<1–3 sentences: what is now committed, stated actively — "X uses Y", "A owns
B", "C is deferred behind D".>

## Consequences
<only if non-obvious: downstream effects, follow-on work unlocked or forced,
what becomes harder.>

## Considered alternatives
<only if worth remembering: each rejected option in one line with the
load-bearing rejection reason, citing where it was evaluated.>
```

`Status` semantics: `proposed` is rare — used only when the record precedes
formal acceptance of the deciding artefact; `accepted` is the normal emission
state; `deprecated` marks a decision no longer operative with no replacement;
`superseded by ADR-NNNN` points at the replacement.

## §"Cite the evidence, don't restate it"

The deciding artefact (an architecture-review verdict with its
Selected/Rejected/Excluded stack analysis and Alternatives-considered dimension,
a routed directive, a plan's locked-decision entry) already carries the full
evaluation. The ADR links to it; it never duplicates the analysis. A
same-commit companion cites the deciding artefact by bare path — its commit SHA
does not exist at write time; cite a SHA only for evidence that already landed. One line of
rejection reason per alternative is the ceiling — a reader who wants the
reasoning follows the evidence link. This keeps records cheap to write, cheap
to load, and impossible to drift from their source.

## §"Supersede, never rewrite"

The corpus is append-only:

- **A reversal or revision is a NEW ADR** with the next number, whose
  `Context` names what changed since the original.
- The superseded record gets exactly one edit: `Status` flips to
  `superseded by ADR-NNNN`. Its `Context`/`Decision` body stays untouched — it
  is a time-stamped historical fact.
- Typo-level fixes are fine; content rewrites are not. If the recorded decision
  text is materially wrong, the correction is itself a supersession (the error
  and its fix are both history).
- Link both directions: the new record's `Context` cites the old number.

## §"Deliver like any routed artefact"

The ADR file itself stays a durable `docs/adr/` doc — **committed** by explicit
path, and held or reported per the session's authority rhythm. Getting that commit
onto the remote is **not** this skill's step and may not be yours: only the worker
and lead roles hold the daemon's branch-publication tool, and the roles that own
the two ADR tiers (architecture-review, apex) do not. Commit, report the branch and
the immutable SHA, and let the lead publish the branch. It is **not**
a coordination record — an ADR is a durable doc, not a routed artefact. Only its *delivery pointer*
rides the coordination path: it is named in the same `coordination.deliver`
notification as the artefact that carried the decision (a technical-tier ADR is
committed when its verdict record is published; a strategic-tier ADR accompanies
the decision relay). Consumers discover ADRs by reading `docs/adr/` during
reconnaissance — reviews already read the corpus for prior rejections; planning
roles respect it when scoping touched areas.

## What this skill does NOT do

- Does NOT decide whether a decision warrants an ADR or when to emit (the
  invoking playbook's mandate + the three-gate test applied by that role).
- Does NOT make, re-make, or re-litigate the decision — upstream authority owns
  it; the record cites it.
- Does NOT record product scope/priority (plan + PRD territory) or
  visual/design-system decisions (design-system artefact territory).
- Does NOT restate the deciding artefact's analysis — it cites the evidence.
- Does NOT rewrite history — supersession is the only revision mechanism.
