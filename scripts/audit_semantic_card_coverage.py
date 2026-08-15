from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from reschem.entity_registry import CardRegistry
from reschem.molecular_semantic_projection import project_molecular_screen_readout
from reschem.phasenav_chem import FROZEN_METHOD_POLICY_SHA256, assert_frozen_method_gate
from reschem.semantic_projection import generate_compound_candidate_cards, generate_relational_state_cards
from reschem.molecular_state_relaxation import xy2_seed_geometries

CARDS = ROOT / "semantic_cards"
COVERAGE = CARDS / "SEMANTIC_CARD_COVERAGE_V0_14A2.json"
COMPOUND_OVERLAYS = CARDS / "COMPOUND_MODEL_OVERLAYS_V0_14A1.jsonl"
MOLECULAR_OVERLAYS = CARDS / "MOLECULAR_STATE_RELAXATION_V0_14A1.jsonl"
A2_OVERLAYS = CARDS / "MOLECULAR_EXECUTION_PARTITION_V0_14A2.jsonl"
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


def audit_relations_and_holonomy(records):
    for record in records:
        assert_unassigned(record, "generated entity")
        holonomy = record.get("provenance_holonomy", {})
        if holonomy.get("status") != "MODEL_DEFINED_LINEAGE" or not holonomy.get("lineage_sha256"):
            raise SystemExit(f"missing provenance holonomy: {record.get('card_id')}")
        physical = record.get("physical_holonomy", {})
        if physical.get("status") != "NOT_COMPUTED" and not physical.get("source_artifacts"):
            raise SystemExit(f"physical holonomy without provenance: {record.get('card_id')}")
        for relation in record.get("relations", []):
            modes = bool(relation.get("target_card_id")) + bool(relation.get("target_selector"))
            if modes != 1:
                raise SystemExit(f"relation target ambiguity: {record.get('card_id')}")


def audit_a2_execution_partition(records):
    if assert_frozen_method_gate() != FROZEN_METHOD_POLICY_SHA256:
        raise SystemExit("v0.14A2 frozen method gate drift")

    model_id = "MODEL:MOLECULAR_EXECUTION_PARTITION:v0.14A2"
    model = next((r for r in records if r.get("card_id") == model_id), None)
    if model is None:
        raise SystemExit("missing v0.14A2 execution-partition model card")
    assert_unassigned(model, "v0.14A2 model")
    control = model.get("physical_control", {})
    if control.get("seed_count") != 5 or control.get("method_changed") is not False:
        raise SystemExit("v0.14A2 model-card frozen execution contract drift")

    unit_records = [r for r in records if r.get("entity_level") == "molecular_seed_execution_unit"]
    expected = [seed.seed_id for seed in xy2_seed_geometries("Ar", "Br", 1.0)]
    got = [r.get("identity", {}).get("seed_id") for r in unit_records]
    if got != expected:
        raise SystemExit(f"v0.14A2 execution-unit identity drift: {got} != {expected}")
    for record in unit_records:
        assert_unassigned(record, "v0.14A2 execution unit")
        physical = record.get("physical_control", {})
        if physical.get("execution_status") != "PENDING":
            raise SystemExit(f"v0.14A2 pre-execution card must remain PENDING: {record.get('card_id')}")
        if physical.get("no_rescue") is not True:
            raise SystemExit(f"v0.14A2 no-rescue invariant missing: {record.get('card_id')}")


def main():
    required_files = [COVERAGE, COMPOUND_OVERLAYS, MOLECULAR_OVERLAYS, A2_OVERLAYS, MOLECULAR_BENCHMARK]
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
    a2_records = load_jsonl(A2_OVERLAYS)
    projection_records = compound_records + molecular_records + a2_records
    projection_ids = {record.get("card_id") for record in projection_records}
    uncovered = sorted(stage_ids - projection_ids)
    if uncovered:
        raise SystemExit(f"model/gate semantic coverage missing: {uncovered}")
    for record in projection_records:
        assert_unassigned(record, "persisted projection")

    audit_a2_execution_partition(a2_records)

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
        raise SystemExit(f"molecular semantic-card formula mismatch: expected={sorted(expected)} got={sorted(formula_records)}")
    for formula in sorted(expected):
        status = formula_records[formula]["physical_control"]["execution_status"]
        wanted = "EXECUTED_5_OF_5_FROZEN_STARTS" if formula in completed else "MISSING_EXECUTION_NOT_CHEMICAL_FAIL"
        if status != wanted:
            raise SystemExit(f"molecular semantic execution status drift: {formula}={status}, wanted={wanted}")

    model_record = next(record for record in molecular_records if record.get("card_id") == "MODEL:MOLECULAR_STATE_RELAXATION:v0.14A1")
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

    generated_compounds = generate_compound_candidate_cards()
    generated_states = generate_relational_state_cards()
    generated_molecular = project_molecular_screen_readout(benchmark)
    if len(generated_compounds) != 231:
        raise SystemExit(f"compound entity-card count drift: {len(generated_compounds)} != 231")
    if len(generated_states) != 27:
        raise SystemExit(f"relational-state entity-card count drift: {len(generated_states)} != 27")
    if len(generated_molecular) != 10:
        raise SystemExit(f"molecular entity-card count drift: {len(generated_molecular)} != 10")

    generated = generated_compounds + generated_states + generated_molecular
    audit_relations_and_holonomy(generated)
    CardRegistry(generated)

    dynamic_formula = {
        record["identity"]["formula"]: record
        for record in generated_molecular
        if record.get("entity_level") == "molecular_formula_screen"
    }
    for formula in sorted(expected):
        persisted = formula_records[formula]["physical_control"]["execution_status"]
        generated_status = dynamic_formula[formula]["properties"]["execution_status"]
        if persisted != generated_status:
            raise SystemExit(f"persisted/dynamic molecular card drift: {formula}")

    print(json.dumps({
        "semantic_card_audit": "PASS",
        "atomic_symbols_h_to_kr": len(atomic_symbols.intersection(H_TO_KR)),
        "model_gate_cards": len(stage_ids),
        "generated_compound_candidate_cards": len(generated_compounds),
        "generated_relational_state_cards": len(generated_states),
        "generated_molecular_cards": len(generated_molecular),
        "v0_14a2_execution_units": len([r for r in a2_records if r.get("entity_level") == "molecular_seed_execution_unit"]),
        "completed_formulae": len(completed),
        "missing_formulae": sorted(expected - completed),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
