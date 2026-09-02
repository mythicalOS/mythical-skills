# SKILLS-INDEX

Single resolution index for **all** agent skills in this repo (all first-party /
authored; there is no vendored open-source tree). This file answers
exactly one question: *"where does skill X live, and when in a session is it used."*
It is the source-of-truth for **existence + location**, **not** authorization.

- It does **not** grant any skill to any role. Role/tool authorization lives in the
  playbook framework and in the consuming deployment's hardcoded audited allowlists.
- It does **not** decide what gets linked into a project's `.claude/skills/`. That
  is the consuming deployment's skill-farm's job, and the farm consults its own
  hardcoded allowlist — **never this index, never `manifest.json`**.
- It is **brand-free** throughout: there is no vendored open-source tree, and no
  upstream brand name, source basename, or version reference appears anywhere in
  this index. The skills below are independent first-party
  work, not derivatives of any upstream.

## Phase legend

Each skill is tagged with the point in a session's lifecycle where it is typically
reached — the same ordering the README's "Skills at a glance" uses. It is an
orientation aid, not an authorization.

| Phase | Where in a session |
|-------|--------------------|
| `start` | Session pickup / recalibration |
| `scope` | Scoping, planning, and decision records |
| `dispatch` | Branch/worktree setup, routing, and parallel dispatch |
| `build` | Implementation, verification, and cross-model review |
| `review` | Review response and gate checks |
| `closeout` | Handoff, close-out, retro, and memory |
| `meta` | Operates on the framework itself, not a work cycle |

**Farm/plugin-linking is a separate axis from the phase above** — it is controlled
entirely by the consuming deployment's setup tooling and its hardcoded allowlists
(the sole registration authority; this index never controls linking), with per-role
authorization in the role policy JSON. Current state: of the **31** authored skills,
**11** register into the project-local `mythical` plugin (resolvable as
`mythical:<name>`), and **17** register into the project-local `agent` plugin
(resolvable as `agent:<name>` — the 16 coordination/continuity skills plus
`docs-bar-gate`); `skill-system-overview`, `docs-governance`
and `maintainer-brief` remain authored source only.

## Authored skills (`skills/`)

First-party skills — all independently authored in the framework's vocabulary. No
upstream source, basename, or version is tracked (there is no vendored tree and no
re-harvest baseline).

| Skill | Path | Phase |
|-------|------|-------|
| design-exploration | `skills/design-exploration/SKILL.md` | scope |
| implementation-planning | `skills/implementation-planning/SKILL.md` | scope |
| coordination-parallel-dispatch | `skills/coordination-parallel-dispatch/SKILL.md` | dispatch |
| branch-lifecycle | `skills/branch-lifecycle/SKILL.md` | dispatch |
| worktree-management | `skills/worktree-management/SKILL.md` | dispatch |
| plan-execution | `skills/plan-execution/SKILL.md` | build |
| test-driven-development | `skills/test-driven-development/SKILL.md` | build |
| root-cause-analysis | `skills/root-cause-analysis/SKILL.md` | build |
| verification-completion | `skills/verification-completion/SKILL.md` | build |
| code-review-response | `skills/code-review-response/SKILL.md` | review |
| skill-authoring | `skills/skill-authoring/SKILL.md` | meta |
| skill-system-overview | `skills/skill-system-overview/SKILL.md` | meta |

31 authored skills; 11 linked into the `mythical` plugin and 17 linked into the
`agent` plugin by the consuming deployment's allowlists (`skill-system-overview`,
`docs-governance` and `maintainer-brief` are authored source only — see the
farm/plugin-linking note above). There is no separate `code-review-request` skill:
the pre-handoff discipline lives in `branch-lifecycle` (§"Reviewer-gate input prep
(pre-handoff)").

### Authored continuity skills (`skills/`)

First-party handoff lifecycle skills for compact session shutdown and pickup.
Linked into the project-local `agent` plugin by the consuming deployment's
coordination allowlist.

| Skill | Path | Phase |
|-------|------|-------|
| good-morning | `skills/good-morning/SKILL.md` | start |
| good-night | `skills/good-night/SKILL.md` | closeout |

### Authored coordination skills (`skills/`)

The `agent:` namespace (parallel to `mythical:`). First-party, no upstream basename.
Linked into the project-local `agent` plugin via the consuming deployment's
coordination allowlist (its setup tooling is the sole registration authority; this
index never controls linking).
`remember` is the in-session tier-1 directed-write surface via the sanctioned
`memory.append` MCP write path. `adr-authoring`, `pm-prd-template` and `domain-glossary`
are the `docs/adr/` decision-record template/procedure and the
`docs/prd/` PRD template; which roles emit them, tiers, and emission ordering
are playbook + role-policy authority, not recorded here; `domain-glossary` is the `docs/glossary/` ubiquitous-language template/maintenance procedure).

| Skill | Path | Phase |
|-------|------|-------|
| pm-prd-template | `skills/pm-prd-template/SKILL.md` | scope |
| pm-master-plan-template | `skills/pm-master-plan-template/SKILL.md` | scope |
| domain-glossary | `skills/domain-glossary/SKILL.md` | scope |
| adr-authoring | `skills/adr-authoring/SKILL.md` | scope |
| lead-decision-patterns | `skills/lead-decision-patterns/SKILL.md` | dispatch |
| routed-comms | `skills/routed-comms/SKILL.md` | dispatch |
| structural-refactor-verification | `skills/structural-refactor-verification/SKILL.md` | build |
| verification-patterns | `skills/verification-patterns/SKILL.md` | build |
| cross-model-review | `skills/cross-model-review/SKILL.md` | build |
| lead-risk-triage-consolidation | `skills/lead-risk-triage-consolidation/SKILL.md` | review |
| coordination-wip-handoff | `skills/coordination-wip-handoff/SKILL.md` | closeout |
| coordination-closeout-templates | `skills/coordination-closeout-templates/SKILL.md` | closeout |
| lead-cycle-retro-template | `skills/lead-cycle-retro-template/SKILL.md` | closeout |
| remember | `skills/remember/SKILL.md` | closeout |

### Authored documentation-governance skills (`skills/`)

The staged pipeline for bringing a multi-repository documentation corpus under a
public/private split, the cheap recurring drift check that holds the line
afterwards, and the maintainer-brief companion. `docs-bar-gate` is farm-linked
into the `agent` plugin (which roles may run it is the role-policy layer's record,
not this index's); the other two are **authored source only** (no farm allowlist,
no project-local plugin).

| Skill | Path | Phase |
|-------|------|-------|
| docs-bar-gate | `skills/docs-bar-gate/SKILL.md` | review |
| docs-governance | `skills/docs-governance/SKILL.md` | meta |
| maintainer-brief | `skills/maintainer-brief/SKILL.md` | meta |

`maintainer-brief` ("maintainer" is the human the brief addresses — distinct from
the framework's cto *role*): the
maintainer-level plain-language companion every plan/design of record ships
with; the pair rule is owned by the consuming deployment's documentation
policy, this skill carries the structure and writing rules.

## Note on `manifest.json`

`manifest.json` (`{ "skills": [], "plugins": [], "prereqs": [] }`) is the repo's
pre-existing machine-readable skeleton. The farm's security model **deliberately
never consults it** (self-declared capability tags are not trusted). It is left
as-is. **`SKILLS-INDEX.md` is the human index of record**; `manifest.json` is not
authoritative for discovery or authorization.
