# Implementation Backlog

**Status:** Proposed  
**Rule:** Items marked `EXTERNAL` require separate authorization after bootstrap review.

Priority meanings: **P0** blocks pilot safety/correctness; **P1** required for a
pilot; **P2** improves evaluation or operations but is not a launch blocker.

## Common/bootstrap

| ID | Pri | Location | Work | Depends on | Acceptance |
| --- | --- | --- | --- | --- | --- |
| C-001 | P0 | AOM-BUILD | Confirm the state-authority matrix and ADR 0001 | Kyle review | Every state question has one authority; no overlapping publication authority |
| C-002 | P0 | KYLE | ~~Confirm canonical Product ID~~ **Resolved 2026-09-03:** `freddie-sflld`; `freddie-sflpd` occurrences are typos (ADR 0003) | none | One stable ID is used in configs, traces, WAP, and evaluation |
| C-003 | P0 | KYLE | ~~Approve trust topology~~ **Resolved 2026-09-03:** separate Personal Hermes VM and Product VM; operator-only ingress (ADR 0003) | C-001 | Product Hermes has no externally prompted route; Personal and Freddie state are isolated |
| C-004 | P0 | AOM-BUILD | Finalize admission, routing, delegation, memory, evidence, publication, and management schemas | C-001 | Schemas validate examples and encode authority/classification fields |
| C-005 | P0 | AOM-BUILD | Implement Shelley adapter capability probe and fixture-based parser | C-004 | Experimental CLI drift fails closed; raw CLI JSON is not exposed to callers |
| C-006 | P0 | AOM-BUILD | Implement idempotent-at-AOM-layer worker creation/reconciliation | C-005 | Ambiguous create exposes duplicate risk and can reconcile by delegation marker |
| C-007 | P0 | AOM-BUILD | Implement worker-routing decision engine from versioned policy | C-004 | Output is immutable, explainable, and separates role/capability from model ID |
| C-008 | P0 | AOM-BUILD | Implement append-only delegation/evidence correlation | C-004,C-005 | Hermes → task → conversation/model → evidence → candidate/WAP is navigable |
| C-009 | P0 | AOM-BUILD | Implement publication resolver adapter interface | C-004,C-002 | Only resolver output can answer current published version |
| C-010 | P1 | AOM-BUILD | Implement disposable Scarf management-snapshot generator | C-004,C-008,C-009 | Output includes source revisions/staleness and changes no authoritative state |
| C-011 | P0 | AOM-BUILD | Add security and redaction tests | C-004 | Secrets, raw personal content, unpublished data, and transcripts are rejected from fixtures/reports |
| C-012 | P1 | EXTERNAL | Verify exact Hermes/Scarf compatibility on a disposable host | Kyle authorization | Chosen versions pass ACP, Kanban, profile, dashboard, and remote diagnostics checks |
| C-013 | P1 | EXTERNAL | Establish backup, restore, retention, and deletion expectations | C-003 | Restore is tested; ownership and retention are documented per state store |
| C-014 | P1 | AOM-BUILD | Build systemd/config templates with placeholders only | C-012,C-013 | Templates use unprivileged users, loopback/private binds, and no embedded secrets |
| C-015 | P1 | EXTERNAL | Inventory model availability/privacy/capacity on target VMs | Kyle authorization | Fable/Sol/Luna/local-Qwen mappings are explicit; unsupported routes fail closed |
| C-016 | P2 | AOM-BUILD | ADR + schema support for the family → product → instance hierarchy (see `iv-business-model.md` §2.1 and Appendix A, CMG example): release identity as tuple (family/mapping versions, product, client instance, as-of, revision, coverage level); versioned source→canonical mappings; composite comparability floor; coverage level orthogonal to assurance tier | first proprietary-core client engagement | Resolver, entitlement, and manifest schemas distinguish family, product, and instance; instance releases pin family, product, mapping, and upstream release tuples; corrections republish same as-of at new revision |

## Pilot 1A — Personal Context

| ID | Pri | Location | Work | Depends on | Acceptance |
| --- | --- | --- | --- | --- | --- |
| P1A-001 | P0 | KYLE | Select Personal Hermes host and approve personal-data scope | C-003 | Host/trust zone and allowed sources are explicit |
| P1A-002 | P0 | AOM-BUILD | Finalize read-mostly policy and evidence-grounding instructions | P1A-001 | Consequential external actions are denied; source retrieval is required when evidence matters |
| P1A-003 | P0 | EXTERNAL | Verify `personal-mcp` transport, auth, tool list, source identifiers, and auditability | authorization | No writes are available or they are mechanically denied; result citations can identify source records |
| P1A-004 | P1 | EXTERNAL | Install/configure dedicated Personal Hermes profile/environment | C-012,P1A-001 | Separate profile/home, credentials, gateway, logs, and backups |
| P1A-005 | P1 | EXTERNAL | Deploy isolated AgentMemory instance and validated Hermes provider plugin | C-012,C-013 | Loopback/private bind, per-pilot data directory, auth if non-loopback, export/delete test |
| P1A-006 | P1 | EXTERNAL | Configure `personal-mcp` in Hermes | P1A-003,P1A-004 | Evidence retrieval works without putting credentials in config/repo |
| P1A-007 | P1 | EXTERNAL | Configure Scarf and ScarfGo operator access | P1A-004 | Key-based SSH, device key handling, reconnect, and diagnostics pass |
| P1A-008 | P1 | BOTH | Run persistent-vs-fresh evaluation cases | P1A-005..007 | Paired results exist for history reconstruction, meeting prep, commitments, and follow-ups |
| P1A-009 | P1 | BOTH | Track recall/evidence failures and time saved | P1A-008 | Metrics distinguish missed/false/stale recall, source-grounding failures, and manual search time |
| P1A-010 | P0 | KYLE | Decide continue/stop/change | P1A-009 | Decision cites measured value versus fresh MCP-enabled agent |

