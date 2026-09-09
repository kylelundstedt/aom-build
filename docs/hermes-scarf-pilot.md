# Hermes + Scarf Pilot Plan

**Status:** Proposed pilot\
**Scope:** Phase 1A personal-context pilot and Phase 1B `freddie-sflld`
Dataset Product pilot\
**Related architecture:** [IV Agent Operating
Model](./iv-agent-operating-model.md) and [AOM Architecture
Contract](./architecture-contract.md)

## 1. Purpose

IV has developed an Agent Operating Model (AOM) built around persistent
Hermes agents, durable Hermes Bots, model-routed Shelley workers,
Write-Audit-Publish (WAP), versioned Product DAGs, deterministic
entitlements, and eventually client-facing Concierge agents.

The architecture is intentionally broader than the initial adoption
plan.

The purpose of this pilot is to learn whether the foundational pieces
create enough practical leverage to justify that broader architecture.

The pilot should answer two different questions:

1.  **Personal-context hypothesis:** Does a persistent Hermes with
    access to rich authoritative personal history materially reduce
    context reconstruction and improve day-to-day assistance?
2.  **Product-operations hypothesis:** Does a persistent Hermes acting
    as a Dataset Product owner/operator materially reduce
    project-management effort and direct worker supervision?

Scarf and ScarfGo are the initial management interfaces for both pilots.
Shelley remains the worker-level implementation interface.

The adoption principle is:

> **Start with useful individual agents, prove persistence and
> delegation, and let the larger AOM emerge only from demonstrated
> coordination pressure.**

## 2. Pilot Architecture at a Glance

``` text
                         PHASE 1

              +-------------------------+
              |                         |
              v                         v

       PILOT 1A                    PILOT 1B
    Personal Context             Product Operations

    Personal Hermes           Freddie Product Hermes
          |                         |
     personal-mcp              AgentMemory
          |                    Hermes Kanban
     AgentMemory               worker-routing
          |                         |
    Scarf / ScarfGo             Shelley
                               /   |   |   \
                            Fable Sol Luna Qwen
                                      |
                                    Entire
                                      |
                             WRITE-AUDIT-PUBLISH
                                      |
                                      v
                            published freddie-sflld
```

Neither pilot requires a Manager Hermes, A2A hierarchy, Paperclip,
FruVisi, Client Concierge, or custom AOM Cockpit.

## 3. Common Management Surface: Scarf

Scarf should be used as the primary Hermes management surface during the
pilot, with ScarfGo providing mobile monitor-and-steer access.

The intended interface split is:

``` text
Scarf / ScarfGo
    Hermes status, sessions, memory,
    Kanban, Bots, project dashboards
              |
              v
           Hermes
              |
              v
           Shelley
    implementation conversations
              |
              v
       Shelley mobile/app
    worker-level drill-down
```

The pilot should determine whether this combination preserves or
improves the current mobile experience.

A useful success test is:

> Can Kyle pick up an iPhone or iPad, understand what a pilot Hermes is
> doing, ask it a management-level question, and only open Shelley when
> implementation-level detail is actually needed?

For Product Pilot 1B, `freddie-sflld` should maintain a useful
`.scarf/dashboard.json` if Scarf's project-dashboard mechanism proves
suitable.

## 4. Pilot 1A --- Personal Context Hermes

### 4.1 Objective

Pilot 1A is the lower-risk introduction to Hermes itself.

Create a persistent **Personal Hermes** whose primary authoritative
information source is the existing `personal-mcp` server hosted on
`klundstedt-mini`.

`personal-mcp` contains historical email, calendar, and meeting
information.

``` text
                     PRIVATE / PERSONAL

                         Kyle
                          |
                    Scarf / ScarfGo
                          |
                          v
                    Personal Hermes
                          |
              +-----------+-----------+
              |                       |
              v                       v
         personal-mcp             AgentMemory
              |
       klundstedt-mini
              |
     +--------+--------+
     |        |        |
   email   calendar  meetings
```

### 4.2 Information authority

`personal-mcp` is an authoritative historical source/tool, not merely
Hermes memory.

For questions such as:

-   What did an email actually say?
-   When did a meeting occur?
-   Who attended?
-   What commitment was made?
-   What was discussed about a client or topic?

Hermes should retrieve the source information from `personal-mcp` when
evidence matters.

