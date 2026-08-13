"""Conformal diagnostics for Jones-polynomial trajectories.

Candidate research utility for Resonant-Chemistry.
No TIR correction. No affective mapping. No atom↔knot identity claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence
import cmath
import math


@dataclass(frozen=True)
class KnotConformalFeatures:
    signed_winding_about_half: int
    minimum_distance_to_half: float
    half_root_angles: tuple[float, ...]
    normalized_cyclic_gaps: tuple[float, ...]


def evaluate_laurent(coefficients: Mapping[int, complex], q: complex) -> complex:
    """Evaluate a Laurent polynomial represented by exponent -> coefficient."""
    return sum(coefficient * (q ** exponent) for exponent, coefficient in coefficients.items())


def trajectory(
    coefficients: Mapping[int, complex],
    samples: int = 16384,
    anchor: complex = 0.5,
) -> tuple[complex, ...]:
    if samples < 16:
        raise ValueError("samples must be >= 16")
    return tuple(
        evaluate_laurent(coefficients, cmath.exp(2j * math.pi * index / samples)) - anchor
        for index in range(samples)
    )


def signed_winding(values: Sequence[complex]) -> int:
    """Discrete winding number of a closed sampled trajectory about zero."""
    if len(values) < 3:
        raise ValueError("closed trajectory requires at least three samples")
    phase_sum = 0.0
    for left, right in zip(values, values[1:] + values[:1]):
        if left == 0 or right == 0:
            raise ValueError("trajectory crosses the winding anchor")
        phase_sum += cmath.phase(right / left)
    return int(round(phase_sum / (2 * math.pi)))


def minimum_distance(values: Sequence[complex]) -> float:
    return min(abs(value) for value in values)


def normalized_cyclic_gaps(angles: Sequence[float]) -> tuple[float, ...]:
    """Return sorted cyclic gaps on [0, 2*pi), normalized to sum to one."""
    if not angles:
        return ()
    ordered = sorted(angle % (2 * math.pi) for angle in angles)
    gaps = [right - left for left, right in zip(ordered, ordered[1:])]
    gaps.append((ordered[0] + 2 * math.pi) - ordered[-1])
    normalized = tuple(sorted(gap / (2 * math.pi) for gap in gaps))
    if not math.isclose(sum(normalized), 1.0, rel_tol=1e-12, abs_tol=1e-12):
        raise ArithmeticError("cyclic gaps failed normalization")
    return normalized


def inverse_conformal_value(value: complex, anchor: complex = 0.5) -> complex:
    shifted = value - anchor
    if shifted == 0:
        raise ZeroDivisionError("Jones trajectory hits conformal anchor")
    return 1 / shifted


def electron_hole_partner(p_electron_count: int, shell_capacity: int = 6) -> int:
    """Intrinsic p-shell particle-hole involution n -> capacity-n."""
    if not 0 <= p_electron_count <= shell_capacity:
        raise ValueError("occupation outside shell capacity")
    return shell_capacity - p_electron_count


def electron_hole_pairs(symbol_to_p_count: Mapping[str, int]) -> tuple[tuple[str, str], ...]:
    """Construct shell-dual pairs without using knot labels or fitting."""
    reverse: dict[int, list[str]] = {}
    for symbol, count in symbol_to_p_count.items():
        reverse.setdefault(count, []).append(symbol)

    pairs: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for symbol, count in sorted(symbol_to_p_count.items()):
        partner_count = electron_hole_partner(count)
        for partner in sorted(reverse.get(partner_count, [])):
            pair = tuple(sorted((symbol, partner)))
            if pair not in seen:
                pairs.append(pair)
                seen.add(pair)
    return tuple(pairs)
