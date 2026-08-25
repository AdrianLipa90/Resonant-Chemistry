#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scipy.stats import pearsonr, spearmanr


PREREG_PATH = Path("benchmarks/POLYHEDRAL_ECLIPSE_STAGE_C_IONIZATION_EDGE_PREREG_V0_15.json")
PREDICTION_PATH = Path("benchmarks/POLYHEDRAL_ECLIPSE_STAGE_B_PREDICTION_LEDGER_V0_15.json")
OBSERVATION_PATH = Path("benchmarks/NIST_B_NE_NEUTRAL_IONIZATION_EDGES_V0_15.json")
SCHEMA = "RESCHEM_POLYHEDRAL_ECLIPSE_STAGE_C_IONIZATION_EDGE_RESULT_V0_15"


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256_json(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _residual(predicted: float, observed: float) -> dict[str, float | str | None]:
    p = float(predicted)
    o = float(observed)
    if not math.isfinite(p) or not math.isfinite(o) or o <= 0.0 or p < 0.0:
        raise ValueError("predicted/observed wavenumbers must be finite with observed>0 and predicted>=0")
    if p == 0.0:
        return {
            "predicted_wavenumber_cm_inverse": 0.0,
            "observed_wavenumber_cm_inverse": o,
            "predicted_to_observed_ratio": 0.0,
            "absolute_relative_error": 1.0,
            "log10_ratio": None,
            "status": "ZERO_CHANNEL_MISMATCH",
        }
    ratio = p / o
    return {
        "predicted_wavenumber_cm_inverse": p,
        "observed_wavenumber_cm_inverse": o,
        "predicted_to_observed_ratio": ratio,
        "absolute_relative_error": abs(p - o) / o,
        "log10_ratio": math.log10(ratio),
        "status": "NONZERO_ABSOLUTE_COMPARISON",
    }


def build_result() -> dict:
    prereg = _load(PREREG_PATH)
    pred = _load(PREDICTION_PATH)
    obs = _load(OBSERVATION_PATH)

    if prereg["status"] != "PREREGISTERED_BEFORE_EXTERNAL_SPECTRAL_LOOKUP":
        raise RuntimeError("Stage-C prereg status drift")
    if prereg["prediction_ledger_sha256"] != pred["ledger_sha256"]:
        raise RuntimeError("prediction ledger identity drift")
    if pred["status"] != "ZERO_FIT_PREDICTIONS_FROZEN_BEFORE_SPECTRAL_JOIN":
        raise RuntimeError("prediction freeze boundary drift")
    if pred["fit_parameters"] != [] or pred["calibration_to_observed_spectrum"] != "NONE":
        raise RuntimeError("prediction zero-fit boundary drift")
    if obs["status"] != "EXTERNAL_REFERENCE_DATA_JOINED_AFTER_STAGE_B_FREEZE":
        raise RuntimeError("observation timing boundary drift")
    if obs["model_parameters_changed_after_lookup"] is not False:
        raise RuntimeError("post-lookup model mutation boundary drift")

    observed = {row["symbol"]: float(row["ionization_wavenumber_cm_inverse"]) for row in obs["rows"]}
    predicted_atoms = {row["symbol"]: row for row in pred["atoms"]}
    expected = ["B", "C", "N", "O", "F", "Ne"]
    if list(observed) != expected or set(predicted_atoms) != set(expected):
        raise RuntimeError("B-Ne cohort/order drift")

    rows: list[dict[str, object]] = []
    primary_pred: list[float] = []
    primary_obs: list[float] = []
    primary_ares: list[float] = []
    primary_logs: list[float] = []

    for symbol in expected:
        atom = predicted_atoms[symbol]
        o = observed[symbol]
        fundamental = float(atom["radial_kepler_phase"]["kepler_wavenumber_cm_inverse"])
        fundamental_residual = _residual(fundamental, o)
        primary_pred.append(fundamental)
        primary_obs.append(o)
        primary_ares.append(float(fundamental_residual["absolute_relative_error"]))
        primary_logs.append(float(fundamental_residual["log10_ratio"]))

        axes = {}
        for axis in ("x", "y", "z"):
            node = atom["tir_sic_axis_frequency_candidates"][axis]
            axes[axis] = {
                "harmonic_order": int(node["frozen_harmonic_order"]),
                "harmonic_strength": float(node["frozen_harmonic_strength"]),
                "residual": _residual(float(node["proper_kepler_candidate"]["wavenumber_cm_inverse"]), o),
            }

        spatial = []
        for node in atom["spatial_probe_frequency_candidates"]:
            spatial.append({
                "spatial_partition": node["spatial_partition"],
                "orbital_label": node["orbital_label"],
                "harmonic_order": int(node["frozen_harmonic_order"]),
                "harmonic_strength": float(node["frozen_harmonic_strength"]),
                "residual": _residual(float(node["proper_kepler_candidate"]["wavenumber_cm_inverse"]), o),
            })

        required_g = o / fundamental
        row_body = {
            "symbol": symbol,
            "Z": int(atom["Z"]),
            "A": int(atom["A"]),
            "observed_ionization_edge_cm_inverse": o,
            "kepler_fundamental": fundamental_residual,
            "tir_sic_axes": axes,
            "spatial_probes": spatial,
            "semantic_mass": atom.get("semantic_mass"),
            "semantic_mass_per_nucleon": atom.get("semantic_mass_per_nucleon"),
            "post_join_diagnostic_only": {
                "g_required_if_all_scale_mismatch_were_assigned_to_subjective_time": required_g,
                "status": "POST_JOIN_DIAGNOSTIC_ONLY_NOT_A_MODEL_INPUT_NOT_A_CALIBRATION",
            },
        }
        rows.append({**row_body, "row_sha256": _sha256_json(row_body)})

    spearman = spearmanr(primary_pred, primary_obs)
    pearson_log = pearsonr(np.log10(primary_pred), np.log10(primary_obs))
    aggregate = {
        "median_absolute_relative_error": float(np.median(primary_ares)),
        "rms_log10_ratio": float(math.sqrt(float(np.mean(np.square(primary_logs))))),
        "spearman_rank_correlation": float(spearman.statistic),
        "spearman_p_value": float(spearman.pvalue),
        "pearson_log10_correlation": float(pearson_log.statistic),
        "pearson_log10_p_value": float(pearson_log.pvalue),
        "absolute_scale_status": "MEASURED_WITHOUT_PREDECLARED_PROMOTION_THRESHOLD",
    }

    body = {
        "schema": SCHEMA,
        "version": "0.15.0",
        "status": "BLIND_IONIZATION_EDGE_JOIN_COMPLETE",
        "sources": {
            str(PREREG_PATH): _sha256_file(PREREG_PATH),
            str(PREDICTION_PATH): _sha256_file(PREDICTION_PATH),
            str(OBSERVATION_PATH): _sha256_file(OBSERVATION_PATH),
        },
        "prediction_ledger_sha256": pred["ledger_sha256"],
        "fit_parameters_added_after_join": [],
        "model_parameters_changed_after_join": False,
        "primary_channel": "KEPLER_FUNDAMENTAL_ZERO_FIT",
        "aggregate_primary_metrics": aggregate,
        "rows": rows,
        "interpretation": "NONE_IN_RESULT_LEDGER",
        "epistemic_operator": "CHYBA",
        "canon_allowed": False,
    }
    return {**body, "result_sha256": _sha256_json(body)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run preregistered Resonant Chemistry v0.15 B-Ne NIST ionization-edge join")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build_result()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": result["status"],
        "result_sha256": result["result_sha256"],
        **result["aggregate_primary_metrics"],
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
