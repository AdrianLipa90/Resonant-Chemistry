"""Generic closed-shell activation candidates for the compound relation layer.

v0.9 addresses the KrF2 falsifier without adding a krypton-specific exception.
The generator starts from the frozen v0.1 shell bookkeeping and admits a
structural three-centre/four-electron (3c4e) candidate only when:

- the centre is an H--Kr main-group atom with a completely filled outer s/p
  shell, relation degree zero, and principal shell n >= 2;
- the ligand is on the above-half branch with frozen relation degree one.

Within the current H--Kr domain this selects centres Ne/Ar/Kr and ligands
F/Cl/Br mechanically, producing a 3 x 3 candidate atlas.  No member is removed
because it is chemically unfamiliar.  In particular, NeF2 and ArF2 remain
visible candidates alongside the motivating KrF2 case.

The activated relation degree ``2`` and ``q_cs=1`` are representation-level
bookkeeping for one symmetric linear 3c4e motif.  They are not an excitation
energy, oxidation state, electron transfer count, or stability prediction.
Energetic/local-minimum admission remains a separate conventional-physics gate.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

from .atom import ELEMENT_SYMBOLS
from .compound_shell_relations import MAIN_GROUP_Z, valence_shell_profile
from .energetic_admission import PairLossChannel


@dataclass(frozen=True)
class ClosedShellActivationCandidate:
    centre_Z: int
    centre_symbol: str
    ligand_Z: int
    ligand_symbol: str
    q_cs: int
    base_relation_degree: int
    activated_relation_degree: int
    ligand_count: int
    empirical_formula: str
    topology: str
    geometry_seed: str
    status: str = "MODEL_DEFINED_CLOSED_SHELL_3C4E_CANDIDATE"

    def to_dict(self) -> dict:
        return asdict(self)


def _eligible_closed_shell_centre(z: int) -> bool:
    profile = valence_shell_profile(z)
    return (
        profile.relation_degree == 0
        and profile.outer_sp_electrons == profile.closed_shell_capacity
        and profile.principal_n >= 2
    )


def _eligible_degree_one_ligand(z: int) -> bool:
    profile = valence_shell_profile(z)
    return profile.relation_degree == 1 and profile.side == "ABOVE_HALF"


def closed_shell_activation_candidate(
    centre_z: int,
    ligand_z: int,
) -> ClosedShellActivationCandidate | None:
    """Return one generic linear 3c4e structural candidate or ``None``.

    The function is intentionally structural.  It does not ask whether the
    candidate is experimentally observed or thermodynamically stable.
    """
    if centre_z not in MAIN_GROUP_Z or ligand_z not in MAIN_GROUP_Z:
        raise ValueError("v0.9 is restricted to the current H-Kr main-group domain")

    if not _eligible_closed_shell_centre(centre_z):
        return None
    if not _eligible_degree_one_ligand(ligand_z):
        return None

    centre = valence_shell_profile(centre_z)
    ligand = valence_shell_profile(ligand_z)
    formula = f"{centre.symbol}{ligand.symbol}2"

    return ClosedShellActivationCandidate(
        centre_Z=centre_z,
        centre_symbol=centre.symbol,
        ligand_Z=ligand_z,
        ligand_symbol=ligand.symbol,
        q_cs=1,
        base_relation_degree=0,
        activated_relation_degree=2,
        ligand_count=2,
        empirical_formula=formula,
        topology="SYMMETRIC_THREE_CENTRE_FOUR_ELECTRON_CANDIDATE",
        geometry_seed="LINEAR_X_CENTRE_X",
    )


def generate_closed_shell_activation_atlas() -> tuple[ClosedShellActivationCandidate, ...]:
    """Generate the complete frozen v0.9 atlas in the current H--Kr domain."""
    out: list[ClosedShellActivationCandidate] = []
    for centre_z in sorted(MAIN_GROUP_Z):
        if not _eligible_closed_shell_centre(centre_z):
            continue
        for ligand_z in sorted(MAIN_GROUP_Z):
            if not _eligible_degree_one_ligand(ligand_z):
                continue
            candidate = closed_shell_activation_candidate(centre_z, ligand_z)
            if candidate is not None:
                out.append(candidate)
    return tuple(out)


def activation_pair_loss_channel(
    candidate: ClosedShellActivationCandidate,
) -> PairLossChannel:
    """Return the frozen whole-ligand-pair loss channel XY2 -> X + Y2."""
    return PairLossChannel(
        parent=candidate.empirical_formula,
        lower=candidate.centre_symbol,
        ligand_dimer=f"{candidate.ligand_symbol}2",
    )


def candidate_formulae() -> tuple[str, ...]:
    return tuple(candidate.empirical_formula for candidate in generate_closed_shell_activation_atlas())
