# Informational Phase / EB-Orbital / Spectroscopy Crosswalk

Status: `CANDIDATE_CROSS_REPO_INTERFACE / STANDARD_CHEMICAL_RESPONSE / PHYSICAL_INFORMATIONAL_COUPLING_OPEN`

## Scope

This note connects Resonant-Chemistry to the upstream informational phase-mechanics and GREMLIN EB-orbital dependency surfaces without changing the conventional quantum-chemistry baseline.

The chemistry repository remains authoritative for electronic/nuclear energies, gradients, Hessians and spectroscopy controls. It does not infer the physical existence of the upstream informational or EB source coupling.

## 1. Typed perturbation interface

Let a declared chemistry adapter supply a Hermitian perturbation

```text
V_I(R)
```

on the same electronic/nuclear configuration `R` as the conventional Hamiltonian.

Then

```text
H_chem_eff(R) = H_chem_0(R) + V_I(R).
```

For a nondegenerate state `|n>`, the first-order energy response is

```text
Delta E_n(R) = <n|V_I(R)|n>.
```

This is standard perturbation theory after `V_I` is admitted. The physical derivation of `V_I` from an informational or EB carrier remains a separate gate.

## 2. Force and curvature readout

The state-specific force contribution is

```text
Delta F_n(R) = -grad_R Delta E_n(R).
```

The molecular curvature contribution is

```text
Delta K_n(R) = Hess_R Delta E_n(R).
```

Therefore an admitted common potential may be interrogated through geometry, relaxation and vibrational-curvature observables without identifying those observables with the source mechanism.

## 3. Spectroscopic differential null

For a transition `n -> m`,

```text
Delta omega_mn
 = (Delta E_m - Delta E_n)/hbar.
```

The relative accumulated phase is

```text
Delta Phi_mn
 = - integral Delta omega_mn dt.
```

If the perturbation is common-mode on the compared states,

```text
V_I = u_0(R) I
```

within that state space, then

```text
Delta E_m = Delta E_n
Delta omega_mn = 0.
```

Thus a scalar/common potential can alter a spatial wavefront or common phase while leaving a transition frequency unchanged. Spectroscopic shifts require differential state coupling.

## 4. Upstream informational phase mechanics

The QHTRI phase-optics project owns the model interface

```text
Xi_I -> U_I = (alpha_I/kappa_E) Xi_I
U_I -> action -> phase
grad U_I -> force
Hess Phi_I -> lens/focusing tensor.
```

A chemistry adapter may consume `U_I(R)` only after its carrier/state-space map is explicit. Resonant-Chemistry does not identify `U_I` with an electronic or nuclear potential by notation alone.

## 5. GREMLIN EB-orbital cross-reference

GREMLIN v0.9 composes the RFC finite phase Hamiltonian with the orbital source and informational radial term:

```text
omega^2
 = C_mu H_Phi^EB eta_G/r^3
 + alpha_I/(m_I r kappa_E) dXi_I/dr.
```

This is an upstream candidate dependency relation.

For chemistry, the useful connection is not to equate orbital radius `r` with a molecular coordinate automatically, but to expose a typed adapter

```text
(rho, phase, current, R)
 -> V_I(R)
 -> Delta E_n(R)
 -> {forces, Hessians, transition shifts}.
```

Any mapping `r <-> R`, source coefficient, or physical EB-condensate identification remains OPEN.

## 6. Cross-domain consistency test

After independently frozen adapters exist, the same upstream state may yield:

```text
orbital route:  U_I -> omega(r), r, stability
chemical route: U_I -> Delta E_n, grad E_n, Hess E_n
spectral route: Delta E_mn -> Delta omega_mn -> Delta Phi_mn
optical route:  U_I -> grad Phi, Hess Phi
```

Agreement is evidential only when one downstream route is not fitted to reproduce another.

## 7. Authority and firewalls

Established/standard after a declared perturbation:
- Hermitian perturbation theory;
- force from the energy gradient;
- curvature from the energy Hessian;
- transition shift from an energy difference;
- common-mode cancellation in transition frequency.

OPEN/CANDIDATE:
- physical `U_I -> V_I(R)` chemistry coupling;
- EB-condensate realization;
- `C_mu` and `eta_G` source ownership;
- any gravitational interpretation of the chemistry perturbation.

External parents:
- QHTRI phase optics: `docs/PHASE_MECHANICS_GREMLIN_ORBITAL_EB_BRIDGE.md`
- GREMLIN: `spec/GREMLIN_EB_CONDENSATE_ORBITAL_PHASE_BRIDGE_V0_9.md`
- RFC: `formalism/RF_GREMLIN_EB_ORBITAL_PHASE_CROSSWALK_V0_1.md`
