# Molecular-state relaxation screen v0.14A

## Purpose

v0.13 changed the compound representation from one structural prediction per
composition to an **unranked ensemble of competing relational states**. v0.14A
is the first common conventional molecular calculation that consumes that
ensemble.

It is intentionally a relaxation screen rather than a final physical admission
gate. No Hessian is run and no geometry is automatically labelled as 3c4e or
van der Waals.

The original preregistration is preserved in
`benchmarks/MOLECULAR_STATE_RELAXATION_PREREG_V0_14A.json`. The later numerical
amendment is preserved separately in
`benchmarks/MOLECULAR_STATE_RELAXATION_AMENDMENT_V0_14A1.json` and documented in
`docs/molecular_state_relaxation_v0_14a1_amendment.md`.

## Frozen conventional method

The screening policy was fixed before molecular relaxation results:

- PySCF `2.14.0`;
- geomeTRIC `1.1.1`;
- B97M-V (`b97m_v`) with VV10 nonlocal correlation;
- `def2-TZVPD` basis;
- neutral singlets, gas phase;
- no relativistic correction in this preliminary screen;
- SCF tolerance `1e-10 hartree`, maximum `200` cycles;
- common DFT and NLC grids;
- no SCF rescue branch.

The corresponding method/software sources are in
`monograph/bibliography/molecular_screening.bib` and are wired into the working
textbook.

## v0.14A1 numerical amendment

The first structured heavy-atom smoke exposed a PySCF SG-1 pruning limitation
while constructing the KrF2 VV10/NLC grid. The failure occurred before a KrF2
SCF energy was produced. The correction therefore remains recorded as a
**post-backend-smoke / pre-screening-output** amendment rather than being folded
silently into the original preregistration.

The grid sizes, functional, basis, charge/spin policy, SCF thresholds, optimizer,
and seeds were not changed. Only the pruning algorithm was changed globally:
regular and NLC grids now use PySCF `nwchem_prune` for every species. No
Kr-specific or element-specific branch exists.

The amended F2 + KrF2 energy/gradient backend smoke subsequently completed and
its durable execution receipt is stored in
`benchmarks/MOLECULAR_BACKEND_SMOKE_V0_14A1_EXECUTION.json`.

## Common ligand-dimer prepass

F2, Cl2 and Br2 are first relaxed under the same amended frozen method, all from
the same numerical starting distance `2.0 angstrom`.

The optimized `r_YY` is used only as a **method-internal seed scale** for the
subsequent XY2 searches. It is not an experimental bond length and does not fit
known noble-gas chemistry.

The durable prepass receipt is
`benchmarks/MOLECULAR_DIMER_PREPASS_V0_14A1_EXECUTION.json`. The persisted
same-method distances are approximately:

- F2: `1.393 Å`;
- Cl2: `1.985 Å`;
- Br2: `2.284 Å`.

These values are numerical seed controls, not new experimental claims.

## Five starts per XY2 composition

Every one of the nine closed-shell XY2 formulae receives the same five starts.

### Activated linear multi-start

Three symmetric `Y-X-Y` starts:

- `r_XY = 1.0 r_YY`;
- `r_XY = 1.3 r_YY`;
- `r_XY = 1.6 r_YY`.

All three belong to the v0.13 `ACTIVATED_LINEAR_3C4E` candidate family, but the
seed label is not a post-optimization topology verdict.

### Weak-complex end-on

One `X...Y-Y` start with the X-to-near-Y separation `1.8 r_YY`.

### Weak-complex T-shaped

One seed with X perpendicular to the Y-Y midpoint at `1.8 r_YY`.

The seed scale factors are numerical search parameters frozen before results;
they are not predicted intermolecular distances.

## Total frozen work

- 3 common ligand-dimer relaxations;
- 9 XY2 formulae;
- 5 starts per formula;
- 45 XY2 relaxations total.

All formula jobs use the same electronic-structure and optimizer policy.
Scientific seed failure is a result record. Candidate-specific rescue remains
forbidden.

## Recorded outputs

Each relaxation preserves:

