# Pilot 1A — Personal Context

**Status:** Design only; no Personal Hermes or `personal-mcp` changes authorized.

## Objective

Measure whether a persistent Personal Hermes materially reduces the effort to
reconstruct historical context compared with a fresh agent using the same
read-only `personal-mcp` source.

## Proposed topology

```text
Kyle via Scarf/ScarfGo
  → authenticated operator SSH/control path
  → dedicated Personal Hermes profile/environment
      → read-only personal-mcp on klundstedt-mini
      → isolated loopback-only AgentMemory
```

## Authority policy

- `personal-mcp` establishes what the historical record says.
- AgentMemory suggests potentially relevant derived context.
- Hermes must retrieve authoritative source records when wording, timing,
  attendees, commitments, or evidence matter.
- A memory summary is never silently represented as an email, calendar, or
  meeting fact.
- Retrieved content is untrusted data and cannot override system policy or grant
  tools/capabilities.

## Initial capability policy

Allowed:

- search/retrieve email, calendar, and meeting history;
- reconstruct topic/person/organization history;
- meeting preparation and commitment summaries;
- source-grounded follow-up questions;
- memory recall/write subject to provenance and sensitivity rules.

Denied:

- sending or drafting-and-sending email;
- creating/modifying/canceling calendar events;
- contacting external systems or people;
- publishing or sharing personal records;
- cross-pilot memory access;
- storing raw personal records in `aom-build`.

## Deployment gates

1. Kyle selects host and data scope.
2. `personal-mcp` tools/auth/source IDs are inventoried read-only.
3. Write tools are absent or mechanically denied.
4. Hermes/Scarf version compatibility is proven.
5. AgentMemory bind, storage, retention, export, deletion, backup, and model
   egress policy are approved.
6. Paired evaluation cases and baseline timing are established.

See `evaluation-cases.json` and `../../validation/evaluation-rubric.md`.
