# Nucleon Boundary v0.1

Status: `SOURCE_BOUND_EFFECTIVE_INPUT_CONTRACT / NUCLEAR_ENTRY_GATE / FEDERATION_CANDIDATE`

Date: 2026-08-31

## 1. Purpose

This contract defines the first explicit boundary between the fundamental-physics repositories and the nuclear sector used by Resonant Chemistry.

The boundary admits the proton and neutron as source-bound low-energy nucleon states and fixes the information that must be carried into any two-nucleon or many-nucleon calculation.

The intended dependency order is

```text
fundamental-physics source surfaces
-> nucleon boundary
-> two-nucleon sector
-> bound nuclei
-> atomic nuclear carrier (Z,N)
-> electronic atom
-> chemistry
```

The boundary is therefore the parent of nuclear binding calculations and the upstream nuclear carrier of `THEORY/02_ATOM_FORMALISM.md`.

## 2. Typed nucleon state

Let

\[
\mathcal N=\{p,n\}.
\]

A nucleon input packet is

\[
\boxed{
\mathfrak N_a=
(a;m_a,q_a,J_a^{P_a},\mu_a,\mathcal F_a,\Pi_a)
},
\qquad a\in\mathcal N,
\]

where:

- `a` is the nucleon species identifier;
- `m_a` is the source-bound rest mass;
- `q_a` is electric charge;
- `J_a^{P_a}` is spin-parity;
- `mu_a` is the magnetic moment coordinate used by magnetic observables;
- `F_a` is the declared form-factor/probe packet when finite-size observables require it;
- `Pi_a` is immutable provenance identifying the admitted external or derived source of the packet.

Every numerical field used by a nuclear solver must resolve to a declared provenance record.

## 3. One-nucleon state space

The low-energy one-nucleon carrier is typed by

\[
\mathcal H_N
=
L^2(\mathbb R^3)
\otimes \mathbb C^2_{\rm spin}
\otimes \mathbb C^2_{\rm iso},
\]

with the proton/neutron species represented on the isospin carrier by the admitted convention of the consuming calculation.

A one-nucleon state therefore carries

\[
|\mathbf p,s,\tau\rangle,
\]

with momentum `p`, spin coordinate `s`, and nucleon-species/isospin coordinate `tau`.

## 4. Two-nucleon entry surface

The first nuclear calculation consumes

\[
\mathcal H_{NN}
=
\mathcal A\left(\mathcal H_N\otimes\mathcal H_N\right),
\]

where `A` is the fermionic antisymmetrization operator in the chosen particle/isospin representation.

The Hamiltonian interface is

\[
\boxed{
H_{NN}=T_{\rm rel}+V_{NN}+H_{\rm corr}
}
\]

with:

- `T_rel` fixed by the source-bound nucleon masses and the declared kinematic convention;
- `V_NN` supplied by one explicitly named interaction provider or by a later source-owned TIR/RFC derivation;
- `H_corr` containing only corrections whose provenance and order are declared independently.

Every parameter at this boundary belongs to the interaction model, correction order, or source-bound nucleon packet and retains the same value across every nucleus within its declared domain.

## 5. Channel decomposition

The two-nucleon solver must expose the channel labels

\[
(S,T,L,J,P),
\]

so that proton-neutron, proton-proton and neutron-neutron sectors share one typed Hamiltonian surface and one provenance discipline.

For the first bound-state gate, the target channel is the deuteron sector with

\[
J^P=1^+,
\qquad T=0,
\]

including the coupled partial-wave structure required by the admitted interaction model.

## 6. First nuclear validation target

The first production-facing nuclear gate is

\[
\boxed{p+n\rightarrow{}^2\mathrm H}.
\]

The minimum observable packet is

\[
\mathcal O_d=
\{B_d,r_d,J^P,\mu_d,Q_d\},
\]

where the binding energy `B_d` is the mandatory primary observable and the remaining entries provide independent structural checks.

A deuteron run must record:

1. exact nucleon-input provenance;
2. exact interaction-provider identity and version/digest;
3. solver and numerical-resolution settings;
4. channel content;
5. predicted observables;
6. reference observable sources;
7. residuals and gate result.

## 7. Atomic handoff

For a nucleus with proton number `Z` and neutron number `N`, the nuclear layer exports the carrier

\[
\boxed{\mathfrak C_A=(Z,N;M_A,J_A^{P_A},\mu_A,Q_A,\Pi_A)}.
\]

`THEORY/02_ATOM_FORMALISM.md` consumes `Z`, `N`, charge state and the nuclear observables required by the chosen atomic approximation.

This establishes the explicit dependency

```text
NUCLEON_BOUNDARY
-> NUCLEAR_BINDING
-> NUCLEAR_CARRIER(Z,N)
-> ATOM_FORMALISM
```

and replaces the previous implicit jump from nuclear labels `(Z,N)` into the atomic model with an explicit nuclear carrier.

## 8. Fundamental-physics handoff

The boundary accepts two provenance classes:

- `EXTERNAL_EMPIRICAL`: nucleon quantities are bound to an admitted external reference dataset;
- `ENDOGENOUS_DERIVED`: a fundamental repository exports the same typed quantity with derivation provenance and a successful promotion gate.

The downstream nuclear solver consumes the same interface in both cases. Replacement of an external anchor by a later TIR/RFC/QCD-derived value is therefore an explicit source substitution under the same typed solver contract.

## 9. Federation contract

FPDG may federate the claim

`RC.NUCLEON_BOUNDARY`

with source authority retained by Resonant Chemistry.

The initial federation state is

`SOURCE_BOUND_EFFECTIVE_INPUT_CONTRACT`.

Promotion to a stronger evidential state requires a source-owned validation receipt for the numerical nucleon packet and the first two-nucleon gate.

## 10. Immediate next gate

After federation freshness is green, the next executable physics task is:

```text
freeze proton/neutron input packet
-> select one controlled NN interaction provider
-> solve deuteron bound state
-> validate B_d first
-> validate radius / magnetic / quadrupole structure
-> only then open A=3
```
