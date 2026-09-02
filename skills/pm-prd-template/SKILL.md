---
name: pm-prd-template
description: |
  Product Requirements Document markdown template. Invoked by the
  planning role at Phase 5 emission, immediately BEFORE the master plan
  is written: the PRD records the user-anchored WHAT and WHY — problem,
  users, user stories, numbered functional and non-functional
  requirements with acceptance criteria, success metrics, explicit
  out-of-scope — and the master plan then carries the phased HOW/WHEN
  and cites the PRD. Template-only: trigger, the PRD-before-plan
  ordering mandate, stable-structure rule, last-reviewed marker
  authority, revision rules on scope change, and path conventions stay
  in pm-agent.md §"Phase 5 — PRD + master plan emission" and §"Output
  contract — the PRD".
assumes:
  - |
    The planning role invokes this skill via whichever host the
    deployment binds it to — on Claude Code via the native Skill tool,
    or — where the deployment runs the planning role on Codex — via
    functions.exec_command reading this file. The section template, the
    authority boundary, and the ordering rule are platform-agnostic and
    bind both paths identically.
  - |
    Lead, Worker, Architect, QA, Reviewer, Explorer roles do NOT invoke
    this skill. PRD emission is a planning-role-only artefact; every
    other role reads the PRD as scope context.
  - |
    The PRD is synthesized from the Phase 0–4 scoping dialogue the
    planning role has already run — it is the writing-down step, not a
    second interview. The stable-structure rule (revisions update
    content in place; do NOT reorganize) and the last-reviewed marker
    rule live in pm-agent.md §"Output contract — the PRD", NOT in this
    skill.
