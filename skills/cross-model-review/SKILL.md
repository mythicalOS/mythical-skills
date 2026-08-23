---
name: cross-model-review
description: |
  How to run the cross-model adversarial validation pass on a load-bearing
  artefact — the per-platform invocation bindings (Claude author → Codex
  reviewer; Codex author → Claude reviewer), the capture-to-file pattern, the
  iterate-to-CLEAN loop with the framework iteration caps (3/8/12 by profile),
  and the model-boundary rule. Resolves the `review mode:` bootstrap line the
  daemon injects in local mode: absent or `cross-model` ⇒ the cross-model
  bindings (today's default); `ephemeral` ⇒ the sanctioned fresh-context
  same-model reviewer-subagent binding for deployments without a second model
  account. Procedural only: WHEN a role must run it and
  WHAT counts as load-bearing FOR THAT ROLE stay in each role playbook's
  §"Cross-model validation of load-bearing output"; the framework principle +
  same-model-forbidden rule live in `README.md` §"Cross-model review
  configuration".
assumes:
  - |
    Claude roles read/invoke this via the native Skill tool or `Read` and run
    the Codex CLI (`codex exec`) as the reviewer; Codex roles read it via
    `functions.exec_command` and run the Claude CLI (`claude -p`) as the
    reviewer. Under the default `cross-model` mode the model-boundary
    (author-model ≠ reviewer-model) is the gate and is platform-agnostic; under
    `review mode: ephemeral` (opt-in) a fresh-context same-model reviewer
    subagent satisfies it instead (§"Model-boundary rule", §"Ephemeral binding").
    The CTO consults this as a read-reference (not a Skill-tool invocation).
---

# Cross-model adversarial review — invocation bindings + loop

The pass is an adversarial consult or whole-file audit against a load-bearing
artefact + its cited evidence (a reasoning artefact, **not** a diff), run — under
the default `cross-model` mode — from a different model than authored it (or, under
`review mode: ephemeral`, from a fresh-context same-model reviewer subagent;
§"Model-boundary rule"). WHEN to run it, and WHAT is load-bearing for
your role, live in your playbook's §"Cross-model validation of load-bearing
output". The framework principle and the same-model-forbidden rule live in
`README.md` §"Cross-model review configuration". This skill is the HOW.

## Model-boundary rule (the gate)

**Under the default `cross-model` mode** (no `review mode:` line, or `review mode:
cross-model` — §"Mode resolution"), the pass MUST run from a different MODEL than
you authored with: a same-model self-review does NOT satisfy the gate — a model
cannot reliably review its own blind spots. The CLI call IS the model-boundary: a
Claude author running Codex (or a Codex author running Claude) satisfies
cross-model even within one session. **The one exception is `review mode:
ephemeral`** (opt-in; §"Ephemeral binding (review mode: ephemeral)"): a deployment
without a second model account may instead satisfy the gate with a fresh-context,
same-model reviewer subagent — honestly weaker against model-family blind spots,
so `cross-model` stays the default. An in-session same-model self-review never
qualifies in either mode.

## Mode resolution (the `review mode:` bootstrap line)

The active review mode reaches the session as a single bootstrap-prompt line the
daemon injects at spawn — `review mode: <mode>`, where `<mode>` is `cross-model`
or `ephemeral` (deployment config `review.mode`; daemon-authoritative, applied at
next spawn; NOT a per-role setting). Resolve it *before* choosing a binding:

- **Line ABSENT ⇒ `cross-model`.** Today's behavior and the default. The
  server / live-stack deployment injects no line, so the cross-model bindings
  below (§"Claude-side binding" / §"Codex-side binding") and the model-boundary
  gate apply UNCHANGED. This is also the high-risk-profile recommendation
  (`README.md` §"Cross-model review configuration").
- **`review mode: cross-model`** — identical to absent: the cross-model bindings
  apply.
- **`review mode: ephemeral`** — use §"Ephemeral binding (review mode: ephemeral)"
  below instead: a fresh-context, same-model reviewer subagent. This is the
  SANCTIONED fallback lane for a deployment without a second model account; it is
  honestly **weaker against model-family blind spots** than a true cross-model
  pass (`README.md` §"Cross-model review configuration").

The mode selects the reviewer WIRING only. The iterate-to-CLEAN loop, the profile
caps, the output contract (`SEVERITY | file:line | issue | fix`, or `CLEAN`), and
the fold-every-finding-before-delivery discipline are IDENTICAL in both modes
(§"Iterate-to-CLEAN loop with caps").

## Claude-side binding (Claude author → Codex reviewer)

Run the Codex CLI as the reviewer; **capture the verdict to a file and read it**
(never background-pipe):

```bash
OUT=$(mktemp "${TMPDIR:-/tmp}/xmodel-<slug>.XXXXXX")   # unique per run — avoids collision when sessions share a checkout
codex exec --sandbox read-only --skip-git-repo-check -c model_reasoning_effort="xhigh" '<adversarial consult naming the artefact reference(s) + its cited evidence; ask for SEVERITY | file:line | issue | fix, or CLEAN>' < /dev/null > "$OUT"
```

then read `"$OUT"`. The `< /dev/null` is **required** — `codex exec`
hangs in the agent Bash environment without it. The `-c model_reasoning_effort="xhigh"` runs the reviewer at maximum reasoning effort; pinning it in the command makes the gate self-contained, independent of a machine-local `~/.codex/config.toml` default that another machine or a fresh setup may not carry. This is a read-only consult, not
a `codex review --uncommitted` diff review. For playbook / cross-file-convention
edits prefer a **whole-file** audit (materially stronger than diff-scoped — it
catches base↔overlay contradictions against unchanged text).

### Local-mode daemon review route (credential stays daemon-held)

Where the deployment provides the daemon review route (local + configured mode only),
route the Codex consult through that route INSTEAD
of a direct `codex exec`. The daemon runs the SAME pinned codex flags (the shipped
`defaultCodexHarness`: `--sandbox read-only -C <cwd> --skip-git-repo-check -c
model_reasoning_effort=xhigh -`) AS THE DAEMON, with a daemon-held,
per-run-ephemeral credential — so the key is never in the agent's own env (a
strict reduction versus a direct `codex exec` that reads the key from the session
env):

