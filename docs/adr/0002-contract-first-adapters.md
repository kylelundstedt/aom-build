# ADR 0002: Contract-First Adapters for Evolving Agent Tools

- **Status:** Superseded in scope by ADR 0004 (retained as Phase 2 reference)
- **Date:** 2026-09-03

## Context

Hermes, Scarf, AgentMemory, Entire, and Shelley's experimental CLI are evolving
quickly. Binding pilot logic directly to command output or internal databases
would make correctness and security depend on undocumented implementation
behavior.

## Decision

Create small versioned AOM contracts and adapters for:

- authenticated request admission;
- Shelley worker lifecycle;
- worker-routing decisions;
- delegation correlation;
- semantic-memory records;
- Entire evidence manifests;
- Product publication resolution;
- Scarf management snapshots.

Adapters expose capability probes and fail closed when required behavior is not
available. AOM-level IDs are stable; provider-native IDs remain opaque
references. Logical worker roles/capabilities are separate from model names.

For Phase 1:

- no custom control plane or task database is introduced;
- Hermes Kanban remains current-work authority;
- the Shelley adapter supports only provider operations that are actually
  advertised/verified;
- ambiguous Shelley conversation creation has at-least-once semantics and must
  be reconciled rather than reported as exactly once;
- Entire capture is best-effort during worker execution, but acceptance policy
  may require a durable verified checkpoint;
- Scarf dashboard data is generated as a disposable projection.

## Consequences

- Upstream upgrades require adapter contract tests before rollout.
- Unsupported cancellation, idempotency, or event behavior is explicit.
- Model substitutions and fallbacks create traceable routing deviations.
- The same adapters and policy formats can be reused by both pilots without
  sharing runtime data.

## Rejected alternatives

- Parsing human-readable CLI output throughout Hermes skills.
- Embedding Fable/Sol/Luna/Qwen names directly in architecture-level schemas.
- Creating separate pilot-specific adapters that drift independently.
- Building Paperclip, a custom cockpit, or a new orchestration framework for the
  initial pilots.
