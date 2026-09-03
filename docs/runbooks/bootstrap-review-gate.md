# Bootstrap Review and Authorization Gate

Use this runbook before making any change to Personal Hermes,
`klundstedt-mini`, `personal-mcp`, or `freddie-sflld`.

## 1. Review artifacts

- [ ] Architecture Contract invariants accepted.
- [ ] ADR 0001 state authority/trust boundaries accepted or revised.
- [ ] ADR 0002 contract-first adapters accepted or revised.
- [ ] P0 decisions in `docs/decisions-required.md` resolved.
- [ ] Backlog priorities and pilot success thresholds approved.

## 2. Authorize a bounded next action

Authorization should name:

- target VM/system;
- read-only discovery versus configuration/change permission;
- permitted repositories and paths;
- permitted network endpoints and credentials;
- whether service installation/restart is allowed;
- whether Product candidate state may change;
- whether AUDIT or PUBLISH may run;
- rollback expectation.

An authorization for one pilot does not authorize the other.

## 3. Preflight before each external change

- [ ] Re-run dated capability/version checks.
- [ ] Read target repository guidance and inspect git status.
- [ ] Capture current config/version/service status without secrets.
- [ ] Confirm backup/restore path.
- [ ] Confirm intended bind addresses and ingress identity.
- [ ] Confirm personal/unpublished data egress policy.
- [ ] Confirm no external prompt route to Product Hermes.
- [ ] Prepare rollback commands.

## 4. Change record

Record in the implementation PR/report:

- exact versions and source SHAs;
- exact commands or configuration changes;
- systems touched;
- validation results;
- rollback performed/tested;
- unresolved warnings;
- links to the applicable Kanban task, Shelley conversation, and Entire evidence
  when those systems are active.

## 5. Stop conditions

Stop and request a decision if:

- Product identity/publication state is ambiguous;
- a tool would bind a sensitive service publicly;
- a write-capable personal tool cannot be mechanically disabled;
- a target model violates locality/data-egress policy;
- Shelley/Entire correlation cannot be verified;
- an audit fails;
- evidence is pending/missing/mismatched;
- a requested action exceeds the named authorization.
