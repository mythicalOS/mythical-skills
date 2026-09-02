---
name: coordination-parallel-dispatch
description: |
  How to structure parallel build work as independent dispatched agent
  sessions — partition the work into conflict-disjoint units, shape one
  self-contained task brief per unit, fan them out as routed dispatches
  (each woken by a `coordination.deliver` wake and isolated in
  its own worktree + feature branch), and integrate the results at the
  lead's merge gate. Procedural only: WHETHER to parallelize and WHO to
  dispatch are the dispatching role's decision (`ROLES.md` — worker
  dispatch is the lead's); this skill is the HOW of the fan-out, not the
  authority to launch it.
assumes:
  - |
    The concurrency unit is a DISPATCHED AGENT SESSION with its own
    isolated worktree + feature branch (`worktree-management`,
    `branch-lifecycle`), woken by a `coordination.deliver` wake — NOT an
    ephemeral in-process subagent. Per-session isolation is by
    construction (separate index + HEAD per worktree), which is why the
    framework's model is parallel-by-default for build work; the decision
    to fan out a given batch remains the dispatcher's, not this skill's.
  - |
    Both lanes route + wake via the same `coordination.*` MCP tools
    (`publish_artefact` for the brief + `deliver` for the wake). The
    dispatch-brief shape, the recipient token, and the wake step are
    platform-agnostic. The isolation mechanics are owned by
    `worktree-management` / `branch-lifecycle` and are referenced, not
    duplicated.
---

# coordination-parallel-dispatch

The procedure for running multiple independent units of build work concurrently
as separately-dispatched agent sessions. Each unit is a full session in its own
worktree on its own feature branch, reached by a routed brief and a
`coordination.deliver` wake — not an in-process subagent inheriting your context. The isolation that makes the
fan-out safe is `worktree-management` + `branch-lifecycle`; this skill is how to
partition, brief, fan out, and reconverge.

## Authority boundary (read first)

This skill is the mechanics of the fan-out, executed within decisions already
made.

- **The decision to parallelize, and the choice of which sessions to dispatch, is
  the dispatching role's** (worker dispatch is the lead's, per `ROLES.md`
  §"Cross-role boundary table"). This skill does not authorize launching agents
  or spawning sessions — it structures work the authority-holder has decided to
  fan out. New agent-session spawns are themselves a reserved action.
- **Integration is owned, not implicit.** The consolidated result of several
  parallel branches lands at the lead's **merge gate** — the one serialized seam.
  This skill routes work *to* that seam; it does not perform the merge
  (`branch-lifecycle` §"Merge to main").

## §"Identify independent units"

Partition the work so each unit can be built without context from the others.
Group by conflict-disjointness, not by convenience:

- **Disjoint surfaces** — different files / modules / subsystems, no shared write
  target.
- **No shared state** — neither unit needs the other's in-flight result to start.
- **Independently reviewable** — a gate role could accept one unit while rejecting
  its neighbour.

If two units would edit the same surface or one depends on the other's output,
they are **not** independent — sequence them, or fold them into one dispatch.
(With per-session worktrees the index/HEAD-collision class is dissolved by
construction; the remaining coupling to test for is *logical* — shared files and
data dependencies, not the shared checkout.)

## §"Shape each dispatch brief"

Each unit gets one self-contained task brief — the dispatched session never
inherits your conversation. A good brief is:

- **Scoped** — one clear surface, with the in/out-of-scope boundary explicit.
- **Self-contained** — all context the session needs to understand the unit
  (requirements, the relevant paths, constraints), constructed for it, not assumed
  from your history.
- **Branch-conventioned** — states the branch naming convention
  (`feat/<issue-id>-<slug>`, the agent names + creates + reports it) rather than a
  pre-named branch or a worktree path (`branch-lifecycle` §"Create and name the
  branch").
- **Authority-rhythm-echoed** — carries the dispatch's rhythm so the session knows
  when its branch-publication / close-out gates (`ROLES.md` §"Authority rhythms").
- **Explicit about output** — the close-out shape, including the required
  `Branch: <name> @ <SHA>` field the merge gate consumes.

## §"Fan out with per-session isolation"

Dispatch the units concurrently. Each dispatch is a routed brief plus a wake:

- Publish the task brief as a coordination record
  (`coordination.publish_artefact {kind:"task", to:<recipient>, body:…}`) and wake
  the session with `coordination.deliver` carrying the returned id — the published
  record alone wakes no one (`agent:routed-comms`).
- Each dispatched session works in its own worktree under `$AGENT_WORKTREE_PATH`
  on its own feature branch (`worktree-management`, `branch-lifecycle`) and
  publishes that branch with `git.push_branch` when its rhythm permits — a
  dispatched session never lands anything itself. Isolation is by construction;
  the sessions do not share an index or a `HEAD`, so they cannot corrupt each
  other's git state.

## §"Integrate at the merge gate"

Parallel units reconverge at the lead's serialized merge gate, not in any single
session's working tree:

1. Each session reports its branch + SHA in its close-out.
2. Gate roles review each branch against its cited SHA (`branch-lifecycle`
   §"Gate-role review against the cited SHA").
3. The lead verifies readiness and requests the landings one at a time with the
   lead-only `git.request_landing` (`branch-lifecycle` §"Merge to main"); the
   daemon performs each one. For ≥2 separately-floored branches landing together,
   the lead runs a `merge-tree` dry-run for surprise conflicts and is the owner of
   the consolidated integration surface.

If parallel units turn out to share a surface after all (a merge conflict the
partition missed), that is a partition error — surface it to the dispatcher
rather than silently resolving cross-unit conflicts inside one session.

## Common mistakes

| Mistake | Fix |
|---|---|
| Treating the units as in-process subagents | They are dispatched sessions — routed brief + `coordination.deliver` wake + own worktree |
| Brief assumes your conversation context | Construct self-contained context per unit |
| Pre-naming the branch / a worktree path in the brief | State the naming convention; the session names + reports the branch |
| Partitioning by file *layer* not by conflict | Disjoint write surfaces + no shared state; else sequence |
| Merging conflicts inside one session | Integration is the lead's merge gate; surface partition errors |

## What this skill does NOT do

- Does NOT authorize parallelization or session spawns (dispatcher's decision;
  spawns are reserved).
- Does NOT carry the worktree or branch mechanics (`worktree-management`,
  `branch-lifecycle`).
- Does NOT perform the merge or own integration (lead's merge gate).
- Does NOT define the recipient-resolution or wake mechanics (`agent:routed-comms`).
- Does NOT govern in-session read-only subagents (`ROLES.md` §"Harness-native subagents (in-session)") — those parallelize reading *within one seat*; this skill parallelizes build work *across dispatched sessions*.
