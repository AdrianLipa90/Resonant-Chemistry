# Molecular-state relaxation screen v0.14A

## Purpose

v0.13 changed the compound representation from one structural prediction per
composition to an **unranked ensemble of competing relational states**.  v0.14A
is the first common conventional molecular calculation that consumes that
ensemble.

It is intentionally a relaxation screen rather than a final physical admission
gate.  No Hessian is run and no geometry is automatically labelled as 3c4e or
van der Waals.

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

The corresponding method/software sources were added in the same development
iteration to `monograph/bibliography/molecular_screening.bib` and wired into the
working textbook.

## Common ligand-dimer prepass

F2, Cl2 and Br2 are first relaxed under the same frozen method, all from the
same numerical starting distance `2.0 angstrom`.

The optimized `r_YY` is used only as a **method-internal seed scale** for the
subsequent XY2 searches.  It is not an experimental bond length and does not fit
known noble-gas chemistry.

If a ligand dimer prepass is unavailable, all XY2 jobs that depend on that
dimer are withheld rather than rescued with an external bond length.

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

## Total work

- 3 common ligand-dimer relaxations;
- 9 XY2 formulae;
- 5 starts per formula;
- 45 XY2 relaxations total.

All formula jobs use the same electronic-structure and optimizer policy.

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

Scientific seed failure is a result record.  No candidate-specific rescue is
allowed.

## What v0.14A does not decide

v0.14A does **not** establish:

- harmonic local-minimum status;
- a validated ground state;
- 3c4e versus VDW electronic topology from geometry alone;
- a high-level molecular dissociation energy;
- replacement of the v0.8 r2SCAN-3c plus DLPNO-CCSD(T1) admission policy.

A later Hessian gate must be frozen separately after v0.14A if the relaxation
screen is executable and produces candidate stationary geometries.

## Backend smoke contract

Before the dimer prepass, the exact frozen backend must demonstrate finite,
converged B97M-V/VV10/def2-TZVPD energies and analytic gradients for F2 and
KrF2.  This is a software/method-compatibility gate, not chemical validation.

The first structured-smoke implementation exposed a reporting-only JSON
serialization bug: Python module objects were inserted directly into the
provenance record.  The doorway was corrected by serializing compact
module/version summaries.  **No method, basis, grid, SCF, optimizer, or seed
parameter was changed.**

Backend status remains dependent on a fresh structured-smoke receipt produced
from the corrected doorway.

## Epistemic status

`PREREGISTERED_CONVENTIONAL_RELAXATION_SCREEN / METHOD_FROZEN /
BACKEND_COMPATIBILITY_RECEIPT_PENDING_FOR_CURRENT_DOORWAY /
NO_HESSIAN_ADMISSION / NO_TOPOLOGY_LABEL / CANON_NOT_PROMOTED`
