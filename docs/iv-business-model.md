# IV Business Model: An Assurance Firm for Data Products

**Status:** Working framing

**Companion to:** `iv-agent-operating-model.md`,
`architecture-contract.md`, ADR 0007 (Intentional Publication Boundary)

## 1. Thesis

How does IndustryVault organize as a business, and sell IV Datasets,
when most of the work is done by agents?

When execution is cheap and rentable — anyone can hire the same
frontier models — labor is not what clients pay for. What clients
cannot rent is an accountable entity that stakes its name on a
specific, immutable, evidenced artifact. The publication boundary
(ADR 0007) separates cheap, probabilistic, agent-generated candidate
work from attested product IV stands behind: it is simultaneously the
security perimeter, the trust product, the pricing line, and the
commercial boundary between cost of goods and revenue surface.

**One-line model:** IV is an assurance firm for data products. Agents
keep the books, controls run the close, evidence fills the workpapers,
and a human signs the opinion.

Four claims carry the model:

1. **IV sells assurance, not labor and not content.** The buyer's
   alternative is running an internal verification or
   source-system-decoding team — expensive, unattested, key-person
   fragile. One specialist verifies; N reliers rely.
2. **What amortizes differs by product layer** — verified public data,
   source-system semantic models, or the canonical function model —
   but in every layer the amortizing asset is methodology and evidence,
   not headcount (§2).
3. **Assurance is produced by controls, proven by re-performable
   evidence, and priced in graduated tiers** (§4).
4. **For products carrying client NPI through agent workers, the
   publication boundary is not good architecture — it is the
   precondition for the business existing** (§2.4).

### 1.1 Why accounting, not manufacturing

A manufacturing analogy fits the production interior well — ADR 0007
already calls it a factory, the Product DAG is a bill of materials,
the release tuple is lot genealogy, and controls-based trust (§4.1) is
statistical process control. Use that vocabulary freely for
architecture and operations.

But manufacturing fails as the *business* frame. Data is a **credence
good**: unlike a widget, the buyer cannot cheaply assess its fitness
even after use, so demand rests on assurance economics — verification
transfer, signaling, recourse, standards (§3) — for which
manufacturing has no story. Data's ~zero marginal reproduction cost
makes per-unit manufacturing pricing intuitions wrong. And the central
human role, the accountable signer, has no manufacturing equivalent:
nobody buys a widget because of who signed the QC report.

The decisive distinction: **a factory's quality process is invisible
to the widget buyer; IV's controls and evidence ship with every
release as the product surface.** When the quality process is what the
customer buys, the firm is an assurance firm that runs a factory — not
a manufacturer with a QA department. The frames compose: manufacturing
inside the boundary, accounting at and beyond it.

## 2. The product line: three economic layers

``` text
Layer                Examples                     Data ownership   What amortizes across N clients
------------------   --------------------------  ---------------  --------------------------------
public-source        gse-lld (fannie/freddie/     public / free    the verified DATA itself
cores                ginnie), FEMA, HMDA

proprietary-source   msp-core, loanserv-core,   client NPI       the SEMANTIC MODEL of the
cores                encompass-core, byte-core,                  source system (not the data)
                     default-management cores

function-specific    ServicerVault,               composite        the CANONICAL FUNCTION MODEL
composites           OriginatorVault                               (source-agnostic semantics)
```

**Public-source cores.** The raw data is free; the product is
verification. One WAP pipeline; N clients rely on the same published
versions. Classic verify-once/N-rely economics — the entry layer, not
the flagship.

**Proprietary-source cores.** `msp-core` for Client A cannot be sold
to Client B — the data is Client A's non-public servicing book. What
amortizes is the **source-system semantic model**: the hard-won map of
MSP's ~50,000 fields, code sets, stop codes, misuse patterns, and
extract quirks — likewise LoanServ, Encompass, Byte, and adjacent
default-management systems. Every client on MSP pays IV to apply the
same versioned methodology to their private data. This is the audit
firm's structure exactly: standardized methodology applied to each
client's private books, producing comparable attested statements.

**Function-specific composites — the flagship.** ServicerVault and
OriginatorVault present a client's servicing or origination operations
in standardized, attested, source-agnostic form, composed from that
client's proprietary cores plus shared public cores. The accounting
mapping completes:

``` text
IV canonical function model      GAAP (align with / extend MISMO —
                                 "MISMO is our GAAP")
msp-core / encompass-core      the audited books
ServicerVault / OriginatorVault  the financial statements
```

Comparability is a first-class feature: ServicerVault means the same
thing whether the client runs MSP or LoanServ, as statements mean the
same thing under GAAP regardless of the ERP.

### 2.1 Family → product → instance

Composites require a three-level hierarchy the architecture documents
do not yet model (backlog C-016):

``` text
family     ServicerVault                canonical model, coverage levels,
                                        versioned source→canonical mappings
  product  Oversight, Reporting         function-specific mapping/metric
                                        sets, versioned per product
    instance  servicervault-oversight@cmg   client data, entitlements,
                                            releases, per-client VM
```

The family and product levels are shared IV IP and contain no client
data; the instance owns the client's data and release stream. A
published instance release is identified by a **tuple, not a scalar**:
family/mapping versions, product, client, as-of period, revision, and
coverage level. Corrections republish the same as-of at a new
revision; published releases are never mutated. Two client instances
are comparable exactly when they share family and product versions.
Full mechanics: Appendix A.

### 2.2 Coverage levels are not assurance tiers

A family defines graded data coverage — level 1 (a small required
field set) through level 5 (thousands of mapped fields). Coverage
level (*how wide*) is orthogonal to assurance tier (*how verified*,
§4): a level-1/human-signed release and a level-4/agent-audited
release are both coherent products. A composite's **comparability
floor** is the highest level all its sources meet — which makes the
level-1 field set the keystone artifact of a family: the common
denominator that makes cross-source comparison possible at all.

### 2.3 Composite economics on the Product DAG

The DAG carries the economics: an instance release pins the client's
proprietary core versions plus shared published public-core versions.
Public-layer verification amortizes into every composite;
family/product methodology amortizes across clients on the same source
systems; only the client's data stays siloed. The marginal cost of a
new client instance approaches one client VM plus the already-built
semantic models.

### 2.4 The boundary as precondition

For the flagship layers the interior holds **client NPI flowing
through agent workers**. IV's market — regulated, agent-skeptical
buyers — will ask how to trust output from a stochastic process. The
boundary converts nondeterministic production into deterministic
product, and it is the only honest answer:

- **Publication, not sanitization.** No client-facing model ever holds
  unpublished or unauthorized information — guaranteed by topology and
  admission control, not prompts.
- **Evidence, not vibes.** Every release carries audit evidence and
  lineage satisfying the workpaper test (§4.3).
- **Reproducibility.** Immutable releases and pinned DAG dependencies
  make any published version reproducible indefinitely.
- **Per-client trust separation.** A separate VM/Hermes environment
  per client for proprietary cores, per the existing AOM rule; the
  shared asset is versioned semantic-model contracts — never shared
  runtime, never shared memory.

The architecture is a differentiator worth marketing, not internal
plumbing.

> **Naming convention (resolved):** **Vault** is reserved for
> client-facing composites (ServicerVault, OriginatorVault). Cores are
> named by role: source-system semantic-model cores as `msp-core`,
> `loanserv-core`, `encompass-core`, `byte-core`; per-client source
> datasets as `cenlar-extract@client` style. The name itself encodes
> the layer — ingredients versus attested product.

## 3. Why buyers pay

Firms pay accountants for five distinct reasons: **(1) verification
economics** — one specialist verifies once, N counterparties rely,
replacing N private due-diligence exercises; **(2) signaling** — an
unaudited statement is cheap talk, and paying an outsider who risks
their franchise to attest is a costly signal; **(3) recourse** — a
party with reputation and liability stands behind the statements;
**(4) coordination on a standard** — GAAP lets a lender compare 50
borrowers without 50 bespoke definitions of "revenue"; **(5)
compulsion** — regulators mandate audits.

**Compulsion does not transfer** — nobody mandates buying attested
datasets — so IV's demand must stand voluntarily on the other four:

1. *Verification economics, per layer.* Public cores: every consumer
   of GSE loan-level data re-does the same reconciliation, code-set,
   and schema-drift work; the buyer pays to not run a verification
   shop over free data. Composites: the buyer pays to not run the
   internal data-engineering team every servicer maintains to decode
   MSP extracts — a team whose output is unattested, undocumented, and
   key-person fragile.
2. *Signaling, with a twist.* The asymmetry is about the raw data's
   fitness, not IV's honesty. Published evidence plus the workpaper
   standard converts "trust me" into "check me": IV *invites*
   re-performance. Few data vendors can.
3. *Recourse, underpriced in the data market.* When a model built on
   bad data misprices a portfolio, today no one is accountable — the
   GSE disclaims, the vendor's terms disclaim. A named signer and an
   evidence chain give the client's governance chain someone to point
   to.
4. *Standards.* Published semantics, code sets, and lineage are the
   GAAP function across agencies, vintages, and source systems.

**The nearest thing to compulsion:** the purchasing center is often
the client's **model-risk / model-validation function** (SR 11-7
world) — or, for composites, subservicer-oversight and
investor-reporting duties — which must document data provenance and
quality regardless of vendor. Regulation compels the *client's*
diligence; IV sells the pre-packaged answer, currently produced
in-house with spreadsheets over incompatible extracts.

### 3.1 The industry already outsources attestation by default

Mortgage finance long ago decomposed into specialist attestation
functions everyone outsources; a lender is largely an assembler of
third-party attestations. IV slots into an existing buying pattern:

``` text
Precedent                 IV layer            What it proves
-----------------------   -----------------   --------------------------------
title plant / policy      public cores        free public records + proprietary
                                              verified copy = moat; policy adds
                                              insurance-grade recourse
flood zone certs          public cores        free FEMA maps + attested
                                              determination + life-of-loan
                                              monitoring + liability, per unit
tape cracking             composites          proprietary extracts normalized by
                                              paid specialists every deal —
                                              ServicerVault is continuous,
                                              attested tape-cracking as a
                                              subscription
McDash-style benchmarks   composites          servicers already ship raw MSP
                                              data out for canonical-semantics
                                              treatment
MSR valuation shops       composites          attested third-party analysis of
                                              a servicer's own tape
RMBS due-diligence        assurance tiers     priced sampling depths (10% →
sampling                                      100%) chosen by deal stakes
appraisal waterfall       assurance tiers     regulator-blessed graduated
                                              assurance, priced per item
```

Two cautions from the precedents: **title** shows verify-once
economics decaying into distribution-protected rent — IV's margins
must be defended by the evidence surface, not friction; **Clayton
(pre-2008 RMBS diligence)** shows evidence produced with the
consequence linkage broken — the historical form of accountability
theater (§7). Anti-model: **credit bureaus** — verify-once at maximum
scale but with weak recourse and no re-performability, which is
precisely IV's differentiation.

The pitch is therefore not "trust a novel agent-built product" but:
**"a specialist attestation layer this asset class has always paid
for — applied to datasets where buyers currently self-perform."**

### 3.2 Why assurance is graduated

Assurance is costly, and its value scales with the **stakes of the
decision the data feeds**: a backtest tolerates agent-compiled; a
production pricing model or regulatory submission demands
human-signed, re-performable evidence and is worth a large multiple.
Flat assurance fails both ways — audit-everything prices out
low-stakes buyers and burns scarce signing capacity; audit-nothing
forfeits high-stakes buyers. Graduated tiers are price discrimination
along the one axis that matters — **the cost of being wrong** — in a
structure buyers already understand (compilation → review → audit).
Tiers also ration the genuinely scarce resource (the human signature,
not agent throughput) and form an upgrade funnel: research use starts
agent-compiled; when the model heads to production and model risk asks
for provenance, the upgrade is a version pin plus a fee, not a
migration.

## 4. How assurance is produced

### 4.1 Controls-based trust

A naive "human signs every release" makes human attention the
bottleneck as agent throughput grows. Accounting solved this: auditors
do not re-verify every transaction — they **design controls, test that
the controls operate, and sample**. Translated:

- Humans design and periodically test the AUDIT stage:
  reconciliations, invariant checks, reviewer policy, thresholds.
