from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Iterable

KAPPA = math.log(2.0) / (24.0 * math.pi)
LAPSE_MIN = 1.0 / 64.0
LAPSE_MAX = 8.0
SCHEMA = "RESCHEM_ATOMIC_SUBJECTIVE_TIME_CANDIDATE_V0_15"
PREREG_SCHEMA = "RESCHEM_ATOMIC_SUBJECTIVE_TIME_POSTJOIN_HYPOTHESIS_PREREG_V0_15"


class AtomicSubjectiveTimeV015Error(ValueError):
    pass


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _sha256_json(value: object) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def _finite_positive(value: float, name: str) -> float:
    x = float(value)
    if not math.isfinite(x) or x <= 0.0:
        raise AtomicSubjectiveTimeV015Error(f"{name} must be finite and positive")
    return x


def hydrodynamic_lapse(density: float, effective_viscosity: float) -> tuple[float, float]:
    rho = _finite_positive(density, "density")
    nu = float(effective_viscosity)
    if not math.isfinite(nu) or nu < 0.0:
        raise AtomicSubjectiveTimeV015Error("effective_viscosity must be finite and nonnegative")
    raw = math.sqrt(rho) / (1.0 + nu)
    return raw, min(LAPSE_MAX, max(LAPSE_MIN, raw))


@dataclass(frozen=True)
class AtomicSubjectiveTimeCandidate:
    symbol: str
    z: int
    policy_id: str
    radial_nuclear_exposure: float
    semantic_mass: float
    x_kappa_exposure: float
    y_mass_over_kappa: float
    density: float
    effective_viscosity: float
    lapse_unclamped: float
    lapse: float

    @property
    def payload(self) -> dict[str, object]:
        return {
            "schema": SCHEMA,
            "prereg_schema": PREREG_SCHEMA,
            "symbol": self.symbol,
            "Z": self.z,
            "policy_id": self.policy_id,
            "kappa": KAPPA,
            "radial_nuclear_exposure": self.radial_nuclear_exposure,
            "semantic_mass": self.semantic_mass,
            "x_kappa_exposure": self.x_kappa_exposure,
            "y_mass_over_kappa": self.y_mass_over_kappa,
            "density": self.density,
            "effective_viscosity": self.effective_viscosity,
            "pncs_lapse_expression": "sqrt(density)/(1+effective_viscosity)",
            "lapse_unclamped": self.lapse_unclamped,
            "lapse": self.lapse,
            "lapse_bounds": [LAPSE_MIN, LAPSE_MAX],
            "fit_parameters": [],
            "calibration_parameters": [],
            "stage_c_result_used_as_input": False,
            "nist_values_used_as_input": False,
            "epistemic_operator": "CHYBA",
            "canon_allowed": False,
        }

    def as_dict(self) -> dict[str, object]:
        body = self.payload
        return {**body, "candidate_sha256": _sha256_json(body)}


def atomic_subjective_time_candidates(
    *,
    symbol: str,
    z: int,
    radial_nuclear_exposure: float,
    semantic_mass: float,
) -> tuple[AtomicSubjectiveTimeCandidate, ...]:
    sym = str(symbol).strip()
    if not sym:
        raise AtomicSubjectiveTimeV015Error("symbol must be nonempty")
    zz = int(z)
    if zz <= 0:
        raise AtomicSubjectiveTimeV015Error("Z must be positive")
    exposure = _finite_positive(radial_nuclear_exposure, "radial_nuclear_exposure")
    mass = _finite_positive(semantic_mass, "semantic_mass")

    x = KAPPA * exposure
    y = mass / KAPPA
    policies: tuple[tuple[str, float, float], ...] = (
        ("NULL_REST_CONTROL", 1.0, 0.0),
        ("KAPPA_RADIAL_BALANCED", 1.0 + x, x),
        ("SEMANTIC_MASS_BALANCED", 1.0 + y, y),
        ("RADIAL_SEMANTIC_GEOMETRIC_COUPLING", 1.0 + x, math.sqrt(x * y)),
        ("RADIAL_SEMANTIC_PRODUCT_COUPLING", 1.0 + x, x * y),
    )
    out: list[AtomicSubjectiveTimeCandidate] = []
    for policy_id, rho, nu in policies:
        raw, lapse = hydrodynamic_lapse(rho, nu)
        out.append(
            AtomicSubjectiveTimeCandidate(
                symbol=sym,
                z=zz,
                policy_id=policy_id,
                radial_nuclear_exposure=exposure,
                semantic_mass=mass,
                x_kappa_exposure=x,
                y_mass_over_kappa=y,
                density=rho,
                effective_viscosity=nu,
                lapse_unclamped=raw,
                lapse=lapse,
            )
        )
    return tuple(out)


def candidate_policy_ids(candidates: Iterable[AtomicSubjectiveTimeCandidate]) -> tuple[str, ...]:
    return tuple(c.policy_id for c in candidates)
