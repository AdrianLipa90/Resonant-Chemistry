"""Conventional atomic-control vector for closed-shell activation candidates.

v0.11 does not add a molecular energy correction and does not fit known noble-
gas chemistry.  It reuses the repository's existing robust average-of-
configuration atomic Hartree--Fock solver for neutral and charged atoms.

For centre X and ligand Y the raw vector is

    I_X^HF      = E_HF(X+) - E_HF(X)
    A_Y^HF      = E_HF(Y)  - E_HF(Y-)
    Delta_CT^HF = I_X^HF - A_Y^HF
    r_X,p       = mean radius of the outermost p channel of neutral X
    r_Y,p       = mean radius of the outermost p channel of neutral Y

The symbols I/A are control-model finite-difference quantities.  In particular,
A_Y^HF is *not* asserted to be an accurate experimental electron affinity: a
finite-basis HF anion can be qualitatively imperfect.  Delta_CT is likewise not
a literal one-electron-transfer mechanism for a 3c4e bond.

No scalar score, fitted weight, threshold, or candidate-specific rescue is
introduced in v0.11.  The purpose is to freeze a conventional atomic descriptor
vector before comparing it with the already-opened 3c4e/VDW reference classes.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from functools import lru_cache
from math import isfinite
from typing import Callable

from .atomic_hf_diis import RobustAtomicHFResult, solve_atom_average_hf_robust
from .atom import ELEMENT_SYMBOLS
from .closed_shell_activation import generate_closed_shell_activation_atlas

AtomicSolver = Callable[[int, int], RobustAtomicHFResult]


@dataclass(frozen=True)
class AtomicActivationControl:
    centre_Z: int
    centre_symbol: str
    ligand_Z: int
    ligand_symbol: str
    centre_neutral_energy_hartree: float
    centre_cation_energy_hartree: float
    ligand_neutral_energy_hartree: float
    ligand_anion_energy_hartree: float
    centre_ionization_cost_hartree: float
    ligand_attachment_gain_hartree: float
    charge_transfer_margin_hartree: float
    centre_outer_p_mean_radius_bohr: float
    ligand_outer_p_mean_radius_bohr: float
    centre_outer_p_radial_sigma_bohr: float
    ligand_outer_p_radial_sigma_bohr: float
    all_atomic_quality_pass: bool
    status: str = "CONVENTIONAL_ATOMIC_CONTROL_VECTOR_NOT_MOLECULAR_ENERGY"

    def to_dict(self) -> dict:
        return asdict(self)


def _outer_p_channel(result: RobustAtomicHFResult) -> tuple[float, float]:
    channels = [item for item in result.result.channel_summary if item["l"] == 1]
    if not channels:
        raise ValueError("no p channel available for atomic activation control")
    outer = max(channels, key=lambda item: (item["n"], item["occupancy"]))

    weighted_radius = 0.0
    weighted_sigma = 0.0
    total = 0
    for spin, occupancy_key in (("alpha", "alpha_occupancy"), ("beta", "beta_occupancy")):
        occupancy = int(outer[occupancy_key])
        if occupancy <= 0:
            continue
        data = outer["radial_channels"].get(spin)
        if data is None:
            raise ValueError(f"missing {spin} radial channel for {outer['subshell']}")
        weighted_radius += occupancy * float(data["mean_radius_bohr"])
        weighted_sigma += occupancy * float(data["radial_sigma_bohr"])
        total += occupancy

    if total <= 0:
        raise ValueError("outer p channel has zero represented occupancy")
    return weighted_radius / total, weighted_sigma / total


def build_atomic_activation_control(
    centre_z: int,
    ligand_z: int,
    *,
    solver: AtomicSolver = solve_atom_average_hf_robust,
) -> AtomicActivationControl:
    """Build one raw v0.11 vector without fitting or model labels."""
    centre_neutral = solver(centre_z, 0)
    centre_cation = solver(centre_z, +1)
    ligand_neutral = solver(ligand_z, 0)
    ligand_anion = solver(ligand_z, -1)

    results = (centre_neutral, centre_cation, ligand_neutral, ligand_anion)
    energies = tuple(float(item.result.energy_hartree) for item in results)
    if not all(isfinite(value) for value in energies):
        raise FloatingPointError("non-finite atomic control energy")

    ionization = energies[1] - energies[0]
    attachment = energies[2] - energies[3]
    margin = ionization - attachment

    centre_r, centre_sigma = _outer_p_channel(centre_neutral)
    ligand_r, ligand_sigma = _outer_p_channel(ligand_neutral)

    return AtomicActivationControl(
        centre_Z=centre_z,
        centre_symbol=ELEMENT_SYMBOLS[centre_z],
        ligand_Z=ligand_z,
        ligand_symbol=ELEMENT_SYMBOLS[ligand_z],
        centre_neutral_energy_hartree=energies[0],
        centre_cation_energy_hartree=energies[1],
        ligand_neutral_energy_hartree=energies[2],
        ligand_anion_energy_hartree=energies[3],
        centre_ionization_cost_hartree=ionization,
        ligand_attachment_gain_hartree=attachment,
        charge_transfer_margin_hartree=margin,
        centre_outer_p_mean_radius_bohr=centre_r,
        ligand_outer_p_mean_radius_bohr=ligand_r,
        centre_outer_p_radial_sigma_bohr=centre_sigma,
        ligand_outer_p_radial_sigma_bohr=ligand_sigma,
        all_atomic_quality_pass=all(item.quality_pass for item in results),
    )


def generate_atomic_activation_control_atlas(
    *,
    solver: AtomicSolver = solve_atom_average_hf_robust,
) -> tuple[AtomicActivationControl, ...]:
    """Build vectors for the frozen nine-member v0.9 atlas.

    A local memoizer prevents repeated neutral/ion calculations while preserving
    the exact same solver call for every atomic species/charge pair.
    """
    cached = lru_cache(maxsize=None)(solver)
    return tuple(
        build_atomic_activation_control(
            candidate.centre_Z,
            candidate.ligand_Z,
            solver=cached,
        )
        for candidate in generate_closed_shell_activation_atlas()
    )
