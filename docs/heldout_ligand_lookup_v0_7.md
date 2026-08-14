# Held-out ligand-family lookup v0.7 — partial result

## Preregistration

The candidate panel was frozen in commit
`ba8cee858f8d17945a8e8069990ff1e59c4d5213` before label lookup in this
execution.  PCl5 was marked preknown and excluded from scoring.

## What worked

Primary literature provides clear positive evidence for several frozen entries:

- **PBr5** — X-ray crystal structure; the solid is ionic `[PBr4]+ Br-` rather
  than a simple neutral trigonal-bipyramidal molecule. DOI `10.1038/145971a0`.
- **AsCl5** — primary literature establishes arsenic pentachloride; DOI
  `10.1021/ja02025a008`.
- **SCl4** — reported but thermally unstable and reproducibility-sensitive;
  later experimental work explicitly notes inability to reproduce the reported
  synthesis (DOI `10.1021/ic802320s`).  Independent 2026 electrochemical work
  supports reversible S/SCl4 chemistry in situ (DOI
  `10.1038/s41586-025-09867-2`).
- **SeCl4** — modern charge-density/crystal work confirms SeCl4 stoichiometry
  with ionic/tetrameric organization, DOI `10.1107/S2053229624010428`.
- **SeBr4** — primary spectrophotometric work directly studies selenium
  tetrabromide and its dissociation, DOI `10.1021/ja01594a025`.

All five resolved non-preknown positives are allowed by both M0 and M1, so the
resolved subset gives `5/5` for both and `Delta accuracy = 0`.

## What failed

The intended negative class could not be established by the lookup protocol.
A search that fails to find a primary report is not evidence that a species is
chemically impossible.  For example, DOI `10.1021/ic802320s` says SBr4 was
synthetically inaccessible in that study, but that is not strong enough to
promote a global `FALSE` label.

Therefore unresolved candidates remain unresolved.  They are not silently
converted to negatives.

## Methodological verdict

**Existence lookup is a poor target for M0-vs-M1 discrimination.**  Positive
reports are straightforward to verify, while rigorous negative labels require
a different evidence standard.

The next comparison should use one common computable observable for every
frozen candidate, for example:

1. energy against a preregistered decomposition channel;
2. optimized stationary-point existence plus harmonic stability;
3. relative energy to the lowest decomposition products.

The electronic-structure method, basis/ECP policy, spin policy and geometry
protocol must be identical across the whole panel.  No candidate-specific
fitting or rescue branches are allowed.

## Epistemic status

`PANEL PREREGISTERED / LOOKUP PARTIAL / NONDISCRIMINATING / TARGET DESIGN FAILURE / PREDICTIONS RETAINED`
