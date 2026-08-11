from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from scipy.linalg import eigh

from .atom import configuration_string, electron_configuration
from .atomic_hf_average import (
    AverageAtomicHFResult,
    _W3J_SQ,
    _analytic_radial_matrices,
    _direct_potential,
    _eval_slater_basis,
    _exchange_matrix,
    _local_matrix,
    _orthonormalize_columns,
    _radial_kernel_apply,
    _trap_weights,
    subshells_for_atom,
)


@dataclass
class _PulayHistory:
    max_size: int = 8
    focks: list[np.ndarray] | None = None
    errors: list[np.ndarray] | None = None

    def __post_init__(self) -> None:
        self.focks = [] if self.focks is None else self.focks
        self.errors = [] if self.errors is None else self.errors

    def push(self, fock: np.ndarray, error: np.ndarray) -> None:
        self.focks.append(fock.copy())
        self.errors.append(error.copy())
        if len(self.focks) > self.max_size:
            self.focks.pop(0)
            self.errors.pop(0)

    def extrapolate(self) -> np.ndarray:
        n = len(self.focks)
        if n < 2:
            return self.focks[-1]

        b = np.empty((n + 1, n + 1), dtype=float)
        b[-1, :-1] = -1.0
        b[:-1, -1] = -1.0
        b[-1, -1] = 0.0
        for i in range(n):
            for j in range(n):
                b[i, j] = float(np.vdot(self.errors[i], self.errors[j]).real)

        scale = max(1.0, float(np.max(np.abs(b[:-1, :-1]))))
        b[:-1, :-1] += np.eye(n) * (1.0e-12 * scale)
        rhs = np.zeros(n + 1)
        rhs[-1] = -1.0

        try:
            coefficients = np.linalg.solve(b, rhs)[:-1]
        except np.linalg.LinAlgError:
            return self.focks[-1]

        if (
            not np.all(np.isfinite(coefficients))
            or float(np.max(np.abs(coefficients))) > 25.0
        ):
            return self.focks[-1]

        out = np.zeros_like(self.focks[-1])
        for coefficient, fock in zip(coefficients, self.focks):
            out += coefficient * fock
        return 0.5 * (out + out.T)


def _commutator_error(
    fock: np.ndarray,
    overlap: np.ndarray,
    coefficients: np.ndarray,
    occupancies: np.ndarray,
) -> np.ndarray:
    density = coefficients @ np.diag(occupancies) @ coefficients.T
    return fock @ density @ overlap - overlap @ density @ fock


@dataclass(frozen=True)
class RobustAtomicHFResult:
    result: AverageAtomicHFResult
    stage: int
    quality_pass: bool
    virial_gate_hartree: float


_GLOBAL_STAGES = (
    {
        "basis_size": 16,
        "grid_points": 700,
        "damping": 0.12,
        "diis_start": 4,
        "diis_size": 6,
        "max_iterations": 350,
    },
    {
        "basis_size": 18,
        "grid_points": 800,
        "damping": 0.10,
        "diis_start": 8,
        "diis_size": 6,
        "max_iterations": 450,
    },
    {
        "basis_size": 20,
        "grid_points": 900,
        "damping": 0.10,
        "diis_start": 8,
        "diis_size": 6,
        "max_iterations": 600,
    },
    {
        "basis_size": 20,
        "grid_points": 1000,
        "damping": 0.08,
        "diis_start": 10,
        "diis_size": 6,
        "max_iterations": 700,
    },
)


