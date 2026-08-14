"""Load the current repository semantic-card graph for calculations.

The repository remains Source of Truth. Base atom cards are selected by the
explicit atom index, later atomic evidence is attached non-destructively, and
high-cardinality model-derived entities are regenerated deterministically from
current scientific generators.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from .entity_registry import CardRegistry
from .molecular_semantic_projection import project_molecular_screen_readout
from .semantic_projection import generate_compound_candidate_cards, generate_relational_state_cards


DEFAULT_ROOT = Path(__file__).resolve().parents[1]


def _load_records(path: Path) -> list[dict]:
    if path.suffix == ".jsonl":
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [dict(item) for item in payload]
    if isinstance(payload, dict) and "card_id" in payload:
        return [payload]
    return []


def _load_atom_bases_and_overlays(root: Path) -> tuple[list[dict], list[dict]]:
    index_path = root / "semantic_cards" / "ATOM_CARD_INDEX_CURRENT.json"
    index = json.loads(index_path.read_text(encoding="utf-8"))

    base_by_id: dict[str, dict] = {}
    for group in index["canonical_groups"]:
        for relpath in group["sources"]:
            path = root / relpath
            for record in _load_records(path):
                card_id = record.get("card_id")
                if not card_id:
                    raise ValueError(f"canonical atom source lacks card_id: {relpath}")
                if card_id in base_by_id:
                    raise ValueError(f"duplicate canonical atom card: {card_id}")
                base_by_id[card_id] = dict(record)

    if len(base_by_id) != index["expected_neutral_symbol_coverage"]:
        raise ValueError(
            f"canonical atom coverage drift: {len(base_by_id)} != {index['expected_neutral_symbol_coverage']}"
        )

    independent_overlays: list[dict] = []
    for relpath in index["overlay_sources"]:
        path = root / relpath
        for record in _load_records(path):
            card_id = record.get("card_id")
            if card_id in base_by_id:
                enriched = dict(base_by_id[card_id])
                overlays = list(enriched.get("evidence_overlays", []))
                overlays.append({"source": relpath, "record": record})
                enriched["evidence_overlays"] = overlays
                base_by_id[card_id] = enriched
            elif card_id:
                independent = dict(record)
                independent.setdefault("source_artifacts", {})
                independent["repository_overlay_source"] = relpath
                independent_overlays.append(independent)

    return list(base_by_id.values()), independent_overlays


def _load_model_overlay_cards(root: Path) -> list[dict]:
    path = root / "semantic_cards" / "COMPOUND_MODEL_OVERLAYS_V0_14A1.jsonl"
    return _load_records(path)


def load_current_card_registry(root: Path | str | None = None) -> CardRegistry:
    """Return the current calculation registry from repository state.

    Composition:
    - 36 explicitly indexed neutral atomic base cards plus nondestructive overlays;
    - persisted model/gate semantic cards through v0.13;
    - deterministic 231 v0.1 compound relation candidates;
    - deterministic 27 v0.13 competing relational states;
    - dynamic v0.14A1 model + nine molecular screen cards from the current
      machine-readable partial readout.
    """
    repo = Path(root) if root is not None else DEFAULT_ROOT
    atom_cards, independent_atom_overlays = _load_atom_bases_and_overlays(repo)
    model_cards = _load_model_overlay_cards(repo)
    compound_cards = list(generate_compound_candidate_cards())
    state_cards = list(generate_relational_state_cards())

    readout_path = repo / "benchmarks" / "MOLECULAR_STATE_RELAXATION_PARTIAL_READOUT_V0_14A1.json"
    readout = json.loads(readout_path.read_text(encoding="utf-8"))
    molecular_cards = list(project_molecular_screen_readout(readout))

    cards: list[dict] = []
    cards.extend(atom_cards)
    cards.extend(independent_atom_overlays)
    cards.extend(model_cards)
    cards.extend(compound_cards)
    cards.extend(state_cards)
    cards.extend(molecular_cards)
    return CardRegistry(cards)


def calculation_context(card_ids: Iterable[str], root: Path | str | None = None, *, include_relation_targets: bool = True) -> dict:
    registry = load_current_card_registry(root)
    return registry.calculation_context(tuple(card_ids), include_relation_targets=include_relation_targets)
