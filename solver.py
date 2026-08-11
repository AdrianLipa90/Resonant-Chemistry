#!/usr/bin/env python3
"""ResChem atomic solver v0.1.

Deterministic atomic identity/configuration solver plus analytic and numerical
hydrogen-like benchmarks. Multi-electron total energies are intentionally not
estimated in this version.
"""

import argparse
import json
from reschem.atom import Atom
from reschem.radial import numerical_hydrogenic_energy_ev


def main() -> int:
    p = argparse.ArgumentParser(description="Resonant Chemistry atom solver v0.1")
    p.add_argument("--Z", type=int, required=True, help="proton / atomic number")
    p.add_argument("--N", type=int, required=True, help="neutron count")
    p.add_argument("--charge", type=int, default=0, help="net ionic charge in units of e")
    p.add_argument("--n", type=int, default=1, help="principal n for one-electron benchmark")
    p.add_argument("--l", type=int, default=0, help="orbital angular momentum for numeric radial solve")
    p.add_argument("--numeric", action="store_true", help="run finite-difference radial solver for one-electron species")
    p.add_argument("--points", type=int, default=600, help="radial grid points for --numeric")
    args = p.parse_args()

    atom = Atom(args.Z, args.N, args.charge)
    data = atom.as_dict(principal_n=args.n)
    if args.numeric:
        if not atom.is_hydrogenic:
            raise SystemExit("--numeric v0.1 is restricted to one-electron species")
        numeric = numerical_hydrogenic_energy_ev(
            z=atom.z, n=args.n, l=args.l, points=args.points
        )
        analytic = data["hydrogenic_solution"]["energy_eV"]
        data["radial_numeric_solution"] = {
            "method": "second_order_finite_difference_dense_eigensolve",
            "points": args.points,
            "l": args.l,
            "energy_eV": numeric,
            "analytic_energy_eV": analytic,
            "relative_error": abs((numeric - analytic) / analytic),
        }
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
