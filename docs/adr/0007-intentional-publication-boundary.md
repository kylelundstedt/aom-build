# ADR 0007: Intentional Publication Boundary as the Unifying Pattern

- **Status:** Proposed
- **Date:** 2026-09-11

## Context

Two IndustryVault models have been designed separately and turn out to share
one architecture:

1. **Agent Operating Model (AOM).** A trusted interior (Hermes, Bots, Shelley
   workers, AgentMemory, Kanban, Entire) produces Products through
   WRITE → AUDIT → PUBLISH, and external consumption happens only through a
   Concierge over the authorized published Product graph
   (`docs/architecture-contract.md`).
2. **Dataset delivery model.** A factory (DuckDB/DuckLake compute fleet,
   transform code, staging) manufactures client datasets, promotes releases
   through quality/redaction gates, and delivers immutable open-format
   artifacts (Iceberg/Parquet + context bundle) into client-owned object
   storage, where the client's own engines and policy govern consumption.

Without a named common pattern, future contracts (delivery manifests, context
bundles, admission interfaces) risk restating — or worse, diverging from — the
same rules. This ADR names the pattern once so both models, and future
boundary-crossing designs, cite a shared parent.

## Decision

Adopt the **Intentional Publication Boundary** as the governing pattern for
any interface between a trusted IndustryVault interior and untrusted external
consumers (clients, client agents, public surfaces).

```text
INTERIOR (trusted, messy, accountable)
  unrestricted context, working state, methodology, iteration
       |
       v
PROMOTION GATE (deliberate, audited, versioned)
  WRITE -> AUDIT -> PUBLISH
       |
========= the only interface that exists =========
       |
       v
PUBLISHED SURFACE (immutable, self-describing, composable)
       |
       v
CONSUMERS (bring their own policy, engine, agents)
```

### Invariants

1. **Interior freedom, exterior discipline.** Inside the boundary anything
   goes: unpublished state, raw transcripts, transform code, privileged
   agents with full context. Nothing interior is ever an interface. The
   exterior sees only deliberately promoted artifacts.
2. **Promotion is a gated, versioned act — not a filter.** Never sanitize
   unrestricted interior information at read time. Publish intentionally,
   then let consumers use only the published surface. Sanitize-on-read is a
   policy hoping to hold; publish-intentionally is a topology that cannot
   fail open.
3. **Published artifacts are self-describing and immutable.** A release
   carries its own interface: schema, semantics, metric definitions,
   coarse-grained lineage/provenance, quality results, limitations, release
   history, and agent-facing documentation. Methodology (interior) stays
   home; semantics (surface) travel with the artifact. Published versions are
   never mutated; supersede by releasing.
4. **Composition and authorization operate only on published versions, as
   separate relations.** Dependencies form a DAG of immutable published
   versions. Entitlement/authorization is a distinct, deterministic,
   pre-retrieval relation — in the dataset model, implemented by the
   client's own IAM over their own storage.
5. **Accountability stays interior; capability is delegated outward.**
   IndustryVault owns what was published (correctness, freshness, delivery
   integrity — the pager) regardless of who or what consumes it. Consumers
   own consumption: query cost, performance, access policy, downstream use.

### Threat rule (topological, not instructional)

Any agent or service exposed to arbitrary external prompts/queries must be
*constructed* with access only to the published surface — no credentials or
retrieval paths into the interior. Prompt injection then has nothing
privileged to exfiltrate. This restates the ADR 0001 / AGENTS.md admission
rule at pattern level: enforce through topology and admission control, never
through prompt instructions alone.

### Instantiation map

| Invariant | AOM | Dataset delivery |
| --- | --- | --- |
| Interior | Hermes + Bots + Shelley, AgentMemory, Kanban, Entire | Factory: compute fleet, DuckLake, transform code, staging |
| Gate | WAP (WRITE → AUDIT → PUBLISH) | Manufacture → quality/redaction gates → atomic release commit |
| Published surface | Published Product versions + docs/provenance | Iceberg/Parquet + context bundle in client bucket |
| Consumer interface | Concierge over authorized published graph | Client engines + optional read-only MCP over bundle + data |
| Threat rule | Product Hermes with unpublished state never accepts arbitrary external prompts | Factory never receives client queries; delivery MCP holds no interior credentials |
| Policy locus | Entitlements, deterministic, pre-retrieval | Client IAM/KMS/bucket policy |
| Composition | Immutable published Product DAG | Versioned dataset dependencies + release manifests |

The pattern nests: worker → Hermes (Hermes audits and owns worker output) →
published Product → client are the same gate applied at increasing scope.
Hierarchy is context compression; each level promotes only what it stands
behind.

### Rules for new work

- Any new boundary-crossing contract in `contracts/` must identify its
  interior, gate, published surface, and policy locus in terms of this ADR.
- Deviations from an invariant require a superseding or amending ADR, not an
  exception in the contract.
- Adversarial review of published surfaces (can a consumer reconstruct
  interior methodology materially faster than from the raw artifact alone?)
  is a release-gate concern and should be automated where practical.

## Consequences

- AOM and dataset-delivery contracts share one vocabulary; the planned
  context-bundle schema and delivery-manifest schema become instantiations,
  not new frameworks.
- The pattern forbids convenience shortcuts that would blur the boundary:
  live query pass-through to interior systems, read-time redaction proxies,
  publishing pipeline-tool metadata wholesale (e.g., dbt `manifest.json`),
  or exposing interior-credentialed agents to external prompts.
- Cost: every external ask must be answered by publishing something, which
  is slower than opening a connection. This is accepted as the price of a
  boundary that cannot fail open.
- Alignment with existing decisions: ADR 0001 (state authority, WAP as sole
  publication authority), ADR 0002 (versioned contracts and adapters), and
  the architecture contract's core invariants 7–10 are all consistent with
  and now framed by this pattern.
