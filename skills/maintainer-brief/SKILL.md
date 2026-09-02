---
name: maintainer-brief
description: |
  Write the maintainer-level companion (conventionally `<plan>-CTO.md` — the suffix is
  the deployment policy's) that every plan or design of
  record ships with — a plain-language translation that makes human review fast without
  making it shallow. Trigger: finalizing any document whose approval belongs to the
  maintainer, or an explicit "write the maintainer brief". The pair rule itself is owned by the
  consuming deployment's documentation policy (typically a "plans of record ship in
  pairs" rule in its documentation-policy document); this skill is the HOW.
assumes:
  - |
    Reached as authored source — this skill is not farm-linked into any project
    plugin, so either harness reads the file directly (`Read` /
    `functions.exec_command`) rather than invoking it as a Skill.
  - |
    The consuming deployment's documentation policy owns the pair rule. Where
    no such rule exists, no companion document is owed and this skill does not
    apply.
---

# maintainer-brief — the maintainer's plain-language companion

## When this applies

A document is **pair-bearing** when its approval belongs to the maintainer: a design of
record, a dated plan of record, anything presented as "please review and approve". Routed
artefacts (task briefs, closeouts, handoffs, reviews) and stable-structure artefacts
(master plan, roadmap, PRDs) are not pair-bearing.

## The contract

1. **Filename:** same directory, same basename, the deployment policy's companion
   suffix (conventionally `-CTO.md`).
2. **Deference:** the companion's opening lines name the plan as the authority and say the
   companion loses on any disagreement.
3. **Same-commit currency:** any commit that changes the plan's content updates the
   companion too, or its message states the companion is unaffected. A stale companion
   reads as current — that is the failure mode this contract exists to prevent.
4. **Status header:** the companion carries the deployment's standard status header
   (`**Status:** live` / `**Updated:** YYYY-MM-DD`) like any ad-hoc doc.

## Structure (adapt, don't pad — target roughly one page, ~80–120 lines)

1. **What this is** — one or two lines: companion to `<plan path>`, plan wins.
2. **The one-paragraph version** — the whole plan in one honest paragraph. Write this
   LAST, keep it FIRST.
3. **What it contains** — the deliverables as a short numbered list, each in consequence
   language ("no inbound port on anyone's laptop, ever"), not mechanism language.
4. **Why this shape** — the 2–4 decisions that make the plan this plan and not another
   one, each with its reason in a sentence.
5. **The stack, and the bets it makes** — every technology and architecture commitment the
   plan carries, as a compact table: the choice · what it does here · why it over the
   alternatives · and its **door** — one-way (hard to leave later) or two-way (swappable).
   Three rules make this section worth having:
   - **Inherited defaults are stated too.** "Bun + TypeScript because it is the house
     standard" is a decision the maintainer may veto; silence is not consent.
   - **Open choices are marked OPEN** with when/how they get decided — never presented as
     settled.
   - **The door column is the review handle**: the maintainer spends their attention on the
     one-way doors.
6. **What "done" means** — the milestones with their criteria translated ("a rollback has
   been exercised, not just written").
7. **Deliberately not in it** — every major deferral, each with why deferring is safe and
   where it is recorded. This section earns the maintainer's trust; never trim it.
8. **The road after** — the follow-on phases as a small table in plain terms.
9. **Quality trail** — what review the plan survived, in one short paragraph with the
   trajectory ("round 1 found three blockers; round 5 returned CLEAN").
10. **What the maintainer still decides** — every open decision, including approving the
    plan itself.

## Writing rules

- **Translate, never abbreviate.** The companion is shorter because it renders meaning,
  not because it drops content. If a section of the plan has no sentence in the
  companion, ask whether the maintainer would be surprised by it later — if yes, it goes
  in ("no silent drops" applies to summaries too).
- **No internal shorthand without a gloss.** Finding IDs (F16, r2.2), gate names, and
  milestone codes appear only with a plain-language rendering, or not at all.
- **Consequence language over mechanism language.** "Even we can only ever hold
  ciphertext" beats "envelope-encrypted to the device public key".
- **Honest edges stay honest.** If the plan defers something risky or carries a declared
  residual, the companion says so at the same strength. Softening in translation is a
  defect, not a courtesy.
- **A one-line motto per surface helps** when it is true: "see everything, drive
  nothing" carries a whole security posture in five words. Never invent one that
  overclaims.
- **The companion inherits its plan's audience, and nothing else decides it.** A companion
  to an internal plan is internal material: internal names are fine in it, and the
  public-copy bar does not apply. A companion to a public-bearing plan is public-bearing
  too, and every rule that binds the plan binds the companion. Decide this once, from the
  plan, before writing — never from where the file happens to live.

## Checklist before committing

- [ ] Opens with deference to the plan
- [ ] One-paragraph version present and true
- [ ] Stack section present — every commitment incl. inherited defaults, doors labeled,
      open choices marked OPEN
- [ ] Every major deferral present, with its recorded home
- [ ] Every open maintainer decision present
- [ ] No unglossed shorthand — read it as someone who never saw the plan
- [ ] Status header present
- [ ] Committed together with (or explicitly declared unaffected by) the plan change
