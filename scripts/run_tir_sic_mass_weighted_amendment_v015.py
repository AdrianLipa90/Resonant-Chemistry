#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

KAPPA = math.log(2.0) / (24.0 * math.pi)
AMENDMENT_PATH = Path("benchmarks/TIR_SIC_MASS_WEIGHTED_AMENDMENT_V0_15.json")
R2_PATH = Path("benchmarks/POLYHEDRAL_ECLIPSE_STAGE_A0_R2_LEDGER_V0_15.json")
A1_PATH = Path("benchmarks/POLYHEDRAL_ECLIPSE_STAGE_A1_LEDGER_V0_15.json")
MASS_PATH = Path("benchmarks/ATOMIC_PNCS_SEMANTIC_MASS_BINDINGS_V0_15.json")
EXPECTED_R2_INTERNAL = "e3438d2e090db378b566eb31b0b03159fca407bee2826c400d8e82099a00f39a"
EXPECTED_A1_INTERNAL = "ecb01b00831140bfc71483ec1f7f64dc69e25929868cafe05d99651390c898f6"
EXPECTED_MASS_INTERNAL = "c7077f59eceaa6217e03ee59a3edfb394a4bbfb4c84d0e16849459f80c2e6f47"
OUTPUT_SCHEMA = "RESCHEM_TIR_SIC_MASS_WEIGHTED_LEDGER_V0_15"


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256_json(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _raw_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def build_ledger() -> dict:
    amendment = _load(AMENDMENT_PATH)
    r2 = _load(R2_PATH)
    a1 = _load(A1_PATH)
    mass = _load(MASS_PATH)

    if amendment.get("status") != "POST_A1_MODEL_SIDE_AMENDMENT_FROZEN_BEFORE_SPECTRAL_JOIN":
        raise ValueError("amendment status drift")
    if amendment.get("timeline_boundary", {}).get("observed_spectrum_accessed_for_amendment") is not False:
        raise ValueError("amendment spectral boundary drift")
    if r2.get("ledger_sha256") != EXPECTED_R2_INTERNAL:
        raise ValueError("Stage-A0 R2 internal SHA drift")
    if a1.get("ledger_sha256") != EXPECTED_A1_INTERNAL:
        raise ValueError("Stage-A1 internal SHA drift")
    if mass.get("manifest_sha256") != EXPECTED_MASS_INTERNAL:
        raise ValueError("semantic-mass manifest internal SHA drift")
    if r2.get("spectral_join") != {"status": "WITHHELD_FOR_BLIND_COMPARISON", "accepted_observed_fields": []}:
        raise ValueError("R2 spectral boundary drift")
    if a1.get("spectral_join") != {"status": "WITHHELD_FOR_BLIND_COMPARISON", "accepted_observed_fields": []}:
        raise ValueError("A1 spectral boundary drift")
    if mass.get("spectral_join") != {"status": "WITHHELD_FOR_BLIND_COMPARISON", "accepted_observed_fields": []}:
        raise ValueError("mass manifest spectral boundary drift")

    mass_by_card = {row["atom_card_id"]: row for row in mass["bindings"]}
    rows = []
    for atom in r2["atoms"]:
        card_id = atom["atom_card_id"]
        binding = mass_by_card.get(card_id)
        if binding is None:
            raise ValueError(f"semantic mass binding missing: {card_id}")
        a = int(atom["A"])
        semantic_mass = float(binding["semantic_mass"])
        mu_s = semantic_mass / float(a)
        chi_r = float(atom["radial_control"]["radial_nuclear_exposure"])
        inference = atom["tetrahedral_inference"]
        i_sic = float(inference["sic_information_nats"])
        eta_sic = i_sic / (float(a) * KAPPA)
        e_sic = mu_s * eta_sic * chi_r
        axis = inference["axis_resolved_phase"]
        if axis.get("selection_status") != "ALL_PREREGISTERED_AXES_PRESERVED":
            raise ValueError(f"axis selection status drift: {card_id}")
        axes = axis["axes"]
        if set(axes) != {"x", "y", "z"}:
            raise ValueError(f"axis population drift: {card_id}")

        body = {
            "atom_card_id": card_id,
            "symbol": atom["symbol"],
            "Z": int(atom["Z"]),
            "A": a,
            "radial_nuclear_exposure": chi_r,
            "semantic_mass": semantic_mass,
            "semantic_mass_per_nucleon": mu_s,
            "sic_information_nats": i_sic,
            "sic_information_ratio_to_nucleons": eta_sic,
            "primary_tir_sic_eclipse_coupling": e_sic,
            "axis_resolved_phase": {
                "x": dict(axes["x"]),
                "y": dict(axes["y"]),
                "z": dict(axes["z"]),
                "selection_status": "ALL_PREREGISTERED_AXES_PRESERVED",
            },
            "semantic_mass_binding_id": binding["source_binding_id"],
            "semantic_mass_candidate_sha256": binding["candidate_sha256"],
            "epistemic_operator": "CHYBA",
            "canon_allowed": False,
            "spectral_join": "WITHHELD_FOR_BLIND_COMPARISON",
        }
        rows.append({**body, "row_sha256": _sha256_json(body)})

    body = {
        "schema": OUTPUT_SCHEMA,
        "status": "PRIMARY_TIR_SIC_MASS_WEIGHTED_FEATURES_FROZEN_BEFORE_SPECTRAL_JOIN",
        "amendment_source": str(AMENDMENT_PATH),
        "source_lineage": {
            "stage_a0_r2": {"path": str(R2_PATH), "raw_sha256": _raw_sha(R2_PATH), "internal_sha256": EXPECTED_R2_INTERNAL},
            "stage_a1": {"path": str(A1_PATH), "raw_sha256": _raw_sha(A1_PATH), "internal_sha256": EXPECTED_A1_INTERNAL},
            "semantic_mass_manifest": {"path": str(MASS_PATH), "raw_sha256": _raw_sha(MASS_PATH), "internal_sha256": EXPECTED_MASS_INTERNAL},
        },
        "kappa": KAPPA,
        "formula": {
            "eta_sic": "I_SIC/(A*kappa)",
            "mu_s": "M_s/A",
            "primary_tir_sic_eclipse_coupling": "mu_s*eta_sic*chi_r",
        },
        "row_count": len(rows),
        "rows": rows,
        "spectral_join": {"status": "WITHHELD_FOR_BLIND_COMPARISON", "accepted_observed_fields": []},
        "epistemic_operator": "CHYBA",
        "canon_allowed": False,
    }
    return {**body, "ledger_sha256": _sha256_json(body)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze post-A1 primary TIR-SIC mass-weighted v0.15 ledger")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    ledger = build_ledger()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": ledger["status"],
        "row_count": ledger["row_count"],
        "ledger_sha256": ledger["ledger_sha256"],
        "coupling_by_card": {row["atom_card_id"]: row["primary_tir_sic_eclipse_coupling"] for row in ledger["rows"]},
        "output": str(args.output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
