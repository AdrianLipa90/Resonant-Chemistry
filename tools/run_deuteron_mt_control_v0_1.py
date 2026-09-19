#!/usr/bin/env python3
"""Run the MT-triplet deuteron control gate and emit a provenance receipt."""
from __future__ import annotations

from dataclasses import asdict
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from reschem.nuclear.deuteron_control import solve_deuteron_mt_triplet  # noqa: E402

OUT = ROOT / "build" / "DEUTERON_MT_CONTROL_V0_1.json"
BINDING_TOL_MEV = 5.0e-4
CONVERGENCE_TOL_MEV = 2.0e-4
RMS_TOL_FM = 1.0e-2


def main() -> int:
    coarse = solve_deuteron_mt_triplet(n_points=4000)
    fine = solve_deuteron_mt_triplet(n_points=8000)
    convergence_delta = abs(fine.binding_energy_mev - coarse.binding_energy_mev)

    checks = {
        "binding_reference_residual": {
            "value_mev": abs(fine.binding_residual_mev),
            "limit_mev": BINDING_TOL_MEV,
        },
        "grid_convergence": {
            "value_mev": convergence_delta,
            "limit_mev": CONVERGENCE_TOL_MEV,
        },
        "single_bound_state_in_lowest_five_levels": {
            "value": fine.bound_state_count_in_sample,
            "expected": 1,
        },
        "second_level_positive": {
            "value_mev": fine.second_level_energy_mev,
            "expected_relation": "> 0",
        },
        "model_single_nucleon_rms": {
            "value_fm": abs(fine.single_nucleon_rms_residual_fm),
            "limit_fm": RMS_TOL_FM,
        },
    }
    passed = (
        checks["binding_reference_residual"]["value_mev"] <= BINDING_TOL_MEV
        and checks["grid_convergence"]["value_mev"] <= CONVERGENCE_TOL_MEV
        and fine.bound_state_count_in_sample == 1
        and fine.second_level_energy_mev > 0.0
        and checks["model_single_nucleon_rms"]["value_fm"] <= RMS_TOL_FM
    )

    receipt = {
        "schema": "RC_DEUTERON_MT_CONTROL_RECEIPT_V0_1",
        "gate": "DEUTERON_MT_TRIPLET_CONTROL",
        "status": "CONTROL_MODEL_REPRODUCTION_PASS" if passed else "FAIL",
        "evidential_class": "CONTROL_MODEL_REPRODUCTION",
        "physical_prediction_frontier": "PENDING_PREDICTIVE_NN_INTERACTION_OR_ENDOGENOUS_DERIVATION",
        "nucleon_packet": "data/nuclear/nucleon_packet_codata2022_pdg2025_v0_1.json",
        "interaction_provider": "data/nuclear/interactions/mt_triplet_control_v0_1.json",
        "coarse": asdict(coarse),
        "fine": asdict(fine),
        "checks": checks,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=2))
    return 0 if passed else 2


if __name__ == "__main__":
    raise SystemExit(main())
