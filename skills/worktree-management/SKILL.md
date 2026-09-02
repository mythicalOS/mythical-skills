---
name: worktree-management
description: |
  Physical worktree lifecycle for per-session isolation — detect whether
  you are already in a linked worktree (git-dir vs git-common-dir, with
  the submodule guard), create a worktree under the launcher-set
  `$AGENT_WORKTREE_PATH/<repo>/<slug>/<branch>`, run project setup + a clean
  baseline (submodule population is usually a no-op under the dep-repo
  isolation design — only the rare parent-repo task populates, and only the
  specific submodules it touches), and execute the mechanics of a worktree
  removal. Procedural only: WHETHER to merge and WHEN to clean up are the
  lead's decision (lead owns merge + gated cleanup); the branch-per-task
  COORDINATION flow (naming, publishing, report, fetch, landing) lives in
  `branch-lifecycle`. This skill is the physical worktree, not the branch
  protocol.
assumes:
  - |
    `$AGENT_WORKTREE_PATH` is the ONE launcher-set base root. The build
    floor carves out `$AGENT_WORKTREE_PATH/<repo>/$AGENT_BUS_COORD_SLUG/**` for
    writes — WORKER role only, and ONLY under its own slug at the 2nd path
    segment. So the worktree MUST be created at
    `$AGENT_WORKTREE_PATH/<repo>/$AGENT_BUS_COORD_SLUG/<branch>`, where `<repo>`
    is the git repo the worktree is OF (the dep repo the task targets, or the
    parent coordination repo for a parent/bin task) and `<slug>` denotes `$AGENT_BUS_COORD_SLUG`
    (the worker's durable identity). The Write-guard fail-safes on a sibling
    slug, a non-worker role, an unsafe base, or the wrong depth. There is no
    per-run "where?" choice and no project-local (`.worktrees/`) fallback.
  - |
    Claude Code roles run the git steps via `Bash`. The native worktree
    tool's default location is inside the reserved `.claude/` prefix and
    is NOT writable under the build floor, so the worktree is created with
    `git -C <repo> worktree add $AGENT_WORKTREE_PATH/...` unless the
    deployment has reconfigured the native tool's base path to
    `$AGENT_WORKTREE_PATH`. Codex roles run the same git commands via
    `functions.exec_command` (no native worktree tool).
---

# worktree-management

The procedure for the **physical** isolated worktree: detect existing isolation,
create the worktree at the launcher-set path, set the project up and confirm a
clean baseline, and (when the authority-holder calls for it) execute the removal
mechanics. The branch-per-task coordination flow that runs *inside* this worktree
— naming the feature branch, publishing it with `git.push_branch`, reporting its
SHA, gate-role fetch, and the lead-only landing request — is `branch-lifecycle`;
this skill does not duplicate it.

## Authority boundary (read first)

This skill is procedural. It executes within decisions the invoking playbook has
already made.

- **The merge / keep / discard decision is NOT this skill's.** The lead owns the
  merge to `main` and the gated worktree + branch cleanup; under rhythm D an
  all-green merge-to-main is green-path-delegated. This skill never presents a
  "merge, PR, or discard?" menu — that decision is hoisted to the authority-holder.
  The skill provides only the worktree *mechanics* the holder's decision invokes.
- **Isolation is the framework's decided model for build/implementation work**
  (parallel-by-default) — not a per-dispatch choice this skill makes. When the
  playbook dispatches build work, the skill executes the worktree mechanics that
  model calls for. (Under that model a gateless, conflict-disjoint pure-docs
  deliverable may land in place on `main`; matching isolation ceremony to actual
  conflict risk is the dispatcher's call, not the skill's.)
- **A failing baseline is a report, not a self-authorized fix.** If the baseline
  is red on entry, report it and surface the decision to proceed-or-investigate
  upward; do not silently start work on a broken baseline.

## §"Detect existing isolation" — run before creating anything

Determine whether you are already in a linked worktree, so you never nest one
inside another.

```bash
GIT_DIR=$(cd "$(git rev-parse --git-dir)" 2>/dev/null && pwd -P)
GIT_COMMON=$(cd "$(git rev-parse --git-common-dir)" 2>/dev/null && pwd -P)
BRANCH=$(git branch --show-current)
```

**Submodule guard.** `GIT_DIR != GIT_COMMON` is *also* true inside a git
submodule. Before concluding "already in a worktree," confirm you are not in a
submodule — this matters because the framework workspace is commonly a submodule
composition:

```bash
# If this prints a path, you are in a submodule — treat as a normal repo, NOT a worktree.
git rev-parse --show-superproject-working-tree 2>/dev/null
```

- **`GIT_DIR != GIT_COMMON` and not a submodule** → already in a linked worktree.
  Skip creation; go to §"Project setup + clean baseline". Report the branch state
  (on a named branch, or detached HEAD = externally managed, branch creation
  deferred to the branch flow).
- **`GIT_DIR == GIT_COMMON` (or in a submodule)** → a normal checkout. Continue to
  §"Create the worktree".

## §"Create the worktree" — under `$AGENT_WORKTREE_PATH`

The location is not a choice: it is `$AGENT_WORKTREE_PATH/<repo>/<slug>/<branch>`
(`<slug>` = `$AGENT_BUS_COORD_SLUG`; `<repo>` = the dep repo the worktree is of),
carved out of the build floor for writes. The feature-branch *name* is
decided per `branch-lifecycle`'s convention (`feat/<issue-id>-<slug>`); this step
takes that name and creates the worktree on it.

Run `git worktree add` from the main repo root via `git -C` (never a chained `cd`
into the worktree — keep the command CWD-stable):

```bash
# <repo> = the git repo this task targets (a dependency repo, or the parent coordination repo
# for a parent/bin task). The worktree is OF that repo, created from ITS OWN checkout — so it carries no
# submodules of its own (the dep repos have none) and there is nothing to populate.
WT="$AGENT_WORKTREE_PATH/<repo>/$AGENT_BUS_COORD_SLUG/<branch>"
git -C "<repo-checkout>" worktree add "$WT" -b "<branch>"
```

- If the deployment reconfigured a **native worktree tool** to use
  `$AGENT_WORKTREE_PATH` as its base, prefer it; otherwise drive the worktree with
  the explicit `git -C` form above and skip the native enter/exit calls. Do NOT
  use the native tool's default location — it lands inside the reserved `.claude/`
  prefix, which the build floor fences off.
- **Submodule population — usually nothing to do (dep-repo-level).** The worktree is of a SINGLE dep
  repo, which carries no submodules of its own, so there is nothing to populate — that is the whole
  point of isolating at the dep-repo level rather than the parent. The ONLY exception is a rare
  task whose `<repo>` is the parent coordination repo itself AND needs a submodule's content: then
  populate ONLY the specific submodule(s) the task touches (`git -C "$WT" submodule update --init --
  <path>`), never a blanket `--recursive` over every submodule.

## §"Project setup + clean baseline"

Auto-detect and run the project's setup, then confirm a clean baseline so a later
failure is attributable to your change, not pre-existing breakage:

```bash
# Setup (whichever applies)
[ -f "$WT/package.json" ] && (cd "$WT" && <install>)        # e.g. bun install / npm install
[ -f "$WT/Cargo.toml" ]   && (cd "$WT" && cargo build)
[ -f "$WT/pyproject.toml" ] && (cd "$WT" && <install>)
[ -f "$WT/go.mod" ]       && (cd "$WT" && go mod download)

# Baseline (project-appropriate test command)
(cd "$WT" && <test command>)
```

- **Baseline passes** → report ready; proceed to build on the branch
  (`branch-lifecycle`).
- **Baseline fails** → report the failures and surface proceed-or-investigate
  upward (authority boundary). Do not proceed silently.

## §"Worktree removal mechanics"

Invoked only when the authority-holder (the lead, post-merge and apex-confirmed)
calls for cleanup. The decision is theirs; the mechanics are here.

```bash
# 1. NEVER run `git worktree remove` from inside the worktree being removed — it
#    fails / misbehaves when CWD is inside the target. Operate from the main root.
MAIN_ROOT=$(git -C "$(git -C "$WT" rev-parse --git-common-dir)/.." rev-parse --show-toplevel)

# 2. Remove the worktree, then self-heal stale registrations.
git -C "$MAIN_ROOT" worktree remove "$WT"
git -C "$MAIN_ROOT" worktree prune
```

- **Provenance fence.** Only remove a worktree under `$AGENT_WORKTREE_PATH` (one
  this model created). A worktree the host environment owns is removed via that
  host's exit mechanism, never with `git worktree remove`.
- **Order with branch deletion.** Deleting the merged **local** branch is part of
  the lead's cleanup in `branch-lifecycle`; remove the worktree before deleting a
  branch the worktree still references. The merged **remote** branch is not deleted
  by any step of this flow — it stays until the forge's delete-on-merge setting or
  an operator removes it.
- **Submodule-populated worktrees.** If submodules were populated here (§"Create
  the worktree"), `git worktree remove` can refuse on leftover submodule state.
  Having confirmed the provenance fence above, either deinit first
  (`git -C "$WT" submodule deinit --all -f`) then remove, or use
  `git -C "$MAIN_ROOT" worktree remove --force "$WT"` — `--force` only ever on a
  `$AGENT_WORKTREE_PATH` worktree this model created, never a host-owned one.

## Quick reference

| Situation | Action |
|---|---|
| Already in a linked worktree (not a submodule) | Skip creation → §"Project setup" |
| In a submodule | Treat as a normal repo (submodule guard) |
| Normal checkout, build dispatch | Create under `$AGENT_WORKTREE_PATH/<repo>/<slug>/<branch>` |
| Parent-repo task touching a submodule (rare) | Populate ONLY the specific submodule(s) the task touches (§"Create the worktree"); dep-repo worktrees have nothing to populate |
| Baseline red on entry | Report + surface decision upward; do not proceed |
| Cleanup called by the lead | Remove from main root + prune; only under `$AGENT_WORKTREE_PATH` |

## What this skill does NOT do

- Does NOT decide merge / keep / discard (lead owns merge + gated cleanup).
- Does NOT name, publish, or report the feature branch, and does NOT run gate-role
  fetch or the landing request — that is `branch-lifecycle`.
- Does NOT auto-fix a failing baseline (report + surface upward).
- Does NOT choose the worktree location (fixed at `$AGENT_WORKTREE_PATH`).
