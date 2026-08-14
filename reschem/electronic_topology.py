"""Backend-neutral electronic-topology admission gate for XY2 candidates.

v0.10 exists because stoichiometry and even a local minimum do not distinguish
an activated three-centre/four-electron (3c4e) motif from a weak X...Y2 van der
Waals complex.  The gate therefore aggregates *independent diagnostic families*
without inventing a single bond-order threshold.

The three frozen families are:

- ORBITAL_SUBSPACE: an explicitly documented localized/subspace bonding analysis;
- REAL_SPACE_FORCE: electron-density and/or local-force diagnostics;
- FRAGMENTATION_ISOMER_ENERGY: conventional energetic comparison against
  preregistered fragmentation and competing weak-complex/isomer channels.

Each family must preserve its raw analysis outside this small aggregator and
report one of SUPPORT_3C4E, SUPPORT_VDW, INCONCLUSIVE, or NOT_RUN with method
and provenance.  The aggregator never converts a missing diagnostic into a
negative label.

A positive topology label requires support from at least two distinct families
and zero opposing informative families.  A VDW label uses the symmetric rule.
Conflicting informative families produce MIXED_CONFLICTING_EVIDENCE.  This
2-of-3 policy is a validation contract, not a physical law or fitted parameter.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

FAMILIES = frozenset(
    {
        "ORBITAL_SUBSPACE",
        "REAL_SPACE_FORCE",
        "FRAGMENTATION_ISOMER_ENERGY",
    }
)

VERDICTS = frozenset(
    {
        "SUPPORT_3C4E",
        "SUPPORT_VDW",
        "INCONCLUSIVE",
        "NOT_RUN",
    }
)


@dataclass(frozen=True)
class TopologyEvidence:
    family: str
    verdict: str
    method_signature: str
    provenance: str
    raw_summary: str

    def __post_init__(self) -> None:
        if self.family not in FAMILIES:
            raise ValueError(f"unknown diagnostic family: {self.family}")
        if self.verdict not in VERDICTS:
            raise ValueError(f"unknown topology verdict: {self.verdict}")
        if not self.method_signature.strip():
            raise ValueError("method_signature must be non-empty")
        if not self.provenance.strip():
            raise ValueError("provenance must be non-empty")
        if not self.raw_summary.strip():
            raise ValueError("raw_summary must be non-empty")

    @property
    def informative(self) -> bool:
        return self.verdict in {"SUPPORT_3C4E", "SUPPORT_VDW"}

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ElectronicTopologyAudit:
    formula: str
    local_minimum: bool | None
    evidence: tuple[TopologyEvidence, ...]
    status: str
    support_3c4e: int
    support_vdw: int
    informative_families: int
    interpretation: str

    def to_dict(self) -> dict:
        return {
            "formula": self.formula,
            "local_minimum": self.local_minimum,
            "evidence": [item.to_dict() for item in self.evidence],
            "status": self.status,
            "support_3c4e": self.support_3c4e,
            "support_vdw": self.support_vdw,
            "informative_families": self.informative_families,
            "interpretation": self.interpretation,
        }


def audit_electronic_topology(
    formula: str,
    evidence: Iterable[TopologyEvidence],
    *,
    local_minimum: bool | None,
) -> ElectronicTopologyAudit:
    """Aggregate independent topology evidence under the frozen 2-of-3 rule."""
    if not formula.strip():
        raise ValueError("formula must be non-empty")

    items = tuple(evidence)
    seen: set[str] = set()
    for item in items:
        if item.family in seen:
            raise ValueError(
                "at most one admitted evidence record per diagnostic family; "
                "combine repeated calculations upstream and preserve their provenance"
            )
        seen.add(item.family)

    if local_minimum is False:
        return ElectronicTopologyAudit(
            formula=formula,
            local_minimum=False,
            evidence=items,
            status="REJECTED_NOT_LOCAL_MINIMUM",
            support_3c4e=0,
            support_vdw=0,
            informative_families=sum(item.informative for item in items),
            interpretation=(
                "The candidate is not a local minimum under the admitted physical "
                "control; no stable-topology label is assigned."
            ),
        )

    n_3c4e = sum(item.verdict == "SUPPORT_3C4E" for item in items)
    n_vdw = sum(item.verdict == "SUPPORT_VDW" for item in items)
    informative = n_3c4e + n_vdw

    if n_3c4e and n_vdw:
        status = "MIXED_CONFLICTING_EVIDENCE"
        interpretation = (
            "Independent diagnostic families disagree; retain raw evidence and "
            "do not force a 3c4e or VDW label."
        )
    elif n_3c4e >= 2:
        status = "CONSISTENT_3C4E_MULTI_DIAGNOSTIC"
        interpretation = (
            "At least two independent families support 3c4e topology and no "
            "informative family supports a VDW interpretation."
        )
    elif n_vdw >= 2:
        status = "CONSISTENT_VDW_MULTI_DIAGNOSTIC"
        interpretation = (
            "At least two independent families support a weak-complex/VDW topology "
            "and no informative family supports 3c4e topology."
        )
    else:
        status = "UNKNOWN_INSUFFICIENT_INDEPENDENT_EVIDENCE"
        interpretation = (
            "Fewer than two independent informative families agree; a single MO, "
            "QTAIM, force, or energy diagnostic is not sufficient."
        )

    if local_minimum is None and status.startswith("CONSISTENT_"):
        status = "UNKNOWN_LOCAL_MINIMUM_NOT_ESTABLISHED"
        interpretation = (
            "Electronic diagnostics may be mutually consistent, but local-minimum "
            "status is unavailable; physical admission remains unresolved."
        )

    return ElectronicTopologyAudit(
        formula=formula,
        local_minimum=local_minimum,
        evidence=items,
        status=status,
        support_3c4e=n_3c4e,
        support_vdw=n_vdw,
        informative_families=informative,
        interpretation=interpretation,
    )


def score_topology_predictions(
    predictions: dict[str, str],
    audits: Iterable[ElectronicTopologyAudit],
    *,
    excluded: Iterable[str] = (),
) -> dict:
    """Score only resolved, non-preknown topology labels.

    ``predictions`` values must be ``3C4E`` or ``VDW``.  Unknown/conflicting
    audits remain visible and are excluded from the denominator.
    """
    excluded_set = set(excluded)
    resolved = []
    unresolved = []

    for audit in audits:
        if audit.formula in excluded_set:
            continue
        if audit.formula not in predictions:
            raise ValueError(f"missing frozen topology prediction for {audit.formula}")
        prediction = predictions[audit.formula]
        if prediction not in {"3C4E", "VDW"}:
            raise ValueError(f"invalid topology prediction for {audit.formula}: {prediction}")

        if audit.status == "CONSISTENT_3C4E_MULTI_DIAGNOSTIC":
            observed = "3C4E"
        elif audit.status == "CONSISTENT_VDW_MULTI_DIAGNOSTIC":
            observed = "VDW"
        else:
            unresolved.append({"formula": audit.formula, "status": audit.status})
            continue

        resolved.append(
            {
                "formula": audit.formula,
                "predicted": prediction,
                "observed": observed,
                "correct": prediction == observed,
            }
        )

    correct = sum(item["correct"] for item in resolved)
    return {
        "resolved_count": len(resolved),
        "correct_count": correct,
        "accuracy": None if not resolved else correct / len(resolved),
        "resolved": resolved,
        "unresolved": unresolved,
    }
