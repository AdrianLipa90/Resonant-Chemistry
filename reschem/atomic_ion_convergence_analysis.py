"""Threshold-free descriptive analysis of a complete v0.12A state scan.

The module does not decide numerical convergence. It aligns neutral/ion states
at the same frozen L0/L1/L2 numerical level and reports the finite differences
that motivated v0.11, together with their adjacent-level drift.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping

LEVEL_ORDER = ("L0", "L1", "L2")


def _key(state: Mapping) -> tuple[str, int]:
    return str(state["symbol"]), int(state["charge"])


def _level_map(state: Mapping) -> dict[str, Mapping]:
    rows = {str(row["level"]): row for row in state["levels"]}
    if tuple(level for level in LEVEL_ORDER if level in rows) != LEVEL_ORDER:
        raise ValueError(f"state {_key(state)} does not contain complete L0/L1/L2 coverage")
    return rows


def matched_difference_trajectory(
    left: Mapping,
    right: Mapping,
    *,
    definition: str,
) -> dict:
    """Return E(right)-E(left) at each numerical level, without a threshold."""
    left_levels = _level_map(left)
    right_levels = _level_map(right)
    values = []
    for level in LEVEL_ORDER:
        delta = float(right_levels[level]["energy_hartree"]) - float(left_levels[level]["energy_hartree"])
        values.append(
            {
                "level": level,
                "value_hartree": delta,
                "left_converged": bool(left_levels[level]["converged"]),
                "right_converged": bool(right_levels[level]["converged"]),
                "left_virial_abs_hartree": float(left_levels[level]["virial_abs_hartree"]),
                "right_virial_abs_hartree": float(right_levels[level]["virial_abs_hartree"]),
            }
        )

    drift = []
    for earlier, later in zip(values, values[1:]):
        change = later["value_hartree"] - earlier["value_hartree"]
        drift.append(
            {
                "from": earlier["level"],
                "to": later["level"],
                "signed_difference_drift_hartree": change,
                "absolute_difference_drift_hartree": abs(change),
            }
        )

    return {
        "definition": definition,
        "left_state": {"symbol": left["symbol"], "charge": left["charge"]},
        "right_state": {"symbol": right["symbol"], "charge": right["charge"]},
        "levels": values,
        "adjacent_difference_drift": drift,
        "status": "DESCRIPTIVE_ONLY_NO_NUMERICAL_ADMISSION_THRESHOLD",
    }


def summarize_complete_scan(states: Iterable[Mapping]) -> dict:
    state_map = {_key(state): state for state in states}
    expected = {
        ("Ne", 0), ("Ne", 1),
        ("Ar", 0), ("Ar", 1),
        ("Kr", 0), ("Kr", 1),
        ("F", 0), ("F", -1),
        ("Cl", 0), ("Cl", -1),
        ("Br", 0), ("Br", -1),
    }
    if set(state_map) != expected:
        raise ValueError(f"incomplete or unexpected v0.12A state set: {sorted(state_map)}")

    ionization = {
        symbol: matched_difference_trajectory(
            state_map[(symbol, 0)],
            state_map[(symbol, 1)],
            definition="E(cation)-E(neutral)",
        )
        for symbol in ("Ne", "Ar", "Kr")
    }

    # Attachment gain retains the v0.11 sign convention E(neutral)-E(anion).
    attachment = {
        symbol: matched_difference_trajectory(
            state_map[(symbol, -1)],
            state_map[(symbol, 0)],
            definition="E(neutral)-E(anion)",
        )
        for symbol in ("F", "Cl", "Br")
    }

    return {
        "schema": "RESCHEM_ATOMIC_ION_CONVERGENCE_DESCRIPTIVE_V0_12A",
        "ionization_cost_trajectories": ionization,
        "attachment_gain_trajectories": attachment,
        "status": "DESCRIPTIVE_ONLY_NO_CONVERGENCE_THRESHOLD_NO_CHEMISTRY_CLASSIFIER",
    }
