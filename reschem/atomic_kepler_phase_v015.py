"""Zero-fit radial Kepler phase-rate control for Resonant Chemistry v0.15.

The phase rate is derived from the existing neutral B-Ne radial HF control state.
No observed spectral values are accepted by this module.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Sequence

import numpy as np
from scipy.integrate import cumulative_trapezoid

from .atomic_radial_spectroscopy import (
    HARTREE_TO_WAVENUMBER_CM,
    _pauli_central_zeta,
    _solve_period2_radial_state,
)

ATOMIC_TIME_SECOND = 2.4188843265864e-17
SPEED_OF_LIGHT_CM_PER_SECOND = 29979245800.0
PREREG_SCHEMA = "RESCHEM_POLYHEDRAL_ECLIPSE_STAGE_B_KEPLER_PHASE_PREREG_V0_15"
RECORD_SCHEMA = "RESCHEM_PERIOD2_RADIAL_KEPLER_PHASE_RATE_V0_15"


class AtomicKeplerPhaseV015Error(ValueError):
    pass


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256_json(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def radial_kepler_observables(
    z: int,
    *,
    r: Sequence[float],
    weights: Sequence[float],
    total_radial_density: Sequence[float],
    one_p_density: Sequence[float],
) -> dict[str, float]:
    zz = int(z)
    if zz <= 0:
        raise AtomicKeplerPhaseV015Error("Z must be positive")
    rr = np.asarray(r, dtype=float)
    ww = np.asarray(weights, dtype=float)
    total = np.asarray(total_radial_density, dtype=float)
    one_p = np.asarray(one_p_density, dtype=float)
    if rr.ndim != 1 or len(rr) < 16:
        raise AtomicKeplerPhaseV015Error("radial grid must be one-dimensional with at least 16 points")
    if ww.shape != rr.shape or total.shape != rr.shape or one_p.shape != rr.shape:
        raise AtomicKeplerPhaseV015Error("radial arrays must have identical shape")
    if np.any(~np.isfinite(rr)) or np.any(~np.isfinite(ww)) or np.any(~np.isfinite(total)) or np.any(~np.isfinite(one_p)):
        raise AtomicKeplerPhaseV015Error("radial arrays must be finite")
    if np.any(rr <= 0.0) or np.any(np.diff(rr) <= 0.0):
        raise AtomicKeplerPhaseV015Error("radial grid must be strictly increasing and positive")
    if np.any(ww < 0.0) or np.any(one_p < -1.0e-12):
        raise AtomicKeplerPhaseV015Error("radial weights/probability must be nonnegative")

    normalization = float(np.sum(ww * one_p))
    if abs(normalization - 1.0) > 1.0e-8:
        raise AtomicKeplerPhaseV015Error(f"one_p_density normalization drift: {normalization}")
    mean_radius = float(np.sum(ww * one_p * rr))
    if not math.isfinite(mean_radius) or mean_radius <= 0.0:
        raise AtomicKeplerPhaseV015Error("mean 2p radius must be positive and finite")

    other_density = total - one_p
    min_other = float(np.min(other_density))
    if min_other < -1.0e-8:
        total_charge = float(np.sum(ww * total))
        active_charge = float(np.sum(ww * one_p))
        integrated_negative_charge = float(np.sum(ww * np.maximum(-other_density, 0.0)))
        raise AtomicKeplerPhaseV015Error(
            "other-electron radial density became negative beyond tolerance: "
            f"min_other={min_other:.17g}, total_charge={total_charge:.17g}, "
            f"active_charge={active_charge:.17g}, "
            f"integrated_negative_charge={integrated_negative_charge:.17g}"
        )
    other_density = np.maximum(other_density, 0.0)
    enclosed_other = cumulative_trapezoid(other_density, rr, initial=0.0)
    q_other = float(np.interp(mean_radius, rr, enclosed_other))
    z_eff = float(zz) - q_other
    if not math.isfinite(z_eff) or z_eff <= 0.0:
        raise AtomicKeplerPhaseV015Error("effective charge at mean radius must be positive and finite")

    omega_au = math.sqrt(z_eff / (mean_radius**3))
    omega_rad_s = omega_au / ATOMIC_TIME_SECOND
    frequency_hz = omega_rad_s / (2.0 * math.pi)
    wavenumber_cm = frequency_hz / SPEED_OF_LIGHT_CM_PER_SECOND
    return {
        "mean_radius_bohr": mean_radius,
        "enclosed_other_charge_at_mean_radius": q_other,
        "effective_charge_at_mean_radius": z_eff,
        "kepler_angular_rate_atomic_units": omega_au,
        "kepler_angular_rate_rad_per_second": omega_rad_s,
        "kepler_frequency_hz": frequency_hz,
        "kepler_wavenumber_cm_inverse": wavenumber_cm,
    }


@dataclass(frozen=True)
class Period2KeplerPhaseRate:
    z: int
    mean_radius_bohr: float
    enclosed_other_charge_at_mean_radius: float
    effective_charge_at_mean_radius: float
    kepler_angular_rate_atomic_units: float
    kepler_angular_rate_rad_per_second: float
    kepler_frequency_hz: float
    kepler_wavenumber_cm_inverse: float
    zeta_2p_hartree: float
    zeta_2p_control_wavenumber_cm_inverse: float
    hf_energy_hartree: float
    virial_residual_hartree: float
    scf_iterations: int

    @property
    def payload(self) -> dict[str, object]:
        return {
            "schema": RECORD_SCHEMA,
            "prereg_schema": PREREG_SCHEMA,
            "Z": self.z,
            "mean_radius_bohr": self.mean_radius_bohr,
            "enclosed_other_charge_at_mean_radius": self.enclosed_other_charge_at_mean_radius,
            "effective_charge_at_mean_radius": self.effective_charge_at_mean_radius,
            "kepler_angular_rate_atomic_units": self.kepler_angular_rate_atomic_units,
            "kepler_angular_rate_rad_per_second": self.kepler_angular_rate_rad_per_second,
            "kepler_frequency_hz": self.kepler_frequency_hz,
            "kepler_wavenumber_cm_inverse": self.kepler_wavenumber_cm_inverse,
            "zeta_2p_hartree": self.zeta_2p_hartree,
            "zeta_2p_control_wavenumber_cm_inverse": self.zeta_2p_control_wavenumber_cm_inverse,
            "hf_energy_hartree": self.hf_energy_hartree,
            "virial_residual_hartree": self.virial_residual_hartree,
            "scf_iterations": self.scf_iterations,
            "constants": {
                "atomic_time_second": ATOMIC_TIME_SECOND,
                "speed_of_light_cm_per_second": SPEED_OF_LIGHT_CM_PER_SECOND,
                "hartree_to_wavenumber_cm_inverse": HARTREE_TO_WAVENUMBER_CM,
            },
            "fit_parameters": [],
            "observed_spectrum": "WITHHELD_FOR_BLIND_COMPARISON",
            "epistemic_operator": "CHYBA",
            "canon_allowed": False,
        }

    def as_dict(self) -> dict[str, object]:
        body = self.payload
        return {**body, "record_sha256": _sha256_json(body)}


def solve_period2_radial_kepler_phase(
    z: int,
    *,
    basis_size: int = 24,
    grid_points: int = 1500,
    mixing: float = 0.32,
    tolerance_hartree: float = 5.0e-8,
    max_iterations: int = 120,
) -> Period2KeplerPhaseRate:
    state = _solve_period2_radial_state(
        int(z),
        basis_size=basis_size,
        grid_points=grid_points,
        mixing=mixing,
        tolerance_hartree=tolerance_hartree,
        max_iterations=max_iterations,
    )
    observables = radial_kepler_observables(
        int(z),
        r=state["r"],
        weights=state["weights"],
        total_radial_density=state["density"],
        one_p_density=state["one_p_density"],
    )
    zeta = _pauli_central_zeta(
        int(z),
        state["density"],
        state["one_p_density"],
        state["r"],
        state["weights"],
    )
    return Period2KeplerPhaseRate(
        z=int(z),
        mean_radius_bohr=observables["mean_radius_bohr"],
        enclosed_other_charge_at_mean_radius=observables["enclosed_other_charge_at_mean_radius"],
        effective_charge_at_mean_radius=observables["effective_charge_at_mean_radius"],
        kepler_angular_rate_atomic_units=observables["kepler_angular_rate_atomic_units"],
        kepler_angular_rate_rad_per_second=observables["kepler_angular_rate_rad_per_second"],
        kepler_frequency_hz=observables["kepler_frequency_hz"],
        kepler_wavenumber_cm_inverse=observables["kepler_wavenumber_cm_inverse"],
        zeta_2p_hartree=float(zeta),
        zeta_2p_control_wavenumber_cm_inverse=float(zeta) * HARTREE_TO_WAVENUMBER_CM,
        hf_energy_hartree=float(state["energy_hartree"]),
        virial_residual_hartree=float(state["virial_residual_hartree"]),
        scf_iterations=int(state["iterations"]),
    )


def harmonic_frequency_candidate(phase: Period2KeplerPhaseRate, harmonic_order: int) -> dict[str, float | int]:
    order = int(harmonic_order)
    if order < 0:
        raise AtomicKeplerPhaseV015Error("harmonic order must be nonnegative")
    return {
        "harmonic_order": order,
        "frequency_hz": float(order) * phase.kepler_frequency_hz,
        "wavenumber_cm_inverse": float(order) * phase.kepler_wavenumber_cm_inverse,
    }
