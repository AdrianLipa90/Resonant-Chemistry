"""Shell-level symmetry primitives for Resonant Chemistry.

This module corrects the comparison level of the earlier knot/atom exploration:
the intrinsic object is a subshell occupation (n, l, k), not an element name.
No knot-shell physical relation is asserted here.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ShellSymmetrySignature:
    n: int
    l: int
    occupation: int
    capacity: int
    holes: int
    partner_occupation: int
    half_filling: float
    signed_offset_from_half: float
    absolute_offset_from_half: float
    self_dual: bool


def shell_capacity(l: int) -> int:
    if not isinstance(l, int) or l < 0:
        raise ValueError("l must be a non-negative integer")
    return 2 * (2 * l + 1)


def validate_occupation(l: int, k: int) -> None:
    cap = shell_capacity(l)
    if not isinstance(k, int) or not 0 <= k <= cap:
        raise ValueError(f"occupation k={k!r} outside [0,{cap}] for l={l}")


def particle_hole_partner(l: int, k: int) -> int:
    validate_occupation(l, k)
    return shell_capacity(l) - k


def shell_signature(n: int, l: int, k: int) -> ShellSymmetrySignature:
    if not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")
    validate_occupation(l, k)
    cap = shell_capacity(l)
    half = cap / 2.0
    signed = (k - half) / half
    return ShellSymmetrySignature(
        n=n,
        l=l,
        occupation=k,
        capacity=cap,
        holes=cap-k,
        partner_occupation=cap-k,
        half_filling=half,
        signed_offset_from_half=signed,
        absolute_offset_from_half=abs(signed),
        self_dual=(k == cap-k),
    )


def particle_hole_orbit(l: int, k: int) -> tuple[int, ...]:
    """Return the intrinsic involution orbit without atom labels."""
    partner = particle_hole_partner(l, k)
    return (k,) if partner == k else tuple(sorted((k, partner)))


def are_particle_hole_partners(l: int, k_a: int, k_b: int) -> bool:
    validate_occupation(l, k_a)
    validate_occupation(l, k_b)
    return particle_hole_partner(l, k_a) == k_b


def principal_shell_transfer_invariant(a: ShellSymmetrySignature, b: ShellSymmetrySignature) -> bool:
    """Check whether two records share l and occupation while n changes.

    This is the shell-invariance gate proposed for 2p^k -> 3p^k tests. It does
    not claim their radial physics or energies are equal.
    """
    return a.l == b.l and a.occupation == b.occupation and a.n != b.n


def symmetry_family(l: int) -> tuple[tuple[int, ...], ...]:
    """Partition all occupations into particle-hole involution orbits."""
    cap = shell_capacity(l)
    seen: set[int] = set()
    out: list[tuple[int, ...]] = []
    for k in range(cap + 1):
        if k in seen:
            continue
        orbit = particle_hole_orbit(l, k)
        out.append(orbit)
        seen.update(orbit)
    return tuple(out)


def freeze_shell_records(records: Iterable[ShellSymmetrySignature]) -> tuple[tuple[int, int, int, int, bool], ...]:
    """Stable label-free tuple suitable for a pre-comparison benchmark receipt."""
    return tuple(sorted((r.n, r.l, r.occupation, r.partner_occupation, r.self_dual) for r in records))
