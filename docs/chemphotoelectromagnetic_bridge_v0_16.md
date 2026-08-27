# Resonant Chemistry v0.16 — Chem-Photo-Electromagnetic Spectral Bridge

Status: `INTEGRATION_ADAPTER_IMPLEMENTED_CANDIDATE / EMPIRICAL_PROMOTION_PENDING`

Base provenance: `AdrianLipa90/Resonant-Chemistry@4d374483e17d6543c2772d048e48b36c65656d2b` (`chem/v0.15-polyhedral-eclipse-spectroscopy`).

Contract: `RCE_CHEM_PHOTO_EM_BRIDGE_V0_1`

## 1. Operational definition

Within this project, **chem-photo-electromagnetic** denotes the calculation path

\[
\boxed{
\text{chemical state}
\rightarrow
\text{photo/electromagnetic transition}
\rightarrow
\text{temporal phase correlation}
\rightarrow
\text{spectral line or band}.
}
\]

The bridge joins the chemical-state machinery already present in Resonant Chemistry to the time/phase layer developed in Informational Dynamics of Time, with TIR geometry as an upstream state descriptor and Secret of a Half as a restricted interference-null kernel.

## 2. Why spectra contain stripes

Let

\[
H_{\rm chem}|n\rangle=E_n|n\rangle
\]

and let \(\hat\mu\) be the leading admitted electromagnetic transition operator. In an eigenbasis,

\[
C_{\mu\mu}(t)=\sum_{n,m}p_n|\mu_{mn}|^2e^{-i(E_m-E_n)t/\hbar}.
\]

Therefore each admitted transition carries a discrete angular frequency

\[
\boxed{\omega_{mn}=\frac{|E_m-E_n|}{\hbar}.}
\]

The spectrum is the Fourier-domain readout of these temporal modes:

\[
S(\omega)\propto\sum_{n,m}p_n|\mu_{mn}|^2L(\omega-\omega_{mn};\Gamma_{mn}).
\]

In the infinite-coherence limit \(L\) approaches delta support. With finite coherence time, lifetime, collisions, temperature and instrumental response, the support broadens.

Thus a spectral stripe is a persistent frequency component of an admitted chemical transition correlation.

## 3. Why each species has its own fingerprint

Different atoms and compounds have different nuclear composition, electronic structure, bonding geometry, electron correlation, spin-orbit structure, electronic/vibrational/rotational state ladders, transition matrix elements, populations and decoherence/lifetime scales.

These differences change

\[
\boxed{\mathcal L_{\rm chem}=\{(\omega_{mn},I_{mn},\Gamma_{mn})\},}
\]

which produces the spectral fingerprint.

For molecules, a state can be labelled schematically by \(|e,v,J,\ldots\rangle\), so electronic transitions acquire vibrational and rotational substructure and appear as line families or bands.

## 4. Existing v0.15 assets reused directly

The bridge consumes the existing v0.15 stack:

```text
reschem/atomic_radial_spectroscopy.py
reschem/period2_correlated_spectrum.py
reschem/polyhedral_eclipse_spectroscopy.py
reschem/atomic_subjective_time_v015.py
reschem/eclipse_time_doppler_v015.py
reschem/atomic_kepler_phase_v015.py
reschem/tetrahedral_inference_v015.py
reschem/pncs_semantic_mass_bridge_v015.py
```

It also preserves the frozen NIST atomic benchmark ledgers and the existing blind-comparison protocol.

## 5. New v0.16 adapter

Implementation:

`reschem/chemphotoelectromagnetic_bridge_v016.py`

Core functions:

```text
half_interface_defect
relational_zero
transition_angular_frequency
electric_dipole_strength
lorentzian
temporal_coherence
build_transition_lines
spectrum
fingerprint_signature
```

The generic spectral centre is determined by the admitted energy gap. The half-interface kernel is attached separately to two-path interference / dark-channel diagnostics.

## 6. Half-interface diagnostic

The imported IDT × Secret-of-a-Half kernel is

\[
D_{1/2}(\sigma,\Delta\tau)=1+2\sqrt{\sigma(1-\sigma)}\cos(\Delta\tau/2).
\]

Its exact zero is

\[
\boxed{\sigma=\frac12,\qquad\Delta\tau\equiv2\pi\pmod{4\pi}.}
\]

This gives an executable test for equal-amplitude destructive cancellation when the chemical transition model supplies a valid two-path mapping.

## 7. Integration boundary

Upstream roles:

```text
TIR:
  tetrahedral SIC / relational information / phase geometry

Informational-Dynamics-of-Time:
  internal elapsed coordinate / 2pi-4pi lift / temporal correlation

Secret-of-a-Half:
  balanced half-interface / spinorial cancellation / doublet ansatz

Resonant-Chemistry:
  chemical state / orbital and molecular structure / transition energies /
  electromagnetic couplings / spectral validation
```

The repository/formalism may suggest that the half-interface is a universal structural origin of spectral nulls, yet does not state that claim as an established result. The v0.16 gate tests it only where an independently defined two-channel physical mapping exists.

## 8. Promotion plan

### Stage A — adapter invariants

- exact half-interface null;
- \(2\pi/4\pi=1/2\) cover identity;
- line centre equals admitted energy gap divided by \(\hbar\);
- zero admitted transition coupling gives zero line strength;
- positive linewidth produces a finite line profile;
- distinct state graphs produce distinct deterministic fingerprints.

### Stage B — atomic control

Reuse the existing NIST atomic line/level datasets to verify that the correlation-to-spectrum adapter preserves the already admitted atomic transition structure.

### Stage C — molecular / compound holdout

Freeze a molecular state model before opening held-out spectral data. Compare line/band centre error, transition-support precision and recall, intensity rank correlation, linewidth residuals and isotope/geometry shift consistency.

### Stage D — half-interface falsifier

Select only physical cases with an independently identified two-path transition amplitude. Preregister the equal-weight / relative-phase prediction and test whether the half-interface correctly predicts a dark or suppressed channel.

### Stage E — incremental-value test

Compare:

```text
chemical baseline
+ TIR geometry
+ IDT temporal features
+ half-interface diagnostic
```

using held-out species/families and frozen metrics. Only increments that survive the held-out gate are eligible for promotion.
