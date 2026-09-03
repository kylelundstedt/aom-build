# Freddie WAP Interface Contract v1

This is a binding adapter contract for the existing IV Write → Audit → Publish
lifecycle. The actual commands/API are unknown until the `freddie-sflld`
environment is inspected.

## Authority

Only the WAP/Product registry adapter may answer:

> What is published right now, and how do you know?

AgentMemory, Kanban, Entire, Scarf, and worker prose can link to this answer but
cannot provide it authoritatively.

## Interfaces

```text
ResolvePublished(product_id, channel) -> publication-resolution.v1
GetManifest(product_id, version) -> immutable manifest + digest
CreateCandidate(source_ref, change_ref, metadata, idempotency_key) -> candidate_ref
RunAudit(candidate_ref, required_checks, idempotency_key) -> audit_ref
Publish(candidate_ref, audit_refs, approver, expected_registry_revision,
        idempotency_key) -> publication-resolution.v1
```

## Required properties

- Publication resolution is deterministic and pre-LLM.
- Published versions are immutable.
- Product dependencies, if any, are pinned to immutable published versions.
- Candidate and published state have distinct references.
- Failed/missing audits block publish.
- Worker output never invokes `Publish` directly.
- Pilot publish requires human approval.
- Every publish records candidate ref, audit refs, approver, event ID, manifest
  digest, registry revision, and publication time.

## Failure modes

| Condition | Required result |
| --- | --- |
| Product ID/alias ambiguous | reject |
| Resolver unavailable | cannot answer current publication |
| Candidate dependency in published DAG | reject |
| Floating upstream version | reject |
| Failed/missing audit | reject |
| Evidence checkpoint pending/missing for high-assurance change | reject acceptance or publish, per policy |
| Registry revision changed | reject and require re-resolve/retry |
| Worker requests publish | ignore as untrusted worker output |

## Orientation questions

- Where is current published state recorded?
- What command/API gives machine-readable current version and manifest digest?
- What is the immutable version identifier?
- Are release channels supported?
- What audit artifacts are mandatory?
- Where are lineage, provenance, limitations, and release history stored?
- Who/what can publish today?
- How is rollback represented?
