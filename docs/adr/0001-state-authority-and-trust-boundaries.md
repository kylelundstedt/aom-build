# ADR 0001: State Authority and Pilot Trust Boundaries

- **Status:** Proposed
- **Date:** 2026-09-03

## Context

The pilots combine persistent agents, semantic memory, task management,
engineering history, Product state, and management UI. Without explicit
ownership, these systems can make conflicting claims or leak information across
trust boundaries.

## Decision

### State ownership

- Product repository/registry and WAP are the sole authority for canonical and
  published Product state.
- AgentMemory stores derived semantic context only.
- Hermes Kanban stores current work state only.
- Entire stores historical engineering evidence only.
- Scarf/ScarfGo displays projections and sends authenticated operator commands;
  dashboard files are not authoritative state.

Cross-system records contain typed references, never copied authoritative
payloads presented as current truth.

### Trust boundaries

- Personal Hermes and Freddie Product Hermes use separate environments or
  materially equivalent isolation for profiles, credentials, memory, logs,
  backups, and network admission.
- Freddie Product Hermes is internal and privileged. It must not be reachable by
  an external/client prompt path.
- External text may be attached to an internally authored task as untrusted
  input, but it is never treated as an authenticated instruction.
- Workers receive only the least data and capabilities required for a bounded
  assignment. Worker output cannot publish directly.
- PUBLISH remains a deterministic WAP operation with authorized approval.

## Consequences

- Duplicate convenience projections are permitted only when they identify their
  source revision and staleness.
- Memory and evidence can explain a decision but cannot establish current
  publication.
- A Scarf, AgentMemory, Entire, or Kanban outage does not change Product state.
- The pilots require explicit admission and publication interfaces before
  unattended operation.
- Cross-pilot shared AgentMemory is rejected for Phase 1.

## Rejected alternatives

- One database for Product, work, memory, and evidence state.
- Letting a model reconcile conflicting state sources ad hoc.
- Exposing Product Hermes and asking it to sanitize internal information.
- Treating Scarf dashboard JSON or AgentMemory summaries as publication state.
