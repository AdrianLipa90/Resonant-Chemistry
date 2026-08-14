# Molecular-state relaxation v0.14A1 — partial 8/9 readout

Status: **PARTIAL EXECUTION EVIDENCE / 40 OF 45 FROZEN STARTS DURABLY RECOVERED / NO TOPOLOGY ADMISSION / NO HESSIAN**

Source workflow: `31795895258`, frozen head `db756f5aa8598a24004f056aeb09b18034a08e5b`.

This note is subordinate to `benchmarks/MOLECULAR_STATE_RELAXATION_READOUT_V0_14A1.json`. It reports only descriptive quantities explicitly allowed by that preregistered readout contract.

## Execution recovery

The original workflow was cancelled after the common backend/dimer gates and eight of nine formula jobs had completed. The following first-attempt formula receipts were recovered from GitHub Actions and persisted unchanged in the raw evidence pack:

- `NeF2`, `NeCl2`, `NeBr2`;
- `ArF2`, `ArCl2`;
- `KrF2`, `KrCl2`, `KrBr2`.

`ArBr2` is **MISSING_EXECUTION**, not a negative chemical result. The eight recovered receipts contain 40 frozen starts in total.

## Threshold-free descriptive observations

For every completed composition, the lowest successful *screening* electronic energy among the frozen starts belongs to one of the weak-complex seed families. This is not a ground-state statement because no Hessian/local-minimum admission has yet been performed.

| Formula | Successful starts | Activated successful | Weak linear successful | Weak T successful | Lowest successful screening seed |
|---|---:|---:|---:|---:|---|
| NeF2 | 4/5 | 2/3 | 1/1 | 1/1 | weak linear |
| NeCl2 | 2/5 | 0/3 | 1/1 | 1/1 | weak T |
| NeBr2 | 2/5 | 0/3 | 1/1 | 1/1 | weak T |
| ArF2 | 5/5 | 3/3 | 1/1 | 1/1 | weak linear |
| ArCl2 | 4/5 | 2/3 | 1/1 | 1/1 | weak linear |
| KrF2 | 5/5 | 3/3 | 1/1 | 1/1 | weak linear |
| KrCl2 | 4/5 | 2/3 | 1/1 | 1/1 | weak linear |
| KrBr2 | 3/5 | 1/3 | 1/1 | 1/1 | weak linear |

The successful symmetric activated KrF2 starts converge to the same stored-precision basin pattern with approximately `r(Kr-F)=1.883 Å`; their screening energy is about `9.288 kcal/mol` above the lowest successful weak-linear start under the same frozen B97M-V/VV10/def2-TZVPD screen. This is a competing-basin observation only.

NeCl2 and NeBr2 have no successful activated start among the three frozen activated seeds, while both weak seed families return converged final SCF receipts. This is an execution/convergence pattern only; it does not by itself assign van-der-Waals topology.

For the weak-complex successful starts, the final Y-Y distances stay close to the independently optimized ligand-dimer prepass values (`F2 ≈ 1.393 Å`, `Cl2 ≈ 1.985 Å`, `Br2 ≈ 2.284 Å`). No distance threshold or topology classifier is introduced from this observation.

## Preserved boundaries

v0.14A1 still forbids:

- assigning `3c4e` or `VDW` topology from these geometries alone;
- calling any returned stationary geometry a harmonic local minimum before a Hessian;
- calling the lowest screening energy a validated ground state;
- introducing a post-result energy or distance threshold;
- changing method, seeds, SCF policy, grid policy, or optimizer settings for a difficult formula;
- deleting failures or results that conflict with known chemistry;
- fitting a PhaseNav/TIR descriptor to these outputs.

The next scientific gate remains blocked until all nine formula receipts / 45 starts are durably persisted.
