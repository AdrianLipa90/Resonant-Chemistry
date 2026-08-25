from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

from scipy.stats import pearsonr, spearmanr

SCHEMA = "RESCHEM_ATOMIC_SUBJECTIVE_TIME_STAGE_E_GROUND_ORIGIN_HOLDOUT_RESULT_V0_15"
PREREG_PATH = Path("benchmarks/ATOMIC_SUBJECTIVE_TIME_STAGE_E_GROUND_RESONANCE_HOLDOUT_PREREG_V0_15.json")
STAGE_B_PATH = Path("benchmarks/POLYHEDRAL_ECLIPSE_STAGE_B_PREDICTION_LEDGER_V0_15.json")
D0_PATH = Path("benchmarks/ATOMIC_SUBJECTIVE_TIME_STAGE_D0_LEDGER_V0_15.json")
OBS_PATH = Path("benchmarks/NIST_GROUND_ORIGIN_STAGE_E_SELECTED_OBSERVED_LEDGER_V0_15.json")
EXPECTED_POLICIES = (
    "NULL_REST_CONTROL",
    "KAPPA_RADIAL_BALANCED",
    "SEMANTIC_MASS_BALANCED",
    "RADIAL_SEMANTIC_GEOMETRIC_COUPLING",
    "RADIAL_SEMANTIC_PRODUCT_COUPLING",
)


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_json(value: object) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def correlation_or_none(x: list[float], y: list[float], kind: str) -> float | None:
    if len(x) != len(y) or len(x) < 2:
        return None
    if len(set(x)) < 2 or len(set(y)) < 2:
        return None
    if kind == "spearman":
        value = float(spearmanr(x, y).statistic)
    elif kind == "pearson_log":
        lx = [math.log10(v) for v in x]
        ly = [math.log10(v) for v in y]
        value = float(pearsonr(lx, ly).statistic)
    else:
        raise ValueError(kind)
    return value if math.isfinite(value) else None


