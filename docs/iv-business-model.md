# IV Business Model: An Assurance Firm for Data Products

**Status:** Working framing

**Companion to:** `iv-agent-operating-model.md`,
`architecture-contract.md`, ADR 0007 (Intentional Publication Boundary)

## 1. The question this doc answers

How does IndustryVault organize as a business, and offer IV Datasets as
a product, when most of the work is done by agents?

The answer falls out of the Intentional Publication Boundary. When
execution is cheap and rentable — anyone can hire the same frontier
models — labor is no longer the thing clients pay for. What clients
cannot rent is an accountable entity that stakes its name on a specific,
immutable, evidenced artifact. Everything left of PUBLISH is cheap,
probabilistic, agent-generated candidate material; everything right of
it is an attested product IV stands behind.

The fundamental information boundary — **working/internal versus
published** — is therefore also the commercial boundary between **cost
of goods and revenue surface**.

## 2. The governing analogy: accounting, not publishing

A publishing analogy captures part of this (immutable public artifact,
name-staking) but misses the essential part: publishers sell content;
accountants sell **assurance produced by controlled process**. IV's
clients are not buying novelty. They are buying the claim that
`freddie-sflld@117` is correct, reconciled, and reproducible.

WAP is a close process:

``` text
Accounting                            IV / AOM
----------------------------------   ----------------------------------
bookkeeping / journal entries        WRITE  — agent candidate work
controls, reconciliation, review     AUDIT  — checks + review + evidence
issue financial statements           PUBLISH — immutable Product version
workpapers                           Entire checkpoints + audit evidence
restatement (never edit filings)     new version (never mutate published)
notes / qualified opinion            known-limitations section
engagement partner signs opinion     accountable human signs release
segregation of duties                preparer ≠ reviewer ≠ approver
period close calendar                release cadence per Dataset
```

**One-line model:** IV is an assurance firm for data products. Agents
keep the books, controls run the close, evidence fills the workpapers,
and a human signs the opinion. The publication boundary is the line
between books-and-records and issued statements.

## 3. The firm is organized around the Product DAG

IV is not organized around functions (engineering, data ops, QA) —
those are worker-routing policies. It is organized around **published
Products**, because that is where accountability, liability, and
pricing attach:

``` text
what IV sells   -> published Product versions + entitlements + Concierge
who owns it     -> a Product Hermes (operator)
                   + a named accountable human (signing principal)
how it is made  -> Bots + Shelley workers (fungible, invisible to clients)
how it composes -> the published Product DAG
```

Headcount does not scale with products; the DAG does. The marginal cost
of a new Dataset approaches one more Product Hermes plus a WAP pipeline.
The moat is not people — it is the **accumulated published graph**:
semantics, lineage, audit evidence, release history, and the
methodology that produces them. That corpus compounds and is difficult
for a competitor with identical model access to replicate.

### The audit-firm pyramid

Audit firms are the one professional-services model built on extreme
leverage: a partner signs; managers run engagements; staff execute
against standardized methodology. Mapped:

``` text
Audit firm                    IV
--------------------------    --------------------------
signing partner               accountable human principal
engagement manager            Product Hermes
staff                         Shelley workers / Bots
firm methodology              contracts, invariants, WAP discipline,
                              worker-routing and audit policy
```

Audit firms spent a century optimizing partner:staff leverage through
methodology that makes staff fungible. IV does the same with agents as
staff. This is why "worker selection is policy, not architecture" is a
business rule, not only a technical one. The core business metric is
the **leverage ratio: Products credibly operated and signed per human
hour**.

## 4. Where humans concentrate

Three points survive agent-heavy production:

1. **The publish decision.** Agents can run every audit, but the
   attestation is the product, and attestation requires a principal who
   can be trusted, referenced, and held responsible. Initially this is
   Kyle; later a small editorial/signing group per product family.
2. **The entitlement and commercial decision.** What gets published
   *for whom* — contracts, pricing, what a `clientx-service` surface
   exposes. Deliberately deterministic and outside any LLM; inherently
   a human commercial judgment.
3. **The operating model itself.** Designing controls, audits,
   worker-routing policy, and the agent organization is the new
   management work.

Everything else — ingestion, mapping, QA drafting, documentation,
routine client Q&A via Concierge — is agent work behind the boundary.

## 5. Controls-based trust: how the audit gate scales

A naive reading of "human signs every release" makes human attention at
AUDIT the bottleneck as agent throughput grows. Accounting already
solved this: auditors do not re-verify every transaction. They **design
controls, test that the controls operate, and sample.**

Translated:

- Humans design and periodically test the AUDIT stage: reconciliations,
  invariant checks, reviewer (e.g., Sol) policy, coverage thresholds.
- Agents execute the controls on every release.
- Humans sign based on evidence that the controls operated, plus
  exception review — not on re-reading worker output.

The management-by-exception posture in the operating model (§20) is
this, made principled. The corresponding failure mode is
**accountability theater**: if the human rubber-stamps what the
reviewer model already approved, the attestation hollows out. Therefore
the audit-evidence surface is itself a product requirement: a human
sign-off must be *real* in bounded time.

### Assurance tiers

