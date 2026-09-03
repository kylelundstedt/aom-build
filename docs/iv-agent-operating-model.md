# IV Agent Operating Model

**Status:** Working architecture

## 1. Core model

IV's Agent Operating Model has four layers:

``` text
ORGANIZATION / SECURITY BOUNDARY
Persistent Hermes environment on exe.dev
        |
        +-- DURABLE SPECIALISTS
        |   Hermes 2.0 Bots / profiles
        |
        +-- WORKER ROUTING
            |
            +-- Shelley-Fable
            +-- Shelley-Sol
            +-- Shelley-Luna
            +-- Shelley-Qwen
            |
            +-- tools / repo / compute
```

A persistent Hermes is the accountable organizational entity. Bots are
durable specialists within its trust boundary. Shelley conversations are
bounded workers. Models are interchangeable capabilities selected by
policy.

**Accountability invariant:** The persistent Hermes agent owns the work
product.

### Terminology

  ----------------------------------------------------------------------
  Layer                  Term                   Examples
  ---------------------- ---------------------- ------------------------
  Overall design         Agent Operating Model  This architecture

  Persistent hierarchy   Agent organization     Client Manager -\>
                                                Project Hermes

  Persistent             Hermes                 Project/Product/Client
  runtime/harness                               agent

  Durable specialists    Hermes Bots            Modeling, Quality,
                                                Publication

  Worker runtime         Shelley                Task conversations

  Worker models          Models                 Fable, Sol, Luna, Qwen

  Communication          Agent fabric           A2A, Bot peer messaging

  Infrastructure         Agent infrastructure   exe.dev,
                                                klundstedt-mini, secrets

  Product lifecycle      Product architecture   WAP, Product DAG,
                                                entitlements
  ----------------------------------------------------------------------

## 2. Persistent Hermes employees

Use one persistent Hermes environment per meaningful organizational,
Product, project, client, execution, or security boundary.

``` text
exe.dev project VM
+-- repo
+-- Project Hermes
|   +-- memory / skills
|   +-- project or Product context
|   +-- planning / orchestration
|   +-- Bots
|   +-- worker-routing
|   +-- A2A / peer relationships
|   +-- credentials / tools
+-- Shelley worker conversations
```

Use a separate VM when trust, client, Product, filesystem, repository,
credentials, execution environment, or security exposure differs
materially. Use a Bot when a persistent specialist can safely operate
inside the same boundary.

## 3. Hermes Bots: durable specialists

Bot Mode fills the layer between the responsible Hermes and ephemeral
workers.

``` text
GSE-LLD Hermes
+-- Modeling Bot
+-- Quality Bot
+-- Publication Bot
+-- Documentation Bot
        |
        +-- worker-routing -> Shelley
```

**Bot versus worker rule:** If a role should learn and become more
valuable across many tasks, make it a Bot. If the need is principally a
bounded assignment, make it a Shelley conversation.

## 4. Hermes manager; Shelley worker pool

IV's customized Shelley can use IV's Codex and Claude subscriptions plus
self-hosted open-weight models such as Qwen on `klundstedt-mini`.

A higher-assurance workflow can be:

``` text
OBJECTIVE
  |
Fable: formulate requirement/specification/plan
  |
Sol: critique assumptions, gaps, risks
  |
Hermes: reconcile
  |
Luna/Qwen workers: execute bounded tasks in parallel
  |
Sol: review significant results
  |
Hermes: accept / reject / iterate
```

Hermes can create, continue, monitor, search, and archive top-level
Shelley conversations:

``` bash
shelley client chat -p "Implement task X" -cwd /path/to/repo
shelley client chat -c "$CONVERSATION_ID" -p "Run the tests"
shelley client read -wait "$CONVERSATION_ID"
shelley client list
shelley client search "task X"
shelley client archive "$CONVERSATION_ID"
```

Because the Shelley CLI is experimental, wrap it behind a Hermes
skill/adapter.

### Worker-routing skill

