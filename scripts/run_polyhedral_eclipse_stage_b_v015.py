#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from reschem.atomic_kepler_phase_v015 import harmonic_frequency_candidate, solve_period2_radial_kepler_phase
from reschem.eclipse_time_doppler_v015 import transform_eclipse_observation


PREREG_PATH = Path("benchmarks/POLYHEDRAL_ECLIPSE_STAGE_B_KEPLER_PHASE_PREREG_V0_15.json")
A0_PATH = Path("benchmarks/POLYHEDRAL_ECLIPSE_STAGE_A0_R2_LEDGER_V0_15.json")
A1_PATH = Path("benchmarks/POLYHEDRAL_ECLIPSE_STAGE_A1_LEDGER_V0_15.json")
TIR_MASS_PATH = Path("benchmarks/TIR_SIC_MASS_WEIGHTED_LEDGER_V0_15.json")
TIME_DOPPLER_PATH = Path("benchmarks/ECLIPSE_TIME_DOPPLER_FREEZE_V0_15.json")
OUTPUT_SCHEMA = "RESCHEM_POLYHEDRAL_ECLIPSE_STAGE_B_ZERO_FIT_PREDICTION_LEDGER_V0_15"


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256_json(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _semantic_mass_index(a1: dict) -> dict[str, float]:
    out: dict[str, float] = {}
    for overlay in a1.get("semantic_mass_overlays", []):
        card_id = str(overlay["card_id"])
        node = overlay["tir"]["semantic_axes"]["values"]["semantic_mass"]
        out[card_id] = float(node["value"])
    return out


def build_stage_b_prediction_ledger() -> dict:
    prereg = _load(PREREG_PATH)
    a0 = _load(A0_PATH)
    a1 = _load(A1_PATH)
    tir_mass = _load(TIR_MASS_PATH)
    time_doppler = _load(TIME_DOPPLER_PATH)

    if prereg.get("status") != "STAGE_B_ZERO_FIT_PHASE_MAPPING_PREREGISTERED_BEFORE_SPECTRAL_JOIN":
        raise RuntimeError("Stage-B prereg status drift")
    if prereg.get("fit_parameters") != [] or prereg.get("calibration_to_observed_spectrum") != "NONE":
        raise RuntimeError("Stage-B zero-fit boundary drift")
    if a0.get("revision") != "R2_AXIS_RESOLVED_TIR_SIC_PHASE":
        raise RuntimeError("Stage-A0 R2 source drift")
    if a0.get("spectral_join") != {"status": "WITHHELD_FOR_BLIND_COMPARISON", "accepted_observed_fields": []}:
        raise RuntimeError("Stage-A0 spectral boundary drift")
    if a1.get("status") != "FEATURES_FROZEN_BEFORE_SPECTRAL_JOIN":
        raise RuntimeError("Stage-A1 source status drift")
    if time_doppler.get("status") != "FROZEN_BEFORE_SPECTRAL_JOIN":
        raise RuntimeError("time/Doppler freeze boundary drift")

    semantic_mass = _semantic_mass_index(a1)
    atoms: list[dict[str, object]] = []
    for atom in a0["atoms"]:
        card_id = str(atom["atom_card_id"])
        z = int(atom["Z"])
        phase = solve_period2_radial_kepler_phase(z)
        phase_record = phase.as_dict()
        if phase_record["observed_spectrum"] != "WITHHELD_FOR_BLIND_COMPARISON":
            raise RuntimeError(f"Kepler phase spectral boundary drift for {card_id}")

        axes: dict[str, dict[str, object]] = {}
        for label, axis in atom["tetrahedral_inference"]["axis_resolved_phase"]["axes"].items():
            order = int(axis["dominant_harmonic_order"])
            candidate = harmonic_frequency_candidate(phase, order)
            null_observer = transform_eclipse_observation(
                harmonic_order=order,
                omega_proper_rad_s=phase.kepler_angular_rate_rad_per_second,
                subjective_time_scale=1.0,
                beta_radial=0.0,
            ).payload
            axes[str(label)] = {
                "frozen_harmonic_order": order,
                "frozen_harmonic_strength": float(axis["dominant_harmonic_strength"]),
                "proper_kepler_candidate": candidate,
                "null_rest_observer_control": null_observer,
            }

        spatial: list[dict[str, object]] = []
        for feature in atom["spatial_orbital_features"]:
            order = int(feature["dominant_orbital_band_harmonic_order"])
            spatial.append({
                "spatial_partition": feature["spatial_partition"],
                "orbital_label": feature["orbital_label"],
                "frozen_harmonic_order": order,
                "frozen_harmonic_strength": float(feature["dominant_orbital_band_harmonic_strength"]),
                "proper_kepler_candidate": harmonic_frequency_candidate(phase, order),
                "source_feature_sha256": feature["feature_sha256"],
            })

        row_body = {
            "atom_card_id": card_id,
            "symbol": atom["symbol"],
            "Z": z,
            "A": int(atom["A"]),
            "semantic_mass": semantic_mass.get(card_id),
            "semantic_mass_per_nucleon": None if card_id not in semantic_mass else semantic_mass[card_id] / float(atom["A"]),
            "radial_kepler_phase": phase_record,
            "tir_sic_axis_frequency_candidates": axes,
            "spatial_probe_frequency_candidates": spatial,
            "subjective_time_observation_policy": {
                "null_control_g": 1.0,
                "atomic_substrate_lapse_mapping": "PENDING_PREREGISTERED_ATOMIC_SUBSTRATE_MAPPING",
                "pncs_default_orbital_kernel_scale": 1.0,
            },
            "doppler_observation_policy": {
                "null_control_beta": 0.0,
                "source_relative_velocity": "PENDING_OBSERVATION_CONTEXT",
            },
            "observed_spectrum": "WITHHELD_FOR_BLIND_COMPARISON",
        }
        atoms.append({**row_body, "prediction_sha256": _sha256_json(row_body)})

    body = {
        "schema": OUTPUT_SCHEMA,
        "version": "0.15.0",
        "status": "ZERO_FIT_PREDICTIONS_FROZEN_BEFORE_SPECTRAL_JOIN",
        "sources": {
            str(PREREG_PATH): _sha256_file(PREREG_PATH),
            str(A0_PATH): _sha256_file(A0_PATH),
            str(A1_PATH): _sha256_file(A1_PATH),
            str(TIR_MASS_PATH): _sha256_file(TIR_MASS_PATH),
            str(TIME_DOPPLER_PATH): _sha256_file(TIME_DOPPLER_PATH),
        },
        "atom_count": len(atoms),
        "fit_parameters": [],
        "calibration_to_observed_spectrum": "NONE",
        "observed_spectrum": "WITHHELD_FOR_BLIND_COMPARISON",
        "observer_transform_boundary": {
            "null_rest_control": {"subjective_time_scale": 1.0, "beta_radial": 0.0},
            "nontrivial_subjective_time": "PENDING_ATOMIC_SUBSTRATE_MAPPING_BEFORE_USE",
            "nonzero_doppler": "PENDING_PROVENANCE_BEARING_OBSERVATION_VELOCITY",
        },
        "tir_mass_ledger_status": tir_mass.get("status"),
        "atoms": atoms,
        "epistemic_operator": "CHYBA",
        "canon_allowed": False,
    }
    return {**body, "ledger_sha256": _sha256_json(body)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze Resonant Chemistry v0.15 zero-fit Stage-B predictions")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    ledger = build_stage_b_prediction_ledger()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": ledger["status"],
        "atom_count": ledger["atom_count"],
        "ledger_sha256": ledger["ledger_sha256"],
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
