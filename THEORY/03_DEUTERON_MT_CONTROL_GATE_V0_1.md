# Deuteron MT Control Gate v0.1

Status: `CONTROL_MODEL_REPRODUCTION_CANDIDATE`

Date: 2026-08-31

## 1. Purpose

This gate is the first executable two-nucleon calculation attached to `RC.NUCLEON_BOUNDARY`.

Its evidential class is

`CONTROL_MODEL_REPRODUCTION`.

The gate verifies the numerical and provenance path

```text
source-bound proton/neutron packet
-> fixed NN interaction provider
-> radial two-body Hamiltonian
-> bound-state solver
-> convergence audit
-> immutable validation receipt
```

The subsequent predictive nuclear gate uses an interaction whose evidential role is declared independently.

## 2. Source-bound nucleon packet

The proton/neutron packet is stored at

`data/nuclear/nucleon_packet_codata2022_pdg2025_v0_1.json`.

It carries the external empirical mass, charge, spin-parity and magnetic-moment coordinates together with source provenance.

For the current mass values,

\[
m_p c^2=938.27208943\ {\rm MeV},
\qquad
m_n c^2=939.56542194\ {\rm MeV}.
\]

The physical proton-neutron reduced mass is

\[
\mu_{pn}=\frac{m_pm_n}{m_p+m_n},
\]

and the corresponding kinetic coefficient is

\[
\frac{(\hbar c)^2}{2\mu_{pn}c^2}
\approx 41.47106\ {\rm MeV\,fm^2}.
\]

## 3. Control interaction

The provider

`MALFLIET_TJON_TRIPLET_CONTROL_V0_1`

uses

\[
V(r)=
\frac{V_A e^{-\mu_A r}+V_R e^{-\mu_R r}}{r}
\]

with the frozen parameter packet

\[
V_A=-626.885\ {\rm MeV\,fm},
\quad
\mu_A=1.55\ {\rm fm^{-1}},
\]

\[
V_R=1438.72\ {\rm MeV\,fm},
\quad
\mu_R=3.11\ {\rm fm^{-1}},
\]

and the benchmark kinetic convention

\[
\frac{\hbar^2}{m}=41.47\ {\rm MeV\,fm^2}.
\]

The literature benchmark carried by this provider is

\[
E_d=-2.2307\ {\rm MeV}.
\]

## 4. Solver

For the reduced S-wave radial state \(u(r)\),

\[
\left[
-\frac{\hbar^2}{m}\frac{d^2}{dr^2}
+V(r)
\right]u(r)=E\,u(r),
\]

with Dirichlet radial boundaries.

The production control grid is

\[
r_{\max}=30\ {\rm fm},
\qquad N=8000.
\]

The Hamiltonian is represented as a symmetric tridiagonal operator and solved with a deterministic lowest-eigenpair routine.

## 5. Gate conditions

The control gate requires:

1. one negative eigenvalue among the lowest five sampled levels;
2. the second sampled level above zero;
3. binding-energy residual below \(5\times10^{-4}\) MeV;
4. 4000-to-8000-point binding change below \(2\times10^{-4}\) MeV;
5. model single-nucleon-about-COM RMS residual below \(10^{-2}\) fm.

The radius metric in this gate is the coordinate-space metric of the declared central S-wave model. Electromagnetic charge-radius, magnetic and quadrupole observables enter the later structure gate with their required operators.

## 6. Promotion boundary

A successful receipt promotes the software/numerical path to

`CONTROL_MODEL_REPRODUCTION_PASS`.

The next nuclear frontier is

```text
predictive NN interaction or endogenous derived interaction
-> p+n bound-state calculation
-> independent observable packet
-> deuteron physical validation
```

The TIR-to-RC endogenous path continues to use the federation promotion gate

`ENDOGENOUS_NUCLEON_PACKET_DERIVATION_AND_VALIDATION`.
