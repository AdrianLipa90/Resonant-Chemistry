from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNC_PATH = ROOT / "semantic_cards" / "SURFACE_SYNC_CURRENT.json"
COVERAGE_PATH = ROOT / "semantic_cards" / "SEMANTIC_CARD_COVERAGE_V0_14A2.json"
REGISTRY_PATH = ROOT / "semantic_cards" / "ENTITY_REGISTRY_CURRENT.json"
MOLECULAR_PATH = ROOT / "semantic_cards" / "MOLECULAR_STATE_RELAXATION_V0_14A1.jsonl"
A2_PATH = ROOT / "semantic_cards" / "MOLECULAR_EXECUTION_PARTITION_V0_14A2.jsonl"
SURVIVAL_PATH = ROOT / "benchmarks" / "MOLECULAR_STATE_RELAXATION_ACTIVATED_SURVIVAL_MATRIX_V0_14A1_PARTIAL.json"

FROZEN_A2_PROVENANCE = {
    "frozen_input_run_id": 31795895258,
    "frozen_input_artifact_id": 9217426658,
    "frozen_input_raw_sha256": "6c322bbc7ea31cfb51e4d195fcaeea32747e09447cd1dd56a8aab4771af19602",
    "frozen_r_YY_angstrom": 2.2842324866344543,
    "method_policy_sha256": "9b58d32d361bd2c2248c10859b12785aa9aa0244e18b5504f6cbb79d2abe366d",
    "reuse_policy": "EXACT_BYTES_NO_REOPTIMIZATION",
}

EXPECTED_A2_SEED_HASHES = {
    "ArBr2_activated_s1p0": "f4a3399a565ac2688ed568edb839c036d981006ef3a1d5ee57c9ce99edaca629",
    "ArBr2_activated_s1p3": "be90ec4a53bff85348b0ebfc45515e3e25a3ec96d5e52169720c0d46a8873127",
    "ArBr2_activated_s1p6": "bd5478a6059cdabe85c1732853177473bd2b3d78bb516a318ff416f958a0a30b",
    "ArBr2_weak_linear": "05c956d722e890dc3f0a5845c3e058681bf602c77560ace58a575d2df6c06101",
    "ArBr2_weak_t": "866f804d66d2c865c1275b4d0c6f71e90d783b85cb9e831562fb668a244f1cfa",
}


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def require_text(path: Path, *tokens: str) -> None:
    text = path.read_text(encoding="utf-8")
    missing = [token for token in tokens if token not in text]
    if missing:
        raise SystemExit(f"surface drift: {path.relative_to(ROOT)} missing tokens {missing}")


