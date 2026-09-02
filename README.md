<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset=".github/assets/logo-dark.svg">
    <img src=".github/assets/logo-light.svg" alt="mythicalOS" width="84" height="84">
  </picture>
</p>

<h1 align="center">mythical-skills</h1>

<p align="center">
  <strong>Reusable procedures that autonomous agents load to do coordination work the same way every time.</strong>
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-Apache_2.0-blue.svg" alt="License: Apache-2.0"></a>
  <img src="https://img.shields.io/badge/content-markdown_only-555.svg" alt="Content: markdown only">
  <a href="https://mythicalos.ai"><img src="https://img.shields.io/badge/part_of-mythicalOS-0F6B66.svg" alt="Part of mythicalOS"></a>
</p>

---

A **skill** is a markdown procedure — a continuity handoff, a review loop, a planning template,
a routed-communication recipe — that an agent session loads to run one kind of coordination work
consistently and auditably. This repo is the content; the role contracts that decide *who may use
what* live in the companion [`mythical-playbooks`](https://github.com/mythicalOS/mythical-playbooks).

Markdown only — no build, no runtime. A consuming deployment links these into its own agent
tooling, where they typically resolve under an `agent:` or `mythical:` namespace. **Nothing here
grants a skill to a role**; authorization lives with the deployment's role policies.

## Layout

```text
skills/<name>/SKILL.md   # one skill per directory; the procedure lives here
SKILLS-INDEX.md          # the source of truth for what exists, where, and its status
```

`SKILLS-INDEX.md` records existence, path, and status — nothing more. It grants no skill and
decides no plugin wiring.

## Stability

This is a **living system, not a frozen spec.** Skills are tuned continuously against real
multi-agent operation, and a release may change a procedure, output shape, or default without
notice. The one line that never moves: a skill never grants authority the invoking role lacks —
boundary changes happen in `mythical-playbooks`, explicitly. **If you depend on today's exact
behaviour, fork and pin.**

## Contributing

New skills follow the doctrine in `skills/skill-authoring/` and must pass the content check:

```sh
scripts/check-project-agnostic.sh
```

See [CONTRIBUTING.md](CONTRIBUTING.md). The human principal is addressed as the **operator**
throughout; skill content stays deployment-neutral.

## License

**Apache-2.0** — see [LICENSE](LICENSE) and [NOTICE](NOTICE). The licence covers the content, not
the mythicalOS name and marks — see [TRADEMARK.md](TRADEMARK.md). Contributions welcome under a DCO
sign-off, no CLA.

## Skills at a glance

The 31 first-party skills, in the order a session typically reaches for them — pick-up, scoping,
dispatch, build, review, hand-off — followed by the skills that maintain the framework itself. The
**namespace** is how each resolves in the reference mythicalOS deployment (`agent:` coordination,
`mythical:` engineering, `source` = authored but not plugin-linked), an assignment the consuming
deployment's allowlists make, not this repo. `SKILLS-INDEX.md` stays the source of truth for
existence, location, and status.

### 1 · Session start

| Skill | Namespace | Purpose |
|-------|-----------|---------|
| `good-morning` | `agent:` | Recalibrate a fresh or resumed session from durable continuity handoffs. |

### 2 · Scope & plan

| Skill | Namespace | Purpose |
|-------|-----------|---------|
| `design-exploration` | `mythical:` | Turn a raw idea into an approved design through Socratic dialogue. |
| `pm-prd-template` | `agent:` | The PRD template — problem, users, stories, and requirements. |
| `pm-master-plan-template` | `agent:` | The master-plan template the PM emits after the PRD. |
| `domain-glossary` | `agent:` | Build and maintain the project's ubiquitous-language glossary. |
| `adr-authoring` | `agent:` | Record an architecture decision, with its three-gate qualification test. |
| `implementation-planning` | `mythical:` | Write a bite-sized, file-mapped, test-first plan for one unit of work. |

### 3 · Dispatch & orchestrate

| Skill | Namespace | Purpose |
|-------|-----------|---------|
| `lead-decision-patterns` | `agent:` | Extended decision patterns and failure modes for the lead role. |
| `coordination-parallel-dispatch` | `mythical:` | Structure parallel build work as conflict-disjoint sessions. |
| `branch-lifecycle` | `mythical:` | The branch-per-task flow from feature branch to reviewed merge. |
| `worktree-management` | `mythical:` | Physical git-worktree lifecycle for per-session isolation. |
| `routed-comms` | `agent:` | Publish a durable coordination record and wake the live recipient session. |

### 4 · Build

| Skill | Namespace | Purpose |
|-------|-----------|---------|
| `plan-execution` | `mythical:` | Execute an implementation plan inside a dispatched task brief. |
| `test-driven-development` | `mythical:` | Fail for the right reason, write the minimal pass, then refactor. |
| `root-cause-analysis` | `mythical:` | Find a bug's true cause before attempting any fix. |
| `structural-refactor-verification` | `agent:` | The verification audit for a pure-structural refactor. |
| `verification-patterns` | `agent:` | A catalogue of rare verification audits, invoked per pattern. |
| `cross-model-review` | `agent:` | Run a different-model adversarial pass over a load-bearing artefact. |
| `verification-completion` | `mythical:` | Prove work actually works before any done / passing claim. |

### 5 · Review & gate

| Skill | Namespace | Purpose |
|-------|-----------|---------|
| `code-review-response` | `mythical:` | Answer review findings with rigor, not performative agreement. |
| `lead-risk-triage-consolidation` | `agent:` | Consolidate simultaneous escalating verdicts before one escalation. |
| `docs-bar-gate` | `agent:` | The cheap recurring tripwire that catches documentation drift early. |

### 6 · Close out & hand off

| Skill | Namespace | Purpose |
|-------|-----------|---------|
| `coordination-wip-handoff` | `agent:` | Hand off work-in-progress when a session must stop mid-task. |
| `coordination-closeout-templates` | `agent:` | The literal close-out, merge, and status-block templates. |
| `lead-cycle-retro-template` | `agent:` | The six-section cycle-retrospective template. |
| `remember` | `agent:` | Durably record one project lesson into tier-1 memory for future sessions. |
| `good-night` | `agent:` | Write the continuity handoff the next session's `good-morning` consumes. |

### Maintaining the framework itself

Not part of a work cycle — these operate on the skills and docs:

| Skill | Namespace | Purpose |
|-------|-----------|---------|
| `skill-authoring` | `mythical:` | The house style and shape for writing a new framework `SKILL.md`. |
| `skill-system-overview` | `source` | Orientation to how the skill system discovers and links skills. |
| `docs-governance` | `source` | The staged pipeline for a multi-repo public/private documentation split. |
| `maintainer-brief` | `source` | The plain-language maintainer companion that ships with a plan of record. |
