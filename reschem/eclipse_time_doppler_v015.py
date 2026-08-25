"""Frozen subjective-time and longitudinal Doppler transform for v0.15.

The transform preserves model-internal and observer-frame frequencies as
separate receipt fields. The subjective-time scale is supplied explicitly from
a provenance-bearing runtime/model source; this module does not infer it.
"""
from __future__ import annotations

from dataclasses import dataclass
import math


C_M_PER_S = 299_792_458.0
CONTRACT_ID = "RESCHEM_ECLIPSE_SUBJECTIVE_TIME_DOPPLER_V0_15_R1"
PNCS_SUBJECTIVE_TIME_REFERENCE = {
    "repository": "AdrianLipa90/PhaseNav-Natural-Coding-System",
    "commit": "5b866572f842407302acbb742df8a3955a0b8325",
    "path": "spec/PNCS_ORCHORBITAL_HYDRO_RUNTIME_V0_27.md",
    "relation": "d_tau = d_t * g_combined",
}
DOPPLER_SIGN_CONVENTION = "beta_radial_positive_receding"


def _finite(value: float, field: str) -> float:
    x = float(value)
    if not math.isfinite(x):
        raise ValueError(f"{field} must be finite")
    return x


def proper_eclipse_frequency_hz(harmonic_order: int, omega_proper_rad_s: float) -> float:
    """Return n*Omega_tau/(2*pi), where Omega_tau is measured per proper time."""
    if isinstance(harmonic_order, bool) or not isinstance(harmonic_order, int) or harmonic_order < 0:
        raise ValueError("harmonic_order must be a non-negative integer")
    omega = _finite(omega_proper_rad_s, "omega_proper_rad_s")
    if omega < 0.0:
        raise ValueError("omega_proper_rad_s must be non-negative")
    return harmonic_order * omega / (2.0 * math.pi)


def coordinate_frequency_hz(proper_frequency_hz: float, subjective_time_scale: float) -> float:
    """Map proper-time frequency to coordinate-time frequency for d_tau/d_t = g."""
    nu = _finite(proper_frequency_hz, "proper_frequency_hz")
    g = _finite(subjective_time_scale, "subjective_time_scale")
    if nu < 0.0:
        raise ValueError("proper_frequency_hz must be non-negative")
    if g <= 0.0:
        raise ValueError("subjective_time_scale must be positive")
    return g * nu


def longitudinal_doppler_factor(beta_radial: float) -> float:
    """Relativistic longitudinal factor; beta>0 denotes recession."""
    beta = _finite(beta_radial, "beta_radial")
    if not -1.0 < beta < 1.0:
        raise ValueError("beta_radial must lie strictly inside (-1, 1)")
    return math.sqrt((1.0 - beta) / (1.0 + beta))


@dataclass(frozen=True)
class EclipseObservationTransform:
    harmonic_order: int
    omega_proper_rad_s: float
    subjective_time_scale: float
    beta_radial: float
    proper_frequency_hz: float
    coordinate_frequency_hz: float
    doppler_factor: float
    observed_frequency_hz: float
    observed_wavelength_m: float | None
    status: str

    @property
    def payload(self) -> dict[str, object]:
        return {
            "schema": CONTRACT_ID,
            "harmonic_order": self.harmonic_order,
            "omega_proper_rad_s": self.omega_proper_rad_s,
            "subjective_time_scale": self.subjective_time_scale,
            "beta_radial": self.beta_radial,
            "doppler_sign_convention": DOPPLER_SIGN_CONVENTION,
            "proper_frequency_hz": self.proper_frequency_hz,
            "coordinate_frequency_hz": self.coordinate_frequency_hz,
            "doppler_factor": self.doppler_factor,
            "observed_frequency_hz": self.observed_frequency_hz,
            "observed_wavelength_m": self.observed_wavelength_m,
            "speed_of_light_m_s": C_M_PER_S,
            "transform_order": [
                "harmonic_and_proper_phase_rate",
                "subjective_time_scale",
                "longitudinal_relativistic_doppler",
                "observer_frequency_and_wavelength",
            ],
            "subjective_time_reference": dict(PNCS_SUBJECTIVE_TIME_REFERENCE),
            "status": self.status,
            "observed_spectrum_input": "WITHHELD",
        }


def transform_eclipse_observation(
    *,
    harmonic_order: int,
    omega_proper_rad_s: float,
    subjective_time_scale: float,
    beta_radial: float,
) -> EclipseObservationTransform:
    """Apply the frozen v0.15 ordering from proper phase to observer frame."""
    proper = proper_eclipse_frequency_hz(harmonic_order, omega_proper_rad_s)
    coordinate = coordinate_frequency_hz(proper, subjective_time_scale)
    doppler = longitudinal_doppler_factor(beta_radial)
    observed = coordinate * doppler
    wavelength = None if observed == 0.0 else C_M_PER_S / observed
    status = "STATIC_ZERO_FREQUENCY" if observed == 0.0 else "OBSERVER_FRAME_FREQUENCY_AVAILABLE"
    return EclipseObservationTransform(
        harmonic_order=harmonic_order,
        omega_proper_rad_s=float(omega_proper_rad_s),
        subjective_time_scale=float(subjective_time_scale),
        beta_radial=float(beta_radial),
        proper_frequency_hz=proper,
        coordinate_frequency_hz=coordinate,
        doppler_factor=doppler,
        observed_frequency_hz=observed,
        observed_wavelength_m=wavelength,
        status=status,
    )
