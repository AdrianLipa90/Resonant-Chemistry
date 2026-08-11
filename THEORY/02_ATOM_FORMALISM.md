# Atom Formalism v0.1

Status: **CANDIDATE FOUNDATION**  
Scope: atomic identity, electronic state space, control Hamiltonian, and the first TIR bridge.

## 1. Atomic identity — ESTABLISHED control layer

An atomic species is represented by

\[
\mathfrak A=(Z,N,q;\mathcal H_A,H_A,\rho_A),
\]

where `Z` is proton number, `N` neutron number, `q` the net charge in units of `e`, and

\[
A=Z+N,\qquad N_e=Z-q.
\]

**Invariant:** the chemical element is identified by `Z`. Resonant or relational descriptors may classify states of an element but do not replace atomic number.

For `N_e` electrons the electronic state space is antisymmetric:

\[
\mathcal H_A=\bigwedge^{N_e}\left[L^2(\mathbb R^3)\otimes\mathbb C^2\right].
\]

## 2. Hamiltonian control layer — ESTABLISHED

In the clamped-nucleus, non-relativistic electronic approximation and atomic units,

\[
H_A=\sum_i\left(-\frac12\nabla_i^2-\frac{Z}{r_i}\right)+\sum_{i<j}\frac1{r_{ij}}+H_{\rm corr}.
\]

`H_corr` is a named extension point for finite-nuclear-mass, relativistic, spin-orbit and QED corrections. ResChem does **not** replace this Hamiltonian by a resonance slogan.

## 3. One-electron benchmark — ESTABLISHED

For a hydrogen-like ion with one electron, the non-relativistic infinite-nuclear-mass spectrum is

\[
E_n=-R_\infty\frac{Z^2}{n^2},
\]

with `R_∞ hc = 13.605693122994 eV` used by the v0.1 solver. The characteristic Bohr radius scales as

\[
r_n\sim a_0\frac{n^2}{Z}.
\]

This is the first benchmark because it has a closed-form solution and therefore exposes implementation errors immediately.

## 4. TIR bridge — TIR-DEFINED / CANDIDATE

TIR treats ordered informational relations as primitive and uses holonomic link operators `W_ij` at the quark/color layer. Atomic chemistry must not copy the color `SU(3)` group onto electron bonding. Instead, the atomic layer reserves a state-space interface:

\[
\mathcal E_A\subset\mathcal H_A,
\]

which later permits a relation operator between active electronic subspaces,

\[
W_{AB}:\mathcal E_B\to\mathcal E_A.
\]

The precise chemistry-level group and construction of `W_AB` are **not assumed in the atom module**. They will be derived from orbital/subspace overlap in the bond milestone.

The TIR information quantum is recorded as

\[
\kappa=\frac{\ln 2}{24\pi}.
\]

At v0.1 `kappa` is metadata; it does not alter standard atomic energies.

## 5. Solver policy

v0.1 computes:

1. `Z,N,q,A,N_e` consistency;
2. element identity for `1 <= Z <= 36`;
3. ground-state baseline electron configurations through Kr, including neutral Cr/Cu exceptions;
4. exact non-relativistic hydrogenic energy/radius for one-electron species.

v0.1 deliberately does **not** claim ab-initio multi-electron energies. Hartree-Fock/DFT/CI are later solver layers.

## 6. Falsification / validation gates

- Hydrogen: `E_1 = -13.605693122994 eV` within numerical tolerance.
- He+: `E_1 = 4 E_H` under the same approximation.
- Electron counting: `N_e=Z-q` for neutral atoms and ions.
- Aufbau bookkeeping tests for H, He, C, Ne, Cr, Cu, Kr.
- Invalid negative particle counts must fail loudly.

No new relational quantity may be promoted merely because it correlates retrospectively with known chemistry.
