# Task Metadata Convention (Pilot)

Every delegation must stay navigable: **Hermes → Kanban task → Shelley
conversation → model → evidence**. The pilot tests whether Hermes Kanban
carries this naturally; until proven, attach this YAML block to each task that
delegates work (as the task body's final section, or a task comment when the
body is long):

```yaml
task:
  id: FREDDIE-184
  owner: freddie-product-hermes
  status: in_progress

worker:
  type: shelley
  vm: freddie-sflld
  conversation_id: 8e7c...
  model: gpt-5.6-luna        # the model that actually ran

evidence:
  entire_checkpoint: ...      # once known; "pending" until then
```

Rules:

- Update `worker.conversation_id` immediately after starting a worker.
- One block per delegation; multiple workers on one task get multiple blocks.
- `evidence.entire_checkpoint` is filled from `entire checkpoint list` after
  the work lands; `pending` is an honest and acceptable value.
- Kanban remains the authority for task **status**; this block only records
  the delegation links.

That's the whole convention. If Kanban's native fields/attachments turn out to
carry this better (hypothesis 5), switch to them and note the finding.