- Agents execute the controls on every release.
- Humans sign on evidence that controls operated, plus exception
  review — not by re-reading worker output.

This is the operating model's management-by-exception posture (§20),
made principled.

### 4.2 Assurance tiers

``` text
Tier            Gate                                    Analogy
-------------   -------------------------------------   ------------
agent-compiled  automated controls only                 compilation
agent-audited   automated controls + agent review       review
                + human sampling of exceptions
human-signed    full control evidence + named human     audit opinion
                attestation on the release
```

Each release declares its tier in release metadata. Tier policy per
product is decided explicitly — never eroded implicitly under
throughput pressure.

### 4.3 The workpaper standard

The evidence chain has one concrete acceptance criterion:

> **Could a competent third party re-perform the audit from the
> retained evidence alone?**

Not "did we log it" — re-performability. This is the standard behind
pilot hypothesis 6 and the navigable chain in
`iv-agent-operating-model.md` §22.6 (Hermes → Kanban task → worker
conversation → execution → Entire evidence → repo/Product state → WAP
publication). A release whose evidence fails the workpaper test has
not completed AUDIT, regardless of what the checks reported. It also
requires that every release pin the exact mapping and methodology
versions that produced it (§2.1).

## 5. The firm

IV is not organized around functions — engineering, data ops, QA are
worker-routing policies. It is organized around **published Products**,
where accountability, liability, and pricing attach:

``` text
what IV sells   -> published Product versions + entitlements + Concierge
who owns it     -> a Product Hermes (operator)
                   + a named accountable human (signing principal)
how it is made  -> Bots + Shelley workers (fungible, invisible to clients)
how it composes -> the published Product DAG
```

Headcount does not scale with products; the DAG does. The moat is the
**accumulated published graph and its methodology**: verified public
cores, source-system semantic models, canonical function models,
lineage, audit evidence, release history. That corpus compounds and is
difficult for a competitor with identical model access to replicate.

**The audit-firm pyramid** is the one professional-services model
built on extreme leverage — partner signs, managers run engagements,
staff execute standardized methodology:

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
methodology that makes staff fungible; IV does the same with agents as
staff — which is why "worker selection is policy, not architecture" is
a business rule. **The core business metric is the leverage ratio:
Products credibly operated and signed per human hour.**

Three human roles survive agent-heavy production:

1. **The publish decision** — attestation requires a principal who can
   be trusted, referenced, and held responsible. Initially Kyle; later
   a small signing group per product family.
2. **The entitlement and commercial decision** — what is published
   *for whom*: contracts, pricing, exposure. Deliberately
   deterministic and outside any LLM.
3. **The operating model itself** — designing controls, audits,
   routing policy, and the agent organization is the new management
   work.

Everything else — ingestion, mapping, QA drafting, documentation,
routine client Q&A via Concierge — is agent work behind the boundary.

## 6. Revenue and pricing

If agents do the work, IV cannot bill hours and should not want to.
Revenue follows the boundary:

1. **Public-core entitlements** — subscription per Product/version
   stream. Entry line.
2. **Composite instances** — `servicervault-oversight@client` etc.:
   continuous attested operation of a client's proprietary cores plus
   composition into the canonical model. The flagship line; the
   tape-cracking-per-deal cost converted to a subscription.
3. **Concierge access** — near-zero-marginal-cost self-service over
   the published, entitled surface; removing the social friction of
   asking is itself a premium feature.
4. **Client-service Products** — `clientx-service` makes the
   relationship itself a Product with a published surface, making
   account service agent-operable.
5. **Assurance upgrades** — higher tiers priced separately per release
   stream.
6. **Cross-client benchmarking (future, opt-in)** — once N clients
   hold composites at shared family/product versions, published,
   entitlement-gated benchmarking becomes a product; feasible only
   because the boundary makes contributing safe.

**TBD — pricing structure.** The price metric is undecided: per
source, per loan, per coverage level × assurance tier, flat per
instance? The upgrade funnel (§3.2) implies the metric must make tier
upgrades cheap to buy and the comparability floor implies per-source
pricing distorts incentives. Needs a dedicated pass with real client
conversations.

## 7. Risks, caveats, competition

