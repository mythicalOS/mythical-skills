# Changelog

All notable changes to the mythical-skills content set are documented here, one
section per released version, newest first. Deployments that pin a version read
the sections between their current pin and an offered target to see what an
upgrade brings. The format follows [Keep a Changelog](https://keepachangelog.com/)
conventions, trimmed to what a content set needs.

## v0.1.0 — 2026-08-19

First tagged release of the skill content set: 31 skills across the `agent:` and
`mythical:` namespaces, as consolidated after the 2026-08 review wave.

### Added
- The full skill set — coordination (routed comms, WIP handoff, closeout
  templates, branch lifecycle), review (cross-model review, verification
  patterns, structural-refactor verification, docs-bar gate), planning
  (design exploration, implementation planning), memory (remember), and the
  role-support set.
- `compat.json` — machine-readable minimum container version for this release.
- Repository governance for the public release: `TRADEMARK.md`, the DCO sign-off
  contract in `CONTRIBUTING.md`, a pull-request template, and a Dependabot policy
  that keeps the SHA-pinned CI action current.

### Changed
- `cross-model-review`: the review-route body documents the four optional label
  fields (`issue`, `issue_title`, `trigger`, `tag`) and the runner-appended
  verdict trailer.
- `remember`: the recall mechanism is described deployment-neutrally (import-based
  or selective tool-served recall).

### Removed
- `code-review-request` — merged into `branch-lifecycle`
  §"Reviewer-gate input prep (pre-handoff)".
