# Resonant Chemistry v0.15 — Polyhedral Eclipse Spectroscopy

## State

**TIR TETRAHEDRAL SIC INFERENCE GEOMETRY IMPLEMENTED / STAGE-A0 GEOMETRY FREEZE IMPLEMENTED / PNCS v0.19 SEMANTIC-MASS BRIDGE IMPLEMENTED / ATOM-T36 BINDINGS OPEN / BLIND SPECTRAL COMPARISON PENDING**

## Objective

v0.15 constructs a provenance-bearing calculation path linking:

```text
atomic semantic card
  -> radial nuclear exposure
  -> orbital-band angular information
  -> TIR tetrahedral SIC inference coordinates
  -> nucleon normalization
  -> exact PNCS v0.19 semantic mass
  -> phase/harmonic observables
  -> frozen blind-transition features
  -> preregistered spectral comparison
```

The geometry and mass layers are frozen in separate steps so the exact PNCS semantic-mass binding enters after the mass-independent atomic geometry ledger has been generated.

## TIR tetrahedral inference geometry

The primary inference geometry is referenced directly to:

```text
repository: AdrianLipa90/Metatime-Relation_of_Information_Framework
commit: 7498d8c6349573f8d58895145342e849d36983c8
path: theory/metatime/foundational_formal_notes/hilbert_kahler_phase_hamiltonian/main.tex
```

The tetrahedral frame inside the Bloch sphere is

\[
\mathbf v_1=\frac{(1,1,1)}{\sqrt3},\quad
\mathbf v_2=\frac{(1,-1,-1)}{\sqrt3},\quad
\mathbf v_3=\frac{(-1,1,-1)}{\sqrt3},\quad
\mathbf v_4=\frac{(-1,-1,1)}{\sqrt3},
\]

with

\[
\mathbf v_i\cdot\mathbf v_j=
\begin{cases}
1,&i=j,\\
-1/3,&i\neq j.
\end{cases}
\]

For a Bloch-ball coordinate \(\mathbf n\), the inference-cone probabilities use the TIR qubit SIC map

\[
\boxed{p_j(\mathbf n)=\frac14\left(1+\mathbf n\cdot\mathbf v_j\right)},
\qquad
\sum_{j=1}^{4}p_j=1.
\]

The corresponding interference Gram matrix is

\[
G_{ij}=\frac{1+\mathbf v_i\cdot\mathbf v_j}{2},
\]

hence

\[
G_{ii}=1,
\qquad
G_{ij}=\frac13\quad(i\neq j).
\]

The implementation contract is

```text
RESCHEM_TIR_TETRAHEDRAL_SIC_INFERENCE_V0_15
```

and lives in `reschem/tetrahedral_inference_v015.py`.

## Period-2 subshell Bloch control

For the first B--Ne cohort, the existing atomic control solver supplies the 2p alpha/beta occupations. v0.15 reduces this shell-level spin population to

\[
P_{2p}=\frac{N_\alpha-N_\beta}{N_\alpha+N_\beta},
\qquad
\mathbf n_{2p}=(0,0,P_{2p}).
\]

The initial cohort therefore carries a deterministic shell-spin coordinate derived from the same atomic configuration machinery already used by Resonant Chemistry.

The reduction receipt is

```text
RESCHEM_PERIOD2_P_SPIN_BLOCH_CONTROL_V0_15
```

with provenance `reschem.atomic_hf_average.subshells_for_atom`.

## Tetrahedral inference information

For the SIC probabilities \(p_j\), v0.15 records the information relative to the central Bloch-ball reference \((1/4,1/4,1/4,1/4)\):

\[
I_{\rm SIC}
=
\sum_{j=1}^{4}p_j\ln(4p_j).
\]

The complete SIC probability vector remains in every receipt. The model therefore preserves both the scalar information and the directional distribution over the four inference sectors.

## Radial nuclear-exposure control

The existing period-2 spectroscopy module supplies the central-field spin-orbit quantity

\[
\zeta_{2p}=\frac{\alpha^2}{2}\chi_r,
\]

with

\[
\chi_r
=
\int \rho_{2p}(r)
\frac{Z-Q_{\rm enc}(r)}{r^3}
\,dr.
\]

