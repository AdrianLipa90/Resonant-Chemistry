"""Semantic entity cards, relations, and provenance holonomy for calculations.

This layer is deliberately downstream of the scientific models. It turns
explicit model outputs into addressable calculation objects without granting a
semantic label additional physical authority.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence

ENTITY_SCHEMA = "RESCHEM_ENTITY_CARD_V0_1"
RELATION_SCHEMA = "RESCHEM_ENTITY_RELATION_V0_1"


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _nested_get(value: Mapping[str, Any], dotted_path: str) -> Any:
    current: Any = value
    for part in dotted_path.split("."):
        if not isinstance(current, Mapping) or part not in current:
            return None
        current = current[part]
    return current


def lineage_sha256(*, parents: Sequence[str], operation: str, identity: Mapping[str, Any]) -> str:
    payload = {
        "parents": sorted(str(parent) for parent in parents),
        "operation": str(operation),
        "identity": dict(identity),
    }
    return hashlib.sha256(_canonical_json(payload).encode("utf-8")).hexdigest()


def make_relation(
    *,
    source_card_id: str,
    predicate: str,
    target_card_id: str | None = None,
    target_selector: Mapping[str, Any] | None = None,
    status: str = "MODEL_DEFINED_RELATION",
    source_artifacts: Sequence[str] = (),
    properties: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if bool(target_card_id) == bool(target_selector):
        raise ValueError("exactly one of target_card_id or target_selector is required")
    return {
        "schema": RELATION_SCHEMA,
        "source_card_id": source_card_id,
        "predicate": predicate,
        "target_card_id": target_card_id,
        "target_selector": dict(target_selector or {}),
        "status": status,
        "source_artifacts": list(source_artifacts),
        "properties": dict(properties or {}),
    }


def make_entity_card(
    *,
    card_id: str,
    entity_level: str,
    identity: Mapping[str, Any],
    properties: Mapping[str, Any],
    state_invariants: Mapping[str, Any],
    source_artifacts: Mapping[str, Sequence[str]],
    epistemic_status: Mapping[str, Any],
    relations: Sequence[Mapping[str, Any]] = (),
    parent_card_ids: Sequence[str] = (),
    generating_operation: str = "DIRECT_REPOSITORY_PROJECTION",
    physical_holonomy: Mapping[str, Any] | None = None,
    emergence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if not card_id or not entity_level:
        raise ValueError("card_id and entity_level are required")
    if not any(source_artifacts.values()):
        raise ValueError("entity cards require named source artifacts")

    physical_holonomy_record = dict(physical_holonomy or {
        "status": "NOT_COMPUTED",
        "observables": {},
        "source_artifacts": [],
    })
    if physical_holonomy_record.get("status") != "NOT_COMPUTED" and not physical_holonomy_record.get("source_artifacts"):
        raise ValueError("computed/candidate physical holonomy requires source artifacts")

    lineage = lineage_sha256(
        parents=parent_card_ids,
        operation=generating_operation,
        identity=identity,
    )
    return {
        "schema": ENTITY_SCHEMA,
        "card_id": card_id,
        "entity_level": entity_level,
        "identity": dict(identity),
        "properties": dict(properties),
        "state_invariants": dict(state_invariants),
        "source_artifacts": {key: list(value) for key, value in source_artifacts.items()},
        "relations": [dict(relation) for relation in relations],
        "provenance_holonomy": {
            "status": "MODEL_DEFINED_LINEAGE",
            "parent_card_ids": list(parent_card_ids),
            "generating_operation": generating_operation,
            "lineage_sha256": lineage,
        },
        "physical_holonomy": physical_holonomy_record,
        "emergence": dict(emergence or {"status": "NOT_EMERGENT"}),
        "tir": {
            "relation_operator": {"status": "RESERVED_NOT_YET_APPLIED", "symbol": "W_ij"},
            "semantic_axes": {"status": "CANDIDATE_UNASSIGNED", "values": {}},
        },
        "affective_mapping": {
            "status": "RESERVED_UNASSIGNED",
            "labels": [],
            "coordinates": {},
            "provenance": [],
        },
        "epistemic_status": {
            **dict(epistemic_status),
            "tir_semantics": "OPEN",
            "affective_semantics": "OPEN",
        },
    }


def make_emergent_candidate_card(
    *,
    card_id: str,
    entity_level: str,
    identity: Mapping[str, Any],
    properties: Mapping[str, Any],
    state_invariants: Mapping[str, Any],
    source_artifacts: Mapping[str, Sequence[str]],
    parent_card_ids: Sequence[str],
    generating_operation: str,
    relations: Sequence[Mapping[str, Any]] = (),
    physical_holonomy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if not parent_card_ids:
        raise ValueError("emergent candidates require parent cards")
    return make_entity_card(
        card_id=card_id,
        entity_level=entity_level,
        identity=identity,
        properties=properties,
        state_invariants=state_invariants,
        source_artifacts=source_artifacts,
        epistemic_status={
            "entity": "MODEL_DEFINED_EMERGENT_CANDIDATE",
            "physical_validation": "OPEN",
        },
        relations=relations,
        parent_card_ids=parent_card_ids,
        generating_operation=generating_operation,
        physical_holonomy=physical_holonomy,
        emergence={
            "status": "MODEL_DEFINED_EMERGENT_CANDIDATE",
            "promotion": "REQUIRES_INDEPENDENT_PHYSICAL_ADMISSION",
        },
    )


@dataclass
class CardRegistry:
    """In-memory semantic graph consumed by downstream calculations.

    Registry membership is addressability, not scientific promotion. Exact-id
    links and selector links can both be resolved. Selector resolution is
    deterministic equality matching on dotted fields such as
    ``identity.symbol``.
    """

    cards: dict[str, dict[str, Any]]

    def __init__(self, cards: Iterable[Mapping[str, Any]] = ()) -> None:
        self.cards = {}
        for card in cards:
            self.add(card)

    def add(self, card: Mapping[str, Any]) -> None:
        card_id = str(card.get("card_id", ""))
        if not card_id:
            raise ValueError("card_id required")
        if card_id in self.cards:
            raise ValueError(f"duplicate card_id: {card_id}")
        self.cards[card_id] = dict(card)

    def resolve(self, card_id: str) -> dict[str, Any]:
        try:
            return self.cards[card_id]
        except KeyError as exc:
            raise KeyError(f"unknown semantic card: {card_id}") from exc

    def match_selector(self, selector: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
        matched = []
        for card in self.cards.values():
            if all(_nested_get(card, key) == expected for key, expected in selector.items()):
                matched.append(card)
        return tuple(sorted((dict(card) for card in matched), key=lambda card: card["card_id"]))

    def neighbors(self, card_id: str, predicate: str | None = None) -> tuple[dict[str, Any], ...]:
        card = self.resolve(card_id)
        relations = card.get("relations", [])
        if predicate is not None:
            relations = [relation for relation in relations if relation.get("predicate") == predicate]
        return tuple(dict(relation) for relation in relations)

    def relation_targets(self, card_id: str, predicate: str | None = None) -> tuple[dict[str, Any], ...]:
        targets: dict[str, dict[str, Any]] = {}
        for relation in self.neighbors(card_id, predicate):
            target_id = relation.get("target_card_id")
            if target_id:
                if target_id in self.cards:
                    targets[target_id] = self.resolve(target_id)
                continue
            for target in self.match_selector(relation.get("target_selector", {})):
                targets[target["card_id"]] = target
        return tuple(targets[key] for key in sorted(targets))

    def provenance_lineage(self, card_id: str, *, max_depth: int = 32) -> tuple[str, ...]:
        seen: set[str] = set()
        order: list[str] = []

        def visit(current_id: str, depth: int) -> None:
            if depth > max_depth or current_id in seen:
                return
            seen.add(current_id)
            card = self.cards.get(current_id)
            if card is None:
                return
            for parent in card.get("provenance_holonomy", {}).get("parent_card_ids", []):
                visit(parent, depth + 1)
            order.append(current_id)

        visit(card_id, 0)
        return tuple(order)

    def calculation_context(self, card_ids: Sequence[str], *, include_relation_targets: bool = False) -> dict[str, Any]:
        selected_ids = list(card_ids)
        if include_relation_targets:
            for card_id in tuple(selected_ids):
                for target in self.relation_targets(card_id):
                    if target["card_id"] not in selected_ids:
                        selected_ids.append(target["card_id"])
        selected = [self.resolve(card_id) for card_id in selected_ids]
        return {
            "schema": "RESCHEM_CARD_CALCULATION_CONTEXT_V0_1",
            "card_ids": selected_ids,
            "cards": selected,
            "context_sha256": hashlib.sha256(_canonical_json(selected).encode("utf-8")).hexdigest(),
            "status": "DERIVED_CALCULATION_CONTEXT_NOT_SCIENTIFIC_PROMOTION",
        }