```bash
# Address: an optional deployment override (set AGENT_REVIEW_URL to relocate
# the route; no deployment vends it today), else the reference container's
# documented default (the daemon's internal control listener):
curl -sS -X POST "${AGENT_REVIEW_URL:-http://127.0.0.1:7800/review/run}" \
  -H "Authorization: Bearer $AGENT_REVIEW_TOKEN" \
  -H 'Content-Type: application/json' \
  --data "$(jq -Rn --arg p '<adversarial consult naming the artefact reference(s) + cited evidence; ask for SEVERITY | file:line | issue | fix, or CLEAN>' '{prompt:$p}')"
```

- **Auth:** `$AGENT_REVIEW_TOKEN` is the per-session review token the daemon
  vended into this session's env at spawn — NOT the control key. Loopback
  only, on the daemon's container-internal control listener — never a
  published port.
- **Body is `{prompt, harness?}` plus four optional LABEL fields (`issue`,
  `issue_title`, `trigger`, `tag`) — send NO `cwd`.** The daemon ALWAYS runs
  the review against THIS session's own recorded cwd; any `cwd` in the body is
  ignored (you cannot point it at a sibling worktree). Omit `harness` to use the
  deployment's `review.selected_harness`. The labels are recorded on the run so
  its history can be grouped and addressed; they change nothing about how the
  review runs.
- **The daemon appends its own verdict-trailer instruction to your prompt — do
  not write one yourself.** Ask for the verdict content you need; the trailer
  format is the runner's contract for extracting and persisting the verdict, so
  a second, conflicting trailer instruction can leave the run with **no stored
  verdict at all** — a failed gate, not merely an untidy one.
- **PARSE the JSON response `status` — it is the gate verdict, stdout is not.**
  Treat ANY `status` other than `"completed"` as a FAILED gate REGARDLESS of
  stdout content: a timed-out or non-zero run can still have printed `CLEAN` into
  stdout, and stdout is only the verdict body WHEN `status == "completed"`. A
  non-completed status is a structural gate failure to surface, never a CLEAN
  reading.

