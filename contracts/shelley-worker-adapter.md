# Shelley Worker Adapter Contract v1

## Purpose

Provide Hermes a stable, testable façade over Shelley's experimental CLI. The
adapter owns command invocation, JSON parsing, capability detection, retries,
and correlation. Callers never parse Shelley output directly.

## Operations

```text
Capabilities() -> WorkerCapabilities
CreateRun(CreateRunRequest) -> WorkerRun
AppendTurn(run_id, AppendTurnRequest, expected_revision) -> WorkerRun
GetRun(run_id) -> WorkerRun
ReadMessages(run_id, after_sequence?) -> MessagePage
Wait(run_id, after_sequence?) -> event stream / terminal WorkerRun
Search(query, limit?) -> WorkerRunSummary[]
Archive(run_id) -> WorkerRun
Cancel(run_id) -> WorkerRun | unsupported
```

### Verified Shelley v0.959 mapping

| Adapter operation | Shelley CLI |
| --- | --- |
| CreateRun | `shelley client chat -p ... -model ... -cwd ...` |
| AppendTurn | `shelley client chat -c ... -p ...` |
| GetRun/ReadMessages | `shelley client read ...` |
| Wait | `shelley client read -wait ...` |
| Search | `shelley client search ...` |
| Archive | `shelley client archive ...` |
| Cancel | unsupported by verified CLI |

The adapter must probe the installed version/help before declaring these
capabilities.

## Create request

Required fields:

- AOM delegation ID and attempt number;
- Hermes/Kanban task reference;
- immutable routing-decision reference and stage ID;
- logical capability/role and requested model mapping;
- absolute workspace path on the target VM;
- prompt package containing objective, constraints, acceptance criteria, input
  references, and untrusted-input labels;
- side-effect, network, data-locality, assurance, and deadline constraints;
- AOM idempotency key.

## Run response

The adapter returns:

- stable AOM run ID;
- Shelley conversation ID;
- requested role/model and actual model;
- VM/workspace identity;
- adapter and Shelley versions;
- lifecycle state and monotonically increasing adapter revision;
- first/last observed message sequence;
- typed warnings/deviations.

## Semantics

1. One delegation attempt normally maps to one Shelley conversation.
2. A conversation cannot be rebound to a different Kanban task or stage.
3. Hermes acceptance is separate from worker completion.
4. Actual model is recorded independently from requested role/model.
5. Worker prose never changes task, evidence, or publication state directly.
6. Unsupported operations return `unsupported`; the adapter does not simulate
   success.
7. Raw prompts/transcripts remain in Shelley/Entire, not delegation summaries.
8. External/untrusted content is labeled in the prompt package and cannot grant
   capabilities.

## Idempotency and reconciliation

The verified CLI does not advertise backend idempotency. `CreateRun` therefore
has **at-least-once** semantics:

1. Generate a unique marker such as `[AOM-DELEGATION:<id>:<attempt>]` in the
   first prompt.
2. Persist the pending AOM attempt before invoking Shelley.
3. If the command returns a conversation ID, bind it atomically.
4. If the result is ambiguous, search/list for the marker and reconcile.
5. If zero matches exist, retry according to policy.
6. If one match exists, bind it and record recovery.
7. If multiple matches exist, mark `duplicate_risk`, stop automatic progress,
   and require reconciliation. Never claim exactly-once creation.

## Lifecycle

```text
pending → accepted → running → completed | failed | archived
                     ↘ duplicate_risk | unknown
```

- `completed` means Shelley's turn ended, not that Hermes accepted the work.
- Archive of an active run creates an exception; it does not complete its Kanban
  task.
- Events are folded by adapter sequence and provider message IDs. Duplicate or
  out-of-order observations must not regress state.

## Errors

At minimum:

- `unsupported`
- `invalid_request`
- `policy_denied`
- `provider_unavailable`
- `provider_output_changed`
- `model_unavailable`
- `workspace_unavailable`
- `timeout`
- `duplicate_risk`
- `conversation_not_found`
- `revision_conflict`
- `archive_failed`

## Security

- Use argument arrays or stdin; do not construct shell command strings from
  prompts.
- Validate workspace paths against policy before invocation.
- Do not pass arbitrary host environment variables to workers.
- Do not place credentials in prompts or records.
- For local/private tasks, reject hosted model mappings before creating a run.
- Product publish credentials are never exposed through the worker adapter.
