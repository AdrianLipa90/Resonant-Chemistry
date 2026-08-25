# Resonant Chemistry v0.15 — Polyhedral Eclipse Spectroscopy

## State

**IMPLEMENTED FEATURE LAYER / PNCS SEMANTIC-MASS BRIDGE IMPLEMENTED / ATOM-T36 BINDINGS OPEN / BLIND SPECTRAL COMPARISON PENDING**

## Objective

v0.15 constructs a calculation path from an atomic semantic card, an explicit PNCS v0.19 semantic-mass binding, orbital angular structure, polyhedral cone occupancy, and the existing radial nuclear-exposure control to frozen model-side spectral features.

The execution path is:

```text
atomic semantic card
  -> explicit PNCS v0.19 T36 binding
  -> semantic mass M_s
  -> nucleon normalization A
  -> orbital angular density
  -> polyhedral cone partition
  -> cone probabilities p_a
  -> solid-angle reference q_a
  -> polyhedral information D_KL(p || q)
  -> radial nuclear exposure chi_r
  -> phase eclipse trace
  -> harmonic spectrum
  -> frozen blind-transition feature record
  -> later spectral comparison
```

## Existing control substrate

The atomic cards already provide `Z`, `N`, `A`, electron configuration, solver provenance, and the canonical information constant

\[
\kappa = \frac{\ln 2}{24\pi}.
\]

The existing period-2 spectroscopy module supplies a radial B--Ne control state and the central-field spin-orbit quantity

\[
\zeta_{2p}=\frac{\alpha^2}{2}\chi_r,
\]

with

\[
\chi_r=\int \rho_{2p}(r)\frac{Z-Q_{\mathrm{enc}}(r)}{r^3}\,dr.
\]

v0.15 exposes the equivalent radial control quantity as

```text
RESCHEM_PERIOD2_P_RADIAL_EXPOSURE_CONTROL_V0_15
```

and keeps it provenance-linked to `reschem.atomic_radial_spectroscopy`.

## PNCS semantic-mass binding

The semantic-mass bridge mirrors PNCS v0.19 exactly:

\[
m_k=\kappa(1+\alpha_M k)+\frac{2}{7}R_k,
\]

where

\[
R_k=\frac{1}{36}\sqrt{\left(\sum_i\sin\phi_i\right)^2+\left(\sum_i\cos\phi_i\right)^2}.
\]

Frozen constants and provenance:

```text
mass_contract_id: PNV_SEMANTIC_MASS_V1
PNCS reference commit: 5b866572f842407302acbb742df8a3955a0b8325
PNCS reference path: src/phasenav_natural_code/mass_v19.py
runtime source SHA-256: 0b4df86cd01db313ea46ebac0eceee9cf6df0673391edd1a3fb2667c30464a32
epistemic operator: CHYBA
canon_allowed: false
```

An atomic binding requires all of:

```text
atom_card_id
phase_index >= 1
exact 36-component phase
realization_id
realization_binding_id
source PNCS mass_binding_id
```

`phase_index` is always explicit. Atom identity, `Z`, isotope mass number, filename, and content ID are not used as hidden index derivation rules.

A verified binding generates a nondestructive semantic-card overlay at:

```text
tir.semantic_axes.values.semantic_mass
```

with the PhaseNav realization and mass-binding provenance retained.

## Polyhedral cone partition

For an orbital angular state

\[
\psi_l(\Omega)=\sum_{m=-l}^{l}c_mY_l^m(\Omega),
\]

the angular probability density is sampled deterministically on an equal-area Fibonacci sphere and assigned to spherical Voronoi cells defined by polyhedral axes.

The initial geometry ensemble is:

```text
tetrahedron: 4 vertex cones
octahedron: 6 vertex cones
cube: 8 vertex cones
icosahedron: 12 vertex cones
```

These geometries are Stage-A candidates. Their scores are generated before spectral observations are joined.

For cone `a`,

\[
p_a=\int_{C_a}|\psi_l(\Omega)|^2\,d\Omega,
\]

and the geometric reference is its solid-angle fraction

\[
q_a=\frac{\Omega_a}{4\pi}.
\]

## Orbital information relative to nucleons

The geometry-sensitive orbital information is

\[
I_{\mathrm{poly}}=D_{KL}(p\Vert q)
=\sum_a p_a\ln\frac{p_a}{q_a}.
\]

