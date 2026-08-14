"""Deterministic projection from Resonant-Chemistry models into entity cards."""
from __future__ import annotations

from typing import Iterable

from .compound_shell_relations import BinaryShellRelation, generate_main_group_binary_atlas
from .compound_state_ensemble import RelationalStateCandidate, generate_closed_shell_state_ensemble_atlas
from .entity_registry import make_emergent_candidate_card, make_entity_card, make_relation


def _element_selector(symbol: str) -> dict:
    return {"entity_level": "atomic_species", "identity.symbol": symbol, "identity.charge": 0}


def project_binary_shell_relation(relation: BinaryShellRelation | dict) -> dict:
    data = relation.to_dict() if isinstance(relation, BinaryShellRelation) else dict(relation)
    formula = data["empirical_formula"]
    card_id = f"COMPOUND_CANDIDATE:{formula}:{data['left_symbol']}-{data['right_symbol']}:v0.1"
    source = "reschem/compound_shell_relations.py"
    relations = [
        make_relation(
            source_card_id=card_id,
            predicate="HAS_ATOMIC_COMPONENT",
            target_selector=_element_selector(data["left_symbol"]),
            source_artifacts=(source,),
            properties={"count": data["left_count"], "relation_degree": data["left_relation_degree"]},
        ),
        make_relation(
            source_card_id=card_id,
            predicate="HAS_ATOMIC_COMPONENT",
            target_selector=_element_selector(data["right_symbol"]),
            source_artifacts=(source,),
            properties={"count": data["right_count"], "relation_degree": data["right_relation_degree"]},
        ),
        make_relation(
            source_card_id=card_id,
            predicate="DERIVED_BY_MODEL",
            target_card_id="MODEL:COMPOUND_SHELL_RELATIONS:v0.1",
            source_artifacts=(source,),
        ),
    ]
    return make_emergent_candidate_card(
        card_id=card_id,
        entity_level="compound_relation_candidate",
        identity={
            "formula": formula,
            "left_symbol": data["left_symbol"],
            "right_symbol": data["right_symbol"],
        },
        properties={
            "left_count": data["left_count"],
            "right_count": data["right_count"],
            "left_relation_degree": data["left_relation_degree"],
            "right_relation_degree": data["right_relation_degree"],
            "endpoint_count_each_side": data["endpoint_count_each_side"],
            "relation_character": data["relation_character"],
        },
        state_invariants={
            "particle_hole_complementarity": data["particle_hole_complementarity"],
            "status": data["status"],
        },
        source_artifacts={
            "implementation": [source],
            "benchmarks": ["benchmarks/COMPOUND_SHELL_RELATION_ATLAS_V0_1.json"],
            "documentation": ["docs/compound_shell_relations_v0_1.md"],
        },
        parent_card_ids=("MODEL:COMPOUND_SHELL_RELATIONS:v0.1",),
        generating_operation="generate_main_group_binary_atlas/binary_saturation_skeleton",
        relations=relations,
    )


def project_relational_state_candidate(state: RelationalStateCandidate) -> dict:
    card_id = f"RELATIONAL_STATE:{state.formula}:{state.state_kind}:v0.13"
    source = "reschem/compound_state_ensemble.py"
    relations = [
        make_relation(
            source_card_id=card_id,
            predicate="DERIVED_BY_MODEL",
            target_card_id="MODEL:COMPOUND_STATE_ENSEMBLE:v0.13",
            source_artifacts=(source,),
        ),
        make_relation(
            source_card_id=card_id,
            predicate="HAS_CENTRE",
            target_selector=_element_selector(state.centre_symbol),
            source_artifacts=(source,),
            properties={"Z": state.centre_Z},
        ),
        make_relation(
            source_card_id=card_id,
            predicate="HAS_LIGAND",
            target_selector=_element_selector(state.ligand_symbol),
            source_artifacts=(source,),
            properties={"Z": state.ligand_Z, "count": 2},
        ),
    ]
    return make_emergent_candidate_card(
        card_id=card_id,
        entity_level="relational_state_candidate",
        identity={
            "formula": state.formula,
            "state_kind": state.state_kind,
            "centre_symbol": state.centre_symbol,
            "ligand_symbol": state.ligand_symbol,
        },
        properties={
            "topology_family": state.topology_family,
            "geometry_seed": state.geometry_seed,
            "source_gate": state.source_gate,
            "prior_rank": state.prior_rank,
            "prior_probability": state.prior_probability,
        },
        state_invariants={"status": state.status},
        source_artifacts={
            "implementation": [source],
            "benchmarks": ["benchmarks/COMPOUND_STATE_ENSEMBLE_V0_13.json"],
            "documentation": ["docs/compound_state_ensemble_v0_13.md"],
        },
        parent_card_ids=("MODEL:COMPOUND_STATE_ENSEMBLE:v0.13", "MODEL:CLOSED_SHELL_ACTIVATION:v0.9"),
        generating_operation="generate_closed_shell_state_ensemble_atlas",
        relations=relations,
        physical_holonomy={
            "status": "CANDIDATE_NOT_COMPUTED_FOR_THIS_ENTITY",
            "observables": {},
            "source_artifacts": ["reschem/shell_nbody_topology.py"],
            "note": "State labels may motivate later winding/phase diagnostics but do not themselves establish physical holonomy.",
        },
    )


def generate_compound_candidate_cards() -> tuple[dict, ...]:
    return tuple(project_binary_shell_relation(row) for row in generate_main_group_binary_atlas())


def generate_relational_state_cards() -> tuple[dict, ...]:
    return tuple(project_relational_state_candidate(state) for state in generate_closed_shell_state_ensemble_atlas())


def generate_calculation_entity_cards() -> tuple[dict, ...]:
    """Current deterministic entity population consumed by calculations.

    Stable atomic cards remain stored under semantic_cards/.  This function adds
    model-derived/emergent compound and relational-state entities without
    changing the underlying scientific generators.
    """
    return generate_compound_candidate_cards() + generate_relational_state_cards()


def index_by_card_id(cards: Iterable[dict]) -> dict[str, dict]:
    out = {}
    for card in cards:
        card_id = card["card_id"]
        if card_id in out:
            raise ValueError(f"duplicate projected card id: {card_id}")
        out[card_id] = card
    return out
