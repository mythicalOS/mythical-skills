---
name: verification-patterns
description: |
  Catalogue of rare verification audit procedures the worker would
  otherwise improvise. Each pattern has its own trigger and procedure;
  invoke at the pattern's sub-section. Currently contains: schema-CHECK
  coverage audit (enumerate accepted values, search write-call sites,
  cross-reference, report the coverage matrix). The skill produces
  observability data — it REPORTS findings; it does NOT auto-fix
  discovered gaps. Coverage gaps go in the close-out's matrix and
  open-questions; the lead decides whether each gap is intentional or
  warrants a follow-up dispatch.
assumes:
  - |
    PM and Lead roles do not invoke this skill — verification audits
    are worker-side execution work.
  - |
    The Worker role has two invocation paths: from Claude Code via
    the native Skill tool (see worker-agent.claude.md §"Allowed
    skills"), or from Codex CLI by reading this file via
    functions.exec_command and executing the relevant pattern's
    sub-procedure using the Codex tool mapping in worker-agent.codex.md
    §"Allowed skills". The pattern procedures, authority boundary,
    and reporting shape are platform-agnostic and bind both paths
    identically.
  - |
    The Reviewer role does NOT invoke this skill. Reviewer reads the
    close-out's coverage matrix as evidence; it does not re-run the
    audit.
  - |
    Other verification patterns currently live in worker-agent.md:
    the schema-accepts-vs-write-path-emits QUALITY rule
    (§"Verification-Question Discipline"); mock-then-construct order
    (general test rule); structural-refactor verification (its own
    skill at agent:structural-refactor-verification). This skill is
    the home for RARE patterns the worker would otherwise improvise.
    High-frequency rules stay general in worker-agent.md.
authority-boundary:
  - |
    This skill is REPORT-ONLY. Every pattern's procedure ENDS at
    populating the close-out's coverage matrix (or equivalent
    structured output for non-schema patterns) and surfacing
    ambiguous entries in §"Open questions". The worker does NOT
    auto-fix discovered gaps even when the fix looks obvious — gaps
    are observability data, not implementation work. The lead reads
    the matrix and decides whether each gap is intentional (annotate
    with justification) or warrants a follow-up dispatch (add a
    write-path; revise the schema; flag for re-design).
  - |
    The worker does NOT scope-expand to add missing write-paths,
    revise schema CHECK clauses, or alter any code outside the
    audit's strict reporting surface during the audit dispatch. A
    schema-accepted value with zero write-paths might be intentional
    (legacy soft-deprecation, future-use placeholder, error-class
    edge case that the test suite cannot exercise). Adding a
    write-path requires business-logic context the audit data alone
    does not provide.
  - |
    This skill does NOT carry CRITICAL-finding override authority.
    If the audit reveals a CRITICAL-class issue (a schema-accepted
    value that maps to a security-relevant flow with no emission
    path, or similar), the worker reports it in the close-out and
    routes upward via the playbook's escalation discipline. The
    skill does NOT decide whether to ship past CRITICAL.
---

# verification-patterns

Catalogue of rare verification audit procedures. Each pattern is self-contained: trigger, procedure, reporting shape.

## Scope and boundary

REPORT-ONLY, uniformly across every pattern — stated once here, normatively in the frontmatter authority-boundary block: the audit ends at the coverage matrix + §"Open questions"; the worker never auto-fixes a discovered gap (not even an "obvious" one — the fix needs business-logic context the audit data does not provide); CRITICAL-class findings route upward via the playbook's escalation discipline, never shipped past by this skill. Two operative specifics beyond that block:

- **The lead's per-gap disposition vocabulary.** For each matrix gap the lead annotates one of: **Intentional** (known soft-deprecation, future-use placeholder, edge case the suite cannot exercise — annotate `intentionally-unused ✓` with a verifiable justification) or **Oversight** (warrants a follow-up dispatch with its own scope — add write-path, revise CHECK clause, re-design schema — never absorbed into the audit dispatch).
- **What produces the data vs who reads it.** The skill's job is to make the audit deterministic and faithful; the lead's job is to read the output against the dispatch's context and decide what each gap means. High-frequency general verification rules stay in `worker-agent.md`; this catalogue hosts only the rare patterns.

## Pattern catalogue

Currently one pattern. The skill is named `verification-patterns` (plural) to signal it can grow — future rare verification patterns belong here rather than each warranting its own skill, provided their trigger fits "rare verification work the worker would otherwise improvise."

A pattern belongs in this skill when ALL of:

- The trigger is rare (worker invokes it in a small fraction of dispatches; not most-dispatches general).
- The procedure is deterministic enough to script + recipe + matrix-format.
- The output is observability data the lead reads as evidence, not implementation work the worker carries through to fix.

A candidate that fails any of those criteria belongs elsewhere: high-frequency general rules stay in `worker-agent.md`; refactor-execution audit lives in `agent:structural-refactor-verification`; coordination procedure lives in `agent:coordination-wip-handoff`.

---

### Schema-CHECK coverage audit

**When to invoke.** The dispatch touches a database schema's CHECK constraint that accepts an enum (or any constrained set), OR touches a write path that feeds a schema-CHECK-bearing column. The playbook (`worker-agent.md` §"Schema-CHECK coverage audit") gates the entry; this section carries the procedure.

