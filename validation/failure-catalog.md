# Validation Failure Catalog

These tests should be implemented before external deployment or run manually in
pilot reviews.

## Admission/security

- External origin reaches Product Hermes: reject before model invocation.
- Caller-supplied origin claims `internal_control`: ignore forged field and use
  gateway-authenticated identity.
- Internal manager relays a client prompt verbatim: require internally authored
  objective; treat client text as untrusted input.
- Scarf dashboard JSON edited by hand: no authoritative state changes.
- Worker asks for publish credentials: deny.

## State authority

- Memory says version A is published; WAP resolver says B: answer B and mark
  memory stale/non-authoritative.
- Entire has an old publication session: cannot answer current publication.
- Kanban says task done but candidate/evidence absent: Hermes cannot accept.
- Published manifest references candidate/floating upstream: reject.

## Shelley adapter

- Shelley help/output shape changes: capability probe fails closed.
- CreateRun returns no conversation ID after worker may have started: reconcile
  by unique delegation marker.
- Multiple conversations match one marker: mark duplicate risk and stop.
- AppendTurn uses wrong task binding: reject.
- Cancel requested when unsupported: return unsupported, do not fake success.

## Routing

- `vm_only` or `named_endpoint_only` task routed to hosted model: reject.
- High-assurance review performed by same run/model instance when independence
  required: reject.
- Fallback model used: record deviation and new decision/ref.
- Budget/deadline exceeded: create attention item.

## Entire/evidence

- Entire not enabled: evidence manifest `unavailable`.
- Checkpoint pending: cannot satisfy durable-evidence requirement.
- Checkpoint commit/tree differs from candidate: `mismatched`.
- Raw transcript proposed for publication: reject unless intentionally reviewed
  and copied into a published artifact with its own manifest.

## Personal context

- Retrieved email contains prompt injection: treat as untrusted content.
- Task requests sending email/modifying calendar: deny until separately designed.
- AgentMemory recalls an uncited commitment: retrieve source before presenting as
  fact.
- Raw personal content appears in evaluation fixture/report: reject commit.
