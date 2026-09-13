# Knowledge Work and Publication Boundaries

**Status:** Essay — a theory of the era, not binding on IV architecture
or plans.

**Companion to:** `iv-business-model.md` (§1.1, §3.1),
ADR 0007 (Intentional Publication Boundary)

## 1. Thesis

AI-era knowledge work — for a firm, a professional, or an employee —
takes one shape:

``` text
EXTERIOR: assurance        "I stand behind this artifact"
          (accounting)      signature, liability, reputation, recourse
------------- publication boundary -------------
INTERIOR: factory          "agents execute my codified methodology"
          (manufacturing)   prompts, skills, evals, routing, process
                            control
```

Externally you sell assurance; internally you automate with agents
without exposing your methodology. The accounting-versus-manufacturing
tension in the business model doc is not a choice between analogies —
it is this structure itself, and it generalizes to all knowledge work.

The claims, compressed:

1. Two forces produce the structure: AI forces you to **codify your
   tacit knowledge** exactly when codified knowledge becomes maximally
   copyable, and it **migrates scarcity from generation to
   accountability** — skin in the game is the one unrentable input
   (§2).
2. The structure is old: guilds, professions, industrialization, and —
   fully formed — modern mortgage finance all arrived at it wherever
   stakes were high enough (§3).
3. For firms, the economy reorganizes into a **DAG of publication
   boundaries** — tiny signing cores, large agent interiors, attested
   artifacts as the only things crossing — and specialist providers
   survive the disintermediation test that pure executors fail (§4).
4. For individuals, defensible positions reduce to **holding a
   signature or owning a boundary**; internal expertise alone is the
   weakly defended position (§5).
5. The structure applies to credence goods facing third parties, and
   fails predictably elsewhere (§6).
6. Its maintenance condition is **meta-tacit judgment**: signers must
   stay close enough to the work to detect factory failure, or the
   signature hollows (§7).

## 2. Two forces produce the structure

### 2.1 The codification paradox (the push)

Polanyi's observation — *we know more than we can tell* — used to be
protection. Tacit knowledge could not be cheaply extracted, so
expertise was naturally safe: unautomatable and uncopyable for the
same reason.

AI breaks that equilibrium asymmetrically. To automate your work you
must externalize the tacit into agent-runnable form — skills, prompts,
evals, contracts, routing policy. But **codified knowledge is exactly
the kind that can be exfiltrated, copied, or captured.** The act that
gives you leverage is the act that destroys your moat. Pre-AI you
could not codify your secret sauce; now you cannot afford not to, and
cannot afford to leak it. The crown jewels migrate from your head
(naturally protected) to your repo (protected only by topology).

The publication boundary is the resolution. ADR 0007's invariant —
*methodology stays home; semantics travel with the artifact* — read
generally, is what makes it **safe to codify yourself**: externalize
tacit knowledge into the interior, run it at machine speed, publish
only attested artifacts that carry meaning but not method. The ADR's
adversarial-review rule (can a consumer reconstruct interior
methodology from the published surface?) is a leak test on codified
tacit knowledge.

### 2.2 Scarcity migrates to accountability (the pull)

The exterior face must be accounting-shaped; this is not a branding
preference. AI commoditizes generation, which floods the verification
channel — cheap output makes "is this right?" more expensive and more
valuable, not less. Scarcity migrates:

``` text
generation -> verification -> accountability
```

The chain terminates at accountability because of what assurance is
made of:

``` text
evidence (re-performable)     <- agents can produce this
controls (tested, operating)  <- agents can run these
a signer with skin            <- only a person or institution
```

An agent cannot be sued, disbarred, or reputationally ruined; it has
no franchise to lose. **Being someone — identity, liability, skin in
the game — is the one input to knowledge work that cannot be rented
from a model vendor.**

The two forces meet at the boundary: the paradox pushes methodology
inside; the scarcity pulls the signature outside. What sits between
them — the gate, the controls, the evidence — is where the design
work of the era lives.

## 3. Precedents: the structure is old

- **Guilds.** The *masterpiece* was the attested public artifact; the
  *mystery* — literally the guild's term for its craft secrets —
  stayed interior, transferred only through controlled apprenticeship.
  A guild was a publication boundary with membership rules.
- **Professions.** Law, medicine, and accounting institutionalized the
  same structure: licensure and liability create the assurance
  exterior; proprietary judgment stays interior. A profession is a
  socially sanctioned right to sell signatures.
