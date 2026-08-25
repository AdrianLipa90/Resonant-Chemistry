#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from reschem.orbital_basis_v015 import P_ORBITAL_BASIS_ID, p_orbital_basis_manifest, real_p_coefficients
from reschem.polyhedral_eclipse_spectroscopy import (
    PolyhedralConePartition,
    cone_probabilities,
    dominant_harmonic,
    eclipse_phase_trace,
    fibonacci_sphere,
    orbital_angular_density,
    period2_p_radial_control_exposure,
    polyhedral_information_nats,
    shannon_information_nats,
)
from reschem.repository_cards import load_current_card_registry
from reschem.tetrahedral_inference_v015 import (
    TETRAHEDRAL_SIC_CONTRACT_ID,
    build_tetrahedral_inference_probe,
    period2_p_spin_bloch_control,
)


PREREG_PATH = Path("benchmarks/POLYHEDRAL_ECLIPSE_SPECTROSCOPY_PREREG_V0_15.json")
SPATIAL_CONTROL_GEOMETRIES = ("tetrahedron", "octahedron", "cube", "icosahedron")
P_STATES = ("p_x", "p_y", "p_z")


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256_json(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _load_prereg() -> dict:
    return json.loads(PREREG_PATH.read_text(encoding="utf-8"))


def _spatial_orbital_feature(
    geometry: str,
    orbital_label: str,
    *,
    sample_count: int,
    phase_samples: int,
) -> dict:
    partition = PolyhedralConePartition.regular(geometry)
    coefficients = real_p_coefficients(orbital_label)
    directions = fibonacci_sphere(sample_count)
    density = orbital_angular_density(1, coefficients, directions)
    probabilities = cone_probabilities(partition, directions, density)
    solid_angles = partition.solid_angle_fractions(sample_count)
    trace = eclipse_phase_trace(
        partition,
        1,
        coefficients,
        sample_count=max(1024, sample_count // 2),
        phase_samples=phase_samples,
    )
    harmonic_order, harmonic_strength = dominant_harmonic(trace)
    body = {
        "spatial_partition": geometry,
        "orbital_basis_id": P_ORBITAL_BASIS_ID,
        "orbital_label": orbital_label,
        "cone_probabilities": [float(value) for value in probabilities],
        "solid_angle_fractions": [float(value) for value in solid_angles],
        "shannon_information_nats": shannon_information_nats(probabilities),
        "polyhedral_information_nats": polyhedral_information_nats(probabilities, solid_angles),
        "dominant_orbital_band_harmonic_order": harmonic_order,
        "dominant_orbital_band_harmonic_strength": harmonic_strength,
        "role": (
            "TETRAHEDRAL_SPATIAL_PROJECTION_CONTROL"
            if geometry == "tetrahedron"
            else "ALTERNATIVE_SPATIAL_PARTITION_CONTROL"
        ),
    }
    return {**body, "feature_sha256": _sha256_json(body)}


def build_stage_a0_ledger(*, sample_count: int, phase_samples: int) -> dict:
    prereg = _load_prereg()
    registry = load_current_card_registry()
    atomic_rows = []

    for cohort_row in prereg["initial_atomic_cohort"]:
        card_id = cohort_row["card_id"]
        card = registry.resolve(card_id)
        identity = card["identity"]
        z = int(identity["Z"])
        a = int(identity["A"])
        if a != int(cohort_row["A"]):
            raise ValueError(f"atomic-card A drift for {card_id}: {a} != {cohort_row['A']}")

        radial = period2_p_radial_control_exposure(z)
        spin = period2_p_spin_bloch_control(z)
        inference = build_tetrahedral_inference_probe(
            spin["bloch_vector"],
            phase_samples=phase_samples,
        ).as_dict()
        if inference["schema"] != TETRAHEDRAL_SIC_CONTRACT_ID:
            raise RuntimeError("tetrahedral inference schema drift")

        spatial = [
            _spatial_orbital_feature(
                geometry,
                orbital_label,
                sample_count=sample_count,
                phase_samples=phase_samples,
            )
            for geometry in SPATIAL_CONTROL_GEOMETRIES
            for orbital_label in P_STATES
        ]
        row = {
            "atom_card_id": card_id,
            "symbol": identity["symbol"],
            "Z": z,
            "A": a,
            "radial_control": radial,
            "subshell_spin_control": spin,
            "tetrahedral_inference": inference,
            "spatial_orbital_features": spatial,
            "semantic_mass_binding": "PENDING_EXACT_PNCS_T36_BINDING",
            "observed_spectrum": "WITHHELD_FOR_BLIND_COMPARISON",
        }
        atomic_rows.append({**row, "atomic_feature_sha256": _sha256_json(row)})

    body = {
        "schema": "RESCHEM_POLYHEDRAL_ECLIPSE_STAGE_A0_GEOMETRY_LEDGER_V0_15",
        "status": "GEOMETRY_FEATURES_FROZEN_BEFORE_SEMANTIC_MASS_AND_SPECTRAL_JOIN",
        "preregister_source": str(PREREG_PATH),
        "orbital_basis": p_orbital_basis_manifest(),
        "primary_inference_geometry": TETRAHEDRAL_SIC_CONTRACT_ID,
        "spatial_partition_controls": list(SPATIAL_CONTROL_GEOMETRIES),
        "sampling": {
            "sphere_samples": int(sample_count),
            "phase_samples": int(phase_samples),
        },
        "atom_count": len(atomic_rows),
        "spatial_feature_count": sum(len(row["spatial_orbital_features"]) for row in atomic_rows),
        "atoms": atomic_rows,
        "semantic_mass_join": "PENDING_EXACT_PNCS_T36_BINDINGS",
        "spectral_join": {
            "status": "WITHHELD_FOR_BLIND_COMPARISON",
            "accepted_observed_fields": [],
        },
    }
    return {**body, "ledger_sha256": _sha256_json(body)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze Resonant Chemistry v0.15 Stage-A0 geometry features")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--sample-count", type=int, default=8192)
    parser.add_argument("--phase-samples", type=int, default=128)
    args = parser.parse_args()

    ledger = build_stage_a0_ledger(
        sample_count=args.sample_count,
        phase_samples=args.phase_samples,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": ledger["status"],
                "atom_count": ledger["atom_count"],
                "spatial_feature_count": ledger["spatial_feature_count"],
                "ledger_sha256": ledger["ledger_sha256"],
                "output": str(args.output),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
