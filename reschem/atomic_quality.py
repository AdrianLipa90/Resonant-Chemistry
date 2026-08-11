from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True)
class VirialQuality:
    energy_hartree: float
    virial_residual_hartree: float

    @property
    def absolute_defect_hartree(self) -> float:
        return abs(self.virial_residual_hartree)

    @property
    def relative_defect(self) -> float:
        if self.energy_hartree == 0.0:
            return math.inf
        return self.absolute_defect_hartree / abs(self.energy_hartree)

    @property
    def kinetic_hartree(self) -> float:
        # E=T+V and R=2T+V=T+E -> T=R-E.
        return self.virial_residual_hartree - self.energy_hartree

    @property
    def potential_hartree(self) -> float:
        return 2.0 * self.energy_hartree - self.virial_residual_hartree

    @property
    def uniform_scale_stationary_lambda(self) -> float:
        """Coordinate scale minimizing E(lambda)=lambda^2 T + lambda V.

        This is a diagnostic variational rescaling, not a replacement HF result.
        lambda=1 is exact virial stationarity for the supplied state.
        """
        t = self.kinetic_hartree
        if t <= 0.0:
            return math.nan
        return -self.potential_hartree / (2.0 * t)

    @property
    def uniformly_scaled_energy_hartree(self) -> float:
        lam = self.uniform_scale_stationary_lambda
        if not math.isfinite(lam):
            return math.nan
        return lam * lam * self.kinetic_hartree + lam * self.potential_hartree


def virial_quality(energy_hartree: float, virial_residual_hartree: float) -> VirialQuality:
    return VirialQuality(float(energy_hartree), float(virial_residual_hartree))