def main() -> None:
    for path in (SYNC_PATH, COVERAGE_PATH, REGISTRY_PATH, MOLECULAR_PATH, A2_PATH, SURVIVAL_PATH):
        if not path.is_file():
            raise SystemExit(f"missing current semantic surface: {path.relative_to(ROOT)}")

    sync = load_json(SYNC_PATH)
    coverage = load_json(COVERAGE_PATH)
    registry = load_json(REGISTRY_PATH)
    molecular = load_jsonl(MOLECULAR_PATH)
    a2 = load_jsonl(A2_PATH)
    survival = load_json(SURVIVAL_PATH)

    # Scientific state remains v0.14A1 until exact ArBr2 receipts are durably
    # persisted and audited.  v0.14A2 is an execution frontier only.
    if sync.get("scientific_checkpoint") != "v0.14A1":
        raise SystemExit("surface sync scientific-checkpoint drift")
    if sync.get("execution_frontier") != "v0.14A2_CANONICAL_ARBR2_EXECUTION_PENDING":
        raise SystemExit("surface sync execution-frontier drift")

    referenced = []
    for key in ("semantic_surfaces", "theory_surfaces", "operational_surfaces", "web_surfaces"):
        referenced.extend(sync.get(key, []))
    missing = [rel for rel in referenced if not (ROOT / rel).is_file()]
    if missing:
        raise SystemExit(f"surface sync references missing files: {missing}")

    stage_versions = {stage["version"] for stage in coverage.get("stages", [])}
    if not {"v0.13", "v0.14A1", "v0.14A2"}.issubset(stage_versions):
        raise SystemExit("semantic coverage ledger does not reach v0.13/v0.14A1/v0.14A2")
    if coverage.get("scientific_checkpoint") != "v0.14A1":
        raise SystemExit("coverage ledger silently promoted the scientific checkpoint")

    frontier = sync.get("execution_frontier_provenance", {})
    if frontier != FROZEN_A2_PROVENANCE:
        raise SystemExit(f"v0.14A2 frozen input provenance drift: {frontier}")

    populations = registry.get("generated_entity_populations", {})
    wanted_populations = {
        "compound_relation_candidates_v0_1": 231,
        "relational_state_candidates_v0_13": 27,
        "molecular_v0_14A1": 10,
        "execution_units_v0_14A2": 5,
    }
    if populations != wanted_populations:
        raise SystemExit(f"entity population drift: {populations} != {wanted_populations}")

    model = next((r for r in molecular if r.get("card_id") == "MODEL:MOLECULAR_STATE_RELAXATION:v0.14A1"), None)
    if model is None:
        raise SystemExit("missing v0.14A1 molecular model card")
    control = model.get("physical_control", {})
    if control.get("completed_formulae") != 8 or control.get("expected_formulae") != 9:
        raise SystemExit("molecular model formula coverage drift")
    if control.get("completed_starts") != 40 or control.get("expected_starts") != 45:
        raise SystemExit("molecular model start coverage drift")

    formula_records = {
        record.get("identity", {}).get("formula"): record
        for record in molecular
        if record.get("entity_level") == "molecular_formula_screen"
    }
    if len(formula_records) != 9:
        raise SystemExit(f"molecular formula-card count drift: {len(formula_records)} != 9")
    arbr2_status = formula_records["ArBr2"]["physical_control"]["execution_status"]
    if arbr2_status != "MISSING_EXECUTION_NOT_CHEMICAL_FAIL":
        raise SystemExit(f"ArBr2 scientific semantic status drift before A2 admission: {arbr2_status}")

    a2_model = next((r for r in a2 if r.get("card_id") == "MODEL:MOLECULAR_EXECUTION_PARTITION:v0.14A2"), None)
    if a2_model is None:
        raise SystemExit("missing v0.14A2 execution-frontier model card")
    a2_control = a2_model.get("physical_control", {})
    if a2_control.get("execution_status") != "CANONICAL_EXECUTION_PENDING":
        raise SystemExit("v0.14A2 model card is not pending canonical execution")
    if a2_control.get("frozen_input", {}).get("raw_json_sha256") != FROZEN_A2_PROVENANCE["frozen_input_raw_sha256"]:
        raise SystemExit("v0.14A2 model card frozen input hash drift")

    units = [r for r in a2 if r.get("entity_level") == "molecular_seed_execution_unit"]
    if len(units) != 5:
        raise SystemExit(f"v0.14A2 execution-unit count drift: {len(units)} != 5")
    got_hashes = {
        r.get("identity", {}).get("seed_id"): r.get("identity", {}).get("seed_identity_sha256")
        for r in units
    }
    if got_hashes != EXPECTED_A2_SEED_HASHES:
        raise SystemExit(f"v0.14A2 execution-unit canonical seed hash drift: {got_hashes}")
    if any(r.get("physical_control", {}).get("execution_status") != "PENDING" for r in units):
        raise SystemExit("pre-admission v0.14A2 execution-unit cards must remain PENDING")

    boundary = sync.get("current_boundary", {})
    expected_boundary = {
        "molecular_formulae": "8_OF_9_COMPLETED",
        "molecular_starts": "40_OF_45_COMPLETED",
        "ArBr2": "MISSING_EXECUTION_NOT_CHEMICAL_FAIL",
        "hessian_admission": "NOT_RUN",
        "ground_state_ranking": "NOT_VALIDATED",
        "geometry_only_topology_assignment": "NOT_PROMOTED",
    }
    if boundary != expected_boundary:
        raise SystemExit(f"surface boundary drift: {boundary}")

    arbr2_cell = survival.get("cells", {}).get("ArBr2", {})
    if arbr2_cell.get("status") != "MISSING_EXECUTION":
        raise SystemExit("survival matrix no longer preserves ArBr2 missing execution")
    if survival.get("status") != "DESCRIPTIVE_ONLY_NO_FIT_NO_THRESHOLD":
        raise SystemExit("survival matrix semantic status drift")

    require_text(
        ROOT / "THEORY" / "02_ATOM_FORMALISM.md",
        "Current repository checkpoint — v0.14A1",
        "8/9 formulae",
        "40/45 frozen starts",
        "MISSING_EXECUTION_NOT_CHEMICAL_FAIL",
    )
    require_text(
        ROOT / "THEORY" / "03_SHELL_NBODY_TOPOLOGY.md",
        "v0.13/v0.14A1",
        "ACTIVATED_LINEAR_3C4E",
        "WEAK_COMPLEX_LINEAR_END_ON",
        "WEAK_COMPLEX_T_SHAPED",
        "geometry seed -> topology label -> physical canon",
    )
    require_text(
        ROOT / "THEORY" / "04_COMPOUND_RELATIONAL_ARCHITECTURE.md",
        "composition -> candidate relational states -> physical admission",
        "ArBr2",
        "95.9280",
        "37.9877",
        "9.28813",
    )
    require_text(
        ROOT / "THEORY" / "05_SEMANTIC_ENTITY_GRAPH.md",
        "231 generated v0.1 compound-relation candidate cards",
        "27 generated v0.13 relational-state candidate cards",
        "provenance_holonomy != physical_holonomy",
        "MISSING_EXECUTION_NOT_CHEMICAL_FAIL",
    )
    require_text(
        ROOT / "docs" / "molecular_state_relaxation_v0_14a2_execution_partition.md",
        "EXACT_BYTES_NO_REOPTIMIZATION",
        FROZEN_A2_PROVENANCE["frozen_input_raw_sha256"],
        "NONCANONICAL_EXECUTION_DIAGNOSTIC_PREPASS_RECOMPUTED",
        "EXECUTION_TIMEOUT_UNKNOWN",
    )

    # The public web surface continues to show the admitted v0.14A1 scientific
    # checkpoint while A2 is pending.  It must not pre-announce 45/45.
    require_text(
        ROOT / "web" / "index.html",
        "Semantic Card Atlas",
        "40/45 frozen starts",
        "ArBr₂ remains missing execution",
    )
    require_text(
        ROOT / "web" / "semantic_card_atlas.html",
        "semantic-summary",
        "formula-grid",
        "EPISTEMIC CONTRACT",
        "semantic_cards.js",
    )
    require_text(
        ROOT / "web" / "semantic_cards.js",
        "ENTITY_REGISTRY_CURRENT.json",
        "MOLECULAR_STATE_RELAXATION_V0_14A1.jsonl",
        "SURFACE_SYNC_CURRENT.json",
        "MOLECULAR_STATE_RELAXATION_ACTIVATED_SURVIVAL_MATRIX_V0_14A1_PARTIAL.json",
        "MISSING_EXECUTION_NOT_CHEMICAL_FAIL",
    )

    print(json.dumps({
        "semantic_surface_sync": "PASS",
        "scientific_checkpoint": "v0.14A1",
        "execution_frontier": "v0.14A2_CANONICAL_ARBR2_EXECUTION_PENDING",
        "atomic_bases": 36,
        "compound_candidates": 231,
        "relational_states": 27,
        "molecular_cards": 10,
        "a2_execution_units": 5,
        "formulae": "8/9",
        "starts": "40/45",
        "missing_formula": "ArBr2",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
