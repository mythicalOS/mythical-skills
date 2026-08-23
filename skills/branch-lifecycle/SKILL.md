---
name: branch-lifecycle
description: |
  The branch-per-task coordination flow that spans the dispatched agent,
  the gate roles, and the lead: create + name a feature branch in the
  isolated worktree, report it (branch + immutable commit SHA) in the
  close-out, push it to the shared remote (never to `main`) per the
  dispatch rhythm, have the gate roles review against that SHA once it is
  on the remote, and have the lead merge to `main` and trigger gated
  cleanup. Includes the pre-handoff reviewer-gate input prep the dispatched
  agent runs at review-ready time (absorbing the former
  `code-review-request` skill) and the merge-readiness
  checklist that feeds the merge gate. Procedural + role-agnostic: WHO may
  do each step, WHICH authority rhythm gates the push/merge, and WHETHER a
  merge is authorized are decisions in the role playbooks + `ROLES.md` —
  this skill is the cross-role mechanics, not the authority.
assumes:
  - |
    The physical worktree (detection, creation under
    `$AGENT_WORKTREE_PATH`, setup, baseline, removal mechanics) is
    `worktree-management`; this skill is the branch protocol that runs
    inside it and does not duplicate the worktree mechanics.
  - |
    Claude Code roles run the git steps via `Bash`; Codex roles run the
    same commands via `functions.exec_command`. The branch naming
    convention, the SHA-as-contract rule, and the role-step ownership are
    platform-agnostic and bind both paths identically.
---

# branch-lifecycle

The coordination flow for one dispatched unit of build work, from feature branch
to merged `main`. It is **role-agnostic by design**: the flow crosses three
owners — the dispatched agent (creates + names, reports, pushes), the gate roles
(fetch, review against the SHA), and the lead (merge, gated cleanup) — so the skill names
each step's owner generically and never bakes a role into its own name or
hardcodes who-may-invoke. The isolated worktree these steps run in is
`worktree-management`.

## Authority boundary (read first)

This skill carries the cross-role *mechanics*. It does not make the authority
decisions the mechanics serve:

- **The merge-to-main decision is the lead's**, not the dispatched agent's and
  not this skill's. The lead owns the serialized merge and the gated cleanup;
  under rhythm D an *all-green* merge-to-main is green-path-delegated (eligibility
  per `ROLES.md` §"Apex substitution under rhythm D"). This skill never presents a
  merge/PR/discard menu.
- **The push follows the dispatch's authority rhythm — this skill does not pick
  it.** The feature-branch push is to the shared remote, **not** to `main`, and is
  not the reserved surface. Under rhythm B / D-semi-auto it is autonomous; under
  rhythm A it waits for the green-light, and under rhythm C it queues for the
  cycle batch (the close-out is the STOP point under A). Which rhythm applies is
  the invoking playbook's call (`ROLES.md` §"Authority rhythms").
- **Branch naming is decentralized to the dispatched agent**, so no agent waits on
  a central namer before starting. The lead's dispatch states the *convention*;
  the agent applies it.
- **The SHA is the contract.** A verdict that cites a different SHA than the
  close-out reports is a stale review — the lead bounces it (the branch-model
  analogue of reconciling a close-out against branch HEAD).

## §"Create and name the branch"

Inside the isolated worktree (`worktree-management` §"Create the worktree"), the
dispatched agent creates and names the feature branch itself, per the convention
the dispatch brief states:

```
feat/<issue-id>-<slug>
```

`<issue-id>` is the tracker id for the dispatched task; `<slug>` is a short
kebab-case descriptor. Example: `feat/ISSUE-123-token-cache-expiry`. The agent
names + creates the branch; the lead does not pre-name it.

## §"Report the branch in the close-out"

The close-out (a `closeout` record addressed to the lead — `agent:routed-comms`)
carries a **required** field — the branch name and the **immutable** commit SHA,
read fresh from git, never a remembered value:

```bash
git -C "$WT" rev-parse HEAD     # capture this verbatim into the close-out
```

```
**Branch:** <branch> @ <full-SHA>
```

For a pure-docs deliverable that landed in place on `main`, the field reads
`n/a — <reason>`. A build close-out without a branch + commit SHA is incomplete
and is bounced. This SHA — not `main`'s moving HEAD, not the branch ref — is what
every downstream step addresses.

**Canonical contract — shared by this flow, the gate review, and the
reviewer-gate input prep (§"Reviewer-gate input prep (pre-handoff)",
below):** the close-out reports the **immutable `rev-parse` SHA**;
the branch is **review-ready once that SHA is on the remote** — immediate under
rhythm B / D-semi-auto, after the rhythm-gated push under A / C. The close-out
field is the *reported* SHA, not a claim that it is already pushed.

