---
name: lead-cycle-retro-template
description: |
  Cycle-retrospective artefact template. Lead invokes after a multi-gate
  cycle (Gate 1+2+3) OR any cycle that surfaced rework / re-dispatch /
  floor-reconciliation / risk-triage events. Carries the 6-section
  template shape + the anti-pattern guard against manufactured content.
  The skill is TEMPLATE-ONLY — it shapes the retrospective prose the
  lead writes; it does NOT decide when the retro fires, does NOT carry
  promotion-threshold semantics with the distillation methodology, and
  does NOT decide the disposition of any candidate playbook change. All
  decision authority stays in lead-agent.md.
assumes:
  - |
    The Lead role has two invocation paths: from Claude Code via the
    native Skill tool (see lead-agent.claude.md §"Allowed skills"),
    or from Codex CLI by reading this file via functions.exec_command
    and executing the template population using the Codex tool
    mapping in lead-agent.codex.md §"Allowed skills" +
    §"Cycle retrospective (Codex-side)". The 6-section template, the
    authority boundary, and the manufactured-content anti-pattern
    guard are platform-agnostic and bind both paths identically.
  - |
    Worker, PM, Architect, QA, Reviewer roles do NOT invoke this skill.
    Cycle retrospectives are a lead-emitted artefact.
  - |
    The composition rule with the maintainers' distillation
    methodology (its parked-pattern register and its
    ≥2-empirical-instances promotion threshold) lives in
    lead-agent.md §"Cycle retrospective", NOT in this skill. The skill
    carries the template slot (§"Candidate playbook change"); the
    methodology consumes it.
authority-boundary:
  - |
    This skill is TEMPLATE-ONLY. It shapes the artefact format the
    lead writes; it does NOT decide when to write a retro (that's the
    lead's call against the trigger in lead-agent.md §"Cycle
    retrospective"), does NOT decide which patterns merit promotion
    (that's the distillation methodology's call), and does NOT decide
    the disposition of any candidate playbook change.
  - |
    The anti-pattern guard against manufactured content
    ("don't pad retros for friction-free cycles") IS in this skill —
    it is intrinsic to the template's faithful use. Padding the
    template corrupts the distillation feedback loop the retro feeds.
---

# lead-cycle-retro-template

Template for the cycle-retrospective artefact the lead writes after a substantial coordination cycle closes. Hosts the 6-section template shape + the anti-pattern guard against manufactured content. All trigger and disposition authority stays in `lead-agent.md`.

## What this skill does

Carries the template the lead populates when writing `<repo>/docs/retros/YYYY-MM-DD-cycle-<slug>.md`. The template's structure is the load-bearing thing — it shapes the lead's attention toward the dimensions that feed the distillation methodology's parked-pattern register (rework signal, gate value, coordination friction, profile calibration delta, candidate playbook change).

## Scope and boundary

TEMPLATE-ONLY — stated once here, normatively in the frontmatter
`authority-boundary` block. The trigger ("when to write"), the
≥2-empirical-instances promotion threshold, and every disposition of a
candidate playbook change stay with `lead-agent.md` §"Cycle retrospective" and
the maintainers' distillation methodology. What this skill DOES carry: the
template below, and the manufactured-content guard — intrinsic to the
template's faithful use, so it lives here.

Invoke at the point where the playbook instructs you to write the artefact.

## Template — the 6-section cycle retrospective

Sections marked `<...>` are placeholders the lead populates; section headings stay verbatim.

```markdown
# Cycle retrospective — <subject>

**Cycle dates:** YYYY-MM-DD to YYYY-MM-DD
**Workflow profile:** <as recorded at cycle start>
**Outcome:** <what was delivered, or stopped, or split-and-deferred>

## Rework caused by unclear scope or handoff
<instances if any; cite the close-out / handoff record id that surfaced the rework>

## Review-role / gate value
<which reviews found material issues that the lead would have missed; which gates ran but produced no material finding — separate signal from ritual>

## Coordination friction
<avoidable roundtrips, blocked clarifications, duplicated artefacts, rhythm-disambiguation incidents, dispatch-brief errors caught at worker execution>

## Workflow profile calibration delta
<if the profile was changed mid-cycle, what triggered it; if the original profile turned out to be over- or under-spec, name the signal>

## Candidate playbook change
<only when a pattern has repeated in ≥2 cycles or the consequence was high; a candidate MUST be checked against the maintainers' parked-pattern register before being asserted as new — when the register is not available in this session, mark the candidate "unchecked against the parked-pattern register" instead of calling it new>
```

**Length target:** ≤1 page total. Brevity is part of the template's faithful use — the artefact's purpose is to anchor distillation signal, not to narrate the cycle.

## Anti-pattern — don't manufacture content

Clean cycles deserve a one-line "no rework, no friction observed; profile calibration held" retro, NOT invented findings.

Padding retros with manufactured findings corrupts the distillation feedback loop. The methodology consumes retros as empirical evidence; fabricated content pollutes the parked-pattern register and induces false-positive promotions.

The trigger sentence in `lead-agent.md` §"Cycle retrospective" is the gate: "after a multi-gate cycle OR any cycle that surfaced rework / re-dispatch / floor-reconciliation / risk-triage events." If none of those triggers fire, the cycle does not earn a retro at all — let alone a padded one. When in doubt, the one-line "no rework, no friction observed; profile calibration held" entry IS the faithful artefact.