v0.15 exposes this as

```text
RESCHEM_PERIOD2_P_RADIAL_EXPOSURE_CONTROL_V0_15
```

and retains the originating HF energy and virial residual in the control receipt.

## Spatial orbital-band channel

For an orbital angular state

\[
\psi_l(\Omega)=\sum_{m=-l}^{l}c_mY_l^m(\Omega),
\]

the spatial cloud is sampled deterministically on an equal-area Fibonacci sphere.

The first frozen real 2p basis is

```text
p_x
p_y
p_z
```

under contract

```text
RESCHEM_REAL_2P_BASIS_V0_15
```

The spatial tetrahedral projection is retained alongside octahedral, cubic, and icosahedral partition controls. These control partitions allow the later held-out comparison to measure the incremental value of the TIR tetrahedral choice while preserving the TIR SIC inference geometry as the primary internal inference layer.

For a spatial partition cell \(C_a\),

\[
p_a^{\rm orb}
=
\int_{C_a}|\psi_l(\Omega)|^2\,d\Omega,
\]

with solid-angle reference

\[
q_a=\frac{\Omega_a}{4\pi}.
\]

The geometry-sensitive orbital information is

\[
I_{\rm orb}
=
D_{KL}(p^{\rm orb}\Vert q)
=
\sum_a p_a^{\rm orb}
\ln\frac{p_a^{\rm orb}}{q_a}.
\]

The cone Shannon quantity

\[
H_{\rm orb}=-\sum_a p_a^{\rm orb}\ln p_a^{\rm orb}
\]

is preserved separately.

## Stage-A0 — mass-independent geometry freeze

`run_polyhedral_eclipse_stage_a0_v015.py` creates the mass-independent ledger before the PNCS semantic-mass join.

For every preregistered atom it freezes:

```text
Z
A
radial nuclear exposure chi_r
2p alpha/beta occupation
2p spin polarization
Bloch coordinate
TIR tetrahedral SIC probabilities
TIR SIC information
TIR inference-cone phase harmonic
p_x / p_y / p_z spatial features
spatial tetrahedral projection control
spatial octahedral control
spatial cubic control
spatial icosahedral control
per-feature SHA-256
per-atom SHA-256
ledger SHA-256
```

The state marker is

```text
GEOMETRY_FEATURES_FROZEN_BEFORE_SEMANTIC_MASS_AND_SPECTRAL_JOIN
```

The spectral field remains

```text
WITHHELD_FOR_BLIND_COMPARISON
```

throughout Stage-A0.

## PNCS v0.19 semantic-mass binding

The semantic-mass bridge mirrors the frozen PNCS v0.19 contract:

\[
\boxed{m_k=\kappa(1+\alpha_M k)+\frac{2}{7}R_k},
\]

where

\[
R_k
=
\frac1{36}
\sqrt{
\left(\sum_i\sin\phi_i\right)^2
+
\left(\sum_i\cos\phi_i\right)^2
}.
\]

Frozen provenance:

```text
mass_contract_id: PNV_SEMANTIC_MASS_V1
PNCS reference commit: 5b866572f842407302acbb742df8a3955a0b8325
PNCS reference path: src/phasenav_natural_code/mass_v19.py
runtime source SHA-256: 0b4df86cd01db313ea46ebac0eceee9cf6df0673391edd1a3fb2667c30464a32
epistemic operator: CHYBA
canon_allowed: false
```

Every atomic binding carries explicitly:

```text
atom_card_id
phase_index >= 1
exact 36-component phase realization
realization_id
realization_binding_id
source PNCS mass_binding_id
```

The explicit binding is the sole Stage-A1 source of `phase_index` and T36 for semantic-mass evaluation.

A verified binding produces a nondestructive atomic semantic-card overlay at

```text
tir.semantic_axes.values.semantic_mass
```

with realization and mass-binding lineage retained.

## Orbital information ratio relative to nucleons

After the atomic mass binding is admitted,

\[
\eta_A
=
\frac{I_{\rm orb}}{A\kappa},
\]

and

\[
\mu_s=\frac{M_s}{A}.
\]

