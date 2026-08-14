# Energetic admission gate v0.8

## Purpose

The v0.7 existence lookup failed as a discriminating target because missing
literature cannot be treated as evidence of nonexistence. v0.8 therefore moves
the next comparison to one common calculable observable for every frozen
candidate.

This gate does **not** add a Resonant-Chemistry energy correction. It defines
how independent conventional electronic-structure results may admit or reject
a structural candidate while keeping v0.1-v0.7 frozen.

## Preregistered pair-loss target

For a higher-coordination candidate `XY_n`, the primary v0.8 decomposition
channel is

\[
XY_n \rightarrow XY_{n-2}+Y_2.
\]

The control quantity is

\[
\Delta E_{pair}
=E(XY_{n-2})+E(Y_2)-E(XY_n).
\]

Positive `Delta E_pair` means the parent lies below that specific pair-loss
channel under the frozen computational policy.

The channel is deliberately aligned with the `+2` coordination ladder, but the
energy is supplied entirely by conventional electronic-structure theory. No
TIR, PhaseNav, shell, topological, semantic, or affective term is added to the
Hamiltonian.

## Stationary-point contract

An energy difference alone is insufficient.

A positive energetic label requires:

1. one identical method policy for parent and products;
2. full optimization of all three species;
3. harmonic Hessian information;
4. zero imaginary frequencies for the parent;
5. zero imaginary frequencies for both preregistered products;
6. `Delta E_pair` above the frozen tolerance.

If the parent has an imaginary frequency it is rejected as a local minimum.
If a product is not a local minimum, the *specific preregistered channel* is
invalid rather than converted into a negative label for the parent. This
prevents a chemically unstable product from creating a false apparent
stabilization or destabilization.

Missing energies or Hessians remain `UNKNOWN`. Mixed method policies are
`INCOMPARABLE`.

## Why pair loss rather than existence lookup

High-level studies of sulfur fluorides show that sequential ligand-loss
energies vary strongly as the electronic structure reorganizes. Woon and
Dunning analyze the entire `SF_n` sequence with multireference CI and coupled
cluster theory and report the alternating sequential dissociation energies
used in the v0.6 null test (DOI `10.1021/jp901949b`).

Independent coupled-cluster thermochemistry for second-row compounds likewise
emphasizes that adiabatic bond dissociation energies contain reorganization of
the product and therefore can differ substantially from step to step (DOI
`10.1021/jp710373e`).

This is exactly why v0.8 freezes the decomposition channel and computational
policy before using the resulting energy as a label.

## Model comparison

- **M0**: parity-only admission.
- **M1**: parity plus the explicit shell gate (`principal_n >= 3`).
- **M2**: reserved shorthand for `M1 + independent conventional energetic
  admission`.

M2 is **not** a new Resonant-Chemistry Hamiltonian. It is an admission/control
layer. If conventional quantum chemistry rejects an M1 candidate, that is a
failure of the structural candidate, not evidence for fitting a new energy
term.

Primary score: balanced accuracy on resolved, non-motivating entries, provided
both positive and negative energetic labels occur. Accuracy and coverage are
secondary. Unknowns remain visible and are excluded from the denominator.

## Method-policy gate

The pair-loss channels and scoring rules are now frozen in
`benchmarks/ENERGETIC_ADMISSION_PREREG_V0_8.json`.

The exact electronic-structure backend/method/basis has **not** yet been
selected because the present execution environment contains no PySCF, Psi4,
ORCA, xTB, or NWChem runtime. No energy result may enter the v0.8 score until a
separate immutable method-policy amendment is committed.

That amendment must freeze, for the complete panel:

- method;
- basis;
- relativistic treatment;
- dispersion treatment;
- environment;
- geometry optimization policy;
- Hessian policy;
- energy kind (electronic vs ZPE-corrected etc.);
- charge and multiplicity policy.

The method policy must be fixed **before the first candidate-specific result is
inspected**.

## Software status

`reschem/energetic_admission.py` implements the backend-neutral ledger and
scorer. Local unit controls cover positive/negative pair loss, missing data,
Hessian failures, method-policy mismatch, tolerance handling, invalid product
channels, unknown exclusion, and balanced-accuracy scoring.

Local prototype: **11/11 tests PASS**.

This is not branch CI and not physical validation.

## Epistemic status

`PREREGISTERED CONTROL INTERFACE / SOFTWARE-TESTED LOCALLY / ENERGY DATA NOT YET RUN / CANON NOT PROMOTED`
