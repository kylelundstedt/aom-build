# ADR 0004: Pilot-First Scope Correction

- **Status:** Accepted
- **Date:** 2026-09-03
- **Decided by:** Kyle

## Context

The bootstrap pass (ADR 0002, Phase A) built a seven-contract schema family,
validation harness, and adapter suite before either pilot environment existed.
Kyle's correction: this is a **pilot to evaluate Hermes and Scarf**, and
front-loading requirements is counterproductive. The pilot plan itself says to
use "the smallest architecture capable of proving or disproving the important
hypotheses" — several of which (Kanban value, management visibility, native-UI
sufficiency) exist precisely to discover whether such instrumentation is needed
at all.

## Decision

1. **The pilots run on native Hermes / Scarf / Shelley / Entire behavior.**
   We install the tools, use them as designed, and observe. No AOM schema
   compliance is imposed on pilot workflows.
2. **Only three build artifacts are pilot prerequisites** (each named by the
   architecture docs):
   - a thin Shelley CLI wrapper skill (the CLI is experimental);
   - an initial worker-routing policy — a readable mapping of stages to models,
     not an enforcement engine;
   - a lightweight task-metadata convention (the ~10-line YAML shape from the
     pilot plan §5.6) so delegations stay navigable.
3. **The contract schemas, adapters, and validation suite are demoted to
   reference material.** They stay in the repo as a design sketch of what a
   hardened Phase 2 could look like — informed by what the pilot actually
   teaches — but they are not requirements, not gates, and not installed on
   pilot VMs.
4. **Up-front rules are limited to the documents' hard invariants**, enforced
   behaviorally and by topology, not by schema validation:
   - the WAP working/published boundary holds;
   - Freddie Product Hermes is never exposed to external prompts;
   - memory/Kanban/Entire/dashboards never substitute for Product/WAP
     authority on publication questions;
   - pilot PUBLISH requires human approval;
   - the two pilots stay isolated (separate VMs, credentials, memory).
5. **Evaluation stays observational.** Track the pilot hypotheses and failure
   modes as originally planned; where native tool behavior already answers a
   need (e.g., Kanban's own run/event history for traceability), prefer it and
   record that finding rather than layering AOM structure on top.

## Consequences

- Phase A code (`src/aom/`, `contracts/`, most of `validation/`) is reference
  material; it carries no maintenance obligation during the pilots.
- The backlog's P0 "contract/adapter" items are reclassified; the critical path
  becomes: resolve remaining decisions → Phase B read-only discovery → install
  and use.
- If the pilots reveal real gaps (drift, traceability loss, boundary
  violations), the reference contracts are the starting point for a considered
  Phase 2 — justified by observed need rather than anticipation.
- ADR 0002 remains recorded but is subordinate to this correction.
