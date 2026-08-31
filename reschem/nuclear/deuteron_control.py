"""Controlled S-wave deuteron benchmark using the Malfliet-Tjon triplet potential.

Evidential class: CONTROL_MODEL_REPRODUCTION.

The implementation solves the reduced radial Schr\u00f6dinger equation on a finite
Dirichlet grid. The interaction parameters and kinetic convention are loaded
from an immutable provider packet; no solver-side parameter fitting occurs.
"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np
from scipy.integrate import trapezoid
from scipy.linalg import eigh_tridiagonal

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INTERACTION_PATH = (
    ROOT / "data" / "nuclear" / "interactions" / "mt_triplet_control_v0_1.json"
)
DEFAULT_NUCLEON_PACKET_PATH = (
    ROOT / "data" / "nuclear" / "nucleon_packet_codata2022_pdg2025_v0_1.json"
)


@dataclass(frozen=True)
class MalflietTjonTriplet:
    V_A_mev_fm: float
    mu_A_inv_fm: float
    V_R_mev_fm: float
    mu_R_inv_fm: float
    hbar2_over_m_mev_fm2: float
    reference_binding_energy_mev: float
    reference_single_nucleon_rms_fm: float
    interaction_id: str

    @classmethod
    def from_json(cls, path: Path | str = DEFAULT_INTERACTION_PATH) -> "MalflietTjonTriplet":
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
        params = payload["parameters"]
        ref = payload["reference"]
        return cls(
            V_A_mev_fm=float(params["V_A_mev_fm"]),
            mu_A_inv_fm=float(params["mu_A_inv_fm"]),
            V_R_mev_fm=float(params["V_R_mev_fm"]),
            mu_R_inv_fm=float(params["mu_R_inv_fm"]),
            hbar2_over_m_mev_fm2=float(params["hbar2_over_m_mev_fm2"]),
            reference_binding_energy_mev=float(ref["binding_energy_mev"]),
            reference_single_nucleon_rms_fm=float(ref["single_nucleon_about_com_rms_fm"]),
            interaction_id=str(payload["interaction_id"]),
        )

    def potential(self, r_fm: np.ndarray) -> np.ndarray:
        r = np.asarray(r_fm, dtype=float)
        if np.any(r <= 0.0):
            raise ValueError("radial grid must be strictly positive")
        return (
            self.V_A_mev_fm * np.exp(-self.mu_A_inv_fm * r)
            + self.V_R_mev_fm * np.exp(-self.mu_R_inv_fm * r)
        ) / r


@dataclass(frozen=True)
class DeuteronControlResult:
    interaction_id: str
    n_points: int
    r_max_fm: float
    dr_fm: float
    ground_state_energy_mev: float
    binding_energy_mev: float
    second_level_energy_mev: float
    bound_state_count_in_sample: int
    relative_coordinate_rms_fm: float
    single_nucleon_about_com_rms_fm: float
    reference_binding_energy_mev: float
    binding_residual_mev: float
    reference_single_nucleon_rms_fm: float
    single_nucleon_rms_residual_fm: float
    physical_pn_reduced_mass_mev: float
    physical_hbar2_over_2mu_mev_fm2: float
    model_hbar2_over_m_mev_fm2: float


def _physical_pn_kinematics(packet_path: Path | str = DEFAULT_NUCLEON_PACKET_PATH) -> tuple[float, float]:
    payload = json.loads(Path(packet_path).read_text(encoding="utf-8"))
    mp = float(payload["values"]["proton"]["mass_energy_mev"])
    mn = float(payload["values"]["neutron"]["mass_energy_mev"])
    hbar_c = float(payload["constants"]["hbar_c_mev_fm"])
    mu = mp * mn / (mp + mn)
    hbar2_over_2mu = hbar_c * hbar_c / (2.0 * mu)
    return mu, hbar2_over_2mu


def solve_deuteron_mt_triplet(
    *,
    n_points: int = 8000,
    r_max_fm: float = 30.0,
    interaction: MalflietTjonTriplet | None = None,
    nucleon_packet_path: Path | str = DEFAULT_NUCLEON_PACKET_PATH,
) -> DeuteronControlResult:
    if n_points < 200:
        raise ValueError("n_points must be >= 200")
    if r_max_fm <= 5.0:
        raise ValueError("r_max_fm must be > 5 fm")

    interaction = interaction or MalflietTjonTriplet.from_json()
    dr = float(r_max_fm) / float(n_points + 1)
    r = dr * np.arange(1, n_points + 1, dtype=float)

    coefficient = interaction.hbar2_over_m_mev_fm2
    potential = interaction.potential(r)
    diagonal = 2.0 * coefficient / (dr * dr) + potential
    off_diagonal = np.full(n_points - 1, -coefficient / (dr * dr), dtype=float)

    levels, vectors = eigh_tridiagonal(
        diagonal,
        off_diagonal,
        select="i",
        select_range=(0, 4),
        eigvals_only=False,
        check_finite=True,
    )
    ground = float(levels[0])
    second = float(levels[1])
    u = np.asarray(vectors[:, 0], dtype=float)
    norm = float(np.sqrt(trapezoid(u * u, r)))
    if not np.isfinite(norm) or norm <= 0.0:
        raise RuntimeError("invalid wavefunction normalization")
    u /= norm

    relative_rms = float(np.sqrt(trapezoid((r * r) * (u * u), r)))
    single_nucleon_rms = 0.5 * relative_rms
    mu, physical_coefficient = _physical_pn_kinematics(nucleon_packet_path)

    binding = -ground
    bound_count = int(np.count_nonzero(levels < 0.0))
    return DeuteronControlResult(
        interaction_id=interaction.interaction_id,
        n_points=int(n_points),
        r_max_fm=float(r_max_fm),
        dr_fm=dr,
        ground_state_energy_mev=ground,
        binding_energy_mev=binding,
        second_level_energy_mev=second,
        bound_state_count_in_sample=bound_count,
        relative_coordinate_rms_fm=relative_rms,
        single_nucleon_about_com_rms_fm=single_nucleon_rms,
        reference_binding_energy_mev=interaction.reference_binding_energy_mev,
        binding_residual_mev=binding - interaction.reference_binding_energy_mev,
        reference_single_nucleon_rms_fm=interaction.reference_single_nucleon_rms_fm,
        single_nucleon_rms_residual_fm=(
            single_nucleon_rms - interaction.reference_single_nucleon_rms_fm
        ),
        physical_pn_reduced_mass_mev=mu,
        physical_hbar2_over_2mu_mev_fm2=physical_coefficient,
        model_hbar2_over_m_mev_fm2=interaction.hbar2_over_m_mev_fm2,
    )
