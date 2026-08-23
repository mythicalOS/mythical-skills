---
name: root-cause-analysis
description: |
  The discipline of finding the TRUE cause of a bug, test failure, or
  unexpected behavior before proposing or attempting any fix — so the fix
  addresses the cause, not the symptom, and the class is hardened against
  recurrence. Use on any defect, and ESPECIALLY under time pressure when a quick
  patch is tempting. Procedural + discipline: it shapes HOW to reason about a defect and
  gates fix-proposals on investigation; it grants NO permission to run tests /
  debug / shell commands (the invoking role's policy + the permission floor govern
  whether anything actually runs), and it does NOT decide scope, rhythm, or
  whether to ship past a finding.
assumes:
  - |
    Where the investigation calls for a command, Claude Code roles run it via
    `Bash` and Codex roles via `functions.exec_command` — but only if their own
    role policy permits it. The find-cause-before-fix reasoning is
    platform-agnostic and is the whole of what this skill contributes.
  - |
    Review-class roles (e.g. QA) consult this to shape a repro / test strategy
    and never execute from it — consistent with a read-reference posture even
    though debugging naturally involves commands.
---

# root-cause-analysis

Random fixes waste time and create new bugs; quick patches mask the underlying
issue. **Always find the root cause before attempting a fix — a symptom fix is a
failure.** Violating the letter of this process is violating its spirit.

## Authority boundary (read first)

This skill shapes *how you reason* about a defect. It carries procedure, not
authority, and not execution rights.

- It grants **NO permission to run tests, debug, or execute shell commands.**
  Whether any diagnostic or fix command may actually run is governed by the
  invoking role's policy + the permission floor — not by this skill. A role with no
  execution rights uses this to reason and to route, not to run.
- **Review-class roles (QA) consult it to shape repro / test strategy only and
  never execute from it** — debugging naturally involves commands, but the
  read-reference posture stands.
- It does NOT replace functional verification of the fix (`verification-completion`)
  and it does NOT decide scope, the authority rhythm, or whether to ship past a
  finding (those are the playbook's / the lead's / operator-only).
- It does NOT apply the fix for you — it tells you what to investigate before a
  fix is even proposed.

## The iron law

```
NO FIX PROPOSED WITHOUT ROOT-CAUSE INVESTIGATION FIRST
```

If you have not completed Phase 1, you cannot propose a fix.

## When to apply

Any technical issue: test failures, production bugs, unexpected behavior,
performance problems, build failures, integration issues.

**Especially when** — under time pressure (emergencies make guessing tempting),
"just one quick fix" seems obvious, a previous fix didn't work, you've already
tried several fixes, or you don't fully understand the issue.

**Do not skip when** — the issue "seems simple" (simple bugs have root causes
too), you're in a hurry (rushing guarantees rework), or someone wants it fixed
NOW (systematic is faster than thrashing).

## §"Phase 1 — Investigate the root cause"

Before attempting any fix:

1. **Read the error completely.** Don't skip past errors or warnings — they
   often contain the exact answer. Read the whole stack trace; note line numbers,
   file paths, error codes.
2. **Reproduce consistently.** Can you trigger it reliably, with exact steps,
   every time? If it is not reproducible, gather more data — do not guess.
3. **Check recent changes.** What changed that could cause this? Inspect the
   diff and recent commits, new dependencies, config or environment differences.
4. **In multi-component systems, instrument the boundaries first.** When the path
   spans components (CI → build → sign; API → service → database), add diagnostic
   logging at each boundary — what data enters, what exits, whether config /
   environment propagates — run once to gather evidence of *where* it breaks,
   then investigate that specific component. Don't propose fixes before the
   evidence localizes the failure.
5. **Trace the data flow backward to the source.** When the error surfaces deep
   in the call stack, the failure point is usually a symptom. Trace the bad value
   up the call chain — where did it originate, what passed it on — until you find
   the original trigger, and fix there, not where it surfaced. When manual
   tracing dead-ends, add stack-capture instrumentation *before* the dangerous
   operation (capture the call stack + the relevant inputs/environment) and
   re-run to get the real origin. To find which test pollutes shared state,
   bisect: run the suite one file at a time, checking for the unwanted artefact
   after each, and stop at the first file that produces it.

## §"Phase 2 — Analyze the pattern"

Find the pattern before fixing:

1. **Find a working example** — locate similar code in the same codebase that
   works. What works that is close to what's broken?
2. **Compare against the reference completely** — if you're implementing a known
   pattern, read the reference implementation in full (every line), not a skim.
