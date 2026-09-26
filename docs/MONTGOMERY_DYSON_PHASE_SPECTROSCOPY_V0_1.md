# Montgomery–Dyson Phase Spectroscopy v0.1 — Resonant Chemistry adapter

Status: CANDIDATE / IMPLEMENTED. No scientific promotion is implied.

Resonant Chemistry owns state construction and physical/candidate admission. The phase-spectroscopy layer operates only after a set of calculated or measured transition coordinates has been established by an explicitly named upstream method.

Shared coordinates:

Phi_j = 2*pi*u_j,

R_2(Delta Phi) = 1 - [sin(Delta Phi/2)/(Delta Phi/2)]^2,

omega_(p,m) = m log p,
w_(p,m) = log(p)/p^(m/2).

## Chemistry binding

1. Standard quantum chemistry remains the physical baseline.
2. transition_energy_phase_coordinates consumes transition energies or frequencies; it does not generate them.
3. The diagnostic must never alter Hamiltonians, SCF/CI/MCSCF solutions, molecular screening energies, state ranking or semantic-card admission.
4. GUE/Poisson comparisons describe spacing statistics only.
5. The prime-power basis is an arithmetic reference and reverse-control family, not a chemical force, interaction or periodic-table generator.
6. Any proposed cross-domain relation must be tested against phase-scrambled carriers and conventional spectral null models.
7. Density-varying spectra require an explicitly preregistered domain unfolding; the affine transform in code is a control/smoke implementation.

The intended chain is:

validated state model -> transition set -> unfolding -> phase coordinates -> pair correlation / form factor -> null comparison.

This preserves the repository distinction between established controls, model-defined quantities and candidates.
