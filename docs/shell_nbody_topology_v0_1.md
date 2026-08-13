# Shell N-body topology v0.1

Status: **candidate formalism; implemented diagnostics; not canon**.

The comparison object is an electronic shell/subshell, not an atom. Nuclei remain explicit attractive Coulomb centres; atomic and molecular states are compositions of shell dynamics around one or more such centres.

## Control physics
In atomic units, the baseline is
`H = sum_i p_i^2/2 - sum_iA Z_A/|r_i-R_A| + sum_i<j 1/|r_i-r_j| + ...`.
The topology layer is diagnostic by default and does not add a new force.

## Dimensional boundary
For identical point particles in three spatial dimensions, fundamental exchange topology reduces to permutations (`S_N`). Ordinary braid-group topology is fundamental only for effective 2D or otherwise constrained motion. The implementation therefore separates 3D exchange parity from declared-plane winding diagnostics.

## Nuclear centres
A nucleus is a Coulomb attractive centre `A_Z=(Z,R)`. In conservative Hamiltonian dynamics it is not a dissipative attractor in the strict sense. Basin/attractor language is reserved for reduced SCF or relaxation maps.

## Shell duality
For angular momentum `l`, capacity is `C_l=2(2l+1)`. Occupation `k` has particle-hole partner `k*=C_l-k`; the self-dual half-filled point is `k=2l+1`. Thus `p1<->p5`, `p2<->p4`, `p3<->p3`; likewise `d5` and `f7` are self-dual.

## Candidate observables
For a declared oriented projection `P:R^3->C`:
`w_iA=(1/2pi) integral d arg P(r_i-R_A)` and `w_ij=(1/2pi) integral d arg P(r_i-r_j)`.
These are projection-dependent diagnostics, not unrestricted 3D knot invariants.

A declared shell-history coordinate `Phi[gamma]` may be transformed by `eta=1/(Phi-z*)`; `z*=1/2` remains a falsifiable model parameter until replacement-anchor and Möbius controls pass.

## Validation ladder
1. Recover standard SCF/CI controls.
2. Extract topology diagnostics without fitting spectroscopy.
3. Test `p^k <-> p^(6-k)` internally.
4. Test transfer `2p^k -> 3p^k`.
5. Only then compare frozen shell classes with knot/conformal families.

No atom-to-knot identification is admitted by this document.