3. **List every difference** between the working and the broken case, however
   small — don't assume "that can't matter."
4. **Understand the dependencies** — what other components, settings, environment,
   or assumptions does this rely on?

## §"Phase 3 — Hypothesize and test minimally"

Use the scientific method:

1. **Form one hypothesis, stated explicitly** — "I think X is the root cause
   because Y." Be specific, not vague; write it down.
2. **Test it with the smallest possible change** — one variable at a time; don't
   change several things at once.
3. **Verify before continuing** — did it work? If yes, go to Phase 4. If no, form
   a NEW hypothesis; do **not** stack another fix on top of the last.
4. **When you don't know, say so** — "I don't understand X." Don't pretend; gather
   more evidence or route for help rather than guess.

## §"Phase 4 — Fix the cause, then harden"

1. **Write the failing test first** — the simplest reproduction, automated where a
   framework exists, before you fix (`test-driven-development`).
2. **Make a single fix at the root cause** — one change, addressing the cause
   identified; no "while I'm here" improvements, no bundled refactor.
3. **Verify the fix with fresh evidence** — the original symptom re-tested passes,
   no other tests broke, the issue is actually resolved (`verification-completion`).
4. **Harden so the class can't recur (defense-in-depth)** — add validation at each
   layer the bad data passes through (entry-point rejection, business-logic check,
   an environment guard for context-specific dangers, debug instrumentation) so
   the same bug becomes structurally impossible, not just patched at one point.
   For timing / flaky failures, replace arbitrary sleeps with **condition-based
   waiting** — poll for the actual state you need, with a bounded timeout and a
   clear error — rather than guessing a delay.
5. **If the fix doesn't work, STOP and count.** Fewer than 3 attempts → return to
   Phase 1 with the new information. **3 or more failed fixes → stop fixing and
   question the architecture** (see below); do not attempt fix #4.

**When 3+ fixes have failed — question the architecture.** A pattern where each
fix reveals new shared state / coupling elsewhere, fixes require "massive
refactoring," or each fix creates new symptoms is not a failed hypothesis — it is
a wrong architecture. STOP and route the architectural question to the dispatcher
/ lead per the playbook's STOP protocol; do not keep fixing symptoms.

## §"Red flags — STOP"

If you catch yourself thinking any of these, STOP and return to Phase 1:

- "Quick fix for now, investigate later."
- "Just try changing X and see if it works."
- "Add several changes at once, then run the tests."
- "Skip the test, I'll verify manually."
- "It's probably X, let me fix that" — proposing a solution before tracing the
  data flow.
- "I don't fully understand it, but this might work."
- "One more fix attempt" — when you've already tried 2+.
- Each fix reveals a new problem in a different place.

## §"Rationalizations"

| Excuse | Reality |
|---|---|
| "Issue is simple, no process needed" | Simple issues have root causes too; the process is fast for them. |
| "Emergency, no time for process" | Systematic is FASTER than guess-and-check thrashing. |
| "Try this first, investigate later" | The first fix sets the pattern — do it right from the start. |
| "I'll write the test after the fix works" | Untested fixes don't stick; the test-first proves it. |
| "Multiple fixes at once saves time" | You can't isolate what worked, and it spawns new bugs. |
| "Reference is long, I'll adapt the pattern" | Partial understanding guarantees bugs — read it completely. |
| "I see the problem, let me fix it" | Seeing the symptom ≠ understanding the root cause. |
| "One more attempt" (after 2+ failures) | 3+ failures = an architectural problem; question the pattern, don't fix again. |

## §"When investigation finds no root cause"

If systematic investigation genuinely shows the issue is environmental,
timing-dependent, or external:

1. You have completed the process — document what you investigated.
2. Choose appropriate handling (retry, timeout, a clear error message) and apply
   or route it per your role's authority — the *choice* of handling is a design
   decision the playbook / lead can own, not this skill's to make.
3. Add monitoring / logging for future investigation.

**But** roughly 95% of "no root cause" conclusions are incomplete investigation —
be honest about which this is.

## What this skill does NOT do

- Does NOT grant permission to run tests, debug, or execute shell commands —
  execution is the invoking role's policy + the permission floor.
- Does NOT replace functional verification of the fix (`verification-completion`).
- Does NOT decide scope, the authority rhythm, or whether to ship past a finding.
- Does NOT apply the fix or route blockers via chat — an architectural STOP is a
  routed artefact to the dispatcher / lead, not a chat aside.
