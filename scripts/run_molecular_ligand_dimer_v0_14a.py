"""Run one common-method ligand-dimer prepass for v0.14A."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reschem.molecular_state_relaxation import ligand_dimer_seed, run_pyscf_relaxation


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ligand", choices=("F", "Cl", "Br"), required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "benchmarks" / "v0_14a_dimers")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    seed = ligand_dimer_seed(args.ligand)
    start = time.perf_counter()
    result = run_pyscf_relaxation(seed)
    result["wall_seconds"] = time.perf_counter() - start

    r_yy = None
    if result.get("geometry_descriptors"):
        r_yy = result["geometry_descriptors"].get("Y_Y_angstrom")

    payload = {
        "schema": "RESCHEM_MOLECULAR_LIGAND_DIMER_V0_14A",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "preregister_source": "benchmarks/MOLECULAR_STATE_RELAXATION_PREREG_V0_14A.json",
        "ligand": args.ligand,
        "formula": f"{args.ligand}2",
        "status": (
            "DIMER_PREPASS_AVAILABLE"
            if result.get("status") == "RELAXATION_RETURNED_FINAL_SCF_CONVERGED_NO_HESSIAN" and r_yy
            else "DIMER_PREPASS_UNAVAILABLE"
        ),
        "optimized_r_YY_angstrom": r_yy,
        "relaxation": result,
        "nonclaim": "optimized dimer distance is used only as a common-method seed scale for XY2 and is not experimental fitting",
    }
    output = args.output_dir / f"{args.ligand}2.json"
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "formula": payload["formula"],
        "status": payload["status"],
        "r_YY_angstrom": r_yy,
        "wall_seconds": result["wall_seconds"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