`worker-routing` should be first-class. Inputs include task type,
ambiguity, reasoning complexity, assurance level, context needs,
parallelizability, model capability, subscription capacity, cost,
latency, and local/privacy requirements.

Its output is a worker **strategy**, not merely a model name. Model
assignments are policy, not architecture.

## 5. Distributed agent organization

Persistent Hermes environments form an organization using A2A and/or
Hermes-native peer mechanisms:

``` text
Portfolio Hermes
+-- Client X Manager Hermes
|   +-- Project 1 Hermes
|   +-- Project 2 Hermes
|   +-- GSE-LLD Hermes
+-- Internal Manager Hermes
    +-- R&D Hermes
```

Each Hermes retains its own memory, skills, tools, credentials, and
execution context.

**Management invariant:** Managers summarize and coordinate; specialists
retain detail. Hierarchy is also a context-compression mechanism.

## 6. Organic evolution

Do not design a large virtual organization in advance.

Start with Hermes on existing project/Product VMs. Add a manager when
repeated cross-project coordination becomes work. Add Client Managers
when client-level context and coordination become valuable. Add
specialist Bots only where durable specialization pays off.

Titles and hierarchy should follow actual coordination responsibilities
rather than precede them.

## 7. Paperclip as optional control plane

Hermes supplies persistent identity, memory, skills, reasoning, tools,
expertise, and delegation. Paperclip may later add authoritative org
charts, tasks, goals, budgets, approvals, heartbeats, centralized
visibility, and audit.

``` text
Paperclip control plane
        |
Persistent Hermes organization
        |
A2A / peers
        |
exe.dev infrastructure
```

Paperclip is optional and should be introduced only when centralized
governance creates more value than complexity.

## 8. Products as first-class organizational objects

IV Products may have persistent Hermes specialists:

-   `fannie-sflpd`
-   `freddie-sflpd`
-   `ginnie-lld`
-   `gse-lld`
-   `clientx-service`

A Dataset Hermes may understand and manage ingestion, transformations,
schema, domains/code sets, semantics, mappings, lineage, provenance,
quality, audit evidence, releases, limitations, and documentation.

## 9. Write -\> Audit -\> Publish

WAP is the common Product lifecycle:

``` text
WRITE -> candidate -> AUDIT -> PUBLISH -> immutable published Product
```

The fundamental information boundary is **WORKING / INTERNAL versus
PUBLISHED PRODUCT**, not "data versus knowledge."

Internal state can contain candidate data, experimental mappings, failed
audits, debugging information, hypotheses, scratch analysis, and
unreleased changes. Downstream consumers operate only on published
Product surfaces.

## 10. Published Product surface

A published Dataset is a complete information Product:

``` text
fannie-sflpd@117
+-- observations
+-- schemas
+-- code sets
+-- semantic definitions
+-- mappings
+-- lineage / provenance
+-- audit / quality evidence
+-- known limitations
+-- release history
+-- documentation
```

Loan counts and Fannie product-type codes are both queries against the
same Product. Different tools may answer them; they are not separate
"data" and "knowledge" security domains.

## 11. Product composition and DAG

Composed Products consume only published upstream versions:

``` text
fannie-sflpd ---+
freddie-sflpd --+--> gse-lld
ginnie-lld -----+
```

A publication pins exact versions:

``` text
gse-lld@42
+-- fannie-sflpd@117
+-- freddie-sflpd@93
+-- ginnie-lld@61
```

A broader graph:

``` text
fannie-sflpd ---+
freddie-sflpd --+--> gse-lld --------+
ginnie-lld -----+                     |
                                      +--> clientx-service
project1 -----------------------------+
project2 -----------------------------+
```

**DAG invariant:** The published Product DAG contains only immutable
published Product versions. Candidate state stays outside the published
DAG until it completes WAP.

## 12. Client service as a Product

Represent the Client X relationship as `clientx-service`.

Its published surface can include account context, active projects,
agreed commitments, project status, milestones, client action items,
decisions, deliverables, terminology, stakeholder roles, service
documentation, and available IV Products.

