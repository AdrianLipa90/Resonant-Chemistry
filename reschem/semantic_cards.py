from __future__ import annotations

from typing import Any, Dict, Iterable, Optional

from .atom import Atom, KAPPA, configuration_string

SCHEMA = "RESCHEM_ATOM_SEMANTIC_CARD_V0_1"


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

    return {
        "schema": SCHEMA,
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
            "note": "Interpretive layer kept separate from physical control data until an explicit mapping is supplied and tested.",
        },
        "solver_evidence": list(solver_evidence or []),
        "epistemic_status": {
            "identity": "ESTABLISHED_INPUT",
            "electronic_bookkeeping": "CONTROL_MODEL_V0_1",
            "tir_semantics": "OPEN",
            "affective_semantics": "OPEN",
        },
    }
