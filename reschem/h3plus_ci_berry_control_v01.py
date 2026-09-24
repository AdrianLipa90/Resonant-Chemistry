from __future__ import annotations

import cmath
import math
from dataclasses import dataclass
from typing import Sequence

import numpy as np


class H3PlusCIBerryError(RuntimeError):
    pass


@dataclass
class FCIPoint:
    atoms_bohr: tuple[tuple[str, tuple[float, float, float]], ...]
    energies_hartree: np.ndarray
    ci_vectors: tuple[np.ndarray, ...]
    mo_coeff: np.ndarray
    mol: object
    nelec: tuple[int, int]


def h3plus_atoms_from_polar(
    *,
    R_bohr: float,
    rho_bohr: float,
    theta_rad: float,
) -> tuple[tuple[str, tuple[float, float, float]], ...]:
    R = float(R_bohr)
    rho = float(rho_bohr)
    theta = float(theta_rad)
    if not all(math.isfinite(x) for x in (R, rho, theta)):
        raise H3PlusCIBerryError("geometry parameters must be finite")
    if R <= 0.0 or rho <= 0.0:
        raise H3PlusCIBerryError("R and rho must be positive")
    return (
        ("H", (R, 0.0, 0.0)),
        ("H", (-R, 0.0, 0.0)),
        ("H", (rho * math.cos(theta), rho * math.sin(theta), 0.0)),
    )


def equilateral_reference(*, R_bohr: float = 2.0) -> tuple[float, float]:
    R = float(R_bohr)
    if not math.isfinite(R) or R <= 0.0:
        raise H3PlusCIBerryError("R must be finite and positive")
    return math.sqrt(3.0) * R, math.pi / 2.0


def frozen_loop_geometries(
    *,
    encircling: bool,
    samples: int = 24,
    R_bohr: float = 2.0,
    delta_rho_bohr: float = 0.15,
    delta_theta_rad: float = 0.05,
    nonencircling_rho_shift_bohr: float = 0.60,
) -> tuple[tuple[tuple[str, tuple[float, float, float]], ...], ...]:
    if not isinstance(samples, int) or samples < 6:
        raise H3PlusCIBerryError("samples must be an integer >= 6")
    rho0, theta0 = equilateral_reference(R_bohr=R_bohr)
    center_rho = rho0 if encircling else rho0 + float(nonencircling_rho_shift_bohr)
    dr = float(delta_rho_bohr)
    dt = float(delta_theta_rad)
    if not all(math.isfinite(x) for x in (center_rho, dr, dt)):
        raise H3PlusCIBerryError("loop parameters must be finite")
    if dr <= 0.0 or dt <= 0.0:
        raise H3PlusCIBerryError("loop radii must be positive")
    out = []
    for k in range(samples):
        phi = 2.0 * math.pi * k / samples
        rho = center_rho + dr * math.cos(phi)
        theta = theta0 + dt * math.sin(phi)
        out.append(
            h3plus_atoms_from_polar(
                R_bohr=R_bohr,
                rho_bohr=rho,
                theta_rad=theta,
            )
        )
    return tuple(out)


def _pyscf_modules():
    try:
        from pyscf import fci, gto, scf
    except Exception as exc:
        raise H3PlusCIBerryError(
            "PySCF is required for the H3+ molecular benchmark"
        ) from exc
    return fci, gto, scf


def fci_point(
    atoms_bohr,
    *,
    basis: str = "sto-3g",
    nroots: int = 3,
) -> FCIPoint:
    fci, gto, scf = _pyscf_modules()
    mol = gto.M(
        atom=list(atoms_bohr),
        unit="Bohr",
        basis=basis,
        charge=1,
        spin=0,
        symmetry=False,
        verbose=0,
    )
    mf = scf.RHF(mol)
    mf.conv_tol = 1e-12
    mf.max_cycle = 200
    mf.kernel()
    if not mf.converged:
        raise H3PlusCIBerryError("RHF did not converge")

    solver = fci.FCI(mf, singlet=True)
    solver.nroots = int(nroots)
    energies, vectors = solver.kernel()
    energies = np.asarray(energies, dtype=float).reshape(-1)
    if energies.size != nroots:
        raise H3PlusCIBerryError("unexpected FCI root count")
    if not np.all(np.isfinite(energies)):
        raise H3PlusCIBerryError("FCI energies must be finite")
    if not isinstance(vectors, (list, tuple)):
        vectors = [vectors]
    if len(vectors) != nroots:
        raise H3PlusCIBerryError("unexpected FCI vector count")
    ci_vectors = tuple(np.asarray(v, dtype=np.complex128) for v in vectors)
    return FCIPoint(
        atoms_bohr=tuple(atoms_bohr),
        energies_hartree=energies,
        ci_vectors=ci_vectors,
        mo_coeff=np.asarray(mf.mo_coeff, dtype=np.complex128),
        mol=mol,
        nelec=tuple(int(x) for x in mol.nelec),
    )


