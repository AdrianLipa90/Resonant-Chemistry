"""Execute one preregistered v0.12A atomic neutral/ion convergence scan."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reschem.atomic_ion_convergence import run_atomic_state_scan, state_label


def _safe_label(z: int, charge: int) -> str:
    label = state_label(z, charge)
    return label.replace("+", "_plus").replace("-", "_minus")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--z", type=int, required=True)
    parser.add_argument("--charge", type=int, choices=(-1, 0, 1), required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "benchmarks" / "v0_12a_states")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    scan = run_atomic_state_scan(args.z, args.charge)
    payload = {
        "schema": "RESCHEM_ATOMIC_ION_CONVERGENCE_V0_12A_STATE",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "preregister_source": "benchmarks/ATOMIC_ION_CONVERGENCE_PREREG_V0_12A.json",
        **scan,
    }
    output = args.output_dir / f"{_safe_label(args.z, args.charge)}.json"
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(output.relative_to(ROOT)),
        "state": state_label(args.z, args.charge),
        "level_converged": {row["level"]: row["converged"] for row in scan["levels"]},
        "virial_abs": {row["level"]: row["virial_abs_hartree"] for row in scan["levels"]},
        "energy_drift": scan["adjacent_energy_drift"],
    }, indent=2))

    # Scientific non-convergence is data in v0.12A, not an infrastructure error.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
