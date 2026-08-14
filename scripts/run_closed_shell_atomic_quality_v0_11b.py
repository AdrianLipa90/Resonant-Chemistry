"""Diagnose v0.11 atomic quality failures without changing the frozen solver."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reschem.atom import ELEMENT_SYMBOLS
from reschem.atomic_hf_diis import solve_atom_average_hf_robust

OUT = ROOT / "benchmarks" / "CLOSED_SHELL_ATOMIC_QUALITY_V0_11B.json"

# Exact unique atom/charge states consumed by v0.11. No extra control state is
# added after seeing the pair-level failure pattern.
STATES = (
    (10, 0), (10, +1),
    (18, 0), (18, +1),
    (36, 0), (36, +1),
    (9, 0), (9, -1),
    (17, 0), (17, -1),
    (35, 0), (35, -1),
)


def record(z: int, charge: int) -> dict:
    robust = solve_atom_average_hf_robust(z, charge)
    result = robust.result
    return {
        "Z": z,
        "symbol": ELEMENT_SYMBOLS[z],
        "charge": charge,
        "electron_count": result.electron_count,
        "configuration": result.configuration,
        "stage": robust.stage,
        "quality_pass": robust.quality_pass,
        "converged": result.converged,
        "iterations": result.iterations,
        "energy_hartree": result.energy_hartree,
        "virial_residual_hartree": result.virial_residual_hartree,
        "virial_abs_hartree": abs(result.virial_residual_hartree),
        "virial_gate_hartree": robust.virial_gate_hartree,
        "basis_size": result.basis_size,
        "grid_points": result.grid_points,
    }


def main() -> int:
    records = [record(z, charge) for z, charge in STATES]
    failed = [
        {"symbol": item["symbol"], "charge": item["charge"]}
        for item in records
        if not item["quality_pass"]
    ]
    payload = {
        "schema": "RESCHEM_CLOSED_SHELL_ATOMIC_QUALITY_V0_11B",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_execution": "benchmarks/CLOSED_SHELL_ATOMIC_CONTROL_V0_11_EXECUTION.json",
        "status": "DIAGNOSTIC_ONLY_NO_SOLVER_CHANGE",
        "states": records,
        "failed_states": failed,
        "anti_rescue": [
            "same solve_atom_average_hf_robust call and global stage ladder as v0.11",
            "no element-specific basis/grid/damping/virial changes",
            "no experimental energies substituted for failed states",
            "diagnostic output does not retroactively validate v0.11 descriptors",
        ],
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(OUT.relative_to(ROOT)), "failed_states": failed}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
