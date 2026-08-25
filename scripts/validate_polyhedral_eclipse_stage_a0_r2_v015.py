#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_SCHEMA = "RESCHEM_POLYHEDRAL_ECLIPSE_STAGE_A0_GEOMETRY_LEDGER_V0_15"
EXPECTED_REVISION = "R2_AXIS_RESOLVED_TIR_SIC_PHASE"
EXPECTED_AXIS_SCHEMA = "RESCHEM_TIR_TETRAHEDRAL_SIC_AXIS_RESOLVED_PHASE_V0_15_R2"
EXPECTED_STATUS = "GEOMETRY_FEATURES_FROZEN_BEFORE_SEMANTIC_MASS_AND_SPECTRAL_JOIN"
EXPECTED_ATOMS = 6
EXPECTED_SPATIAL_FEATURES = 72
EXPECTED_AXES = {"x", "y", "z"}


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256_json(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _verify_hashed_record(record: dict, hash_field: str) -> None:
    expected = record.get(hash_field)
    if not isinstance(expected, str) or len(expected) != 64:
        raise ValueError(f"missing or malformed {hash_field}")
    body = {key: value for key, value in record.items() if key != hash_field}
    observed = _sha256_json(body)
    if observed != expected:
        raise ValueError(f"{hash_field} mismatch: {observed} != {expected}")


def validate(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != EXPECTED_SCHEMA:
        raise ValueError("Stage-A0 schema mismatch")
    if payload.get("revision") != EXPECTED_REVISION:
        raise ValueError("Stage-A0 R2 revision mismatch")
    if payload.get("status") != EXPECTED_STATUS:
        raise ValueError("Stage-A0 status mismatch")
    if payload.get("atom_count") != EXPECTED_ATOMS:
        raise ValueError("Stage-A0 atom count mismatch")
    if payload.get("spatial_feature_count") != EXPECTED_SPATIAL_FEATURES:
        raise ValueError("Stage-A0 spatial feature count mismatch")
    if payload.get("semantic_mass_join") != "PENDING_EXACT_PNCS_T36_BINDINGS":
        raise ValueError("semantic mass gate drift")
    spectral = payload.get("spectral_join", {})
    if spectral.get("status") != "WITHHELD_FOR_BLIND_COMPARISON" or spectral.get("accepted_observed_fields") != []:
        raise ValueError("blind spectral gate drift")

    atoms = payload.get("atoms")
    if not isinstance(atoms, list) or len(atoms) != EXPECTED_ATOMS:
        raise ValueError("atomic ledger population mismatch")

    spatial_count = 0
    for atom in atoms:
        if atom.get("semantic_mass_binding") != "PENDING_EXACT_PNCS_T36_BINDING":
            raise ValueError("atom semantic mass gate drift")
        if atom.get("observed_spectrum") != "WITHHELD_FOR_BLIND_COMPARISON":
            raise ValueError("atom spectral gate drift")
        inference = atom.get("tetrahedral_inference", {})
        axis_phase = inference.get("axis_resolved_phase", {})
        if axis_phase.get("schema") != EXPECTED_AXIS_SCHEMA:
            raise ValueError("axis-resolved phase schema mismatch")
        if axis_phase.get("selection_status") != "ALL_PREREGISTERED_AXES_PRESERVED":
            raise ValueError("axis selection contract drift")
        if axis_phase.get("spectral_join") != "WITHHELD_FOR_BLIND_COMPARISON":
            raise ValueError("axis spectral gate drift")
        axes = axis_phase.get("axes")
        if not isinstance(axes, dict) or set(axes) != EXPECTED_AXES:
            raise ValueError("axis set mismatch")
        for label in sorted(EXPECTED_AXES):
            row = axes[label]
            order = row.get("dominant_harmonic_order")
            strength = row.get("dominant_harmonic_strength")
            if isinstance(order, bool) or not isinstance(order, int) or order < 0:
                raise ValueError(f"invalid harmonic order for axis {label}")
            if not isinstance(strength, (int, float)) or float(strength) < 0.0:
                raise ValueError(f"invalid harmonic strength for axis {label}")

        spatial = atom.get("spatial_orbital_features")
        if not isinstance(spatial, list) or len(spatial) != 12:
            raise ValueError("expected 12 spatial orbital features per atom")
        for feature in spatial:
            _verify_hashed_record(feature, "feature_sha256")
        spatial_count += len(spatial)
        _verify_hashed_record(atom, "atomic_feature_sha256")

    if spatial_count != EXPECTED_SPATIAL_FEATURES:
        raise ValueError("recomputed spatial feature count mismatch")
    _verify_hashed_record(payload, "ledger_sha256")

    raw_sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
    return {
        "status": "PASS_EXACT_STAGE_A0_R2_LEDGER",
        "revision": payload["revision"],
        "atom_count": len(atoms),
        "spatial_feature_count": spatial_count,
        "ledger_sha256": payload["ledger_sha256"],
        "raw_file_sha256": raw_sha256,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Resonant Chemistry v0.15 Stage-A0 R2 ledger")
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(args.ledger), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
