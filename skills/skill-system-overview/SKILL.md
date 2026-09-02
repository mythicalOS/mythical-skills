---
name: skill-system-overview
description: |
  Orientation to the framework's skill system — how a project's skill
  farm discovers and links the first-party (authored) skills, the §-anchor
  invocation convention, and the decision/procedure split every skill obeys.
  Read this once to learn how skills are sourced and invoked; it is not
  itself a procedure you execute. Authorization of any individual skill to
  any role (the farm allowlist + the role policy) is NOT decided here — it
  lives in the project-setup farm's hardcoded allowlist and the role policy
  layer.
assumes:
  - |
    Claude Code roles read this via the native Skill tool or `Read`;
    Codex roles read it via `functions.exec_command` (e.g.
    `cat skills/skill-system-overview/SKILL.md`). It is reference content,
    not a procedure — invoking it loads the orientation, nothing executes.
---

# Skill system — orientation

The framework treats skills as a third structural layer beneath the role
playbook (the role contract) and the host overlay (the platform binding): a
skill extracts a conditional or rare *procedure* into a lazily-loaded markdown
file at `skills/<name>/SKILL.md`. The always-on cost of a skill is its
frontmatter `description` only; the body loads when a role invokes it. This file
explains how skills are **sourced, discovered, and invoked** — it is not a
procedure you run.

## Skill source: first-party authored

All skills are **first-party (authored)** — written for this framework, living
under `skills/<name>/SKILL.md`, speaking the framework's vocabulary (authority
rhythms, the gate chain, coordination routing, branch-per-task, the worktree-path
mechanism, lead-owns-merge, the permission floor) and obeying the conventions below.

The resolution index (`SKILLS-INDEX.md`) answers exactly one question — *where
does skill X live and what is its status*. It records existence + location; it
grants nothing.

## Discovery + linking: the farm

A project does not read the authored tree directly. The **skill farm** (the
project-setup step that builds a project's `.claude/skills/`) links skills in
**by reference**, consulting its own **hardcoded, audited allowlist** — never the
resolution index and never any self-declared capability manifest. A skill
existing in the authored tree does **not** make it available to a project; the
farm allowlist does. This is the floor posture: nothing auto-activates.

## Invocation convention

- **Reference form.** First-party skills are addressed as
  `<framework-namespace>:<skill-name>` when a playbook pins one (e.g.
  `<ns>:worktree-management`). The exact namespace token is assigned by the
  consuming deployment's wiring layer, not here.
- **§-anchor pinning.** A playbook pins a skill to a named section with the
  `§"Section Name"` convention so an invocation point references a stable anchor,
  not a line number or an upstream heading. Author section names for the action
  they carry, so future invocation points do not drift.
- **Platform binding.** The same skill is invoked with different mechanics per
  host — Claude Code via the native Skill tool, Codex by reading the file via
  `functions.exec_command` — but with identical authority semantics. The skill
  body is platform-agnostic; each host overlay binds its own tool names.

## The decision/procedure split (every skill obeys it)

A skill carries the **HOW** — the procedure executed *within* decisions the
invoking playbook has already made. It does **not** carry authority decisions:
when to STOP, which authority rhythm applies, what is in scope, who may invoke
it, or any override semantics. Those are role-contract material. Every authored
skill states this boundary in a §"Authority boundary" section and routes genuine
decisions to the authority-holder. If a candidate skill needs to make an
authority decision to operate, the extraction is wrong — the content belongs in
the playbook.

## What this orientation does NOT do

- Does NOT authorize any skill for any role (farm allowlist + role policy own
  that).
- Does NOT decide which skills a project links (the farm allowlist does).
- Does NOT finalize the namespace token (the wiring layer does).
- Does NOT replace `SKILLS-INDEX.md` as the existence/location record.
