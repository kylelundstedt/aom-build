# AOM Implementation Plan

**Status:** Bootstrap proposal  
**Date:** 2026-09-03  
**Execution gate:** No pilot environment changes are authorized by this document.

## 1. Objective

Build the smallest reusable contract and adapter layer needed to evaluate:

- **Pilot 1A:** a read-mostly Personal Hermes grounded in the existing
  `personal-mcp` source and augmented by an isolated AgentMemory instance;
- **Pilot 1B:** an internal-only `freddie-sflld` Product Hermes that maintains
  current work in Hermes Kanban, delegates bounded work through Shelley,
  preserves evidence in Entire, and operates the existing Write → Audit →
  Publish lifecycle without weakening the publication boundary.

Success means less human context reconstruction and direct worker supervision,
not merely more agent activity.

## 2. Repository role and proposed structure

`aom-build` is the source for reusable contracts, policies, adapters, templates,
and evaluation methods. Runtime state stays on the relevant pilot environment.

```text
aom-build/
├── AGENTS.md                         repository safety rules
├── config/                           versioned policy inputs
├── contracts/
│   ├── schemas/                      machine-readable interface schemas
│   ├── examples/                     synthetic contract fixtures
│   └── shelley-worker-adapter.md     stable façade over experimental CLI
├── docs/
│   ├── adr/                          architectural decisions
│   ├── research/                     dated capability verification
│   ├── runbooks/                     review/deployment gates
│   ├── backlog.md
│   ├── decisions-required.md
│   └── implementation-plan.md
├── pilots/
│   ├── personal-context/             instructions and evaluation cases
│   └── freddie-sflld/                orientation, WAP, Scarf, evaluation
├── scripts/                          repository validation and later adapters
└── validation/                       cross-pilot rubric and failure catalog
```

Later implementation should add small adapters under `adapters/` only after the
contracts have been exercised with fixtures. Do not create an AOM database or
control plane during Phase 1.

## 3. Authoritative state model

| Domain | Sole authority | Permitted cross-links | Forbidden substitution |
| --- | --- | --- | --- |
| Product/source/WAP | Product repo, audit outputs, publication registry | commit, candidate, audit, immutable publication refs | Memory, Kanban, Entire, or dashboard claiming current publication |
| Semantic memory | AgentMemory instance scoped to one pilot/trust zone | source/evidence refs, confidence, staleness | Publication, authorization, task status, or canonical semantics |
| Current work | Hermes Kanban board | routing, worker, evidence, candidate refs | Product truth or durable historical proof |
| Historical evidence | Entire plus explicit evidence manifests | session, checkpoint, commit/tree refs | Current work state or current publication |
| Presentation | Scarf/ScarfGo projection | deep links and source revisions | Any authoritative transition |

Entire observes work in parallel with repository changes; it is not a gateway
between Shelley and the repository.

## 4. Reusable components built here

1. **Admission contract** — establishes authenticated origin and prevents an
   internal Product Hermes from becoming externally prompted.
2. **Shelley worker adapter contract** — create, continue, inspect, wait, search,
   and archive bounded worker conversations without exposing Shelley CLI output
   as the AOM interface.
3. **Worker-routing policy** — selects a multi-stage strategy from task type,
   assurance, locality, ambiguity, cost, and available capabilities.
4. **Delegation record** — correlates accountable Hermes, Kanban task, routing
   decision, Shelley conversation/model, evidence, candidate change, and WAP
   outcome.
5. **AgentMemory record contract** — marks memory as derived/non-canonical and
   requires provenance, scope, confidence, and staleness fields.
6. **Entire evidence manifest** — records capture state and verifies the evidence
   against the reviewed candidate commit/tree.
7. **Publication resolution contract** — the only interface permitted to answer
   “what is published right now?”
8. **Management snapshot** — disposable Scarf projection with source revisions
   and explicit staleness.
9. **Pilot policy/templates** — instructions, orientation checklist, dashboard
   template, synthetic evaluation cases, and review gates.

## 5. Phased execution

### Gate 0 — review this bootstrap

- Review architecture decisions, backlog, unknowns, and security questions.
- Confirm canonical Product identity and target environments.
- Approve or change the proposed isolation, version-pin, retention, routing,
  and publication-approval decisions.

**Exit:** Kyle authorizes specific external discovery/deployment steps.

### Phase A — common contract and adapter implementation

Performed entirely in `aom-build`:

