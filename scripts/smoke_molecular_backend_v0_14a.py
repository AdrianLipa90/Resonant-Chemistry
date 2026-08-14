"""Smoke-test the exact pinned molecular backend before v0.14A relaxation."""
from __future__ import annotations

import json
from math import isfinite
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reschem.molecular_state_relaxation import METHOD_POLICY, _configure_rks


def run_case(atom: str, label: str) -> dict:
    import numpy as np
    from pyscf import gto

    mol = gto.M(
        atom=atom,
        basis=METHOD_POLICY["basis"],
        unit="Angstrom",
        charge=0,
        spin=0,
        symmetry=False,
        verbose=2,
    )
    mf = _configure_rks(mol)
    energy = float(mf.kernel())
    gradient = np.asarray(mf.nuc_grad_method().kernel(), dtype=float) if mf.converged else None
    return {
        "label": label,
        "basis_functions": int(mol.nao_nr()),
        "energy_hartree": energy,
        "scf_converged": bool(mf.converged),
        "energy_finite": isfinite(energy),
        "gradient_finite": bool(gradient is not None and np.all(np.isfinite(gradient))),
        "gradient_shape": None if gradient is None else list(gradient.shape),
    }


def main() -> int:
    import pyscf
    import geometric

    cases = [
        run_case("F 0 0 -0.7; F 0 0 0.7", "F2"),
        run_case("Kr 0 0 0; F 0 0 -1.9; F 0 0 1.9", "KrF2"),
    ]
    payload = {
        "schema": "RESCHEM_MOLECULAR_BACKEND_SMOKE_V0_14A",
        "software": {
            "python": platform.python_version(),
            "pyscf": getattr(pyscf, "__version__", "UNKNOWN"),
            "geometric": getattr(geometric, "__version__", "UNKNOWN"),
        },
        "method_policy": METHOD_POLICY,
        "cases": cases,
    }
    print(json.dumps(payload, indent=2))

    if payload["software"]["pyscf"] != "2.14.0":
        raise SystemExit(f"unexpected PySCF version: {payload['software']['pyscf']}")
    if payload["software"]["geometric"] != "1.1.1":
        raise SystemExit(f"unexpected geomeTRIC version: {payload['software']['geometric']}")
    if not all(x["scf_converged"] and x["energy_finite"] and x["gradient_finite"] for x in cases):
        raise SystemExit("frozen B97M-V/def2-TZVPD backend smoke failed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
