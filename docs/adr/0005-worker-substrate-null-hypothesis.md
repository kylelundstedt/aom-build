# ADR 0005: Worker-Substrate Null Hypothesis for Pilot 1B

- **Status:** Accepted
- **Date:** 2026-09-09
- **Decided by:** Kyle

## Context

The pilot plan evaluates whether the Hermes/Shelley stack "reduces human
context reconstruction and direct worker supervision." Its hypotheses
(§5.8) implicitly compare the stack against *nothing* — they ask whether
each component helps, not whether a simpler composition would do as well.

Two step-back reviews sharpened this:

1. **Hermes vs. Shelley-only management.** Much of Hermes's claimed value
   (delegation, model routing, scheduling, searchable history) overlaps
   Shelley. Hermes's distinctive residue is proactivity (daemon posture:
   heartbeat, cron, gateway channels), curated durable state (profiles,
   SOUL, memory, Kanban) as first-class structures rather than transcript
   archaeology, and a management-legible accountable identity that Scarf
   reads.
2. **Shelley vs. Kanban-native workers.** The converse claim — that Shelley
   uniquely provides durable, resumable, inspectable workers — is stale
   against Hermes `v0.21.0`, whose Kanban natively provides durable task
   rows, named worker processes, crash reclaim, block/unblock resumption,
   review transitions, and Scarf drill-down. See
   [kanban-worker-durability-2026-09-09](../research/kanban-worker-durability-2026-09-09.md).
   Shelley's distinctive residue is subscription model access (IV's Claude
   and Codex subscriptions), the state-of-the-art coding harness class, and
   the qualified Entire evidence pipeline (`entire-agent-shelley`).

Evaluating either layer against "nothing" would overstate its value.

## Decision

1. **Each layer is evaluated against the strongest simpler alternative, not
   against its absence.**
   - *Hermes null hypothesis:* a designated long-lived Shelley conversation
     plus a Kanban-like file convention would serve as well as a Hermes
     manager. Hermes earns its place only if the pilot shows value from
     proactivity (Hermes initiating/pushing rather than Kyle pulling),
     curated state (Kanban/memory answering "what is happening / what was
     learned" better than Shelley conversation search), or the accountable
     identity + Scarf surface reducing conversations Kyle monitors.
   - *Shelley null hypothesis:* Hermes Kanban-native workers (Hermes
     profiles spawned by the dispatcher) would serve as well as Shelley
     workers. Shelley earns its place only if the pilot shows value from
     subscription-priced frontier coding models, materially better
     agentic coding than the Hermes worker loop, or Entire evidence that
     Kanban's run/event history cannot match for WAP audit needs.
2. **Pilot 1B routes at least one real task through a Kanban-native Hermes
   worker** (no Shelley) where model quality permits, so the comparison is
   observed rather than assumed. This aligns with ADR 0004's instruction to
   prefer native tool behavior and record findings.
3. **The evaluation write-up must state, per layer, which residual
   capability (if any) justified it.** "It worked" is not evidence against
   the null; only the residuals are.
4. No new instrumentation is built for this comparison; it is observational,
   per ADR 0004.

## Consequences

- Pilot 1B hypotheses §5.8 are read with these nulls in mind; hypothesis 1
  already has this shape (same Hermes vs. fresh Hermes + repo context) and
  serves as the template.
- The worker-routing policy gains a legitimate "Kanban-native worker"
  strategy alongside Shelley-backed strategies; worker choice remains
  explicit policy (contract invariant 4).
- If a null hypothesis survives the pilot, the corresponding layer is
  dropped or demoted in Phase 2 rather than carried by architectural
  momentum.
- The metadata-chain invariant (accountable Hermes → task → VM → worker
  conversation) must hold for Kanban-native workers too: task rows and run
  events substitute for Shelley conversation IDs in that chain.
