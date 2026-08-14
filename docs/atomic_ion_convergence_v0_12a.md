# Global atomic neutral/ion convergence scan v0.12A

## Why this gate exists

v0.11 attempted to construct finite-difference atomic controls from the first
stage of the existing robust HF ladder that passed a broad SCF/virial gate.
Two independent problems were exposed:

1. F- and Br- failed the atomic quality gate while their neutral atoms passed;
2. the first-passing neutral energies used by v0.11 were not numerically
   identical to the previously frozen neutral H--Kr checkpoints, with especially
   large differences for Br and Kr.

Therefore the current evidence does not support using first-passing robust-stage
energies as precision finite-difference descriptors.

v0.12A does **not** repair v0.11 and does not introduce a chemical score.  It
asks the more basic numerical question: what happens when every required
neutral/cation/anion state is run through the same explicit sequence of enlarged
radial numerical spaces without early acceptance?

## Frozen states

Exactly twelve states are scanned:

- Ne, Ne+;
- Ar, Ar+;
- Kr, Kr+;
- F, F-;
- Cl, Cl-;
- Br, Br-.

No state may receive a different numerical ladder.

## Frozen numerical ladder

### L0

- basis size: 20;
- grid points: 1000;
- `zeta_min=0.02`;
- `r_max=120 bohr`;
- damping 0.08;
- DIIS start 10, history 6;
- maximum 700 iterations.

### L1

- basis size: 24;
- grid points: 1400;
- `zeta_min=0.01`;
- `r_max=180 bohr`;
- damping 0.08;
- DIIS start 10, history 8;
- maximum 900 iterations.

### L2

- basis size: 28;
- grid points: 1800;
- `zeta_min=0.005`;
- `r_max=240 bohr`;
- damping 0.06;
- DIIS start 12, history 8;
- maximum 1200 iterations.

All levels use the same tolerance `1e-6 hartree`.

The lower `zeta_min` and larger radial box are applied globally, not only to
problematic anions.

## Recorded observables

For every state and every level the scan retains:

- electronic configuration;
- energy;
- whether the energy is finite;
- SCF convergence flag;
- iteration count;
- virial residual;
- exact basis/grid/radial parameters.

The only derived quantities are the raw adjacent energy differences

`E(L1)-E(L0)` and `E(L2)-E(L1)`

plus their absolute values.

## Deliberate absence of an admission threshold

v0.12A does **not** define a rule such as

`|E(L2)-E(L1)| < epsilon => converged`.

Choosing such an `epsilon` after viewing these trajectories would be a new
model-selection decision.  If a numerical admission rule is still useful after
v0.12A, it must be frozen separately as v0.12B and applied globally.

Likewise, a small energy drift cannot override an unconverged SCF or an
obviously pathological virial trajectory merely because the energy looks
smooth.

## CI semantics

The GitHub Actions matrix executes all twelve states independently.  A state
with `converged=false` still produces a valid scientific receipt; scientific
non-convergence is data, not an infrastructure failure.

The aggregate job fails only for missing/corrupt receipts or incomplete matrix
coverage.

## Epistemic status

`PREREGISTERED_GLOBAL_NUMERICAL_SCAN / EXECUTION_RECEIPT_DEPENDENT /
NO_CONVERGENCE_THRESHOLD / NO_CHEMICAL_CLASSIFIER / NO_RESCUE_OF_V0_11`