- **Industrialization.** When machines codified weaving, the execution
  premium died. Survivors took one of two positions: they owned the
  mill (the factory) or became inspectors and certifiers (the
  signature). Wage labor qua execution never recovered its premium.
  The AI-era choice set is the same: own the agent factory, own the
  accountability, ideally both.
- **Mortgage finance — the living existence proof.** The industry
  arrived at the full equilibrium a century before AI. Title plants,
  flood-zone determiners, appraisers, credit bureaus, diligence firms:
  each is an interior (proprietary methodology, plant, data)
  publishing attested artifacts — policy, certificate, opinion,
  score — that cross between firms. A lender is largely an assembler
  of third-party attestations; a loan file *is* a bundle of
  publication-boundary crossings. Mortgage got there early because it
  maximizes every driving condition: credence goods, dense
  counterparty chains (borrower → lender → GSE → investor →
  regulator), high cost of being wrong.

AI does not create the economy of boundaries; it extends an
equilibrium that already governs wherever stakes were high enough to
force it.

## 4. Consequences for firms: an economy of boundaries

### 4.1 The Coasean shift

Coase: firm boundaries sit where market transaction costs exceed
internal coordination costs. Agents collapse internal coordination
costs, so firms can shrink drastically. But market *trust* costs do
not collapse — they rise (§2.2). The equilibrium: **tiny human
signing cores, large agent interiors, and attested artifacts as the
only things crossing between entities.** Inter-firm relations become
exactly what `clientx-service` consuming `gse-lld@42` looks like —
published, versioned, evidenced surfaces. The economy trends toward a
DAG of publication boundaries, each firm an interior. IV is not
adopting an unusual architecture; it is arriving early at the general
form.

### 4.2 The disintermediation test

The demand-side dual of §2.2 must also hold: granted that someone
must sign, why pay *this* provider rather than rent the same agents
and internalize? Every knowledge-work relationship now faces this
test. (The IV-specific version and its answers:
`iv-business-model.md` §3.1.)

Three answers generalize:

1. **Agents commoditize generation, not verification.** Renting
   agents gives the buyer cheap production and a *larger*
   verification burden. Whoever's value was execution is
   disintermediated; whoever's value is the verification apparatus is
   strengthened by the same force.
2. **Self-attestation is structurally worthless to counterparties.**
   Second opinions, external audits, peer review, and licensed
   sign-offs exist because an interior cannot attest to itself.
   Renting agents changes the cost of producing an assertion, not
   whose name makes it credible.
3. **The N-case flywheel is unavailable to any single-buyer
   interior.** A specialist across N clients accumulates validated
   edge cases; agents can regenerate methodology but not the
   validation corpus.

The third answer is why the §4.1 equilibrium is stable as specialist
firms selling attested artifacts rather than every buyer running
everything in-house — and why it systematically favors external
specialists over internal staff, who see one book by definition.

## 5. Consequences for individuals: signature or boundary

The structure holds for an employee exactly as for a firm: what you
ultimately sell your employer is not output — they can rent that —
but your willingness to be the one accountable for it.

But run the disintermediation test for an individual employee and
most of the firm-level defenses fail: the employer needs no external
attestation for internal work (self-attestation to management is
fine); the employee sees one employer's cases (no flywheel); and IP
assignment hands the employer the codified methodology (no boundary
moat). Only the verification-burden argument and meta-tacit judgment
(§7) survive.

So the individual's defensible positions reduce to two: **(a) being
the accountable signer in a counterparty-facing role** — officer,
licensed professional, the person the regulator names — **or (b)
owning a boundary, i.e., the firm.** Pure internal expertise, however
excellent and agent-amplified, is the weakly defended position: its
codification is owned by the employer and its outputs need no
external signature.

The transition is contested ground. An employee who quietly automates
their own job is running an unlicensed publication boundary inside
their employer — selling attested outputs upward while keeping the
factory hidden. Employers will respond as they always have, with
IP-assignment claims over methodology. "Whose factory is it" becomes
a central labor conflict of the era. IV dodges this by construction:
the accountable humans own the firm that owns the factory.

## 6. Scope: where the structure does not apply

The whole argument assumes **credence goods facing third parties**. It
fails where knowledge work is (a) cheaply verifiable by the buyer on
receipt — the verification burden collapses; (b) consumed purely
internally with no counterparty — no attestation demand; or (c) valued
for taste or identity rather than correctness — content and
entertainment buy the voice, not the assurance. The safe harbors of
the era are not where work is hardest but where these conditions
break.

