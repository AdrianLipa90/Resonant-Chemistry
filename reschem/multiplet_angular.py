from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
from math import factorial, pi, sqrt

import numpy as np

_TERM_LETTERS = "SPDFGHIKLMNOQRTUVWXYZ"


@dataclass(frozen=True)
class AngularTerm:
    energy_units: float
    L: int
    S: float
    degeneracy: int

    @property
    def multiplicity(self) -> int:
        return int(round(2.0 * self.S + 1.0))

    @property
    def symbol(self) -> str:
        return f"^{self.multiplicity}{_TERM_LETTERS[self.L]}"

    def as_dict(self) -> dict:
        return {
            "term": self.symbol,
            "L": self.L,
            "S": self.S,
            "multiplicity": self.multiplicity,
            "degeneracy": self.degeneracy,
            "energy_units": self.energy_units,
        }


@dataclass(frozen=True)
class ShellMultipletResult:
    l: int
    electron_count: int
    slater_parameters: dict[int, float]
    terms: tuple[AngularTerm, ...]

    @property
    def ground_term(self) -> AngularTerm:
        return self.terms[0]

    @property
    def microstate_count(self) -> int:
        return sum(term.degeneracy for term in self.terms)

    def as_dict(self) -> dict:
        return {
            "schema": "RESCHEM_ANGULAR_MULTIPLET_V0_1",
            "l": self.l,
            "electron_count": self.electron_count,
            "slater_parameters": {str(k): v for k, v in self.slater_parameters.items()},
            "microstate_count": self.microstate_count,
            "ground_term": self.ground_term.symbol,
            "terms": [term.as_dict() for term in self.terms],
            "scope": "electrostatic LS angular shell algebra; no spin-orbit J splitting",
            "tir_status": "NOT_APPLIED_CONTROL_BASELINE",
            "affective_status": "NOT_APPLIED_CONTROL_BASELINE",
        }


def _wigner_3j_int(j1: int, j2: int, j3: int, m1: int, m2: int, m3: int) -> float:
    """Integer-angular-momentum Wigner 3j via the Racah factorial formula."""
    if m1 + m2 + m3 != 0:
        return 0.0
    if any(abs(m) > j for m, j in ((m1, j1), (m2, j2), (m3, j3))):
        return 0.0
    if j3 < abs(j1 - j2) or j3 > j1 + j2:
        return 0.0

    delta = (
        factorial(j1 + j2 - j3)
        * factorial(j1 - j2 + j3)
        * factorial(-j1 + j2 + j3)
        / factorial(j1 + j2 + j3 + 1)
    )
    prefactor = (-1) ** (j1 - j2 - m3) * sqrt(delta)
    prefactor *= sqrt(
        factorial(j1 + m1)
        * factorial(j1 - m1)
        * factorial(j2 + m2)
        * factorial(j2 - m2)
        * factorial(j3 + m3)
        * factorial(j3 - m3)
    )

    z_min = max(0, j2 - j3 - m1, j1 - j3 + m2)
    z_max = min(j1 + j2 - j3, j1 - m1, j2 + m2)
    series = 0.0
    for z in range(z_min, z_max + 1):
        denominator = (
            factorial(z)
            * factorial(j1 + j2 - j3 - z)
            * factorial(j1 - m1 - z)
            * factorial(j2 + m2 - z)
            * factorial(j3 - j2 + m1 + z)
            * factorial(j3 - j1 - m2 + z)
        )
        series += (-1) ** z / denominator
    return prefactor * series


@lru_cache(maxsize=None)
def _angular_coulomb_coefficient(
    l: int,
    m1: int,
    m2: int,
    m3: int,
    m4: int,
    multipole_k: int,
) -> float:
    prefactor = sqrt((2 * l + 1) ** 2 * (2 * multipole_k + 1) / (4.0 * pi))
    zero_symbol = _wigner_3j_int(l, multipole_k, l, 0, 0, 0)
    if abs(zero_symbol) < 1.0e-15:
        return 0.0

    total = 0.0
    for q in range(-multipole_k, multipole_k + 1):
        first = (
            (-1) ** (m1 + q)
            * prefactor
            * zero_symbol
            * _wigner_3j_int(l, multipole_k, l, -m1, -q, m3)
        )
        second = (
            (-1) ** m2
            * prefactor
            * zero_symbol
            * _wigner_3j_int(l, multipole_k, l, -m2, q, m4)
        )
        total += (4.0 * pi / (2 * multipole_k + 1)) * first * second
    return total


def _spin_orbitals(l: int) -> tuple[tuple[int, int], ...]:
    return tuple((m, spin2) for m in range(-l, l + 1) for spin2 in (-1, 1))


