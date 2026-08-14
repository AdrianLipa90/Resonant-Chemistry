from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional, Sequence

from .atom import Atom, KAPPA, configuration_string

ATOM_SCHEMA = "RESCHEM_ATOM_SEMANTIC_CARD_V0_1"
OVERLAY_SCHEMA = "RESCHEM_REPOSITORY_SEMANTIC_OVERLAY_V0_1"
SCHEMA = ATOM_SCHEMA  # backward-compatible public name


def _unassigned_interpretive_layers() -> Dict[str, Any]:
    return {
        "tir": {
            "kappa": KAPPA,
            "relation_operator": {"status": "RESERVED_NOT_YET_APPLIED", "symbol": "W_ij"},
            "semantic_axes": {"status": "CANDIDATE_UNASSIGNED", "values": {}},
        },
        "affective_mapping": {
            "status": "RESERVED_UNASSIGNED",
            "labels": [],
            "coordinates": {},
            "provenance": [],
            "note": "Interpretive layer kept separate from physical/control evidence until an explicit mapping is supplied and tested.",
        },
    }


def make_atom_semantic_card(
    atom: Atom,
    *,
    card_id: Optional[str] = None,
    solver_evidence: Optional[Iterable[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Build a provenance-friendly semantic card from verified atomic state.

    Physical fields are derived from Atom. TIR and affective semantics are
    separate namespaces and remain unassigned until an explicit mapping and
    validation rule are supplied.
    """
    config = atom.configuration
    shells = atom.shell_population
    outer_n = max(shells) if shells else 0
    outer_e = shells.get(outer_n, 0) if outer_n else 0
    closed_shell_control = atom.electron_count in {2, 10, 18, 36}
    interpretive = _unassigned_interpretive_layers()

    return {
        "schema": ATOM_SCHEMA,
        "card_id": card_id or f"ATOM:{atom.symbol}:{atom.mass_number}:q{atom.charge:+d}",
        "entity_level": "atomic_species",
        "identity": {
            "symbol": atom.symbol,
            "Z": atom.z,
            "N": atom.n_neutrons,
            "A": atom.mass_number,
            "charge": atom.charge,
            "electron_count": atom.electron_count,
        },
        "physical_control": {
            "electron_configuration": configuration_string(config),
            "shell_population": {str(k): v for k, v in shells.items()},
            "outer_shell_n": outer_n,
            "outer_shell_electrons": outer_e,
            "closed_shell_control": closed_shell_control,
            "hydrogenic": atom.is_hydrogenic,
        },
        **interpretive,
        "solver_evidence": list(solver_evidence or []),
        "epistemic_status": {
            "identity": "ESTABLISHED_INPUT",
            "electronic_bookkeeping": "CONTROL_MODEL_V0_1",
            "tir_semantics": "OPEN",
            "affective_semantics": "OPEN",
        },
    }


def make_repository_semantic_overlay(
    *,
    card_id: str,
    entity_level: str,
    model_version: str,
    identity: Mapping[str, Any],
    source_artifacts: Mapping[str, Sequence[str]],
    physical_control: Mapping[str, Any],
    epistemic_status: Mapping[str, Any],
) -> Dict[str, Any]:
    """Create a deterministic semantic projection of repository evidence.

    The function is intentionally conservative: it accepts only explicit source
    paths and explicit control/status fields. It never infers TIR or affective
    coordinates, and therefore cannot silently promote interpretation into
    physical evidence.
    """
    if not card_id or not entity_level or not model_version:
        raise ValueError("card_id, entity_level and model_version are required")
    if not any(source_artifacts.values()):
        raise ValueError("at least one source artifact is required")

    interpretive = _unassigned_interpretive_layers()
    return {
        "schema": OVERLAY_SCHEMA,
        "card_id": card_id,
        "entity_level": entity_level,
        "model_version": model_version,
        "identity": dict(identity),
        "source_artifacts": {key: list(value) for key, value in source_artifacts.items()},
        "physical_control": dict(physical_control),
        **interpretive,
        "epistemic_status": {
            **dict(epistemic_status),
            "tir_semantics": "OPEN",
            "affective_semantics": "OPEN",
        },
    }
