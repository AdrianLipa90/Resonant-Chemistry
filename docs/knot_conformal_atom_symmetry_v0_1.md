# Knot conformal ↔ atomic symmetry experiment v0.1

Status: **CANDIDATE / NON-CANON**

Branch: `knot-conformal-atom-symmetry-v0.1`

## Scope

This note records a controlled exploratory comparison between:

1. conformal/topological features derived from Jones-polynomial trajectories of prime knots;
2. independent atomic structure observables already present in Resonant-Chemistry.

No TIR correction is applied. No affective mapping is applied. No atom↔knot identity is asserted.

## Knot-side construction

For a knot K with Jones polynomial V_K(q), parameterize the unit circle by

`q = exp(i theta)`

and define

`Phi_K(theta) = V_K(exp(i theta))`

with the distinguished anchor

`z_* = 1/2`.

The conformal inversion is

`eta_K(theta) = 1 / (Phi_K(theta) - 1/2)`.

The diagnostic feature vector is

`Sigma_K = (crossing_number, Jones_breadth, |wind_{1/2}|, d_min, N_{1/2})`

where:

- `wind_{1/2}` is the winding number of `V_K(S^1)` around `1/2`;
- `d_min = min_theta |V_K(exp(i theta)) - 1/2|`;
- `N_{1/2}` counts roots of `V_K(q)-1/2` numerically lying on `|q|=1`.

The absolute winding is used for mirror-robust clustering; the signed winding is retained as provenance.

## Observed candidate family

The first sweep through prime knots up to eight crossings identified the following candidate `1/2`-singular family:

`4_1, 6_3, 8_3, 8_9, 8_12, 8_17, 8_18`.

In the current numerical experiment these knots have roots of `V_K(q)-1/2` on the unit circle within numerical tolerance, so the inverse trajectory develops poles on the parameter path.

This is a **numerical observation**, not an analytic theorem. Exact unit-circle membership should be checked symbolically before any promotion.

## Gap-spectrum test

For each singular knot, the angles of unit-circle roots were converted into cyclic normalized gaps. These were compared with normalized atomic multiplet level gaps.

The direct knot-gap ↔ atom-gap comparison did **not** survive a simple null test. In particular, the visually closest observed candidate (`8_18` against O in the first comparison) had an empirical null probability of roughly 0.36 under random four-gap partitions.

Therefore:

**Direct spectral matching is rejected as a promoted interpretation.**

The result is retained as a negative control.

## Atomic-side construction

The atomic feature vector is constructed independently from existing Resonant-Chemistry control outputs only:

`Sigma_A = (period, n_valence, n_p, S, |E_HF|/Z^2, log(|virial_residual|+eps), log(1+zeta), N_levels)`.

No knot feature is used to define `Sigma_A`.

The blind H→Ne checkpoint remains the control baseline. Period-2 atom-specific spectroscopy provides F^k, central-field spin-orbit zeta, LS/J labels and level structures for B→Ne.

## Current interpretation

The experiment does **not** support `knot = atom` or a direct atom-number mapping.

The more natural next question is structural symmetry:

`knot amphichirality / conformal symmetry ↔ electron-hole symmetry of an open shell`.

For the p shell this means comparing the intrinsic pairs

- `p^1 ↔ p^5`  (B ↔ F)
- `p^2 ↔ p^4`  (C ↔ O)
- `p^3 ↔ p^3`  (N self-dual half-filled shell)

without fitting labels or permuting atoms after seeing the result.

## Next gate

1. Symbolically verify `V_K(q)=1/2` unit-circle roots for the candidate singular family.
2. Add mirror/amphichirality metadata from a canonical knot table.
3. Define a shell electron-hole involution that uses only atomic occupation and term structure.
4. Compare symmetry-class invariants, not raw gap spectra.
5. Run permutation/null controls before interpreting any association.

Promotion rule: **no physical claim unless the relation survives controls and is independent of label fitting.**
