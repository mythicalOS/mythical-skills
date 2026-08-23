# SKILLS-INDEX

Single resolution index for **all** agent skills in this repo (all first-party /
authored — the vendored open-source tree was removed 2026-06-19). This file answers
exactly one question: *"where does skill X live, and what is its status."* It is the
source-of-truth for **existence + location**, **not** authorization.

- It does **not** grant any skill to any role. Role/tool authorization lives in the
  playbook framework and in the consuming deployment's hardcoded audited allowlists.
- It does **not** decide what gets linked into a project's `.claude/skills/`. That
  is the consuming deployment's skill-farm's job, and the farm consults its own
  hardcoded allowlist — **never this index, never `manifest.json`**.
- It is **brand-free** throughout: the vendored open-source tree was removed
  2026-06-19, and no upstream brand name, source basename, or version reference
  appears anywhere in this index. The skills below are independent first-party
  work, not derivatives of any upstream.

## Status legend

| Status | Meaning |
|--------|---------|
| `authored · ported` | First-party skill under `skills/` covering a general capability the retired upstream tree also addressed — **independently authored** in framework vocabulary (a clean rewrite, not a derivative copy). |
| `authored · native` | First-party skill under `skills/`, authored from scratch (no prior art in the retired upstream). |

**Farm/plugin-linking is a separate axis from the status above** — it is controlled
entirely by the consuming deployment's setup tooling and its hardcoded allowlists
(the sole registration authority; this index never controls linking), with per-role
authorization in the role policy JSON. Current state: of the **32** authored skills,
**12** register into the project-local `mythical` plugin (resolvable as
`mythical:<name>`), and **17** register into the project-local `agent` plugin
(resolvable as `agent:<name>` — the 16 coordination/continuity skills plus
`docs-bar-gate`, farmed 2026-08-18); `skill-system-overview`, `docs-governance`
and `maintainer-brief` remain authored source only.

## Authored skills (`skills/`)

First-party skills — all independently authored in the framework's vocabulary. No
upstream source, basename, or version is tracked (the vendored tree was retired
2026-06-19; skills carry no re-harvest baseline).

| Skill | Path | Status |
|-------|------|--------|
| skill-system-overview | `skills/skill-system-overview/SKILL.md` | authored · native |
| branch-lifecycle | `skills/branch-lifecycle/SKILL.md` | authored · native |
| worktree-management | `skills/worktree-management/SKILL.md` | authored · ported |
| coordination-parallel-dispatch | `skills/coordination-parallel-dispatch/SKILL.md` | authored · ported |
| plan-execution | `skills/plan-execution/SKILL.md` | authored · ported |
| implementation-planning | `skills/implementation-planning/SKILL.md` | authored · ported |
| design-exploration | `skills/design-exploration/SKILL.md` | authored · ported |
| code-review-response | `skills/code-review-response/SKILL.md` | authored · ported |
| verification-completion | `skills/verification-completion/SKILL.md` | authored · ported |
| skill-authoring | `skills/skill-authoring/SKILL.md` | authored · ported |
| root-cause-analysis | `skills/root-cause-analysis/SKILL.md` | authored · ported |
| test-driven-development | `skills/test-driven-development/SKILL.md` | authored · ported |

31 authored skills (21 native, 10 ported); 11 linked into the `mythical` plugin and
17 linked into the `agent` plugin by the consuming deployment's allowlists
(`skill-system-overview`, `docs-governance` and `maintainer-brief` are authored
source only — see the farm/plugin-linking note above). The former
`code-review-request` skill was merged into `branch-lifecycle`
(§"Reviewer-gate input prep (pre-handoff)") on 2026-08-18 — its pre-handoff
discipline lives there now, not in a skill of its own.

### Authored continuity skills (`skills/`) — framework-native

First-party handoff lifecycle skills for compact session shutdown and pickup.
Linked into the project-local `agent` plugin by the consuming deployment's
coordination allowlist.

