---
name: verification-completion
description: |
  Functional confirmation that work actually works before any
  completion / fixed / passing claim — run the proving command fresh in
  this turn, read the full output and exit code, and only then state the
  claim WITH that evidence. Use before committing, before a close-out,
  before reporting a branch ready, before delegating onward. Explicitly
  distinct from the cross-model adversarial gate and from the coverage /
  structural audit skills (see the positioning section). Procedural +
  discipline: this skill gates the executor's own claims with evidence; it
  does not decide scope, rhythm, or whether to ship past a finding.
assumes:
  - |
    Claude Code roles run the proving command via `Bash`; Codex roles via
    `functions.exec_command`. The evidence-before-claims discipline is
    platform-agnostic. This is a same-executor functional check; the
    cross-MODEL pass is a different gate (`agent:cross-model-review`).
---

# verification-completion

Claiming work is complete, fixed, or passing without fresh verification is
dishonesty, not efficiency. **Evidence before claims, always.** Violating the
letter of this rule is violating its spirit.

## Authority boundary (read first)

This skill is a positive obligation on the executor's own claims — it gates *what
you may assert*, not what the team decides.

- It does NOT decide scope, the authority rhythm, or whether to ship past a
  reviewer finding (those are the playbook's / the reviewer's / operator-only).
- It does NOT auto-fix what verification reveals — a failing check is reported
  honestly with its output; the disposition is the playbook's.

## The iron law

```
NO COMPLETION CLAIM WITHOUT FRESH VERIFICATION EVIDENCE
```

If you have not run the verification command in this message, you cannot claim it
passes.

## §"The gate function"

Before claiming any status or expressing satisfaction:

1. **Identify** the command that proves the claim.
2. **Run** the full command, fresh and complete (not a remembered prior run).
3. **Read** the full output, check the exit code, count failures.
4. **Verify** the output actually confirms the claim — if not, state the real
   status with evidence.
5. **Only then** make the claim, with the evidence attached.

Skipping any step is asserting, not verifying.

## §"Position among the verification surfaces"

This is one of several verification surfaces in the framework; it is the
**functional, same-executor** one, and it is **not** a substitute for the others:

- **vs the cross-model adversarial gate (`agent:cross-model-review`, Gate 2.2).** That
  pass has a *different model* review the artefact for blind spots a self-review
  cannot see. This skill is *you* running the proving command on your own work.
  Both are required and neither substitutes: cross-model can be CLEAN while the
  build is functionally broken, and a passing test can coexist with a defect only
  another model spots.
- **vs the coverage / structural audit skills (`agent:verification-patterns`,
  `agent:structural-refactor-verification`).** Those are *report-only observability*
  audits — they answer "what is covered" / "is the structure intact" and hand the
  lead a matrix to disposition. This skill answers "does *this specific claim*
  hold, with fresh evidence, right now." It produces a claim+evidence, not a
  coverage matrix.

State the claim against the right surface; do not let one stand in for another.

## §"Common failures"

| Claim | Requires | Not sufficient |
|---|---|---|
| Tests pass | Test command output: 0 failures | A previous run; "should pass" |
| Linter clean | Linter output: 0 errors | A partial check; extrapolation |
| Build succeeds | Build command: exit 0 | Linter passing; "logs look fine" |
| Bug fixed | Original symptom re-tested: passes | Code changed, assumed fixed |
| Regression test works | Red-green cycle verified (revert fix → fails → restore → passes) | Test passes once |
| Dispatched work landed | VCS diff / branch SHA shows the change | The session reported "success" |
| Requirements met | Line-by-line checklist against the brief | Tests passing |

## §"Rationalization prevention"

| Excuse | Reality |
|---|---|
| "Should work now" | Run the verification |
| "I'm confident" | Confidence ≠ evidence |
| "Just this once" | No exceptions |
| "Linter passed" | Linter ≠ compiler |
| "The dispatched session said success" | Verify independently (diff / SHA) |
| "I'm tired" | Exhaustion ≠ excuse |
| "Partial check is enough" | Partial proves nothing |
| "Different words, so the rule doesn't apply" | Spirit over letter |

## §"Red flags — STOP"

- Using "should", "probably", "seems to".
- Expressing satisfaction before verification ("Great!", "Perfect!", "Done!").
- About to commit / push / report a branch ready / close out without fresh
  verification.
- Trusting a dispatched session's success report without checking the diff/SHA.
- Relying on a partial check; thinking "just this once"; wanting the work over.
- ANY wording implying success without having run the verification.

## When to apply

Always before: any completion/fixed/passing claim or expression of satisfaction;
committing, pushing, or reporting a branch ready for the merge gate; writing a
close-out that claims done; delegating onward. The rule applies to exact phrases,
paraphrases, synonyms, and any implication of success.

## What this skill does NOT do

- Does NOT replace the cross-model adversarial gate (`agent:cross-model-review`).
- Does NOT produce a coverage matrix or structural audit
  (`agent:verification-patterns`, `agent:structural-refactor-verification`).
- Does NOT decide scope, rhythm, or shipping past a finding.
- Does NOT auto-fix what verification reveals — report it honestly.
