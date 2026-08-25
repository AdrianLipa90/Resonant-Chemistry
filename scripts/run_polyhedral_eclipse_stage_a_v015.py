#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from reschem.orbital_basis_v015 import P_ORBITAL_BASIS_ID, p_orbital_basis_manifest, real_p_coefficients
from reschem.pncs_semantic_mass_bridge_v015 import binding_from_manifest_entry
from reschem.polyhedral_eclipse_spectroscopy import (
    PolyhedralConePartition,
    build_orbital_eclipse_probe,
    period2_p_radial_control_exposure,
)
from reschem.repository_cards import load_current_card_registry


PREREG_PATH = Path("benchmarks/POLYHEDRAL_ECLIPSE_SPECTROSCOPY_PREREG_V0_15.json")
GEOMETRIES = ("tetrahedron", "octahedron", "cube", "icosahedron")
P_STATES = ("p_x", "p_y", "p_z")


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256_json(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_binding_entries(path: Path) -> list[dict]:
    payload = _load_json(path)
    if not isinstance(payload, dict):
        raise ValueError("binding manifest must be a JSON object")
    if payload.get("schema") != "RESCHEM_ATOMIC_PNCS_SEMANTIC_MASS_BINDING_MANIFEST_V0_15":
        raise ValueError(f"unexpected binding manifest schema: {payload.get('schema')}")
    rows = payload.get("bindings")
    if not isinstance(rows, list) or not rows:
        raise ValueError("binding manifest requires a non-empty bindings list")
    return [dict(row) for row in rows]


def build_stage_a_ledger(
    bindings_path: Path,
    *,
    sample_count: int,
    phase_samples: int,
) -> dict:
    prereg = _load_json(PREREG_PATH)
    registry = load_current_card_registry()
    raw_entries = _load_binding_entries(bindings_path)
    bindings = [binding_from_manifest_entry(row) for row in raw_entries]
    by_card = {binding.atom_card_id: binding for binding in bindings}
    if len(by_card) != len(bindings):
        raise ValueError("duplicate atom_card_id in semantic-mass binding manifest")

    cohort = prereg["initial_atomic_cohort"]
    required_cards = [row["card_id"] for row in cohort]
    missing = [card_id for card_id in required_cards if card_id not in by_card]
    extras = sorted(set(by_card) - set(required_cards))
    if missing:
        raise ValueError(f"missing required atom-to-PNCS bindings: {missing}")
    if extras:
        raise ValueError(f"unexpected atom bindings outside preregistered cohort: {extras}")

    features = []
    radial_controls = {}
    overlays = []
    for cohort_row in cohort:
        card_id = cohort_row["card_id"]
        binding = by_card[card_id]
        card = registry.resolve(card_id)
        identity = card.get("identity", {})
        z = int(identity["Z"])
        a = int(identity["A"])
        if a != int(cohort_row["A"]):
            raise ValueError(f"atomic-card A drift for {card_id}: {a} != {cohort_row['A']}")

        radial = period2_p_radial_control_exposure(z)
        radial_controls[card_id] = radial
        overlays.append(binding.overlay_record)

        for geometry in GEOMETRIES:
            partition = PolyhedralConePartition.regular(geometry)
            for orbital_label in P_STATES:
                probe = build_orbital_eclipse_probe(
                    partition=partition,
                    l=1,
                    coefficients=real_p_coefficients(orbital_label),
                    nucleon_count=a,
                    semantic_mass=binding.semantic_mass,
                    semantic_mass_provenance=(
                        f"pncs-v0.19:{binding.source_binding_id}:{binding.payload['bridge_sha256']}"
                    ),
                    radial_nuclear_exposure=float(radial["radial_nuclear_exposure"]),
                    sample_count=sample_count,
                    phase_samples=phase_samples,
                ).as_dict()
                row = {
                    "atom_card_id": card_id,
                    "symbol": identity["symbol"],
                    "Z": z,
                    "A": a,
                    "orbital_basis_id": P_ORBITAL_BASIS_ID,
                    "orbital_label": orbital_label,
                    "polyhedron": geometry,
                    "probe": probe,
                }
                features.append({**row, "feature_sha256": _sha256_json(row)})

    body = {
        "schema": "RESCHEM_POLYHEDRAL_ECLIPSE_STAGE_A_LEDGER_V0_15",
        "status": "FEATURES_FROZEN_BEFORE_SPECTRAL_JOIN",
        "preregister_source": str(PREREG_PATH),
        "binding_manifest_source": str(bindings_path),
        "binding_manifest_sha256": hashlib.sha256(bindings_path.read_bytes()).hexdigest(),
        "orbital_basis": p_orbital_basis_manifest(),
        "sampling": {
            "sphere_samples": int(sample_count),
            "phase_samples": int(phase_samples),
        },
        "radial_controls": radial_controls,
        "semantic_mass_overlays": overlays,
        "feature_count": len(features),
        "features": features,
        "spectral_join": {
            "status": "WITHHELD_FOR_BLIND_COMPARISON",
            "accepted_observed_fields": [],
        },
    }
    return {**body, "ledger_sha256": _sha256_json(body)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze Resonant Chemistry v0.15 Stage-A polyhedral eclipse features")
    parser.add_argument("--bindings", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-count", type=int, default=8192)
    parser.add_argument("--phase-samples", type=int, default=128)
    args = parser.parse_args()

    ledger = build_stage_a_ledger(
        args.bindings,
        sample_count=args.sample_count,
        phase_samples=args.phase_samples,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": ledger["status"],
                "feature_count": ledger["feature_count"],
                "ledger_sha256": ledger["ledger_sha256"],
                "output": str(args.output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
