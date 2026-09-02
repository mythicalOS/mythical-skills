---
name: test-driven-development
description: |
  The test-first discipline — write a failing test, watch it fail for the
  right reason, then write the minimal code to pass, then refactor while
  green. If you did not watch the test fail, you do not know it tests the
  right thing. Use when implementing any feature or bugfix, before writing
  implementation code. Procedural + discipline: it gates production code on a
  failing test first; it grants NO permission to run tests / shell commands
  (the invoking role's policy + the permission floor govern whether anything
  actually runs) and it does NOT decide scope, rhythm, or whether to ship
  past a finding. Distinct from functional completion verification
  (`verification-completion`) and from root-cause investigation
  (`root-cause-analysis`).
assumes:
  - |
    Claude Code roles run the test command via `Bash`; Codex roles via
    `functions.exec_command` — but only if their own role policy permits it.
    The test-first reasoning is platform-agnostic and is the whole of what
    this skill contributes.
---

# test-driven-development

Write the test first. Watch it fail. Write the minimal code to pass. **If you
did not watch the test fail, you do not know it tests the right thing.**
Violating the letter of this process is violating its spirit.

## Authority boundary (read first)

This skill shapes *how you implement*. It carries procedure, not authority, and
not execution rights.

- It grants **NO permission to run tests or execute shell commands.** Whether the
  test command may actually run is governed by the invoking role's policy + the
  permission floor — not by this skill. A role with no execution rights uses this to
  reason about test-first design and to route, not to run.
- It does NOT decide scope, the authority rhythm, or whether to ship past a
  finding (those are the playbook's / the lead's / operator-only). The exceptions
  below are deferred to the invoking role per the playbook, never decided here.
- It does NOT replace functional verification of the finished work
  (`verification-completion`) or root-cause investigation of a defect
  (`root-cause-analysis`) — it is the implementation discipline between them.

## The Iron Law

```
NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST
```

Wrote production code before its failing test? Delete **the code you yourself
wrote in this TDD attempt** and start over — do not keep it as "reference", do not
"adapt" it while writing the test, do not look at it. Delete means delete, then
implement fresh from the test.

**Shared-checkout guard.** "Delete" applies ONLY to your own just-written code in
the current attempt. This is a shared checkout — **never delete, revert, or
rewrite existing, user-authored, or another agent's code** to satisfy this rule.
If pre-existing code lacks tests, that is not yours to discard: surface it and
handle it within your task boundary, or route per your role. This skill grants no
authority over anyone else's work.

## When to apply

**Always:** new features, bug fixes, refactoring, behavior changes.

**Exceptions** (throwaway prototypes, generated code, configuration files) are
not yours to grant here — defer the call to the invoking role / the operator per the
playbook. Thinking "skip the test just this once"? That is rationalization, not
an exception.

## §"Red-Green-Refactor"

1. **RED — write one failing test.** One behavior, a clear name describing that
   behavior, against real code (no mocks unless unavoidable — a test of a mock
   tests the mock). If the name needs "and", split it.
2. **Verify RED — watch it fail (MANDATORY, never skip).** Run the test. Confirm
   it *fails* (not errors), the failure message is the expected one, and it fails
   because the feature is missing — not a typo. Passes already? You are testing
   existing behavior — fix the test. Errors? Fix the error, re-run until it fails
   correctly.
3. **GREEN — minimal code to pass.** The simplest thing that makes the test pass.
   No extra features, no "while I'm here" refactor, no speculative options (YAGNI).
4. **Verify GREEN — watch it pass (MANDATORY).** Run the test. Confirm it passes,
   the other tests still pass, and the output is pristine (no errors or warnings).
   Test fails? Fix the code, not the test. Other tests fail? If *your* change
   caused them, fix the cause; if they are unrelated or pre-existing baseline
   failures, STOP and report / route per your role — do not silently fix them or
   expand scope (this skill does not decide scope).
5. **REFACTOR — clean up while green.** Remove duplication, improve names, extract
   helpers. Keep every test green; add no behavior.
6. **Repeat** — next failing test for the next behavior.

## §"Good tests"

| Quality | Good | Bad |
|---|---|---|
| **Minimal** | One behavior; "and" in the name means split it | One test asserting validation + parsing + whitespace |
| **Clear** | Name states the behavior | `test('test1')` |
| **Shows intent** | Demonstrates the desired API / behavior | Obscures what the code should do; asserts on a mock |

## §"Why order matters"

A test written *after* the code passes immediately — and passing immediately
proves nothing: it may test the wrong thing, test the implementation rather than
the behavior, or miss the edge case you forgot. You never saw it catch the bug.
Test-first forces you to see the test fail, which is the only proof it tests
something. Tests-after answer "what does this do?"; tests-first answer "what
should this do?"

## §"Rationalizations"

| Excuse | Reality |
|---|---|
| "Too simple to test" | Simple code breaks; the test costs 30 seconds. |
| "I'll test after" | A test passing immediately proves nothing. |
| "Tests-after achieve the same goal" | Tests-after are biased by the code you wrote; tests-first discover the edge cases. |
| "Already manually tested it" | Ad-hoc ≠ systematic; no record, can't re-run. |
| "Deleting hours of work is wasteful" | Sunk cost; unverified code you can't trust IS the waste. |
| "Keep it as reference, test first" | You'll adapt it — that is testing after. Delete means delete. |
| "Need to explore first" | Fine — throw the exploration away, then start with TDD. |
| "Hard to test" | Hard to test = hard to use; listen to the test, simplify the interface. |
| "TDD will slow me down" | TDD is faster than debugging after; that is the pragmatic path. |

## §"Red flags — STOP"

Any of these means STOP and start over with a failing test first:

- Code written before the test; a test added "later".
- A test that passes immediately on first run.
- Can't explain why the test failed.
- "Quick patch now, test later"; "I already manually tested it".
- "It's about spirit not ritual"; "this is different because…".
- "Keep my pre-test code as reference" / "adapt the code I already wrote" (about
  *your own* untested code — not a license to touch anyone else's).

## §"When stuck"

| Problem | Resolution |
|---|---|
| Don't know how to test it | Write the wished-for API first; write the assertion first. Still stuck → route per your role. |
| Test too complicated | The design is too complicated — simplify the interface. |
| Must mock everything | The code is too coupled — use dependency injection. |
| Test setup huge | Extract helpers; if still huge, simplify the design. |

## What this skill does NOT do

- Does NOT grant permission to run tests or execute shell commands — execution is
  the invoking role's policy + the permission floor.
- Does NOT replace functional completion verification (`verification-completion`)
  or root-cause investigation of a defect (`root-cause-analysis`). For a bug fix,
  investigate the root cause, then write the failing test that reproduces it
  before fixing.
- Does NOT decide scope, the authority rhythm, or whether to ship past a finding,
  nor grant the "exceptions" above — those route to the invoking role / the operator.
- Does NOT authorize deleting, reverting, or rewriting existing, user-authored, or
  another agent's code — "start over" applies only to your own just-written code in
  the current attempt (shared-checkout rule).
