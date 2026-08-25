"""Exact PNCS v0.19 semantic-mass bridge for Resonant Chemistry v0.15.

The bridge accepts an explicit atom-to-PhaseNav realization binding. It mirrors
the validated PNCS v0.19 scalar contract so Resonant Chemistry can verify a
semantic-mass value before attaching it to an atomic semantic-card overlay.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Mapping, Sequence


PI = 3.14159265358979323846
TAU = 6.28318530717958647692
KAPPA = math.log(2.0) / (24.0 * PI)
L3 = 7
L4 = 2
L5 = 5
ALPHA_M = 1.0 / ((L3 * L4) ** 2 - L3**2 - L4 * L5 + L4**2 * KAPPA)
L_RATIO = L4 / L3
MASS_CONTRACT_ID = "PNV_SEMANTIC_MASS_V1"
RUNTIME_SOURCE_SHA256 = "0b4df86cd01db313ea46ebac0eceee9cf6df0673391edd1a3fb2667c30464a32"
PNCS_REFERENCE_COMMIT = "5b866572f842407302acbb742df8a3955a0b8325"
PNCS_REFERENCE_PATH = "src/phasenav_natural_code/mass_v19.py"
BRIDGE_SCHEMA = "RESCHEM_PNCS_SEMANTIC_MASS_BINDING_V0_15"


class PNCSSemanticMassBridgeError(ValueError):
    pass


def _compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256_json(value: object) -> str:
    return hashlib.sha256(_compact_json(value).encode("utf-8")).hexdigest()


def _phase_index(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise PNCSSemanticMassBridgeError("phase_index must be an explicit positive integer")
    return value


def _phase36(values: Sequence[float]) -> tuple[float, ...]:
    row = tuple(float(value) for value in values)
    if len(row) != 36:
        raise PNCSSemanticMassBridgeError("phase36 must contain exactly 36 angles")
    if any(not math.isfinite(value) for value in row):
        raise PNCSSemanticMassBridgeError("phase36 angles must be finite")
    return row


def _runtime_sin(x: float) -> float:
    x = float(x) % TAU
    total = 0.0
    term = x
    for n in range(1, 30, 2):
        total += term
        term *= -x * x / ((n + 1) * (n + 2))
    return total


def _runtime_cos(x: float) -> float:
    x = float(x) % TAU
    total = 0.0
    term = 1.0
    for n in range(0, 30, 2):
        total += term
        term *= -x * x / ((n + 1) * (n + 2))
    return total


def phase_order_parameter(phase36: Sequence[float]) -> float:
    phase = _phase36(phase36)
    sine_sum = sum(_runtime_sin(value) for value in phase)
    cosine_sum = sum(_runtime_cos(value) for value in phase)
    return math.sqrt(sine_sum * sine_sum + cosine_sum * cosine_sum) / 36.0


def semantic_mass_value(phase_index: int, phase36: Sequence[float]) -> float:
    k = _phase_index(phase_index)
    order_parameter = phase_order_parameter(phase36)
    return round(KAPPA * (1.0 + ALPHA_M * k) + L_RATIO * order_parameter, 10)


@dataclass(frozen=True)
class AtomicPNCSSemanticMassBinding:
    atom_card_id: str
    phase_index: int
    phase36: tuple[float, ...]
    realization_id: str
    realization_binding_id: str
    source_binding_id: str
    mass_contract_id: str = MASS_CONTRACT_ID
    runtime_source_sha256: str = RUNTIME_SOURCE_SHA256
    epistemic_operator: str = "CHYBA"
    canon_allowed: bool = False

    def __post_init__(self) -> None:
        if not self.atom_card_id.startswith("ATOM:"):
            raise PNCSSemanticMassBridgeError("atom_card_id must identify an atomic semantic card")
        object.__setattr__(self, "phase_index", _phase_index(self.phase_index))
        object.__setattr__(self, "phase36", _phase36(self.phase36))
        for name in ("realization_id", "realization_binding_id", "source_binding_id"):
            if not getattr(self, name):
                raise PNCSSemanticMassBridgeError(f"{name} is required")
        if self.mass_contract_id != MASS_CONTRACT_ID:
            raise PNCSSemanticMassBridgeError("semantic-mass contract ID mismatch")
        if self.runtime_source_sha256 != RUNTIME_SOURCE_SHA256:
            raise PNCSSemanticMassBridgeError("semantic-mass runtime source digest mismatch")
        if self.epistemic_operator != "CHYBA":
            raise PNCSSemanticMassBridgeError("semantic-mass binding must retain CHYBA epistemic operator")
        if self.canon_allowed:
            raise PNCSSemanticMassBridgeError("semantic-mass bridge cannot self-promote canon")

    @property
    def order_parameter_R(self) -> float:
        return phase_order_parameter(self.phase36)

    @property
    def semantic_mass(self) -> float:
        return semantic_mass_value(self.phase_index, self.phase36)

    @property
    def phase36_sha256(self) -> str:
        return hashlib.sha256(_compact_json(list(self.phase36)).encode("utf-8")).hexdigest()

    @property
    def payload(self) -> dict:
        body = {
            "schema": BRIDGE_SCHEMA,
            "atom_card_id": self.atom_card_id,
            "phase_index": self.phase_index,
            "phase36": list(self.phase36),
            "phase36_sha256": self.phase36_sha256,
            "realization_id": self.realization_id,
            "realization_binding_id": self.realization_binding_id,
            "source_binding_id": self.source_binding_id,
            "mass_contract_id": self.mass_contract_id,
            "runtime_source_sha256": self.runtime_source_sha256,
            "pncs_reference_commit": PNCS_REFERENCE_COMMIT,
            "pncs_reference_path": PNCS_REFERENCE_PATH,
            "kappa": KAPPA,
            "alpha_m": ALPHA_M,
            "l_ratio": L_RATIO,
            "order_parameter_R": self.order_parameter_R,
            "semantic_mass": self.semantic_mass,
            "epistemic_operator": self.epistemic_operator,
            "canon_allowed": self.canon_allowed,
        }
        return {**body, "bridge_sha256": _sha256_json(body)}

    @property
    def overlay_record(self) -> dict:
        provenance = f"pncs-v0.19:{self.source_binding_id}:{self.payload['bridge_sha256']}"
        return {
            "card_id": self.atom_card_id,
            "overlay_schema": "RESCHEM_ATOMIC_TIR_SEMANTIC_MASS_OVERLAY_V0_15",
            "tir": {
                "kappa": KAPPA,
                "semantic_axes": {
                    "status": "PNCS_V0_19_BOUND_CHYBA",
                    "values": {
                        "semantic_mass": {
                            "value": self.semantic_mass,
                            "provenance": provenance,
                            "phase_index": self.phase_index,
                            "phase36_sha256": self.phase36_sha256,
                            "mass_contract_id": self.mass_contract_id,
                        }
                    },
                },
            },
            "source_artifacts": {
                "pncs_mass_binding_id": self.source_binding_id,
                "pncs_realization_id": self.realization_id,
                "pncs_realization_binding_id": self.realization_binding_id,
                "pncs_reference_commit": PNCS_REFERENCE_COMMIT,
                "pncs_reference_path": PNCS_REFERENCE_PATH,
                "runtime_source_sha256": self.runtime_source_sha256,
            },
            "epistemic_status": {
                "semantic_mass_binding": "BOUND_UNDER_CHYBA",
                "spectral_use": "MODEL_INPUT_AVAILABLE",
            },
        }


def binding_from_manifest_entry(entry: Mapping[str, object]) -> AtomicPNCSSemanticMassBinding:
    if not isinstance(entry, Mapping):
        raise PNCSSemanticMassBridgeError("manifest entry must be a mapping")
    required = {
        "atom_card_id",
        "phase_index",
        "phase36",
        "realization_id",
        "realization_binding_id",
        "source_binding_id",
    }
    missing = sorted(required - set(entry))
    if missing:
        raise PNCSSemanticMassBridgeError(f"manifest entry missing fields: {missing}")
    return AtomicPNCSSemanticMassBinding(
        atom_card_id=str(entry["atom_card_id"]),
        phase_index=_phase_index(entry["phase_index"]),
        phase36=_phase36(entry["phase36"]),
        realization_id=str(entry["realization_id"]),
        realization_binding_id=str(entry["realization_binding_id"]),
        source_binding_id=str(entry["source_binding_id"]),
    )


def verify_bound_semantic_mass(entry: Mapping[str, object], expected_mass: float) -> AtomicPNCSSemanticMassBinding:
    binding = binding_from_manifest_entry(entry)
    expected = float(expected_mass)
    if not math.isfinite(expected):
        raise PNCSSemanticMassBridgeError("expected semantic mass must be finite")
    if binding.semantic_mass != expected:
        raise PNCSSemanticMassBridgeError(
            f"semantic-mass mismatch: {binding.semantic_mass} != {expected}"
        )
    return binding
