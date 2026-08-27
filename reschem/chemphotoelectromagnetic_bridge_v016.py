"""Chem-photo-electromagnetic spectroscopy bridge v0.16.

This module is an integration adapter between chemical state models, temporal
phase/correlation structure, and electromagnetic spectral observables.

The standard spectroscopy layer is kept explicit:
    hbar * omega_fi = E_f - E_i
    I_fi ~ p_i * |<f|mu|i>|^2

The Secret-of-a-Half / IDT half-interface kernel is exposed separately as an
interference/null diagnostic. Generic line positions remain set by admitted
energy differences.
"""

from __future__ import annotations

from dataclasses import dataclass
import cmath
import math
from typing import Iterable, Mapping, Sequence


class ChemPhotoEMError(ValueError):
    """Fail-closed validation error for the spectroscopy bridge."""


@dataclass(frozen=True)
class TransitionLine:
    initial: int
    final: int
    omega: float
    strength: float
    linewidth: float
    delta_energy: float


def _finite(x: float, name: str) -> float:
    x = float(x)
    if not math.isfinite(x):
        raise ChemPhotoEMError(f"{name} must be finite")
    return x


def half_interface_defect(sigma: float, delta_tau: float) -> float:
    """Exact two-channel cancellation defect.

    D = 1 + 2 sqrt(sigma(1-sigma)) cos(delta_tau/2)

    D=0 exactly at equal channel weight sigma=1/2 and a spinorial half-turn
    delta_tau = 2*pi (mod 4*pi).
    """
    sigma = _finite(sigma, "sigma")
    delta_tau = _finite(delta_tau, "delta_tau")
    if not 0.0 <= sigma <= 1.0:
        raise ChemPhotoEMError("sigma must lie in [0,1]")
    return 1.0 + 2.0 * math.sqrt(sigma * (1.0 - sigma)) * math.cos(delta_tau / 2.0)


def relational_zero(sigma: float, delta_tau: float, *, atol: float = 1e-12) -> bool:
    atol = _finite(atol, "atol")
    if atol < 0:
        raise ChemPhotoEMError("atol must be non-negative")
    return abs(half_interface_defect(sigma, delta_tau)) <= atol


def transition_angular_frequency(
    energy_initial: float,
    energy_final: float,
    *,
    hbar: float = 1.0,
) -> float:
    """Positive angular line frequency |E_f-E_i|/hbar."""
    ei = _finite(energy_initial, "energy_initial")
    ef = _finite(energy_final, "energy_final")
    hbar = _finite(hbar, "hbar")
    if hbar <= 0:
        raise ChemPhotoEMError("hbar must be positive")
    return abs(ef - ei) / hbar


def electric_dipole_strength(population_initial: float, dipole_matrix_element_sq: float) -> float:
    """Population-weighted electric-dipole line strength."""
    p = _finite(population_initial, "population_initial")
    mu2 = _finite(dipole_matrix_element_sq, "dipole_matrix_element_sq")
    if p < 0:
        raise ChemPhotoEMError("population_initial must be non-negative")
    if mu2 < 0:
        raise ChemPhotoEMError("dipole_matrix_element_sq must be non-negative")
    return p * mu2


def lorentzian(omega: float, center: float, linewidth: float) -> float:
    """Normalized Lorentzian with FWHM=linewidth."""
    omega = _finite(omega, "omega")
    center = _finite(center, "center")
    linewidth = _finite(linewidth, "linewidth")
    if linewidth <= 0:
        raise ChemPhotoEMError("linewidth must be positive")
    half = linewidth / 2.0
    return (half / math.pi) / ((omega - center) ** 2 + half**2)


def temporal_coherence(delta_tau: float, omega_fi: float, linewidth: float) -> complex:
    """Damped relative-phase correlation C_fi(delta_tau).

    C = exp[-Gamma |delta_tau| / 2] exp[-i omega_fi delta_tau]
    """
    dt = _finite(delta_tau, "delta_tau")
    w = _finite(omega_fi, "omega_fi")
    gamma = _finite(linewidth, "linewidth")
    if gamma < 0:
        raise ChemPhotoEMError("linewidth must be non-negative")
    return math.exp(-gamma * abs(dt) / 2.0) * cmath.exp(-1j * w * dt)


def build_transition_lines(
    energies: Sequence[float],
    couplings: Mapping[tuple[int, int], float],
    populations: Sequence[float],
    *,
    linewidth: float,
    hbar: float = 1.0,
) -> tuple[TransitionLine, ...]:
    """Build a spectral fingerprint from state energies and EM couplings.

    `couplings[(i,j)]` stores |<j|mu|i>|^2 or an admitted non-negative
    transition-coupling proxy. Energies and couplings enter through the admitted
    chemical-state layer; this function converts that state into line data.
    """
    es = tuple(_finite(e, f"energy[{i}]") for i, e in enumerate(energies))
    ps = tuple(_finite(p, f"population[{i}]") for i, p in enumerate(populations))
    if len(es) != len(ps):
        raise ChemPhotoEMError("energies and populations must have equal length")
    if len(es) < 2:
        raise ChemPhotoEMError("at least two states are required")
    if any(p < 0 for p in ps):
        raise ChemPhotoEMError("populations must be non-negative")
    linewidth = _finite(linewidth, "linewidth")
    hbar = _finite(hbar, "hbar")
    if linewidth <= 0:
        raise ChemPhotoEMError("linewidth must be positive")
    if hbar <= 0:
        raise ChemPhotoEMError("hbar must be positive")

    out: list[TransitionLine] = []
    n = len(es)
    for (i, j), mu2_raw in couplings.items():
        if not (0 <= i < n and 0 <= j < n) or i == j:
            raise ChemPhotoEMError(f"invalid transition index {(i, j)}")
        mu2 = _finite(mu2_raw, f"coupling[{i},{j}]")
        if mu2 < 0:
            raise ChemPhotoEMError("transition couplings must be non-negative")
        de = es[j] - es[i]
        omega = abs(de) / hbar
        strength = electric_dipole_strength(ps[i], mu2)
        out.append(TransitionLine(i, j, omega, strength, linewidth, de))
    out.sort(key=lambda line: (line.omega, line.initial, line.final))
    return tuple(out)


def spectrum(omega_grid: Iterable[float], lines: Sequence[TransitionLine]) -> tuple[float, ...]:
    """Sum admitted line profiles over an angular-frequency grid."""
    grid = tuple(_finite(w, "omega") for w in omega_grid)
    values = []
    for w in grid:
        s = 0.0
        for line in lines:
            if line.strength < 0 or line.linewidth <= 0:
                raise ChemPhotoEMError("invalid TransitionLine")
            s += line.strength * lorentzian(w, line.omega, line.linewidth)
        values.append(s)
    return tuple(values)


def fingerprint_signature(lines: Sequence[TransitionLine], *, ndigits: int = 12) -> tuple[tuple[float, float], ...]:
    """Deterministic comparison signature: (center, strength) pairs."""
    return tuple((round(line.omega, ndigits), round(line.strength, ndigits)) for line in lines)