## 7. Maintenance: the meta-tacit condition

Codifying tacit knowledge does not drain the tacit pool — it moves it
up a level. What must remain tacit in the signer: knowing when the
methodology is wrong, smelling the exception the controls missed,
judging what to codify next. Call it **meta-tacit knowledge**. The
signature is only worth buying because the signer retains it; a signer
who can no longer detect factory failure is performing accountability
theater with extra steps — the Clayton failure
(`iv-business-model.md` §3.2), individualized.

The sustainability condition for any assurance-over-factory business:
**the signing humans must stay in enough contact with the work to keep
their exception-detection alive.** Skill atrophy is not an HR concern;
it is depreciation of the firm's core asset. For IV this argues for
humans periodically re-performing audits by hand — not because agents
cannot, but to keep the signature real.

## 8. Compressed

AI forces knowledge workers to codify their tacit knowledge (to get
leverage) at the exact moment codification becomes maximally dangerous
(anything explicit is copyable). The publication boundary is the
general resolution: factory inside, signature outside, methodology
never crossing. Scarcity migrates to accountability because
skin-in-the-game is the one unrentable input. Buyers still pay
particular providers because generation is rentable but verification
is not, self-attestation is worthless to counterparties, and the
N-case flywheel accrues only to specialists — so the economy
reorganizes into a DAG of such boundaries (as mortgage finance already
did, a century early), defensible individual positions reduce to
holding a signature or owning a boundary, and the residual human asset
is meta-tacit judgment, which must be actively maintained or the
signature hollows.

---

## Appendix A: Worked example — the mid-size mortgage lender

Apply the disintermediation test (§4.2) to an independent mortgage
bank (IMB) — a firm that is already mostly boundary network (§3) —
and ask what it should do internally when agents commoditize its
labor.

First, what an IMB actually sells: not loans as manufactured objects
but **signed loans**. Delivery to a GSE or aggregator is an attested
artifact — the file plus reps and warrants, backed by buyback
liability. The investor does not re-underwrite every file precisely
because the lender's signature has skin behind it. The IMB is itself
an assurance firm: interior = loan manufacturing; published artifact =
the saleable loan under R&W.

Running the test across its functions:

**Correctly external, permanently.** Title, flood, credit, MI,
appraisal, doc custody, often subservicing: each is a specialist with
an N-flywheel the lender can never match, and some are mandated
external — appraisal-independence rules literally encode "you cannot
attest to yourself." No amount of rented agents changes these.

**The contested middle: fulfillment labor.** Processing, underwriting
grunt work, closing prep, post-close stacking are WRITE, and agents
commoditize them — whether the lender's agents or a vendor's. But the
signature does not transfer: fulfillment vendors disclaim, and the
R&W stays with the lender no matter who touched the file. You can
rent the WRITE; you cannot rent away the AUDIT obligation. The
equilibrium: **rent or automate the production; own the controls.**
The ops organization shrinks into control design, sampling, and
exception handling.

**The irreducible internal core:**

1. **The credit decision as policy, and its exceptions.** Delegated
   underwriting authority is the franchise; the credit box, overlays,
   and exception judgment are the signature content plus the
   meta-tacit (§7) that keeps the R&W signable.
2. **Pricing, margin, and hedge decisions.** Balance-sheet skin —
   definitionally unrentable. The industry already splits this
   correctly: hedge *analytics* outsourced, hedge *decisions*
   in-house.
3. **The borrower and referral relationship.** The lender's
   proprietary N and its actual flywheel — and largely a trust/taste
   good (§6) where assurance logic does not govern.
4. **Control design and vendor oversight.** The turtles bottom out
   here: regulators and GSEs hold the lender accountable for its
   vendors, so everything can be outsourced *except the oversight of
   the outsourcers*. Orchestrating the boundary network — choosing
   attestors, verifying their attestations, assembling them into a
   signable whole — is irreducible by construction: pushing it out
   just creates a new vendor needing the same oversight. The
   recursion terminates at whoever holds the liability.
5. **Compliance posture and officer signatures.** Monitoring tooling
   is rentable; the named individuals a regulator can reach are not.

Compressed: the post-AI IMB collapses to **relationships, risk
decisions with skin, the R&W signature and its control apparatus, and
orchestration of the boundary network**. The fulfillment middle
evaporates — not to in-place automation but into the boundary
network. This also instantiates the individual claim (§5) with a
concrete population: the mid-level fulfillment professional holds
neither signature nor boundary — the weakly defended position,
staffed by thousands.