The internal Client X Manager may know substantially more. Internal
account notes, tentative plans, commercial considerations, staffing
discussions, risk assessments, and unpublished status are not published
merely because the Manager knows them.

## 13. Client Concierge

The Client X Concierge is an **agentic interface to Client X's
authorized published Product graph**.

``` text
Client X user
    |
Client X Concierge
    |
clientx-service
    |
    +-- project1
    +-- project2
    +-- gse-lld
         +-- fannie
         +-- freddie
         +-- ginnie
```

The Concierge supports effectively zero-marginal-employee-time
self-service for basic, repeated, exploratory, technical, and executive
questions. Removing the social friction of deciding whether a question
is worth an IV employee's time is itself a service feature.

Do not expose privileged internal Project or Client Manager Hermes
directly to arbitrary client prompts.

## 14. Publication, not sanitization

Do not give a client-facing model unrestricted internal information and
ask it to redact.

``` text
BAD:  internal corpus -> LLM sanitization -> client

GOOD: internal work -> WRITE -> AUDIT -> PUBLISH
                                      |
                                      v
                               published Product
                                      |
                                      v
                                  Concierge
```

The governing question is: **What has IV affirmatively published for
this audience?**

## 15. Deterministic entitlements

Authorization is outside the LLM.

``` text
Bob @ Client X

ALLOW clientx-service
ALLOW project1
ALLOW project2
ALLOW gse-lld

DENY  fannie-sflpd
DENY  Client Y products
```

Runtime:

``` text
authenticated principal
 -> entitlement engine
 -> authorized Products
 -> published Product surfaces
 -> retrieval / SQL / tools
 -> reasoning
 -> answer
```

The model never receives unauthorized information.

**Visibility invariant:**
`VISIBLE = PUBLISHED AND PRINCIPAL_IS_ENTITLED`, with any additional
deterministic classification rules enforced before retrieval.

## 16. Product DAG and entitlements are separate

The Product DAG represents dependency/provenance:

``` text
product version -> upstream product version
```

Entitlements represent authorization:

``` text
principal -> Product
```

Access to a composed Product does not automatically grant direct access
to upstream Products. Bob may access `gse-lld` without standalone
`fannie-sflpd` access. If `gse-lld` itself publishes Fannie mappings,
Bob may see those mappings through `gse-lld`.

## 17. Concierge query model

``` text
authenticated user
 -> entitlements
 -> authorized Products
 -> published Product DAG/surfaces
 -> tool selection (SQL / metadata / docs / provenance)
 -> reasoning
 -> answer
```

Tool selection is implementation detail. Publication and authorization
define the permissible information surface.

## 18. Core architectural invariants

1.  Persistent Hermes agents own organizational, project, or Product
    responsibility.
2.  Bots are durable specialists inside a shared trust/Product boundary.
3.  Shelley conversations are task workers, not organizational peers.
4.  Worker selection is policy implemented through a worker-routing
    skill.
5.  Hermes remains accountable for worker output.
6.  Organizational hierarchy emerges from real coordination pressure.
7.  Managers summarize; specialists retain detailed institutional
    knowledge.
8.  WAP governs Product publication.
9.  The fundamental information boundary is working/internal versus
    published.
10. A published Product includes observations, semantics, provenance,
    evidence, and documentation as one surface.
11. Downstream Products consume only immutable published upstream
    versions.
12. Published Product dependencies form a DAG.
13. Product composition and user entitlement are separate relations.
14. Authorization is deterministic and enforced before retrieval.
15. Client-facing agents consume published information; they do not
    sanitize unrestricted internal information.
16. Concierge is an interface to an authorized Product graph, not the
    authoritative store itself.

## 19. Initial adoption path

1.  Add Hermes to two or three existing project/Product exe.dev VMs.
2.  Give each Hermes a Shelley integration and initial `worker-routing`
    skill.
3.  Introduce Bots where durable specialization proves useful.
4.  Add a Project Manager Hermes when cross-project coordination becomes
    repetitive.
