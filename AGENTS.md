# AOM Build Agent Instructions

## Authority

- Treat `docs/architecture-contract.md` as constraints.
- Treat `docs/hermes-scarf-pilot.md` as the current execution plan.
- Preserve the hard split among Product/WAP authority, AgentMemory semantic
  context, Hermes Kanban current work, Entire evidence, and Scarf presentation.
- A Product Hermes that can access unpublished state must never accept arbitrary
  external prompts. Enforce this through topology and admission controls, not
  prompt instructions alone.

## Bootstrap safety

- Do not modify Personal Hermes, `klundstedt-mini`, `personal-mcp`, or the
  `freddie-sflld` VM/repository without explicit authorization.
- Do not commit secrets, personal records, unpublished Product data, runtime
  memories, raw transcripts, or Entire checkpoints.
- Use only synthetic/redacted fixtures in this repository.
- Prefer versioned contracts and small adapters over a new control plane.
- Do not introduce Paperclip, AgentView, FruVisi, Manager/CEO Hermes hierarchy,
  Client Concierge, or a custom AOM cockpit for Phase 1.

## Change discipline

- Record architectural changes as ADRs.
- Update contract schemas and examples together.
- Run `./scripts/validate-contracts` before committing.
- Verify evolving upstream behavior before relying on it; record the checked
  version/date in `docs/research/`.
