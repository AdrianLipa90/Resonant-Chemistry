from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from reschem.carbon_state_averaged_orbital_relaxation import (
    _normalize_weights,
    _point_for_theta,
    _reference_with_external_p,
)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--basis-size", type=int, default=18)
    ap.add_argument("--grid-points", type=int, default=800)
    ap.add_argument("--tolerance-hartree", type=float, default=1.0e-9)
    ap.add_argument("--coarse-points", type=int, default=21)
    ap.add_argument("--theta-limit", type=float, default=1.45)
    ap.add_argument("--refine-points", type=int, default=11)
    ap.add_argument("--output", default="ci_artifacts/CARBON_STATE_AVERAGED_P_RELAXATION_V0_1.json")
    args = ap.parse_args()

    if args.coarse_points < 5 or args.coarse_points % 2 == 0:
        raise SystemExit("coarse-points must be odd and >=5")
    if args.refine_points < 5 or args.refine_points % 2 == 0:
        raise SystemExit("refine-points must be odd and >=5")
    if not (0.0 < args.theta_limit < math.pi / 2):
        raise SystemExit("theta-limit must be in (0, pi/2)")

    objective_terms = ("^3P", "^1D", "^1S")
    objective_weights = _normalize_weights((1.0, 1.0, 1.0), 3)

    r, weights_grid, u2s, p_radials3, h_s, h_p3 = _reference_with_external_p(
        basis_size=args.basis_size,
        grid_points=args.grid_points,
        tolerance_hartree=args.tolerance_hartree,
    )

    def evaluate(theta: float):
        return _point_for_theta(
            float(theta),
            r=r,
            weights_grid=weights_grid,
            u2s=u2s,
            p_radials3=p_radials3,
            h_s=h_s,
            h_p3=h_p3,
            objective_terms=objective_terms,
            objective_weights=objective_weights,
        )

    coarse_angles = np.linspace(-args.theta_limit, args.theta_limit, args.coarse_points)
    coarse = tuple(evaluate(float(theta)) for theta in coarse_angles)
    coarse_values = np.asarray([p.state_average_hartree for p in coarse])
    coarse_best = int(np.argmin(coarse_values))

    # Refine only after the globally predeclared coarse scan.  The refinement
    # interval is determined from adjacent coarse grid points, not from any
    # experimental spectrum.
    if coarse_best == 0 or coarse_best == len(coarse) - 1:
        refine_lo = max(-math.pi / 2 + 1.0e-4, float(coarse_angles[max(0, coarse_best - 1)]))
        refine_hi = min(math.pi / 2 - 1.0e-4, float(coarse_angles[min(len(coarse)-1, coarse_best + 1)]))
    else:
        refine_lo = float(coarse_angles[coarse_best - 1])
        refine_hi = float(coarse_angles[coarse_best + 1])
    refined_angles = np.linspace(refine_lo, refine_hi, args.refine_points)
    refined = tuple(evaluate(float(theta)) for theta in refined_angles)
    refined_values = np.asarray([p.state_average_hartree for p in refined])
    refined_best = int(np.argmin(refined_values))

    baseline = min(coarse, key=lambda p: abs(p.theta_rad))
    best = refined[refined_best]
    improvement = baseline.state_average_hartree - best.state_average_hartree
    boundary = refined_best in (0, len(refined) - 1)

    payload = {
        "schema": "RESCHEM_CARBON_STATE_AVERAGED_P_RELAXATION_BENCHMARK_V0_1",
        "status": "PASS_VARIATIONAL_DIRECTION" if improvement > 1.0e-8 else "NO_STRICT_VARIATIONAL_GAIN",
        "epistemic_status": "PRODUCTION_NUMERICAL_CANDIDATE_NOT_MCSCF_CANON",
        "configuration": {
            "basis_size": args.basis_size,
            "grid_points": args.grid_points,
            "tolerance_hartree": args.tolerance_hartree,
            "objective_terms": list(objective_terms),
            "weights": list(objective_weights),
            "coarse_points": args.coarse_points,
            "theta_limit_rad": args.theta_limit,
            "refine_points": args.refine_points,
            "refine_interval_rad": [refine_lo, refine_hi],
        },
        "baseline": baseline.as_dict(),
        "coarse_best": coarse[coarse_best].as_dict(),
        "best": best.as_dict(),
        "improvement_hartree": float(improvement),
        "refined_minimum_on_boundary": bool(boundary),
        "coarse_points_data": [p.as_dict() for p in coarse],
        "refined_points_data": [p.as_dict() for p in refined],
        "acceptance": {
            "strict_variational_gain": bool(improvement > 1.0e-8),
            "minimum_interior_to_refined_interval": bool(not boundary),
            "experimental_term_energies_used_in_objective": False,
            "tir_used": False,
            "affective_mapping_used": False,
        },
        "interpretation_boundary": [
            "This benchmark tests one radial-p active-external coordinate only.",
            "A strict energy decrease shows the frozen active p subspace is not stationary along this tested direction.",
            "It is not a full MCSCF/CASSCF result and does not validate knot, conformal, TIR, or affective physics.",
        ],
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
