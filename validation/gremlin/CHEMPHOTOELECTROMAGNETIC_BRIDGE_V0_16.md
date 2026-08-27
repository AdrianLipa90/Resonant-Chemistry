# GREMLIN audit — Chem-Photo-Electromagnetic Bridge v0.16

Status: `CANDIDATE_AUDIT_ONLY`

Contract: `RCE_CHEM_PHOTO_EM_BRIDGE_V0_1`

GREMLIN authority: relational-isomorphism candidate generation and audit only. Canon promotion remains external to GREMLIN.

## Accepted structural mappings

### G1 — temporal mode ↔ spectral line

For an admitted chemical eigenstate pair,

\[
C_{mn}(t)=A_{mn}e^{-\Gamma_{mn}|t|/2}e^{-i\omega_{mn}t},
\qquad
\omega_{mn}=\frac{E_m-E_n}{\hbar}.
\]

Fourier transformation maps the temporal mode to spectral support centred at \(\omega_{mn}\).

Classification: `EXACT_GIVEN_ADMITTED_HAMILTONIAN_AND_COUPLING`.

### G2 — chemical state graph ↔ spectral fingerprint

Changing the chemical state operator changes its energy differences and transition matrix elements, hence changes

\[
\mathcal L_{\rm chem}=\{(\omega_{mn},I_{mn},\Gamma_{mn})\}.
\]

Classification: `STANDARD_SPECTRAL_CONSEQUENCE / EMPIRICAL_VALIDATION_REQUIRED_FOR_MODEL_PREDICTIONS`.

### G3 — half interface ↔ spectral null

The cross-repository kernel

\[
D_{1/2}(\sigma,\Delta\tau)=1+2\sqrt{\sigma(1-\sigma)}\cos(\Delta\tau/2)
\]

has exact zero at

\[
\sigma=\frac12,
\qquad
\Delta\tau\equiv2\pi\pmod{4\pi}.
\]

Classification: `EXACT_LOCAL_IDENTITY / PHYSICAL_TWO_PATH_BINDING_PENDING`.

### G4 — SOH Zeeman-type split ↔ transition-frequency coordinate

Inside the declared SOH two-level ansatz,

\[
\Delta E(B)=2|\lambda B|
\quad\Longrightarrow\quad
\omega_{+-}(B)=\frac{2|\lambda B|}{\hbar}.
\]

Classification: `EXACT_INSIDE_DECLARED_ANSATZ / CROSS-DOMAIN_PHYSICAL_PROMOTION_PENDING`.

### G5 — TIR relational geometry ↔ chemical-state descriptor

TIR tetrahedral SIC probabilities and relative information already have an executable Resonant Chemistry v0.15 carrier. Their incremental value for predicting held-out spectral structure is a direct test target.

Classification: `IMPLEMENTED_DESCRIPTOR / INCREMENTAL_PREDICTION_PENDING`.

## Typing rejection

Candidate statement:

`the value 1/2 determines all spectral line centres`

GREMLIN verdict:

`REJECTED_BY_CURRENT_TYPING`.

Current line centres are typed by admitted energy differences through \(\hbar\omega_{mn}=E_m-E_n\). The half-interface is admitted at this gate as an interference/null condition. A wider role requires an independent derivation and held-out validation.

## Promotable hypotheses

- `H-CPEM-01`: the IDT temporal-correlation adapter reproduces the line centres implied by the frozen chemical state model.
- `H-CPEM-02`: distinct frozen chemical state graphs yield distinct deterministic spectral fingerprints.
- `H-CPEM-03`: in independently identified two-path transitions, the half-interface predicts a dark/suppressed channel at equal weight and spinorial half-turn.
- `H-CPEM-04`: TIR geometric features improve held-out spectral prediction relative to matched baseline controls.
- `H-CPEM-05`: IDT temporal features improve held-out linewidth/phase-coherence prediction relative to the same chemical baseline.

## Proof firewall

`SOH-C004`: `UNCHANGED`

`SOH-C005`: `UNCHANGED`

TIR claim hierarchy: `UNCHANGED`

IDT Einstein Closure: `UNCHANGED`

Empirical molecular/compound promotion: `PENDING`.
