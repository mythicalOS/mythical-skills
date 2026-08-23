# CLAUDE.md

Read `AGENTS.md` first — the harness-neutral source of truth for this repo. It does **not**
override your active role contract. The import below loads it for Claude Code.

@AGENTS.md

Claude-specific notes:

- Skills here resolve into consuming projects as `.claude/` plugins (e.g. `agent:<name>`) via
  the consumer's setup script — an edit here reaches sessions only after that project re-links,
  so don't expect a live session to see your change.
