"""Run all five frozen v0.14A starts for one closed-shell XY2 formula."""
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

from reschem.molecular_state_relaxation import add_relative_energies, run_pyscf_relaxation, xy2_seed_geometries


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--centre", choices=("Ne", "Ar", "Kr"), required=True)
    parser.add_argument("--ligand", choices=("F", "Cl", "Br"), required=True)
    parser.add_argument("--dimer-json", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "benchmarks" / "v0_14a_formulae")
    args = parser.parse_args()

    formula = f"{args.centre}{args.ligand}2"
    args.output_dir.mkdir(parents=True, exist_ok=True)
    output = args.output_dir / f"{formula}.json"

    dimer = json.loads(args.dimer_json.read_text(encoding="utf-8"))
    r_yy = dimer.get("optimized_r_YY_angstrom")
    if dimer.get("status") != "DIMER_PREPASS_AVAILABLE" or r_yy is None:
        payload = {
            "schema": "RESCHEM_MOLECULAR_FORMULA_RELAXATION_V0_14A",
            "generated_utc": datetime.now(timezone.utc).isoformat(),
            "preregister_source": "benchmarks/MOLECULAR_STATE_RELAXATION_PREREG_V0_14A.json",
            "formula": formula,
            "centre": args.centre,
            "ligand": args.ligand,
            "status": "FORMULA_NOT_RUN_DIMER_PREPASS_UNAVAILABLE",
            "dimer_source": str(args.dimer_json),
            "optimized_r_YY_angstrom": r_yy,
            "relaxations": [],
        }
        output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(json.dumps({"formula": formula, "status": payload["status"]}, indent=2))
        return 0

    results = []
    formula_start = time.perf_counter()
    for seed in xy2_seed_geometries(args.centre, args.ligand, float(r_yy)):
        start = time.perf_counter()
        row = run_pyscf_relaxation(seed)
        row["wall_seconds"] = time.perf_counter() - start
        results.append(row)

    results = add_relative_energies(results)
    success_count = sum(
        row.get("status") == "RELAXATION_RETURNED_FINAL_SCF_CONVERGED_NO_HESSIAN"
        for row in results
    )
    payload = {
        "schema": "RESCHEM_MOLECULAR_FORMULA_RELAXATION_V0_14A",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "preregister_source": "benchmarks/MOLECULAR_STATE_RELAXATION_PREREG_V0_14A.json",
        "formula": formula,
        "centre": args.centre,
        "ligand": args.ligand,
        "status": "FORMULA_RELAXATION_SCREEN_COMPLETE",
        "optimized_r_YY_angstrom": r_yy,
        "start_count": len(results),
        "successful_relaxation_count": success_count,
        "formula_wall_seconds": time.perf_counter() - formula_start,
        "relaxations": results,
        "nonclaims": [
            "relative electronic energies are screening results only",
            "no Hessian/local-minimum admission is performed",
            "geometry is not converted automatically into a 3c4e/VDW topology label",
        ],
    }
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(output),
        "formula": formula,
        "start_count": len(results),
        "successful_relaxation_count": success_count,
        "formula_wall_seconds": payload["formula_wall_seconds"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
