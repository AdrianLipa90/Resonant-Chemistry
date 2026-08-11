from __future__ import annotations

from dataclasses import dataclass
import numpy as np

HARTREE_TO_EV = 27.211386245988


@dataclass(frozen=True)
class RadialEigenstate:
    z: int
    n: int
    l: int
    energy_hartree: float
    energy_ev: float
    radius_bohr: np.ndarray
    u: np.ndarray

    @property
    def radial_probability(self) -> np.ndarray:
        """Probability density in dr for u(r)=rR(r): |u(r)|^2."""
        return np.abs(self.u) ** 2


def hydrogenic_radial_states(
    z: int,
    l: int = 0,
    states: int = 3,
    points: int = 600,
    r_max_bohr: float | None = None,
) -> list[RadialEigenstate]:
    """Finite-difference radial Schrödinger solver in atomic units.

    Solves for u(r)=rR(r) with Dirichlet boundaries and
        H = -1/2 d^2/dr^2 + l(l+1)/(2r^2) - Z/r.

    This solver is only a one-electron Coulomb benchmark. It is intentionally
    separate from future many-electron ResChem layers.
    """
    if z <= 0:
        raise ValueError("Z must be positive")
    if l < 0:
        raise ValueError("l must be non-negative")
    if states <= 0:
        raise ValueError("states must be positive")
    if points < 100:
        raise ValueError("use at least 100 radial grid points")

    if r_max_bohr is None:
        r_max_bohr = 40.0 / z
    if r_max_bohr <= 0:
        raise ValueError("r_max_bohr must be positive")

    dr = r_max_bohr / (points + 1)
    r = np.arange(1, points + 1, dtype=float) * dr

    diagonal = (
        np.full(points, 1.0 / dr**2)
        + l * (l + 1) / (2.0 * r**2)
        - z / r
    )
    off_diagonal = np.full(points - 1, -0.5 / dr**2)
    hamiltonian = (
        np.diag(diagonal)
        + np.diag(off_diagonal, 1)
        + np.diag(off_diagonal, -1)
    )

    eigenvalues, eigenvectors = np.linalg.eigh(hamiltonian)
    bound = [(e, eigenvectors[:, i]) for i, e in enumerate(eigenvalues) if e < 0]
    if len(bound) < states:
        raise RuntimeError("radial box/grid does not contain enough bound states")

    out: list[RadialEigenstate] = []
    for index, (energy, vec) in enumerate(bound[:states]):
        # For fixed l, the j-th radial bound state has n=l+1+j.
        n = l + 1 + index
        norm = float(np.sqrt(np.trapezoid(np.abs(vec) ** 2, r)))
        u = vec / norm
        out.append(
            RadialEigenstate(
                z=z,
                n=n,
                l=l,
                energy_hartree=float(energy),
                energy_ev=float(energy * HARTREE_TO_EV),
                radius_bohr=r.copy(),
                u=u,
            )
        )
    return out


def numerical_hydrogenic_energy_ev(
    z: int,
    n: int = 1,
    l: int = 0,
    points: int = 600,
) -> float:
    if n <= l:
        raise ValueError("hydrogenic states require n > l")
    index = n - l - 1
    states = hydrogenic_radial_states(z=z, l=l, states=index + 1, points=points)
    return states[index].energy_ev
