"""Structured smoke-test of the exact pinned v0.14A molecular backend.

This file does not change the frozen method.  It only decomposes backend
compatibility into explicit provenance-preserving steps and writes a JSON
receipt even when one step fails.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
from math import isfinite
from pathlib import Path
import platform
import sys
import traceback

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reschem.molecular_state_relaxation import METHOD_POLICY, _configure_rks

OUT = ROOT / "benchmarks" / "MOLECULAR_BACKEND_SMOKE_V0_14A.json"


def _jsonable_summary(value):
    """Return a compact JSON-safe provenance summary without changing execution."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (list, tuple)):
        return [_jsonable_summary(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable_summary(item) for key, item in value.items()}
    module_name = getattr(value, "__name__", None)
    module_version = getattr(value, "__version__", None)
    if module_name is not None:
        return {"module": str(module_name), "version": None if module_version is None else str(module_version)}
    return repr(value)


def _step(name, fn, steps):
    try:
        value = fn()
        steps.append({"step": name, "status": "PASS", "value": _jsonable_summary(value)})
        return value
    except Exception as exc:
        steps.append({
            "step": name,
            "status": "FAIL",
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "traceback_tail": traceback.format_exc().splitlines()[-12:],
        })
        raise


def _case(atom: str, label: str, steps: list[dict]) -> dict:
    import numpy as np
    from pyscf import gto

    mol = _step(
        f"{label}:build_molecule_and_basis",
        lambda: gto.M(
            atom=atom,
            basis=METHOD_POLICY["basis"],
            unit="Angstrom",
            charge=0,
            spin=0,
            symmetry=False,
            verbose=2,
        ),
        steps,
    )
    mf = _step(f"{label}:configure_rks", lambda: _configure_rks(mol), steps)
    energy = _step(f"{label}:scf_kernel", lambda: float(mf.kernel()), steps)
    if not mf.converged or not isfinite(energy):
        raise RuntimeError(f"{label} SCF did not converge to a finite energy")
    gradient = _step(
        f"{label}:analytic_gradient",
        lambda: np.asarray(mf.nuc_grad_method().kernel(), dtype=float),
        steps,
    )
    if not np.all(np.isfinite(gradient)):
        raise RuntimeError(f"{label} analytic gradient contains non-finite values")
    return {
        "label": label,
        "basis_functions": int(mol.nao_nr()),
        "energy_hartree": energy,
        "scf_converged": bool(mf.converged),
        "energy_finite": isfinite(energy),
        "gradient_finite": True,
        "gradient_shape": list(gradient.shape),
    }


def main() -> int:
    steps: list[dict] = []
    cases: list[dict] = []
    software = {"python": platform.python_version(), "pyscf": None, "geometric": None}
    overall = "FAIL"

    try:
        pyscf = _step("import_pyscf", lambda: __import__("pyscf"), steps)
        geometric = _step("import_geometric", lambda: __import__("geometric"), steps)
        software["pyscf"] = getattr(pyscf, "__version__", "UNKNOWN")
        software["geometric"] = getattr(geometric, "__version__", "UNKNOWN")

        _step(
            "verify_pyscf_version",
            lambda: software["pyscf"] if software["pyscf"] == "2.14.0" else (_ for _ in ()).throw(RuntimeError(f"unexpected PySCF version {software['pyscf']}")),
            steps,
        )
        _step(
            "verify_geometric_version",
            lambda: software["geometric"] if software["geometric"] == "1.1.1" else (_ for _ in ()).throw(RuntimeError(f"unexpected geomeTRIC version {software['geometric']}")),
            steps,
        )

        cases.append(_case("F 0 0 -0.7; F 0 0 0.7", "F2", steps))
        cases.append(_case("Kr 0 0 0; F 0 0 -1.9; F 0 0 1.9", "KrF2", steps))
        overall = "PASS"
    except Exception:
        pass

    payload = {
        "schema": "RESCHEM_MOLECULAR_BACKEND_SMOKE_V0_14A",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": overall,
        "software": software,
        "method_policy": METHOD_POLICY,
        "steps": steps,
        "cases": cases,
        "nonclaim": "structured smoke diagnoses backend compatibility only; it does not alter or validate the frozen molecular screening method",
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0 if overall == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