Accounting prices by assurance level (compilation → review → audit).
IV Datasets can do the same, turning graduated assurance from an
erosion risk into the pricing axis:

``` text
Tier            Gate                                    Analogy
-------------   -------------------------------------   ------------
agent-compiled  automated controls only                 compilation
agent-audited   automated controls + agent review       review
                + human sampling of exceptions
human-signed    full control evidence + named human     audit opinion
                attestation on the release
```

Each published version should declare its assurance tier as part of the
release metadata. The tier policy (which releases require which tier)
is decided explicitly, per Product — never eroded implicitly under
throughput pressure.

## 6. The workpaper standard for evidence

The accounting frame gives Entire and the audit-evidence chain a
concrete acceptance criterion — the workpaper test:

> **Could a competent third party re-perform the audit from the
> retained evidence alone?**

Not "did we log it," but re-performability. This is the crisp standard
behind pilot hypothesis 6 (provenance value) and the evidence chain in
`iv-agent-operating-model.md` §22.6:

``` text
Product Hermes -> Kanban task -> worker conversation
  -> execution -> Entire evidence -> repo/Product state
  -> WAP publication
```

A release whose evidence fails the workpaper test has not completed
AUDIT, regardless of what the checks reported.

## 7. Why the boundary makes agent-heavy production sellable

IV's market (GSE/mortgage data; regulated, agent-skeptical buyers) will
object: how do we trust output from a stochastic process? The boundary
converts nondeterministic production into deterministic product:

- **Publication, not sanitization.** No client-facing model ever holds
  unpublished or unauthorized information. This is an architectural
  guarantee (topology and admission control), not a prompt-engineering
  promise.
- **Evidence, not vibes.** Every published version carries audit
  evidence and lineage; "why should I trust field X?" is answered with
  a provenance chain that satisfies the workpaper test.
- **Reproducibility.** Immutable versions and pinned DAG dependencies
  mean a client's `gse-lld@42` is reproducible indefinitely, regardless
  of what agents did since.

The conversion itself is the trust product. The architecture is a
differentiator worth marketing, not internal plumbing.

## 8. Independence caveat

In accounting, preparer and auditor are different firms. IV prepares
*and* audits its own Products. Strictly, IV issues
**management-attested statements over audited internal controls**, not
independent audit opinions.

Implications:

- **Client language must be precise.** IV attests, with evidence
  sufficient for third-party re-performance. Do not imply independent
  audit.
- **A future premium tier exists.** Have IV's *controls* externally
  examined (SOC-style), or let a client's own auditors re-perform from
  IV workpapers. The evidence surface already supports this — that is
  what it is for.

## 9. Revenue lines

If agents do the work, IV cannot bill hours and should not want to.
Revenue follows the boundary:

1. **Entitlements to published Products** — subscription per Product /
   version stream. The core line.
2. **Concierge access** — near-zero-marginal-cost self-service over the
   published, entitled surface. Removing the social friction of asking
   is itself a premium feature.
3. **Composed and bespoke Products** — `clientx-service` makes the
   client relationship itself a Product with a published surface, which
   makes account service agent-operable.
4. **Assurance itself (future)** — higher assurance tiers priced
   separately; potentially running client-supplied data through IV's
   WAP pipeline and attesting the result.

## 10. Risks created by the model

- **The gate is the bottleneck by design.** Managed via controls-based
  trust and explicit assurance-tier policy (§5), not by weakening the
  boundary.
- **Accountability theater.** Countered by the workpaper standard and
  by treating the human-facing evidence surface as a first-class
  product requirement.
- **Institutional knowledge lives in agents.** AgentMemory and Product
  Hermes context become institutional capital. The operating model's
  rule that memory is never authoritative — canon lives in repo /
  Product / WAP state — is also business-continuity policy: it is what
  lets IV replace a Hermes instance, a model vendor, or a runtime
  without losing the company.
- **Self-audit perception.** Addressed by the independence caveat (§8):
  precise language now, external examination of controls later.

## 11. What the freddie-sflld pilot tests, commercially

Read through this frame, the pilot (`iv-agent-operating-model.md` §22)
is not only an operations experiment. It tests whether **one human can
credibly *sign* — not merely supervise — an agent-operated Dataset**:

- Can the AUDIT stage produce evidence that makes a real human sign-off
  possible in bounded time (workpaper test)?
- Does the diagnostic question "what is published right now, and how do
  you know?" resolve deterministically from WAP state (the close is
  real)?
- Does delegation traceability support the navigable chain an external
  re-performer would need?
- Does the leverage ratio actually improve — sustained operation with
  less human context reconstruction and supervision?

If yes, the business scales by adding Products to the DAG, not people
to the org chart.

## 12. Summary invariants

1. IV sells assurance over published data products, not labor and not
   content.
2. The publication boundary is simultaneously the security perimeter,
   the trust product, the pricing line, and the definition of the firm.
3. Agents prepare; controls close; evidence proves; a human signs.
4. Assurance level is an explicit, per-release, priced attribute —
   never an implicit casualty of throughput.
5. Audit evidence must pass the workpaper (re-performance) test to
   count as evidence.
6. IV attests to its own products over audited controls; it does not
   claim independence it does not have.
7. The core business metric is leverage: Products credibly operated and
   signed per human hour.
