# Current Capability Snapshot — 2026-09-03

This is a dated verification record, not a permanent compatibility promise.
Re-run the checks before deploying either pilot.

## Local `aom-build` VM

### exe.dev / IV provisioning

- VM: `aom-build`; default proxied port: `8000`.
- Attached capabilities visible through the supported reflection integration:
  `repo-aom-build-rw`, `api-tailscale`, `notify`, `llm`, and `reflection`.
- The VM uses `exeslim-dev` plus IV provisioning commit
  `1871444e8a9f6a682c9bff19352c8401c1ba5ec5`.
- No Hermes, Scarf, ScarfGo, or AgentMemory executable is installed here.
- Shelley and Entire are installed and active/available.

Local sources: `/home/exedev/iv-provision.lock`, `systemctl cat
shelley.service shelley.socket`, and `https://reflection.int.exe.xyz/`.

### Shelley

Verified with `shelley version`, `shelley models`, and `shelley client help`:

- Version: `0.959.914757635`, commit
  `33df9d893b0de54d32942c7541841cb0e626baa2`.
- Service binds to `127.0.0.1:9999` through systemd socket activation and
  requires the exe.dev-injected `X-Exedev-Userid` header on HTTP access.
- Experimental CLI supports:
  - `chat -p ... [-c id] [-model model] [-cwd dir] [-ephemeral]`;
  - `read [-wait] id`;
  - `list`, `search`, and `archive`.
- No stable CLI capability negotiation, cancellation operation, or documented
  creation idempotency is exposed. The adapter must advertise only verified
  operations and reconcile ambiguous creates.
- Current local model catalog includes `gpt-5.6-sol`, `gpt-5.6-luna`, and
  hosted Qwen-family models. It does **not** expose a model named Fable or a
  verified self-hosted Qwen endpoint. Target-VM routing mappings remain unknown.

### Entire and Shelley capture

Verified with `entire version`, `entire agent-help`, the installed plugin, and IV
provisioning documentation:

- Installed Entire CLI: `0.10.1`.
- Latest upstream release observed: `0.10.4` (2026-09-02), but IV intentionally
  pins a qualified pair rather than independently following latest.
- Installed IV plugin: `entire-agent-shelley` `0.1.3`, external-agent protocol
  version 1.
- The plugin is discovered as `shelley`, reports live lifecycle hooks, reads the
  Shelley SQLite database directly, and implements full-session projection at
  turn end.
- IV documents Entire `0.10.1` + plugin `0.1.3` as qualified together on
  2026-08-19. Do not upgrade one without re-qualification.
- Entire is not enabled in `aom-build`; no pilot repo was changed during this
  bootstrap.
- Per-repository enablement is expected to use a git-backed checkpoint backend
  and install Shelley hooks. The exact command must be re-confirmed on the
  target VM with `entire agent-help enable` before execution.

Upstream sources:

- [Entire CLI releases](https://github.com/entireio/cli/releases)
- [External Agent Plugin Protocol](https://github.com/entireio/cli/blob/main/docs/architecture/external-agent-protocol.md)
- [Agent Integration Checklist](https://github.com/entireio/cli/blob/main/docs/architecture/agent-integration-checklist.md)

## Hermes Agent

Upstream release observed on 2026-09-03:

- Latest release: Hermes Agent `v0.21.0` / tag `v2026.8.31`, published
  2026-08-31.
- Linux installer is supported and creates a per-user Hermes home under
  `~/.hermes/`; service-user installs are supported.
- Hermes profiles isolate config, `.env`, SOUL, memory, sessions, skills, logs,
  cron, gateway state, and state DB through `HERMES_HOME`. A profile is **not** a
  filesystem sandbox; local tools retain the host user's filesystem access.
- Programmatic interfaces include ACP over stdio, TUI gateway JSON-RPC, and an
  OpenAI-compatible HTTP/SSE API. Scarf remote rich chat uses ACP over SSH.
- Hermes Kanban is a local SQLite-backed, single-host current-work system.
  Separate boards are hard isolation; tenant labels are soft filters.
- Kanban supports task statuses, dependencies, runs, append-only events,
  review/changes-requested transitions, attachments, per-task model overrides,
  and a REST/dashboard surface.
- Kanban auto-decomposition is enabled by default upstream. The Freddie pilot
  should start in manual mode and disable automatic creator-session follow-up
  until reviewed.
- Hermes security includes gateway allowlists/pairing, dangerous-command
  approvals, user deny rules, MCP environment filtering, context-file scanning,
  SSRF controls, and container/SSH backends. These are defense in depth, not a
  replacement for VM/network isolation.

Sources:

- [Hermes Agent releases](https://github.com/NousResearch/hermes-agent/releases)
- [Installation](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/getting-started/installation.md)
- [Programmatic integration](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/programmatic-integration.md)
- [Profiles](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/profiles.md)
- [Kanban](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/kanban.md)
- [Security](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/security.md)

## Scarf / ScarfGo

Upstream release observed on 2026-09-03:

- Latest Scarf release: `v3.0.1`, published 2026-09-03.
- Requirements: macOS 14.6+ for Scarf and iOS 18+ for ScarfGo.
- Remote hosts use key-based SSH; Scarf documents `sqlite3`, `pgrep`, and a
  readable Hermes home as remote requirements.
- Rich chat tunnels `hermes acp` over SSH. Scarf reads Hermes SQLite state
  read-only and performs management actions through Hermes CLI/protocols.
- The current README documents Hermes `v0.20.4` as its verified target, while
  Hermes `v0.21.0` is newer. Compatibility must be tested before pinning.
- Scarf project dashboards use `.scarf/dashboard.json` schema version 1.
  Supported widgets include stats, progress, text, table, chart, list, webview,
  markdown file, log tail, cron status, status grid, Kanban summary, and image.
- Dashboard files are projections. Embedded webviews and file widgets require
  careful path/URL policy; they are not a security or publication boundary.
- ScarfGo stores an on-device Ed25519 key in the iOS Keychain and connects to
  configured Hermes hosts over SSH according to the project README.

Sources:

- [Scarf releases](https://github.com/awizemann/scarf/releases)
- [Scarf README](https://github.com/awizemann/scarf/blob/main/README.md)
- [Dashboard schema](https://github.com/awizemann/scarf/blob/main/scarf/docs/DASHBOARD_SCHEMA.md)

## AgentMemory

Upstream release observed on 2026-09-03:

- Latest release: `v0.9.29`, published 2026-08-16.
- Requires Node.js 20+ and a pinned iii-engine runtime; default local ports are
  3111 (REST/MCP), 3112 (streams), 3113 (viewer), and 49134 (worker WebSocket).
- REST binds to `127.0.0.1` by default. Protected endpoints use a bearer secret
  when `AGENTMEMORY_SECRET` is set.
- The Hermes integration can be MCP-only or a deeper memory-provider plugin.
  Plugin hooks include prefetch, turn sync, session end, pre-compress, memory
  write mirroring, and system-prompt block injection.
- The provider's turn sync must be non-blocking. Provider data is profile-scoped
  by Hermes but the AgentMemory service/data directory must also be isolated by
  pilot.
- Keyless mode provides BM25; local embeddings are opt-in. LLM observation
  compression is off by default and may create significant data egress/token
  use when enabled.
- The upstream integration does not make memory authoritative. AOM adds source
  references, staleness, scope, sensitivity, and explicit `non_canonical`
  authority to memory records.

Sources:

- [AgentMemory releases](https://github.com/rohitg00/agentmemory/releases)
- [AgentMemory README](https://github.com/rohitg00/agentmemory/blob/main/README.md)
- [Hermes integration](https://github.com/rohitg00/agentmemory/blob/main/integrations/hermes/README.md)
- [Hermes memory-provider API](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/developer-guide/memory-provider-plugin.md)

## Design consequences

1. Pin and qualify a tool **set**, not independent latest versions.
2. Treat Fable and self-hosted Qwen as unresolved capabilities, not assumed
   model IDs.
3. Use a dedicated Hermes profile, AgentMemory instance/data directory, Kanban
   board, and admission path per pilot.
4. Keep AgentMemory and dashboard ports loopback-only unless a separately
   authenticated private-network design is approved.
5. Use the IV Shelley adapter for Entire only after target-repo enrollment and a
   live capture test.
6. Build adapters against public CLI/protocol contracts and capability probes;
   do not rely on mutable SQLite schemas except where an upstream integration
   explicitly owns that compatibility burden.
