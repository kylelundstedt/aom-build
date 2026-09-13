# Knowledge Work and Publication Boundaries

**Status:** Essay — a theory of the era, not binding on IV architecture
or plans.

**Companion to:** `iv-business-model.md` (§1.1),
ADR 0007 (Intentional Publication Boundary)

The accounting-versus-manufacturing question in the business model doc
generalizes: any knowledge work in the AI era faces the same tension.
Externally you sell assurance — to an employer, to customers. 
Internally you automate your own work with agents without exposing
your tacit knowledge. This essay works out why that structure is
general, why it is stable, and what it costs to maintain.

## 1. The Janus-faced structure is universal

Strip IV away and the pattern is: every knowledge worker and firm in
the AI era becomes two-faced —

``` text
EXTERIOR: assurance        "I stand behind this artifact"
          (accounting)      signature, liability, reputation, recourse
------------- publication boundary -------------
INTERIOR: factory          "agents execute my codified methodology"
          (manufacturing)   prompts, skills, evals, routing, process
                            control
```

The accounting-versus-manufacturing "tension" is not a choice between
analogies. It is the structure of the thing itself: every knowledge
business now has a manufacturing inside and an accounting outside, and
the consequential design question is what sits between them.

## 2. The codification paradox

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

This is why the publication boundary matters beyond security. ADR
0007's invariant — *methodology stays home; semantics travel with the
artifact* — read generally, is the **resolution of the codification
paradox**: the boundary is what makes it safe to codify yourself. You
externalize tacit knowledge into the interior, run it at machine
speed, and publish only attested artifacts that carry meaning but not
method. The ADR's adversarial-review rule (can a consumer reconstruct
interior methodology from the published surface?) is precisely a leak
test on codified tacit knowledge.

## 3. History has run this experiment

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
accountability, ideally both. "Be good at execution" is not a
position.

## 4. Scarcity migrates to accountability

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
from a model vendor.** This is the deepest form of the business
model's first thesis claim, and it holds for an individual employee
exactly as for a firm: what you ultimately sell your employer is not
output (they can rent that) but your willingness to be the one
accountable for it.

## 5. The Coasean consequence: an economy of boundaries

Coase: firm boundaries sit where market transaction costs exceed
internal coordination costs. Agents collapse internal coordination
costs, so firms can shrink drastically. But market *trust* costs do
not collapse — they rise (§4). The equilibrium: **tiny human signing
cores, large agent interiors, and attested artifacts as the only
things crossing between entities.** Inter-firm relations become
exactly what `clientx-service` consuming `gse-lld@42` looks like —
published, versioned, evidenced surfaces. The economy trends toward a
DAG of publication boundaries, each firm an interior. IV is not
adopting an unusual architecture; it is arriving early at the general
form.

The intra-firm version is contested ground. An employee who quietly
automates their own job is running an unlicensed publication boundary
inside their employer — selling attested outputs upward while keeping
the factory hidden. Employers will respond as they always have, with
IP-assignment claims over methodology. "Whose factory is it" becomes a
central labor conflict of the era. IV dodges this by construction: the
accountable humans own the firm that owns the factory.

## 6. The failure mode: losing the meta-tacit

Codifying tacit knowledge does not drain the tacit pool — it moves it
up a level. What must remain tacit in the signer: knowing when the
methodology is wrong, smelling the exception the controls missed,
judging what to codify next. Call it **meta-tacit knowledge**. The
signature is only worth buying because the signer retains it; a signer
who can no longer detect factory failure is performing accountability
theater with extra steps — the Clayton failure
(`iv-business-model.md` §3.1), individualized.

The sustainability condition for any assurance-over-factory business:
**the signing humans must stay in enough contact with the work to keep
their exception-detection alive.** Skill atrophy is not an HR concern;
it is depreciation of the firm's core asset. For IV this argues for
humans periodically re-performing audits by hand — not because agents
cannot, but to keep the signature real.

## 7. Compressed

AI forces knowledge workers to codify their tacit knowledge (to get
leverage) at the exact moment codification becomes maximally dangerous
(anything explicit is copyable). The publication boundary is the
general resolution: factory inside, signature outside, methodology
never crossing. Scarcity migrates to accountability because
skin-in-the-game is the one unrentable input. The economy reorganizes
into a DAG of such boundaries — and the residual human asset is
meta-tacit judgment, which must be actively maintained or the
signature hollows.
