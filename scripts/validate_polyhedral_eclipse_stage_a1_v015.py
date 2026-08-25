#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_SCHEMA = "RESCHEM_POLYHEDRAL_ECLIPSE_STAGE_A_LEDGER_V0_15"
EXPECTED_STATUS = "FEATURES_FROZEN_BEFORE_SPECTRAL_JOIN"
EXPECTED_FEATURES = 72
EXPECTED_CARDS = {
    "ATOM:B:11:q+0",
    "ATOM:C:12:q+0",
    "ATOM:N:14:q+0",
    "ATOM:O:16:q+0",
    "ATOM:F:19:q+0",
    "ATOM:Ne:20:q+0",
}


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256_json(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _verify_hash(record: dict, field: str) -> None:
    recorded = record.get(field)
    if not isinstance(recorded, str) or len(recorded) != 64:
        raise ValueError(f"missing or malformed {field}")
    body = dict(record)
    body.pop(field)
    computed = _sha256_json(body)
    if computed != recorded:
        raise ValueError(f"{field} mismatch: {computed} != {recorded}")


def validate(stage_a_path: Path, binding_manifest_path: Path) -> dict:
    payload = json.loads(stage_a_path.read_text(encoding="utf-8"))
    if payload.get("schema") != EXPECTED_SCHEMA:
        raise ValueError("Stage-A1 schema mismatch")
    if payload.get("status") != EXPECTED_STATUS:
        raise ValueError("Stage-A1 status mismatch")
    if payload.get("feature_count") != EXPECTED_FEATURES:
        raise ValueError("Stage-A1 feature count mismatch")
    if payload.get("spectral_join") != {"status": "WITHHELD_FOR_BLIND_COMPARISON", "accepted_observed_fields": []}:
        raise ValueError("Stage-A1 spectral boundary drift")
    raw_manifest_sha = hashlib.sha256(binding_manifest_path.read_bytes()).hexdigest()
    if payload.get("binding_manifest_sha256") != raw_manifest_sha:
        raise ValueError("Stage-A1 binding manifest raw SHA mismatch")

    radial_controls = payload.get("radial_controls")
    overlays = payload.get("semantic_mass_overlays")
    features = payload.get("features")
    if not isinstance(radial_controls, dict) or set(radial_controls) != EXPECTED_CARDS:
        raise ValueError("Stage-A1 radial-control cohort drift")
    if not isinstance(overlays, list) or len(overlays) != 6:
        raise ValueError("Stage-A1 semantic-mass overlay count drift")
    if not isinstance(features, list) or len(features) != EXPECTED_FEATURES:
        raise ValueError("Stage-A1 feature population drift")

    overlay_cards = {overlay.get("card_id") for overlay in overlays}
    if overlay_cards != EXPECTED_CARDS:
        raise ValueError("Stage-A1 semantic-mass overlay cohort drift")
    for overlay in overlays:
        tir = overlay.get("tir", {})
        semantic_axes = tir.get("semantic_axes", {})
        semantic_mass = semantic_axes.get("values", {}).get("semantic_mass", {})
        if semantic_axes.get("status") != "PNCS_V0_19_BOUND_CHYBA":
            raise ValueError(f"semantic-mass overlay status drift: {overlay.get('card_id')}")
        if not isinstance(semantic_mass.get("value"), (int, float)):
            raise ValueError(f"semantic-mass overlay value missing: {overlay.get('card_id')}")

    counts: dict[str, int] = {card_id: 0 for card_id in EXPECTED_CARDS}
    coupling_summary: dict[str, list[float]] = {card_id: [] for card_id in EXPECTED_CARDS}
    mass_summary: dict[str, float] = {}
    for feature in features:
        _verify_hash(feature, "feature_sha256")
        card_id = feature.get("atom_card_id")
        if card_id not in EXPECTED_CARDS:
            raise ValueError(f"unexpected Stage-A1 feature card: {card_id}")
        counts[card_id] += 1
        probe = feature.get("probe")
        if not isinstance(probe, dict) or probe.get("schema") != "RESCHEM_POLYHEDRAL_ECLIPSE_PROBE_V0_15":
            raise ValueError(f"probe schema drift: {card_id}")
        if probe.get("epistemic_status", {}).get("spectral_validation") != "BLIND_COMPARISON_PENDING":
            raise ValueError(f"probe spectral status drift: {card_id}")
        phase = probe.get("phase", {})
        if phase.get("frequency_mapping_status") != "REQUIRES_INDEPENDENT_PHASE_RATE":
            raise ValueError(f"phase-rate boundary drift: {card_id}")
        semantic_mass = probe.get("semantic_mass", {})
        nuclear_exposure = probe.get("nuclear_exposure", {})
        value = semantic_mass.get("value")
        coupling = nuclear_exposure.get("eclipse_coupling")
        if not isinstance(value, (int, float)) or not isinstance(coupling, (int, float)):
            raise ValueError(f"mass/coupling missing: {card_id}")
        if card_id in mass_summary and mass_summary[card_id] != float(value):
            raise ValueError(f"semantic mass drift across probes: {card_id}")
        mass_summary[card_id] = float(value)
        coupling_summary[card_id].append(float(coupling))

    if any(count != 12 for count in counts.values()):
        raise ValueError(f"expected 12 Stage-A1 probes per atom, got {counts}")
    _verify_hash(payload, "ledger_sha256")

    text = stage_a_path.read_text(encoding="utf-8").lower()
    for forbidden in ("observed_wavelength", "observed_wavenumber", "oscillator_strength", "line_intensity"):
        if forbidden in text:
            raise ValueError(f"forbidden spectral field present: {forbidden}")

    return {
        "status": "PASS_STAGE_A1_MASS_WEIGHTED_LEDGER",
        "feature_count": EXPECTED_FEATURES,
        "ledger_sha256": payload["ledger_sha256"],
        "raw_file_sha256": hashlib.sha256(stage_a_path.read_bytes()).hexdigest(),
        "binding_manifest_raw_sha256": raw_manifest_sha,
        "semantic_mass_by_card": mass_summary,
        "eclipse_coupling_minmax_by_card": {
            card_id: [min(values), max(values)] for card_id, values in coupling_summary.items()
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Resonant Chemistry v0.15 Stage-A1 mass-weighted ledger")
    parser.add_argument("--stage-a", type=Path, required=True)
    parser.add_argument("--bindings", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(validate(args.stage_a, args.bindings), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
