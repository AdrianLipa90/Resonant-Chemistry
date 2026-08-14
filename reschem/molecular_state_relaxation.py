"""Common conventional relaxation screen for v0.13 competing molecular states.

The pure seed/descriptor helpers have no PySCF dependency and are covered by the
normal repository test suite.  The optional runtime function imports pinned
PySCF/geomeTRIC only when the dedicated v0.14A workflow executes.

v0.14A is deliberately a relaxation screen, not a local-minimum or electronic-
topology admission result: no Hessian is run and geometry alone never assigns
3c4e versus van-der-Waals topology.

Numerical amendment v0.14A1 replaces the preregistered SG-1 pruning on the NLC
grid with PySCF's general-purpose NWChem pruning on both DFT grids.  The change
is global for every dimer and XY2 seed and was made after backend smoke failure
but before any molecular relaxation-screen output was admitted.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import acos, degrees, isfinite, sqrt
from typing import Iterable

METHOD_POLICY = {
    "xc": "b97m_v",
    "nlc": "vv10",
    "basis": "def2-tzvpd",
    "charge": 0,
    "spin": 0,
    "scf_conv_tol_hartree": 1.0e-10,
    "scf_max_cycle": 200,
    "grid_atom": (99, 590),
    "grid_prune": "nwchem_prune",
    "nlc_grid_atom": (50, 194),
    "nlc_grid_prune": "nwchem_prune",
    "optimizer_maxsteps": 120,
    "convergence_energy_hartree": 1.0e-6,
    "convergence_grms_hartree_per_bohr": 3.0e-4,
    "convergence_gmax_hartree_per_bohr": 4.5e-4,
    "convergence_drms_angstrom": 1.2e-3,
    "convergence_dmax_angstrom": 1.8e-3,
}

ACTIVATED_SCALES = (1.0, 1.3, 1.6)
WEAK_COMPLEX_SCALE = 1.8
DIMER_INITIAL_DISTANCE_ANGSTROM = 2.0
HARTREE_TO_KCAL_MOL = 627.5094740631


@dataclass(frozen=True)
class MolecularSeed:
    seed_id: str
    formula: str
    state_kind: str
    atoms: tuple[str, ...]
    coordinates_angstrom: tuple[tuple[float, float, float], ...]
    source_rule: str

    def __post_init__(self) -> None:
        if len(self.atoms) != len(self.coordinates_angstrom):
            raise ValueError("atoms/coordinates length mismatch")
        if len(self.atoms) < 2:
            raise ValueError("molecular seed requires at least two atoms")
        if not self.seed_id or not self.formula or not self.state_kind:
            raise ValueError("seed metadata must be non-empty")

    def to_dict(self) -> dict:
        data = asdict(self)
        data["coordinates_angstrom"] = [list(x) for x in self.coordinates_angstrom]
        return data


def ligand_dimer_seed(ligand_symbol: str) -> MolecularSeed:
    if not ligand_symbol:
        raise ValueError("ligand symbol must be non-empty")
    r = DIMER_INITIAL_DISTANCE_ANGSTROM
    return MolecularSeed(
        seed_id=f"{ligand_symbol}2_common_2p0A",
        formula=f"{ligand_symbol}2",
        state_kind="LIGAND_DIMER_PREPASS",
        atoms=(ligand_symbol, ligand_symbol),
        coordinates_angstrom=((0.0, 0.0, -0.5 * r), (0.0, 0.0, 0.5 * r)),
        source_rule="COMMON_INITIAL_DIMER_DISTANCE_2.0_ANGSTROM",
    )


def xy2_seed_geometries(
    centre_symbol: str,
    ligand_symbol: str,
    r_yy_angstrom: float,
) -> tuple[MolecularSeed, ...]:
    """Generate the frozen five numerical starts for one XY2 composition."""
    ryy = float(r_yy_angstrom)
    if not isfinite(ryy) or ryy <= 0.0:
        raise ValueError("r_yy_angstrom must be positive and finite")
    if not centre_symbol or not ligand_symbol:
        raise ValueError("element symbols must be non-empty")

    formula = f"{centre_symbol}{ligand_symbol}2"
    seeds: list[MolecularSeed] = []

    for scale in ACTIVATED_SCALES:
        rxy = scale * ryy
        scale_tag = str(scale).replace(".", "p")
        seeds.append(
            MolecularSeed(
                seed_id=f"{formula}_activated_s{scale_tag}",
                formula=formula,
                state_kind="ACTIVATED_LINEAR_3C4E",
                atoms=(centre_symbol, ligand_symbol, ligand_symbol),
                coordinates_angstrom=(
                    (0.0, 0.0, 0.0),
                    (0.0, 0.0, -rxy),
                    (0.0, 0.0, rxy),
                ),
                source_rule=f"R_XY={scale}*R_YY_FROM_COMMON_DIMER_PREPASS",
            )
        )

    separation = WEAK_COMPLEX_SCALE * ryy
    seeds.append(
        MolecularSeed(
            seed_id=f"{formula}_weak_linear",
            formula=formula,
            state_kind="WEAK_COMPLEX_LINEAR_END_ON",
            atoms=(centre_symbol, ligand_symbol, ligand_symbol),
            coordinates_angstrom=(
                (0.0, 0.0, -separation),
                (0.0, 0.0, 0.0),
                (0.0, 0.0, ryy),
            ),
            source_rule="R_X_TO_NEAR_Y=1.8*R_YY_FROM_COMMON_DIMER_PREPASS",
        )
    )
    seeds.append(
        MolecularSeed(
            seed_id=f"{formula}_weak_t",
            formula=formula,
            state_kind="WEAK_COMPLEX_T_SHAPED",
            atoms=(centre_symbol, ligand_symbol, ligand_symbol),
            coordinates_angstrom=(
                (separation, 0.0, 0.0),
                (0.0, 0.0, -0.5 * ryy),
                (0.0, 0.0, 0.5 * ryy),
            ),
            source_rule="R_X_TO_YY_MIDPOINT=1.8*R_YY_FROM_COMMON_DIMER_PREPASS",
        )
    )
    return tuple(seeds)


def _distance(a: Iterable[float], b: Iterable[float]) -> float:
    av = tuple(float(x) for x in a)
    bv = tuple(float(x) for x in b)
    return sqrt(sum((x - y) ** 2 for x, y in zip(av, bv)))


def xy2_geometry_descriptors(coordinates_angstrom: Iterable[Iterable[float]]) -> dict:
    """Return raw geometry descriptors for atom order X,Y1,Y2."""
    coords = tuple(tuple(float(v) for v in row) for row in coordinates_angstrom)
    if len(coords) != 3 or any(len(row) != 3 for row in coords):
        raise ValueError("XY2 descriptor expects three Cartesian 3-vectors")
    x, y1, y2 = coords
    d1 = _distance(x, y1)
    d2 = _distance(x, y2)
    dyy = _distance(y1, y2)
    if d1 <= 0.0 or d2 <= 0.0 or dyy <= 0.0:
        raise ValueError("coincident atoms are invalid")

    v1 = tuple(a - b for a, b in zip(y1, x))
    v2 = tuple(a - b for a, b in zip(y2, x))
    dot = sum(a * b for a, b in zip(v1, v2))
    cosine = max(-1.0, min(1.0, dot / (d1 * d2)))
    angle = degrees(acos(cosine))

    midpoint = tuple(0.5 * (a + b) for a, b in zip(y1, y2))
    x_to_mid = _distance(x, midpoint)
    return {
        "X_Y1_angstrom": d1,
        "X_Y2_angstrom": d2,
        "Y_Y_angstrom": dyy,
        "Y_X_Y_angle_degrees": angle,
        "X_to_YY_midpoint_angstrom": x_to_mid,
    }


def dimer_bond_length_angstrom(coordinates_angstrom: Iterable[Iterable[float]]) -> float:
    coords = tuple(tuple(float(v) for v in row) for row in coordinates_angstrom)
    if len(coords) != 2 or any(len(row) != 3 for row in coords):
        raise ValueError("dimer descriptor expects two Cartesian 3-vectors")
    return _distance(coords[0], coords[1])


def _atom_string(seed: MolecularSeed) -> str:
    return "; ".join(
        f"{symbol} {xyz[0]:.16f} {xyz[1]:.16f} {xyz[2]:.16f}"
        for symbol, xyz in zip(seed.atoms, seed.coordinates_angstrom)
    )


def _configure_rks(mol):
    """Create one PySCF RKS object under the amended global v0.14A1 policy."""
    from pyscf import dft

    prune_map = {
        "nwchem_prune": dft.gen_grid.nwchem_prune,
        "treutler_prune": dft.gen_grid.treutler_prune,
        "none": None,
    }
    try:
        grid_prune = prune_map[METHOD_POLICY["grid_prune"]]
        nlc_grid_prune = prune_map[METHOD_POLICY["nlc_grid_prune"]]
    except KeyError as exc:
        raise ValueError(f"unsupported frozen grid pruning policy: {exc.args[0]}") from exc

    mf = dft.RKS(mol)
    mf.xc = METHOD_POLICY["xc"]
    mf.nlc = METHOD_POLICY["nlc"]
    mf.conv_tol = METHOD_POLICY["scf_conv_tol_hartree"]
    mf.max_cycle = METHOD_POLICY["scf_max_cycle"]
    mf.grids.atom_grid = METHOD_POLICY["grid_atom"]
    mf.grids.prune = grid_prune
    mf.nlcgrids.atom_grid = METHOD_POLICY["nlc_grid_atom"]
    mf.nlcgrids.prune = nlc_grid_prune
    return mf


def run_pyscf_relaxation(seed: MolecularSeed) -> dict:
    """Execute one amended B97M-V/def2-TZVPD v0.14A1 relaxation.

    Scientific failure is returned as structured data.  No SCF or geometry
    rescue is attempted.
    """
    import platform
    import traceback
    import numpy as np
    import pyscf
    import geometric
    from pyscf import gto
    from pyscf.geomopt.geometric_solver import optimize

    result = {
        "seed": seed.to_dict(),
        "method_policy": dict(METHOD_POLICY),
        "software": {
            "python": platform.python_version(),
            "pyscf": getattr(pyscf, "__version__", "UNKNOWN"),
            "geometric": getattr(geometric, "__version__", "UNKNOWN"),
        },
        "status": "STARTED",
        "initial_scf_converged": False,
        "initial_energy_hartree": None,
        "optimizer_returned": False,
        "final_scf_converged": False,
        "final_energy_hartree": None,
        "final_coordinates_angstrom": None,
        "final_gradient_rms_hartree_per_bohr": None,
        "final_gradient_max_abs_hartree_per_bohr": None,
        "geometry_descriptors": None,
        "exception_type": None,
        "exception_message": None,
    }

    try:
        mol = gto.M(
            atom=_atom_string(seed),
            basis=METHOD_POLICY["basis"],
            unit="Angstrom",
            charge=METHOD_POLICY["charge"],
            spin=METHOD_POLICY["spin"],
            symmetry=False,
            verbose=3,
        )
        mf = _configure_rks(mol)
        initial_energy = float(mf.kernel())
        result["initial_energy_hartree"] = initial_energy
        result["initial_scf_converged"] = bool(mf.converged)
        if not mf.converged or not isfinite(initial_energy):
            result["status"] = "INITIAL_SCF_FAILED_NO_RESCUE"
            return result

        mol_eq = optimize(
            mf,
            maxsteps=METHOD_POLICY["optimizer_maxsteps"],
            convergence_energy=METHOD_POLICY["convergence_energy_hartree"],
            convergence_grms=METHOD_POLICY["convergence_grms_hartree_per_bohr"],
            convergence_gmax=METHOD_POLICY["convergence_gmax_hartree_per_bohr"],
            convergence_drms=METHOD_POLICY["convergence_drms_angstrom"],
            convergence_dmax=METHOD_POLICY["convergence_dmax_angstrom"],
        )
        result["optimizer_returned"] = True

        final_mf = _configure_rks(mol_eq)
        final_energy = float(final_mf.kernel())
        result["final_energy_hartree"] = final_energy
        result["final_scf_converged"] = bool(final_mf.converged)
        coords = np.asarray(mol_eq.atom_coords(unit="Angstrom"), dtype=float)
        result["final_coordinates_angstrom"] = coords.tolist()

        if final_mf.converged and isfinite(final_energy):
            gradient = np.asarray(final_mf.nuc_grad_method().kernel(), dtype=float)
            result["final_gradient_rms_hartree_per_bohr"] = float(np.sqrt(np.mean(gradient ** 2)))
            result["final_gradient_max_abs_hartree_per_bohr"] = float(np.max(np.abs(gradient)))
            if len(seed.atoms) == 3:
                result["geometry_descriptors"] = xy2_geometry_descriptors(coords)
            elif len(seed.atoms) == 2:
                result["geometry_descriptors"] = {
                    "Y_Y_angstrom": dimer_bond_length_angstrom(coords)
                }
            result["status"] = "RELAXATION_RETURNED_FINAL_SCF_CONVERGED_NO_HESSIAN"
        else:
            result["status"] = "OPTIMIZER_RETURNED_FINAL_SCF_FAILED"
        return result
    except Exception as exc:  # provenance-preserving failure receipt
        result["status"] = "RELAXATION_EXCEPTION"
        result["exception_type"] = type(exc).__name__
        result["exception_message"] = str(exc)
        result["exception_traceback_tail"] = traceback.format_exc().splitlines()[-12:]
        return result


def add_relative_energies(results: Iterable[dict]) -> list[dict]:
    """Attach within-formula electronic relative energies, without a threshold."""
    rows = [dict(row) for row in results]
    successful = [
        row for row in rows
        if row.get("status") == "RELAXATION_RETURNED_FINAL_SCF_CONVERGED_NO_HESSIAN"
        and row.get("final_energy_hartree") is not None
    ]
    if not successful:
        for row in rows:
            row["relative_energy_kcal_mol"] = None
        return rows
    e0 = min(float(row["final_energy_hartree"]) for row in successful)
    for row in rows:
        if row in successful:
            row["relative_energy_kcal_mol"] = (
                float(row["final_energy_hartree"]) - e0
            ) * HARTREE_TO_KCAL_MOL
        else:
            row["relative_energy_kcal_mol"] = None
    return rows
