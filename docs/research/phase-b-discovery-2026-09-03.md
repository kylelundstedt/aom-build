# Phase B Discovery Notes — 2026-09-03 (read-only, from aom-build)

Probes run from this VM over the tailnet; nothing modified anywhere.

## Tailnet inventory

Relevant hosts visible: `klundstedt-mini` (100.123.154.23), `ai`,
`fannie-sflpd-poc`, `iv-personal-mcp-relay` (100.105.81.31), `iv-home`,
`iv-entire-agent-shelley`, plus IV infra VMs. Personal devices
(mbp/ipad/iphone) currently offline.

## Findings

1. **No `freddie-sflld` VM exists yet.** Nothing matching on the tailnet;
   `freddie-sflld.exe.xyz` does not resolve. A `fannie-sflpd-poc` VM exists
   (the sibling Fannie product). → The Product VM and repo apparently need to
   be created, or live under a name I haven't found. **Question for Kyle.**
2. **No `freddie-sflld` GitHub repo visible** (404 for freddie-sflld /
   freddie-sflpd under kylelundstedt — though 404 is also what a private repo
   returns to unauthenticated queries; a repo integration would see it).
3. **`iv-personal-mcp-relay` exists** and serves :8000, returning 403 to
   unauthenticated requests — consistent with an authenticated MCP relay for
   `personal-mcp`. This is likely the intended access path for Pilot 1A
   (rather than talking to klundstedt-mini directly). Auth mechanism unknown;
   needs Kyle or a look at that VM.
4. **Qwen endpoint on klundstedt-mini: not found.** Only :8080 is open of ~25
   common LLM-serving ports probed (11434 Ollama, 1234 LM Studio, 8000/8001
   vLLM, 5000, 8888, 30000, 52415, etc.), and :8080 is the AgentsView source
   daemon (serves HTML). If Qwen runs there, it's on an unprobed port, bound
   differently, or not currently running. **Need the port/server type from
   Kyle.**
5. **Personal Hermes VM does not exist yet** (per D-002 it is to be a new
   dedicated VM).

## Consequences for the critical path

- Pilot 1B needs the Product VM/repo identified or created before Hermes
  installation. Creation is possible from here via the `create-vm` skill once
  authorized.
- Pilot 1A needs: (a) the new Personal Hermes VM created; (b) the
  personal-mcp relay auth model confirmed.
- Local-Qwen routing stays fail-closed; hosted-only strategies work today.
