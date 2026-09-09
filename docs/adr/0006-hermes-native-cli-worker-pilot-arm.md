# ADR 0006: Hermes + Native CLI Workers Is a First-Class Pilot Arm

- **Status:** Accepted (amends ADR 0005)
- **Date:** 2026-09-09
- **Decided by:** Kyle

## Context

ADR 0005 framed "Hermes + Kanban-native workers, no Shelley" as a null
hypothesis, with Shelley justified by three residuals: subscription model
access, coding-harness quality, and the Entire evidence pipeline. Upstream
verification the same day
([research note](../research/hermes-native-cli-workers-2026-09-09.md))
eliminated most of that residue:

- Hermes's **Codex app-server runtime** runs Kanban workers on the Codex
  harness under **ChatGPT subscription auth**, natively.
- Hermes's bundled **claude-code skill** orchestrates Claude Code under
  **Pro/Max OAuth** — subscription semantics at least as good as Shelley's.
- Kanban **PR acceptance receipts** (required-check-gated, durable SQLite
  events) plausibly meet WAP evidence needs without Entire.

Shelley's remaining case is incumbency and exe.dev integration (deployed,
Entire-qualified, exe.dev auth/proxy/mobile, IV customizations) — switching
costs, not capabilities. Treating the alternative as a token control
("route at least one task Kanban-native") understates what the evidence now
supports.

## Decision

1. **Pilot 1B's worker layer runs two arms of comparable, real tasks:**
   - **Arm S (incumbent):** Hermes delegating to Shelley conversations via
     the CLI wrapper skill, per the existing plan.
   - **Arm C (challenger):** Hermes Kanban dispatch to native CLI workers —
     the Codex app-server runtime for OpenAI-side tasks and the bundled
     claude-code skill (print mode) for Anthropic-side tasks.
   Neither arm is the default; worker-routing policy assigns tasks to arms
   explicitly so results are attributable.
2. **Arm C setup is a pilot prerequisite**, alongside ADR 0004's three
   artifacts: install Codex CLI (≥ 0.130.0) and Claude Code on the pilot VM,
   complete both subscription logins, enable the app-server runtime for a
   dedicated worker profile, and run the live probes listed in the research
   note before real tasks flow.
3. **Evidence comparison is part of the evaluation.** For matched tasks,
   compare Kanban run/event/receipt history against Entire checkpoints from
   Arm S for answering the contract's two diagnostic questions. Building an
   `entire-agent-hermes` plugin is deferred until this comparison shows a
   concrete gap (ADR 0004: prefer native behavior, record the finding).
4. **ADR 0005's Shelley justification is restated:** Shelley earns Phase 2
   worker-substrate status only if exe.dev integration, drill-down UX, or
   migration cost demonstrably outweigh the Hermes-native worker path — not
   on subscription, harness, or evidence grounds, which are no longer
   distinctive. ADR 0005's evaluation discipline (name the residual that
   justified each layer; "it worked" is not evidence) stands.
5. The Hermes-vs-Shelley-manager null from ADR 0005 §1 is unaffected.

## Consequences

- The pilot plan's worker-routing exercise (§5.5) and hypotheses (§5.8) are
  read as a two-arm comparison; the plan is cross-referenced accordingly.
- If Arm C matches Arm S on quality and supervision cost, Phase 2 drops
  Shelley from the Freddie worker substrate and the metadata-chain invariant
  resolves to Kanban task/run IDs instead of Shelley conversation IDs.
- If Arm C fails on harness quality, sandboxing on exeslim, subscription
  economics, or mobile drill-down, that failure is recorded with specifics
  and Shelley's incumbency is affirmed on observed — not assumed — grounds.
- Risk note: the app-server runtime is opt-in, OpenAI-scoped, and its cron
  interaction is documented as untested upstream; Arm C tasks stay off cron
  paths during the pilot.