AgentMemory may retain useful derived context, but remembered summaries
should not silently replace authoritative source retrieval.

Conceptually:

``` text
AgentMemory
"What is relevant from prior experience?"

personal-mcp
"What does the historical record actually establish?"
```

### 4.3 Initial scope

Begin read-mostly.

Initial tasks should include:

-   reconstruct the history of a topic or decision;
-   prepare context before a meeting;
-   identify prior conversations with a person or organization;
-   summarize commitments made over time;
-   locate historical discussions relevant to a current question;
-   answer follow-up questions without requiring repeated context
    reconstruction.

Do not initially use the pilot to send email, modify calendars, or
perform other consequential external actions unless separately designed
and authorized.

### 4.4 Pilot 1A hypotheses

Test:

1.  Does Hermes become easier to use as it accumulates personal context?
2.  Does AgentMemory surface relevant prior information without
    excessive noise?
3.  Does Hermes appropriately return to `personal-mcp` for authoritative
    evidence?
4.  Does the combination materially reduce manual searching across
    email/calendar/meeting history?
5.  Does ScarfGo provide a good enough mobile interface to make Personal
    Hermes useful on the go?
6.  Does persistent Hermes memory add meaningful value beyond simply
    querying `personal-mcp` with a fresh agent?

### 4.5 Success criterion

> **Personal Hermes should materially reduce the effort required to
> reconstruct historical context while remaining grounded in
> authoritative `personal-mcp` records.**

If persistence does not improve the experience over a fresh agent with
MCP access, the AOM should not assume persistent memory is intrinsically
valuable.

## 5. Pilot 1B --- `freddie-sflld` Dataset Product Hermes

### 5.1 Objective

Pilot 1B tests the more ambitious operational AOM model.

Create a persistent **Freddie Product Hermes** responsible for helping
IV operate the `freddie-sflld` Dataset Product.

This Hermes is an **internal privileged Product owner/operator**. It is
not an external Dataset interface and must not be exposed directly to
arbitrary client prompts.

``` text
                    INTERNAL TRUST BOUNDARY

                    freddie-sflld.exe.dev
                              |
                     Scarf / ScarfGo
                              |
                              v
                    Freddie Product Hermes
                              |
          +-------------------+-------------------+
          |                   |                   |
     AgentMemory         Hermes Kanban       worker-routing
                                                  |
                                   +--------------+--------------+
                                   |              |              |
                              Shelley-Fable  Shelley-Sol   Luna / Qwen
                                   |              |              |
                                   +--------------+--------------+
                                                  |
                                                Entire
                                                  |
                                                  v
                                      repo / candidate state
                                                  |
                                                  v
                                      WRITE -> AUDIT -> PUBLISH
                                                  |
                         =========================+=========================
                                      PUBLICATION BOUNDARY
                                                  |
                                                  v
                                  immutable published freddie-sflld
```

### 5.2 Trust-boundary invariant

> **A Hermes that can create, inspect, or operate unpublished Product
> state must not be directly exposed to external user prompts.**

Freddie Product Hermes may access candidate data, failed audits,
internal investigation, repository credentials, AgentMemory, worker
conversations, and development history.

The published Product is a distinct artifact produced through WAP.

Future consumers sit downstream:

``` text
Freddie Product Hermes
        |
       WAP
        |
        v
published freddie-sflld
        |
        +--> GSE-LLD Product Hermes
        +--> authorized Client Concierge
        +--> optional dedicated Freddie Concierge
```

### 5.3 Persistence and state responsibilities

The pilot deliberately separates four concerns:

  Component              Responsibility
  ---------------------- -------------------------------------------------
  **AgentMemory**        Learned semantic/cross-agent context
  **Entire**             Engineering history, checkpoints, and evidence
  **Hermes Kanban**      Current work, ownership, blockers, review state
  **Repo/Product/WAP**   Authoritative Dataset and publication state

Hermes memory is not the authority for Dataset semantics or publication
state.

### 5.4 Initial orientation task

Before substantive modification, Freddie Product Hermes should inspect
and understand:

-   source and ingestion;
-   Dataset grain and major relations;
-   schema;
-   domains and code sets;
-   transformations and mappings;
-   audit and reconciliation;
-   WAP/publication mechanics;
-   lineage and provenance;
-   known gaps and limitations.

