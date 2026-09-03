---
name: shelley-worker
description: Delegate bounded work to Shelley worker conversations from Hermes. Use when a Kanban task needs implementation, review, or research work done by a Shelley worker. Covers creating, continuing, monitoring, searching, and archiving worker conversations, and the metadata you must record for every delegation.
---

# Shelley Worker Management

Shelley's CLI is **experimental** — flags and output may change without notice.
This skill is the only place Shelley invocation knowledge should live. If a
command behaves differently than documented here, stop and report it; do not
improvise new invocations.

## The six operations

```bash
# 1. Start a worker (returns JSON: capture conversation_id!)
shelley client chat -p "PROMPT" -cwd /abs/path/to/workdir -model MODEL

# 2. Continue an existing worker (forgetting -c silently starts a NEW conversation)
shelley client chat -c CONVERSATION_ID -p "PROMPT"

# 3. Read a conversation; -wait blocks until the agent turn ends
shelley client read -wait CONVERSATION_ID

# 4. List recent conversations
shelley client list -limit 20

# 5. Search by content (how you find lost workers — see task tags below)
shelley client search "QUERY"

# 6. Archive when the task closes
shelley client archive CONVERSATION_ID
```

There is **no cancel**. A runaway worker can only be archived; note that in the
task if it happens.

## Rules

1. **Tag every first prompt** with the task ID on its own line:
   `[task: TASK_ID]`. This makes `shelley client search "TASK_ID"` find the
   conversation later.
2. **Capture the conversation_id** from the JSON that operation 1 prints, and
   record it in the task metadata (see task-metadata-convention.md) before
   doing anything else.
3. **One task stage → one conversation.** Don't reuse a worker conversation
   for a different task; start a new one.
4. **State the assignment fully in the first prompt**: objective, working
   directory, constraints, acceptance criteria, and what NOT to touch. Workers
   can't see the Kanban board or sibling workers.
5. **A finished turn is not accepted work.** Read the result, judge it against
   the acceptance criteria, and only then update the task. You remain
   accountable for the output.
6. **Model choice comes from the routing policy** (worker-routing-policy.md),
   not habit. Record which model actually ran.
7. **Never put credentials in prompts.** Workers get file paths and
   instructions, not secrets.
8. If `chat` output is not parseable JSON or the conversation_id is missing,
   assume the worker may or may not have started: search for the task tag
   before retrying, so you don't create duplicates.
