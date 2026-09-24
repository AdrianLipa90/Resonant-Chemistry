#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from reschem.h3plus_ci_berry_control_v01 import run_frozen_h3plus_protocol


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="build/H3PLUS_CI_BERRY_RESULT_V0_1.json",
    )
    args = parser.parse_args()
    result = run_frozen_h3plus_protocol()
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