Where the deployment does NOT provide the route (e.g. the live server stack — no
`review mode:` line, no route mounted), the direct `codex exec` binding above is
unchanged.

## Codex-side binding (Codex author → Claude reviewer)

Run the Claude Code CLI as the reviewer; pipe the artefact + cited evidence:

```bash
claude -p '<adversarial consult; ask for SEVERITY | file:line | issue | fix, or CLEAN>' --output-format text
```

Read-only consult, not a diff review. Same whole-file preference for playbook /
cross-file-convention edits.

## Ephemeral binding (review mode: ephemeral)

Engaged ONLY when the bootstrap line reads `review mode: ephemeral`
(§"Mode resolution"). This is the SANCTIONED fresh-context same-model lane for a
deployment without a second model account — honestly **weaker against
model-family blind spots** than the cross-model bindings above, so cross-model
stays the default and the high-risk-profile recommendation
(`README.md` §"Cross-model review configuration"). Do NOT use this lane unless the
`review mode: ephemeral` line is present.

The pass is delegated to a **fresh-context reviewer subagent** that shares NO
conversation state with the authoring session — a genuinely clean context is what
gives a same-model reviewer any independent purchase; a same-session
self-critique does not qualify and never satisfies the gate. The consult prompt
shape, the reasoning-artefact framing, and the output contract are IDENTICAL to
the cross-model consult — the reviewer receives the artefact reference(s) + cited
evidence and returns `SEVERITY | file:line | issue | fix`, or `CLEAN`.

- **Claude author:** dispatch the reviewer via the `Agent` tool as a fresh
  subagent (no shared conversation state), passing the same adversarial consult
  prompt the Claude-side `codex exec` binding would carry. The subagent reads the
  named artefact reference(s) + cited evidence and returns the same
  `SEVERITY | file:line | issue | fix` / `CLEAN` contract.
- **Codex author:** dispatch a **fresh `codex exec` process** (a new process is a
  fresh context with no shared session state) carrying the same consult prompt and
  the same output contract. This is the one case where a Codex-authored artefact
  is reviewed by Codex — permitted ONLY under `review mode: ephemeral`, and only
  through a fresh-context process, never an in-session self-review.

Everything else is unchanged from the default lane: the SAME iterate-to-CLEAN
loop, the SAME profile caps (lightweight 3 / standard 8 / high-risk 12), the SAME
fold-every-finding-before-delivery discipline, and the SAME cap-hit-without-
convergence STOP (§"Iterate-to-CLEAN loop with caps"). Record the pass in the
close-out exactly as for the cross-model pass, noting the mode was `ephemeral`.

## Iterate-to-CLEAN loop with caps

1. Run the pass; fold each finding into the artefact — **fix**, refute with cited
   evidence, or defer-with-rationale — BEFORE commit/delivery (never silently
   drop a finding).
2. Re-run until the reviewer returns CLEAN.
3. **Iteration cap** scales by workflow profile: **lightweight 3 / standard 8 /
   high-risk 12** rounds (`README.md` §"Gate matrix" / §"Cross-model review
   configuration"). Hitting the cap **without** convergence is a structural STOP,
   not a "try harder" prompt — surface the non-convergence to your dispatcher /
   apex via your role's escalation path rather than shipping unreviewed output;
   "continue under the same profile and cap" is not a valid disposition. (The
   worker's diff-review Gate 2.2 has its own cap-hit handling — a WIP-handoff per
   `worker-agent.md` §"Cross-model adversarial review before commit" + lead
   disposition — which is a DIFFERENT pass from this reasoning-artefact consult.)

## Read-only framing

The single `codex exec` / `claude -p` call is a read-only consult that runs no
project test/build and mutates nothing — NOT a `codex review --uncommitted` diff
review. For the read-only **QA** role, this consult is the **one sanctioned
external operation** its Forbidden list carves out (`qa-agent.md` §"Forbidden" →
"Single sanctioned external operation"); it is NOT general `Bash`/network access.
(The **reviewer's** sanctioned external operation is a different pass — its
frozen-surface baseline, `codex review --commit`/`--base`; see `reviewer-agent.md`
§"Cross-model baseline". This skill does not govern that pass.)
