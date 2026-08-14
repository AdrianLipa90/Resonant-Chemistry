from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SYNC_PATH = ROOT / "semantic_cards" / "SURFACE_SYNC_CURRENT.json"
COVERAGE_PATH = ROOT / "semantic_cards" / "SEMANTIC_CARD_COVERAGE_V0_14A1.json"
REGISTRY_PATH = ROOT / "semantic_cards" / "ENTITY_REGISTRY_CURRENT.json"
MOLECULAR_PATH = ROOT / "semantic_cards" / "MOLECULAR_STATE_RELAXATION_V0_14A1.jsonl"
SURVIVAL_PATH = ROOT / "benchmarks" / "MOLECULAR_STATE_RELAXATION_ACTIVATED_SURVIVAL_MATRIX_V0_14A1_PARTIAL.json"


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
    for path in (SYNC_PATH, COVERAGE_PATH, REGISTRY_PATH, MOLECULAR_PATH, SURVIVAL_PATH):
        if not path.is_file():
            raise SystemExit(f"missing current semantic surface: {path.relative_to(ROOT)}")

    sync = load_json(SYNC_PATH)
    coverage = load_json(COVERAGE_PATH)
    registry = load_json(REGISTRY_PATH)
    molecular = load_jsonl(MOLECULAR_PATH)
    survival = load_json(SURVIVAL_PATH)

    if sync.get("scientific_checkpoint") != "v0.14A1":
        raise SystemExit("surface sync checkpoint drift")

    referenced = []
    for key in ("semantic_surfaces", "theory_surfaces", "web_surfaces"):
        referenced.extend(sync.get(key, []))
    missing = [rel for rel in referenced if not (ROOT / rel).is_file()]
    if missing:
        raise SystemExit(f"surface sync references missing files: {missing}")

    stage_versions = {stage["version"] for stage in coverage.get("stages", [])}
    if "v0.14A1" not in stage_versions or "v0.13" not in stage_versions:
        raise SystemExit("semantic coverage ledger does not reach v0.13/v0.14A1")

    populations = registry.get("generated_entity_populations", {})
    wanted_populations = {
        "compound_relation_candidates_v0_1": 231,
        "relational_state_candidates_v0_13": 27,
        "molecular_v0_14A1": 10,
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
        raise SystemExit(f"ArBr2 semantic status drift: {arbr2_status}")

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
        "SEMANTIC_CARD_COVERAGE_V0_14A1.json",
        "ENTITY_REGISTRY_CURRENT.json",
        "MOLECULAR_STATE_RELAXATION_V0_14A1.jsonl",
        "SURFACE_SYNC_CURRENT.json",
        "MOLECULAR_STATE_RELAXATION_ACTIVATED_SURVIVAL_MATRIX_V0_14A1_PARTIAL.json",
        "MISSING_EXECUTION_NOT_CHEMICAL_FAIL",
    )

    print(json.dumps({
        "semantic_surface_sync": "PASS",
        "checkpoint": "v0.14A1",
        "atomic_bases": 36,
        "compound_candidates": 231,
        "relational_states": 27,
        "molecular_cards": 10,
        "formulae": "8/9",
        "starts": "40/45",
        "missing_formula": "ArBr2",
    }, sort_keys=True))


if __name__ == "__main__":
    main()
