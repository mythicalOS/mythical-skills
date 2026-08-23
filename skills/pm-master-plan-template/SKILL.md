---
name: pm-master-plan-template
description: |
  Master plan markdown template. Invoked by PM at Phase 5 emission, after
  the user has signalled readiness and confirmed the path, immediately
  before writing the populated plan file. Template-only; trigger,
  stable-structure rule, last-reviewed marker authority, and path
  conventions stay in pm-agent.md §"Output contract — the master plan"
  and §"Phase 5 — PRD + master plan emission".
assumes:
  - |
    The PM role invokes this skill via whichever host the deployment
    binds it to — on Claude Code via the native Skill tool (see
    pm-agent.claude.md §"Allowed skills"), or — where the deployment
    runs PM on Codex — via functions.exec_command reading this file
    (see pm-agent.codex.md §"Allowed skills"). The 10-section template,
    the authority boundary, and the section ordering rule are
    platform-agnostic and bind both paths identically.
  - |
    Lead, Worker, Architect, QA, Reviewer, Explorer roles do NOT invoke
    this skill. Master plan emission is a PM-only artefact.
  - |
    The stable-structure rule (subsequent revisions update content in
    place; do NOT reorganize) and the last-reviewed marker rule
    (every revision updates `Last reviewed: <YYYY-MM-DD>` near the top)
    live in pm-agent.md §"Output contract — the master plan", NOT in
    this skill. The skill carries the section shape; the playbook
    carries the revision-permission authority that governs subsequent
    edits to the populated artefact.
authority-boundary:
  - |
    This skill is TEMPLATE-ONLY. It shapes the artefact prose the PM
    writes; it does NOT decide when the plan is emitted (Phase 5
    trigger lives in pm-agent.md §"Phase 5 — PRD + master plan emission"),
    does NOT decide stable-structure or revision rules (stays in
    pm-agent.md §"Output contract — the master plan"), does NOT decide
    path conventions (default `<repo>/docs/plans/<project-slug>-master-plan.md`
    with user override permitted — playbook authority), and does NOT
    decide section content semantics (e.g., what counts as a goal vs
    non-goal — that's PM judgment exercised against Phase 1–4 dialogue,
    not template guidance).
  - |
    The skill carries only the section shape: required sections, order,
    intra-section bullet conventions, and the placeholder convention
    (`<bullet list of what this project achieves>` etc.). The
    structural ordering of sections IS load-bearing — it shapes the
    reader's reading order (problem → goals → constraints → phases →
    risks → parking → open → locked → handoff → metadata) so revisions
    diff cleanly under the stable-structure rule.
---

# pm-master-plan-template

Template for the master plan markdown artefact the PM writes at Phase 5 emission. Hosts the 10-section template shape PM populates after the user signals readiness and confirms the path. All trigger, stable-structure, last-reviewed marker, and path-convention authority stays in `pm-agent.md`.

## What this skill does

Carries the template the PM populates when writing `<repo>/docs/plans/<project-slug>-master-plan.md` (default path; user override permitted per `pm-agent.md` §"Output contract — the master plan"). The template's section structure is the load-bearing thing — it shapes the reader's reading order so subsequent revisions under the stable-structure rule diff cleanly.

## Scope and boundary

