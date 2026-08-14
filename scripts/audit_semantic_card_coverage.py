from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARDS = ROOT / "semantic_cards"
COVERAGE = CARDS / "SEMANTIC_CARD_COVERAGE_V0_14A1.json"
COMPOUND_OVERLAYS = CARDS / "COMPOUND_MODEL_OVERLAYS_V0_14A1.jsonl"
MOLECULAR_OVERLAYS = CARDS / "MOLECULAR_STATE_RELAXATION_V0_14A1.jsonl"
MOLECULAR_BENCHMARK = ROOT / "benchmarks" / "MOLECULAR_STATE_RELAXATION_PARTIAL_READOUT_V0_14A1.json"

H_TO_KR = [
    "H", "He", "Li", "Be", "B", "C", "N", "O", "F", "Ne",
    "Na", "Mg", "Al", "Si", "P", "S", "Cl", "Ar",
    "K", "Ca", "Sc", "Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni",
    "Cu", "Zn", "Ga", "Ge", "As", "Se", "Br", "Kr",
]


def load_jsonl(path: Path):
    records = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise SystemExit(f"invalid JSONL {path}:{line_no}: {exc}") from exc
    return records


def assert_unassigned(record, source: str):
    axes = record.get("tir", {}).get("semantic_axes", {})
    if axes.get("values") not in ({}, None):
        raise SystemExit(f"silent TIR semantic assignment in {source}: {record.get('card_id')}")
    affective = record.get("affective_mapping", {})
    provenance = affective.get("provenance", [])
    if not provenance and affective.get("status") not in (None, "RESERVED_UNASSIGNED"):
        raise SystemExit(f"affective status without provenance in {source}: {record.get('card_id')}")
    if not provenance and (affective.get("labels") or affective.get("coordinates")):
        raise SystemExit(f"affective content without provenance in {source}: {record.get('card_id')}")


def collect_atomic_symbols():
    symbols = set()
    for path in sorted(CARDS.glob("*")):
        if path.name.startswith("schema_") or path.name.startswith("SEMANTIC_CARD_COVERAGE") or path.name == "README.md":
            continue
        records = []
        if path.suffix == ".jsonl":
            records = load_jsonl(path)
        elif path.suffix == ".json":
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict) and "card_id" in payload:
                records = [payload]
        for record in records:
            if str(record.get("card_id", "")).startswith("ATOM:"):
                symbol = record.get("identity", {}).get("symbol")
                if symbol:
                    symbols.add(symbol)
    return symbols


def main():
    required_files = [COVERAGE, COMPOUND_OVERLAYS, MOLECULAR_OVERLAYS, MOLECULAR_BENCHMARK]
    missing = [str(p.relative_to(ROOT)) for p in required_files if not p.is_file()]
    if missing:
        raise SystemExit(f"missing semantic coverage surfaces: {missing}")

    coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))
    stages = coverage["stages"]
    stage_ids = {stage["card_id"] for stage in stages}
    if len(stage_ids) != len(stages):
        raise SystemExit("duplicate card_id in semantic coverage ledger")

    for stage in stages:
        for key in ("implementation", "benchmark", "documentation"):
            path = ROOT / stage[key]
            if not path.is_file():
                raise SystemExit(f"coverage source missing for {stage['card_id']}: {stage[key]}")

    compound_records = load_jsonl(COMPOUND_OVERLAYS)
    molecular_records = load_jsonl(MOLECULAR_OVERLAYS)
    projection_records = compound_records + molecular_records
    projection_ids = {record.get("card_id") for record in projection_records}
    uncovered = sorted(stage_ids - projection_ids)
    if uncovered:
        raise SystemExit(f"model/gate semantic coverage missing: {uncovered}")

    for record in projection_records:
        assert_unassigned(record, "projection")

    atomic_symbols = collect_atomic_symbols()
    missing_atoms = [symbol for symbol in H_TO_KR if symbol not in atomic_symbols]
    if missing_atoms:
        raise SystemExit(f"H-Kr atomic semantic-card coverage missing symbols: {missing_atoms}")

    benchmark = json.loads(MOLECULAR_BENCHMARK.read_text(encoding="utf-8"))
    expected = set(benchmark["expected_formulae"])
    completed = set(benchmark["completed_formulae"])
    formula_records = {
        record["identity"]["formula"]: record
        for record in molecular_records
        if record.get("entity_level") == "molecular_formula_screen"
    }
    if set(formula_records) != expected:
        raise SystemExit(
            f"molecular semantic-card formula mismatch: expected={sorted(expected)} got={sorted(formula_records)}"
        )

    for formula in sorted(expected):
        status = formula_records[formula]["physical_control"]["execution_status"]
        if formula in completed:
            if status != "EXECUTED_5_OF_5_FROZEN_STARTS":
                raise SystemExit(f"completed formula has wrong semantic execution status: {formula}={status}")
        else:
            if status != "MISSING_EXECUTION_NOT_CHEMICAL_FAIL":
                raise SystemExit(f"missing formula was semantically promoted or misclassified: {formula}={status}")

    model_record = next(
        record for record in molecular_records
        if record.get("card_id") == "MODEL:MOLECULAR_STATE_RELAXATION:v0.14A1"
    )
    if model_record["physical_control"]["completed_formulae"] != len(completed):
        raise SystemExit("molecular model card completed_formulae drift")
    if model_record["physical_control"]["completed_starts"] != benchmark["completed_starts"]:
        raise SystemExit("molecular model card completed_starts drift")
    if model_record["epistemic_status"].get("hessian_admission") != "NOT_RUN":
        raise SystemExit("semantic layer attempted Hessian promotion")
    if model_record["epistemic_status"].get("ground_state_ranking") != "NOT_VALIDATED":
        raise SystemExit("semantic layer attempted ground-state promotion")
    if model_record["epistemic_status"].get("geometry_only_topology_assignment") != "NOT_PROMOTED":
        raise SystemExit("semantic layer attempted topology promotion")

    print(json.dumps({
        "semantic_card_audit": "PASS",
        "atomic_symbols_h_to_kr": len(atomic_symbols.intersection(H_TO_KR)),
        "model_gate_cards": len(stage_ids),
        "molecular_formula_cards": len(formula_records),
        "completed_formulae": len(completed),
        "missing_formulae": sorted(expected - completed),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
