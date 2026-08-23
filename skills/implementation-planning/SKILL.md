---
name: implementation-planning
description: |
  How to write an implementation plan at the dispatch altitude — the
  bite-sized, file-mapped, TDD-stepped plan for building one already-scoped
  unit of work, used to shape a dispatch brief or to structure a worker's
  execution of a large dispatch. Covers file-structure mapping, task
  right-sizing to a reviewable gate unit, interface contracts between
  tasks, no-placeholder discipline, and the self-review pass. Procedural
  only: WHAT gets built and its priority are the PM's scope decision (this
  is NOT a product master plan — `agent:pm-master-plan-template` owns that); the
  dispatch decision is the lead's. This skill is the HOW of planning a
  build, not the authority to scope it.
assumes:
  - |
    The plan sits BELOW the master plan: it builds one already-scoped
    unit, it does not decide product scope or phase ordering (those are
    the PM's, `agent:pm-master-plan-template`). It feeds a lead's task brief or
    a worker's execution (`plan-execution`); it does not duplicate the
    task-brief contract.
  - |
    Claude Code roles author the plan via the native edit tools; Codex
    roles via `functions.apply_patch`. The right-sizing, interface-block,
    no-placeholder, and self-review discipline is platform-agnostic.
---

# implementation-planning

The procedure for writing an implementation plan for **one already-scoped unit of
work** — the level a dispatch brief carries or a worker structures before a large
build. Write it for an engineer who is skilled but has zero context for this
codebase: exact file paths, complete code in every step, exact commands with
expected output, bite-sized tasks. DRY, YAGNI, TDD, frequent commits.

This is **not** a product master plan. Product scope, feature priority, and phase
ordering are the PM's decision and live in the master plan
(`agent:pm-master-plan-template`). This plan executes *within* that scope.

## Authority boundary (read first)

- **Scope is decided upstream.** The PM owns what-gets-built and priority; the
  lead owns the dispatch decision and the brief's scope boundary. This skill
  structures the HOW of an already-scoped unit — it does not expand or re-decide
  scope. A discovered scope gap is surfaced (scope-discovery), not planned-in.
- **Decomposition that crosses the dispatch boundary routes up.** If the unit is
  really several independent subsystems, that is a scope/sequencing decision for
  the PM/lead — surface it, do not silently split it into a multi-subsystem plan.

## §"Scope check — is this one dispatch?"

Before planning, confirm the unit is one coherent, independently-buildable piece.
If it spans multiple independent subsystems, it should have been decomposed at
scope time — surface that to the dispatcher rather than writing a sprawling plan.
Each plan should produce working, testable software on its own.

## §"File structure + task right-sizing"

Map the files first, then draw task boundaries:

- **File map.** List every file created or modified and its single
  responsibility. Files that change together live together; split by
  responsibility, not by technical layer. Prefer small, focused files. In an
  existing codebase, follow established patterns.
- **Task right-sizing.** A task is the smallest unit that carries its own test
  cycle and is worth a fresh reviewer's gate. Fold setup, config, scaffolding, and
  docs into the task whose deliverable needs them; split only where a gate role
  could meaningfully accept one task while rejecting its neighbour. Each task ends
  with an independently testable deliverable — the natural unit a gate reviews
  against the branch SHA.

## §"Bite-sized steps"

Each step is one action (a couple of minutes):

- Write the failing test → run it (confirm it fails) → implement minimally → run
  it (confirm it passes) → commit.

## §"Plan header + task template"

Start the plan with a header carrying goal, approach, tech, and the global
constraints copied verbatim from the scope source (version floors, dependency
limits, naming/copy rules — every task implicitly includes these). Then one block
per task:

````markdown
### Task N: [Component]

**Files:**
- Create: `exact/path/to/file.ext`
- Modify: `exact/path/to/existing.ext:120-145`
- Test:   `tests/exact/path/to/test.ext`

**Interfaces:**
- Consumes: [exact signatures this task uses from earlier tasks]
- Produces: [exact names + parameter/return types later tasks rely on — the
  only way a task's implementer learns neighbouring tasks' symbols]

- [ ] **Step 1: Write the failing test**  ```<code>```
- [ ] **Step 2: Run it — expect FAIL** (`<command>` → expected failure)
- [ ] **Step 3: Minimal implementation**  ```<code>```
- [ ] **Step 4: Run it — expect PASS** (`<command>` → PASS)
- [ ] **Step 5: Commit** (`git add <paths> && git commit -m "<msg>"`)
````

## §"No placeholders"

Every step contains the actual content the engineer needs. These are plan
failures — never write them:

- "TBD" / "TODO" / "implement later" / "fill in details".
- "Add appropriate error handling" / "add validation" / "handle edge cases".
- "Write tests for the above" without the test code.
- "Similar to Task N" — repeat the code (tasks may be read out of order).
- A reference to a type/function/method defined in no task.

## §"Self-review"

After writing the full plan, read it against the scope source with fresh eyes (a
checklist you run yourself, not a dispatch):

1. **Coverage** — point each scoped requirement to a task; list gaps and add the
   missing task.
2. **Placeholder scan** — search for the failures above; fix inline.
3. **Type/symbol consistency** — a name defined in Task 3 and used differently in
   Task 7 is a bug; reconcile.

Fix issues inline; the checklist itself needs no re-run.

**The checklist is the floor, not necessarily the terminal gate.** Whether the
plan then gets an *independent* pass is the invoking playbook's call, not this
skill's: when that playbook's §"Cross-model validation of load-bearing output"
classifies the plan as load-bearing, run the pass per
`agent:cross-model-review` after the checklist and fold findings in before the
handoff — that skill resolves the deployment's configured review binding itself
(the `review mode:` bootstrap line: the cross-model CLI, or the fresh-context
ephemeral reviewer). A role whose playbook has no such section keeps the
self-review floor plus its own review gates. This skill decides neither the
depth nor the mechanism.

## §"Handoff"

The completed plan feeds the dispatch, not a single-agent execution choice: it
becomes (or attaches to) the lead's task brief, and the dispatched session
executes it via `plan-execution` in its isolated worktree + branch. Do not append
an interactive "which execution mode?" offer — the framework distributes
execution across the dispatch model.

## What this skill does NOT do

- Does NOT decide product scope, priority, or phase ordering (PM;
  `agent:pm-master-plan-template`).
- Does NOT author the dispatch brief or its routing (the lead's task brief +
  `agent:routed-comms`).
- Does NOT execute the plan (`plan-execution`).
