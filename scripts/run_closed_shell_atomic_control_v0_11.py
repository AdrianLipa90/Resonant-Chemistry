"""Execute the preregistered v0.11 conventional atomic control vector."""
from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reschem.closed_shell_atomic_control import generate_atomic_activation_control_atlas

OUT = ROOT / "benchmarks" / "CLOSED_SHELL_ATOMIC_CONTROL_V0_11.json"


def main() -> int:
    atlas = generate_atomic_activation_control_atlas()
    payload = {
        "schema": "RESCHEM_CLOSED_SHELL_ATOMIC_CONTROL_V0_11",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "preregister_source": "benchmarks/CLOSED_SHELL_ATOMIC_CONTROL_PREREG_V0_11.json",
        "status": (
            "CONVENTIONAL_ATOMIC_CONTROL_EXECUTED"
            if all(item.all_atomic_quality_pass for item in atlas)
            else "ATOMIC_CONTROL_EXECUTED_WITH_QUALITY_FAILURES"
        ),
        "candidate_count": len(atlas),
        "vectors": [item.to_dict() for item in atlas],
        "nonclaims": [
            "no molecular binding energy is computed here",
            "no scalar classifier is fitted here",
            "HF finite-difference attachment gain is not asserted experimental electron affinity",
            "the output is an explanatory conventional-control vector, not a Resonant-Chemistry correction term",
        ],
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "output": str(OUT.relative_to(ROOT)),
        "candidate_count": len(atlas),
        "quality_pass": all(item.all_atomic_quality_pass for item in atlas),
    }, indent=2))
    return 0 if all(item.all_atomic_quality_pass for item in atlas) else 2


if __name__ == "__main__":
    raise SystemExit(main())