- **Independence.** Preparer and auditor are different firms in
  accounting; IV prepares *and* audits its own Products. Strictly, IV
  issues management-attested statements over audited internal
  controls, not independent opinions. Client language must be precise;
  the premium path is SOC-style external examination of IV's controls,
  or client auditors re-performing from IV workpapers — which the
  evidence surface exists to support.
- **The gate is the bottleneck by design.** Managed via controls-based
  trust and explicit tier policy (§4), never by weakening the
  boundary.
- **Accountability theater.** If humans rubber-stamp what the reviewer
  model approved, the attestation hollows out (the Clayton failure,
  §3.1). The human-facing evidence surface is therefore a first-class
  product requirement: a sign-off must be *real* in bounded time.
- **Institutional knowledge lives in agents.** AgentMemory and Hermes
  context are institutional capital. The operating-model rule that
  memory is never authoritative — canon lives in repo/Product/WAP
  state — is also business-continuity policy: IV can replace a Hermes
  instance, model vendor, or runtime without losing the company.
- **TBD — competition.** Who else could do this and why don't they?
  Candidates: source-system vendors (ICE/MSP itself), servicing
  analytics incumbents (McDash lineage), Big-4 advisory, in-house
  builds. A real positioning pass is needed; the provisional answer is
  that incumbents monetize lock-in or hours, and none invite
  re-performance.

## 8. What the freddie-sflld pilot tests, commercially

Read through this frame, the pilot (`iv-agent-operating-model.md`
§22) tests whether **one human can credibly *sign* — not merely
supervise — an agent-operated Dataset**:

- Can AUDIT produce evidence that makes a real human sign-off possible
  in bounded time (workpaper test)?
- Does "what is published right now, and how do you know?" resolve
  deterministically from WAP state (the close is real)?
- Does delegation traceability support the chain an external
  re-performer would need?
- Does the leverage ratio actually improve — sustained operation with
  less human context reconstruction and supervision?

If yes, the business scales by adding Products to the DAG — and client
instances to families — not people to the org chart.

---

## Appendix A: CMG Subservicer Oversight — versioning mechanics

> **Status:** Proposed mechanics, pending ADR and schema support
> (backlog C-016). Business insight summarized in §2.1–2.2; nothing
> here is yet binding architecture.

CMG uses four subservicers — ServiceMac, Cenlar, Northpoint, and
Merchants — providing extracts from ~70 fields (Merchants) to ~1,000
fields (Cenlar), with no standardization. The oversight DAG:

``` text
servicemac-extract@cmg ---+
cenlar-extract@cmg -------+--> servicervault-oversight@cmg
northpoint-extract@cmg ---+
merchants-extract@cmg ----+
```

**Release identity tuple.** Each published source release carries at
least:

``` text
cenlar-extract release = {
  family:   cenlar-model@S, cenlar→sv-mapping@M   # shared IV IP
  product:  oversight                              # mapping/metric set
  instance: cmg                                    # client's book at Cenlar
  as-of:    2026-08                                # data period
  rev:      2                                      # correction revision
  coverage: level 3
}
```

**As-of / revision axis.** Servicing data arrives periodically;
corrections republish the *same as-of* at rev+1, never mutating a
published release — the restatement discipline with a mechanism.

**Coverage levels.** The servicervault family defines level 1 (50–70
required fields) through level 5 (~3,000 fields drawn from the ~50,000
in MSP or LoanServ). Merchants' extract publishes only at level 1;
Cenlar's supports higher levels.

**Comparability floor.** `servicervault-oversight@cmg` pins the four
upstream release tuples (with an as-of alignment rule), family and
product versions, and a per-source coverage vector. The floor — the
highest level all sources meet, likely level 1 here — defines which
metrics are honestly comparable across subservicers; above it,
coverage is disclosed per source. The level-1 field set is thus the
family's keystone artifact.

**Versioned mappings.** Each (source model, product, coverage level)
has a versioned standardized mapping evolving independently of data
periods. Every release pins the exact mapping version that produced
it — required by the workpaper test (§4.3).

**Adjacent products.** The same client cores serve
`servicervault-reporting@cmg` under its own product-level mapping
versions — the family → product → instance hierarchy of §2.1 in
action.