def _determinant_basis(n_orbitals: int, electron_count: int) -> tuple[int, ...]:
    return tuple(
        sum(1 << orbital for orbital in occupied)
        for occupied in combinations(range(n_orbitals), electron_count)
    )


def _fermion_sign_before(bitstring: int, orbital: int) -> int:
    return -1 if (bitstring & ((1 << orbital) - 1)).bit_count() % 2 else 1


def _annihilate(bitstring: int, orbital: int):
    if not ((bitstring >> orbital) & 1):
        return None
    return bitstring ^ (1 << orbital), _fermion_sign_before(bitstring, orbital)


def _create(bitstring: int, orbital: int):
    if (bitstring >> orbital) & 1:
        return None
    return bitstring | (1 << orbital), _fermion_sign_before(bitstring, orbital)


def _apply_one_body(bitstring: int, p: int, q: int):
    first = _annihilate(bitstring, q)
    if first is None:
        return None
    state, sign = first
    second = _create(state, p)
    if second is None:
        return None
    state, sign2 = second
    return state, sign * sign2


def _apply_two_body(bitstring: int, p: int, q: int, r: int, s: int):
    operations = (("ann", r), ("ann", s), ("cre", q), ("cre", p))
    state = bitstring
    sign = 1
    for operation, orbital in operations:
        result = _annihilate(state, orbital) if operation == "ann" else _create(state, orbital)
        if result is None:
            return None
        state, local_sign = result
        sign *= local_sign
    return state, sign


def _one_body_many_body_matrix(one_body: np.ndarray, electron_count: int) -> np.ndarray:
    basis = _determinant_basis(one_body.shape[0], electron_count)
    lookup = {state: index for index, state in enumerate(basis)}
    matrix = np.zeros((len(basis), len(basis)), dtype=float)
    nonzero = np.argwhere(np.abs(one_body) > 1.0e-14)
    for p, q in nonzero:
        value = float(one_body[p, q])
        for column, state in enumerate(basis):
            applied = _apply_one_body(state, int(p), int(q))
            if applied is None:
                continue
            target, sign = applied
            matrix[lookup[target], column] += value * sign
    return matrix


def _two_body_shell_hamiltonian(
    l: int,
    electron_count: int,
    slater_parameters: dict[int, float],
) -> np.ndarray:
    spin_orbitals = _spin_orbitals(l)
    basis = _determinant_basis(len(spin_orbitals), electron_count)
    lookup = {state: index for index, state in enumerate(basis)}
    matrix = np.zeros((len(basis), len(basis)), dtype=float)

    spatial_cache: dict[tuple[int, int, int, int], float] = {}
    for m1 in range(-l, l + 1):
        for m2 in range(-l, l + 1):
            for m3 in range(-l, l + 1):
                for m4 in range(-l, l + 1):
                    spatial_cache[(m1, m2, m3, m4)] = sum(
                        value
                        * _angular_coulomb_coefficient(l, m1, m2, m3, m4, multipole_k)
                        for multipole_k, value in slater_parameters.items()
                    )

    for p, (m1, spin1) in enumerate(spin_orbitals):
        for q, (m2, spin2) in enumerate(spin_orbitals):
            for r, (m3, spin3) in enumerate(spin_orbitals):
                if spin1 != spin3:
                    continue
                for s, (m4, spin4) in enumerate(spin_orbitals):
                    if spin2 != spin4:
                        continue
                    integral = spatial_cache[(m1, m2, m3, m4)]
                    if abs(integral) < 1.0e-14:
                        continue
                    for column, state in enumerate(basis):
                        applied = _apply_two_body(state, p, q, r, s)
                        if applied is None:
                            continue
                        target, sign = applied
                        matrix[lookup[target], column] += 0.5 * integral * sign

    return 0.5 * (matrix + matrix.T)


def _ls_squared_matrices(l: int, electron_count: int) -> tuple[np.ndarray, np.ndarray]:
    spin_orbitals = _spin_orbitals(l)
    lookup = {orbital: index for index, orbital in enumerate(spin_orbitals)}
    size = len(spin_orbitals)

    lz = np.zeros((size, size), dtype=float)
    lplus = np.zeros_like(lz)
    lminus = np.zeros_like(lz)
    sz = np.zeros_like(lz)
    splus = np.zeros_like(lz)
    sminus = np.zeros_like(lz)

    for index, (m, spin2) in enumerate(spin_orbitals):
        lz[index, index] = m
        sz[index, index] = spin2 / 2.0
        if m < l:
            lplus[lookup[(m + 1, spin2)], index] = sqrt(l * (l + 1) - m * (m + 1))
        if m > -l:
            lminus[lookup[(m - 1, spin2)], index] = sqrt(l * (l + 1) - m * (m - 1))
        if spin2 == -1:
            splus[lookup[(m, 1)], index] = 1.0
        else:
            sminus[lookup[(m, -1)], index] = 1.0

    lz_mb = _one_body_many_body_matrix(lz, electron_count)
    lp_mb = _one_body_many_body_matrix(lplus, electron_count)
    lm_mb = _one_body_many_body_matrix(lminus, electron_count)
    sz_mb = _one_body_many_body_matrix(sz, electron_count)
    sp_mb = _one_body_many_body_matrix(splus, electron_count)
    sm_mb = _one_body_many_body_matrix(sminus, electron_count)

    l2 = lz_mb @ lz_mb + 0.5 * (lp_mb @ lm_mb + lm_mb @ lp_mb)
    s2 = sz_mb @ sz_mb + 0.5 * (sp_mb @ sm_mb + sm_mb @ sp_mb)
    return 0.5 * (l2 + l2.T), 0.5 * (s2 + s2.T)


