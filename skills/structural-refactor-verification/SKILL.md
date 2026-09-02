---
name: structural-refactor-verification
description: |
  Execute the verification audit for a pure-structural refactor.
  Covers per-file accessibility audit, pre-test sanity checks (syntax,
  test suite, accessibility, build), mock-then-construct ordering for
  capture-at-init dependencies, and post-refactor import-graph DAG
  confirmation. Worker invokes when the dispatch is a pure-structural
  refactor (file split, component extraction, module reshuffling,
  dependency-injection refactor). Refactor regressions (missing
  imports, lost exports, broken accessibility, DAG cycles created
  by the new structure) are in-scope and the worker fixes them as
  part of the dispatch. Adjacent-surface improvements that pre-existed
  the refactor or are structurally unrelated are out-of-scope and go
  in §"Rejected findings" — surface, do NOT auto-fix.
assumes:
  - |
    PM and Lead roles do not invoke this skill — refactor verification
    is worker-side execution work.
  - |
    The Worker role has two invocation paths: from Claude Code via
    the native Skill tool (see worker-agent.claude.md §"Allowed
    skills"), or from Codex CLI by reading this file via
    functions.exec_command and executing §"Audit procedure" using
    the Codex tool mapping in worker-agent.codex.md §"Allowed
    skills". The audit procedure, authority boundary, and reporting
    shape are platform-agnostic and bind both paths identically.
  - |
    The Reviewer role does NOT invoke this skill. Reviewer reads the
    close-out's verification report; it does not re-run the audit.
  - |
    Schema-CHECK coverage audit is NOT part of this skill — it lives
    in the agent:verification-patterns skill. The rationale:
    schema-CHECK's trigger is data-write paths, not structural changes
    — different triggers, different consumers, would create
    trigger-promiscuity if folded into this skill.
authority-boundary:
  - |
    This skill distinguishes refactor regressions (in-scope, MUST
    FIX) from adjacent-surface improvements (out-of-scope, Rejected
    findings). A finding the structural refactor itself CREATED
    (missing imports between sibling files, lost exports, broken
    accessibility, DAG cycles introduced by the new structure,
    mock-then-construct regressions from re-wired dependencies) is
    in-scope and the worker fixes it as part of this dispatch —
    behavior parity is the refactor's goal. A finding the refactor
    merely SURFACED (pre-existing code-smells, dead exports unrelated
    to moved symbols, "while I'm here" optimizations) is
    out-of-scope and goes in §"Rejected findings". The heuristic:
    "did the refactor create this, or did the refactor surface
    this?" Created → fix; surfaced → Rejected findings. See
    §"Authority boundary" in this skill body for full examples and
    the ambiguous-case rule (route to lead, do NOT default to
    fixing).
  - |
    The scope-discipline rule "preserve byte-identical bodies"
    lives in worker-agent.md, not in this skill. The skill
    references it but does not redefine it. The skill audits;
    the playbook says "do not absorb adjacent fixes."
  - |
    This skill does NOT carry CRITICAL-finding override authority.
    Reviewer-issued CRITICAL findings stay in playbook authority
    (operator-only override per reviewer-agent.md).
---

# structural-refactor-verification

Verification audit for a pure-structural refactor. The two halves of the workflow — pre-refactor coverage gate (Step 0) and post-refactor verification (Steps 1–6) — share one authority boundary, stated once in §"Authority boundary" below: the created-vs-surfaced heuristic that routes every finding.

## What this skill does

Carries the *audit procedure* for a pure-structural refactor: verify that the new file structure preserves behavior parity, that every referenced symbol is reachable from each file that uses it, that the test suite passes after the structural change, that the import graph is a DAG, and that any capture-at-init dependencies are mocked in the correct order. Carries the canonical reporting shape against which the lead reads the verification claims in the close-out. Scope decisions, the "preserve byte-identical bodies" rule, and CRITICAL-finding override authority live in the calling playbook — this skill's §"Other boundary rules" points to their homes — and the verification report never replaces the lead's own read of it against the dispatch's specific refactor brief.

## Authority boundary (read first)

This skill is procedural. It audits + reports; it does NOT decide. But the report-vs-fix distinction is NOT a blanket rule — it depends on whether the finding is a **refactor regression** (in-scope, MUST FIX) or an **adjacent-surface improvement** (out-of-scope, Rejected findings).

### Refactor regressions — IN-SCOPE, MUST FIX

A finding is a refactor regression when the structural change itself **created** it — when applying the refactor diff is what brought the issue into existence. The worker fixes these as part of the refactor dispatch; they are not Rejected findings. (Compare with "surfaced" issues below — the refactor merely revealed something that already existed; those are out-of-scope. The heuristic later in this section formalises the distinction.) Examples of refactor-created regressions:

- **Missing imports between sibling files** that exist because the split left a reference behind. The pre-split file had access to symbol `X` as an internal declaration; the post-split file `b.ts` references `X` but does not `import { X } from './a'`. The refactor caused the bug — the worker fixes it.
- **Lost exports** when a moved symbol was not re-exported from its new location, breaking external callers. The export-surface parity check (Step 5) catches this; fix it.
- **Broken per-file accessibility** for any symbol the pre-refactor file had access to but the post-refactor file does not. Step 3 surfaces this; the fix is to add the missing import / re-export.
- **DAG cycles** introduced by the new file structure (a "shared" module importing from a sibling). Step 4 catches this; the fix is to re-shuffle the import direction so the dependency graph is acyclic.
- **Mock-then-construct regressions** introduced when a refactor changes a captured-at-init dependency's wiring such that existing tests no longer mock in time. Step 2 catches this; the fix is to re-order the test setup.

Behavior parity is the goal of a pure-structural refactor — leaving any of the above uncorrected ships a behavior change. The audit's job is to find them; the worker's job is to fix them inside this dispatch.

### Adjacent-surface improvements — OUT-OF-SCOPE, Rejected findings

A finding is an adjacent-surface improvement when it **pre-existed the refactor** or is **structurally unrelated** to the dispatched change. The worker records these in the close-out's §"Rejected findings" per worker-agent.md §"Rejected findings as required close-out section"; the lead decides whether to dispatch a follow-up. Examples:

- A function in an untouched file has a code-smell the audit happened to notice during the accessibility sweep. Pre-existing; out of scope.
- A dead export in a file the refactor moved but did not split. The export was already dead before the refactor began; surfacing it is useful but fixing it is scope expansion.
- A test fixture in the same directory that has a stale comment, broken assertion against deprecated behavior, etc. Adjacent surface; surface in Rejected findings.
- A "while I'm here" optimization opportunity inside a moved body. Pure-structural refactors do not change behavior — even an obvious optimization is scope expansion; surface it.

The heuristic: **"did the refactor create this, or did the refactor surface this?"** If created → fix; if surfaced → Rejected findings.

### Other boundary rules

- **The "preserve byte-identical bodies" rule stays in worker-agent.md.** It is scope-fence authority, not verification procedure. The skill references it (the audit's purpose is to verify the rule was held) but does not redefine it.
- **The skill does NOT carry CRITICAL-finding override authority.** If the audit reveals a CRITICAL-class issue (including a refactor regression severe enough to be CRITICAL), the worker reports it in the close-out and routes it up via the reviewer or lead per the playbook's escalation discipline. The skill does NOT decide whether to ship past CRITICAL.
- **When in doubt — route to lead, do NOT default to fixing.** Worker-agent.md §"Honest reporting" is explicit: "Scope / boundary uncertainty routes to Lead — always. Reversibility is irrelevant; a reversible scope change is still a scope change." Apply that rule here. If a finding is ambiguous between refactor regression and adjacent-surface improvement, do NOT decide unilaterally. Surface it to lead via close-out's §"Open questions" (or chat-message during the dispatch if the ambiguity blocks progress) and let lead classify. The "did the refactor create this?" heuristic resolves most cases; the genuinely-ambiguous remainder is scope-class uncertainty, not implementation uncertainty, so it routes upward.

## When to invoke

The playbook (`worker-agent.md` §"Refactor-Specific Discipline") gates the entry. This skill applies when the dispatch is a **pure-structural refactor** — i.e., one of:

- **File split:** one source file becomes two or more, with the same exports reachable from the same external surface.
- **Component extraction:** a logical sub-unit (function, class, module-of-functions) is lifted from its host file into its own file, with imports rewired across the original consumers.
- **Module reshuffling:** files move between directories with no behavior change; imports rewrite consistently.
- **Dependency-injection refactor:** a captured-at-init dependency becomes injected (the global-capture pattern that motivates the mock-then-construct rule below); behavior preserved, structure changed.

"Pure-structural" means **behavior preservation is the goal**. If the refactor changes behavior (renames a column, tweaks fallback logic, introduces a new code path), it is NOT pure-structural and this skill does NOT apply — see worker-agent.md §"Contract preservation" for the behavior-preservation rules in that case.

## Audit procedure

Run in this order. Numbered steps are sequential; bullets within a step are conjunctive (do all of them). **Step 0 runs BEFORE the structural change** (it captures the pre-refactor baseline); Steps 1–6 run after.

### Step 0 — Existing test coverage audit (pre-refactor)

Run this BEFORE making any structural change. Audit what's already tested and what isn't:

- List the test files that exercise the pre-refactor file(s) being changed.
- For each, capture the pass/fail state of the test suite NOW (before the refactor).
- If coverage is thin in the area being refactored, **STOP** before proceeding with the structural change and ask the lead for the baseline-test decision. **Route the ask the way a bounce is routed** (`agent:routed-comms` §"Bounce-back as a routing mechanic"): when the lead is a routed (idle) session, publish a `clarification` record addressed to it (`coordination.publish_artefact {kind:"clarification", to:<lead-slug>, body:…}`) and `coordination.deliver` its returned id, or the lead is never woken and the wait below never ends — a chat-only ask reaches whoever is at the keyboard, not an idle dispatcher. An operator-direct dispatcher present in chat may be asked in chat. Propose the baseline-test scope; do NOT aim for "full coverage" — just enough that Step 1.2 (post-refactor test suite) has a meaningful parity claim to make. Wait for the lead's response before touching the structural surface.

If the dispatch already named a baseline test as a prereq, this step verifies it landed and passes — no STOP required. If not and coverage is thin, the STOP is mandatory: a close-out written AFTER the refactor delivers the lead's baseline-test decision too late to act on; the parity claim would be ungrounded. The STOP is what makes Step 0 a real pre-refactor gate, not a retroactive note.

The output of Step 0 becomes the parity benchmark Step 1.2 measures against: "the tests that existed and passed before the refactor still pass after." Without Step 0, that claim has no grounding.

### Step 1 — Pre-test sanity checks (post-refactor)

For structural refactors, run in this order. Each step is faster than the next; doing them in order catches the cheap errors before the expensive ones.

1. **Syntax check** each new file (`node --check`, `python -c "import x"`, equivalent for the language). Catches off-by-one slice errors and orphan braces in seconds.
2. **Test suite** (`npm test`, `cargo test`, equivalent). Includes any export-integrity baseline added before the refactor.
3. **Per-file accessibility audit** (script or `grep` sweep). Catches runtime ReferenceErrors that the test suite misses if the failing function isn't exercised. See Step 3 below for the audit shape.
4. **Production build** (`npm run build`, equivalent) for frontend codebases without a test framework, or when the project's test framework doesn't resolve every import. Catches both syntax errors and missing imports.

Step 1 catches what Step 2 would catch, faster. Step 3 catches what 1–2 cannot. Step 4 is the safety net when no test framework is configured.

### Step 2 — Mock-then-construct order for capture-at-init dependencies

The general rule lives in `worker-agent.md` §"Mock-then-construct order in tests" (it applies to all test work, not only refactors). Re-read it; this step applies the rule to the refactor-specific case where a captured-at-init dependency's wiring just changed.

**Refactor-specific application:** when the refactor rewires a captured-at-init dependency (e.g., the dependency moves from being constructed inline to being injected via a factory, or vice versa, or moves between files such that the import order in existing tests now differs), existing mock-then-construct setups may no longer apply in the correct order. Re-audit every test that mocks the affected dependency:

- If the dependency is still capture-at-init in its new wiring, confirm the test still mocks BEFORE the construct/import.
- If the refactor converted the dependency to a call-time lookup, the mock-then-construct discipline is no longer required for the new wiring — the test can be simplified (though doing so is a behavior-adjacent change and goes in §"Rejected findings", not auto-cleanup).
- If the refactor breaks an existing test's mock-then-construct ordering (the test was mocking correctly before; the new wiring captures earlier than the test's setup runs), that's a refactor regression per §"Authority boundary" — fix it inside the dispatch by re-ordering the test setup.

The conditional gate from the general rule (capture-at-init only; call-time lookups don't need it) still applies; do NOT over-extend mock-then-construct to tests that don't have a capture-at-init dependency.

### Step 3 — Per-file accessibility audit (post-refactor)

For every name the pre-split file had access to (its internal declarations + its external imports), check per new file: is the symbol declared in this file, imported into this file, or re-exported from this file? If a file references a symbol without one of those three, it's a regression waiting.

**The unified module-system mental model.** Once a file is split into multiple files, every name needs to be either declared locally or imported. There is no real "internal" vs "external" distinction. A symbol declared in the new "shared" file is no more available to a sibling file than a symbol declared in a third-party dependency.

**Audit shape per file:**

- List every identifier referenced in the file body that is not a local binding (function parameter, local variable, loop variable).
- **Exclude ambient/runtime globals** before the missing-import check: JS/TS runtime names like `console`, `window`, `document`, `globalThis`, `Promise`, `Array`, `Object`, `Symbol`, `process`, `Buffer`, JSX runtime names; Python builtins like `print`, `len`, `range`, `isinstance`, `dict`, `list`; any identifier the project's ambient-type declarations (`*.d.ts`, `__builtins__`, etc.) provide. These remain accessible after a split without an import; flagging them is a false positive that would push the worker to add bogus imports. The audit targets identifiers that came from pre-refactor internal declarations or explicit external imports — those are the ones a split can leave behind.
- For each remaining identifier: is it declared in this file? Imported into this file? Re-exported from this file?
- Any identifier that fails all three is a missing-import bug.

**Pattern recognition: same-tree-different-file ReferenceErrors.** Module A exports X. Module B references X. If B doesn't `import { X }`, it's a runtime error when B's relevant function is called. The split looks fine at module-load time; it fails on first invocation. Public-API tests don't catch this — they only check the export surface, not the internal references.

**Sub-rule: per-file vs tree-wide audit collapse.** When sweeping for unresolved symbols, asking "is this declared anywhere in the new tree?" is structurally incapable of detecting missing imports between sibling files. The right question is "is this accessible from the file that uses it?" — meaning declared-in, imported-into, or re-exported-from that file. Audit at the file level, not the tree level.

### Step 4 — Post-refactor import-graph DAG verification

The post-refactor import graph MUST be acyclic. Layered DAGs are valid — `consumer → service → shared` is fine; `consumer → service → consumer` is a cycle. Forbid cycles, not all chains. If the refactor designates a base-layer module (a `shared` file the other files depend on), additionally forbid that base-layer file from importing any sibling — its inbound edges only make a cycle possible if it also has outbound edges.

Run this search to surface all relative same-directory dependency edges inside the new directory, then inspect the matches against the layering you intend:

```bash
# Find every dependency edge that can participate in a cycle inside the
# refactor's surface. For a same-directory split these are `./...` edges;
# for a module reshuffle that nests files into subdirectories, edges also
# appear via `../...` or deeper relative paths AND via project-alias
# imports if the project's tsconfig/jsconfig defines them (e.g.,
# `@app/foo`). Run all four patterns and inspect the union; restricting
# to `./` alone misses cross-directory cycles a reshuffle can introduce.
grep -rnE "(^|[^a-zA-Z_])(import|export) .*['\"](\\.\\.?/)" <refactor-surface>
grep -rnE "^import ['\"](\\.\\.?/)" <refactor-surface>     # bare side-effect imports, ./ or ../
grep -rnE "from ['\"](\\.\\.?/)" <refactor-surface>        # backstop — multi-line imports where path is on its own line
grep -rnE "from ['\"]@" <refactor-surface>                 # project-alias imports (adjust @ to the project's alias prefix)
```

Where `<refactor-surface>` is the full set of directories the refactor touched, not just the immediate new directory — a reshuffle can move files across directories, and cycles can form through `../` edges.

(The patterns above target JS/TS; other languages use the same principle — find every dependency edge that can participate in a cycle inside the refactor's surface, including cross-directory, aliased, and package-level forms, and walk them for cycles. Per-language patterns: §"Appendix — DAG-scan language variants".)

A hit IN a designated base-layer file (one the refactor declared as `shared`/`core`/equivalent) means the file is no longer a pure base layer — there is a sibling edge that risks a cycle. For non-base-layer files, sibling edges are fine as long as the resulting graph has no cycles. Layered chains like `consumer → service → shared` are valid; the rule is acyclicity, not "no inbound + outbound on the same node."

**Cycle detection:** if the new directory has N files, build the import-edge list (each `<file> → <same-dir-import>` from the grep above is one edge) and walk it for cycles. For N ≤ ~10, walking by hand surfaces back-edges quickly; for N > ~10, use a real DAG-check tool (e.g., `madge --circular` for JS/TS, `pydeps --show-cycles` for Python). Manual walking gets unreliable past that size.

### Step 5 — Public-API export-surface check

**Public-API tests are necessary but not sufficient.** Pinning the export surface catches "lost an export" at module-load time. It does NOT catch runtime errors from function bodies referencing symbols that aren't imported into the new file (Step 3 covers that). Plan for both.

The export-surface check compares **only the original public entrypoint(s)** (the file or barrel that external callers import from) — NOT the union of every new internal file the split created. File splits routinely introduce internal exports between sibling modules so the split files can import from each other; those internal exports are part of the refactor, not API drift. The parity claim is "external callers see the same surface."

Concretely:

- Identify the pre-refactor public entrypoint(s): the file(s) external callers were importing from. For a file-split refactor of `a.ts` into `a.ts + helpers.ts`, `a.ts` is the entrypoint; `helpers.ts` is internal.
- Compare exports from the pre-refactor entrypoint against exports from the post-refactor entrypoint. The set should be byte-identical (same names, same types, same default-vs-named convention).
- **Drift on the public entrypoint caused by the refactor itself** (a moved symbol that did not get re-exported from the entrypoint, a renamed export the dispatch did not authorize, a default-vs-named convention flip) is a refactor regression — fix it inline per §"Authority boundary". The lost re-export is the canonical case: the refactor moved `X` from `a.ts` to `helpers.ts` but `a.ts` no longer re-exports `X`, breaking external `import { X } from './a'` callers. Restore the re-export (or update consumers if the dispatch authorized that), then re-run Step 5.
- **New internal exports on non-entrypoint files** are expected (the split needs them); these are NOT drift and do not enter Step 5's comparison.
- **Drift that is genuinely ambiguous** (an entrypoint export the worker isn't sure was intentional behavior change vs accidental refactor side-effect) goes in close-out's §"Open questions" per §"Honest reporting" scope-uncertainty-routes-to-lead rule. Reserve open-questions for the ambiguous case; do NOT default to open-questions for clear refactor-introduced entrypoint drift.

### Step 6 — Byte-identical body confirmation

Spot-check: a pure-structural refactor moves code; it doesn't rename columns, tweak fallback logic, or "improve while we're here." If during the audit you find a real improvement, **surface it as a follow-up** in §"Rejected findings", per the authority boundary above.

The byte-identity check is informal — the audit doesn't run a diff against the pre-refactor state automatically (that's the lead's review surface against the dispatch). The worker's discipline is to not silently introduce body changes during a pure-structural refactor; the audit's role is to confirm the changes the worker made are exclusively structural.

## Reporting shape

The verification close-out (per worker-agent.md §"How to Report at a Gate" + §"PASS/FAIL Distinct from Semantic Match") must include the audit's outputs. Numbers, not adjectives.

```
## Verification claim

Tests: <N/N passing in M ms>
Files audited: <list>
Per-file accessibility audit: <PASS / FAIL + which files have which missing imports>
Import-graph DAG: <confirmed / cycle found at <edge>>
Export-surface parity vs pre-refactor: <byte-identical / drift in <names>>
Byte-identical bodies: <confirmed / drift surfaced in §"Rejected findings">
Mock-then-construct (if applicable): <applied to <deps> / not applicable (no capture-at-init dependencies)>
Build (if no test framework or as safety net): <PASS / output excerpt>

## What question this audit asked
"Does the post-refactor file structure preserve behavior parity with the pre-refactor state?"

## What this audit cannot catch
- Behavior changes hidden inside byte-identical bodies (impossible without behavioral tests)
- Test-coverage gaps in the pre-refactor state (the audit only verifies what was tested still passes)
- Cross-file refactors that touched both src/ and test fixtures (audit per-file; cross-file consistency surfaces via test-suite step)

## Rejected findings (per worker-agent.md §"Rejected findings as required close-out section")
- <each adjacent-surface temptation the audit revealed but the worker did NOT fix, per the findings-not-fixes obligation>
```

The "What this audit cannot catch" section is the pre-mortem for the verification claim. The "Rejected findings" section is the discipline-signature that the worker held the scope-fence under the audit's provocations.

## Common failure patterns

Route each finding per the §"Authority boundary" heuristic (created → fix inline; surfaced → Rejected findings). The default routing per pattern below names the typical case; the same pattern can be created or surfaced depending on what the dispatched diff did.

- **Missing public-export keyword after split** (typically refactor-created → FIX INLINE). Internal helpers (no export keyword) need the keyword added when domain files start importing them. If the split is the reason the helper is now consumed across files, adding the export is part of the refactor.
- **Same-tree-different-file ReferenceErrors** (typically refactor-created → FIX INLINE). Module A exports X; module B references it. If B doesn't `import { X }`, it's a runtime error on first invocation. Public-API tests don't catch this. If the refactor moved X into A (and B used to have direct access), adding the import to B is part of the refactor.
- **Off-by-one in slice ranges** (refactor-created → FIX INLINE). When extracting line ranges, the closing brace may be on the line *after* what you'd expect. Syntax-check (Step 1.1) catches the resulting orphans; fix the slice before claiming verification.
- **Per-file vs tree-wide audit collapse** (audit-procedure trap, not a finding class — restated here because it's the canonical refactor-verification mistake; see Step 3 sub-rule).
- **Sync→async wrappers** (judgment-dependent — usually surfaced, not created by a pure-structural refactor). Wrapping a sync export with an async toolkit silently breaks every caller that doesn't await. Check call-site await usage. If the refactor introduced the async wrapper, that's a behavior change — NOT pure-structural; surface to lead. If the wrapper pre-existed, surface in §"Rejected findings".
- **URL-encoding assumptions** (typically surfaced, not created — §"Rejected findings"). Toolkits often encode internally. Don't pre-encode if the toolkit does. If the audit notices this during the verification sweep, it's adjacent surface unless the refactor itself introduced the double-encoding.

## Platform-specific tool selection

**Claude Code:** see `worker-agent.claude.md` §"One-Shot Transformation Scripts" for the inline-Bash-first pattern when deterministic line-range slicing is needed during the refactor itself (note: that's refactor execution, not verification — but the audit's syntax-check and accessibility-audit steps benefit from the same inline-Bash approach because the harness verifier sees the full transformation).

**Codex CLI:** see `worker-agent.codex.md` §"Allowed skills" + §"Tool affordances" for the `functions.exec_command` invocation pattern. The audit's steps map directly: syntax-check via `node --check`, test suite via the project's test runner, accessibility audit via `grep -rn`, build via the project's build command.

## Appendix — DAG-scan language variants

Per-language patterns for Step 4's cycle-edge scan (the JS/TS patterns are canonical in §"Step 4 — Post-refactor import-graph DAG verification" itself):

- **Python** — two patterns are needed: `from \\.\\.?[a-zA-Z_]` catches `from .x import ...` / `from ..util import ...`, but it MISSES the package-level form `from . import sibling` / `from .. import util` because there's no identifier directly after the dots; add `from \\.\\.?\\s+import\\s` to cover that.
- **Rust** — look for `use crate::`, `use super::`, and `use self::` (intra-crate edges).
