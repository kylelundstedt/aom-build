# Evaluation Rubric

Score each dimension from 0–3 and include concrete evidence.

| Score | Meaning |
| --- | --- |
| 0 | Failed, unsafe, or materially worse than baseline |
| 1 | Works occasionally but adds meaningful overhead/risk |
| 2 | Useful with manageable issues |
| 3 | Clearly improves baseline and preserves boundaries |

## Dimensions

### 1. Persistence

- Same Hermes becomes more useful over time.
- Relevant memory appears without excessive noise.
- Stale/conflicting memory is labeled and does not override authority.
- Comparison against fresh agent is explicit.

### 2. Delegation

- Hermes decomposes bounded work without offloading accountability.
- Worker-routing improves quality, cost, latency, or human attention.
- Model/worker choices are explainable and policy-backed.
- Human can understand current work without reading every worker transcript.

### 3. State and evidence separation

- Product/source/WAP, AgentMemory, Kanban, Entire, and Scarf roles remain clear.
- “What is published?” resolves only from Product/WAP.
- “Why did we implement X?” distinguishes Product facts, memory, and evidence.
- Missing evidence creates explicit gaps rather than silent success.

### 4. Management UX

- Scarf/ScarfGo supports status, exceptions, steering, and drill-down.
- Shelley remains useful for worker-level detail.
- Mobile use reduces rather than increases conversation monitoring.
- Dashboard projections show source revisions/staleness.

### 5. Security and boundaries

- Personal and Product states are isolated.
- Read-only Personal pilot policy holds.
- Product Hermes has no external prompt route.
- Hosted/local model routing respects data locality.
- No secrets, raw personal records, unpublished Product data, or raw transcripts
  enter `aom-build`.

### 6. Administrative overhead

- Kanban is useful current-work state, not duplicate bureaucracy.
- Evidence capture is reliable enough for review.
- Version/tool drift is manageable through adapters and tests.
- Setup/maintenance burden is justified by reduced context reconstruction.

## Continuation rule

Do not expand to hierarchy, A2A, Concierge, Paperclip, AgentView, FruVisi, or a
custom cockpit unless Phase 1 scores at least 2 in all safety dimensions and
shows measurable reduction in human management burden.