5.  Add Client X Manager when client-level context becomes valuable.
6.  Apply WAP rigorously to Product publication.
7.  Define deterministic Product entitlements.
8.  Build a constrained Client X Concierge over published, entitled
    Products.
9.  Add Paperclip only if centralized governance becomes necessary.
10. Continue evolving the organization from observed coordination
    pressure rather than a predetermined org chart.

## 20. Management Interface and Observability

The AOM must improve organizational leverage without degrading IV's
existing mobile management experience.

The management model should deliberately separate **organizational
control** from **worker drill-down**.

### 20.1 Three management levels

#### Level 1 --- Executive / management interface

Normal on-the-go interaction should occur with a small number of
persistent Hermes managers rather than every subordinate agent and
worker.

``` text
You / mobile
     |
Portfolio / Client / Product Manager Hermes
     |
     +-- subordinate Hermes agents
             |
             +-- Bots
             +-- Shelley workers
```

Typical management interactions include:

-   What needs my attention?
-   What changed overnight?
-   How is Client X doing?
-   Which projects are blocked?
-   What decisions require me?
-   Ask Project 1 to investigate an issue.
-   Which agents and workers are currently active?
-   Did any publication audits fail?

The intended operating mode is **management by exception**. Hierarchy
should reduce the number of conversations a human must personally
monitor.

Hermes messaging/gateway interfaces can provide an initial mobile front
door. Only a small number of useful management agents should normally be
exposed directly; reproducing every subordinate agent in a messaging
client would recreate the conversation-overload problem.

#### Level 2 --- Manager / Project / Product agent interface

When deeper context is required, the user should be able to interact
directly with the responsible persistent Hermes, such as:

``` text
Client X Manager Hermes
Project 1 Hermes
GSE-LLD Hermes
```

Hermes's own Bot/web/desktop interfaces can serve this level as they
mature.

#### Level 3 --- Worker drill-down

Shelley's existing mobile UX remains valuable for inspecting or directly
steering implementation conversations.

``` text
Hermes
  WHY / WHAT / STATUS / RESPONSIBILITY

Shelley
  HOW / CODE / TOOL ACTIVITY / WORKER CONVERSATION
```

The AOM should preserve Shelley as the worker-level management surface
rather than attempting to replace it unnecessarily.

### 20.2 Delegation traceability

Every delegated task must remain navigable from organizational
responsibility to the actual worker performing it.

At minimum, Hermes should retain structured metadata such as:

``` yaml
task:
  id: task-184
  owner: project1-hermes
  description: implement parser changes

worker:
  type: shelley
  vm: project1
  conversation_id: 8e7c...
  model: luna

status: working
```

This enables a manager to report:

``` text
Project 1

Active workers:
- Parser implementation — Luna — working
- Architecture review — Sol — complete
- Documentation update — Qwen — waiting
```

and allows a future UI to deep-link into the relevant Shelley
conversation.

> **Every delegation must remain traceable from the accountable Hermes
> agent down to the executing worker.**

### 20.3 Attention routing

Alongside `worker-routing`, the AOM should define a first-class
**management-reporting / attention-routing skill**.

Its purpose is to continuously compress subordinate activity into
information appropriate for the next management level:

``` text
subordinate activity
        |
        v
management-reporting
        |
        +-- status
        +-- exceptions
        +-- blockers
        +-- risks
        +-- decisions required
        +-- failed audits/routines
        +-- significant completions
        |
        v
manager
```

The skill should aggressively avoid forwarding routine implementation
detail upward unless requested.

The desired outcome is that adding agents produces **fewer human
management interactions**, not more.

### 20.4 Future AOM Cockpit

If the organizational model proves valuable, IV may eventually build a
thin, mobile-first AOM Cockpit.

It should be a presentation and navigation layer over existing AOM state
rather than another agent runtime.

A conceptual home screen:

``` text
IV AOM

NEEDS YOU
--------------------------------
Client X
  Decision required: Project 2 scope

GSE-LLD
  Publication audit failed

Client Y
  Contract assumption unresolved


ACTIVE
--------------------------------
Client X Manager
  Project 1          2 workers
  Project 2          1 worker

Products
  GSE-LLD            3 workers
  Fannie-SFLPD       idle
```

