# AOM Contracts

These contracts are the stable boundary between AOM policy and evolving tool
implementations. Provider-native payloads remain behind adapters.

## Contract set

| Schema | Purpose | Authority |
| --- | --- | --- |
| `admission-context.v1` | Authenticated origin and trust-zone decision | Admission gateway/policy |
| `routing-decision.v1` | Immutable worker strategy selected by policy | Worker-routing policy |
| `delegation-attempt.v1` | Correlation of task, worker conversation, and lifecycle | Hermes + worker adapter |
| `memory-record.v1` | Derived semantic context with provenance/staleness | AgentMemory (non-canonical) |
| `evidence-manifest.v1` | Entire session/checkpoint and candidate verification | Entire/evidence adapter |
| `publication-resolution.v1` | Current immutable published Product | Product/WAP registry |
| `management-snapshot.v1` | Disposable Scarf/ScarfGo projection | None; presentation only |

## Common rules

- IDs are opaque and immutable within their domain.
- Timestamps are RFC 3339 UTC.
- `classification` is mandatory on records that may carry sensitive context.
- Cross-domain data is linked by references; authoritative payloads are not
  copied and silently treated as current.
- Mutable state includes a provider revision or event sequence.
- Immutable artifacts include a digest where practical.
- All records identify producer/version and contract version.
- Unknown required enum values fail closed until an adapter is upgraded.

## End-to-end trace

```text
admitted internal request
  → Hermes Kanban task
  → routing decision
  → delegation attempt(s)
  → Shelley conversation/model/execution
  → Entire evidence manifest
  → candidate commit/tree
  → Hermes acceptance
  → WAP audit
  → publication resolution (if published)
```

Kanban remains the current-work authority. Delegation records do not replace task
status; they describe worker attempts linked to a task.

## Validate

```bash
./scripts/validate-contracts
```
