---
name: code-review-response
description: |
  How to respond to review findings with technical rigor instead of
  performative agreement — read the full verdict, verify each finding
  against the codebase before implementing, disposition each as fix /
  refute-with-cited-evidence / defer-with-rationale, fix in
  severity order testing each, and route the re-review back to the
  reviewer via `coordination.deliver`. Procedural only: severity grading and the verdict are
  the reviewer's; CRITICAL override is operator-only; WHICH authority rhythm
  gates the re-commit is the playbook's. This skill is the disciplined HOW
  of folding findings, not the authority to overrule a verdict.
assumes:
  - |
    Findings arrive as a routed reviewer verdict — a `code_review`
    record carrying severity/category/location/evidence and citing the
    reviewed branch SHA (`branch-lifecycle`). The response folds them on
    the feature branch and routes the re-review back to the reviewer via
    `coordination.deliver` (`agent:routed-comms`) — it is not a chat
    exchange with a present human partner.
  - |
    Claude Code roles verify + fix via `Bash` (`git`, `grep`) + the native
    edit tools; Codex roles via `functions.exec_command` /
    `functions.apply_patch`. The verify-before-implementing, disposition,
    and no-performative-agreement discipline is platform-agnostic.
---

# code-review-response

The procedure for handling review findings: evaluate them technically, fold the
correct ones, refute the wrong ones with cited evidence, and route the re-review
back. Review is technical evaluation, not emotional performance — verify before
implementing, no performative agreement, technical correctness over social
comfort.

## Authority boundary (read first)

- **The verdict and severity grading are the reviewer's**, not the responder's.
  This skill folds findings within that verdict; a CRITICAL finding is operator-only
  override (exercised through the apex under rhythm D) — the responder does not
  decide to ship past it.
- **Disagreement is refutation with evidence, not unilateral override.** Pushing
  back on a finding means citing the code/tests that prove it wrong, the same
  fix / refute / defer discipline the framework applies to any review pass — never
  silently ignoring it.
- **The re-commit follows the dispatch's authority rhythm**, decided by the
  playbook, not here.
- **No co-design creep.** Responding to a finding does not license scope
  expansion; an adjacent improvement a reviewer suggests beyond the dispatch's
  scope is surfaced (scope-discovery), not absorbed into the fix.

## §"Read and verify before implementing"

1. **Read** the complete verdict without reacting to any single item.
2. **Understand** each finding — restate the requirement in your own words; if any
   item is unclear, STOP and ask for clarification before implementing *anything*
   (items can be related; partial understanding yields a wrong fix). Route the
   clarification to the verdict's author/dispatcher via the token, not a guess.
3. **Verify** each finding against codebase reality: is it correct for *this*
   codebase, does the current implementation exist for a reason, would the change
   break something, does it apply on all targeted platforms/versions?

**No performative agreement.** Do not open with "you're absolutely right",
"great catch", or any gratitude/affirmation; do not announce "implementing now"
before verifying. State the technical disposition or just make the fix — the code
shows you heard it.

## §"Disposition each finding: fix / refute / defer"

Every finding gets one explicit disposition before re-review (never silently
dropped):

- **Fix** — the finding is correct and in-scope: fold it on the branch.
- **Refute** — the finding is wrong for this codebase: push back with technical
  reasoning and the cited evidence (the test/code/version constraint that proves
  it). Apply a YAGNI check to "implement it properly" suggestions for unused
  surface — grep for actual usage; if unused, propose removal rather than building
  it out.
- **Defer** — correct but legitimately out of this dispatch's scope: record the
  rationale and surface it for a follow-up, do not absorb it now.

## §"Fix discipline"

For multi-item feedback:

1. Clarify everything unclear FIRST (above).
2. Then fix in severity order: blocking/security → simple (typos, imports) →
   complex (logic, refactor).
3. **Test each fix individually**; verify no regressions (`verification-completion`).
4. If you pushed back and were wrong, state the correction factually and move on —
   no long apology, no defending why you pushed back.

## §"Route the re-review back"

After folding, push the updated branch per the rhythm and report the **new SHA**;
route the re-review back to the gate with `coordination.deliver` (`agent:routed-comms`),
so the reviewer re-reviews against the new commit (`branch-lifecycle` §"Gate-role
review against the cited SHA"). A verdict cites a SHA — a re-review must point at
the folded SHA, not the original.

## Common mistakes

| Mistake | Fix |
|---|---|
| Performative agreement | State the disposition or just fix it |
| Implementing before verifying | Verify each finding against the codebase first |
| Fixing the clear items, asking about the rest later | Clarify ALL unclear items first |
| Batch-fixing without testing | One at a time, verify each |
| Expanding scope to satisfy a suggestion | Fix in-scope; defer/ surface the rest |
| Re-routing the re-review at the old SHA | Push the fold; cite the new SHA |

## What this skill does NOT do

- Does NOT grade severity or issue the verdict (reviewer's).
- Does NOT decide to ship past CRITICAL (operator-only override).
- Does NOT pick the re-commit authority rhythm (playbook).
- Does NOT license scope expansion in response to a finding.
