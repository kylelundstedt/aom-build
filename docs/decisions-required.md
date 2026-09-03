# Decisions and Questions Requiring Kyle

## Resolution log

**2026-09-03 — Kyle resolved the P0 decisions as follows:**

| ID | Resolution |
| --- | --- |
| D-001 | **Resolved:** canonical ID is `freddie-sflld`. All `freddie-sflpd` references in the architecture documents are typos for the Freddie product (note: `fannie-sflpd` remains a distinct product name). |
| D-002 | **Resolved:** separate Personal Hermes VM and separate `freddie-sflld` Product VM. |
| D-003 | **Resolved (default accepted):** operator-only ingress via Scarf/ScarfGo over authenticated SSH/private control path. |
| D-004 | **Resolved (default accepted):** human approval required for pilot publication. |
| D-005 | **Resolved (default accepted):** validate Scarf 3.0.1 against Hermes 0.21.0; otherwise pin Hermes 0.20.4. |
| D-006 | **Resolved (default accepted):** one AgentMemory instance/data directory per pilot; no cross-pilot sharing. |
| D-007 | **Resolved (default accepted):** BM25-only or local embeddings; no external memory compression initially. |
| D-008 | **Resolved (default accepted):** Entire 0.10.1 + `entire-agent-shelley` 0.1.3 qualified pair. |
| D-009 | **Open:** first Freddie improvement — selected after orientation. |
| D-010 | **Open:** pilot duration and thresholds — to be set before deployment. |

Still unresolved: Fable model identity, self-hosted Qwen endpoint, and the
model-routing/data-egress questions below. See ADR 0003.

No external pilot changes should begin until the remaining open items are
resolved.

## P0 decisions

| ID | Decision | Proposed default | Why it matters |
| --- | --- | --- | --- |
| D-001 | Canonical Freddie Product identifier | `freddie-sflld`; treat `freddie-sflpd` references as an alias/typo until confirmed | Prevents ambiguous trace, WAP, and publication identifiers |
| D-002 | Personal Hermes host | A dedicated Personal Hermes environment, not the Freddie Product VM and not `klundstedt-mini` unless intentionally chosen | Separates personal data, Product data, credentials, memory, and logs |
| D-003 | Product Hermes ingress | Operator-only via Scarf/ScarfGo over authenticated SSH/private control path; no arbitrary messaging/API users | Enforces the no-external-prompt rule structurally |
| D-004 | Pilot publication authority | Human approval required after existing audits | Avoids silently expanding the current WAP authority model during the pilot |
| D-005 | Hermes/Scarf version pair | Validate Scarf 3.0.1 against Hermes 0.21.0; otherwise pin Hermes 0.20.4, Scarf's documented verified target | Upstream versions are moving faster than the pilot plan |
| D-006 | AgentMemory isolation | One instance/data directory per pilot; no Personal↔Freddie shared memory | Prevents cross-boundary semantic leakage |
| D-007 | AgentMemory LLM/embedding policy | Start BM25-only or local embeddings; no external memory compression until data-egress policy is approved | Memory may contain personal or unpublished Product context |
| D-008 | Entire evidence policy | Use IV-qualified Entire 0.10.1 + `entire-agent-shelley` 0.1.3 until jointly re-qualified | The installed integration is version-coupled; latest CLI alone is not automatically safer |
| D-009 | First Freddie improvement | Kyle selects after orientation from genuine gaps | Avoids changing Product state merely to demonstrate autonomy |
| D-010 | Pilot duration and success thresholds | Define baseline period, multi-week duration, and stop criteria before deployment | Prevents post-hoc success definitions |

## Model-routing decisions

1. What exact model/service does **Fable** refer to on the target VM? It is not
   exposed by name on the current `aom-build` Shelley instance.
2. Are Sol and Luna the `gpt-5.6-sol` / `gpt-5.6-luna` models, aliases, or a
   subscription-specific configuration on another VM?
3. Where does self-hosted Qwen run, what API/protocol exposes it, and what data
   classifications may be sent to it?
4. May personal information or unpublished Product content be sent to hosted
   models? If yes, which providers/models and under what retention terms?
5. What per-task cost, latency, concurrency, and subscription-capacity limits
   should routing enforce?
6. When is independent review required, and must it use a different model,
   provider, conversation, or all three?

## Personal Context security questions

1. Which `personal-mcp` sources and date ranges are in scope?
2. Does `personal-mcp` expose any write tools? If so, can writes be disabled at
   the server or integration layer rather than relying on instructions?
3. What source IDs/citations can it return for email, calendar, and meeting
   evidence?
4. May raw retrieved content appear in Hermes logs, AgentMemory, Scarf, Shelley,
   Entire, backups, or evaluation reports? Proposed answer: only where strictly
   required, with raw content excluded from this repository.
5. What are retention, deletion, export, and backup rules for Personal Hermes and
   AgentMemory state?
6. Should ScarfGo access the Personal Hermes host directly over Tailscale/SSH,
   through exe.dev SSH, or another approved path?

## Freddie Product security and WAP questions

1. What VM/repository is canonical for `freddie-sflld`?
2. What deterministic command/API/registry answers “what is published now?”
3. What constitutes an immutable Product version and manifest?
4. Which audits are mandatory, and what evidence is required for each?
5. Who can approve publication, and how is approval represented mechanically?
6. Can Shelley workers write directly to the main worktree, or must each attempt
   use a worktree/branch? Proposed default: bounded worktree/branch per attempt.
7. What unpublished data classifications exist and which model destinations are
   permitted for each?
8. Which credentials does Product Hermes need, and can publish credentials be
   withheld from workers and granted only to the WAP operation?
9. What publication rollback/recovery exists after a bad release?
10. Which parts of Entire evidence, if any, may be intentionally included in a
    published Product? Raw transcripts should remain internal by default.

## Operational questions

- Who owns updates and compatibility qualification for Hermes, Scarf,
  AgentMemory, Shelley, and Entire?
- What uptime is expected for each pilot?
- What backup restore time and data-loss window are acceptable?
- Where should alerts go when a gateway, dispatcher, memory service, or evidence
  capture fails?
- Should Hermes Kanban auto-decomposition and auto-follow-up remain disabled for
  the entire pilot or be enabled after a review checkpoint?
- Are generated `.scarf/dashboard.json` files committed, generated at runtime,
  or both (tracked template plus ignored live projection)? Proposed default:
  tracked template/schema, generated live projection outside Product authority.
