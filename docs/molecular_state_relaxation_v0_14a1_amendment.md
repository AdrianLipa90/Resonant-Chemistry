# Molecular-state relaxation v0.14A1 — numerical grid amendment

## Status

`POST_BACKEND_SMOKE / PRE_SCREENING_OUTPUT / GLOBAL_NUMERICAL_AMENDMENT`

This document does **not** replace the original v0.14A preregistration. The
original file remains at `benchmarks/MOLECULAR_STATE_RELAXATION_PREREG_V0_14A.json`.
The amendment receipt is
`benchmarks/MOLECULAR_STATE_RELAXATION_AMENDMENT_V0_14A1.json`.

## Why an amendment was required

The first durable backend smoke used the exact pinned PySCF 2.14.0 and
geomeTRIC 1.1.1 environment. F2 completed the B97M-V/VV10/def2-TZVPD SCF and
analytic-gradient smoke, but KrF2 failed while building the VV10/NLC numerical
grid. The exception was:

`IndexError: index 36 is out of bounds for axis 0 with size 19`

The traceback terminates in `pyscf.dft.gen_grid.sg1_prune` at `radii[nuc]`.
Thus no KrF2 SCF energy had been produced at the failure point.

## Amendment

The preregistered grid sizes are unchanged:

- primary DFT atom grid: `(99, 590)`;
- VV10/NLC atom grid: `(50, 194)`.

The pruning policy is amended globally to PySCF `nwchem_prune` on **both**
grids. PySCF documents `nwchem_prune` as the default `Grids.prune` option and
lists it together with SG-1 and Treutler pruning. The change applies identically
to every F/Cl/Br dimer and every Ne/Ar/Kr × F/Cl/Br XY2 seed.

No element-specific branch exists.

## What was known before the amendment

Only backend-smoke information was available:

- F2 energy/gradient smoke: PASS;
- KrF2: grid-construction exception before an SCF energy;
- optimized ligand dimers: none;
- completed XY2 relaxation results: none;
- within-formula energy rankings: none;
- topology labels inferred from v0.14A: none.

Therefore this is explicitly recorded as a **post-smoke, pre-screening-output**
numerical amendment, not silently treated as part of the original preregistered
method.

## Unchanged scientific policy

B97M-V, VV10, def2-TZVPD, charge/spin, SCF tolerances, optimizer settings, all
seed geometries/scales, no-rescue behavior, and the no-Hessian/no-topology
nonclaims remain unchanged.

## Admission rule

The amended backend must pass the same F2 + KrF2 energy/gradient smoke before
ligand-dimer prepass and the 45 XY2 relaxations are interpreted. A later failure
is preserved as a result; no candidate-specific rescue is permitted.

## Technical provenance

See bibliography key `pyscf_dft_grid_docs_2026` and the existing PySCF program
reference `sun_et_al_2020_pyscf`.

## Subsequent execution state — provenance update, not amendment rewrite

The historical status above remains unchanged: the amendment itself was made
before screening output existed. Later execution has now established the
following downstream state without changing the amendment:

- amended F2 + KrF2 structured backend smoke: **PASS**, durably recorded in
  `benchmarks/MOLECULAR_BACKEND_SMOKE_V0_14A1_EXECUTION.json`;
- common F2/Cl2/Br2 ligand-dimer prepass: recorded in
  `benchmarks/MOLECULAR_DIMER_PREPASS_V0_14A1_EXECUTION.json`;
- eight of nine XY2 formula receipts recovered from the first full workflow;
- 40 of 45 frozen starts have durable first-attempt evidence;
- `ArBr2` remains `MISSING_EXECUTION`;
- no Hessian/local-minimum admission or topology verdict has been performed.

This follow-up does not retroactively alter what was known when A1 was frozen.
For the constrained partial interpretation, see
`docs/molecular_state_relaxation_v0_14a1_partial_readout.md`.
