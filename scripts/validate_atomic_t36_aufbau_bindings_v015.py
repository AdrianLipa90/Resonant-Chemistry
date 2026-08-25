#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from reschem.atomic_t36_aufbau_v015 import CANDIDATE_SCHEMA, PREREG_SCHEMA, phase36_sha256
from reschem.pncs_semantic_mass_bridge_v015 import binding_from_manifest_entry

MANIFEST_SCHEMA = "RESCHEM_ATOMIC_PNCS_SEMANTIC_MASS_BINDING_MANIFEST_V0_15"
EVIDENCE_SCHEMA = "RESCHEM_ATOMIC_T36_AUFBAU_PHASE_CONTROL_EVIDENCE_V0_15"
EXPECTED_CARDS = (
    "ATOM:B:11:q+0",
    "ATOM:C:12:q+0",
    "ATOM:N:14:q+0",
    "ATOM:O:16:q+0",
    "ATOM:F:19:q+0",
    "ATOM:Ne:20:q+0",
)


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
    if recorded != computed:
        raise ValueError(f"{field} mismatch: {computed} != {recorded}")


def validate(manifest_path: Path, evidence_path: Path) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise ValueError("binding manifest schema mismatch")
    if manifest.get("binding_count") != 6:
        raise ValueError("binding manifest count mismatch")
    if manifest.get("spectral_join") != {"status": "WITHHELD_FOR_BLIND_COMPARISON", "accepted_observed_fields": []}:
        raise ValueError("binding manifest spectral boundary drift")
    if manifest.get("epistemic_operator") != "CHYBA" or manifest.get("canon_allowed") is not False:
        raise ValueError("binding manifest epistemic boundary drift")
    _verify_hash(manifest, "manifest_sha256")

    if evidence.get("schema") != EVIDENCE_SCHEMA:
        raise ValueError("binding evidence schema mismatch")
    if evidence.get("candidate_count") != 6:
        raise ValueError("binding evidence count mismatch")
    if evidence.get("spectral_input") != "NONE":
        raise ValueError("binding evidence spectral input drift")
    if evidence.get("epistemic_operator") != "CHYBA" or evidence.get("canon_allowed") is not False:
        raise ValueError("binding evidence epistemic boundary drift")
    if evidence.get("manifest_sha256") != manifest["manifest_sha256"]:
        raise ValueError("evidence-to-manifest SHA linkage mismatch")
    _verify_hash(evidence, "evidence_sha256")

    bindings = manifest.get("bindings")
    candidates = evidence.get("candidates")
    if not isinstance(bindings, list) or not isinstance(candidates, list):
        raise ValueError("binding/evidence rows must be lists")
    by_binding = {row["atom_card_id"]: row for row in bindings}
    by_candidate = {row["atom_card_id"]: row for row in candidates}
    if tuple(by_binding) != EXPECTED_CARDS or tuple(by_candidate) != EXPECTED_CARDS:
        raise ValueError("binding cohort order/content drift")

    masses = {}
    order_parameters = {}
    for card_id in EXPECTED_CARDS:
        row = by_binding[card_id]
        candidate = by_candidate[card_id]
        if candidate.get("schema") != CANDIDATE_SCHEMA or candidate.get("prereg_schema") != PREREG_SCHEMA:
            raise ValueError(f"candidate schema drift: {card_id}")
        if candidate.get("spectral_input") != "NONE":
            raise ValueError(f"candidate spectral input drift: {card_id}")
        if candidate.get("epistemic_operator") != "CHYBA" or candidate.get("canon_allowed") is not False:
            raise ValueError(f"candidate epistemic drift: {card_id}")
        if candidate.get("phase_index") != candidate.get("electron_count"):
            raise ValueError(f"explicit phase-index/electron-count mismatch: {card_id}")
        occupancy = candidate.get("occupancy36")
        phase36 = candidate.get("phase36")
        if not isinstance(occupancy, list) or len(occupancy) != 36 or sum(occupancy) != candidate["electron_count"]:
            raise ValueError(f"occupancy36 drift: {card_id}")
        if not isinstance(phase36, list) or len(phase36) != 36:
            raise ValueError(f"phase36 length drift: {card_id}")
        if phase36_sha256(phase36) != candidate.get("phase36_sha256"):
            raise ValueError(f"phase36 SHA drift: {card_id}")
        _verify_hash(candidate, "candidate_sha256")

        if row.get("candidate_sha256") != candidate["candidate_sha256"]:
            raise ValueError(f"manifest candidate linkage drift: {card_id}")
        if row.get("phase36_sha256") != candidate["phase36_sha256"]:
            raise ValueError(f"manifest phase linkage drift: {card_id}")
        if row.get("source_digest_sha256") != candidate["source_digest_sha256"]:
            raise ValueError(f"manifest source linkage drift: {card_id}")
        if row.get("source_binding_id") != candidate["pncs_v019"]["mass_binding_id"]:
            raise ValueError(f"manifest PNCS mass-binding linkage drift: {card_id}")
        if row.get("realization_id") != candidate["pncs_v018"]["realization_id"]:
            raise ValueError(f"manifest realization linkage drift: {card_id}")
        if row.get("realization_binding_id") != candidate["pncs_v018"]["binding_id"]:
            raise ValueError(f"manifest realization-binding linkage drift: {card_id}")
        bridge = binding_from_manifest_entry(row)
        if bridge.semantic_mass != row.get("semantic_mass") or bridge.semantic_mass != candidate.get("semantic_mass"):
            raise ValueError(f"semantic mass parity drift: {card_id}")
        if abs(bridge.order_parameter_R - float(row["order_parameter_R"])) > 1.0e-12:
            raise ValueError(f"order parameter parity drift: {card_id}")
        masses[card_id] = bridge.semantic_mass
        order_parameters[card_id] = bridge.order_parameter_R

    text = (manifest_path.read_text(encoding="utf-8") + evidence_path.read_text(encoding="utf-8")).lower()
    for forbidden in ("observed_wavelength", "observed_wavenumber", "oscillator_strength", "line_intensity"):
        if forbidden in text:
            raise ValueError(f"forbidden spectral field present: {forbidden}")

    return {
        "status": "PASS_A1_AUFBAU36_BINDINGS",
        "binding_count": 6,
        "manifest_sha256": manifest["manifest_sha256"],
        "evidence_sha256": evidence["evidence_sha256"],
        "manifest_raw_sha256": hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        "evidence_raw_sha256": hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
        "semantic_mass_by_card": masses,
        "order_parameter_R_by_card": order_parameters,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Resonant Chemistry v0.15 Aufbau-36 binding artifacts")
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(validate(args.manifest, args.evidence), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
