---
name: domain-glossary
description: |
  How to build and maintain the project's ubiquitous-language glossary at
  `<repo>/docs/glossary/CONTEXT.md` — the entry format (one opinionated
  canonical term, a tight one-or-two-sentence IS-definition, an `_Avoid_:`
  synonym list), the maintenance disciplines (challenge conflicting usage,
  sharpen fuzzy terms, stress-test with concrete scenarios, cross-reference
  the code, update inline the moment a term resolves — never batched), the
  context-specific-only inclusion rule, and the multi-context layout
  (per-context files + `CONTEXT-MAP.md`). Procedural only: WHETHER a term
  needs resolving, WHAT the canonical term is, and WHEN the glossary is
  consulted are the planning role's judgment with the stakeholder per
  pm-agent.md §"Output contract — the domain glossary"; other roles READ
  the glossary and flag conflicts to the planning role — they do not edit
  it. This skill is the HOW of the artefact, not the language authority.
assumes:
  - |
    The planning role invokes this skill via whichever host the deployment
    binds it to — on Claude Code via the native Skill tool, or — where the
    deployment runs the planning role on Codex — via functions.exec_command
    reading this file. Format, disciplines, and layout are platform-agnostic
    and bind both paths identically.
  - |
    The glossary is a LIVING artefact, unlike the Phase-5-gated PRD and
    master plan: entries land the moment a term resolves in dialogue, at
    any phase. Lazy creation — the file exists only once the first term is
    resolved; no empty scaffolding.
  - |
    Only the planning role writes `docs/glossary/**`. Every other role
    reads it — reviews challenge inputs against it, briefs and artefacts
    use its vocabulary — and routes a term conflict to the planning role
    through its normal channel instead of editing.
---

# domain-glossary

The procedure for the project's ubiquitous language: one canonical term per
concept, tightly defined, with the rejected synonyms named. The glossary exists
so that a PRD requirement, a task brief, a verdict, and the code all mean the
same thing by the same word — and so the next session does not re-negotiate
vocabulary the stakeholder already settled.

## Authority boundary (read first)

- **Term resolution is the planning role's call, made with the stakeholder.**
  Which word wins, what it means, and what gets demoted to `_Avoid_:` are
  language decisions the planning role owns (pm-agent.md §"Output contract —
  the domain glossary"); this skill carries the format and maintenance craft.
- **Readers flag, never edit.** A role that finds usage conflicting with the
  glossary (in an input, an artefact, or code) surfaces the conflict to the
  planning role via its normal routing — the glossary is not multi-writer.
- **A glossary is not a spec.** Entries are definitions of what a concept IS —
  never implementation detail, mechanism, schema, or decision rationale.
  Decisions live in `docs/adr/` (`agent:adr-authoring`); requirements live in
  the PRD (`agent:pm-prd-template`); the glossary carries only language.

## §"Entry format"

```markdown
# <Context name>

<One or two sentences: what this context is and why it exists.>

## Language

**Order**:
A customer's confirmed request for delivery of specific items.
_Avoid_: Purchase, transaction

**Invoice**:
A request for payment sent to a customer after delivery.
_Avoid_: Bill, payment request
```

- **Be opinionated.** When several words compete for one concept, pick the
  best and list the losers under `_Avoid_:` — an entry without the rejected
  synonyms fails at its one job (stopping the synonyms).
- **Keep definitions tight.** One or two sentences, defining what the concept
  IS, not what it does or how it is built.
- **Context-specific terms only.** General programming concepts (timeout,
  retry, cache, error type) do not belong even when used heavily. Before
  adding, ask: is this concept unique to this domain, or generic engineering?
  Only the former enters.
- **Group under subheadings** when natural clusters emerge; a flat list is
  fine while the language is small.

## §"Maintain during dialogue" — the active disciplines

- **Challenge against the glossary.** When the stakeholder (or an inbound
  artefact) uses a term that conflicts with an existing entry, surface it
  immediately: "the glossary defines *cancellation* as X, but this reads as Y
  — which is it?" Silent coexistence of two meanings is the failure this
  artefact exists to prevent.
- **Sharpen fuzzy language.** When a term is vague or overloaded ("account",
  "job", "sync"), propose a precise canonical term and get it confirmed.
- **Stress-test with concrete scenarios.** When two concepts' boundary is
  unclear, invent edge-case scenarios that force precision about where one
  ends and the other begins — before writing the entries.
- **Cross-reference the code.** When the stakeholder states how something
  works, check whether the codebase agrees; a contradiction between stated
  language and implemented behaviour is surfaced, not papered over. (In an
  existing codebase, explorer artefacts at `docs/architecture/` are the
  harvested vocabulary source — read them before coining new terms.)
- **Update inline, the moment a term resolves.** Write the entry right then —
  batching term capture to an emission gate loses the nuance that resolved it.
  The glossary is exempt from the draft-nothing-before-Phase-5 discipline
  precisely because it records *settled dialogue outcomes*, not draft scope.

## §"Layout — single context by default"

Most projects carry one language: a single `<repo>/docs/glossary/CONTEXT.md`.
Create it lazily when the first term resolves.

When the project genuinely spans multiple bounded contexts (the same word
correctly means different things in different subsystems), split:

```
docs/glossary/
├── CONTEXT-MAP.md        ← lists the contexts + how they relate
├── ordering.md
└── billing.md
```

`CONTEXT-MAP.md` names each context (one line each, linking its file) and the
relationships between them (which context consumes which concepts, which IDs
cross the boundary). Infer which context a term belongs to from the topic under
discussion; when unclear, ask — a term filed in the wrong context is a new
ambiguity, not a resolution. Do not split pre-emptively: the map exists only
once a real second context has emerged.

## §"Consumption by other artefacts"

- The PRD, master plan, task briefs, and review artefacts use the glossary's
  canonical terms — an `_Avoid_:`-listed synonym appearing in a new artefact
  is a flag, not a style choice.
- Reviews measure *inputs* against the glossary: an input whose language
  contradicts an entry gets the conflict surfaced before evaluation proceeds.
- The glossary never blocks emission the way a missing PRD does — it is a
  quality surface, not a gate; the planning role decides when language debt
  warrants stopping to resolve terms.

## What this skill does NOT do

- Does NOT decide which term wins or what it means (planning-role judgment
  with the stakeholder).
- Does NOT grant write access to reader roles — conflicts route to the
  planning role.
- Does NOT record decisions, requirements, or implementation detail (ADR /
  PRD / code territory).
- Does NOT scaffold empty files or pre-emptive context maps — lazy creation
  on the first resolved term, split only on a real second context.
