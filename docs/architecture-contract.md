# IV Agent Operating Model --- Architecture Contract

This is the concise companion to `iv-agent-operating-model.md`.

## Layering

``` text
Hermes environment / VM
    persistent responsibility + security boundary
        |
        +-- Hermes Bots
        |   durable specialists
        |
        +-- worker-routing
            |
            +-- Shelley conversations
                bounded workers
                    |
                    +-- Fable / Sol / Luna / Qwen
                        interchangeable model capabilities
```

## Decision rules

### VM versus Bot

Use a **VM/Hermes environment** when trust, client, Product, repository,
credentials, execution, or security exposure differs materially.

Use a **Bot** for a durable specialist inside the same boundary.

### Bot versus Shelley worker

Use a **Bot** when the role should retain specialist memory and improve
across many tasks.

Use a **Shelley conversation** for a bounded assignment.

### Worker selection

Worker/model choice is policy. A first-class `worker-routing` skill
chooses a strategy based on task type, ambiguity, complexity, assurance,
context, parallelism, capability, subscription capacity, cost, latency,
and local/privacy needs.

Hermes remains accountable for the result.

## Organizational evolution

Add hierarchy only when it removes coordination work.

``` text
projects
   -> project manager
      -> client manager
         -> portfolio/company manager
```

Managers summarize and coordinate; specialists retain detail. Hierarchy
is a context-compression mechanism.

## Product lifecycle

Every IV Product follows:

``` text
WRITE -> AUDIT -> PUBLISH
```

The key boundary is **working/internal versus published**, not data
versus knowledge.

A published Product may include observations, schemas, code sets,
semantics, mappings, lineage, provenance, audit evidence, quality
results, release history, limitations, and documentation.

## Product DAG

Published Products may compose other published Products.

``` text
fannie-sflpd ---+
freddie-sflpd --+--> gse-lld --------+
ginnie-lld -----+                     |
                                      +--> clientx-service
project1 -----------------------------+
project2 -----------------------------+
```

Every published dependency points to an immutable published Product
version.

> **The published Product DAG contains only immutable published Product
> versions.**

## Entitlements

Product dependency and user authorization are separate relations:

``` text
Product DAG:  product version -> upstream product version
Entitlement:  principal -> Product
```

Authorization is deterministic and occurs before retrieval.

> **VISIBLE = PUBLISHED AND PRINCIPAL_IS_ENTITLED**

A user's entitlement to a composed Product does not automatically grant
direct access to its upstream Products.

## Concierge

A Client Concierge is an agentic interface to the authenticated user's
authorized published Product graph.

``` text
user
 -> identity
 -> entitlements
 -> authorized published Products
 -> SQL / metadata / docs / provenance
 -> reasoning
 -> answer
```

Do not expose privileged internal agents directly to arbitrary client
prompts.

Do not sanitize unrestricted internal information after retrieval.
**Publish intentionally, then let Concierge consume the published
surface.**

## Management interface

The primary human interface is the **management hierarchy**, not the
complete agent/worker roster.

``` text
mobile user
 -> manager Hermes
 -> subordinate Hermes
 -> Bots / delegated tasks
 -> Shelley workers
```

Use **management by exception**: managers compress subordinate activity
into status, blockers, risks, decisions, failed routines/audits, and
significant completions.

Preserve Shelley as the worker-level drill-down interface.

Every delegation must retain enough metadata to navigate:

``` text
accountable Hermes -> task -> VM -> Shelley conversation -> model/execution
```

A future mobile AOM Cockpit may present attention items, organizational
status, active workers, and deep links, but it should remain a
presentation layer rather than another agent runtime.

> **Adding agents should reduce, not increase, the number of
> conversations a human must personally monitor.**

## Core invariants

1.  Hermes owns persistent responsibility.
2.  Bots provide durable specialization.
3.  Shelley provides bounded computational labor.
4.  Worker routing is explicit policy.
5.  Hermes owns worker output.
6.  Agent hierarchy evolves from coordination pressure.
7.  WAP governs Product publication.
8.  Published Product dependencies form a versioned DAG.
9.  Authorization is deterministic and pre-retrieval.
10. Concierge operates only over the authorized published Product graph.

## Initial pilot: `freddie-sflld`

Use `freddie-sflld` as the first concrete AOM pilot.

``` text
INTERNAL
Freddie Product Hermes
+ AgentMemory
+ Hermes Kanban
+ worker-routing
+ Shelley (Fable / Sol / Luna / Qwen)
+ Entire
        |
        v
WRITE -> AUDIT -> PUBLISH
        |
======== publication boundary ========
        |
        v
published freddie-sflld
```

`Freddie Product Hermes` is an internal privileged Product
owner/operator, **not** an external Product interface.

> **A Hermes that can create, inspect, or operate unpublished Product
> state must not be directly exposed to external user prompts.**

External consumers---including a future Client Concierge or dedicated
Freddie Concierge---consume only the published Product surface through a
separate trust boundary and deterministic entitlements.

The persistence/state separation is:

-   **AgentMemory:** learned semantic context.
-   **Entire:** engineering history and evidence.
-   **Kanban:** current agent work state.
-   **Repo/Product/WAP:** authoritative Product and publication state.

Two recurring diagnostic questions should be used:

1.  **What is published right now, and how do you know?** --- must
    resolve from Product/WAP state.
2.  **Why did we implement X this way?** --- may combine Product
    semantics, AgentMemory context, and Entire evidence.

The pilot succeeds if the stack reduces human context reconstruction and
direct worker supervision while preserving the hard WAP publication
boundary.

Do not add AgentView, Paperclip, FruVisi, a Manager Hermes, or an
external Concierge until the pilot demonstrates a concrete need.
