# Knot conformal <-> shell symmetry experiment v0.2

Status: **CANDIDATE / NON-CANON / CORRECTED COMPARISON LEVEL**

This note supersedes the interpretation layer of `knot_conformal_atom_symmetry_v0_1.md`. The v0.1 numerical knot sweep and its negative null result remain historical evidence; what changes here is the comparison object.

## Correction

The primary object is **not an atom label**. The candidate relation, if any, is between a frozen topological/conformal class and an electronic subshell occupation class `(n,l,k)` around explicit nuclear Coulomb centres.

Atom names may instantiate occupations (for example B has a `2p^1` valence occupation), but element names do not define particle-hole pairs.

## Intrinsic shell involution

For angular momentum `l`:

`C_l = 2(2l+1)`

`k* = C_l - k`

The self-dual half-filled point is `k=2l+1`.

Thus:

- `p^1 <-> p^5`, `p^2 <-> p^4`, `p^3 <-> p^3`;
- `d^k <-> d^(10-k)` with `d^5` self-dual;
- `f^k <-> f^(14-k)` with `f^7` self-dual.

The first transfer gate is to hold `(l,k)` fixed while changing principal shell number, e.g. `2p^k -> 3p^k`. This is a symmetry-class test only; radial wavefunctions and energies are not assumed equal.

## Knot-side state

The v0.1 conformal construction remains exploratory:

`Phi_K(theta)=V_K(exp(i theta))`

`eta_K(theta)=1/(Phi_K(theta)-z_*)`

with `z_*=1/2` as a falsifiable anchor. The numerical candidate family found in the first sweep was

`4_1, 6_3, 8_3, 8_9, 8_12, 8_17, 8_18`.

Exact unit-circle membership of roots of `V_K(q)-1/2` remains a symbolic gate.

## Negative control retained

The direct knot-gap versus atom-gap comparison did not beat the random-gap null test. The closest first comparison had empirical null probability about 0.36. That interpretation remains **NOT PROMOTED** and is not rescued by relabelling atoms.

## Correct next gate

1. Freeze shell-only descriptors before looking at knot labels.
2. Test `p^k <-> p^(6-k)` from control shell calculations.
3. Test `2p^k -> 3p^k` transfer.
4. Freeze knot mirror/amphichirality metadata and normalization.
5. Pre-register a symmetry-class comparison.
6. Run permutation, replacement-anchor and look-elsewhere controls.
7. Retain failure without retuning `z_*` or changing the selected knot family.

No physical knot-shell law is claimed by this note.
