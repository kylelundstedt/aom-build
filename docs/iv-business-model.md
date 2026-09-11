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

## 3. Why buyers pay: the demand side

The analogy must survive one hard question: why do firms pay
accountants at all, and why should firms pay for datasets with
graduated assurance?

### 3.1 Why firms pay accountants

Five distinct reasons — and it matters that they are distinct:

1. **Verification economics.** Any counterparty *could* verify a
   company's books, but it is expensive, requires access, and every
   counterparty would duplicate the work. One specialist verifies once;
   N counterparties rely. Assurance replaces N private due-diligence
   exercises with one shared, credible one.
2. **Information asymmetry / signaling.** Management knows the truth;
   outsiders don't, and management has incentives to shade. An
   unaudited statement is cheap talk. Paying an outsider who risks
   their franchise to attest is a costly signal; the *willingness to be
   audited* is itself information.
3. **Risk and liability transfer.** If audited statements are wrong,
   a party with reputation, insurance, and legal exposure stands behind
   them. The buyer is partly buying **recourse**.
4. **Coordination on a standard.** GAAP lets a lender compare 50
   borrowers without negotiating 50 bespoke definitions of "revenue."
   Much of the value is standardized semantics, not the checking.
5. **Compulsion.** The largest by volume: regulators and exchanges
   mandate audits. Demand is legally manufactured.

### 3.2 Which reasons transfer to IV Datasets

**#5 does not transfer.** Nobody mandates buying an attested
loan-level dataset. IV's demand must be built voluntarily on #1–#4.
That discipline shapes the whole model.

**#1 transfers strongly — the core pitch.** Every consumer of
Freddie/Fannie/Ginnie loan-level data re-does the same verification
work: reconciling counts against disclosures, resolving code-set
changes across vintages, chasing schema drift, rediscovering the known
traps in the raw files. Each buyer pays that cost privately, badly, and
repeatedly. IV verifies once, retains the evidence, and N clients rely.
**The buyer is not paying for the data — the GSEs give it away. They
are paying to not run their own verification shop.** That is the
auditor's economic seat.

**#2 transfers, with a twist.** The asymmetry is not about IV's honesty
but about the *raw data's* fitness, which the client cannot cheaply
assess. Published audit evidence plus the workpaper standard (§7)
converts "trust me" into "check me": the signal is that IV *invites*
re-performance. Very few data vendors can.

**#3 transfers and is underpriced in the data market.** When a model
built on bad data misprices a portfolio, today no one is accountable —
the GSE disclaims, the vendor's terms disclaim. An attested dataset
with a named signer and an evidence chain gives the client's own
governance chain someone to point to.

**#4 transfers.** Published semantics, code sets, and lineage are the
GAAP function: two clients of `gse-lld@42` compare results without
renegotiating what "loan purpose" means across three agencies and
fifteen vintages.

### 3.3 The real buyer: model risk management

The purchasing center is often not the analyst but the client's
**model-risk / model-validation function** (the SR 11-7 world), which
must document data provenance and quality for every model input
regardless of vendor. IV's evidence bundle is a compliance artifact
they currently fabricate themselves, expensively. This is the closest
IV gets to compulsion (#5): regulation compels the *client's*
diligence, and IV sells the pre-packaged answer to it.

### 3.4 Why assurance is graduated

Assurance is costly to produce, and its value scales with the **stakes
of the decision the data feeds**, not with the data itself:

- Exploratory research, a conference chart, a quick backtest —
  wrongness is cheap; agent-compiled suffices, and audit pricing would
  lose the sale.
- A production pricing model, a regulatory submission, a fairness
  analysis — wrongness is catastrophic, and the client's own auditors
  will ask how inputs were validated; human-signed, re-performable
  evidence is worth a large multiple.

Flat assurance fails in both directions: audit-everything prices out
the low-stakes buyer and burns scarce signing capacity;
audit-nothing forfeits the high-stakes buyer. Graduated tiers (§6) are
price discrimination along the only axis that matters — **the cost of
being wrong** — in a structure buyers already understand
(compilation → review → audit), so the pricing needs no education.

Two further reasons:

- **Rationing the scarce resource.** Agent throughput is elastic; the
  human signature is not. Tiers ensure the signature is spent only
  where a signature is what is being bought.
- **Upgrade funnel.** A client starts agent-compiled for research; the
  model works; it heads to production; model risk asks for provenance —
  and the upgrade to human-signed is a version pin plus a fee, not a
  migration. The low tier is distribution for the high tier.

### 3.5 One-sentence answers

- Firms pay accountants to **replace N expensive private verifications
  with one credible shared one, and to have someone accountable when it
  is wrong** — with regulation inflating the volume.
- Firms should pay for graduated-assurance datasets because
  **verification of free data is the actual cost, the value of
  verification scales with decision stakes, and their own regulators
  already compel them to buy it — currently from themselves,
  expensively.**

## 4. The firm is organized around the Product DAG

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

## 5. Where humans concentrate

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

## 6. Controls-based trust: how the audit gate scales

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

## 7. The workpaper standard for evidence

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

## 8. Why the boundary makes agent-heavy production sellable

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

## 9. Independence caveat

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

## 10. Revenue lines

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

## 11. Risks created by the model

- **The gate is the bottleneck by design.** Managed via controls-based
  trust and explicit assurance-tier policy (§6), not by weakening the
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
- **Self-audit perception.** Addressed by the independence caveat (§9):
  precise language now, external examination of controls later.

## 12. What the freddie-sflld pilot tests, commercially

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

## 13. Summary invariants

1. IV sells assurance over published data products, not labor and not
   content. The buyer's alternative is running their own verification
   shop over free raw data; IV verifies once so N clients can rely.
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
