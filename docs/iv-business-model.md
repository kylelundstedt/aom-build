# IV Business Model — AOM companion (doctrine moved)

**Status:** The full business model doc moved to the `iv-docs` repo on
2026-09-13 (`drafts/iv-business-model.md` there, iv-docs commit
`8543779`); it is firm-wide doctrine, not pilot material. Later
revisions happen there. The named-client worked example (CMG
subservicer oversight) moved to the `iv-cmg` repo
(`memos/cmg-servicervault-oversight-versioning.md`), generalized by
role in the iv-docs copy per that repo's content boundary.

This file retains only what is AOM-pilot-specific.

## One-line model (for reference)

IV is an assurance firm for data products: agents keep the books,
controls run the close, evidence fills the workpapers, and a human
signs the opinion. The publication boundary (ADR 0007) is
simultaneously the security perimeter, the trust product, the pricing
line, and the definition of the firm. Full argument — three-layer
product economics, demand side and the internalization objection,
graduated assurance, controls-based trust, workpaper standard, firm
structure, revenue — in iv-docs.

## What the freddie-sflld pilot tests, commercially

Read through the assurance-firm frame, the pilot
(`iv-agent-operating-model.md` §22) is not only an operations
experiment. It tests whether **one human can credibly *sign* — not
merely supervise — an agent-operated Dataset**:

- Can AUDIT produce evidence that makes a real human sign-off possible
  in bounded time (the workpaper/re-performance test)?
- Does "what is published right now, and how do you know?" resolve
  deterministically from WAP state (the close is real)?
- Does delegation traceability support the chain an external
  re-performer would need (Hermes → Kanban task → worker conversation
  → execution → Entire evidence → repo/Product state → WAP
  publication, `iv-agent-operating-model.md` §22.6)?
- Does the leverage ratio — Products credibly operated and signed per
  human hour — actually improve?

If yes, the business scales by adding Products to the DAG — and client
instances to families — not people to the org chart.

## Versioning mechanics tracked here

The family → product → instance hierarchy, release-identity tuple
(family/mapping versions, product, client instance, as-of, revision,
coverage level), versioned source→canonical mappings, and composite
comparability floor are tracked as **backlog C-016** for an eventual
ADR and schema support, blocked on the first proprietary-core client
engagement. The business rationale is iv-docs §2.1–2.2 and its
Appendix A; the named instance is the iv-cmg memo.
