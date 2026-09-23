import math
import unittest

from reschem.h3plus_ci_berry_control_v01 import (
    H3PlusCIBerryError,
    equilateral_reference,
    frozen_loop_geometries,
    h3plus_atoms_from_polar,
)


class H3PlusCIBerryControlV01Tests(unittest.TestCase):
    def test_equilateral_reference_has_equal_side_lengths(self):
        R = 2.0
        rho, theta = equilateral_reference(R_bohr=R)
        atoms = h3plus_atoms_from_polar(
            R_bohr=R,
            rho_bohr=rho,
            theta_rad=theta,
        )
        xyz = [a[1] for a in atoms]

        def distance(a, b):
            return math.sqrt(sum((x-y)**2 for x, y in zip(a, b)))

        sides = [
            distance(xyz[0], xyz[1]),
            distance(xyz[1], xyz[2]),
            distance(xyz[2], xyz[0]),
        ]
        for side in sides:
            self.assertAlmostEqual(side, 2.0 * R, places=12)

    def test_frozen_loops_have_expected_size_and_are_distinct(self):
        enc = frozen_loop_geometries(encircling=True)
        ctl = frozen_loop_geometries(encircling=False)
        self.assertEqual(len(enc), 24)
        self.assertEqual(len(ctl), 24)
        self.assertNotEqual(enc[0], ctl[0])

    def test_invalid_geometry_fails_closed(self):
        with self.assertRaises(H3PlusCIBerryError):
            h3plus_atoms_from_polar(R_bohr=0.0, rho_bohr=1.0, theta_rad=0.0)
        with self.assertRaises(H3PlusCIBerryError):
            frozen_loop_geometries(encircling=True, samples=3)


if __name__ == "__main__":
    unittest.main()