The current Stage-A1 combined eclipse feature is

\[
\boxed{\mathcal E=\mu_s\,\eta_A\,\chi_r}.
\]

Every factor remains available as an independent column for the later comparison panel.

## Phase and eclipse harmonics

For a spatial orbital-band partition, the normalized observer-cell occupancy contrast is

\[
O_{\rm orb}(\phi)
=
\frac{p_o^{\rm orb}(\phi)}{q_o}-1.
\]

For the TIR inference sector, the phase trace is generated directly from the rotated Bloch coordinate:

\[
O_{\rm SIC}^{(j)}(\phi)
=
p_j(R(\phi)\mathbf n)-\frac14.
\]

Each trace is decomposed by a discrete Fourier transform and stores its dominant harmonic order and amplitude.

Conversion to hertz is activated by a separately provenance-bound phase rate:

\[
\nu_{\rm eclipse}
=
\frac{n_*\Omega_{\rm phase}}{2\pi}.
\]

The phase-rate binding is part of the later spectral-mapping preregistration.

## Blind validation stages

### Stage A0 — geometry freeze

1. Resolve the B--Ne atomic cards.
2. Compute radial exposure.
3. Compute the 2p shell-spin Bloch control.
4. Compute the TIR tetrahedral SIC inference coordinates.
5. Compute the frozen real-2p spatial orbital controls.
6. Persist hashes before the semantic-mass and spectral joins.

Gate:

```text
GEOMETRY_FEATURES_FROZEN_BEFORE_SEMANTIC_MASS_AND_SPECTRAL_JOIN
```

### Stage A1 — semantic-mass join

1. Bind each atomic card to an exact PNCS v0.19 realization.
2. Verify `M_s` under the frozen mass contract.
3. Compute `M_s/A`, `I_orb/(A*kappa)`, and the combined eclipse feature.
4. Freeze mass-weighted feature receipts.

Gate:

```text
FEATURES_FROZEN_BEFORE_SPECTRAL_JOIN
```

### Stage B — spectral mapping preregistration

Freeze the map from Stage-A features to spectral observables, including global scale parameters, calibration subset, held-out subset, error metric, and comparison controls.

Gate:

```text
SPECTRAL_MAPPING_PREREGISTERED
```

### Stage C — spectral join

Join the preregistered experimental observations and evaluate the frozen mapping on held-out transitions/elements.

Gate states:

```text
MODEL_FEATURE_AVAILABLE
BLIND_PREDICTION_FROZEN
EXPERIMENTAL_COMPARISON_AVAILABLE
HELD_OUT_VALIDATION_PASS
HELD_OUT_VALIDATION_FAIL
```

## Initial cohort

The first cohort is the implemented period-2 p-shell control path:

```text
B-11
C-12
N-14
O-16
F-19
Ne-20
```

This cohort supplies a continuous sequence from open 2p occupation through half filling to the closed 2p shell while remaining inside one established radial-control implementation.

## Model comparison columns

The frozen comparison surface preserves:

```text
radial exposure
2p spin polarization
TIR SIC probability vector
TIR SIC information
TIR SIC harmonic order and strength
spatial orbital information
spatial orbital harmonic order and strength
semantic mass per nucleon
orbital information per nucleon
semantic mass x orbital information
full eclipse coupling
spatial control partition identity
```

## Scientific status

The v0.15 model may suggest a relation between polyhedral electron-cone information, nuclear exposure, semantic mass, and spectral structure, yet does not state that relation as an established result.

Current evidential state:

```text
TIR tetrahedral SIC inference geometry: IMPLEMENTED
period-2 spin-Bloch control reduction: IMPLEMENTED
mass-independent Stage-A0 runner: IMPLEMENTED
spatial orbital feature layer: IMPLEMENTED
PNCS v0.19 semantic-mass bridge: IMPLEMENTED
semantic-card representation: IMPLEMENTED
atom-to-T36 bindings: OPEN
Stage-A0 durable execution ledger: PENDING EXECUTION
Stage-A1 mass-weighted ledger: PENDING T36 BINDINGS
spectral mapping preregistration: PENDING
experimental spectral comparison: PENDING
```
