"""Energetic admission gate for preregistered compound-relation candidates.

v0.8 does not add a novel energy term. It defines how an independent,
conventional electronic-structure calculation may admit or reject a structural
candidate without changing the frozen relation rules.

For the higher-coordination ladder the primary channel is pair loss

    XY_n -> XY_(n-2) + Y2

with

    DeltaE_pair = E(XY_(n-2)) + E(Y2) - E(XY_n).

Positive DeltaE_pair means the parent is lower in the policy-defined energy
than that specific decomposition channel. A candidate is not called locally
stable unless the optimized parent and the preregistered products are harmonic
local minima under one identical method policy.

Missing data stays UNKNOWN. Method/basis/policy mismatches are INCOMPARABLE.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Iterable, Mapping

HARTREE_TO_KCAL_MOL = 627.5094740631


@dataclass(frozen=True)
class MethodPolicy:
    method: str
    basis: str
    relativistic: str = "NONE_OR_BACKEND_DEFAULT"
    dispersion: str = "NONE_OR_INCLUDED_IN_METHOD"
    environment: str = "GAS_PHASE"
    geometry_policy: str = "FULL_OPTIMIZATION"
    hessian_policy: str = "HARMONIC_AT_OPTIMIZED_GEOMETRY"
    energy_kind: str = "ELECTRONIC_ENERGY"

    @property
    def signature(self) -> tuple[str, ...]:
        return (
            self.method,
            self.basis,
            self.relativistic,
            self.dispersion,
            self.environment,
            self.geometry_policy,
            self.hessian_policy,
            self.energy_kind,
        )

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class EnergyDatum:
    formula: str
    energy_hartree: float
    policy: MethodPolicy
    charge: int = 0
    multiplicity: int = 1
    optimized: bool = True
    imaginary_frequencies: int | None = 0
    provenance: str = "UNSPECIFIED"

    def __post_init__(self) -> None:
        if not self.formula:
            raise ValueError("formula must be non-empty")
        if not isfinite(float(self.energy_hartree)):
            raise ValueError("energy_hartree must be finite")
        if not isinstance(self.charge, int):
            raise ValueError("charge must be an integer")
        if not isinstance(self.multiplicity, int) or self.multiplicity < 1:
            raise ValueError("multiplicity must be a positive integer")
        if self.imaginary_frequencies is not None:
            if not isinstance(self.imaginary_frequencies, int) or self.imaginary_frequencies < 0:
                raise ValueError("imaginary_frequencies must be None or a non-negative integer")

    @property
    def local_minimum(self) -> bool | None:
        if not self.optimized:
            return False
        if self.imaginary_frequencies is None:
            return None
        return self.imaginary_frequencies == 0

    def to_dict(self) -> dict:
        out = asdict(self)
        out["policy"] = self.policy.to_dict()
        out["local_minimum"] = self.local_minimum
        return out


@dataclass(frozen=True)
class PairLossChannel:
    parent: str
    lower: str
    ligand_dimer: str
    ligand_atoms_lost: int = 2
    status: str = "PREREGISTERED_PAIR_LOSS_CHANNEL"

    def __post_init__(self) -> None:
        if self.ligand_atoms_lost != 2:
            raise ValueError("v0.8 pair-loss channel is fixed to loss of one ligand dimer")
        if len({self.parent, self.lower, self.ligand_dimer}) != 3:
            raise ValueError("parent, lower, and ligand_dimer labels must be distinct")

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class EnergeticAdmission:
    channel: PairLossChannel
    status: str
    delta_e_hartree: float | None
    delta_e_kcal_mol: float | None
    parent_local_minimum: bool | None
    comparable_policy: bool
    interpretation: str

    def to_dict(self) -> dict:
        return {
            "channel": self.channel.to_dict(),
            "status": self.status,
            "delta_e_hartree": self.delta_e_hartree,
            "delta_e_kcal_mol": self.delta_e_kcal_mol,
            "parent_local_minimum": self.parent_local_minimum,
            "comparable_policy": self.comparable_policy,
            "interpretation": self.interpretation,
        }


def _lookup(records: Mapping[str, EnergyDatum], formula: str) -> EnergyDatum | None:
    datum = records.get(formula)
    if datum is not None and datum.formula != formula:
        raise ValueError(f"energy-record key/formula mismatch for {formula}")
    return datum


def evaluate_pair_loss(
    channel: PairLossChannel,
    records: Mapping[str, EnergyDatum],
    tolerance_hartree: float = 1.0e-6,
) -> EnergeticAdmission:
    """Evaluate one frozen pair-loss channel without fitting model parameters."""
    if tolerance_hartree < 0 or not isfinite(float(tolerance_hartree)):
        raise ValueError("tolerance_hartree must be finite and non-negative")

    parent = _lookup(records, channel.parent)
    lower = _lookup(records, channel.lower)
    dimer = _lookup(records, channel.ligand_dimer)

    if parent is None or lower is None or dimer is None:
        return EnergeticAdmission(
            channel=channel,
            status="UNKNOWN_MISSING_ENERGY_DATA",
            delta_e_hartree=None,
            delta_e_kcal_mol=None,
            parent_local_minimum=None if parent is None else parent.local_minimum,
            comparable_policy=False,
            interpretation="At least one preregistered species has no energy record.",
        )

    comparable = parent.policy.signature == lower.policy.signature == dimer.policy.signature
    if not comparable:
        return EnergeticAdmission(
            channel=channel,
            status="INCOMPARABLE_METHOD_POLICY",
            delta_e_hartree=None,
            delta_e_kcal_mol=None,
            parent_local_minimum=parent.local_minimum,
            comparable_policy=False,
            interpretation="Parent and products were not computed under one frozen method policy.",
        )

    delta = lower.energy_hartree + dimer.energy_hartree - parent.energy_hartree
    delta_kcal = delta * HARTREE_TO_KCAL_MOL
    local_minimum = parent.local_minimum
    product_minima = (lower.local_minimum, dimer.local_minimum)

    if local_minimum is None:
        status = "UNKNOWN_PARENT_HESSIAN_NOT_AVAILABLE"
        interpretation = "Pair-loss energy is available, but parent local-minimum status is unknown."
    elif local_minimum is False:
        status = "REJECTED_PARENT_NO_LOCAL_MINIMUM"
        interpretation = "The optimized parent is not a harmonic local minimum."
    elif any(value is None for value in product_minima):
        status = "UNKNOWN_PRODUCT_HESSIAN_NOT_AVAILABLE"
        interpretation = "At least one preregistered product has unknown local-minimum status."
    elif any(value is False for value in product_minima):
        status = "INVALID_PAIR_LOSS_CHANNEL_PRODUCT_NOT_LOCAL_MINIMUM"
        interpretation = "At least one preregistered product is not a harmonic local minimum; this channel cannot supply a resolved stability label."
    elif delta > tolerance_hartree:
        status = "ADMITTED_BOUND_AGAINST_PAIR_LOSS"
        interpretation = "Parent is a local minimum and lies below the preregistered pair-loss products."
    elif delta < -tolerance_hartree:
        status = "METASTABLE_OR_UNBOUND_TO_PAIR_LOSS"
        interpretation = "Parent is a local minimum but lies above the preregistered pair-loss products."
    else:
        status = "ENERGETICALLY_DEGENERATE_WITHIN_TOLERANCE"
        interpretation = "Pair-loss energy is indistinguishable from zero at the frozen tolerance."

    return EnergeticAdmission(
        channel=channel,
        status=status,
        delta_e_hartree=delta,
        delta_e_kcal_mol=delta_kcal,
        parent_local_minimum=local_minimum,
        comparable_policy=True,
        interpretation=interpretation,
    )


def evaluate_panel(
    channels: Iterable[PairLossChannel],
    records: Mapping[str, EnergyDatum],
    tolerance_hartree: float = 1.0e-6,
) -> tuple[EnergeticAdmission, ...]:
    return tuple(
        evaluate_pair_loss(channel, records, tolerance_hartree=tolerance_hartree)
        for channel in channels
    )


def score_boolean_model(
    predictions: Mapping[str, bool],
    admissions: Iterable[EnergeticAdmission],
) -> dict:
    """Score a frozen structural model only where the energy label is resolved."""
    positive = {"ADMITTED_BOUND_AGAINST_PAIR_LOSS"}
    negative = {"METASTABLE_OR_UNBOUND_TO_PAIR_LOSS", "REJECTED_PARENT_NO_LOCAL_MINIMUM"}

    resolved = []
    unresolved = []
    for admission in admissions:
        formula = admission.channel.parent
        if formula not in predictions:
            raise ValueError(f"missing frozen prediction for {formula}")
        if admission.status in positive | negative:
            observed = admission.status in positive
            predicted = bool(predictions[formula])
            resolved.append((formula, predicted, observed, predicted == observed))
        else:
            unresolved.append((formula, admission.status))

    correct = sum(item[3] for item in resolved)
    positives = [x for x in resolved if x[2]]
    negatives = [x for x in resolved if not x[2]]

    tpr = sum(x[1] is True for x in positives) / len(positives) if positives else None
    tnr = sum(x[1] is False for x in negatives) / len(negatives) if negatives else None
    balanced_accuracy = None if tpr is None or tnr is None else 0.5 * (tpr + tnr)

    return {
        "resolved_count": len(resolved),
        "correct_count": correct,
        "accuracy": None if not resolved else correct / len(resolved),
        "balanced_accuracy": balanced_accuracy,
        "resolved": [
            {
                "formula": formula,
                "predicted": predicted,
                "observed_energy_label": observed,
                "correct": is_correct,
            }
            for formula, predicted, observed, is_correct in resolved
        ],
        "unresolved": [
            {"formula": formula, "status": status}
            for formula, status in unresolved
        ],
    }
