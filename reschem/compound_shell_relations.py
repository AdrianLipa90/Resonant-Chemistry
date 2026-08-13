"""Main-group shell-relation candidates for Resonant Chemistry.

The module maps the repository's existing neutral-atom electron-configuration
bookkeeping to a deliberately small candidate relation grammar.

Nuclear identity is never interpolated. For the outer s/p shell, the model
uses the distance in electron count to the nearest closed shell,

    d(v) = min(v, C-v),

with C=2 for n=1 and C=8 thereafter. For a binary pair A,B the minimal
endpoint-balanced stoichiometric skeleton satisfies

    n_A d_A = n_B d_B.

This is representation-level chemistry. It is not a molecular Hamiltonian,
bond-energy model, oxidation-state solver, or geometry predictor. Transition
metals and closed-shell exceptions fail closed in v0.1 rather than being fit
post hoc.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import gcd
from typing import Dict

from .atom import ELEMENT_SYMBOLS, electron_configuration

MAIN_GROUP_Z = frozenset(list(range(1, 21)) + list(range(31, 37)))


@dataclass(frozen=True)
class ValenceShellProfile:
    Z: int
    symbol: str
    principal_n: int
    outer_sp_electrons: int
    closed_shell_capacity: int
    holes_to_closed_shell: int
    relation_degree: int
    signed_half_coordinate: float
    side: str
    epistemic_status: str = "MODEL_DEFINED_FROM_CONTROL_BOOKKEEPING"

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class BinaryShellRelation:
    left_Z: int
    left_symbol: str
    right_Z: int
    right_symbol: str
    left_count: int
    right_count: int
    empirical_formula: str
    left_relation_degree: int
    right_relation_degree: int
    particle_hole_complementarity: float
    endpoint_count_each_side: int
    relation_character: str
    status: str = "CANDIDATE_NEAREST_CLOSED_SHELL_SATURATION_SKELETON"

    def to_dict(self) -> dict:
        return asdict(self)


def _outer_n(configuration: Dict[str, int]) -> int:
    if not configuration:
        raise ValueError("empty electronic configuration")
    return max(int(label[0]) for label in configuration)


def _outer_sp_count(configuration: Dict[str, int], n: int) -> int:
    return sum(
        occupation
        for label, occupation in configuration.items()
        if int(label[0]) == n and label[1] in ("s", "p")
    )


def valence_shell_profile(z: int) -> ValenceShellProfile:
    if z not in MAIN_GROUP_Z:
        raise ValueError(
            f"Z={z} outside v0.1 main-group domain; d-block chemistry fails closed"
        )

    configuration = electron_configuration(z)
    n = _outer_n(configuration)
    v = _outer_sp_count(configuration, n)
    capacity = 2 if n == 1 else 8
    if not 0 <= v <= capacity:
        raise RuntimeError("outer s/p occupation outside closed-shell capacity")

    holes = capacity - v
    degree = min(v, holes)
    half = capacity / 2.0
    signed = (v - half) / half

    if degree == 0:
        side = "CLOSED"
    elif signed < 0:
        side = "BELOW_HALF"
    elif signed > 0:
        side = "ABOVE_HALF"
    else:
        side = "HALF_FILLED"

    return ValenceShellProfile(
        Z=z,
        symbol=ELEMENT_SYMBOLS[z],
        principal_n=n,
        outer_sp_electrons=v,
        closed_shell_capacity=capacity,
        holes_to_closed_shell=holes,
        relation_degree=degree,
        signed_half_coordinate=signed,
        side=side,
    )


def particle_hole_complementarity(
    a: ValenceShellProfile, b: ValenceShellProfile
) -> float:
    """Return a bounded shell-coordinate complementarity diagnostic.

    A value of one means the normalized offsets from half filling cancel
    exactly. This is not electronegativity, bond order, or bond energy.
    """
    value = 1.0 - abs(a.signed_half_coordinate + b.signed_half_coordinate) / 2.0
    return max(0.0, min(1.0, value))


def _formula_piece(symbol: str, count: int) -> str:
    return symbol if count == 1 else f"{symbol}{count}"


def binary_saturation_skeleton(
    left_z: int, right_z: int
) -> BinaryShellRelation | None:
    """Return the minimal endpoint-balanced binary skeleton.

    Caller ordering is preserved in the formula string. If either endpoint
    is closed-shell in the present reduction, the candidate fails closed and
    ``None`` is returned.
    """
    left = valence_shell_profile(left_z)
    right = valence_shell_profile(right_z)
    d_left = left.relation_degree
    d_right = right.relation_degree

    if d_left == 0 or d_right == 0:
        return None

    divisor = gcd(d_left, d_right)
    n_left = d_right // divisor
    n_right = d_left // divisor
    endpoints_left = n_left * d_left
    endpoints_right = n_right * d_right
    if endpoints_left != endpoints_right:
        raise RuntimeError("endpoint-balance reduction failed")

    if left.side != right.side and "HALF_FILLED" not in (left.side, right.side):
        character = "PARTICLE_HOLE_COMPLEMENTARY_CANDIDATE"
    else:
        character = "SHARED_SATURATION_CANDIDATE"

    return BinaryShellRelation(
        left_Z=left.Z,
        left_symbol=left.symbol,
        right_Z=right.Z,
        right_symbol=right.symbol,
        left_count=n_left,
        right_count=n_right,
        empirical_formula=(
            _formula_piece(left.symbol, n_left)
            + _formula_piece(right.symbol, n_right)
        ),
        left_relation_degree=d_left,
        right_relation_degree=d_right,
        particle_hole_complementarity=particle_hole_complementarity(left, right),
        endpoint_count_each_side=endpoints_left,
        relation_character=character,
    )


def stoichiometric_balance_residual(composition: Dict[int, int]) -> dict:
    """Audit a binary composition against the same endpoint grammar."""
    if len(composition) != 2:
        raise ValueError("v0.1 balance audit accepts exactly two element types")

    (left_z, n_left), (right_z, n_right) = list(composition.items())
    if not (
        isinstance(n_left, int)
        and n_left > 0
        and isinstance(n_right, int)
        and n_right > 0
    ):
        raise ValueError("stoichiometric counts must be positive integers")

    left = valence_shell_profile(left_z)
    right = valence_shell_profile(right_z)
    endpoints_left = n_left * left.relation_degree
    endpoints_right = n_right * right.relation_degree

    return {
        "left": {
            "Z": left_z,
            "symbol": left.symbol,
            "count": n_left,
            "relation_degree": left.relation_degree,
            "endpoints": endpoints_left,
        },
        "right": {
            "Z": right_z,
            "symbol": right.symbol,
            "count": n_right,
            "relation_degree": right.relation_degree,
            "endpoints": endpoints_right,
        },
        "residual": abs(endpoints_left - endpoints_right),
        "balanced": endpoints_left == endpoints_right and endpoints_left > 0,
        "status": "MODEL_DEFINED_ENDPOINT_BALANCE_AUDIT",
    }


def generate_main_group_binary_atlas() -> list[dict]:
    """Generate all unordered non-closed-shell binary candidates in-domain."""
    zs = sorted(MAIN_GROUP_Z)
    out: list[dict] = []
    for index, left_z in enumerate(zs):
        for right_z in zs[index + 1 :]:
            relation = binary_saturation_skeleton(left_z, right_z)
            if relation is not None:
                out.append(relation.to_dict())
    return out
