# Pilot 1B — `freddie-sflld` Product Operations

**Status:** Design only; no `freddie-sflld` VM or repository changes authorized.

## Objective

Evaluate whether a persistent internal Product Hermes can operate the Dataset
Product with less human context reconstruction and worker supervision while
preserving existing Write → Audit → Publish controls.

## Proposed topology

```text
approved internal operator via Scarf/ScarfGo
  → internal-only Freddie Product Hermes
      → dedicated AgentMemory
      → dedicated Hermes Kanban board (manual orchestration initially)
      → AOM Shelley adapter
          → Fable/Sol/Luna/local-Qwen capability mappings
          → Entire captures engineering evidence in parallel
      → candidate repo/Product state
      → existing AUDIT
      → human-approved PUBLISH
      → immutable published freddie-sflld
```

## Non-negotiable rules

- The Product Hermes is not an external Product interface.
- No arbitrary client/external prompt path may reach it.
- Product/WAP state alone establishes canonical and published facts.
- AgentMemory is derived context, Kanban is current work, and Entire is history.
- Workers do not receive publish credentials or authority.
- A worker completing a turn does not complete the Kanban task and does not mean
  Hermes accepted the result.
- A failed audit, missing/mismatched evidence, ambiguous Product identity, or
  unresolved current publication blocks PUBLISH.

## Initial operating choices

- Dedicated Kanban board rather than tenant-only separation.
- `kanban.auto_decompose: false` and
  `kanban.auto_subscribe_on_create: false` until delegation behavior is reviewed.
- Isolated worktree/branch per write-capable worker attempt unless the existing
  repository has a stronger established mechanism.
- Human publication approval for the pilot.
- Tracked Scarf dashboard template plus generated projection; dashboard values
  carry source revisions/staleness and are never Product authority.

## Execution sequence

1. Read-only environment/WAP inventory.
2. Orientation exercise using `orientation-checklist.md`.
3. Create tasks only for genuine gaps.
4. Kyle selects one bounded improvement.
5. Run the routed worker stages with full delegation correlation.
6. Verify Entire evidence against the candidate tree.
7. Run existing audits.
8. Publish only if authorized and all gates pass.
9. Evaluate with `evaluation-cases.json` and the common rubric.
