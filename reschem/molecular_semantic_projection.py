"""Project v0.14 molecular-screen evidence into calculation entity cards."""
from __future__ import annotations

from typing import Any, Mapping

from .entity_registry import make_entity_card, make_relation

STATE_KINDS = (
    "ACTIVATED_LINEAR_3C4E",
    "WEAK_COMPLEX_LINEAR_END_ON",
    "WEAK_COMPLEX_T_SHAPED",
)


def _state_card_id(formula: str, state_kind: str) -> str:
    return f"RELATIONAL_STATE:{formula}:{state_kind}:v0.13"


def project_molecular_screen_readout(readout: Mapping[str, Any]) -> tuple[dict, ...]:
    expected = tuple(readout["expected_formulae"])
    completed = set(readout["completed_formulae"])
    formula_data = readout.get("formulae", {})
    benchmark_path = "benchmarks/MOLECULAR_STATE_RELAXATION_PARTIAL_READOUT_V0_14A1.json"
    implementation_path = "reschem/molecular_state_relaxation.py"
    documentation_path = "docs/molecular_state_relaxation_v0_14a1_partial_readout.md"

    model_card = make_entity_card(
        card_id="MODEL:MOLECULAR_STATE_RELAXATION:v0.14A1",
        entity_level="molecular_screening_gate",
        identity={"model": "MOLECULAR_STATE_RELAXATION", "version": "v0.14A1"},
        properties={
            "expected_formulae": len(expected),
            "completed_formulae": len(completed),
            "expected_starts": readout["expected_starts"],
            "completed_starts": readout["completed_starts"],
            "screening_only": True,
        },
        state_invariants={"status": readout["status"]},
        source_artifacts={
            "implementation": [implementation_path],
            "benchmarks": [benchmark_path],
            "documentation": [documentation_path],
        },
        epistemic_status={
            "entity": "PARTIAL_EXECUTION_EVIDENCE",
            "hessian_admission": "NOT_RUN",
            "ground_state_ranking": "NOT_VALIDATED",
            "geometry_only_topology_assignment": "NOT_PROMOTED",
        },
        parent_card_ids=("MODEL:COMPOUND_STATE_ENSEMBLE:v0.13",),
        generating_operation="v0.14A1_frozen_relaxation_screen",
    )

    cards = [model_card]
    for formula in expected:
        card_id = f"MOLECULE:{formula}:SCREEN:v0.14A1"
        parents = tuple(_state_card_id(formula, kind) for kind in STATE_KINDS)
        relations = [
            make_relation(
                source_card_id=card_id,
                predicate="SCREENED_STATE_CANDIDATE",
                target_card_id=parent,
                source_artifacts=(benchmark_path,),
                status="FROZEN_INPUT_STATE_RELATION",
            )
            for parent in parents
        ]

        if formula in completed:
            data = formula_data[formula]
            lowest = data["lowest_successful_screening"]
            lowest_state = lowest["state_kind"]
            relations.append(
                make_relation(
                    source_card_id=card_id,
                    predicate="LOWEST_SUCCESSFUL_SCREENING_WITHIN_FROZEN_STARTS",
                    target_card_id=_state_card_id(formula, lowest_state),
                    source_artifacts=(benchmark_path,),
                    status="SCREENING_ONLY_NOT_GROUND_STATE",
                    properties={"seed_id": lowest["seed_id"]},
                )
            )
            properties = {
                "execution_status": "EXECUTED_5_OF_5_FROZEN_STARTS",
                "start_count": data["start_count"],
                "successful_relaxation_count": data["successful_relaxation_count"],
                "families": {
                    family: {"starts": item["starts"], "successful": item["successful"]}
                    for family, item in data["families"].items()
                },
                "lowest_successful_screening": lowest,
                "raw_json_sha256": data["raw_json_sha256"],
            }
            entity_status = "SCREENING_EVIDENCE_ONLY"
        else:
            properties = {
                "execution_status": "MISSING_EXECUTION_NOT_CHEMICAL_FAIL",
                "start_count": 5,
                "successful_relaxation_count": None,
                "families": {},
                "lowest_successful_screening": None,
            }
            entity_status = "UNKNOWN_EXECUTION"

        cards.append(make_entity_card(
            card_id=card_id,
            entity_level="molecular_formula_screen",
            identity={"formula": formula},
            properties=properties,
            state_invariants={"screening_only": True},
            source_artifacts={
                "implementation": [implementation_path],
                "benchmarks": [benchmark_path],
                "documentation": [documentation_path],
            },
            epistemic_status={
                "entity": entity_status,
                "hessian_admission": "NOT_RUN",
                "ground_state_ranking": "NOT_VALIDATED",
                "topology_assignment": "NOT_PROMOTED",
            },
            relations=relations,
            parent_card_ids=parents + ("MODEL:MOLECULAR_STATE_RELAXATION:v0.14A1",),
            generating_operation="relax_frozen_v0.13_state_ensemble_under_v0.14A1",
            physical_holonomy={
                "status": "NOT_COMPUTED",
                "observables": {},
                "source_artifacts": [],
            },
        ))

    return tuple(cards)
