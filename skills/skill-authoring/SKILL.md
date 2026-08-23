---
name: skill-authoring
description: |
  The craft of writing a framework SKILL.md once an extraction is
  decided — the house-style frontmatter + body shape, the description
  convention, stable §-anchors, the decision/procedure split, platform
  tool bindings, the brand-free + project-agnostic invariant for shipped
  skills, matching the guidance form to the failure type, and the
  cross-model validation gate. Procedural only + DEFERS: whether to
  extract a skill and WHERE content lives (playbook / overlay / skill) are
  the playbook distillation methodology's relocation gate, NOT re-decided
  here. This skill adds the authoring craft on top of that doctrine; it
  does not create a competing doctrine.
assumes:
  - |
    The doctrine of record for skill EXTRACTION + ALLOCATION + the
    staged validation gates is the maintainers' playbook distillation
    methodology — maintained alongside the role playbooks, not shipped
    with the framework skills; its operative rules are summarized in
    the body below so this file stands alone. This skill is the
    authoring craft for the SKILL.md file once that methodology has
    decided the content belongs in a skill — it summarizes the
    methodology's rules, it does not replace them.
  - |
    Claude Code roles author via the native edit tools; Codex roles via
    `functions.apply_patch`. The house-style conventions, form-to-failure
    matching, and brand-free/project-agnostic discipline are
    platform-agnostic.
---

# skill-authoring

The procedure for writing a framework SKILL.md to house style. It is deliberately
**thin**: the doctrine for *whether* to extract a skill and *where* content lives
already exists in the maintainers' playbook distillation methodology (the
relocation gate, authority-shape, multi-surface consistency, YAML hygiene,
staged validation). This skill adds only the authoring craft for the file
itself, and defers everything that methodology already owns — the deferred
rules are summarized in the next section so this file stands alone.

## Authority boundary (read first)

- **The extraction + allocation decision is NOT this skill's.** Whether a pattern
  is real (recurrence) and where it lives (playbook vs overlay vs skill) are the
  methodology's relocation gate and what-does-NOT-belong rule (both summarized
  below) and the distilling role's call.
  This skill assumes that decision is made and helps write the resulting file.
