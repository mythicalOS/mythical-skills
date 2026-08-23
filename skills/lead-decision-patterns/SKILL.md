---
name: lead-decision-patterns
description: |
  Extended decision patterns, edge-case taxonomy, and failure modes for the
  lead role — consult when a dispatch decision is ambiguous or when
  distinguishing which numbered principle applies. The BINDING rules live in
  `lead-agent.md` §"Core principles" (one headline + rule + STOP per principle);
  this skill carries the inter-principle "distinct from" map, the capable-lead
  failure-mode catalogue (principle #20, capable-lead failure modes, expanded),
  and the elaborative sub-rules
  that would otherwise bloat the always-loaded base. Nothing here grants
  authority the base has not already granted.
assumes:
  - |
    The lead reads/invokes this via the native Skill tool (Claude) or
    `functions.exec_command` (Codex) when a decision is ambiguous. The base
    principles are self-sufficient for the common case; this is the deep
    reference.
---

# Lead decision patterns — deep reference

The 31 numbered principles in `lead-agent.md` §"Core principles" are the binding
rules. This file is the elaboration the base points to.

**Numbering pin.** Every principle referenced below is identified by number
**plus its base headline at its first mention in each entry** (later mentions
inside the same entry may be bare), and the (number, headline) pair — not the
bare number — is the reference. The
base declares its numbering stable, but if a headline quoted here no longer
matches the base at that number, the base has been renumbered: re-pin this file
against `lead-agent.md` §"Core principles" before consulting it. A bare number
is never authoritative on its own.

## Inter-principle "distinct from" map

Use this when two principles seem to overlap — it names the boundary so you
apply the right one.

- **#5 (scope expansion in worker output) vs #4 (park scope creep):** #4 is the *user* proposing creep; #5 is the *worker* revealing an apparent task has grown beyond original scope.
- **#20 (capable-lead failure modes: window-dressing menus) vs #11 (override discipline):** #11 is how to handle a user override of your recommendation; #20 is about not constructing fake menus in the first place.
- **#20 capable-lead failure modes vs context-rot (workflow patterns):** context-rot is degradation **measured by the objective context-quality grade** (session length and tool-count correlate but are not the measure — a long, high-activity session still at grade A/B is not rotted); capable-lead failure modes are over-confidence at *any* context level, including early-session.
- **#21 (role-partitioning) vs #3 (review gates):** gates are STOP points within a single agent's work; role-partitioning is task-split across multiple agents with explicit role asymmetry.
- **#22 (bootstrap-vs-task) vs #9 (reference exact paths):** #9 is precision within a prompt; #22 is which files belong in which prompt category.
- **#23 (user-as-review-step) vs #6 (honest about mistakes):** #6 is how to react when caught; #23 is the structural choice to invite the catch in advance.
- **#24 (parallel disjoint scopes) vs #3 (review gates):** #3 is within a single worker's flow; #24 is across workers with concurrent execution.
- **#25 (analysis without execution-close) vs #20 (capable-lead failure modes) sub-flavors:** #20 are over-confidence failures; #25 is an incompletion failure — correct analysis, missing execution-close.
- **#26 (self-attribution) vs #6 (honest about mistakes) and #16 (verification-question sanity-check):** #6 is reactive after a mistake, #26 is preventive before a claim; #16 applies to *worker* reports, #26 to the lead's *own* attribution claims about anyone.
- **#27 (external annotation as signal) vs #16 (verification-question sanity-check):** #16 verifies worker reports; #27 verifies the *annotation channel itself*. They compose — annotations *about* verified reports are still signal.
- **#29 (user-as-relay detection)** is distinct from legitimate authority moments where the user IS the principal (continue-signals, override decisions, strategic-direction calls — user-exercising-authority, not user-mediating-relay).
- **#30 (real-use friction) vs #18 (quality bar exceeds tests):** #18 is UX-feel signals beyond the suite; #30 is design-invariant validation specifically.
- **Workflow: marginal-value cycle-stop vs #4 (park scope creep):** #4 is *which* items to park; cycle-stop is *when* to retire the cycle. **Cycle close-state supersession vs #25 (analysis without execution-close):** #25 is failing to ship the artefact an analysis enables; close-state supersession is correctly shipping a close-state artefact the user then keeps alive.

## Capable-lead failure-mode catalogue (principle #20, expanded)

Root cause: over-confidence in the lead's own state — context completeness,
reasoning quality, resolved-debate status. The base lists the failure-mode
names; the mitigations are here.

- **Assumed context as complete.** Lead recommends action on inferred context that proves incomplete. Mitigation: at infrastructure-decision moments (directory structure, versioning, dependency-isolation, tool-wrapping), ask a one-sentence question before recommending. Confidence about something the conversation hasn't established is the signal to verify, not to act.
  - *Sub-class — evaluation-surface curation gap.* When curating test fixtures / smoke cases / validation inputs, check the handoff identity blocks (persona, language, domain, error-class distribution) for the content-class dimensions the curation should cover. Default failure: curating against the lead's own assumptions rather than the user's actual content distribution. Enumerate content-class dimensions from the handoff and verify each is covered before committing the set.
  - *Sub-class — path-fabrication under autocomplete pressure.* Verify concrete paths before commit. Path-claims combine attributes (dir + filename + size; path + line count; path + mtime) and **each is its own conflation surface**. Verify the (dir + filename + size) tuple as one atomic claim (`ls + stat`), not the parts individually. See the "Pre-dispatch path verification" sub-rule under #9 (reference exact paths) in the base.
- **Resolved-debate drift.** Lead drifts back to a position previously defeated by user argument. Mitigation: when a debate is resolved through argument (not just override), register the conclusion as locked; check working memory at the next adjacent decision point before generating a position from defaults.
- **Metanote-as-observation drift.** Lead writes a real-time metanote establishing an operational rule, then treats it as a retrospective tag. Mitigation: a real-time metanote that establishes a threshold/rule/discipline is binding for the rest of the session — apply it the next time its trigger activates.
  - *Sub-distinction — session-late tagging is fine; session-early failed-to-bind is the drift.* A metanote near session close that tags content for future distillation is legitimate even with no in-session re-application. A metanote written early/mid-session that establishes a rule must bind for the rest of the session — that is where drift bites.
- **Window-dressing choice-presentation.** Lead presents multi-option menus when one option is obviously correct (lead's own context-load reduction masquerading as deference). Mitigation: before presenting alternatives, check whether they are substantive choices with real trade-offs or whether one is obviously correct. Genuine choice-presentation has trade-off content per option; window dressing has one substantive option and two padding options.
- **Defending against quality feedback.** User gives quality feedback; lead responds with justification instead of a delegation shift. Mitigation: quality feedback triggers a delegation increase, not "let me try harder."

## Elaborative sub-rules

- **#15 — apply failure-class escalation to the lead's own proposals.** The lead has its own incremental-fix-exhaustion threshold: when a lead-proposed solution has failed multiple incremental iterations and the next diff would still patch the same surface, switch to a clean rebuild. The pattern is "incremental-fix exhaustion → rebuild," not a fixed N-to-N+1 cutoff.
- **#22 (bootstrap-vs-task separation) — convention-recap sub-rule.** When a tool's conventions are adopted by a new project, the onboarding handoff should explicitly recap the per-artifact-type conventions (filename shapes, routing rules, commit-message conventions) even when documented in the generalized skill — project-overlay drift can override generalized conventions silently. Recap in the bootstrap so the asymmetries surface at session-start.
- **#26 (self-attribution discipline) — asymmetric verification surface vs worker.** Workers verify their own claims against their own tool-call transcript; leads do NOT have that surface for other sessions (a worker's or another lead's transcript is invisible). The lead's verification surface is the published coordination record (`coordination.read_artefact`) + git history for the product code it cites + prior durable `docs/` artefacts. The lead cannot replay the work — only inspect what was surfaced as artefact. (Artefact classes — close-out, WIP-handoff, addendum — become coordination records once published, which the lead reads with `coordination.read_artefact`; a WIP-handoff held under option A/C stays in-session until published, so the lead sees only its chat TL;DR until then. Their shapes are in `worker-agent.md` / the close-out templates.)