## Pilot 1B — `freddie-sflld` Product Operations

| ID | Pri | Location | Work | Depends on | Acceptance |
| --- | --- | --- | --- | --- | --- |
| P1B-001 | P0 | KYLE | Confirm VM/repo, Product ID, Product owner, and publication approver | C-002,C-003 | Names and authority are unambiguous |
| P1B-002 | P0 | EXTERNAL | Read-only inventory of repo, data flows, audit, WAP, publication registry, and security exposure | authorization,P1B-001 | Current publication can be resolved deterministically; no Product changes made |
| P1B-003 | P0 | AOM-BUILD | Bind publication resolver and WAP adapter contract to actual interfaces | P1B-002 | Candidate, audit, publish, and resolve operations have explicit inputs/errors |
| P1B-004 | P1 | EXTERNAL | Install/configure internal-only Product Hermes | C-012,P1B-001 | Only approved internal operators can reach it; no public/messaging allow-all route |
| P1B-005 | P1 | EXTERNAL | Create dedicated AgentMemory instance and Hermes provider | P1B-004,C-013 | Isolated from Personal memory; canonical Product facts remain source-linked and non-authoritative in memory |
| P1B-006 | P1 | EXTERNAL | Initialize dedicated Hermes Kanban board in manual orchestration mode | P1B-004 | Board is hard-isolated; auto-decompose and autonomous follow-up creation are disabled initially |
| P1B-007 | P0 | EXTERNAL | Enable IV-qualified Entire + Shelley capture in Product repo | P1B-002 | New, resumed, committed, and failed turns produce verifiable checkpoints without blocking Shelley |
| P1B-008 | P1 | EXTERNAL | Deploy Shelley worker adapter and target model mapping | C-005..008,C-015 | Create/continue/read/archive work; actual model and conversation ID are recorded |
| P1B-009 | P1 | BOTH | Run orientation exercise | P1B-002,P1B-004..008 | Hermes documents source, grain, schema, domains, mappings, audits, WAP, lineage, limits; only genuine gaps become tasks |
| P1B-010 | P1 | BOTH | Generate Scarf dashboard projection | C-010,P1B-006,P1B-009 | Shows attention, work, workers, evidence gaps, and current publication with staleness |
| P1B-011 | P0 | KYLE | Select one bounded useful improvement and assurance/locality requirements | P1B-009 | Acceptance criteria and publish authority are explicit |
| P1B-012 | P1 | BOTH | Execute formulate → critique → reconcile → implement → review routing | P1B-008,P1B-011 | Each stage has an immutable routing decision and independent review where required |
| P1B-013 | P0 | BOTH | Verify evidence against candidate commit/tree | P1B-007,P1B-012 | Entire checkpoint is durable and matches reviewed candidate; gaps are explicit |
| P1B-014 | P0 | EXTERNAL | Run existing AUDIT and conditionally PUBLISH | P1B-003,P1B-013 | Failed audit blocks publish; pilot publish requires authorized human approval |
| P1B-015 | P1 | BOTH | Answer diagnostic questions repeatedly | P1B-009..014 | “Published now” resolves from WAP; “why X” distinguishes Product facts, memory, and evidence |
| P1B-016 | P0 | KYLE | Decide continue/stop/change | P1B-015 | Decision weighs supervision reduction, correctness, overhead, and boundary preservation |

## Validation/evaluation

| ID | Pri | Location | Work | Depends on | Acceptance |
| --- | --- | --- | --- | --- | --- |
| V-001 | P0 | AOM-BUILD | Contract/schema validation in CI/local script | C-004 | All examples and policy JSON validate |
| V-002 | P0 | AOM-BUILD | Admission/security failure tests | C-003,C-011 | Forged/external origins are rejected before model invocation |
| V-003 | P0 | AOM-BUILD | State-authority conflict tests | C-009 | Stale memory/dashboard/Entire claims never override WAP/Product authority |
| V-004 | P0 | AOM-BUILD | Shelley retry/drift/event-order tests | C-005,C-006 | Duplicate/out-of-order/changed output produces deterministic failure or reconciliation |
| V-005 | P0 | AOM-BUILD | Routing privacy and independence tests | C-007 | Local-only work never routes to cloud; required independent review is enforced |
| V-006 | P0 | BOTH | Entire evidence failure tests | P1B-007 | Pending, missing, mismatched, or unavailable checkpoints cannot satisfy evidence requirements |
| V-007 | P1 | BOTH | Scarf/ScarfGo management UX study | P1A-007,P1B-010 | Kyle can see status/exceptions and drill into Shelley only when needed |
| V-008 | P1 | BOTH | Pilot scorecard and recommendation | P1A-009,P1B-015 | Report compares baseline and pilot on persistence, delegation, state/evidence, UX, security, and overhead |

## Critical path

`C-001 → C-004 → C-005/C-007/C-008 → C-012/C-015 → P1B-002 → P1B-003/P1B-007/P1B-008 → P1B-009 → P1B-011 → P1B-012 → P1B-014 → V-008`

Pilot 1A can run in parallel after `C-012`, `C-013`, and `P1A-003`.
