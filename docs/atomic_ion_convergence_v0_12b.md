# Global atomic-ion L3 continuation v0.12B

## Why v0.12B is an extension, not a threshold

v0.12A completed a common L0/L1/L2 numerical scan for all twelve atomic
neutral/ion states used by the closed-shell activation control.

The ordinary neutral/cation states and Cl/Cl- showed progressively smaller
adjacent energy drift, but F- and Br- changed numerical branch only at the
terminal L2 level:

- F-: L0/L1 had very large virial residuals; L2 became SCF-converged with a
  small virial residual and a qualitatively different energy;
- Br-: L0/L1 did not converge; L2 converged with a much smaller virial residual.

Therefore selecting a convergence tolerance immediately after v0.12A would be
underdetermined for the two states that entered their viable branch only at the
last available point.

v0.12B adds one globally identical L3 point before any admission rule is
considered.

## Frozen L3

The continuation follows the arithmetic pattern already used by L0/L1/L2:

- basis size: `32` (`+4`);
- grid points: `2200` (`+400`);
- `zeta_min=0.0025` (halved again);
- `r_max=300 bohr` (`+60 bohr`);
- damping `0.06`;
- DIIS start `12`, history `8`;
- maximum iterations `1500`;
- energy tolerance `1e-6 hartree`.

Exactly the same L3 is run for:

`Ne`, `Ne+`, `Ar`, `Ar+`, `Kr`, `Kr+`, `F`, `F-`, `Cl`, `Cl-`, `Br`, `Br-`.

## Readout

For every state v0.12B records:

- L3 energy;
- SCF convergence and iterations;
- virial residual;
- exact numerical parameters;
- `E(L3)-E(L2)` using the durable v0.12A execution receipt.

It also recomputes at matched numerical level:

- `E(X+)-E(X)` for Ne/Ar/Kr;
- `E(Y)-E(Y-)` for F/Cl/Br;
- the L3-minus-L2 drift of those finite differences.

## Still no numerical PASS rule

v0.12B does **not** say that L3 is converged because it is larger than L2.
It likewise defines no accepted drift epsilon.

The purpose is narrower: check whether the F-/Br- L2 branch persists under a
further globally enlarged numerical space and whether the matched finite
-difference trajectories begin to stabilize rather than undergoing another
qualitative transition.

Only after the complete L3 matrix exists may a separate global numerical
admission criterion be proposed.

## Epistemic status

`PREREGISTERED_GLOBAL_CONTINUATION / SAME_LEVEL_FOR_ALL_STATES /
NO_CONVERGENCE_THRESHOLD / NO_CHEMISTRY_CLASSIFIER / EXECUTION_RECEIPT_DEPENDENT`