- **A skill carries procedure, never authority.** If the file you are writing
  needs to make an authority decision to operate (when to STOP, which rhythm, what
  is in scope, override semantics), the extraction is wrong — that content belongs
  in the playbook (the methodology's what-does-NOT-belong rule, below). Author
  within that constraint.

## §"Read the methodology first" (the deferred doctrine, summarized)

The doctrine of record is the maintainers' playbook distillation methodology —
it is maintained alongside the role playbooks and does not ship with the
framework skills, so its operative rules are summarized here; this skill does
not replace it:

- **Relocation gate** — before extracting, weigh how often the pattern fires,
  whether the harness needs it, and where authority lives → the answer places
  content in playbook / overlay / skill.
- **Iteration budget by authority shape** — single- vs two-faced authority sets
  the cross-model round budget for validating the file.
- **Multi-surface authority consistency** — the same authority statement on
  every surface (frontmatter description, body §"Authority boundary", overlay
  allowlist bullet, index).
- **YAML hygiene** — use block scalars (`- |`) for any multi-paragraph
  frontmatter entry from the start.
- **What does NOT belong in a skill** — authority decisions (when to STOP,
  which rhythm, what is in scope, override semantics) stay in the playbook; a
  skill carries procedure only.

## §"House style for a SKILL.md" (the craft this skill adds)

Derive the conventions from the authored skills already in `skills/`; the shape:

- **Frontmatter** — YAML with `name` (letters/numbers/hyphens only) and a piped
  (`|`) multi-line `description`. Per house style the description states the
  skill's mechanics AND closes with the **decision/procedure demarcation**
  ("Procedural only: WHEN / WHETHER X lives in <playbook> §…; this skill is the
  HOW") — this demarcation in the description is the **canonical** authority
  surface every skill carries. Add an `assumes:` block (the per-platform
  invocation paths + key preconditions). A dedicated `authority-boundary:` block
  is **optional** reinforcement — used where the limits are intricate enough to
  restate verbatim (e.g. the template/audit skills' report-not-fix /
  STOP-and-route); most skills carry the demarcation in the description alone.
  Write any such block as a `- |` block scalar (the YAML-hygiene rule above).
  These state the
  procedure's limits; they do not let the skill make scope decisions.
  - *Craft caveat (SDO):* a description that summarizes the full *workflow* tempts
    a reader to act on the description and skip the body. Summarize mechanics +
    the demarcation; do not encode the step sequence in the description.
- **Body** — open with a one-paragraph "this is the HOW" framing, then a
  §"Authority boundary (read first)" section naming what the invoker owns vs what
  the skill does, then **stable §-anchor sections named for the action** (not the
  upstream heading, not `step1`/`helper2`) so invocation points pin to a durable
  anchor. Close with a "What this skill does NOT do" list.
- **Platform tool bindings** — where the procedure runs tools, carry the Claude
  (`Bash` / native edit tools) vs Codex (`functions.exec_command` /
  `functions.apply_patch`) selection in the skill, as the authored skills do; do
  not push it to overlays.
- **Cross-references** — name sibling skills and playbook §-anchors by name; never
  force-load with `@`-links (they burn context). Reference, never duplicate, what
  another skill or the playbook owns.
- **Token discipline** — the always-on cost is the description; keep the body
  focused and cross-reference rather than restate. One excellent example beats
  many; no narrative storytelling.

## §"Match the form to the failure"

Pick the guidance form by the failure it must prevent:

- **A rule skipped under pressure** (the agent knows better and does it anyway) →
  prohibition + a rationalization table + a red-flags list, closing every
  loophole explicitly. (Discipline skills like `verification-completion`.)
- **Wrong-shaped output** (bloated, buried, restated) → a positive recipe/contract
  stating what the output IS, in order — a prohibition backfires here.
- **A required element omitted** → a structural REQUIRED slot in the template.
- **Behaviour that should depend on a condition** → a conditional keyed to an
  observable predicate, not an unconditional rule with exemption clauses.

Avoid nuance/exemption clauses on a recipe — they reopen the negotiation.

## §"Brand-free + project-agnostic (shipped skills)"

These skills ship **with the framework to many consuming projects**, so the file
must reference only framework-generic concepts (roles, rhythms, gates, routing
tokens, the worktree-path mechanism, lead-owns-merge, the permission floor):

- **No upstream-brand reference** anywhere — no brand, no URL, no marketing, and no
  upstream re-harvest baseline in frontmatter. (The vendoring is retired; these are
  first-party skills, not tracked against an upstream.)
- **No consuming-project reference** — no project codename, milestone, repo name,
  domain noun, or single-deployment path. Use generic placeholders ("the
  dispatched task", `feat/<issue-id>-<slug>`).
- **No deployment-host editorializing** — never assert which host a role runs on in
  a given launch ("Reviewer is Codex-only in this project", "Lead runs on Claude",
  "start-agent.sh spawns `claude` only"). The framework supports both hosts and each
  launch chooses; hardcoding one is both project-leakage AND a false invariant for
  the next deployment. State role-ownership (who invokes the skill) and the per-host
  invocation paths bound "per the deployment" — not the host a role happens to use
  here.
- **Grep gate** before declaring done: zero upstream-brand hits, zero
  project-codename / milestone hits, and zero deployment-host-binding claims
  ("in this project", "Codex-only", "runs on Claude", "spawns `claude` only") in the
  body or frontmatter. (This doctrine file necessarily quotes those forbidden forms
  as examples; run the gate over the skill being authored and exclude quoted example
  lists — or this file itself — so the gate does not match its own illustrations.)

## §"Validation: the cross-model gate"

A skill file is load-bearing behaviour-shaping content; validate it cross-model
before it is done (`agent:cross-model-review`). Target the two failure modes most likely
in an authored/ported skill: **decision-leak** (a procedure that smuggles an
authority decision — the what-does-NOT-belong rule above) and **state/project
leak** (a non-generic reference).
Fold each finding to CLEAN; budget rounds by authority shape (the
iteration-budget rule above).
Cross-model is the structural defence the methodology relies on because
self-review misses authority-consistency drift across surfaces (the
multi-surface consistency rule above).

## What this skill does NOT do

- Does NOT decide whether to extract a skill or where content lives (the
  methodology's relocation gate).
- Does NOT own the iteration-budget, multi-surface, or YAML doctrine (the
  maintainers' methodology does) — it carries their operative summaries above.
- Does NOT create a competing skill-authoring doctrine — it is the craft layer
  over the methodology.
