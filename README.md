# aom-build

Implementation workspace for Industry Vault's Agent Operating Model (AOM) pilots.

This repository converts the architecture documents into reviewable contracts,
policies, pilot templates, validation fixtures, and deployment plans. It is **not**
a runtime state store and must not contain personal records, unpublished Product
data, credentials, AgentMemory contents, Hermes state, Shelley transcripts, or
Entire checkpoints.

## Governing documents

1. [`docs/architecture-contract.md`](docs/architecture-contract.md) — binding architectural constraints.
2. [`docs/hermes-scarf-pilot.md`](docs/hermes-scarf-pilot.md) — current execution plan.
3. [`docs/iv-agent-operating-model.md`](docs/iv-agent-operating-model.md) — full architecture and rationale.

When they differ, the Architecture Contract constrains the pilot plan.

## Bootstrap artifacts

- [`docs/implementation-plan.md`](docs/implementation-plan.md) — phased execution plan and repository layout.
- [`docs/backlog.md`](docs/backlog.md) — concrete backlog with dependencies and acceptance criteria.
- [`docs/decisions-required.md`](docs/decisions-required.md) — decisions and security questions requiring Kyle.
- [`docs/research/current-capabilities-2026-09-03.md`](docs/research/current-capabilities-2026-09-03.md) — verified local/upstream capability snapshot.
- [`contracts/`](contracts/) — versioned integration schemas and interface contracts.
- [`config/`](config/) — initial routing, authority, and security policies.
- [`pilots/`](pilots/) — pilot-specific instructions, checklists, and evaluation cases.
- [`validation/`](validation/) — evaluation rubric and synthetic test catalog.

## State separation

| Concern | Authority |
| --- | --- |
| Canonical Product/source and publication state | Product repo/registry and WAP |
| Learned semantic context | AgentMemory |
| Current work, ownership, blockers, review | Hermes Kanban |
| Historical engineering evidence | Entire |
| Management presentation | Scarf/ScarfGo projections |

No projection or memory system may answer a question owned by an authoritative
source when that source is available.

## Review gate

This bootstrap pass makes no changes to Personal Hermes, `klundstedt-mini`,
`personal-mcp`, or the `freddie-sflld` VM/repository. External deployment starts
only after the unresolved decisions are reviewed and authorized.

## Validate artifacts

```bash
./scripts/validate-contracts
```

The validator uses `uv` to run a pinned `jsonschema` package and validates every
contract example plus the repository JSON configuration.