def build_result() -> dict[str, object]:
    prereg_raw = PREREG_PATH.read_bytes()
    stage_b_raw = STAGE_B_PATH.read_bytes()
    d0_raw = D0_PATH.read_bytes()
    obs_raw = OBS_PATH.read_bytes()
    prereg = json.loads(prereg_raw)
    stage_b = json.loads(stage_b_raw)
    d0 = json.loads(d0_raw)
    observed = json.loads(obs_raw)

    if prereg.get("status") != "INDEPENDENT_NIST_GROUND_ORIGIN_LINE_HOLDOUT_PREREGISTERED_BEFORE_DATA_JOIN":
        raise SystemExit("Stage-E prereg status drift")
    if stage_b.get("status") != "ZERO_FIT_PREDICTIONS_FROZEN_BEFORE_SPECTRAL_JOIN":
        raise SystemExit("Stage-B prediction ledger drift")
    if d0.get("status") != "MODEL_SIDE_SUBJECTIVE_TIME_HYPOTHESES_FROZEN_FOR_FUTURE_HOLDOUT":
        raise SystemExit("Stage-D0 subjective-time ledger drift")
    if observed.get("status") != "STAGE_E_OBSERVED_GROUND_ORIGIN_LINES_SELECTED_BY_PREREGISTERED_RULE":
        raise SystemExit("Stage-E observed ledger drift")
    if observed.get("model_data_join_performed") is not False:
        raise SystemExit("Stage-E observed ledger was already joined")
    if d0.get("fit_parameters") != [] or d0.get("calibration_parameters") != []:
        raise SystemExit("Stage-D0 fit/calibration drift")

    b_by_symbol = {row["symbol"]: row for row in stage_b["atoms"]}
    d_by_symbol = {row["symbol"]: row for row in d0["rows"]}
    o_by_symbol = {row["symbol"]: row for row in observed["rows"]}
    symbols = tuple(row["symbol"] for row in d0["rows"])
    if symbols != ("B", "C", "N", "O", "F", "Ne"):
        raise SystemExit(f"Stage-D0 atom order drift: {symbols}")
    if set(b_by_symbol) != set(symbols) or set(o_by_symbol) != set(symbols):
        raise SystemExit("Stage-E cohort mismatch")
    ids = tuple(c["policy_id"] for c in d0["rows"][0]["candidates"])
    if ids != EXPECTED_POLICIES:
        raise SystemExit(f"Stage-D0 policy set drift: {ids}")

    policies: list[dict[str, object]] = []
    for policy_id in EXPECTED_POLICIES:
        rows: list[dict[str, object]] = []
        predicted_values: list[float] = []
        observed_values: list[float] = []
        abs_rel: list[float] = []
        log_ratios: list[float] = []
        for symbol in symbols:
            base = float(b_by_symbol[symbol]["radial_kepler_phase"]["kepler_wavenumber_cm_inverse"])
            candidate = next(c for c in d_by_symbol[symbol]["candidates"] if c["policy_id"] == policy_id)
            g = float(candidate["lapse"])
            pred = base * g
            obs = float(o_by_symbol[symbol]["selected_wavenumber_cm_inverse"])
            if not (math.isfinite(pred) and pred > 0 and math.isfinite(obs) and obs > 0):
                raise SystemExit(f"nonpositive/nonfinite Stage-E value: {symbol}:{policy_id}")
            ratio = pred / obs
            are = abs(pred - obs) / obs
            logr = math.log10(ratio)
            predicted_values.append(pred)
            observed_values.append(obs)
            abs_rel.append(are)
            log_ratios.append(logr)
            row_body: dict[str, object] = {
                "symbol": symbol,
                "policy_id": policy_id,
                "kepler_fundamental_wavenumber_cm_inverse": base,
                "frozen_subjective_time_lapse": g,
                "doppler_beta_radial": 0.0,
                "doppler_factor": 1.0,
                "predicted_wavenumber_cm_inverse": pred,
                "observed_ground_origin_wavenumber_cm_inverse": obs,
                "predicted_to_observed_ratio": ratio,
                "absolute_relative_error": are,
                "log10_ratio": logr,
                "fit_parameters_added": [],
                "calibration_parameters_added": [],
                "model_parameters_changed": False,
            }
            rows.append({**row_body, "row_sha256": sha256_json(row_body)})
        metrics = {
            "median_absolute_relative_error": statistics.median(abs_rel),
            "mean_absolute_relative_error": statistics.mean(abs_rel),
            "rms_log10_ratio": math.sqrt(sum(x*x for x in log_ratios)/len(log_ratios)),
            "spearman_rank_correlation": correlation_or_none(predicted_values, observed_values, "spearman"),
            "pearson_log10_correlation": correlation_or_none(predicted_values, observed_values, "pearson_log"),
        }
        policy_body: dict[str, object] = {
            "policy_id": policy_id,
            "metrics": metrics,
            "rows": rows,
            "validation_claimed": False,
            "candidate_selected_for_model_update": False,
        }
        policies.append({**policy_body, "policy_sha256": sha256_json(policy_body)})

    body: dict[str, object] = {
        "schema": SCHEMA,
        "version": "0.15.0",
        "status": "INDEPENDENT_STAGE_E_GROUND_ORIGIN_HOLDOUT_JOIN_COMPLETE",
        "sources": {
            str(PREREG_PATH): sha256_bytes(prereg_raw),
            str(STAGE_B_PATH): sha256_bytes(stage_b_raw),
            str(D0_PATH): sha256_bytes(d0_raw),
            str(OBS_PATH): sha256_bytes(obs_raw),
        },
        "stage_b_prediction_ledger_sha256": stage_b["ledger_sha256"],
        "stage_d0_subjective_time_ledger_sha256": d0["ledger_sha256"],
        "stage_e_observed_ledger_sha256": observed["ledger_sha256"],
        "policy_count": len(policies),
        "species_count": len(symbols),
        "all_frozen_policies_reported": True,
        "candidate_selected_or_removed": False,
        "model_parameters_changed_after_join": False,
        "fit_parameters_added_after_join": [],
        "calibration_parameters_added_after_join": [],
        "promotion_threshold": "NONE_PREDECLARED",
        "validation_claimed": False,
        "policies": policies,
        "interpretation": "NONE_IN_RESULT_LEDGER",
        "canon_allowed": False,
    }
    return {**body, "result_sha256": sha256_json(body)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="out/ATOMIC_SUBJECTIVE_TIME_STAGE_E_GROUND_ORIGIN_HOLDOUT_RESULT_V0_15.json")
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    result = build_result()
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print(json.dumps({
        "status": result["status"],
        "result_sha256": result["result_sha256"],
        "metrics": {p["policy_id"]: p["metrics"] for p in result["policies"]},
        "output": str(output),
    }, indent=2))


if __name__ == "__main__":
    main()
