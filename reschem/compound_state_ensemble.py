"""Competing relational-state ensembles for compound candidates.

v0.13 changes the *architecture*, not the frozen lower-level predictions.
A chemical composition is allowed to carry multiple competing relation-state
candidates until conventional physical/electronic controls select among them.

The immediate motivating case is the v0.9 closed-shell XY2 atlas.  Post-freeze
literature showed that the same XY2 stoichiometry can correspond to an activated
linear three-centre/four-electron motif (KrF2-type) or a weak X...Y2 complex
(NeCl2/NeBr2/ArBr2-type reference classes).

Therefore every v0.9-eligible XY2 composition receives the same unranked state
ensemble:

- ACTIVATED_LINEAR_3C4E
- WEAK_COMPLEX_LINEAR_END_ON
- WEAK_COMPLEX_T_SHAPED

No element is special-cased and no state is deleted because of prior chemical
knowledge.  Energetic/local-minimum and electronic-topology gates remain the
admission mechanisms.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

from .closed_shell_activation import (
    ClosedShellActivationCandidate,
    closed_shell_activation_candidate,
    generate_closed_shell_activation_atlas,
)


@dataclass(frozen=True)
class RelationalStateCandidate:
    formula: str
    centre_Z: int
    centre_symbol: str
    ligand_Z: int
    ligand_symbol: str
    state_kind: str
    topology_family: str
    geometry_seed: str
    source_gate: str
    prior_rank: int | None = None
    prior_probability: float | None = None
    status: str = "UNRANKED_RELATIONAL_STATE_CANDIDATE"

    def __post_init__(self) -> None:
        if self.prior_rank is not None or self.prior_probability is not None:
            raise ValueError("v0.13 forbids prior ranking/probabilities before physical admission")

    def to_dict(self) -> dict:
        return asdict(self)


_STATE_SPECS = (
    (
        "ACTIVATED_LINEAR_3C4E",
        "ACTIVATED_THREE_CENTRE_FOUR_ELECTRON",
        "LINEAR_LIGAND_CENTRE_LIGAND",
        "v0.9_closed_shell_activation",
    ),
    (
        "WEAK_COMPLEX_LINEAR_END_ON",
        "WEAK_COMPLEX_X_DOT_LIGAND_DIMER",
        "LINEAR_CENTRE_LIGAND_LIGAND",
        "v0.13_competing_weak_complex_branch",
    ),
    (
        "WEAK_COMPLEX_T_SHAPED",
        "WEAK_COMPLEX_X_DOT_LIGAND_DIMER",
        "T_SHAPED_CENTRE_TO_LIGAND_DIMER",
        "v0.13_competing_weak_complex_branch",
    ),
)


def closed_shell_xy2_state_ensemble(
    centre_z: int,
    ligand_z: int,
) -> tuple[RelationalStateCandidate, ...]:
    """Return the unranked competing state ensemble for one v0.9 candidate."""
    base = closed_shell_activation_candidate(centre_z, ligand_z)
    if base is None:
        return ()
    return _ensemble_from_v09(base)


def _ensemble_from_v09(
    base: ClosedShellActivationCandidate,
) -> tuple[RelationalStateCandidate, ...]:
    return tuple(
        RelationalStateCandidate(
            formula=base.empirical_formula,
            centre_Z=base.centre_Z,
            centre_symbol=base.centre_symbol,
            ligand_Z=base.ligand_Z,
            ligand_symbol=base.ligand_symbol,
            state_kind=state_kind,
            topology_family=topology_family,
            geometry_seed=geometry_seed,
            source_gate=source_gate,
        )
        for state_kind, topology_family, geometry_seed, source_gate in _STATE_SPECS
    )


def generate_closed_shell_state_ensemble_atlas() -> tuple[RelationalStateCandidate, ...]:
    """Expand all nine frozen v0.9 compositions into 27 unranked states."""
    out = []
    for base in generate_closed_shell_activation_atlas():
        out.extend(_ensemble_from_v09(base))
    return tuple(out)


def group_states_by_formula() -> dict[str, tuple[RelationalStateCandidate, ...]]:
    grouped: dict[str, list[RelationalStateCandidate]] = {}
    for state in generate_closed_shell_state_ensemble_atlas():
        grouped.setdefault(state.formula, []).append(state)
    return {formula: tuple(states) for formula, states in grouped.items()}
