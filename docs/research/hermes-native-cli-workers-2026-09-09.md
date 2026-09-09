# Hermes + Native CLI Workers — Verified Capabilities (2026-09-09)

**Checked:** Hermes Agent upstream docs (`main` branch) on 2026-09-09:
`user-guide/features/codex-app-server-runtime.md`,
`user-guide/skills/bundled/autonomous-ai-agents/autonomous-ai-agents-claude-code.md`,
`integrations/providers.md`, `user-guide/configuring-models.md`. Successor to
[kanban-worker-durability-2026-09-09](./kanban-worker-durability-2026-09-09.md),
which narrowed Shelley's residual value to subscription access, harness
quality, and Entire evidence. This note eliminates most of that residue.

## 1. Codex subscription: Hermes-native, first-class

The opt-in **Codex app-server runtime** hands `openai/*` turns to
`codex app-server` entirely: Codex's own toolset (`shell`, `apply_patch`,
`update_plan`), seatbelt/landlock sandboxing, and **ChatGPT subscription auth
(no API key)**. Hermes remains the shell: sessions DB, gateway, memory and
skill review; Codex events are projected into Hermes's message shape and
stream live into TUI/desktop/gateways.

**Kanban workers run on this runtime.** Dispatcher-spawned `hermes chat -q`
workers inherit `model.openai_runtime: codex_app_server`; the `kanban_*`
handoff tools work through an MCP callback gated by `HERMES_KANBAN_TASK`,
with narrow sandbox overrides for the board DB and pinned workspaces. This is
a documented, supported configuration — not a hack.

Limits: requires Codex CLI ≥ 0.130.0 and a separate `codex login`; runtime is
OpenAI-scoped; agent-loop tools (`delegate_task`, `memory`, `session_search`,
`todo`) are unavailable on it (mostly irrelevant to a Kanban worker); cron on
this runtime is documented as not specifically tested.

## 2. Claude subscription: native OAuth is poor; the bundled CLI skill is good

- **Hermes-native Anthropic OAuth** works only on Claude **Max with purchased
  extra-usage credits**, and consumes **only** those extra credits — never
  the base Max allowance. Claude Pro OAuth is blocked; Pro users are directed
  to pay-per-token API keys.
- **Bundled skill `autonomous-ai-agents/claude-code` (v2.2.1)** orchestrates
  the Claude Code CLI via the terminal tool, preferring one-shot print mode
  (`claude -p ... --allowedTools ... --max-turns N`). Auth is claude-code's
  own browser OAuth for **Pro/Max** — i.e., normal subscription allowance
  semantics, *better* than Hermes's native Anthropic path. Sibling bundled
  skills exist for `codex` and `opencode`.

Downside of the claude-code path (real but bounded): the inner agent's
reasoning arrives as captured terminal output, not projected events — no live
inner-turn streaming, coarser evidence granularity, and the outer Hermes loop
spends iterations supervising. The codex app-server path does not share this
downside.

## 3. Evidence: Kanban receipts may supersede Entire for WAP needs

Kanban PR completion contracts gate completion on GitHub **required checks**
and persist durable `pr_acceptance` events: PR URL, head SHA, required
contexts, check IDs/URLs, classifications, recovery instructions — written
under a single SQLite lock so a reclaimed worker cannot attach acceptance to
a new run. For publication-audit purposes this is arguably stronger evidence
than session checkpoints. An `entire-agent-hermes` plugin remains feasible
(public external-agent protocol; Hermes session transcripts and state DB in
`~/.hermes/`) but may be unnecessary; ADR 0004 already directs us to prefer
native behavior and record the finding.

## 4. Revised residuals for Shelley

| ADR 0005 residual | Status after this check |
|---|---|
| Codex subscription access | Hermes-native via app-server runtime |
| Claude subscription access | claude-code skill w/ Pro/Max OAuth ≥ Shelley's path |
| Coding harness quality | Codex harness runs natively; claude-code via skill |
| Entire evidence pipeline | Buildable for Hermes; Kanban receipts may supersede |

What remains for Shelley is **incumbency and exe.dev integration**: deployed,
qualified with Entire, wired into exe.dev auth/proxy and the mobile UI, and
already customized by IV. These are switching-cost arguments, not capability
arguments.

## Consequence

A **Hermes + native CLI workers** configuration (Kanban dispatch, Codex
app-server runtime, claude-code skill) is a complete worker substrate on
paper and must be piloted as a first-class arm, not treated as a
hypothetical control. Recorded as
[ADR 0006](../adr/0006-hermes-native-cli-worker-pilot-arm.md).

**Unverified / live-probe list for the pilot VM:**

1. Codex app-server runtime + Kanban worker end-to-end on exeslim (npm,
   codex ≥ 0.130.0, `codex login` headless via oauth-over-ssh guide).
2. Claude Max OAuth extra-credits-only billing behavior (documented today,
   not observed).
3. claude-code print-mode quality/latency under Kanban supervision vs. the
   same task in Shelley.
4. Whether Scarf drill-down into a codex-runtime worker session is adequate
   on iPhone/iPad.
