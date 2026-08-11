from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Dict

KAPPA = math.log(2.0) / (24.0 * math.pi)
RYDBERG_ENERGY_EV = 13.605693122994
BOHR_RADIUS_ANGSTROM = 0.529177210903

ELEMENT_SYMBOLS = [
    "", "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar", "K", "Ca",
    "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn",
    "Ga", "Ge", "As", "Se", "Br", "Kr",
]

# (principal n, spectroscopic letter, capacity)
ORBITALS = [
    (1, "s", 2), (2, "s", 2), (2, "p", 6), (3, "s", 2),
    (3, "p", 6), (4, "s", 2), (3, "d", 10), (4, "p", 6),
]


def _orbital_key(n: int, subshell: str) -> str:
    return f"{n}{subshell}"


def _baseline_fill(electrons: int) -> Dict[str, int]:
    if electrons < 0 or electrons > 36:
        raise ValueError("v0.1 electron configuration supports 0..36 electrons")
    left = electrons
    out: Dict[str, int] = {}
    for n, shell, cap in ORBITALS:
        if left <= 0:
            break
        occ = min(cap, left)
        out[_orbital_key(n, shell)] = occ
        left -= occ
    return out


def electron_configuration(z: int, charge: int = 0) -> Dict[str, int]:
    """Return a deterministic v0.1 configuration through Kr.

    Neutral Cr and Cu ground-state exceptions are included. Ions are generated
    from the neutral state by removing the largest principal-n electrons first,
    then by the baseline Aufbau order for anions. This is bookkeeping, not a
    many-body energy solver.
    """
    if not (1 <= z <= 36):
        raise ValueError("v0.1 supports elements H..Kr (Z=1..36)")
    ne = z - charge
    if ne < 0 or ne > 36:
        raise ValueError("electron count must remain in 0..36 for v0.1")

    neutral = _baseline_fill(z)
    if z == 24:  # Cr: [Ar] 3d5 4s1
        neutral["4s"] = 1
        neutral["3d"] = 5
    elif z == 29:  # Cu: [Ar] 3d10 4s1
        neutral["4s"] = 1
        neutral["3d"] = 10

    if charge == 0:
        return {k: v for k, v in neutral.items() if v}

    conf = dict(neutral)
    if charge > 0:
        remove = charge
        # Highest principal n is ionized first; within same n use later
        # subshells first. This captures 4s-before-3d removal.
        def order_key(label: str):
            n = int(label[0])
            l = "spdf".index(label[1])
            return (n, l)
        for label in sorted(conf, key=order_key, reverse=True):
            if remove <= 0:
                break
            take = min(conf[label], remove)
            conf[label] -= take
            remove -= take
    else:
        # Refill from scratch for anions within the supported electron range.
        conf = _baseline_fill(ne)

    return {k: v for k, v in conf.items() if v}


def configuration_string(configuration: Dict[str, int]) -> str:
    return " ".join(f"{orb}^{occ}" for orb, occ in configuration.items()) or "(no electrons)"


def shell_population(configuration: Dict[str, int]) -> Dict[int, int]:
    shells: Dict[int, int] = {}
    for label, occ in configuration.items():
        n = int(label[0])
        shells[n] = shells.get(n, 0) + occ
    return dict(sorted(shells.items()))


def hydrogenic_energy_ev(z: int, n: int = 1) -> float:
    if z <= 0:
        raise ValueError("Z must be positive")
    if n <= 0:
        raise ValueError("principal quantum number n must be positive")
    return -RYDBERG_ENERGY_EV * (z * z) / (n * n)


def hydrogenic_radius_angstrom(z: int, n: int = 1) -> float:
    if z <= 0:
        raise ValueError("Z must be positive")
    if n <= 0:
        raise ValueError("principal quantum number n must be positive")
    return BOHR_RADIUS_ANGSTROM * (n * n) / z


@dataclass(frozen=True)
class Atom:
    z: int
    n_neutrons: int
    charge: int = 0

    def __post_init__(self) -> None:
        if not (1 <= self.z <= 36):
            raise ValueError("v0.1 supports Z=1..36")
        if self.n_neutrons < 0:
            raise ValueError("neutron count cannot be negative")
        if self.electron_count < 0 or self.electron_count > 36:
            raise ValueError("electron count outside v0.1 range 0..36")

    @property
    def symbol(self) -> str:
        return ELEMENT_SYMBOLS[self.z]

    @property
    def mass_number(self) -> int:
        return self.z + self.n_neutrons

    @property
    def electron_count(self) -> int:
        return self.z - self.charge

    @property
    def configuration(self) -> Dict[str, int]:
        return electron_configuration(self.z, self.charge)

    @property
    def shell_population(self) -> Dict[int, int]:
        return shell_population(self.configuration)

    @property
    def is_hydrogenic(self) -> bool:
        return self.electron_count == 1

    def as_dict(self, principal_n: int = 1) -> dict:
        data = {
            "schema": "RESCHEM_ATOM_V0_1",
            "symbol": self.symbol,
            "Z": self.z,
            "N": self.n_neutrons,
            "A": self.mass_number,
            "charge": self.charge,
            "electron_count": self.electron_count,
            "configuration": configuration_string(self.configuration),
            "shell_population": self.shell_population,
            "kappa_tir": KAPPA,
            "hydrogenic": self.is_hydrogenic,
            "epistemic_status": {
                "identity_and_counting": "ESTABLISHED",
                "electron_configuration": "CONTROL_BOOKKEEPING_V0_1",
                "tir_relation_operator": "RESERVED_NOT_YET_APPLIED",
            },
        }
        if self.is_hydrogenic:
            data["hydrogenic_solution"] = {
                "approximation": "nonrelativistic_infinite_nuclear_mass",
                "n": principal_n,
                "energy_eV": hydrogenic_energy_ev(self.z, principal_n),
                "characteristic_radius_A": hydrogenic_radius_angstrom(self.z, principal_n),
            }
        return data