def _quantum_number_from_casimir(value: float) -> float:
    return 0.5 * (-1.0 + sqrt(max(0.0, 1.0 + 4.0 * value)))


def solve_equivalent_shell_multiplets(
    l: int,
    electron_count: int,
    *,
    slater_parameters: dict[int, float] | None = None,
    degeneracy_tolerance: float = 1.0e-8,
) -> ShellMultipletResult:
    """Resolve LS terms for equivalent electrons in one l shell.

    Radial Slater integrals F^k are input coefficients.  With dimensionless
    choices this acts as a pure angular diagnostic.  No spin-orbit coupling is
    included, so J splitting remains outside this layer.
    """
    if l not in (0, 1, 2):
        raise ValueError("v0.1 supports s, p and d shells (l=0,1,2)")
    capacity = 2 * (2 * l + 1)
    if not (1 <= electron_count <= capacity):
        raise ValueError(f"electron_count must be in 1..{capacity}")

    if slater_parameters is None:
        if l == 0:
            slater_parameters = {0: 0.0}
        elif l == 1:
            slater_parameters = {0: 0.0, 2: 1.0}
        else:
            slater_parameters = {0: 0.0, 2: 1.0, 4: 0.625}
    slater_parameters = {int(k): float(v) for k, v in slater_parameters.items()}

    allowed_k = tuple(range(0, 2 * l + 1, 2))
    if any(k not in allowed_k for k in slater_parameters):
        raise ValueError(f"allowed multipoles for l={l} are {allowed_k}")

    hamiltonian = _two_body_shell_hamiltonian(l, electron_count, slater_parameters)
    l2, s2 = _ls_squared_matrices(l, electron_count)
    energies, eigenvectors = np.linalg.eigh(hamiltonian)

    terms: list[AngularTerm] = []
    start = 0
    while start < len(energies):
        stop = start + 1
        while stop < len(energies) and abs(energies[stop] - energies[start]) < degeneracy_tolerance:
            stop += 1

        energy_vectors = eigenvectors[:, start:stop]
        l_values, l_rotation = np.linalg.eigh(energy_vectors.T @ l2 @ energy_vectors)
        l_vectors = energy_vectors @ l_rotation

        l_start = 0
        while l_start < len(l_values):
            l_stop = l_start + 1
            while l_stop < len(l_values) and abs(l_values[l_stop] - l_values[l_start]) < 1.0e-7:
                l_stop += 1
            L = int(round(_quantum_number_from_casimir(float(l_values[l_start]))))
            fixed_l = l_vectors[:, l_start:l_stop]
            s_values = np.linalg.eigvalsh(fixed_l.T @ s2 @ fixed_l)

            s_start = 0
            while s_start < len(s_values):
                s_stop = s_start + 1
                while s_stop < len(s_values) and abs(s_values[s_stop] - s_values[s_start]) < 1.0e-7:
                    s_stop += 1
                S = _quantum_number_from_casimir(float(s_values[s_start]))
                terms.append(
                    AngularTerm(
                        energy_units=float(energies[start]),
                        L=L,
                        S=round(2.0 * S) / 2.0,
                        degeneracy=s_stop - s_start,
                    )
                )
                s_start = s_stop
            l_start = l_stop
        start = stop

    terms.sort(key=lambda term: (term.energy_units, term.L, term.S))
    return ShellMultipletResult(
        l=l,
        electron_count=electron_count,
        slater_parameters=slater_parameters,
        terms=tuple(terms),
    )


def p_shell_ground_terms() -> tuple[str, ...]:
    return tuple(solve_equivalent_shell_multiplets(1, n).ground_term.symbol for n in range(1, 7))


def d_shell_ground_terms() -> tuple[str, ...]:
    return tuple(solve_equivalent_shell_multiplets(2, n).ground_term.symbol for n in range(1, 11))