authority-boundary:
  - |
    This skill is TEMPLATE-ONLY. It shapes the artefact prose the
    planning role writes; it does NOT decide when the PRD is emitted
    (Phase 5 trigger and the PRD-before-master-plan ordering live in
    pm-agent.md), does NOT decide revision permission on scope change
    (playbook authority), does NOT decide path conventions (default
    `<repo>/docs/prd/<project-slug>-prd.md` with user override
    permitted — playbook authority), and does NOT decide section content
    semantics (what counts as a requirement vs a want, which stories are
    in scope — planning-role judgment exercised against the Phase 0–4
    dialogue, not template guidance).
  - |
    The PRD records the product WHAT/WHY only. Technical architecture
    decisions stay with the architecture-review role (pm-agent.md
    core principle "Do not lock technical decisions that belong to the
    architect"); phasing, triggers, and delivery mechanics stay in the
    master plan; visual/design-system decisions stay in the
    design-system artefact. A PRD that locks any of those has leaked
    authority, whatever its section headings say.
---

# pm-prd-template

Template for the Product Requirements Document the planning role writes at
Phase 5 emission, immediately before the master plan. The PRD is the durable,
user-anchored record of WHAT is being built and WHY — the master plan is the
lead-facing record of HOW and WHEN. Keeping them separate lets requirements
survive re-phasing untouched, and lets downstream artefacts cite stable
requirement IDs (`FR-3`, `NFR-1`) instead of re-deriving intent from plan prose.

## What this skill does

Carries the template the planning role populates when writing
`<repo>/docs/prd/<project-slug>-prd.md` (default path; user override permitted
per `pm-agent.md` §"Output contract — the PRD"). The section structure is the
load-bearing thing — it fixes the reading order (problem → users → stories →
requirements → metrics → out-of-scope → dependencies → open questions →
decision links) so revisions diff cleanly under the stable-structure rule, and
so every functional requirement carries a citable ID with acceptance criteria.

## Scope and boundary

TEMPLATE-ONLY — stated once here, normatively in the frontmatter
`authority-boundary` block. Emission timing and the PRD-before-plan ordering,
revision rules on scope change, and the path convention stay with
`pm-agent.md` (§"Phase 5 — PRD + master plan emission", §"Output contract —
the PRD"). Four rules bind how the template is populated:

- **Requirement-vs-want is planning-role judgment** (`pm-agent.md` core
  principle "Distinguish wants from requirements"): a requirement means the
  project fails or causes harm without it; wants live in the master plan's
  parking lot, not in the requirements sections.
- **No technical lock-in.** Where a requirement brushes an architecture choice,
  state the requirement ("audit events must be queryable for 7 years"), never
  the mechanism ("store audit events in PostgreSQL") — mechanism is the
  architecture-review role's territory, recorded in `docs/adr/` when it
  crystallizes (see `agent:adr-authoring`).
- **Use the glossary's canonical vocabulary.** Where a domain glossary exists (`docs/glossary/`, `agent:domain-glossary`), the PRD uses its canonical terms throughout — an `_Avoid_:`-listed synonym in a PRD is a defect, not a style choice.
- **Respect the existing decision corpus** (playbook rule, restated —
  `pm-agent.md` §"Output contract — the PRD"): before writing, read `docs/adr/`
  for records touching the scoped area; a PRD that contradicts an accepted ADR
  surfaces the conflict to the deciding authority — it does not silently
  overrule the record.

## When to invoke

At the point in Phase 5 where the playbook instructs you to write the PRD,
after the user has confirmed readiness and the path — and before
`agent:pm-master-plan-template` is invoked for the plan. Clean Phase 0–4
conversations do NOT invoke this skill early; it is the writing-down step, not
the scoping step, and drafting the PRD mid-conversation before Phase 5 is the
same anti-pattern as drafting the plan early.

## Template — the PRD markdown

Sections marked `<...>` are placeholders the planning role populates; section
headings stay verbatim. Section ordering is load-bearing under the playbook's
stable-structure rule and must NOT be reorganized. User stories and
requirements are numbered once and never renumbered — retired items are struck
through with a one-line reason, so downstream citations stay valid.

```markdown
# <Project name> — PRD

> Status: draft | accepted | superseded
> Last reviewed: <YYYY-MM-DD>
> Master plan: <path once emitted — the plan cites this PRD back>

## Problem statement
<One paragraph, from the user's perspective. The locked output of Phase 1 —
verbatim or tightened, never re-negotiated here.>

## Users and stakeholders
- <actor>: <one line — who they are and what they need from this>

## User stories
<Numbered, extensive — cover every aspect of the scoped capability.>
1. As a <actor>, I want <capability>, so that <benefit>.
2. ...

## Functional requirements
<Numbered FR-n. Each requirement: the project fails or causes harm if it is
missing — everything else is a want and belongs in the master plan's parking
lot. State WHAT, never the mechanism.>

### FR-1 — <short name>
- **Requirement:** <one or two sentences>
- **Acceptance criteria:** <observable conditions under which this counts as
  satisfied — testable, not adjectives>
- **Stories served:** <story numbers>

### FR-2 — <short name>
<same structure>

## Non-functional requirements
<Numbered NFR-n: performance, security, data and compliance, operability,
accessibility — with the same acceptance-criteria discipline. Only those that
are real constraints for this project; no boilerplate checklists.>

### NFR-1 — <short name>
- **Requirement:** <one or two sentences>
- **Acceptance criteria:** <observable / measurable conditions>

## Success metrics
<How the shipped product is judged, as observable outcomes — usage, latency
experienced, error budget, task-completion — not delivery milestones (the
master plan's success criteria own those).>

## Out of scope
<Explicit negative requirements — what this product does NOT do, per
pm-agent.md "Negative requirements are first-class". The user will assume
anything unnamed is in scope.>

## Dependencies and assumptions
<External systems, teams, data sources, and the assumptions the requirements
stand on. If an assumption falls, which requirements fall with it.>

## Open questions
<Unresolved items that do not block acceptance, each with who resolves it.>

## Decision links
<Pointers, filled as they come to exist: architecture-review verdicts and
docs/adr/ records that honor or constrain these requirements. Links only —
the PRD never restates or re-litigates a decision.>
```

## Relationship to the master plan

(This section restates `pm-agent.md` §"Phase 5 — PRD + master plan emission" and
§"Output contract — the PRD" for template context; every rule here is the
playbook's, none is this skill's to decide or relax.)

- The PRD is emitted first; the master plan's Problem statement and
  Goals/Non-goals derive from it and its header links back here.
- Re-phasing, re-ordering, or re-scheduling work touches the master plan only.
  A scope change that adds, removes, or alters a *requirement* updates the PRD
  in place (stable structure, last-reviewed marker) — narrated in the same
  scope-change handoff that updates the plan.
- Phase success criteria in the plan cite requirement IDs; QA and review roles
  trace acceptance back to `FR-n`/`NFR-n` rather than plan prose.