The SHA is captured at close-out time. Under B / D-semi-auto the push is immediate
(continuous with the close-out), so the SHA is fetchable right away. Under A / C
the push is rhythm-gated (§"Push the branch to the shared remote", below), so the
reported SHA becomes fetchable only after that gated push. Gate-role review and
reviewer-prep therefore run at **review-ready (post-push)** time, not off the
close-out alone; no downstream step is ever asked to fetch a SHA that is not yet on
the remote.

## §"Push the branch to the shared remote"

When the dispatch's authority rhythm permits (autonomous under B / D-semi-auto;
after the green-light under A; at the cycle batch under C), push the branch — and
only the branch, never `main`:

```bash
git -C "$WT" push -u origin "<branch>"
```

The push publishes the reported SHA, making it review-ready (fetchable by the gate
roles). It is reversible (the branch can be deleted) and is distinct from the
reserved merge-to-main.

## §"Reviewer-gate input prep (pre-handoff)"

*(Absorbs the former `code-review-request` skill — the same discipline, now a
stage of this flow.)*

The reviewer is a gate in the chain (Gate 2), dispatched by the lead, reviewing
the pushed branch at the close-out's cited SHA (§"Gate-role review against the
cited SHA", below). This step is the dispatched agent preparing that gate's
input — it is not a parallel review, it does not grade (the verdict —
accept / accept-with-fixes / reject — and severity are the reviewer's; CRITICAL
override is operator-only), and it does not decide when review happens or who
reviews (the lead's gate decision). It is also **distinct from the cross-model
pass** the agent runs on its own diff before commit (`agent:cross-model-review`,
Gate 2.2) — both run; neither substitutes for the other (the reviewer gate is
Gate 2.3).

**The reviewer input IS the close-out already routed to the lead** — no separate
"review request" artefact exists, and no second close-out is written. What makes
that close-out review-ready input:

- the **branch + immutable SHA** (§"Report the branch in the close-out");
- a **real, pushed diff** — actual code at the pinned commit, not a prose
  apply-spec (§"Gate-role review against the cited SHA");
- **what it should do** — the requirement/brief the work implements, so the
  reviewer can check the diff against intent;
- **verification evidence** — the fresh test/build output proving the claim
  (`verification-completion`), not "should pass".

**Pre-handoff self-check** — run at **review-ready (post-push) time** (immediate
under rhythm B / D-semi-auto; after the rhythm-gated push under A / C — the
canonical contract above). All must hold; each line catches an issue that
otherwise cascades into a bounced review:

- [ ] Branch pushed **to the remote** — run the exact pushed-proof from the
      merge-readiness "Branch fully pushed" line (§"Merge-readiness checklist",
      below, the single owner of that command text): remote ref == the
      close-out's reported SHA == local HEAD. A local-HEAD match alone does not
      prove it was pushed.
- [ ] Worktree clean (`git -C "$WT" status --porcelain` empty); no unpushed work.
- [ ] Verification run fresh; evidence attached (not "looks correct").
- [ ] Cross-model pass on the diff is CLEAN or its capped-iteration STOP is
      surfaced (`agent:cross-model-review`).
- [ ] Close-out states what the work does and the requirement it meets.

If the SHA changed after the close-out was written (e.g. a re-fold added
commits), signal the new SHA with a routed **addendum** (`agent:routed-comms`),
not a duplicate close-out. Do not dispatch a reviewer yourself — the lead owns
the gate chain.

## §"Gate-role review against the cited SHA"

A gate role (architect / QA / reviewer) reviews against the **exact SHA the
close-out reported**, not `main`'s HEAD and not the moving branch ref. This
presupposes the branch is pushed (under A/C that is after the rhythm-gated push,
above). It fetches and reads at that commit, read-only — no checkout, no local
branch:

```bash
git fetch origin
git diff origin/main...<SHA>     # the real diff at the pinned commit
git show <SHA>                   # or read individual commits, read-only
```

The verdict artefact **cites the reviewed SHA**. This gives the reviewer actual
code (not a prose apply-spec) and the cross-model pass a real diff. Delivery follows
`agent:routed-comms`: publish the verdict as a coordination record
(`coordination.publish_artefact`) addressed to the recipient, `coordination.deliver`
its id, and STOP; the lead consumes it at the gate.

## §"Merge-readiness checklist" — feeds the merge gate

Before the lead runs the merge gate, the branch must be *ready*. This is a
readiness checklist, not a merge decision (the decision is the lead's, above). All
must hold:

- **Baseline + work verified** — the dispatched agent ran the project's
  verification on the branch and reported evidence (see `verification-completion`);
  no "should pass".
- **Branch fully pushed** — the reported SHA is actually **on the remote**, not
  just the local HEAD: `git ls-remote origin "<branch>"` (or `git rev-parse
  origin/<branch>` after `git fetch origin`) equals the close-out's `Branch:` SHA,
  and the local `git -C "$WT" rev-parse HEAD` equals it too. A local-HEAD match
  alone does not prove the commit was pushed. No uncommitted or unpushed work in
  the worktree.
- **Worktree clean** — `git -C "$WT" status --porcelain` is empty.
- **Gates cite the same SHA** — every required verdict (Gate 1 architect/QA, Gate
  2 reviewer) references the SHA the close-out reported; a mismatch is a stale
  review → bounce + re-dispatch.
- **Cross-model CLEAN** — the load-bearing cross-model pass converged
  (`agent:cross-model-review`); the worker's diff-review Gate 2.2 likewise.
- **Mergeable** — for ≥2 separately-floored branches landing together, a
  `git merge-tree` dry-run shows no surprise conflict before the serialized merge.

A failure on any line routes to the authority-holder (the lead bounces a stale
verdict; the dispatched agent fixes a red verification or unpushed work); it is
not a green-light.

## §"Merge to main"

**Floor execution note.** Under the build floor the lead holds no `Bash`, so the lead
*authorizes* the merge but does not run the `git` keystrokes: the **executing** role is the
**worker** via its green-path land contract (the worker holds `Bash`) — or an operator. Lead
keystroke-execution of the merge returns only when a daemon-side merge broker provides a contained merge
capability. The steps below are the procedure-of-record for whichever role executes.

The lead — the single pusher to `main` — runs the serialized merge once the
checklist holds and the merge is authorized. The merge is the reserved surface;
authorization is decided per `ROLES.md` §"Apex substitution under rhythm D"
(operator-gated under A/B/C; CTO green-path under D when all-green) — this skill does
not decide it, it executes the merge the authority-holder approved:

```bash
# Fetch ALL refs so the remote-tracking ref origin/<branch> is reliably updated —
# `git fetch origin <branch>` only updates FETCH_HEAD on some configs, which can
# leave `origin/<branch>` stale before the merge.
git -C "<main-root>" fetch origin
git -C "<main-root>" checkout main && git -C "<main-root>" pull --ff-only

# Merge. A surprise conflict here means the merge-readiness checklist's merge-tree
# dry-run missed something — ABORT and bounce it; never hand-resolve an unexpected
# conflict directly on main inside this step.
if ! git -C "<main-root>" merge --no-ff "origin/<branch>"; then   # per project merge policy
    git -C "<main-root>" merge --abort
    # STOP: route the conflict back to the readiness checklist; do NOT push main.
    exit 1
fi

# Gate the push on a GREEN run of the project's tests on the MERGED result — a fresh
# run, not a remembered one (`verification-completion`). Only push main if it passes.
(cd "<main-root>" && <project test command>) \
    || { echo "merged-result tests RED — main NOT pushed; investigate or revert the merge"; exit 1; }
git -C "<main-root>" push origin main
```

Commits remain reachable from `main` after merge.

## §"Cleanup"

Post-merge and apex-confirmed, the lead triggers cleanup: remove the worktree
(`worktree-management` §"Worktree removal mechanics") **before** deleting the
merged remote branch, since the worktree still references it:

**Floor execution note** — same as the merge (§"Merge to main"): the lead *authorizes*
cleanup; the **worker** (green-path land contract) or an operator executes the keystrokes.

```bash
git -C "<main-root>" push origin --delete "<branch>"     # merged commits stay on main
```

## Quick reference — step → owner → artefact

| Step | Owner | Touches | Artefact |
|---|---|---|---|
| Create + name branch | dispatched agent | `feat/<issue-id>-<slug>` in `$AGENT_WORKTREE_PATH` | — |
| Report branch | dispatched agent | `**Branch:** <name> @ <SHA>` (immutable) | `closeout` record (to: lead) |
| Push branch (rhythm-gated) | dispatched agent | branch → shared remote (makes the SHA review-ready) | — |
| Prep reviewer-gate input | dispatched agent | pre-handoff self-check at review-ready time | the routed close-out is the input (+ addendum if SHA changed) |
| Review against SHA | gate role | `git fetch`; review at `<SHA>` once on the remote | verdict cites `<SHA>` |
| Verify same SHA + checklist | lead | all verdicts vs the one SHA | gate close-out |
| Merge to main | lead | fetch → merge → push `main` | merge close-out |
| Cleanup | lead | remove worktree + delete remote branch | — |

## What this skill does NOT do

- Does NOT decide whether to merge (lead-owned; green-path under D).
- Does NOT pick the authority rhythm that gates the push/merge.
- Does NOT grade or issue the review verdict (reviewer's; CRITICAL override is
  operator-only), and does NOT replace the cross-model pass
  (`agent:cross-model-review`, Gate 2.2).
- Does NOT carry the physical worktree mechanics (`worktree-management`).
- Does NOT define the close-out template shape beyond the required `Branch:`
  field, nor the routing mechanics (the close-out templates + `agent:routed-comms`).
