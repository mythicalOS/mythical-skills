---
name: branch-lifecycle
description: |
  The branch-per-task coordination flow that spans the dispatched agent,
  the gate roles, and the lead: create + name a feature branch in the
  isolated worktree, report it (branch + immutable commit SHA) in the
  close-out, publish it to the shared remote (never to `main`) with the
  daemon's `git.push_branch` per the dispatch rhythm, have the gate roles
  review against that SHA once it is on the remote, and have the lead
  request the landing with the lead-only `git.request_landing` and trigger
  gated cleanup. Includes the pre-handoff reviewer-gate input prep the
  dispatched agent runs at review-ready time (absorbing the former
  `code-review-request` skill) and the merge-readiness
  checklist that feeds the merge gate. Procedural + role-agnostic: WHO may
  do each step, WHICH authority rhythm gates the publication/landing, and
  WHETHER a landing is authorized are decisions in the role playbooks +
  `ROLES.md` — this skill is the cross-role mechanics, not the authority.
assumes:
  - |
    The physical worktree (detection, creation under
    `$AGENT_WORKTREE_PATH`, setup, baseline, removal mechanics) is
    `worktree-management`; this skill is the branch protocol that runs
    inside it and does not duplicate the worktree mechanics.
  - |
    Claude Code roles run the LOCAL git steps via `Bash`; Codex roles run
    the same commands via `functions.exec_command`. Publishing a branch and
    landing it are not local git steps: both lanes call the same daemon
    tools (`git.push_branch`, `git.request_landing`), so no session needs a
    remote credential. The branch naming convention, the SHA-as-contract
    rule, and the role-step ownership are platform-agnostic and bind both
    paths identically.
---

# branch-lifecycle

The coordination flow for one dispatched unit of build work, from feature branch
to merged `main`. It is **role-agnostic by design**: the flow crosses three
owners — the dispatched agent (creates + names, reports, publishes), the gate roles
(fetch, review against the SHA), and the lead (requests the landing, gated cleanup) — so
the skill names each step's owner generically and never bakes a role into its own name or
hardcodes who-may-invoke. The isolated worktree these steps run in is
`worktree-management`.

**No session pushes or merges with its own keystrokes.** Sessions hold no remote
credential; the daemon owns the remote. Two tools carry the whole remote half of
this flow — `git.push_branch` (worker or lead) publishes a feature branch, and
`git.request_landing` (**lead only**) asks the daemon to land a reviewed
candidate. Everything else below is local git.

## Authority boundary (read first)

This skill carries the cross-role *mechanics*. It does not make the authority
decisions the mechanics serve:

- **The landing decision is the lead's**, not the dispatched agent's and
  not this skill's. The lead owns the serialized landing request and the gated
  cleanup; under rhythm D an *all-green* landing is green-path-delegated (eligibility
  per `ROLES.md` §"Apex substitution under rhythm D"). This skill never presents a
  merge/PR/discard menu. `git.request_landing` is refused for every role but the
  lead, at the daemon — the refusal is the boundary, not this prose.
- **The branch publication follows the dispatch's authority rhythm — this skill
  does not pick it.** Publishing goes to the shared remote, **not** to `main`, and is
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
rhythm B / D-semi-auto, after the rhythm-gated publication under A / C. The close-out
field is the *reported* SHA, not a claim that it is already on the remote.

The SHA is captured at close-out time. Under B / D-semi-auto the publication is
immediate (continuous with the close-out), so the SHA is fetchable right away. Under
A / C it is rhythm-gated (§"Publish the branch to the shared remote", below), so the
reported SHA becomes fetchable only after that gated publication. Gate-role review and
reviewer-prep therefore run at **review-ready (post-publication)** time, not off the
close-out alone; no downstream step is ever asked to fetch a SHA that is not yet on
the remote.

## §"Publish the branch to the shared remote"

When the dispatch's authority rhythm permits (autonomous under B / D-semi-auto;
after the green-light under A; at the cycle batch under C), publish the branch — and
only the branch, never `main`. You do not run the remote-writing command yourself and
you hold no credential for it; ask the daemon:

```text
git.push_branch {repo: "<repo-name>", branch: "<branch>", sha: "<full-SHA>"}
  → {ok: true, sha, ref}
```