TEMPLATE-ONLY — stated once here, normatively in the frontmatter
`authority-boundary` block. The Phase 5 emission trigger ("you signal you are
ready; user confirms; you do NOT emit before user signals"), the
stable-structure and revision-permission rules, the last-reviewed marker, and
the path convention (default
`<repo>/docs/plans/<project-slug>-master-plan.md`, user override permitted)
all stay with `pm-agent.md` (§"Phase 5 — PRD + master plan emission",
§"Output contract — the master plan"). Section content semantics — goal vs
non-goal, in-scope vs out-of-scope, locked vs open — are PM judgment exercised
against the Phase 1–4 dialogue, not template guidance.

Invoke at the point where the playbook instructs you to write the master plan
markdown, after the user has confirmed the path and signalled readiness. Clean
Phase 0–4 conversations do NOT invoke this skill — it is the writing-down
step, not the scoping step, and drafting the plan mid-conversation before
Phase 5 is the anti-pattern the playbook names.

## Template — the master plan markdown

Sections marked `<...>` are placeholders the PM populates; section headings stay verbatim. Section ordering is load-bearing under the playbook's stable-structure rule and must NOT be reorganized.

```markdown
# <Project name>

> PRD: `<repo>/docs/prd/<project-slug>-prd.md` — the requirement record this plan phases; emitted first, per `pm-agent.md` §"Output contract — the PRD"

## Problem statement
<One paragraph. The locked output of Phase 1, derived from the PRD's Problem statement.>

## Goals and non-goals
### Goals
- <bullet list of what this project achieves>
### Non-goals
- <bullet list of what this project explicitly does NOT do>

## Constraints
- Tech stack: <list>
- Team capacity: <description>
- Data and compliance: <list>
- Integration: <list>
- Cost / budget: <description>
- Timing: <real deadlines>
- Delivery mode (project default): <ci-cd | on-main | yolo> — how far "done" reaches and who goes live (`ROLES.md` §"Delivery modes"). For `on-main`, also name the human go-live operator who takes the work live from the go-live handbook: <the operator | the user | named ops human>

## Phases
### Phase 1 — <name>
- Deliverable: <what concrete thing this phase produces>
- Independent units: <the independently deliverable units inside this phase — no dependency between them, each buildable without the others' output; `single unit` when the phase is one indivisible deliverable; real orderings listed as `<unit> → <unit>`>
- Success criteria: <how we know it's done — cite the PRD requirement IDs this phase satisfies (`FR-n`/`NFR-n`), not restated requirement prose>
- Out of scope (this phase): <bullet list>
- Trigger for Phase 2: <condition, not date>

### Phase 2 — <name>
<same structure>

### Phase N — <name>
<same structure>

## Risks
- <risk>: <mitigation or status>

## Parking lot
- <item>: parked because <reason>; trigger: <condition>

## Open questions
- <question still unresolved>

## Locked decisions
- <decision>: <one-line rationale>

## Handoff to lead
<One short paragraph describing what the lead should pick up first.>

## Master plan metadata
- Drafted: <YYYY-MM-DD>
- Drafter: pm-agent v<version>
- Status: <draft | accepted | superseded>
```

**Placeholder convention.** The `<...>` markers indicate populated content; PM replaces them with the concrete output of the Phase 1–4 dialogue. Bullet placeholders (`- <bullet list of what this project achieves>`) become real bullet lists; paragraph placeholders (`<One paragraph. ...>`) become real paragraphs. Do not ship a plan with `<...>` markers still present.

**Trigger-not-date phase boundaries.** The `Trigger for Phase 2:` slot takes a condition (e.g., "explorer artefact accepted", "architect verdict on transport layer landed"), not a calendar date. Date-anchored phase boundaries are a Phase 3 anti-pattern the playbook calls out; the template structure invites the trigger framing.

**Independent-units field.** The `Independent units:` slot names the independently deliverable units inside the phase — deliverable-level statements of what can be built without another unit's output — so the lead can partition the phase into concurrent worker lanes at intake (`lead-agent.md` §"Wave planning at plan intake"). It declares independence, not execution: no worker counts, no assignments, no dispatch order, no file paths or branch names — worker dispatch and execution detail are lead territory (`pm-agent.md` must-route). `single unit` is a legitimate populated value; an unpopulated slot is not — a phase that was never examined for internal independence reads as serial by default and silently costs the team its parallelism. Which units are genuinely independent is PM judgment against the Phase 1–4 dialogue, not template guidance.

**Delivery-mode default.** The `Delivery mode (project default)` constraint records the project's delivery contract — one of `ci-cd | on-main | yolo` (`ROLES.md` §"Delivery modes") — that the PM owns with the operator at plan time; the lead selects/echoes the active mode per cycle but does not redefine the default (`pm-agent.md` §"Phase 5 — PRD + master plan emission"). When the default is (or may be) `on-main`, name the human go-live operator too — the lead routes the go-live handbook to that named counterpart. This is the field-shape only; what mode a given project defaults to is PM judgment against the Phase 1–4 dialogue, not template guidance.

## After populating

Before delivering the populated artefact:

1. **Confirm structure matches.** Section ordering as shown above; no sections reordered, dropped, or added relative to the template. Subsequent in-place revisions under the playbook's stable-structure rule depend on this baseline.
2. **Confirm no `<...>` placeholders remain.** A shipped plan with template placeholders signals incomplete dialogue.
3. **Add the `Last reviewed: <YYYY-MM-DD>` line** near the top of the file (immediately after the `# <Project name>` heading is conventional). The marker is playbook-required (`pm-agent.md` §"Output contract — the master plan"); every subsequent in-place revision updates this line.

The artefact then meets the contract for Phase 5 emission: the PRD + master plan are committed + pushed (durable `docs/` docs), and the PM-to-lead kickoff handoff is published as a `handoff` record (`coordination.publish_artefact {kind:"handoff", to:<recipient>, body:…}`) — not committed with them — per `pm-agent.md` §"Phase 5 — PRD + master plan emission"; the PRD is emitted first via `agent:pm-prd-template` and the plan's header cites it.