def solve_atom_average_hf_diis(
    z: int,
    charge: int = 0,
    *,
    basis_size: int = 22,
    grid_points: int = 1400,
    zeta_min: float = 0.02,
    radial_grid_max_bohr: float = 120.0,
    damping: float = 0.25,
    diis_start: int = 3,
    diis_size: int = 7,
    max_iterations: int = 260,
    tolerance_hartree: float = 5e-8,
) -> AverageAtomicHFResult:
    """Average-of-configuration atomic HF with global Pulay/DIIS stabilization.

    The physical operator is the same control-layer operator as
    ``solve_atom_average_hf``.  Stabilization acts only on the SCF fixed-point
    iteration.  No element-specific branches, fitted reference energies, TIR
    corrections, or affective terms are used.
    """
    if basis_size < 12:
        raise ValueError("basis_size must be >= 12")
    if grid_points < 500:
        raise ValueError("grid_points must be >= 500")
    if zeta_min <= 0.0:
        raise ValueError("zeta_min must be positive")
    if radial_grid_max_bohr <= 0.0:
        raise ValueError("radial_grid_max_bohr must be positive")
    if not (0.0 < damping <= 1.0):
        raise ValueError("damping must be in (0,1]")
    if diis_start < 2 or diis_size < 2:
        raise ValueError("DIIS parameters must be >= 2")

    subshells = subshells_for_atom(z, charge)
    electron_count = sum(shell.occupancy for shell in subshells)
    if electron_count <= 0:
        raise ValueError("at least one electron is required")

    active_l = sorted({shell.l for shell in subshells})
    zetas = np.geomspace(zeta_min, max(20.0, 4.0 * z), basis_size)
    r = np.geomspace(1e-8, radial_grid_max_bohr, grid_points)
    weights = _trap_weights(r)

    overlap = {}
    kinetic = {}
    nuclear = {}
    one_body = {}
    basis = {}
    for l in active_l:
        overlap[l], kinetic[l], nuclear[l], one_body[l] = _analytic_radial_matrices(
            l, z, zetas
        )
        basis[l] = _eval_slater_basis(l, zetas, r)

    occupation = {}
    orbitals = {}
    for l in active_l:
        highest_index = max(
            shell.n - l - 1 for shell in subshells if shell.l == l
        )
        _, vectors = eigh(
            one_body[l],
            overlap[l],
            subset_by_index=[0, highest_index],
            check_finite=False,
        )
        for shell in subshells:
            if shell.l != l:
                continue
            index = shell.n - l - 1
            if shell.alpha_occupancy:
                key = (shell.n, l, "alpha")
                occupation[key] = shell.alpha_occupancy
                orbitals[key] = vectors[:, index].copy()
            if shell.beta_occupancy:
                key = (shell.n, l, "beta")
                occupation[key] = shell.beta_occupancy
                orbitals[key] = vectors[:, index].copy()

    def radial_orbital(key):
        return basis[key[1]] @ orbitals[key]

    def energy_components():
        density = np.zeros_like(r)
        cache = {}
        kinetic_energy = 0.0
        nuclear_energy = 0.0

        for key, count in occupation.items():
            u = radial_orbital(key)
            cache[key] = u
            density += count * u * u
            l = key[1]
            c = orbitals[key]
            kinetic_energy += count * float(c @ kinetic[l] @ c)
            nuclear_energy += count * float(c @ nuclear[l] @ c)

        direct_potential = _direct_potential(density, r)
        direct_energy = 0.5 * float(np.sum(weights * density * direct_potential))

        exchange_energy = 0.0
        for key_a, count_a in occupation.items():
            _, l_a, spin_a = key_a
            u_a = cache[key_a]
            for key_b, count_b in occupation.items():
                _, l_b, spin_b = key_b
                if spin_a != spin_b:
                    continue
                product = u_a * cache[key_b]
                for multipole_k, angular in _W3J_SQ[(l_a, l_b)].items():
                    transformed = _radial_kernel_apply(
                        product[:, None], r, multipole_k
                    )[:, 0]
                    exchange_energy -= (
                        0.5
                        * count_a
                        * count_b
                        * angular
                        * float(np.sum(weights * product * transformed))
                    )

        total = kinetic_energy + nuclear_energy + direct_energy + exchange_energy
        return total, kinetic_energy, nuclear_energy, direct_energy, exchange_energy

    histories = {}
    previous_used_fock = {}
    previous_energy = None
    converged = False

    for iteration in range(1, max_iterations + 1):
        density = np.zeros_like(r)
        orbital_cache = {}
        for key, count in occupation.items():
            u = radial_orbital(key)
            orbital_cache[key] = u
            density += count * u * u

        direct_potential = _direct_potential(density, r)
        updated = {}

        for l in active_l:
            direct_matrix = _local_matrix(basis[l], direct_potential, weights)
            for spin in ("alpha", "beta"):
                targets = sorted(
                    key for key in occupation if key[1] == l and key[2] == spin
                )
                if not targets:
                    continue

                exchange = np.zeros_like(one_body[l])
                for source_key, source_count in occupation.items():
                    _, source_l, source_spin = source_key
                    if source_spin != spin:
                        continue
                    source = orbital_cache[source_key]
                    for multipole_k, angular in _W3J_SQ[(l, source_l)].items():
                        exchange += source_count * angular * _exchange_matrix(
                            basis[l], source, r, weights, multipole_k
                        )

                raw_fock = one_body[l] + direct_matrix - exchange
                tag = (l, spin)
                current = np.column_stack([orbitals[key] for key in targets])
                occupancies = np.array(
                    [occupation[key] for key in targets], dtype=float
                )
                error = _commutator_error(
                    raw_fock, overlap[l], current, occupancies
                )

                history = histories.setdefault(tag, _PulayHistory(diis_size))
                history.push(raw_fock, error)

                if iteration >= diis_start and len(history.focks) >= 2:
                    used_fock = history.extrapolate()
                elif tag in previous_used_fock:
                    used_fock = (
                        (1.0 - damping) * previous_used_fock[tag]
                        + damping * raw_fock
                    )
                else:
                    used_fock = raw_fock
                previous_used_fock[tag] = used_fock

                highest_index = max(key[0] - l - 1 for key in targets)
                _, vectors = eigh(
                    used_fock,
                    overlap[l],
                    subset_by_index=[0, highest_index],
                    check_finite=False,
                )
                candidate = np.column_stack(
                    [vectors[:, key[0] - l - 1] for key in targets]
                )

                for column in range(candidate.shape[1]):
                    if (
                        float(
                            current[:, column]
                            @ overlap[l]
                            @ candidate[:, column]
                        )
                        < 0.0
                    ):
                        candidate[:, column] *= -1.0

                if iteration < diis_start:
                    candidate = _orthonormalize_columns(
                        (1.0 - damping) * current + damping * candidate,
                        overlap[l],
                    )
                else:
                    candidate = _orthonormalize_columns(candidate, overlap[l])

                for column, key in enumerate(targets):
                    updated[key] = candidate[:, column]

        orbitals.update(updated)
        total, _, _, _, _ = energy_components()
        if (
            previous_energy is not None
            and abs(total - previous_energy) < tolerance_hartree
        ):
            converged = True
            break
        previous_energy = total

    total, kinetic_energy, nuclear_energy, direct_energy, exchange_energy = (
        energy_components()
    )

    n_alpha = sum(
        count for key, count in occupation.items() if key[2] == "alpha"
    )
    n_beta = sum(
        count for key, count in occupation.items() if key[2] == "beta"
    )
    target_s = 0.5 * (n_alpha - n_beta)

    channels = []
    for shell in subshells:
        item = {
            "subshell": shell.label,
            "n": shell.n,
            "l": shell.l,
            "occupancy": shell.occupancy,
            "alpha_occupancy": shell.alpha_occupancy,
            "beta_occupancy": shell.beta_occupancy,
        }
        spin_channels = {}
        for spin in ("alpha", "beta"):
            key = (shell.n, shell.l, spin)
            if key not in orbitals:
                continue
            u = radial_orbital(key)
            mean_r = float(np.sum(weights * r * u * u))
            mean_r2 = float(np.sum(weights * r * r * u * u))
            spin_channels[spin] = {
                "mean_radius_bohr": mean_r,
                "radial_sigma_bohr": math.sqrt(
                    max(0.0, mean_r2 - mean_r * mean_r)
                ),
            }
        item["radial_channels"] = spin_channels
        channels.append(item)

    return AverageAtomicHFResult(
        z=z,
        charge=charge,
        electron_count=electron_count,
        configuration=configuration_string(electron_configuration(z, charge)),
        basis_size=basis_size,
        grid_points=grid_points,
        iterations=iteration,
        converged=converged,
        energy_hartree=total,
        kinetic_hartree=kinetic_energy,
        nuclear_attraction_hartree=nuclear_energy,
        direct_hartree=direct_energy,
        exchange_hartree=exchange_energy,
        virial_residual_hartree=(
            2.0 * kinetic_energy
            + nuclear_energy
            + direct_energy
            + exchange_energy
        ),
        target_s=target_s,
        target_s2=target_s * (target_s + 1.0),
        channel_summary=tuple(channels),
    )


