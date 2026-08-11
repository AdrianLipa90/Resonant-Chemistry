#!/usr/bin/env python3
"""ResChem atomic solver v0.1.

Deterministic atomic identity/configuration solver plus exact non-relativistic
hydrogen-like benchmark. Multi-electron total energies are intentionally not
estimated in this version.
"""

import argparse
import json
from reschem.atom import Atom


def main() -> int:
    p = argparse.ArgumentParser(description="Resonant Chemistry atom solver v0.1")
    p.add_argument("--Z", type=int, required=True, help="proton / atomic number")
    p.add_argument("--N", type=int, required=True, help="neutron count")
    p.add_argument("--charge", type=int, default=0, help="net ionic charge in units of e")
    p.add_argument("--n", type=int, default=1, help="principal n for one-electron benchmark")
    args = p.parse_args()

    atom = Atom(args.Z, args.N, args.charge)
    print(json.dumps(atom.as_dict(principal_n=args.n), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
