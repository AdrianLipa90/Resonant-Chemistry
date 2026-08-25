from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

SCHEMA = "RESCHEM_ATOMIC_SUBJECTIVE_TIME_STAGE_D1_DIAGNOSTIC_LEDGER_V0_15"
CONTRACT_PATH = Path("benchmarks/ATOMIC_SUBJECTIVE_TIME_STAGE_D1_DIAGNOSTIC_CONTRACT_V0_15.json")
D0_PATH = Path("benchmarks/ATOMIC_SUBJECTIVE_TIME_STAGE_D0_LEDGER_V0_15.json")
STAGE_C_PATH = Path("benchmarks/POLYHEDRAL_ECLIPSE_STAGE_C_IONIZATION_EDGE_RESULT_V0_15.json")
G_REQUIRED_KEY = "g_required_if_all_scale_mismatch_were_assigned_to_subjective_time"


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_json(value: object) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def build_diagnostic() -> dict[str, object]:
    contract_raw = CONTRACT_PATH.read_bytes()
    d0_raw = D0_PATH.read_bytes()
    stage_c_raw = STAGE_C_PATH.read_bytes()
    contract = json.loads(contract_raw)
    d0 = json.loads(d0_raw)
    stage_c = json.loads(stage_c_raw)

    if contract.get("status") != "POST_JOIN_DIAGNOSTIC_METRICS_FROZEN":
        raise SystemExit("Stage-D1 contract drift")
    if d0.get("status") != "MODEL_SIDE_SUBJECTIVE_TIME_HYPOTHESES_FROZEN_FOR_FUTURE_HOLDOUT":
        raise SystemExit("Stage-D0 ledger is not frozen")
    if stage_c.get("status") != "BLIND_IONIZATION_EDGE_JOIN_COMPLETE":
        raise SystemExit("Stage-C result is not frozen")
    if d0.get("fit_parameters") != [] or d0.get("calibration_parameters") != []:
        raise SystemExit("Stage-D0 fit/calibration boundary drift")
    if stage_c.get("fit_parameters_added_after_join") != [] or stage_c.get("model_parameters_changed_after_join") is not False:
        raise SystemExit("Stage-C mutation boundary drift")

    stage_c_by_symbol = {row["symbol"]: row for row in stage_c["rows"]}
    policies = [candidate["policy_id"] for candidate in d0["rows"][0]["candidates"]]
    policy_rows: list[dict[str, object]] = []

    for policy_id in policies:
        atom_rows: list[dict[str, object]] = []
        absolute_relative_errors: list[float] = []
        log10_g_ratios: list[float] = []
        for d0_row in d0["rows"]:
            symbol = d0_row["symbol"]
            c_row = stage_c_by_symbol[symbol]
            candidate = next(c for c in d0_row["candidates"] if c["policy_id"] == policy_id)
            g = float(candidate["lapse"])
            predicted = float(c_row["kepler_fundamental"]["predicted_wavenumber_cm_inverse"])
            observed = float(c_row["observed_ionization_edge_cm_inverse"])
            g_required = float(c_row["post_join_diagnostic_only"][G_REQUIRED_KEY])
            corrected = predicted * g
            are = abs(corrected - observed) / observed
            g_ratio = g / g_required
            log10_g_ratio = math.log10(g_ratio)
            absolute_relative_errors.append(are)
            log10_g_ratios.append(log10_g_ratio)
            atom_body = {
                "symbol": symbol,
                "Z": int(d0_row["Z"]),
                "policy_id": policy_id,
                "frozen_subjective_time_lapse": g,
                "post_join_g_required_diagnostic": g_required,
                "g_ratio": g_ratio,
                "log10_g_ratio": log10_g_ratio,
                "kepler_fundamental_predicted_wavenumber_cm_inverse": predicted,
                "corrected_wavenumber_cm_inverse": corrected,
                "observed_ionization_edge_cm_inverse": observed,
                "absolute_relative_error": are,
                "status": "POST_JOIN_DIAGNOSTIC_ONLY_NOT_VALIDATION_NOT_CALIBRATION",
            }
            atom_rows.append({**atom_body, "row_sha256": sha256_json(atom_body)})

        metrics = {
            "median_absolute_relative_error": statistics.median(absolute_relative_errors),
            "mean_absolute_relative_error": statistics.mean(absolute_relative_errors),
            "rms_log10_g_ratio": math.sqrt(sum(x * x for x in log10_g_ratios) / len(log10_g_ratios)),
        }
        policy_body = {
            "policy_id": policy_id,
            "metrics": metrics,
            "atom_rows": atom_rows,
            "candidate_selected_for_model_update": False,
            "validation_claimed": False,
        }
        policy_rows.append({**policy_body, "policy_sha256": sha256_json(policy_body)})

    body: dict[str, object] = {
        "schema": SCHEMA,
        "version": "0.15.0",
        "status": "POST_JOIN_SUBJECTIVE_TIME_DIAGNOSTIC_COMPLETE",
        "sources": {
            str(CONTRACT_PATH): sha256_bytes(contract_raw),
            str(D0_PATH): sha256_bytes(d0_raw),
            str(STAGE_C_PATH): sha256_bytes(stage_c_raw),
        },
        "diagnostic_only": True,
        "validation_claimed": False,
        "model_parameters_changed": False,
        "candidate_selected_or_removed": False,
        "fit_parameters_added": [],
        "calibration_parameters_added": [],
        "reference_policy": "NULL_REST_CONTROL",
        "policy_count": len(policy_rows),
        "policies": policy_rows,
        "interpretation": "NONE_IN_DIAGNOSTIC_LEDGER",
        "canon_allowed": False,
    }
    return {**body, "diagnostic_sha256": sha256_json(body)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="out/ATOMIC_SUBJECTIVE_TIME_STAGE_D1_DIAGNOSTIC_LEDGER_V0_15.json")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    result = build_diagnostic()
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print(json.dumps({
        "status": result["status"],
        "policy_count": result["policy_count"],
        "diagnostic_sha256": result["diagnostic_sha256"],
        "metrics": {p["policy_id"]: p["metrics"] for p in result["policies"]},
        "output": str(output),
    }, indent=2))


if __name__ == "__main__":
    main()
