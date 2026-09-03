# Worker Routing Policy (Pilot v1)

Which model gets which kind of work. This is **policy, not architecture** —
expect it to change as we learn which strategies work.

## Model roster

| Worker | Model | Access | Good for |
| --- | --- | --- | --- |
| Fable | `claude-fable-5` | Shelley (Anthropic subscription; per-VM login) | Formulating requirements, specs, plans |
| Sol | `gpt-5.6-sol` | Shelley (exe.dev gateway) | Critique, risk analysis, independent review |
| Luna | `gpt-5.6-luna` | Shelley (exe.dev gateway) | Implementation, tool-heavy work |
| Qwen (local) | TBD | klundstedt-mini over tailnet — **endpoint unresolved** | Local/private bounded work, cheap parallelism |

## Default strategies

**High-assurance Product change** (anything touching data semantics, mappings,
or publication):

```text
Fable: formulate requirement / spec / plan
  → Sol: critique semantics, assumptions, risks
  → Hermes: reconcile and approve plan
  → Luna (and/or Qwen when available): implement
  → Sol: review the result (never reviews its own work)
  → Hermes: accept / reject / iterate
```

**Routine bounded work** (docs, small fixes, research, investigation):
Luna directly; add a Sol review when the result feeds a Product change.

**Local-only work** (data that must not leave IV infrastructure):
Qwen on klundstedt-mini only. **Until that endpoint exists, this work is not
delegated to any hosted model — it waits or Kyle decides.**

## Standing rules

- Reviewer must be a different conversation than the author; prefer a
  different model (Sol reviews Fable/Luna work).
- Record the model that actually ran in the task metadata.
- At most 2 workers in parallel until we learn the supervision cost.
- Unpublished Freddie candidate data may go to the hosted models above;
  personal data and anything Kyle designates stricter may not.
- When a model is unavailable, say so in the task and ask — don't silently
  substitute on high-assurance work.
