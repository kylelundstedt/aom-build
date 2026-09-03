# Freddie Product Orientation Checklist

The orientation phase is read-first. Do not make substantive Product changes
merely to demonstrate agent autonomy.

## Identity and authority

- [ ] Confirm canonical Product ID and aliases.
- [ ] Confirm canonical repository, default branch, and deployment/publication
  environments.
- [ ] Identify Product owner and publication approver.
- [ ] Locate the deterministic current-publication resolver.
- [ ] Record the immutable Product version/manifest format.

## Source and ingestion

- [ ] Enumerate source systems/files/endpoints and credentials by role (not value).
- [ ] Document ingestion entry points, schedules, incremental/full behavior, and
  retry/idempotency behavior.
- [ ] Identify raw/candidate storage and its retention.
- [ ] Record source record identifiers and provenance preserved downstream.

## Dataset structure and semantics

- [ ] Define Dataset grain for every major relation.
- [ ] Inventory schemas, keys, constraints, and important nullability rules.
- [ ] Inventory domains/code sets and their authoritative source/version.
- [ ] Document transformations, mappings, derived fields, and semantic
  definitions.
- [ ] Identify known ambiguities, exceptions, and unsupported cases.

## Quality, audit, and reconciliation

- [ ] Locate all automated and manual audit entry points.
- [ ] Record mandatory gates, thresholds, expected outputs, and failure handling.
- [ ] Document source-to-candidate and candidate-to-published reconciliation.
- [ ] Identify audit evidence that becomes part of the Product versus internal
 -only evidence.
- [ ] Test a non-destructive audit/read path if authorized.

## WAP and publication

- [ ] Document WRITE candidate creation.
- [ ] Document AUDIT invocation and result identity.
- [ ] Document PUBLISH invocation, required authorization, and idempotency.
- [ ] Confirm workers cannot invoke PUBLISH directly.
- [ ] Confirm published artifacts are immutable and dependencies are pinned.
- [ ] Document rollback/recovery and how a superseded version remains addressable.

## Lineage, provenance, limitations, and documentation

- [ ] Trace at least one representative field from source to published output.
- [ ] Locate lineage/provenance manifests.
- [ ] Locate release notes/history and known-limitations documentation.
- [ ] Identify missing or stale documentation.

## AOM state systems

- [ ] Confirm dedicated Hermes profile and ingress policy.
- [ ] Confirm dedicated AgentMemory instance/data directory and memory policy.
- [ ] Confirm dedicated Kanban board and manual orchestration settings.
- [ ] Confirm Shelley adapter version and target model capability mapping.
- [ ] Confirm Entire enrollment and live capture for new/resumed/failed sessions.
- [ ] Confirm Scarf projection source revisions and staleness display.

## Outputs

- [ ] Product orientation report with source references.
- [ ] Publication resolution example produced by the real WAP adapter.
- [ ] State-authority test showing Product, memory, Kanban, and Entire answers are
  distinguished.
- [ ] Kanban tasks for genuine material gaps only.
- [ ] Candidate list of bounded improvements for Kyle, each with risk,
  assurance, data-locality, and expected value.
