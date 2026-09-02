# Changelog

All notable changes to the mythical-skills content set are documented here, one
section per released version, newest first. Deployments that pin a version read
the sections between their current pin and an offered target to see what an
upgrade brings. The format follows [Keep a Changelog](https://keepachangelog.com/)
conventions, trimmed to what a content set needs.

## v0.2.0 — 2026-08-27

The coordination doctrine moves the remote off the agent. A session holds no
remote credential and spells no remote-mutating command: it publishes a branch
with `git.push_branch` (worker or lead) and the **lead alone** requests a landing
with `git.request_landing`, which the daemon performs. A deployment pinning this
version needs a container that serves those tools — see `compat.json`.

### Changed
- `branch-lifecycle`: §"Push the branch to the shared remote" is now
  §"Publish the branch to the shared remote" and carries `git.push_branch` — its
  arguments, the daemon-reported `sha`/`ref`, and the worker/lead-only rule.
  §"Merge to main" is the lead-only `git.request_landing`: its arguments, the
  `landing_id` to record, and what each `status` does and does not claim. The
  former "floor execution note" that delegated the merge keystrokes to a worker
  or an operator is gone.
- `coordination-closeout-templates`: the `merge_closeout` record is stated as
  **daemon-authored on the `landed` transition** — no session publishes one, for
any outcome, and only the `landed` status produces one. What the lead carries
  instead is the `landing_id` and the authority the landing ran under. Every
  other status produces no `merge_closeout` at all: a `refused` landing changed
  nothing on the remote and needs only the lead's own reporting, and a `failed`
  one that left the remote changed is published by the lead as a
  `clarification`. The old "merged commands" block is gone.
- `good-night`: the handoff is published with the structured `branch` and
  `head_sha` record fields, carrying exactly what the header line carries
  (`branch` omitted on a detached HEAD; `head_sha` omitted only when `HEAD`
  resolves to nothing at all). The template's `Unpushed work:` line is now
  `Unpublished work:` —
  a body-field rename a handoff author must follow.
- `routed-comms` §1: names the sibling bridge namespaces — read-only
  `workitems.*` and the two `git.*` tools — and how a landing correlates back to
  the `task` record it completes.
- `coordination-parallel-dispatch`, `plan-execution`, `worktree-management`,
  `coordination-wip-handoff`, `code-review-response`, `docs-governance`,
  `adr-authoring`, `pm-master-plan-template`, `verification-completion`,
  `docs-bar-gate`, `good-morning`, `remember`: push mechanics and vocabulary
  swept to the daemon tools, vocabulary included: state that is committed but
  not on the remote is now "unpublished" throughout, and the authority
  statements name branch publication and landing requests rather than a push or
  a merge. The command sweep is enforced, not asserted — the new push-form gate
  fails on any remaining spelling of a remote-mutating command, and it reports
  zero across the tree.
- `adr-authoring`, `pm-master-plan-template`: the roles that own those artefacts
  hold no branch-publication tool — they commit and report the branch + SHA for
  the lead to publish. Only worker and lead may call `git.push_branch`.

### Removed
- Remote feature-branch deletion from the doctrine. No tool can delete a ref, so
  a merged branch stays on the remote until the forge's delete-on-merge setting
  or an operator removes it. Deleting the **local** branch is unchanged.

### Added
- `scripts/check-push-forms.py` — the structural push-form absence gate, wired
  into CI, with a `--selftest` fixture covering the continuation,
  Markdown-prefix, rendered-inline (code span, emphasis, strikethrough, link
  label) and nested-shell forms, a form soft-wrapped across two lines of one
  paragraph, plus the benign look-alikes. Carrier options are read with their
  real arity, short options as the CLUSTERS they are — within one dash token the
  first operand-taking letter takes the rest of the token, or the next token
  when it ends this one AND its operand is mandatory — so a carrier reaches the
  command behind a consumed operand rather than stopping at it. The VCS (which
  accepts no attached or clustered short global option) and the shells follow
  different real rules and are modelled separately, so a shell's script is found
  by parsing its invocation options rather than scanning past them — and the
  shells do not agree with EACH OTHER either, so each carries its own measured
  letter map: bash's `-o`/`-O` and dash's `-o` take the next token and never an
  attached remainder, while zsh's `-o` and ksh93's `-T`/`-R` take an
  attached operand when the token has one and end the cluster there (so
  `zsh -O -c <script>` runs `<script>` and `zsh -oc <opt> <script>` contains no
  `-c` at all). ksh93's `-o` does that but declines a SEPARATE operand that is
  itself an option, so `ksh -o -c <script>` runs `<script>` where every other
  shell eats the `-c`. A bare `+` splits them the same way — bash/dash skip it,
  zsh/ksh93 end options at it — and a `+` token containing a dash splits them
  three ways (bash/dash reject, zsh takes exactly `+-` as end-of-options, ksh93
  parses through). With NO `-c` at all they split once more, and that one needs
  no option spelling: bash/dash/zsh read the first operand as a script FILE,
  while ksh93 opens it as a file and runs its TEXT as a command line when the
  open fails — so `ksh <cmd>`, `ksh -oc <cmd>`, `ksh -o c <cmd>`,
  `ksh +oc <cmd>`, `ksh +-xoc <cmd>` and `ksh -- <cmd>` all execute `<cmd>`,
  and the operands BEHIND that first one are appended to the command line as
  WORDS (it runs the text with a literal `"$@"` after it), so `ksh X=1 <vcs>
  <publish> origin main` publishes without quoting, escaping or any option at
  all — and each appended operand keeps its own boundary, so a nested `-c`
  script or a spaced option value handed over as one operand is reconstructed
  as one word rather than re-split into source. That reconstruction is checked
  against the binary as a whole (25 operand vectors, 25/25 agreeing with what
  ksh93 prints) and is faithful but not exact: the tokenizer discards quoting,
  so an appended operand that looks like an assignment or a keyword is still
  read as one — over-reporting, never a miss, and recorded as a residual.
  Nesting a command line no longer has to shrink it: the walk terminates on a
  LEXICOGRAPHIC pair — (sum of token-value lengths, serialized length) in the
  quote-aware reading, (token count, serialized length) in the quote-naive one,
  since neither quantity falls in both — after the reconstruction became the
  first producer that can grow a string and a 50-byte line reconstructing to 54
  was silently dropped. The visited set is a de-duplicator, not the termination
  proof: it stops a string that recurs, never one that grows.
  A NAME is not an implementation, so the ambiguous
  `sh` and `ksh`
  are each read as a UNION of models — including the minimal POSIX one, which is
  how an unmeasured shell's bare letters still yield a script candidate, and
  including ksh93, which keeps the first-operand behaviour when it IS `/bin/sh`.
  The maps are measured (bash 3.2.57, dash, zsh 5.9, ksh93u+) and none claims to
  describe mksh, pdksh or busybox ash, which this host cannot run; that
  residual is named as a class in the module docstring — renamed from
  "unmeasured-arity", which was too narrow in both halves, and widened with a
  fourth source: an unprobed interaction or fallback inside a binary that WAS
  measured, plus the sharper form of it, a behaviour that was probed and
  recorded and that no branch acted on. It
  also records that the parser is measured-complete over its recorded probes and
  NOT proven-complete over the grammar: an earlier claim that the token kinds
  were enumerated in full was falsified three times and is retracted there, as
  is the claim that a miss additionally required an implausible option spelling.
  Every execution carrier,
  every carrier option the scanner models as consuming an operand, the short
  letters among them split by mandatory vs optional operand, every
  operand-consuming VCS/forge global option, the forge API's
  own operand-taking short options, each shell's invocation-option arity and the
  models each shell NAME is read under, and a
  selection of the flags that
  must consume none — every optional-operand form among them, which is where
  that drift happens — is enumerated BY HAND in the fixtures, not read from the
  scanner's rule tables, and exercised through the real parse, so dropping an
  entry from a rule table, or changing its arity, fails the selftest. Those
  carrier tables are the platform UNION (BSD-only `xargs -J/-R/-S`, `env -P` and
  FreeBSD `env -L/-U` beside GNU-only `ionice` and `xargs -e/-i/-l`), which can
  only over-detect. Zero
  findings tree-wide is the acceptance.
- `scripts/check-bridge-prefix.sh` — the bridge-prefix absence gate, wired into
  CI: the retired MCP server prefix cannot re-enter shipped content.

## v0.1.0 — 2026-08-23

First tagged release of the skill content set: 31 skills across the `agent:` and
`mythical:` namespaces, as consolidated after the 2026-08 review wave.

### Added
- The full skill set — coordination (routed comms, WIP handoff, closeout
  templates, branch lifecycle), review (cross-model review, verification
  patterns, structural-refactor verification, docs-bar gate), planning
  (design exploration, implementation planning), memory (remember), and the
  role-support set.
- `compat.json` — machine-readable minimum container version for this release.
- Repository governance for the public release: a trademark policy, a DCO sign-off
  contract for contributions, a pull-request template, and a Dependabot policy that
  keeps the SHA-pinned CI action current.

### Changed
- `cross-model-review`: the review-route body documents the four optional label
  fields (`issue`, `issue_title`, `trigger`, `tag`) and the runner-appended
  verdict trailer.
- `remember`: the recall mechanism is described deployment-neutrally (import-based
  or selective tool-served recall).

### Removed
- `code-review-request` — merged into `branch-lifecycle`
  §"Reviewer-gate input prep (pre-handoff)".
