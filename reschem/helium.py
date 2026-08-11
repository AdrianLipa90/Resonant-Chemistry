from __future__ import annotations

from dataclasses import dataclass

HARTREE_TO_EV = 27.211386245988

# Reference diagnostics only; never solver inputs.
HELIUM_EXACT_NONREL_HARTREE = -2.903724377034
HELIUM_HF_LIMIT_HARTREE = -2.861679995612


def variational_energy_hartree(nuclear_charge: int, zeta: float) -> float:
    """Two-electron 1s^2 product ansatz in atomic units.

    E(zeta) = zeta^2 - 2 Z zeta + (5/8) zeta.
    The final term is the analytic expectation value of 1/r12.
    """
    if nuclear_charge <= 0:
        raise ValueError("nuclear_charge must be positive")
    if zeta <= 0:
        raise ValueError("zeta must be positive")
    z = float(nuclear_charge)
    return zeta * zeta - 2.0 * z * zeta + (5.0 / 8.0) * zeta


def optimal_zeta(nuclear_charge: int) -> float:
    if nuclear_charge <= 0:
        raise ValueError("nuclear_charge must be positive")
    zeta = float(nuclear_charge) - 5.0 / 16.0
    if zeta <= 0:
        raise ValueError("simple 1s^2 ansatz has no positive optimum")
    return zeta


def optimal_energy_hartree(nuclear_charge: int) -> float:
    zeta = optimal_zeta(nuclear_charge)
    return variational_energy_hartree(nuclear_charge, zeta)


@dataclass(frozen=True)
class TwoElectronVariationalResult:
    nuclear_charge: int
    zeta: float
    energy_hartree: float

    @property
    def energy_ev(self) -> float:
        return self.energy_hartree * HARTREE_TO_EV

    @property
    def kinetic_hartree(self) -> float:
        return self.zeta ** 2

    @property
    def potential_hartree(self) -> float:
        z = float(self.nuclear_charge)
        return -2.0 * z * self.zeta + (5.0 / 8.0) * self.zeta

    @property
    def virial_residual_hartree(self) -> float:
        return 2.0 * self.kinetic_hartree + self.potential_hartree

    def as_dict(self) -> dict:
        out = {
            "schema": "RESCHEM_TWO_ELECTRON_VARIATIONAL_V0_1",
            "Z": self.nuclear_charge,
            "zeta": self.zeta,
            "energy_hartree": self.energy_hartree,
            "energy_eV": self.energy_ev,
            "kinetic_hartree": self.kinetic_hartree,
            "potential_hartree": self.potential_hartree,
            "virial_residual_hartree": self.virial_residual_hartree,
            "ansatz": "spin-singlet with shared hydrogenic 1s spatial orbital",
            "electron_electron_term": "analytic <1/r12> = 5 zeta / 8",
            "tir_status": "NOT_APPLIED_CONTROL_BASELINE",
            "epistemic_status": "VARIATIONAL_CONTROL_MODEL",
        }
        if self.nuclear_charge == 2:
            out["helium_diagnostics"] = {
                "exact_nonrel_reference_hartree": HELIUM_EXACT_NONREL_HARTREE,
                "hartree_fock_limit_reference_hartree": HELIUM_HF_LIMIT_HARTREE,
                "relative_error_vs_exact": abs(self.energy_hartree - HELIUM_EXACT_NONREL_HARTREE) / abs(HELIUM_EXACT_NONREL_HARTREE),
                "relative_error_vs_hf_limit": abs(self.energy_hartree - HELIUM_HF_LIMIT_HARTREE) / abs(HELIUM_HF_LIMIT_HARTREE),
                "missing_binding_vs_exact_hartree": self.energy_hartree - HELIUM_EXACT_NONREL_HARTREE,
            }
        return out


def solve_two_electron_variational(nuclear_charge: int) -> TwoElectronVariationalResult:
    zeta = optimal_zeta(nuclear_charge)
    return TwoElectronVariationalResult(
        nuclear_charge=nuclear_charge,
        zeta=zeta,
        energy_hartree=variational_energy_hartree(nuclear_charge, zeta),
    )