- **`sha`** is the immutable id you already captured (`git -C "$WT" rev-parse HEAD`) —
  the same one the close-out reports. The tool publishes exactly that object and does
  not resolve a ref on your behalf. **That cuts both ways, and the second way is the
  dangerous one:** a malformed or unknown id is refused, but a **stale-but-valid** id
  — a real earlier commit you remembered instead of re-read — publishes successfully
  and puts the WRONG commit on the remote under the right branch name, returning
  `ok: true`. Nothing downstream distinguishes that from the commit you meant. Re-read
  it (`git -C "$WT" rev-parse HEAD`) immediately before the call and compare it to
  what your close-out reports; never retype one from memory or from an earlier message.
- **`repo`** is the repository's configured name — **required** when the project has
  more than one configured repository, omitted when it has exactly one.
- The returned **`sha` and `ref` are the daemon's report of what is on the remote**
  — quote those, never an echo of what you asked for. They exist only after the call,
  so they belong wherever you report the *publication*: in the close-out when
  publication is continuous with it (B / D-semi-auto), and in the post-publication
  addendum when the rhythm deferred it (A / C — the close-out was written and routed
  before the branch was on the remote, and is not rewritten).

The tool is available to the **worker** and the **lead** only; a read-only gate role
calling it is refused at the daemon. Publication makes the reported SHA review-ready
(fetchable by the gate roles). It is reversible and is distinct from the reserved
landing.

## §"Reviewer-gate input prep (pre-handoff)"

*(Absorbs the former `code-review-request` skill — the same discipline, now a
stage of this flow.)*

The reviewer is a gate in the chain (Gate 2), dispatched by the lead, reviewing
the published branch at the close-out's cited SHA (§"Gate-role review against the
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
- a **real, published diff** — actual code at the pinned commit, not a prose
  apply-spec (§"Gate-role review against the cited SHA");
- **what it should do** — the requirement/brief the work implements, so the
  reviewer can check the diff against intent;
- **verification evidence** — the fresh test/build output proving the claim
  (`verification-completion`), not "should pass".

**Pre-handoff self-check** — run at **review-ready (post-publication) time** (immediate
under rhythm B / D-semi-auto; after the rhythm-gated publication under A / C — the
canonical contract above). All must hold; each line catches an issue that
otherwise cascades into a bounced review:

- [ ] Branch published **to the remote** — run the exact on-remote proof from the
      merge-readiness "Branch fully published" line (§"Merge-readiness checklist",
      below, the single owner of that command text): remote ref == the
      close-out's reported SHA == local HEAD. A local-HEAD match alone does not
      prove it reached the remote, and neither does having called the tool.
- [ ] Worktree clean (`git -C "$WT" status --porcelain` empty); nothing committed
      locally that was left unpublished.
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
presupposes the branch is published (under A/C that is after the rhythm-gated
publication, above). It fetches and reads at that commit, read-only — no checkout,
no local branch:

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
- **Branch fully published** — the reported SHA is actually **on the remote**, not
  just the local HEAD: `git ls-remote origin "<branch>"` (or `git rev-parse
  origin/<branch>` after `git fetch origin`) equals the close-out's `Branch:` SHA,
  and the local `git -C "$WT" rev-parse HEAD` equals it too. A local-HEAD match
  alone does not prove the commit reached the remote, and the `ref`/`sha` a
  `git.push_branch` call returned is a report, not a substitute for this check.
  Nothing uncommitted, and nothing committed-but-unpublished, in the worktree.
- **Worktree clean** — `git -C "$WT" status --porcelain` is empty.
- **Gates cite the same SHA** — every required verdict (Gate 1 architect/QA, Gate
  2 reviewer) references the SHA the close-out reported; a mismatch is a stale
  review → bounce + re-dispatch.
- **Cross-model CLEAN** — the load-bearing cross-model pass converged
  (`agent:cross-model-review`); the worker's diff-review Gate 2.2 likewise.
- **Mergeable** — for ≥2 separately-floored branches landing together, a
  `git merge-tree` dry-run shows no surprise conflict before the serialized merge.

A failure on any line routes to the authority-holder (the lead bounces a stale
verdict; the dispatched agent fixes a red verification or an unpublished commit); it is
not a green-light.

## §"Merge to main"

**Nobody runs the merge keystrokes.** The lead does not need `Bash` for this, and no
role substitutes for the lead here: the **daemon** performs the landing — fetch,
gate-completeness check, merge and remote write — behind one lead-only tool. There is no
worker "land contract" and no operator keystroke path in this flow.