It should create Kanban work items for meaningful gaps rather than
modifying the Product merely to demonstrate autonomy.

This should test whether Hermes distinguishes:

``` text
canonical Product facts
        vs.
AgentMemory observations
        vs.
Kanban work state
        vs.
Entire historical evidence
```

### 5.5 Worker-routing exercise

After orientation, select one real bounded Dataset improvement.

A representative high-assurance workflow is:

``` text
Freddie Product Hermes
        |
        v
Kanban task
        |
        v
Fable: formulate requirement/specification/plan
        |
        v
Sol: critique semantics, assumptions, and risks
        |
        v
Hermes: reconcile
        |
        +--> Luna: implementation
        +--> Qwen: suitable bounded/local parallel work
        |
        v
Sol: review significant result
        |
        v
Hermes: accept / reject / iterate
        |
        v
AUDIT -> PUBLISH when appropriate
```

The exact model assignments are policy, not architecture.

### 5.6 Delegation traceability

The pilot should retain a navigable chain from responsible Hermes to
worker execution and evidence:

``` text
Freddie Product Hermes
 -> Kanban task
 -> Shelley conversation
 -> selected model
 -> tool execution
 -> Entire checkpoint/evidence
 -> repo/Product change
 -> WAP publication, if accepted
```

Illustrative task metadata:

``` yaml
task:
  id: FREDDIE-184
  owner: freddie-product-hermes
  status: in_progress

worker:
  type: shelley
  vm: freddie-sflld
  conversation_id: 8e7c...
  model: luna

evidence:
  entire_checkpoint: ...
```

### 5.7 Diagnostic questions

Repeatedly test:

**What is published right now, and how do you know?**

The answer must come from deterministic Product/WAP state.

**Why did we implement field or mapping X this way?**

The answer may combine published Product semantics, AgentMemory
contextual recall, and Entire evidentiary history, while clearly
distinguishing their roles.

### 5.8 Pilot 1B hypotheses

Test:

1.  Is the same Freddie Product Hermes materially more useful after
    repeated work than a fresh Hermes plus repository context?
2.  Does Hermes add value as a Dataset Product owner/operator rather
    than merely another coding agent?
3.  Does AgentMemory retain useful cross-agent learning without
    excessive cleanup?
4.  Does worker-routing improve quality, cost, or human attention?
5.  Does Kanban naturally capture current work, or become duplicate
    administration?
6.  Does Entire provide sufficient evidence to verify and revisit agent
    work?
7.  Does Hermes reliably preserve the working/published WAP boundary?
8.  Can current work be understood without reading every Shelley
    conversation?
9.  Does Scarf/ScarfGo provide an adequate management interface?
10. Are Hermes + Scarf + Shelley native interfaces sufficient without
    AgentView, Paperclip, FruVisi, or a custom cockpit?

Per [ADR 0005](./adr/0005-worker-substrate-null-hypothesis.md) and
[ADR 0006](./adr/0006-hermes-native-cli-worker-pilot-arm.md), each layer
is evaluated against the strongest simpler alternative, not its absence.
Hermes is compared against a designated long-lived Shelley manager
conversation. The worker layer runs **two arms of real tasks**: Shelley
conversations (Arm S) versus Hermes Kanban dispatch to native CLI
workers — Codex app-server runtime and the bundled claude-code skill
(Arm C). Worker-routing assigns tasks to arms explicitly so results are
attributable.

### 5.9 Success criterion

> **The Freddie stack should reduce human context reconstruction and
> direct worker supervision while preserving authoritative Product
> state, evidentiary history, and the hard WAP publication boundary.**

## 6. Implementation Plan

### Phase 0 --- Preparation

-   Confirm current `personal-mcp` connectivity and authentication
    model.
-   Select the exe.dev VM for Personal Hermes.
-   Confirm `freddie-sflld` pilot VM/repository.
-   Install and configure Hermes on both pilot environments.
-   Configure Scarf and ScarfGo against the pilot Hermes instances.
-   Establish backup/recovery expectations for Hermes state.
-   Record baseline workflows so pilot improvements can be judged
    against current practice.

### Phase 1A --- Personal Hermes

1.  Configure `personal-mcp` as an MCP source.
2.  Configure AgentMemory.
3.  Establish minimal Personal Hermes instructions and security policy.
4.  Use Scarf/ScarfGo as the normal interface.
5.  Run real historical-context tasks for several weeks.
6.  Track failures: missed recall, incorrect recall, unnecessary
    retrieval, stale memory, and evidence-grounding problems.