def solve_atom_average_hf_robust(
    z: int,
    charge: int = 0,
    *,
    virial_gate_hartree: float = 2.0,
    tolerance_hartree: float = 1e-6,
) -> RobustAtomicHFResult:
    """Apply the same convergence/quality ladder to every atom.

    Escalation depends only on failed SCF/virial quality, never on element
    identity.  A large-virial false stationary point is therefore rejected
    even if the energy iteration itself appears converged.
    """
    if virial_gate_hartree <= 0.0:
        raise ValueError("virial_gate_hartree must be positive")

    last = None
    for stage, parameters in enumerate(_GLOBAL_STAGES, start=1):
        last = solve_atom_average_hf_diis(
            z,
            charge,
            tolerance_hartree=tolerance_hartree,
            **parameters,
        )
        quality_pass = (
            last.converged
            and math.isfinite(last.energy_hartree)
            and abs(last.virial_residual_hartree) < virial_gate_hartree
        )
        if quality_pass:
            return RobustAtomicHFResult(
                result=last,
                stage=stage,
                quality_pass=True,
                virial_gate_hartree=virial_gate_hartree,
            )

    return RobustAtomicHFResult(
        result=last,
        stage=len(_GLOBAL_STAGES),
        quality_pass=False,
        virial_gate_hartree=virial_gate_hartree,
    )


def solve_na_to_ar_stabilized(**kwargs):
    return tuple(
        solve_atom_average_hf_diis(z, **kwargs)
        for z in range(11, 19)
    )