The lead requests the landing once the checklist holds and the landing is authorized.
The landing is the reserved surface; authorization is decided per `ROLES.md`
§"Apex substitution under rhythm D" (operator-gated under A/B/C; CTO green-path under D
when all-green) — this skill does not decide it, it carries the request the
authority-holder approved:

```text
git.request_landing {sha: "<the close-out's SHA>", task_record_id: "<the task record id>",
                     repo: "<repo-name>", branch: "<branch>"}
  → {landing_id, status, reason?}
```

- **`sha`** is the candidate: the exact commit every verdict cites (§"Merge-readiness
  checklist" — a set of verdicts that do not all cite it is not ready).
- **`task_record_id`** is the `task` record this landing completes. It is required —
  a landing that closes no dispatched task is refused, and it is what carries the work
  item to `merged`.
- **`repo`** follows the `git.push_branch` rule (required when the project has more
  than one configured repository); **`branch`** disambiguates when that SHA was
  published under more than one ref.

**`status` is where the landing got to. Only `landed` means it merged** — and only
`landed` makes the daemon append the `merge_closeout` record. The others do not:
`queued`, `awaiting_ack` (an acknowledgment is still owed before it merges),
`awaiting_external_merge` (it is a pull request on the forge now), `refused` and
`failed`. `reason` is optional on **any** status — report it when the daemon gave you
one and never invent one. Read the status; do not assume `landed`.

**Record the `landing_id`.** It is the landing's stable identity: you cite it in your
own gate close-out and TL;DR, and the `merge_closeout` record — which the **daemon**
writes on the `landed` transition, never you — is minted against the same landing
(`agent:coordination-closeout-templates` §"Mandatory merge close-out").

A refusal is a bounce, not a fallback: an incomplete or rejected gate set is refused
**before any remote mutation happens**, and the answer is to fix the gate set and ask
again — never to do it by hand. A merge conflict is likewise the daemon's report back
to you, routing to the readiness checklist.

Commits remain reachable from the integration branch after the landing.

## §"Cleanup"

Post-landing and apex-confirmed, the lead triggers cleanup: remove the worktree
(`worktree-management` §"Worktree removal mechanics").

**The merged remote branch is not deleted here.** Neither `git.push_branch` nor
`git.request_landing` can delete a ref and no daemon tool does yet, so the merged
branch **stays on the remote** until the forge's delete-on-merge setting or an
operator removes it. That is the current doctrine, not an oversight: do not reach for
a remote-deleting command to "finish" the cleanup.

Deleting the **local** branch is unchanged — it touches no remote — and runs after
the worktree is gone, since the worktree still references it:

```bash
git -C "<main-root>" branch -d "<branch>"   # local only; merged commits stay on the integration branch
```

## Quick reference — step → owner → artefact

| Step | Owner | Touches | Artefact |
|---|---|---|---|
| Create + name branch | dispatched agent | `feat/<issue-id>-<slug>` in `$AGENT_WORKTREE_PATH` | — |
| Report branch | dispatched agent | `**Branch:** <name> @ <SHA>` (immutable) | `closeout` record (to: lead) |
| Publish branch (rhythm-gated) | dispatched agent (worker or lead) | `git.push_branch` → shared remote (makes the SHA review-ready) | — |
| Prep reviewer-gate input | dispatched agent | pre-handoff self-check at review-ready time | the routed close-out is the input (+ addendum if SHA changed) |
| Review against SHA | gate role | `git fetch`; review at `<SHA>` once on the remote | verdict cites `<SHA>` |
| Verify same SHA + checklist | lead | all verdicts vs the one SHA | gate close-out |
| Merge to main | lead **only** | `git.request_landing`; the daemon fetches, merges and writes the remote | the daemon's `merge_closeout`, correlated by `re` to the task record; the `landing_id` is what YOUR gate close-out cites |
| Cleanup | lead | remove worktree + delete the LOCAL branch (the remote branch stays) | — |

## What this skill does NOT do

- Does NOT decide whether to land (lead-owned; green-path under D).
- Does NOT pick the authority rhythm that gates the publication/landing.
- Does NOT grade or issue the review verdict (reviewer's; CRITICAL override is
  operator-only), and does NOT replace the cross-model pass
  (`agent:cross-model-review`, Gate 2.2).
- Does NOT carry the physical worktree mechanics (`worktree-management`).
- Does NOT define the close-out template shape beyond the required `Branch:`
  field, nor the routing mechanics (the close-out templates + `agent:routed-comms`).