- exact initial Cartesian geometry;
- initial SCF convergence and energy;
- returned final geometry if available;
- final SCF convergence and energy;
- final analytic gradient RMS and maximum component;
- X-Y1, X-Y2, Y-Y distances, Y-X-Y angle, and X-to-YY-midpoint distance;
- exact exception type/message if the calculation fails;
- Python/PySCF/geomeTRIC versions;
- wall time;
- within-formula relative electronic energy among successful starts.

## Current execution state

The original full workflow was cancelled after the common backend/dimer stages
and eight of nine formula jobs had completed. The first-attempt receipts for
those eight formulae were recovered and persisted in the repository without
rewriting their numerical content.

Durable current state:

- completed formulae: `NeF2`, `NeCl2`, `NeBr2`, `ArF2`, `ArCl2`, `KrF2`,
  `KrCl2`, `KrBr2`;
- completed starts: **40/45**;
- `ArBr2`: **MISSING_EXECUTION**;
- `ArBr2` is not labelled unstable/nonexistent/false;
- no missing result is imputed.

The machine-readable partial aggregate is
`benchmarks/MOLECULAR_STATE_RELAXATION_PARTIAL_READOUT_V0_14A1.json`; the
human-readable constrained interpretation is
`docs/molecular_state_relaxation_v0_14a1_partial_readout.md`.

A later GitHub matrix rerun repeated a broader scope than the intended missing
job. The provenance guard in
`benchmarks/MOLECULAR_STATE_RELAXATION_RERUN_SCOPE_V0_14A1.json` therefore keeps
the original first-attempt receipts as the v0.14A1 evidence for the eight
already-completed formulae. A future run may fill the missing ArBr2 slot but may
not silently replace those receipts in this checkpoint.

## Threshold-free partial observations

For every completed formula the lowest successful *screening* electronic energy
comes from a weak-complex seed family. This is not a validated ground-state
statement because harmonic local-minimum admission has not been performed.

The activated-start survival pattern is preserved separately in
`benchmarks/MOLECULAR_STATE_RELAXATION_ACTIVATED_SURVIVAL_MATRIX_V0_14A1_PARTIAL.json`.
Descriptive examples include:

- KrF2: 3/3 activated starts complete; the symmetric activated basin has
  `r(Kr-F) ~ 1.883 Å` and lies about `9.288 kcal/mol` above the lowest successful
  weak-linear screening state under the same method;
- ArF2: 3/3 activated starts complete, with an activated-to-lowest-weak screening
  gap of about `37.99 kcal/mol`;
- NeF2: 2/3 activated starts complete, with a corresponding gap of about
  `95.93 kcal/mol`;
- NeCl2 and NeBr2: 0/3 activated starts complete, while both weak seed families
  complete;
- ArCl2: 2/3 activated starts complete;
- KrCl2: 2/3;
- KrBr2: 1/3.

No fit, threshold, activation law, topology classifier, or post-result seed
policy is derived from this partial matrix.

## What v0.14A/A1 does not decide

v0.14A/A1 does **not** establish:

- harmonic local-minimum status;
- a validated ground state;
- 3c4e versus VDW electronic topology from geometry alone;
- a high-level molecular dissociation energy;
- replacement of the v0.8 r2SCAN-3c plus DLPNO-CCSD(T1) admission policy;
- completeness before ArBr2 is durably executed;
- a PhaseNav/TIR correction to conventional electronic energies.

## Next gate

The next permitted step is to complete the missing ArBr2 execution under the
same frozen A1 method/seed policy. Only after **9/9 formula receipts and 45/45
starts** are durably present may a separate Hessian/local-minimum protocol be
frozen as v0.14B.

A timeout, cancellation, optimizer failure, or SCF failure remains explicit
execution/scientific evidence and must not trigger candidate-specific rescue.

## Epistemic status

`PREREGISTERED_CONVENTIONAL_RELAXATION_SCREEN / A1_GLOBAL_NUMERICAL_AMENDMENT_RECORDED /
BACKEND_SMOKE_PASS / DIMER_PREPASS_RECORDED / PARTIAL_8_OF_9_FORMULAE /
40_OF_45_FROZEN_STARTS / ARBR2_MISSING_EXECUTION / NO_HESSIAN_ADMISSION /
NO_TOPOLOGY_LABEL / CANON_NOT_PROMOTED`