1. Finalize schemas and contract tests.
2. Implement a local Shelley adapter against fixture output, with a capability
   probe and fail-closed parsing.
3. Implement routing as policy evaluation returning an immutable decision, not
   direct model invocation.
4. Implement append-only delegation/evidence correlation output.
5. Implement management snapshot generation from synthetic provider adapters.
6. Add redaction and no-secret tests.

**Exit:** all adapters pass fixture, retry, drift, and state-separation tests.

### Phase B — read-only environment discovery

Requires later access to pilot systems but no Product modification:

- verify Personal Hermes host selection and `personal-mcp` network/auth model;
- inventory `freddie-sflld` repository, WAP commands, publication registry,
  Entire status, Shelley version/models, and current VM security exposure;
- validate Hermes/Scarf/AgentMemory version compatibility in a disposable or
  non-production environment;
- document backups, restore tests, retention, and credential ownership.

**Exit:** deployment manifests can be populated without guesses.

### Phase C — Pilot 1A deployment and evaluation

1. Install a dedicated Personal Hermes profile/environment.
2. Connect `personal-mcp` read-only.
3. Run a separate loopback-only AgentMemory instance and configure the Hermes
   provider after validating the plugin version.
4. Configure Scarf/ScarfGo over operator-controlled SSH.
5. Run paired persistent-vs-fresh historical-context cases for several weeks.
6. Track missed recall, false recall, stale memory, unnecessary retrieval,
   evidence failures, latency, and time saved.

**Exit:** evidence shows whether persistence adds value beyond fresh MCP access.

### Phase D — Pilot 1B orientation

1. Install an internal-only Freddie Product Hermes on the authorized VM.
2. Use a dedicated Hermes profile, AgentMemory instance/data directory, and
   Kanban board.
3. Enroll the Product repo in the IV-qualified Entire + Shelley capture path.
4. Inspect source, grain, schema, domains, transformations, audits, WAP,
   lineage, limitations, and current publication without changing Product
   semantics merely to demonstrate autonomy.
5. Create Kanban tasks for genuine gaps and produce a Scarf management snapshot.

**Exit:** the Product Hermes can correctly distinguish canonical facts, memory,
current work, historical evidence, and published state.

### Phase E — one bounded Freddie improvement

1. Kyle approves one useful, bounded improvement and publication authority.
2. Hermes creates/uses one Kanban task and an immutable routing decision.
3. Initial high-assurance strategy:
   - formulation capability (intended Fable role),
   - independent critique capability (intended Sol role),
   - Hermes reconciliation,
   - bounded execution (intended Luna and/or local Qwen),
   - independent review (intended Sol role).
4. Every worker attempt is correlated to its Shelley conversation and Entire
   evidence.
5. Hermes accepts/rejects the result; existing AUDIT gates run.
6. PUBLISH remains human-approved for the pilot unless Kyle explicitly changes
   that rule.

**Exit:** one end-to-end trace proves the WAP boundary and evidentiary chain.

### Phase F — evaluation and decision

Evaluate persistence, delegation, state/evidence separation, management UX,
security, and administrative overhead against the baseline. Continue only if
human cognitive burden decreases. Otherwise simplify before adding any hierarchy
or external-facing agent.

## 6. Work-location boundary

### Entirely inside `aom-build`

- contracts, schemas, policies, templates, synthetic fixtures;
- Shelley adapter and capability probes;
- routing decision engine;
- trace/evidence manifest generation;
- Scarf dashboard projection generator;
- deployment manifests and systemd templates that contain no secrets;
- validation harness and evaluation reports using redacted/aggregate data.

### Requires later external changes

- installing/configuring Hermes, AgentMemory, Scarf access, and services;
- connecting to `personal-mcp` and verifying its evidence/citation behavior;
- enabling Entire on the `freddie-sflld` repository;
- adding Hermes instructions, Kanban board, and Shelley adapter on the Product VM;
- inspecting/modifying the Product repository and invoking WAP;
- configuring self-hosted Qwen connectivity and model credentials/capacity;
- running real pilot tasks and collecting sensitive operational evidence.

## 7. Explicit exclusions

Phase 1 does not add Manager/CEO Hermes hierarchy, A2A organizational fabric,
Paperclip, AgentView, FruVisi, Client Concierge, external Freddie agent,
deterministic entitlement implementation, Product DAG rollout, or a custom AOM
cockpit. Reconsider only after measured pilot pressure demonstrates a need.