def fci_cross_overlap(
    left: FCIPoint,
    left_root: int,
    right: FCIPoint,
    right_root: int,
) -> complex:
    fci, gto, _ = _pyscf_modules()
    if left.mo_coeff.shape[1] != right.mo_coeff.shape[1]:
        raise H3PlusCIBerryError("orbital dimensions differ across geometries")
    if left.nelec != right.nelec:
        raise H3PlusCIBerryError("electron counts differ across geometries")
    s_ao = gto.intor_cross("int1e_ovlp", left.mol, right.mol)
    s_mo = left.mo_coeff.conjugate().T @ s_ao @ right.mo_coeff
    norb = left.mo_coeff.shape[1]
    value = fci.addons.overlap(
        left.ci_vectors[int(left_root)],
        right.ci_vectors[int(right_root)],
        norb,
        left.nelec,
        s=s_mo,
    )
    value = complex(value)
    if not (math.isfinite(value.real) and math.isfinite(value.imag)):
        raise H3PlusCIBerryError("FCI overlap must be finite")
    return value


def track_excited_loop(
    points: Sequence[FCIPoint],
    *,
    initial_root: int = 1,
    candidate_roots: tuple[int, ...] = (1, 2),
    min_overlap: float = 1e-8,
) -> dict:
    if len(points) < 6:
        raise H3PlusCIBerryError("loop requires at least six points")
    root = int(initial_root)
    roots = [root]
    links = []
    min_gap = math.inf

    for point in points:
        if point.energies_hartree.size < 3:
            raise H3PlusCIBerryError("three FCI roots are required")
        gap = float(point.energies_hartree[2] - point.energies_hartree[1])
        if not math.isfinite(gap) or gap <= 0.0:
            raise H3PlusCIBerryError("excited-state gap closed on sampled path")
        min_gap = min(min_gap, gap)

    for left, right in zip(points[:-1], points[1:]):
        candidates = [
            (candidate, fci_cross_overlap(left, root, right, candidate))
            for candidate in candidate_roots
        ]
        root_next, overlap = max(candidates, key=lambda item: abs(item[1]))
        if abs(overlap) <= min_overlap:
            raise H3PlusCIBerryError("adjacent tracked overlap is too small")
        links.append(overlap / abs(overlap))
        root = int(root_next)
        roots.append(root)

    closure = fci_cross_overlap(points[-1], roots[-1], points[0], roots[0])
    if abs(closure) <= min_overlap:
        raise H3PlusCIBerryError("closure overlap is too small")
    links.append(closure / abs(closure))

    wilson = 1.0 + 0.0j
    for link in links:
        wilson *= link
    wilson /= abs(wilson)

    return {
        "tracked_roots": roots,
        "link_overlaps": [
            {"real": float(z.real), "imag": float(z.imag), "abs": float(abs(z))}
            for z in links
        ],
        "wilson": {"real": float(wilson.real), "imag": float(wilson.imag)},
        "berry_phase_rad": float(cmath.phase(wilson)),
        "min_excited_gap_hartree": float(min_gap),
    }


def run_frozen_h3plus_protocol() -> dict:
    results = {}
    for label, encircling in (("encircling", True), ("non_encircling", False)):
        geometries = frozen_loop_geometries(encircling=encircling)
        points = tuple(fci_point(atoms) for atoms in geometries)
        results[label] = track_excited_loop(points)

    enc = results["encircling"]["wilson"]
    ctl = results["non_encircling"]["wilson"]
    passed = (
        abs(enc["imag"]) < 1e-6
        and abs(enc["real"] + 1.0) < 1e-4
        and abs(ctl["imag"]) < 1e-6
        and abs(ctl["real"] - 1.0) < 1e-4
    )
    return {
        "schema": "RESCHEM_H3PLUS_CI_BERRY_RESULT_V0_1",
        "status": "PASS" if passed else "FAIL",
        "protocol": {
            "R_bohr": 2.0,
            "basis": "STO-3G",
            "method": "RHF + singlet FCI",
            "samples": 24,
            "delta_rho_bohr": 0.15,
            "delta_theta_rad": 0.05,
            "nonencircling_rho_shift_bohr": 0.60,
            "tracking": "maximum absolute FCI overlap among roots 1,2",
        },
        "results": results,
        "interpretation": "STANDARD_QM_MOLECULAR_BERRY_CONTROL_ONLY",
    }
