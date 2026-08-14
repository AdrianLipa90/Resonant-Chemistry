"""Execute one frozen v0.12B L3 atomic neutral/ion continuation state."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reschem.atomic_ion_convergence import state_label
from reschem.atomic_ion_convergence_continuation import run_l3_state


def _safe_label(z: int, charge: int) -> str:
    return state_label(z, charge).replace("+", "_plus").replace("-", "_minus")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--z", type=int, required=True)
    parser.add_argument("--charge", type=int, choices=(-1, 0, 1), required=True)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "benchmarks" / "v0_12b_states")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    state = run_l3_state(args.z, args.charge)
    payload = {
        "schema": "RESCHEM_ATOMIC_ION_CONVERGENCE_V0_12B_STATE",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "preregister_source": "benchmarks/ATOMIC_ION_CONVERGENCE_PREREG_V0_12B.json",
        **state,
    }
    output = args.output_dir / f"{_safe_label(args.z, args.charge)}.json"
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({
        "output": str(output),
        "state": state_label(args.z, args.charge),
        "converged": state["converged"],
        "energy_hartree": state["energy_hartree"],
        "virial_abs_hartree": state["virial_abs_hartree"],
        "iterations": state["iterations"],
    }, indent=2))

    # Scientific non-convergence remains valid output, not CI infrastructure failure.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
