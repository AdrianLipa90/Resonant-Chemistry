#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from reschem.atomic_t36_aufbau_v015 import basis_manifest, build_atomic_t36_candidate


PREREG_PATH = Path("benchmarks/ATOMIC_T36_AUFBAU_PHASE_CONTROL_PREREG_V0_15.json")
ATOM_INDEX_PATH = Path("semantic_cards/ATOM_CARD_INDEX_CURRENT.json")
MANIFEST_SCHEMA = "RESCHEM_ATOMIC_PNCS_SEMANTIC_MASS_BINDING_MANIFEST_V0_15"
EVIDENCE_SCHEMA = "RESCHEM_ATOMIC_T36_AUFBAU_PHASE_CONTROL_EVIDENCE_V0_15"


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256_json(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _load_json(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def _canonical_atom_sources() -> dict[str, tuple[dict, bytes, str]]:
    index = _load_json(ATOM_INDEX_PATH)
    out: dict[str, tuple[dict, bytes, str]] = {}
    for group in index["canonical_groups"]:
        for relpath_text in group["sources"]:
            relpath = Path(relpath_text)
            raw = relpath.read_bytes()
            if relpath.suffix == ".json":
                record = json.loads(raw)
                if isinstance(record, dict) and record.get("card_id"):
                    card_id = str(record["card_id"])
                    if card_id in out:
                        raise ValueError(f"duplicate canonical atom source: {card_id}")
                    out[card_id] = (record, raw, relpath.as_posix())
            elif relpath.suffix == ".jsonl":
                lines = raw.splitlines(keepends=True)
                for line_no, line in enumerate(lines, start=1):
                    if not line.strip():
                        continue
                    record = json.loads(line)
                    if not isinstance(record, dict) or not record.get("card_id"):
                        continue
                    card_id = str(record["card_id"])
                    if card_id in out:
                        raise ValueError(f"duplicate canonical atom source: {card_id}")
                    out[card_id] = (record, bytes(line), f"{relpath.as_posix()}#L{line_no}")
            else:
                raise ValueError(f"unsupported canonical atom source format: {relpath}")
    return out


def build_bindings() -> tuple[dict, dict]:
    prereg = _load_json(PREREG_PATH)
    if prereg.get("status") != "PREREGISTERED_BEFORE_SEMANTIC_MASS_EXECUTION":
        raise ValueError("Aufbau-36 preregistration status drift")
    if prereg.get("spectral_input") != "PROHIBITED":
        raise ValueError("Aufbau-36 spectral boundary drift")

    sources = _canonical_atom_sources()
    requested = [str(card_id) for card_id in prereg["initial_execution_cohort"]]
    candidates = []
    bindings = []
    for card_id in requested:
        if card_id not in sources:
            raise ValueError(f"canonical atom source unavailable: {card_id}")
        card, raw, locator = sources[card_id]
        identity = card.get("identity", {})
        physical = card.get("physical_control", {})
        electron_count = int(identity["electron_count"])
        configuration = str(physical["electron_configuration"])
        candidate = build_atomic_t36_candidate(
            atom_card_id=card_id,
            electron_configuration=configuration,
            electron_count=electron_count,
            source_raw=raw,
            source_locator=locator,
        )
        candidates.append(candidate)
        bindings.append(
            {
                "atom_card_id": card_id,
                "phase_index": candidate["phase_index"],
                "phase36": candidate["phase36"],
                "realization_id": candidate["pncs_v018"]["realization_id"],
                "realization_binding_id": candidate["pncs_v018"]["binding_id"],
                "source_binding_id": candidate["pncs_v019"]["mass_binding_id"],
                "semantic_mass": candidate["semantic_mass"],
                "order_parameter_R": candidate["order_parameter_R"],
                "phase36_sha256": candidate["phase36_sha256"],
                "source_digest_sha256": candidate["source_digest_sha256"],
                "candidate_sha256": candidate["candidate_sha256"],
                "epistemic_operator": "CHYBA",
                "canon_allowed": False,
            }
        )

    manifest_body = {
        "schema": MANIFEST_SCHEMA,
        "status": "PREREGISTERED_CANDIDATE_BINDINGS_FROZEN_BEFORE_SPECTRAL_JOIN",
        "preregister_source": str(PREREG_PATH),
        "basis": basis_manifest(),
        "binding_count": len(bindings),
        "bindings": bindings,
        "spectral_join": {
            "status": "WITHHELD_FOR_BLIND_COMPARISON",
            "accepted_observed_fields": [],
        },
        "epistemic_operator": "CHYBA",
        "canon_allowed": False,
    }
    manifest = {**manifest_body, "manifest_sha256": _sha256_json(manifest_body)}

    evidence_body = {
        "schema": EVIDENCE_SCHEMA,
        "status": "A1_ATOM_TO_T36_CANDIDATE_EVIDENCE_FROZEN",
        "preregister_source": str(PREREG_PATH),
        "manifest_sha256": manifest["manifest_sha256"],
        "candidate_count": len(candidates),
        "candidates": candidates,
        "spectral_input": "NONE",
        "epistemic_operator": "CHYBA",
        "canon_allowed": False,
    }
    evidence = {**evidence_body, "evidence_sha256": _sha256_json(evidence_body)}
    return manifest, evidence


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze preregistered Resonant Chemistry v0.15 Aufbau-36 PNCS bindings")
    parser.add_argument("--manifest-output", type=Path, required=True)
    parser.add_argument("--evidence-output", type=Path, required=True)
    args = parser.parse_args()

    manifest, evidence = build_bindings()
    args.manifest_output.parent.mkdir(parents=True, exist_ok=True)
    args.evidence_output.parent.mkdir(parents=True, exist_ok=True)
    args.manifest_output.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    args.evidence_output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": manifest["status"],
                "binding_count": manifest["binding_count"],
                "manifest_sha256": manifest["manifest_sha256"],
                "evidence_sha256": evidence["evidence_sha256"],
                "manifest_output": str(args.manifest_output),
                "evidence_output": str(args.evidence_output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
