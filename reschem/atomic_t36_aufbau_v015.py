"""Preregistered atom-to-T36 candidate control for Resonant Chemistry v0.15.

The construction consumes an atom-card electron configuration and emits a
36-phase realization plus PNCS v0.18/v0.19-compatible receipt payloads. The
contract remains under CHYBA with canon_allowed=false.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
from typing import Mapping, Sequence

from .pncs_semantic_mass_bridge_v015 import (
    ALPHA_M,
    KAPPA,
    L3,
    L4,
    L5,
    L_RATIO,
    MASS_CONTRACT_ID,
    RUNTIME_SOURCE_SHA256,
    AtomicPNCSSemanticMassBinding,
    phase_order_parameter,
    semantic_mass_value,
)

DIM = 36
TAU = 2.0 * math.pi
BASIS_ID = "RESCHEM_AUFBAU36_ROOTS_OF_UNITY_OCCUPANCY_PHASE_V0_15"
DERIVATION_ID = "RESCHEM_ATOM_CARD_ELECTRON_CONFIGURATION_TO_T36_V0_15"
PREREG_SCHEMA = "RESCHEM_ATOMIC_T36_AUFBAU_PHASE_CONTROL_PREREG_V0_15"
CANDIDATE_SCHEMA = "RESCHEM_ATOMIC_T36_AUFBAU_PHASE_CONTROL_BINDING_V0_15"
PNCS_REALIZATION_SCHEMA = "PNCS_EXACT_36D_REALIZATION_V0_18"
PNCS_REALIZATION_BINDING_SCHEMA = "PNCS_EXACT_36D_BINDING_V0_18"
PNCS_MASS_REALIZATION_SCHEMA = "PNCS_SEMANTIC_MASS_REALIZATION_V0_19"
PNCS_MASS_BINDING_SCHEMA = "PNCS_SEMANTIC_MASS_BINDING_V0_19"
PNCS_MASS_RUNTIME_SOURCE_LOCATOR = "NOEMA_LIBRARY:file_00000000ea0c8210b0ff0db8ea94071a:v1:pnv_runtime.py"

_SUBSHELLS = (
    ("1s", 1, 0),
    ("2s", 2, 0),
    ("2p", 2, 1),
    ("3s", 3, 0),
    ("3p", 3, 1),
    ("4s", 4, 0),
    ("3d", 3, 2),
    ("4p", 4, 1),
)
_SUBSHELL_BY_LABEL = {label: (n, ell) for label, n, ell in _SUBSHELLS}
_CONFIGURATION_TOKEN = re.compile(r"^(\d+)([spdf])\^(\d+)$")


class AtomicT36AufbauError(ValueError):
    pass


def _compact_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha256_json(value: object) -> str:
    return _sha256_bytes(_compact_json(value).encode("utf-8"))


def _typed_id(prefix: str, payload: Mapping[str, object]) -> str:
    return f"{prefix}:sha256:{_sha256_json(dict(payload))}"


@dataclass(frozen=True)
class SpinOrbitalSlot:
    index: int
    subshell: str
    n: int
    l: int
    m_l: int
    spin: str

    @property
    def label(self) -> str:
        return f"{self.subshell}:m{self.m_l:+d}:{self.spin}"

    @property
    def payload(self) -> dict[str, object]:
        return {
            "index": self.index,
            "subshell": self.subshell,
            "n": self.n,
            "l": self.l,
            "m_l": self.m_l,
            "spin": self.spin,
            "label": self.label,
        }


def spin_orbital_basis36() -> tuple[SpinOrbitalSlot, ...]:
    slots: list[SpinOrbitalSlot] = []
    for subshell, n, ell in _SUBSHELLS:
        for m_l in range(-ell, ell + 1):
            for spin in ("alpha", "beta"):
                slots.append(SpinOrbitalSlot(len(slots), subshell, n, ell, m_l, spin))
    if len(slots) != DIM:
        raise RuntimeError(f"Aufbau basis drift: {len(slots)} != {DIM}")
    return tuple(slots)


def basis_manifest() -> dict[str, object]:
    slots = spin_orbital_basis36()
    body = {
        "schema": "RESCHEM_AUFBAU36_SPIN_ORBITAL_BASIS_V0_15",
        "basis_id": BASIS_ID,
        "dimension": DIM,
        "subshell_order": [label for label, _, _ in _SUBSHELLS],
        "slot_order": "m_l_ASCENDING_THEN_spin_ALPHA_BETA",
        "occupancy_assignment": "HUND_ALPHA_CHANNEL_FIRST_THEN_BETA_CHANNEL_WITH_m_l_ASCENDING",
        "slots": [slot.payload for slot in slots],
    }
    return {**body, "basis_sha256": _sha256_json(body)}


def parse_electron_configuration(configuration: str) -> dict[str, int]:
    if not isinstance(configuration, str) or not configuration.strip():
        raise AtomicT36AufbauError("electron configuration must be a non-empty string")
    occupancy = {label: 0 for label, _, _ in _SUBSHELLS}
    seen: set[str] = set()
    for token in configuration.split():
        match = _CONFIGURATION_TOKEN.fullmatch(token)
        if match is None:
            raise AtomicT36AufbauError(f"unsupported electron-configuration token: {token!r}")
        n_text, orbital_letter, count_text = match.groups()
        label = f"{int(n_text)}{orbital_letter}"
        if label not in _SUBSHELL_BY_LABEL:
            raise AtomicT36AufbauError(f"subshell {label!r} is outside the frozen H-Kr 36-slot basis")
        if label in seen:
            raise AtomicT36AufbauError(f"duplicate subshell token: {label}")
        seen.add(label)
        _, ell = _SUBSHELL_BY_LABEL[label]
        capacity = 2 * (2 * ell + 1)
        count = int(count_text)
        if count < 0 or count > capacity:
            raise AtomicT36AufbauError(f"occupancy {count} outside capacity {capacity} for {label}")
        occupancy[label] = count
    return occupancy


def occupancy_vector36(configuration: str) -> tuple[int, ...]:
    subshell_occupancy = parse_electron_configuration(configuration)
    slots = spin_orbital_basis36()
    occupied_labels: set[str] = set()
    for subshell, _, ell in _SUBSHELLS:
        count = subshell_occupancy[subshell]
        degeneracy = 2 * ell + 1
        alpha_count = min(count, degeneracy)
        beta_count = max(0, count - degeneracy)
        m_values = list(range(-ell, ell + 1))
        for m_l in m_values[:alpha_count]:
            occupied_labels.add(f"{subshell}:m{m_l:+d}:alpha")
        for m_l in m_values[:beta_count]:
            occupied_labels.add(f"{subshell}:m{m_l:+d}:beta")
    return tuple(1 if slot.label in occupied_labels else 0 for slot in slots)


def phase36_from_occupancy(occupancy: Sequence[int]) -> tuple[float, ...]:
    bits = tuple(occupancy)
    if len(bits) != DIM or any(value not in (0, 1) for value in bits):
        raise AtomicT36AufbauError("occupancy must contain exactly 36 binary slot values")
    return tuple(((TAU * index / DIM) + math.pi * bit) % TAU for index, bit in enumerate(bits))


def complement_occupancy(occupancy: Sequence[int]) -> tuple[int, ...]:
    bits = tuple(occupancy)
    if len(bits) != DIM or any(value not in (0, 1) for value in bits):
        raise AtomicT36AufbauError("occupancy must contain exactly 36 binary slot values")
    return tuple(1 - value for value in bits)


def phase36_sha256(phase36: Sequence[float]) -> str:
    phase = tuple(float(value) for value in phase36)
    if len(phase) != DIM or any(not math.isfinite(value) or value < 0.0 or value >= TAU for value in phase):
        raise AtomicT36AufbauError("phase36 must contain 36 finite angles in [0,2*pi)")
    return _sha256_json(list(phase))


def pncs_v018_realization_binding(
    *,
    content_id: str,
    phase36: Sequence[float],
    source_digest_sha256: str,
    source_locator: str,
) -> dict[str, object]:
    phase = tuple(float(value) for value in phase36)
    phase_sha = phase36_sha256(phase)
    realization_payload: dict[str, object] = {
        "schema": PNCS_REALIZATION_SCHEMA,
        "content_id": content_id,
        "basis_id": BASIS_ID,
        "derivation_id": DERIVATION_ID,
        "space": "T^36",
        "coordinate_semantics": "phase_angles_radians",
        "coordinate_range": "[0,2π)",
        "phase36": list(phase),
        "phase36_sha256": phase_sha,
    }
    realization_id = _typed_id("pncs:realization36", realization_payload)
    binding_payload: dict[str, object] = {
        "schema": PNCS_REALIZATION_BINDING_SCHEMA,
        "realization_id": realization_id,
        "content_id": content_id,
        "basis_id": BASIS_ID,
        "derivation_id": DERIVATION_ID,
        "phase36_sha256": phase_sha,
        "source_digest_sha256": source_digest_sha256,
        "source_locator": source_locator,
        "epistemic_operator": "CHYBA",
        "canon_allowed": False,
    }
    return {
        "realization": realization_payload,
        "realization_id": realization_id,
        "binding": binding_payload,
        "binding_id": _typed_id("pncs:binding36", binding_payload),
    }


def pncs_v019_mass_binding(
    *,
    realization_record: Mapping[str, object],
    phase_index: int,
    phase36: Sequence[float],
) -> dict[str, object]:
    if isinstance(phase_index, bool) or not isinstance(phase_index, int) or phase_index < 1:
        raise AtomicT36AufbauError("phase_index must be a positive integer")
    realization = realization_record.get("realization")
    if not isinstance(realization, Mapping):
        raise AtomicT36AufbauError("v0.18 realization payload required")
    realization_id = str(realization_record.get("realization_id", ""))
    realization_binding_id = str(realization_record.get("binding_id", ""))
    content_id = str(realization.get("content_id", ""))
    semantic_mass = semantic_mass_value(phase_index, phase36)
    mass_payload: dict[str, object] = {
        "schema": PNCS_MASS_REALIZATION_SCHEMA,
        "content_id": content_id,
        "realization_id": realization_id,
        "phase_index": phase_index,
        "mass_contract_id": MASS_CONTRACT_ID,
        "runtime_source_sha256": RUNTIME_SOURCE_SHA256,
        "kappa": KAPPA,
        "alpha_m": ALPHA_M,
        "l3": L3,
        "l4": L4,
        "l5": L5,
        "l_ratio": L_RATIO,
        "order_parameter_R": phase_order_parameter(phase36),
        "semantic_mass": semantic_mass,
    }
    mass_realization_id = _typed_id("pncs:mass", mass_payload)
    binding_payload: dict[str, object] = {
        "schema": PNCS_MASS_BINDING_SCHEMA,
        "mass_realization_id": mass_realization_id,
        "content_id": content_id,
        "realization_id": realization_id,
        "realization_binding_id": realization_binding_id,
        "phase_index": phase_index,
        "mass_contract_id": MASS_CONTRACT_ID,
        "runtime_source_sha256": RUNTIME_SOURCE_SHA256,
        "runtime_source_locator": PNCS_MASS_RUNTIME_SOURCE_LOCATOR,
        "semantic_mass": semantic_mass,
        "epistemic_operator": "CHYBA",
        "canon_allowed": False,
    }
    return {
        "mass_realization": mass_payload,
        "mass_realization_id": mass_realization_id,
        "binding": binding_payload,
        "mass_binding_id": _typed_id("pncs:mass-binding", binding_payload),
    }


def build_atomic_t36_candidate(
    *,
    atom_card_id: str,
    electron_configuration: str,
    electron_count: int,
    source_raw: bytes,
    source_locator: str,
) -> dict[str, object]:
    if not atom_card_id.startswith("ATOM:"):
        raise AtomicT36AufbauError("atom_card_id must identify an atom card")
    if isinstance(electron_count, bool) or not isinstance(electron_count, int) or electron_count < 1 or electron_count > DIM:
        raise AtomicT36AufbauError("electron_count must be an integer in [1,36]")
    if not isinstance(source_raw, (bytes, bytearray)) or not source_raw:
        raise AtomicT36AufbauError("source_raw bytes are required")
    if not isinstance(source_locator, str) or not source_locator.strip():
        raise AtomicT36AufbauError("source_locator is required")

    occupancy = occupancy_vector36(electron_configuration)
    if sum(occupancy) != electron_count:
        raise AtomicT36AufbauError(
            f"electron configuration occupancy {sum(occupancy)} != electron_count {electron_count}"
        )
    phase36 = phase36_from_occupancy(occupancy)
    source_digest = _sha256_bytes(bytes(source_raw))
    content_id = f"pncs:file:sha256:{source_digest}"
    phase_index = sum(occupancy)
    realization_record = pncs_v018_realization_binding(
        content_id=content_id,
        phase36=phase36,
        source_digest_sha256=source_digest,
        source_locator=source_locator,
    )
    mass_record = pncs_v019_mass_binding(
        realization_record=realization_record,
        phase_index=phase_index,
        phase36=phase36,
    )
    bridge = AtomicPNCSSemanticMassBinding(
        atom_card_id=atom_card_id,
        phase_index=phase_index,
        phase36=phase36,
        realization_id=str(realization_record["realization_id"]),
        realization_binding_id=str(realization_record["binding_id"]),
        source_binding_id=str(mass_record["mass_binding_id"]),
    )
    if bridge.semantic_mass != mass_record["binding"]["semantic_mass"]:
        raise AtomicT36AufbauError("PNCS v0.19 mass parity mismatch")

    body: dict[str, object] = {
        "schema": CANDIDATE_SCHEMA,
        "prereg_schema": PREREG_SCHEMA,
        "atom_card_id": atom_card_id,
        "source_locator": source_locator,
        "source_digest_sha256": source_digest,
        "content_id": content_id,
        "electron_configuration": electron_configuration,
        "electron_count": electron_count,
        "slot_basis_id": BASIS_ID,
        "derivation_id": DERIVATION_ID,
        "occupancy36": list(occupancy),
        "phase_index": phase_index,
        "phase36": list(phase36),
        "phase36_sha256": phase36_sha256(phase36),
        "order_parameter_R": phase_order_parameter(phase36),
        "semantic_mass": bridge.semantic_mass,
        "pncs_v018": realization_record,
        "pncs_v019": mass_record,
        "reschem_bridge": bridge.payload,
        "epistemic_operator": "CHYBA",
        "canon_allowed": False,
        "spectral_input": "NONE",
    }
    return {**body, "candidate_sha256": _sha256_json(body)}