Drilling into a Project or Product could expose:

``` text
Project 1

Ask Project 1 Hermes...

Status
Decisions
Risks
Recent publications

Active workers
  Shelley-Sol     architecture review
  Shelley-Luna    parser implementation
```

The Cockpit should provide navigation across:

``` text
human attention item
      -> accountable manager
      -> responsible Project/Product Hermes
      -> Bot or delegated task
      -> Shelley conversation
      -> underlying execution
```

This should remain a future option rather than a prerequisite for
initial AOM adoption.

### 20.5 Management-interface invariant

> **The primary human interface is the management hierarchy; direct
> worker interaction is an intentional drill-down path.**

The AOM succeeds operationally only if organizational hierarchy,
attention routing, and delegation traceability allow humans to supervise
more work while personally monitoring fewer conversations.

## 22. Initial Hermes Pilot: `freddie-sflld`

The first concrete AOM pilot should use the existing `freddie-sflld`
Dataset Product.

The pilot is intentionally **internal-only**. `Freddie Product Hermes`
is the privileged Product owner/operator; it is not a client-facing or
externally prompted agent.

``` text
                    INTERNAL TRUST BOUNDARY

                    freddie-sflld.exe.dev
                              |
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
                                  data / schema / semantics /
                                  lineage / evidence / docs
```

### 22.1 Critical trust-boundary invariant

> **A Hermes that can create, inspect, or operate unpublished Product
> state must not be directly exposed to external user prompts. External
> agents consume only published Product surfaces through a separate
> trust boundary.**

`Freddie Product Hermes` may legitimately have access to:

-   source and candidate data;
-   repository and development environment;
-   experimental mappings and transformations;
-   failed audits;
-   internal investigation notes;
-   AgentMemory;
-   Shelley worker conversations;
-   Entire checkpoints/history;
-   Product credentials and tools.

None of those capabilities imply external visibility.

The published `freddie-sflld` Product is a separate artifact produced
through WAP.

An eventual external consumer would sit on the other side of the
publication boundary:

``` text
Freddie Product Hermes
        |
       WAP
        |
        v
published freddie-sflld
        |
        +------> GSE-LLD Product Hermes
        |
        +------> Client X Concierge
        |
        +------> optional Freddie Concierge
```

If IV later creates a dedicated Freddie-facing Concierge, it should run
in a separate trust environment and have access only to the published
Product surface for which its principal is entitled.

### 22.2 Pilot objective

The pilot is not primarily intended to prove that an agent can write
code. Shelley already demonstrates that.

It should test whether a persistent Dataset Product Hermes can become a
useful long-lived **Product owner/operator** that:

-   understands the Dataset's source, grain, schema, domains/code sets,
    semantics, mappings, lineage, audit process, publication process,
    and known limitations;
-   maintains current work state without requiring a human to
    reconstruct it from conversations;
-   delegates bounded work to heterogeneous Shelley workers;
-   accumulates useful semantic memory without confusing memory with
    authoritative Product state;
-   preserves evidentiary development history;
-   operates the Dataset through WAP;
-   knows deterministically what is currently published.

### 22.3 Initial orientation task

The first assignment should emphasize understanding rather than
modification.

Freddie Product Hermes should inspect the existing repository and
Product state and establish an understanding of:

-   source and ingestion;
-   Dataset grain and major relations;
-   schema;
-   domains and code sets;
-   transformations and mappings;
-   audit/reconciliation process;
-   WAP/publication process;
-   lineage and provenance;
-   known gaps and limitations.

It should create Kanban work items for material gaps it identifies but
should not make substantive Product changes merely to demonstrate
autonomy.

This first exercise should reveal whether Hermes correctly
distinguishes:

``` text
canonical repo/Product facts
        vs.
AgentMemory observations
        vs.
Kanban current work state
        vs.
Entire historical evidence
```

### 22.4 Pilot persistence/state stack

