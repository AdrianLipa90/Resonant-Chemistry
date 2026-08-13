# 03 — Shell N-body Topology

**Status:** candidate, non-canonical.

## Primitive object
The object is a subshell state `(n,l,k)` around one or more explicit nuclear Coulomb centres `A_A=(Z_A,R_A)`. Atom-level labels are derived compositions and are not the primary topological objects.

## Hamiltonian control
`H = sum_i p_i^2/2 - sum_iA Z_A/|r_i-R_A| + sum_i<j 1/|r_i-r_j| + ...` in atomic units.

No topology term is added to the Hamiltonian at this stage.

## 3D / 2D topology boundary
For indistinguishable point particles in 3D the exchange class is a permutation class. Braid-group language is reserved for effective 2D or constrained sectors. Projected windings are retained only as explicitly projection-dependent observables.

## Particle-hole duality
`C_l=2(2l+1)`, `k*=C_l-k`, self-dual point `k=2l+1`.

- `p^1 <-> p^5`, `p^2 <-> p^4`, `p^3 <-> p^3`
- `d^k <-> d^(10-k)`, centre `d^5`
- `f^k <-> f^(14-k)`, centre `f^7`

## Relational diagnostics
For a declared oriented projection `P`, use electron-nucleus winding `w_iA` and pair winding `w_ij`. A separate exchange-permutation parity is retained for 3D. A declared complex shell-history coordinate may be mapped by `eta=1/(Phi-z*)`, with `z*=1/2` treated as a test parameter.

## Required falsification order
SCF/CI control -> shell-only particle-hole tests -> transfer across principal shell number `n` -> only then knot/conformal comparison.
