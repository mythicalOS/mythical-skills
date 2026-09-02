---
name: remember
description: >-
  Durably record ONE project lesson, decision, or non-obvious fact into tier-1
  memory (`docs/memory/`) so future sessions recall it. Use when you learn
  something a fresh session would otherwise have to rediscover — a sharp gotcha,
  a standing directive, a hard-won constraint — and especially when the operator says
  "remember this". Drives the deployment's sanctioned writer (reached in-session
  via the `memory.append` MCP tool), which enforces no-bleed
  scope, collision-free naming, and the atomic record+index bijection — so you
  never hand-write a record file or hand-edit `MEMORY.md`
  (that path is fragile and bypasses every invariant). Procedural only: WHETHER a
  lesson is worth persisting, and whether your role may write `docs/**`, is
  governed by your role contract and the floor write-path guard — this skill is
  the HOW, never the whether.
assumes:
  - |
    Claude Code roles read/invoke this via the native Skill tool or `Read`;
    Codex roles read this file via `functions.exec_command`. Both lanes reach
    the same `memory.append` MCP tool, composed per session by the deployment.
  - |
    The consuming project carries a tier-1 memory store (`docs/memory/` with
    the sanctioned writer behind `memory.append`). Where no such store or tool
    is composed, there is nothing to write and this skill does not apply.
---

# remember

Tier-1 project memory is **markdown in-git** under `docs/memory/` (one body per
record in `records/`, one pointer line per record in `MEMORY.md`). How it is
recalled is the deployment's choice: some import `MEMORY.md` into every session
(e.g. via the project `CLAUDE.md`), others serve records selectively through a
recall tool — either way the store below is the same. The **only** sanctioned
writer is the one the deployment composes behind `memory.append`.
**The canonical in-session write path, for every role, is the `memory.append`
MCP tool** (below) — the deployment's own CLI (§"Outside a session") drives the
same writer but is distiller/operator tooling, not an in-session instruction. Never
hand-write the record file or hand-edit `MEMORY.md`: doing so skips the no-bleed
scope check, the seq-collision-free exclusive create, and the atomic
record↔pointer write (a half-finished hand-edit leaves the index and records out
of sync).

## When to store — and when not to

Store the **non-obvious, durable** thing a fresh session would otherwise
rediscover the hard way:

- a standing directive or decision with its **why** ("the operator wants X driven, not buffered, because …");
- a sharp gotcha (an env var that must be set, a tool that hangs without a flag);
- a constraint or boundary that isn't visible in the code.

Do **not** store what the repo already records — code structure, a past fix in
git history, anything in `CLAUDE.md`/`AGENTS.md`, or facts that only matter to the
current conversation. If asked to "remember" one of those, capture instead what
was *non-obvious* about it.

Keep each memory to **one fact**. The **first line becomes the `MEMORY.md` index
summary**, so lead with the lesson in one sentence, then add the why/how below it.

## Store a lesson (the `memory.append` MCP tool — canonical, every role)

Call the **`memory.append`** MCP tool on the deployment's coordination-bus bridge. The bridge performs the
tier-1 write **host-side, on your behalf**: same sanctioned writer, same `docs/memory/`
destination, no `Write`/`Bash` tool needed. This is the **canonical in-session write
path for every role** — it is granted to **every bus-connected role** (all roles except
`devil`, which has no bus), so a command-capable role and a read-only review role use
the identical mechanism; neither hand-writes a record file nor needs a teammate or the
retirement distiller to persist a lesson now.

```jsonc
// tool: mcp__<server>__memory_append   (<server> = the bridge server name your deployment pins)
{
  "content": "Lead delivery directive = drive idle work forward, not buffer back.\nWhy: …\nHow to apply: …",
  "kind": "observation",   // observation | decision | event | reference (default observation)
  "priority": 1,            // tier-1 priority (default 1)
  "dry_run": false          // true → full preflight, writes nothing (same refusals as a real write)
}
```

You supply only the **lesson body** (its first line becomes the `MEMORY.md` summary) and
`kind`/`priority`/`dry_run`. **All provenance is derived from your session env — you
cannot set or forge it:** `project` is the launched repo (`AGENT_BUS_COORD_REPO`; the
tool **fails closed** if it is unset — no project scope, no write), `source` is
`<your-role>-directed`, `session` is your agent slug. So you can neither stamp a false
author nor write into another project's memory. Every guarantee below (no-bleed,
no-clobber, atomic record↔pointer) holds identically — it is the same writer the
deployment's CLI drives outside a session (§"Outside a session").

> Because tier-1 is recalled into every future session, a poisoned "lesson" persists until
> a human removes it. This durable surface is an accepted, bounded tradeoff under the
> operator's "every role can save memory, no exception" directive; the deployment's
> decision record carries the full rationale.

## §"Outside a session" — the deployment's distiller / operator CLI

Not an in-session instruction — in-session, every role uses the MCP tool above.
The same sanctioned writer is also drivable outside a bus-connected session by
the deployment's own CLI, which exists for the **external fresh-context
distiller** (retirement distill) and for an **operator** working directly in a
terminal. That CLI — its location, flags, and invocation — is deployment
tooling, documented in the deployment's own docs, never here. Whatever drives
the writer, every guarantee below holds identically.

## What it guarantees (so you don't re-implement it)

- **No cross-project bleed** — a record is refused unless its scope matches the
  authorized project; the MCP tool derives `project` from your session env and the
  deployment CLI binds it explicitly, so neither path can be told to write into
  another project's memory.
- **No clobber** — sequence numbers are probed for a free slot and the body is
  created exclusively; an existing record is never overwritten.
- **Record + pointer are all-or-nothing** — the `records/*.md` body and its
  `MEMORY.md` pointer are written together; if the index update fails, the record
  is rolled back, so the store never holds an orphan body the index doesn't
  address. A duplicate pointer is skipped (idempotent re-index). You never edit
  `MEMORY.md` by hand.

## Authority stays external

This skill restores the *mechanism* of persisting a lesson. It does **not** decide
whether a lesson should be persisted, grant `docs/**` write scope, or authorize a
commit or a branch publication. Your role contract and the floor write-path guard govern all of
that. The external fresh-context distiller remains the primary tier-1 populator
(it distills retired-session transcripts, via the deployment's CLI —
§"Outside a session"); the `memory.append` MCP tool is the in-session directed
path for a lesson worth recording now.
