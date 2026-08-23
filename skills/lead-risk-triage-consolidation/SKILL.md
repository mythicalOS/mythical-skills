---
name: lead-risk-triage-consolidation
description: |
  Risk-triage artefact template + one-escalation-per-triage anti-pattern.
  Lead invokes when ≥2 review-role verdicts for the same phase carry
  escalation-grade signals simultaneously, BEFORE requesting a
  consolidated operator decision. The skill is TEMPLATE-ONLY — it shapes
  the artefact format that consolidates side-by-side verdicts +
  lead's joint reading + recommended consolidated routing; it does
  NOT decide when triage applies, does NOT carry CRITICAL hard-block
  override authority, does NOT delay hard-block acknowledgment to
  the operator, and does NOT decide which consolidated routing the lead
  recommends. All decision authority stays in lead-agent.md.
assumes:
  - |
    The Lead role has two invocation paths: from Claude Code via the
    native Skill tool (see lead-agent.claude.md §"Allowed skills"),
    or from Codex CLI by reading this file via functions.exec_command
    and executing the template population using the Codex tool
    mapping in lead-agent.codex.md §"Allowed skills" +
    §"Risk-triage gate (Codex-side)". The template (side-by-side
    matrix + joint reading + recommended-routing + decision-capture),
    the authority boundary, and the one-escalation-per-triage
    anti-pattern guard are platform-agnostic and bind both paths
    identically.
  - |
    Worker, PM, Architect, QA, Reviewer roles do NOT invoke this skill.
    Risk-triage consolidation is a lead-emitted artefact written before
    operator escalation.
  - |
    Hard-block authority (CRITICAL reviewer findings, architect
    `reject` / `re-scope`) stays in lead-agent.md and reviewer-agent.md.
    The risk-triage artefact does NOT delay acknowledgment of an
    already-effective hard block — the block is acknowledged to the operator
    immediately with the verdict record id; the triage artefact then
    consolidates HOW the consolidated decision is presented to the operator.
authority-boundary:
  - |
    This skill is TEMPLATE-ONLY. It shapes the artefact format the
    lead writes; it does NOT decide when triage applies (that's the
    lead's call against the trigger in lead-agent.md §"Risk-triage
    gate"), does NOT change hard-block override semantics, and does
    NOT decide which consolidated routing the lead recommends.
  - |
    The one-escalation-per-triage anti-pattern guard
    ("one operator escalation per triage artefact, not one per verdict")
    IS in this skill — it is intrinsic to the template's faithful
    use. Fragmenting escalations across the side-by-side verdicts
    defeats the consolidation purpose.
  - |
    This skill does NOT carry CRITICAL-finding override authority.
    CRITICAL reviewer findings, architect `reject` / `re-scope`, and
    operator-only override semantics live in the playbook. The template
    names the verdict slots they land in; it does NOT redefine
    override semantics.
---

# lead-risk-triage-consolidation

Template for the risk-triage artefact the lead writes when ≥2 review-role verdicts for the same phase simultaneously carry escalation-grade signals. Hosts the side-by-side matrix shape + joint-reading slot + recommended-routing options + decision-capture slot, plus the one-escalation-per-triage anti-pattern guard. All trigger and override authority stays in `lead-agent.md`.

**Throughout this skill, "the operator" denotes the apex decision-maker — the human apex.** Under rhythm D the apex is the **CTO** (operator-proxy, per `ROLES.md` §"Apex substitution under rhythm D"); read every "escalate to the operator" / "the operator decides" below as "to the apex." The concrete recipient and the routing are owned by `lead-agent.md` §"Risk-triage gate" — not this skill (under D the triage `to` addresses the idle CTO session, resolved with `coordination.resolve_recipient` and woken with `coordination.deliver`; under A/B/C the `to` is an `operator` discovery token that the operator reads via the chat surface, no live wake). `coordination.deliver` refuses an unknown/non-live recipient (`UNKNOWN_RECIPIENT`), so a mis-addressed triage fails at the call rather than dead-lettering.

## What this skill does

Carries the template the lead populates when publishing the risk-triage artefact as a `risk_triage` record (`coordination.publish_artefact {kind:"risk_triage", to:…, body:…}`; recipient + routing are rhythm-conditional per the note above, set by `lead-agent.md` §"Risk-triage gate", not here). The template's structure consolidates fragmented escalations: instead of N separate operator decisions on N role verdicts, the operator reads a single side-by-side view + the lead's joint reading + a recommended consolidated routing, and decides once.

## Scope and boundary

TEMPLATE-ONLY — stated once here, normatively in the frontmatter
`authority-boundary` block. The trigger ("when triage applies") with its
does-not-apply rule, hard-block override semantics, scope-discovery routing,
and the consolidated-routing choice itself all stay with `lead-agent.md`
§"Risk-triage gate" (+ `reviewer-agent.md` for CRITICAL override semantics).
Two operative points bind the template's faithful use and therefore live here:

- **Hard-block acknowledgment is never delayed.** A CRITICAL reviewer finding,
  architect `reject`, or architect `re-scope` blocks the gate the moment it
  lands and is acknowledged to the operator immediately with the verdict
  record id; the triage artefact then consolidates HOW the decision is
  presented — it never lets the lead sit on a CRITICAL finding while drafting
  prose.
- **The one-escalation-per-triage guard** (§"Anti-pattern" below) is intrinsic
  to the template.

Invoke at the point where the playbook instructs you to write the consolidated
artefact — AFTER acknowledging any already-effective hard block, BEFORE
requesting the consolidated decision.

## Template — risk-triage artefact

Sections marked `<...>` are placeholders the lead populates; section headings stay verbatim.

```markdown
# Risk triage — <phase / subject>

**Triggered by:** <N review verdicts simultaneously carrying escalation-grade signal>
**Phase:** <which phase the verdicts review>
**Date:** YYYY-MM-DD
**Triaging lead:** <session id>

## Verdicts side-by-side
| Role | Verdict | Severity | Load-bearing signal | Artefact (record id) |
| --- | --- | --- | --- | --- |
| architect | <verdict> | <if applicable> | <one line> | `<record id>` |
| qa | <scope status> | <if applicable> | <one line> | `<record id>` |
| reviewer | <verdict> | <count by severity> | <one line> | `<record id>` |

## Lead's joint reading
<2–4 paragraphs: do the verdicts compose to a single underlying concern, three distinct concerns, or somewhere between? Where do they reinforce each other? Where do they pull in different directions?>

## Recommended consolidated routing
<one of: operator-decide (with proposed options laid out), re-dispatch to specific role(s) with revised brief, accept-with-required-changes consolidated across roles, escalate to PM as scope discovery>

## Decision capture
<populated after the operator responds; mirrors the override-with-acknowledgment shape>
```

## Anti-pattern — one escalation per triage, not one per verdict

The consolidation purpose is to reduce operator-side reconciliation burden: the operator reads a single side-by-side view, decides once, and the lead executes against the consolidated decision. Fragmenting escalation across the verdicts (N separate "operator, decide on this" messages, one per role) defeats the purpose and reintroduces the contradictory-framings burden the triage was designed to eliminate.

Once the triage record is published, the lead emits ONE escalation carrying its record id — routed per the rhythm-conditional rule above: a live `coordination.deliver` to the idle CTO under rhythm D; under A/B/C, surfaced to the operator via the chat surface, who reads the published record (no live wake). Per-verdict escalations are an anti-pattern that compose with the playbook's `Does NOT apply when:` rule poorly — they signal the lead should have de-duped rather than triaged, OR that only one verdict actually carried escalation-grade signal and the triage was unwarranted.