The pilot deliberately tests four distinct functions:

  -----------------------------------------------------------------------
  Component                           Primary question
  ----------------------------------- -----------------------------------
  **AgentMemory**                     What have we learned that is
                                      relevant now?

  **Entire**                          What actually happened during
                                      development, and what
                                      evidence/checkpoint proves it?

  **Hermes Kanban**                   What work exists, who/what owns it,
                                      and what is its state right now?

  **IV Product/repo/WAP state**       What is authoritative, and what is
                                      published right now?
  -----------------------------------------------------------------------

These systems complement rather than substitute for one another.

Hermes memory must not become the authority for Dataset semantics,
publication status, or other canonical Product state.

### 22.5 Worker-routing exercise

After orientation, give Freddie Product Hermes one real bounded Dataset
improvement that exercises multiple worker roles.

For example:

``` text
Freddie Product Hermes
        |
        v
Kanban task
        |
        v
Fable: formulate requirement / specification / plan
        |
        v
Sol: critique semantic and implementation risks
        |
        v
Hermes: reconcile and approve plan
        |
        +------> Luna: implementation
        +------> Qwen: bounded/local parallel work
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

The exact Fable/Sol/Luna/Qwen assignments are initial policy and may
change as the `worker-routing` skill learns which strategies are
effective.

### 22.6 Delegation traceability

The pilot should test whether Kanban naturally carries or links the
metadata required for AOM observability:

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

The desired navigable chain is:

``` text
Freddie Product Hermes
 -> Kanban task
 -> Shelley worker conversation
 -> model/tool execution
 -> Entire evidence
 -> resulting repo/Product state
 -> WAP publication, if accepted
```

### 22.7 Two diagnostic questions

The pilot should repeatedly test two questions that exercise different
persistence domains.

**Question 1:**

> What is published right now, and how do you know?

The answer must come from deterministic Product/WAP state, not
AgentMemory.

**Question 2:**

> Why did we implement field or mapping X this way?

The answer may combine:

``` text
published Product semantics
        +
AgentMemory contextual recall
        +
Entire evidentiary history
```

but should distinguish authoritative Product facts from remembered
context and historical evidence.

### 22.8 Pilot hypotheses

The Freddie pilot should explicitly test:

1.  **Persistent-agent value:** Is Freddie Product Hermes materially
    more useful after repeated work than a fresh Hermes plus repository
    context?
2.  **Dataset-agent value:** Does a persistent Hermes provide leverage
    as a Dataset Product owner/operator rather than merely as another
    coding agent?
3.  **Memory value:** Does AgentMemory surface useful prior learning
    across Hermes and heterogeneous Shelley workers without excessive
    noise or cleanup?
4.  **Worker-routing value:** Does routing formulation, critique,
    execution, and review among Fable/Sol/Luna/Qwen improve quality,
    cost, or human attention?
5.  **Kanban value:** Does Hermes naturally maintain useful current work
    state while delegating to Shelley, or does Kanban become duplicate
    administration?
6.  **Provenance value:** Does Entire provide sufficient evidence to
    verify or revisit agent conclusions and implementation?
7.  **WAP discipline:** Does Hermes reliably distinguish
    working/candidate state from published Product state?
8.  **Management value:** Can a human understand current work and
    exceptions without reading every Shelley conversation?
9.  **Native UI sufficiency:** Are Hermes and Shelley native interfaces
    sufficient for the pilot without AgentView, Paperclip, FruVisi, or a
    custom AOM Cockpit?

### 22.9 Success criterion

The key question is:

> **Does Freddie Product Hermes + AgentMemory + Kanban +
> worker-routing + Shelley + Entire allow IV to operate `freddie-sflld`
> over sustained work with less human context reconstruction and less
> direct worker supervision, while preserving a hard WAP publication
> boundary?**

If yes, the next step is to repeat the pattern on one or two additional
Products/projects and observe whether cross-agent coordination pressure
justifies a Manager Hermes or A2A hierarchy.

If no, simplify the AOM before adding hierarchy or external-facing
agents.
