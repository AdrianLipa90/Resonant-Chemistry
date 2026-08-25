from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from reschem.atomic_subjective_time_v015 import (
    KAPPA,
    atomic_subjective_time_candidates,
)

SCHEMA = "RESCHEM_ATOMIC_SUBJECTIVE_TIME_STAGE_D0_LEDGER_V0_15"
PREREG_PATH = Path("benchmarks/ATOMIC_SUBJECTIVE_TIME_POSTJOIN_HYPOTHESIS_PREREG_V0_15.json")
STAGE_A1_PATH = Path("benchmarks/POLYHEDRAL_ECLIPSE_STAGE_A1_LEDGER_V0_15.json")


def canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_json(value: object) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text("utf-8"))


def build_ledger() -> dict[str, object]:
    prereg_raw = PREREG_PATH.read_bytes()
    stage_a1_raw = STAGE_A1_PATH.read_bytes()
    prereg = json.loads(prereg_raw)
    stage_a1 = json.loads(stage_a1_raw)

    if prereg.get("schema") != "RESCHEM_ATOMIC_SUBJECTIVE_TIME_POSTJOIN_HYPOTHESIS_PREREG_V0_15":
        raise SystemExit("subjective-time prereg schema drift")
    if stage_a1.get("status") != "FEATURES_FROZEN_BEFORE_SPECTRAL_JOIN":
        raise SystemExit("Stage-A1 is not frozen")

    radial_controls = stage_a1.get("radial_controls")
    overlays = stage_a1.get("semantic_mass_overlays")
    if not isinstance(radial_controls, dict) or not isinstance(overlays, list):
        raise SystemExit("Stage-A1 model-side inputs missing")

    mass_by_card: dict[str, float] = {}
    for overlay in overlays:
        if not isinstance(overlay, dict):
            raise SystemExit("invalid semantic mass overlay")
        card_id = str(overlay["card_id"])
        mass = float(
            overlay["tir"]["semantic_axes"]["values"]["semantic_mass"]["value"]
        )
        mass_by_card[card_id] = mass

    rows: list[dict[str, object]] = []
    for card_id, control in radial_controls.items():
        if not isinstance(control, dict):
            raise SystemExit(f"invalid radial control: {card_id}")
        if card_id not in mass_by_card:
            raise SystemExit(f"semantic mass missing: {card_id}")
        parts = str(card_id).split(":")
        if len(parts) < 4 or parts[0] != "ATOM":
            raise SystemExit(f"invalid atom card id: {card_id}")
        symbol = parts[1]
        z = int(control["Z"])
        exposure = float(control["radial_nuclear_exposure"])
        mass = mass_by_card[card_id]
        candidates = [
            c.as_dict()
            for c in atomic_subjective_time_candidates(
                symbol=symbol,
                z=z,
                radial_nuclear_exposure=exposure,
                semantic_mass=mass,
            )
        ]
        row_body = {
            "card_id": card_id,
            "symbol": symbol,
            "Z": z,
            "radial_nuclear_exposure": exposure,
            "semantic_mass": mass,
            "candidate_count": len(candidates),
            "candidates": candidates,
        }
        rows.append({**row_body, "row_sha256": sha256_json(row_body)})

    rows.sort(key=lambda row: int(row["Z"]))
    body: dict[str, object] = {
        "schema": SCHEMA,
        "version": "0.15.0",
        "status": "MODEL_SIDE_SUBJECTIVE_TIME_HYPOTHESES_FROZEN_FOR_FUTURE_HOLDOUT",
        "epistemic_status": "POST_STAGE_C_HYPOTHESIS_GENERATION_NOT_IONIZATION_EDGE_VALIDATION",
        "sources": {
            str(PREREG_PATH): sha256_bytes(prereg_raw),
            str(STAGE_A1_PATH): sha256_bytes(stage_a1_raw),
        },
        "kappa": KAPPA,
        "atom_count": len(rows),
        "candidate_policy_count": 5,
        "fit_parameters": [],
        "calibration_parameters": [],
        "stage_c_result_used_as_input": False,
        "nist_values_used_as_input": False,
        "future_holdout_required": True,
        "rows": rows,
        "interpretation": "NONE_IN_MODEL_SIDE_LEDGER",
        "canon_allowed": False,
    }
    return {**body, "ledger_sha256": sha256_json(body)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="out/ATOMIC_SUBJECTIVE_TIME_STAGE_D0_LEDGER_V0_15.json",
    )
    args = parser.parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    ledger = build_ledger()
    output.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", "utf-8")
    print(
        json.dumps(
            {
                "status": ledger["status"],
                "atom_count": ledger["atom_count"],
                "candidate_policy_count": ledger["candidate_policy_count"],
                "ledger_sha256": ledger["ledger_sha256"],
                "output": str(output),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