The pairing rule from `worker-agent.md` §"Verification-Question Discipline" → "Schema-accepts vs write-path-emits sub-class" is the WHY: schema acceptance and write-path emission are two independent verification questions; CHECK extensions repeatedly ship with one face verified and the other unverified. The coverage matrix is the canonical artefact that closes both faces in one pass.

**Audit procedure (platform-agnostic):**

1. **Enumerate accepted values from the CHECK clause.** Read the schema file for the CHECK constraint definition. For an enum-style constraint (`CHECK (col IN ('a', 'b', 'c'))`) the accepted values are explicit. For a regex or range constraint, enumerate the realistic emission set (not the theoretical set — `LIKE '%@%'` accepts infinitely many strings; the audit cares about which strings production code actually emits).
2. **For each accepted value, find write-call sites that emit it.** Search the codebase for the value's literal representation at the relevant column's write surface. Note the call-site count per value.
3. **Cross-reference.** Build the coverage matrix:
   - **Schema-accepted ✓ + write-paths-emit ✓ (count ≥ 1):** the value is reachable and the audit accepts.
   - **Schema-accepted ✓ + write-paths-emit ✗ (count = 0):** silent observability gap — record in matrix, surface in §"Open questions" with the explicit ambiguity ("is this value's silence intentional, or an oversight?").
   - **Schema-rejected + write-paths-emit ✓:** production code tries to emit a value the schema doesn't accept — this is a hard bug surfaced by the audit. **Do NOT fix it during the audit dispatch** (the report-only authority boundary applies; extending the CHECK or stopping the emission is a separate scope decision the lead must authorize). Record the finding in the coverage matrix AND surface it as CRITICAL-class in §"Open questions" with the specific value, the write-call site(s), and the schema constraint. The lead routes it for follow-up. The exception: if the dispatch brief EXPLICITLY authorizes the fix (e.g., "this audit doubles as a hardening pass — fix any schema-rejected emissions you find inline"), the worker may fix it within that explicit authorization; without that authorization, the audit's job ends at surfacing.
   - **Schema-accepted ✓ + intentionally-unused ✓:** annotate with the justification the worker can verify (legacy soft-deprecation, future-use placeholder reserved by an upcoming feature, error-class case that fires only under conditions the test suite can't exercise). The justification must be verifiable — "looks unused" is not a justification.

**Reporting shape — the coverage matrix.** Include in the close-out:

```
## Schema-CHECK coverage audit

Schema: <file:line>
Column: <table.column>
CHECK clause: <verbatim>

| Value | Schema-accepts | Write-paths-emit | Intentionally-unused | Justification |
|---|---|---|---|---|
| <v1> | ✓ | ✓ (N sites) |  |  |
| <v2> | ✓ | ✗ |  | <intentional? oversight? — surface in Open questions> |
| <v3> | ✓ | ✓ (N sites) | ✓ | <verifiable reason> |

## Audit's question
"Schema accepts {v1, ..., vN}; for each, does production code emit it under at least one realistic flow?"

## What this audit cannot catch
- Values emitted via dynamic dispatch (constructed strings, computed enum names) that grep cannot trace
- Test-only write-paths that don't reflect production traffic
- Write-paths in code paths that exist but are unreachable from current entry points
```

**Platform-specific tool selection.**

**Claude Code:** `Bash` + `grep -rn`:

```bash
# 1. Enumerate accepted values from the CHECK clause
grep -nE "CHECK \\(.* IN \\(" <schema-file> | head -5

# 2. Enumerate write-call sites for each accepted value
for v in <value1> <value2> ... <valueN>; do
    echo "=== $v ===" ; grep -rn "<column-name>.*['\"]${v}['\"]" --include='*.<ext>' src/ ;
done

# 3. Cross-reference: values in step 1 with zero matches in step 2?
```

Adjust the file extension (`*.ts`, `*.py`, etc.) and the column-name pattern to the project's conventions. The grep pattern uses string-literal quoting; for codebases that build the value programmatically (e.g., `EVENT_TYPES.FOO`), add a secondary grep over the constant name.

**Codex CLI:** `functions.exec_command` with the same `grep -rn` invocations (Codex's sandbox typically has grep/rg available). For the per-value loop, use a Codex multi-step exec rather than an inline shell loop if the tool's loop semantics are unreliable. The matrix population goes into the close-out record body (composed in-session, then published via `coordination.publish_artefact {kind:"closeout", to:<recipient>, body:…}`).

**Common audit-blind-spots (surface in §"What this audit cannot catch"):**

- **Dynamic dispatch.** A value constructed at runtime from configuration, env vars, or computed enum names won't show up in a literal-string grep. If the codebase uses any of these patterns, the audit's coverage claim is a lower bound, not an upper bound.
- **Test-only writes.** A write-call site that exists only in test fixtures doesn't reflect production reachability. The audit should distinguish src/ from test/ when counting call sites.
- **Unreachable code paths.** A write-call site exists in code that is no longer reached from any entry point. The audit can't prove reachability without dead-code analysis; surface as a sub-bullet of "what this audit cannot catch" when the count includes suspicious files.
