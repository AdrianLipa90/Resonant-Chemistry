from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

INPUT_SCHEMA = "GREMLIN_RESIDUAL_PRESERVING_SPECTROSCOPY_V0_2"
SCHEMA = "RESCHEM_RESIDUAL_SPECTROSCOPY_BRIDGE_V0_1"
_ALLOWED = {
    "STOCHASTIC_BACKGROUND_COMPATIBLE",
    "SYSTEMATIC_OR_INSTRUMENTAL_CANDIDATE",
    "SYSTEMATIC_DRIFT_CANDIDATE",
    "KNOWN_MODEL_STRUCTURE_CANDIDATE",
    "PERSISTENT_OFFSET_CANDIDATE",
    "UNRESOLVED_STRUCTURED_CANDIDATE",
    "UNRESOLVED_RESIDUAL",
}

def validate_residual_packet(packet: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(packet, Mapping):
        raise ValueError("packet must be mapping")
    if packet.get("schema") != INPUT_SCHEMA:
        raise ValueError("unsupported residual packet schema")
    if packet.get("classification") not in _ALLOWED:
        raise ValueError("unsupported residual classification")
    policy = packet.get("policy")
    if not isinstance(policy, Mapping):
        raise ValueError("policy missing")
    required = {
        "raw_preserved": True,
        "residual_preserved": True,
        "destructive_denoising": False,
        "interpretation_last": True,
        "new_physics_from_residual_only": False,
        "time_fluctuation_claim_allowed": False,
    }
    for key, value in required.items():
        if policy.get(key) is not value:
            raise ValueError(f"unsafe residual policy: {key}")
    commitments = packet.get("commitments")
    if not isinstance(commitments, Mapping):
        raise ValueError("missing residual commitments")
    for key in ("raw_sha256", "model_sha256", "residual_sha256"):
        value = commitments.get(key)
        if not isinstance(value, str) or len(value) != 64:
            raise ValueError("missing residual commitments")
    return dict(packet)

def attach_residual_diagnostics(
    spectrum_payload: Mapping[str, Any],
    residual_packet: Mapping[str, Any],
) -> dict[str, Any]:
    if not isinstance(spectrum_payload, Mapping):
        raise ValueError("spectrum_payload must be mapping")
    packet = validate_residual_packet(residual_packet)
    spectrum = json.loads(json.dumps(spectrum_payload, sort_keys=True, allow_nan=False))
    before = hashlib.sha256(
        json.dumps(spectrum, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    out = {
        "schema": SCHEMA,
        "spectrum": spectrum,
        "spectrum_sha256": before,
        "residual_diagnostics": {
            "classification": packet["classification"],
            "analysis_sha256": packet["analysis_sha256"],
            "commitments": packet["commitments"],
            "metrics": packet["metrics"],
        },
        "claims": {
            "spectrum_modified_by_residual_layer": False,
            "residual_is_chemical_assignment": False,
            "new_physics_established": False,
            "time_fluctuation_established": False,
        },
        "promotion_gates": list(packet.get("promotion_gates", [])),
    }
    after = hashlib.sha256(
        json.dumps(out["spectrum"], sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if before != after:
        raise RuntimeError("residual bridge mutated spectrum")
    out["bridge_sha256"] = hashlib.sha256(
        json.dumps(out, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()
    return out