The v0.15 nucleon-normalized information ratio is

\[
\eta_A=\frac{I_{\mathrm{poly}}}{A\kappa}.
\]

The ordinary cone Shannon information

\[
H_C=-\sum_a p_a\ln p_a
\]

is retained in every receipt as a separate observable.

For an isotropic angular state, `p_a=q_a` and therefore

\[
I_{\mathrm{poly}}=0.
\]

This provides the spherical angular control inside the same implementation.

## Semantic mass per nucleon

For a provenance-bound semantic mass `M_s`,

\[
\mu_s=\frac{M_s}{A}.
\]

The Stage-A eclipse coupling is

\[
\mathcal E=\mu_s\,\eta_A\,\chi_r.
\]

Its components are always persisted separately so later tests can compare the combined scalar against each component and against the radial control.

## Phase eclipse trace

A model phase `phi` rotates the orbital angular density relative to a fixed polyhedral partition and observer direction. For the observer cone `o`, the normalized occupancy contrast is

\[
O(\phi)=\frac{p_o(\phi)}{q_o}-1.
\]

The discrete Fourier transform of one phase cycle yields a harmonic order and amplitude:

\[
O(\phi)\rightarrow \{A_n\},
\qquad
n_*=\arg\max_{n>0}|A_n|.
\]

v0.15 stores `n_*` and its amplitude. Conversion to hertz requires an independently supplied physical/model phase rate:

\[
\nu_{\mathrm{eclipse}}=\frac{n_*\Omega_{\mathrm{phase}}}{2\pi}.
\]

The phase-rate source must be provenance-bearing in the later mapping stage.

## Blind transition records

For initial and final orbital probes, v0.15 freezes:

```text
delta_polyhedral_information_nats
delta_orbital_information_ratio
delta_eclipse_coupling
initial_harmonic_order
final_harmonic_order
```

and writes

```text
observed_spectrum = WITHHELD_FOR_BLIND_COMPARISON
validation_status = PREDICTION_FEATURES_FROZEN
```

No observed wavelength, wavenumber, oscillator strength, or line intensity is accepted by the Stage-A feature builder.

## Validation stages

### Stage A — feature freeze

1. Bind selected atomic cards to exact PNCS v0.19 realizations.
2. Verify semantic mass exactly under the frozen PNCS contract.
3. Compute radial control exposure.
4. Compute all four polyhedral candidate feature sets.
5. Freeze transition-feature receipts and hashes.

Gate: **FEATURES_FROZEN_BEFORE_SPECTRAL_JOIN**.

### Stage B — mapping preregistration

Define one explicit map from frozen model features to spectral observables, including any global scale parameter, calibration subset, held-out subset, error metric, and null baselines.

Gate: **SPECTRAL_MAPPING_PREREGISTERED**.

### Stage C — spectral join

Join the preregistered experimental spectrum and evaluate the frozen map on held-out transitions/elements.

Gate statuses distinguish:

```text
MODEL_FEATURE_AVAILABLE
BLIND_PREDICTION_FROZEN
EXPERIMENTAL_COMPARISON_AVAILABLE
HELD_OUT_VALIDATION_PASS
HELD_OUT_VALIDATION_FAIL
```

## Initial element cohort

The first control cohort is the existing period-2 p-shell path:

```text
B-11
C-12
N-14
O-16
F-19
Ne-20
```

The cohort is selected from the already implemented B--Ne radial spectroscopy surface. Atom-to-T36 semantic-mass bindings remain a required input before Stage A can be closed.

## Model comparison contract

The Stage-A outputs preserve separate columns for:

```text
radial exposure only
semantic mass per nucleon only
polyhedral information only
semantic mass x polyhedral information
full eclipse coupling
harmonic order
harmonic strength
polyhedron identity
```

This permits the later validation to measure the incremental contribution of each layer.

## Scientific status

The v0.15 model may suggest a relation between polyhedral electron-cone information, nuclear exposure, semantic mass, and spectral structure, yet does not state that relation as an established result.

Current evidential state:

```text
polyhedral feature implementation: IMPLEMENTED
unit-test contract: IMPLEMENTED
PNCS v0.19 mass bridge: IMPLEMENTED
atom-to-T36 bindings: OPEN
blind spectral prediction ledger: PENDING BINDINGS
experimental spectral comparison: PENDING
```