7.  Decide whether persistent memory creates measurable value.

### Phase 1B --- Freddie Product Hermes

1.  Install/configure Hermes on the existing `freddie-sflld` VM.
2.  Configure AgentMemory.
3.  Configure Hermes Kanban.
4.  Wrap Shelley's CLI behind a Hermes worker-management skill.
5.  Implement initial `worker-routing` policy.
6.  Ensure Entire captures worker development history.
7.  Perform the orientation exercise.
8.  Build a useful Scarf Product dashboard.
9.  Select one real improvement and run the full routed-worker workflow.
10. Exercise WAP and publication-state questions.
11. Evaluate the pilot hypotheses.

Pilots 1A and 1B can overlap in calendar time; they are intentionally
testing different aspects of Hermes.

## 7. What Not to Build Yet

Do not initially introduce:

-   CEO/Portfolio Hermes;
-   Client Manager hierarchy;
-   A2A organizational delegation;
-   extensive Bot teams;
-   Paperclip;
-   AgentView unless a concrete session/collaboration gap appears;
-   FruVisi unless organizational visualization becomes useful;
-   Client Concierge;
-   custom AOM Cockpit;
-   external Freddie agent.

The pilots should use the smallest architecture capable of proving or
disproving the important hypotheses.

## 8. Evaluation

At the end of Phase 1, evaluate along four dimensions.

### Persistence

Does the same Hermes become more useful over time?

### Delegation

Can Hermes successfully supervise Shelley workers with less human
intervention than direct Shelley management?

### State and evidence

Do AgentMemory, Kanban, Entire, and authoritative Product/source systems
maintain clean, useful, non-conflicting responsibilities?

### Management UX

Does Scarf/ScarfGo provide enough fleet/project visibility and mobile
steering to make persistent agents operationally pleasant?

A pilot is successful only if the architecture reduces human
cognitive/management burden. More autonomous activity by itself is not
success.

## 9. Possible Future AOM Steps

If both pilots are successful, expansion should remain organic.

### Step 2 --- Additional persistent Product/project agents

Add Hermes to one or two additional existing projects or Dataset
Products.

Observe whether persistent identity and memory continue to compound
usefully.

### Step 3 --- Manager Hermes

When coordinating several agents becomes repetitive:

``` text
Project / Product Manager Hermes
        |
        +--> Agent A
        +--> Agent B
        +--> Agent C
```

Introduce A2A or Hermes peer messaging and test management-by-exception.

### Step 4 --- Durable Bots

Create Bots only where a specialist role repeatedly benefits from
persistent memory---for example Modeling, Quality, Publication, or
Documentation.

### Step 5 --- Product DAG

Once multiple Dataset Product agents are proven:

``` text
fannie-sflpd ---+
freddie-sflld --+--> gse-lld
ginnie-lld -----+
```

Require composed Products to consume immutable published upstream
versions.

### Step 6 --- Client Manager and `clientx-service`

Introduce a Client X Manager when multiple Client X projects/Products
create genuine client-level coordination pressure.

Publish `clientx-service` through WAP as a first-class Product.

### Step 7 --- Deterministic entitlements

Establish principal-to-Product authorization independent of the LLM.

``` text
principal -> entitled Products -> published surfaces
```

### Step 8 --- Client Concierge

Only after publication and entitlement boundaries are proven, introduce
a separate client-facing Concierge environment:

``` text
Client user
   |
Client X Concierge
   |
authorized published Product graph
```

The Concierge must never have unrestricted access to internal Product
agents or unpublished state.

### Step 9 --- Broader management control plane

Evaluate Hermes native UI, Scarf, Kanban, Bots, and A2A under real
organizational load.

Add Paperclip, FruVisi, or an IV-specific AOM dashboard only if concrete
governance, visualization, or management gaps remain.

## 10. Guiding Principle

The broader AOM remains a destination hypothesis rather than a
deployment requirement.

Phase 1 should establish whether two simple persistent agents---one
personal and one Product-oriented---create enough practical value to
justify expanding the model.

> **Prove persistence first. Prove delegation second. Add hierarchy only
> when coordination pressure demands it. Publish before exposing.**