| Skill | Path | Status |
|-------|------|--------|
| good-morning | `skills/good-morning/SKILL.md` | authored · native |
| good-night | `skills/good-night/SKILL.md` | authored · native |

### Authored coordination skills (`skills/`) — framework-native

Ported 2026-06-18 from the playbook framework's then-embedded skills tree into the
`agent:` namespace (parallel to `mythical:`). First-party, no upstream basename.
Linked into the project-local `agent` plugin via the consuming deployment's
coordination allowlist (its setup tooling is the sole registration authority; this
index never controls linking).
`remember` added 2026-06-27 (native — the in-session tier-1 directed-write surface
over `tools/memory` `append`). `adr-authoring` + `pm-prd-template` + `domain-glossary` added 2026-07-02
(native — the `docs/adr/` decision-record template/procedure and the
`docs/prd/` PRD template; which roles emit them, tiers, and emission ordering
are playbook + role-policy authority, not recorded here; `domain-glossary` is the `docs/glossary/` ubiquitous-language template/maintenance procedure).

| Skill | Path | Status |
|-------|------|--------|
| routed-comms | `skills/routed-comms/SKILL.md` | authored · native |
| remember | `skills/remember/SKILL.md` | authored · native |
| adr-authoring | `skills/adr-authoring/SKILL.md` | authored · native |
| coordination-wip-handoff | `skills/coordination-wip-handoff/SKILL.md` | authored · native |
| cross-model-review | `skills/cross-model-review/SKILL.md` | authored · native |
| coordination-closeout-templates | `skills/coordination-closeout-templates/SKILL.md` | authored · native |
| lead-cycle-retro-template | `skills/lead-cycle-retro-template/SKILL.md` | authored · native |
| lead-decision-patterns | `skills/lead-decision-patterns/SKILL.md` | authored · native |
| lead-risk-triage-consolidation | `skills/lead-risk-triage-consolidation/SKILL.md` | authored · native |
| pm-master-plan-template | `skills/pm-master-plan-template/SKILL.md` | authored · native |
| pm-prd-template | `skills/pm-prd-template/SKILL.md` | authored · native |
| domain-glossary | `skills/domain-glossary/SKILL.md` | authored · native |
| structural-refactor-verification | `skills/structural-refactor-verification/SKILL.md` | authored · native |
| verification-patterns | `skills/verification-patterns/SKILL.md` | authored · native |

### Authored documentation-governance skills (`skills/`) — framework-native

Added 2026-08-02 (native). The staged pipeline for bringing a multi-repository
documentation corpus under a public/private split, the cheap recurring drift
check that holds the line afterwards, and the maintainer-brief companion.
`docs-bar-gate` was farm-linked into the `agent` plugin on 2026-08-18 (which
roles may run it is the role-policy layer's record, not this index's); the
other two are **authored source only** (no farm allowlist, no project-local
plugin).

| Skill | Path | Status |
|-------|------|--------|
| docs-governance | `skills/docs-governance/SKILL.md` | authored · native |
| docs-bar-gate | `skills/docs-bar-gate/SKILL.md` | authored · native |
| maintainer-brief | `skills/maintainer-brief/SKILL.md` | authored · native |

Added 2026-08-02 (native, same terms as the batch above). `maintainer-brief`
(renamed from `cto-brief` 2026-08-18 — the old name collided with the
framework's cto *role*; "maintainer" is the human the brief addresses): the
maintainer-level plain-language companion every plan/design of record ships
with; the pair rule is owned by the consuming deployment's documentation
policy, this skill carries the structure and writing rules.

## Note on `manifest.json`

`manifest.json` (`{ "skills": [], "plugins": [], "prereqs": [] }`) is the repo's
pre-existing machine-readable skeleton. The farm's security model **deliberately
never consults it** (self-declared capability tags are not trusted). It is left
as-is. **`SKILLS-INDEX.md` is the human index of record**; `manifest.json` is not
authoritative for discovery or authorization.
