# ADR 0003: Resolved Pilot Topology and Version Pins

- **Status:** Accepted
- **Date:** 2026-09-03
- **Decided by:** Kyle

## Context

The bootstrap pass surfaced ten P0 decisions (`docs/decisions-required.md`).
Kyle resolved eight; two remain open pending orientation and deployment
planning.

## Decisions

1. **Product identity.** The canonical Product ID is `freddie-sflld`.
   Occurrences of `freddie-sflpd` in the architecture documents are typos for
   this Product and must not be treated as a second Product. (`fannie-sflpd`
   remains a distinct, separate Product.) All configs, traces, WAP interfaces,
   and evaluation artifacts use `freddie-sflld` / `product:freddie-sflld`.
2. **Topology.** Two separate VMs: a dedicated Personal Hermes VM and the
   `freddie-sflld` Product VM. No shared profiles, credentials, memory stores,
   Kanban boards, logs, or backups between them.
3. **Ingress.** Product Hermes accepts only authenticated internal operators
   via Scarf/ScarfGo over SSH/private control paths. No public messaging or
   API allow-all routes.
4. **Publication.** PUBLISH requires human approval for the pilot.
5. **Versions.** Validate Scarf 3.0.1 against Hermes 0.21.0 on a disposable
   host; fall back to Hermes 0.20.4 (Scarf's documented verified target) if
   incompatible. Entire stays at the IV-qualified 0.10.1 + plugin 0.1.3 pair.
6. **Memory.** One AgentMemory instance and data directory per pilot,
   loopback-bound; BM25/local embeddings only; no LLM memory compression until
   a data-egress policy is approved.

## Still open

- Fable model identity and self-hosted Qwen endpoint (routing catalog entries
  remain `availability: unresolved`; strategies requiring them fail closed).
- First bounded Freddie improvement (selected after orientation, D-009).
- Pilot duration, baselines, and stop thresholds (D-010).

## Consequences

- The architecture documents in `docs/` are preserved as delivered; the typo
  correction is recorded here and in the decision log rather than by editing
  the source documents.
- Deployment manifests can now name two target environments.
- Phase A adapter implementation can proceed inside `aom-build`.
