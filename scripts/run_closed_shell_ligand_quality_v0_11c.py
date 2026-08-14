"""Targeted localization of the four unresolved v0.11 ligand-side states."""
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

OUT = ROOT / "benchmarks" / "CLOSED_SHELL_LIGAND_QUALITY_V0_11C.json"
STATES = ((9, 0), (9, -1), (35, 0), (35, -1))


def record(z: int, charge: int) -> dict:
    robust = solve_atom_average_hf_robust(z, charge)
    result = robust.result
    return {
        "Z": z,
        "symbol": ELEMENT_SYMBOLS[z],
        "charge": charge,
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
    by_label = {
        item["symbol"] + ("-" if item["charge"] == -1 else ""): item["quality_pass"]
        for item in records
    }
    payload = {
        "schema": "RESCHEM_CLOSED_SHELL_LIGAND_QUALITY_V0_11C",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "preregister_source": "benchmarks/CLOSED_SHELL_LIGAND_QUALITY_PREREG_V0_11C.json",
        "status": "TARGETED_DIAGNOSTIC_EXECUTED_NO_SOLVER_CHANGE",
        "states": records,
        "quality_map": by_label,
        "interpretation": {
            "F": "anion_only_failure" if by_label["F"] and not by_label["F-"] else ("neutral_only_failure" if not by_label["F"] and by_label["F-"] else ("both_failure" if not by_label["F"] and not by_label["F-"] else "both_pass_pair_receipt_inconsistency")),
            "Br": "anion_only_failure" if by_label["Br"] and not by_label["Br-"] else ("neutral_only_failure" if not by_label["Br"] and by_label["Br-"] else ("both_failure" if not by_label["Br"] and not by_label["Br-"] else "both_pass_pair_receipt_inconsistency")),
        },
        "nonclaims": [
            "diagnostic does not repair v0.11",
            "no experimental affinity is substituted",
            "no classifier is fit",
        ],
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"quality_map": by_label, "interpretation": payload["interpretation"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
