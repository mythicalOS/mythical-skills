# mythical-skills

First-party skill content for an agent coordination framework: markdown
procedures ("skills") that autonomous agent sessions load to run coordination
work — continuity handoffs, reviews, planning, verification, routed
communication — in a consistent, auditable way.

This is a standalone content repository: markdown only, no build step, no
runtime. A consuming deployment's setup tooling links skills into its own agent
plugins (where they typically resolve under an `agent:` or `mythical:`
namespace). Nothing in this repo grants any skill to any role — authorization
lives with the consuming deployment's role policies, alongside the companion
playbook repository, `mythical-playbooks`.

## Stability and forking

This skill content is a **living system, not a frozen spec**. Skills are tuned
continuously against real multi-agent operation, and releases may change a
skill's procedure, output shape, or defaults without notice when something is
found to work better. What stays deliberately stable is the authority line: a
skill never grants authority the invoking role's policy lacks, and changes that
would move a role boundary happen in the playbook repository, explicitly —
never as a side effect of skill tuning.

If you depend on today's exact behaviour, **fork this repository and maintain
your own copy** — that is the supported way to pin it. Tracking this repo
directly means accepting behavioural drift in exchange for the improvements.

## Layout

Skills live at:

```text
skills/<name>/SKILL.md
```

`SKILLS-INDEX.md` is the human source of truth for skill existence, path, and
status. It does not grant a skill to any role and does not decide project plugin
linking; the consuming deployment's setup tooling and role-policy layer own
that.

## Vocabulary

The human principal is called the **operator** throughout — the human apex who
holds final decision authority (operator-only overrides, operator-direct
dispatch). A deployment may supply a preferred call-name for the operator at
session start; the skills themselves stay neutral.

## Continuity skills

- `good-morning` - Recalibrates a fresh or resumed agent from durable
  `good-night` handoff records before work continues, then settles each
  consumed record so the store can reclaim it.
- `good-night` - Defines the format of the continuity handoff `good-morning`
  consumes. Every retired session is guaranteed one: the system scribe writes
  it from the session record on the session's behalf, unless the session
  chooses to publish its own first.

Both skills are authored under `skills/` and keep their procedure in `SKILL.md`.
A consuming deployment's setup tooling links them into its agent plugin, where
they resolve as `agent:good-morning` and `agent:good-night`.

## Validation

Run the project-agnostic content check from this repo when changing skill
content:

```bash
scripts/check-project-agnostic.sh
```

CI additionally runs a vocabulary denylist gate over every tracked file (see
`.github/workflows/checks.yml`).

## Contributing

See `CONTRIBUTING.md`. New skills follow the doctrine in
`skills/skill-authoring/` and must pass `scripts/check-project-agnostic.sh`.

## License

Apache-2.0 — see [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE).

The licence covers the content. The **mythical** and **mythicalOS** names and marks are covered separately by [`TRADEMARK.md`](TRADEMARK.md) — you may fork, modify, and redistribute freely; the marks are what let a user tell whose build they are running.
