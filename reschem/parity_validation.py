"""Parity-matched validation helpers for the coordination-ladder candidate.

This module asks whether the v0.5 shell gate contributes information beyond a
simpler parity-only null.  It deliberately separates two questions:

1. Within the SF_n sequence, does the shell ladder explain more of the observed
   sequential bond-energy alternation than electron-count parity alone?
2. Across period analogues, does the explicit principal-shell gate (n >= 3)
   remove false-positive higher-coordination candidates that a parity-only null
   would retain?

No energetic parameters are fit here.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import mean

from .compound_shell_relations import valence_shell_profile
from .coordination_ladder import coordination_degrees


@dataclass(frozen=True)
class BinaryRankResult:
    auc: float
    positive_mean: float
    negative_mean: float
    separation: float

    def to_dict(self) -> dict:
        return asdict(self)


def parity_only_degrees(z: int) -> tuple[int, ...]:
    """Return the parity-matched null ladder with no principal-shell gate.

    The null uses the same shell endpoints as v0.5 but applies the +2 parity
    progression to every above-half non-closed main-group centre, regardless
    of principal shell.  It therefore asks specifically whether the n>=3 gate
    adds discriminating information.
    """
    profile = valence_shell_profile(z)
    base = profile.relation_degree
    if base == 0:
        return (0,)
    dual = max(profile.outer_sp_electrons, profile.holes_to_closed_shell)
    if profile.outer_sp_electrons <= profile.closed_shell_capacity / 2.0:
        return (base,)
    return tuple(range(base, dual + 1, 2))


def shell_gated_degrees(z: int) -> tuple[int, ...]:
    return coordination_degrees(z)


def binary_rank_auc(scores: dict[int, int], values: dict[int, float]) -> BinaryRankResult:
    """Rank separation of positive vs negative classes without fitting a cutoff."""
    if set(scores) != set(values):
        raise ValueError("scores and values must have identical keys")
    positives = [float(values[key]) for key, label in scores.items() if label == 1]
    negatives = [float(values[key]) for key, label in scores.items() if label == 0]
    if not positives or not negatives:
        raise ValueError("both score classes must be represented")

    wins = sum(a > b for a in positives for b in negatives)
    ties = sum(a == b for a in positives for b in negatives)
    auc = (wins + 0.5 * ties) / (len(positives) * len(negatives))
    pmean = mean(positives)
    nmean = mean(negatives)
    return BinaryRankResult(
        auc=auc,
        positive_mean=pmean,
        negative_mean=nmean,
        separation=pmean - nmean,
    )


def sf_parity_benchmark(d0_by_n: dict[int, float]) -> dict:
    """Compare parity-only M0 with shell-ladder M1 on SF_n bond energies.

    For sulfur v0.5 has degrees (2,4,6), so on n=2..6 M1 labels exactly the
    even coordination numbers.  The function makes that identity explicit
    rather than crediting the shell model for a parity pattern it does not add.
    """
    required = {2, 3, 4, 5, 6}
    if set(d0_by_n) != required:
        raise ValueError("SF_n benchmark requires n=2..6 exactly")

    m0 = {n: int(n % 2 == 0) for n in sorted(d0_by_n)}
    sulfur_degrees = set(shell_gated_degrees(16))
    m1 = {n: int(n in sulfur_degrees) for n in sorted(d0_by_n)}

    m0_result = binary_rank_auc(m0, d0_by_n)
    m1_result = binary_rank_auc(m1, d0_by_n)
    return {
        "M0_parity_labels": m0,
        "M1_shell_labels": m1,
        "M0": m0_result.to_dict(),
        "M1": m1_result.to_dict(),
        "delta_auc_M1_minus_M0": m1_result.auc - m0_result.auc,
        "identical_labels": m0 == m1,
        "status": "PARITY_MATCHED_INCREMENTAL_TEST",
    }


def retrospective_period_gate_panel() -> dict:
    """Small non-blind sanity panel for the explicit n>=3 gate.

    The labels in this panel were already known when v0.5 was formulated, so
    this function must never be described as blind validation.  Its purpose is
    only to show the logical discrimination between the parity null and the
    principal-shell gate before a genuinely held-out family is screened.
    """
    entries = {
        "NF5": {"centre_Z": 7, "coordination": 5, "realized": False},
        "PF5": {"centre_Z": 15, "coordination": 5, "realized": True},
        "OF6": {"centre_Z": 8, "coordination": 6, "realized": False},
        "SF6": {"centre_Z": 16, "coordination": 6, "realized": True},
    }
    out = {}
    for formula, row in entries.items():
        z = row["centre_Z"]
        degree = row["coordination"]
        observed = bool(row["realized"])
        pred_m0 = degree in parity_only_degrees(z)
        pred_m1 = degree in shell_gated_degrees(z)
        out[formula] = {
            **row,
            "M0_parity_predicts": pred_m0,
            "M1_shell_gate_predicts": pred_m1,
            "M0_correct": pred_m0 == observed,
            "M1_correct": pred_m1 == observed,
        }

    return {
        "entries": out,
        "M0_correct": sum(row["M0_correct"] for row in out.values()),
        "M1_correct": sum(row["M1_correct"] for row in out.values()),
        "count": len(out),
        "status": "RETROSPECTIVE_SANITY_NOT_BLIND_VALIDATION",
    }
