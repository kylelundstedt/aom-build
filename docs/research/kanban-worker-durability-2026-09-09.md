# Kanban Worker Durability — Correction to the Shelley Rationale (2026-09-09)

**Checked:** Hermes Agent upstream Kanban docs (`main` branch,
`website/docs/user-guide/features/kanban.md`) on 2026-09-09, corresponding to
the `v0.21.0` / `v2026.8.31` release recorded in
[current-capabilities-2026-09-03](./current-capabilities-2026-09-03.md).

## What was wrong

An informal rationale for keeping Shelley in the worker layer claimed that raw
CLI workers (claude-code / codex in tmux) lack durability, and that Shelley
uniquely supplies "workers as durable records": stable IDs, resumability, crash
survival, searchable history, and drill-down. That rationale is **stale**
against Hermes `v0.21.0`. Hermes Kanban already provides a durable worker
substrate natively:

- Every task is a row in `~/.hermes/kanban.db` with runs, append-only events,
  comments, and attachments. Upstream explicitly contrasts this with
  `delegate_task`: durable SQLite rows vs. history lost on context compression.
- Workers are full OS processes with named profile identity and persistent
  memory, not anonymous subagents.
- The dispatcher reclaims crashed workers (PID gone, heartbeat TTL expired);
  reclaimed tasks return to `ready` without a failure-counter tick.
- Resumability is a state machine: block → unblock → re-run; a re-spawned
  worker reads the full comment thread as context.
- Per-task workspaces (scratch / `dir:` / git worktree) with declared artifacts
  copied to durable attachment storage on completion.
- Review transitions, per-task model overrides, and PR completion contracts
  gated on GitHub required checks.
- Worker session transcripts persist under the Hermes home; Scarf reads them
  (and board state) over SSH, so management drill-down does not require
  Shelley.

In a hypothetical "Hermes + raw CLIs" topology, the durability, resumability,
search, and drill-down arguments for Shelley therefore collapse: Kanban is that
layer, and in several respects (state machine, review gating, PR contracts) it
is richer than Shelley's conversation store.

## What actually remains distinctive about Shelley

1. **Subscription model access.** IV's customized Shelley consumes IV's Claude
   and Codex subscription credentials. Hermes workers run their own model loop
   against API-style backends and (as of `v0.21.0`, unverified in detail)
   cannot natively consume Claude/Codex subscription auth. Without Shelley,
   frontier coding models cost API rates, or a coding CLI must be nested inside
   a Hermes worker's terminal tool — a model loop babysitting another model
   loop, with the inner agent's reasoning opaque to the transcript.
2. **The coding harness.** Kanban makes Hermes-profile workers durable, but the
   agentic coding quality is Hermes's own loop (iteration caps, budget
   warnings). Claude-code/codex-class harnesses remain the state of the art for
   implementation work; Shelley is the addressable service wrapper around that
   worker class.
3. **Entire evidence capture.** `entire-agent-shelley` `0.1.3` is qualified
   against Shelley's SQLite with lifecycle hooks and full-session projection
   (see current-capabilities note). No equivalent Hermes-worker plugin exists
   in the IV stack today, so only Shelley workers are instrumented for WAP
   audit evidence.

Items 2 and 3 are contingent (integrations could be built); item 1 is the
durable economic/quality core. Summary:

> **Shelley's distinctive value is making IV's subscription-priced frontier
> coding agents addressable, instrumented workers — not worker durability,
> which Hermes Kanban provides natively.**

## Consequence

Pilot 1B's worker-layer evaluation should compare Hermes+Shelley against
Hermes with Kanban-native workers, not against "no durability." Recorded as
[ADR 0005](../adr/0005-worker-substrate-null-hypothesis.md).
