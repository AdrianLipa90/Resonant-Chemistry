# Quantum Matter Bridge / H2+ no-refit gate v0.1

Status: `CANDIDATE_INTERFACE / CONTROL_PHYSICS_PRESERVED / PHYSICAL_OPERATOR_BINDING_OPEN`

## 1. Scope

This document defines the minimum typed bridge between the existing relational/phase source surfaces and conventional quantum chemistry. It does **not** add a new physical term to the Resonant Chemistry control Hamiltonian.

The conventional electronic-structure solution remains authoritative. A candidate relational contribution may enter only through a separately derived Hermitian perturbation

\[
\hat V_I[X;R],
\]

where the chemical state record is explicitly declared, for example

\[
X=(\rho,\gamma,J,\Phi,\mathcal E,R).
\]

No symbol in this tuple is automatically identified with a TIR, RFC, GREMLIN, QHTRI, or PhaseNav carrier by notation alone.

## 2. Physical state-binding gate

The missing physical bridge is a source-owned map

\[
\mathcal B_{\rm chem}: X_{\rm electronic}\longrightarrow X_{\rm relational},
\]

or an equivalent typed construction that states exactly which SCF/CI/MCSCF observables source the candidate operator.

Promotion requires all of the following:

1. named electronic-state inputs with provenance;
2. basis/gauge transformation law;
3. units and normalization;
4. a declared domain of validity;
5. no use of target spectroscopy residuals to construct the map.

Until these conditions are met:

`RC.MATTER.PHYSICAL_STATE_BINDING = OPEN_CANDIDATE`.

## 3. Informational perturbation interface

After state binding is supplied, the candidate Hamiltonian is

\[
\hat H_{\rm eff}(R)=\hat H_0(R)+\hat V_I(R).
\]

Admission requirements for \(\hat V_I\):

- \(\hat V_I^\dagger=\hat V_I\);
- energy dimensions are explicit;
- all coefficients have provenance;
- transformation behaviour under the declared basis/gauge action is explicit;
- no coefficient is fitted to the target holdout;
- setting the candidate coupling to zero exactly recovers \(\hat H_0\).

For a normalized nondegenerate control state \(|n\rangle\), the standard first-order response is

\[
\Delta E_n=\langle n|\hat V_I|n\rangle.
\]

For a transition \(n\to m\),

\[
\Delta\omega_{mn}=\frac{\Delta E_m-\Delta E_n}{\hbar}.
\]

A common-mode perturbation

\[
\hat V_I=u_0(R)\mathbf 1
\]

therefore gives the exact null

\[
\boxed{\Delta\omega_{mn}=0}.
\]

This null is part of the preregistered falsification contract.

## 4. H2+ first molecular control

The first molecular target is \(H_2^+\) because it is a genuine two-centre molecular problem with one electron and therefore does not require electron-electron correlation.

In atomic units, under the clamped-nuclei Born-Oppenheimer control,

\[
\hat H_{\rm el}^{(0)}
=
-\frac12\nabla^2
-\frac1{r_A}
-\frac1{r_B},
\]

and the total Born-Oppenheimer energy is

\[
E_{\rm BO}^{(0)}(R)=E_{\rm el}^{(0)}(R)+\frac1R.
\]

The candidate layer may only add the already-frozen \(\hat V_I\); it may not alter the baseline solver to improve agreement.

The control ladder is

\[
H\rightarrow He\rightarrow H_2^+\rightarrow H_2\rightarrow HeH^+\rightarrow LiH.
\]

Interpretation:

- \(H\): one-electron atomic control;
- \(He\): electron-electron control;
- \(H_2^+\): first two-centre control;
- \(H_2\): exchange/correlation;
- \(HeH^+\): asymmetry;
- \(LiH\): core/valence and charge-transfer stress test.

## 5. No-refit prospective gate

Before any withheld molecular/spectroscopic residual is inspected, freeze:

1. state-binding map;
2. complete \(\hat V_I\) definition;
3. all constants and units;
4. basis/gauge convention;
5. target transition/observable;
6. predicted sign, magnitude or exact null;
7. solver/tolerances;
8. PASS/FAIL decision rule.

The sequence is then

\[
\text{freeze}
\to
\text{control baseline}
\to
\text{candidate evaluation}
\to
\text{withheld observation}
\to
\text{PASS/FAIL}.
\]

A failed prediction remains evidence. Post-result retuning creates a new version and does not overwrite the frozen result.

## 6. Current epistemic boundary

Implemented here:

- fail-closed Hermitian-operator checks;
- normalized-state checks;
- standard first-order expectation value;
- transition angular-frequency shift;
- exact common-mode spectral null;
- the conventional \(H_2^+\) nuclear-repulsion bookkeeping helper;
- a preregistration schema with no target measurements.

Not implemented / OPEN:

- physical \(X_{\rm electronic}\to X_{\rm relational}\) binding;
- a source-derived physical \(\hat V_I\);
- a prospective experimental holdout result;
- promotion of any new energy term into the canonical chemistry Hamiltonian.

## 7. FPDG handoff

Only after source-owned RC claims exist should FPDG add a cross-repository candidate interface. FPDG must not invent the physical operator on behalf of Resonant Chemistry.

The intended future cross-repository edge is therefore downstream of the source claims defined here and remains `CANDIDATE_ONLY` until the physical state/operator binding gate passes.
