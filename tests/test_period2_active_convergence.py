import math
import unittest

from reschem.period2_active_convergence import solve_carbon_active_space_convergence


class Period2ActiveConvergenceTests(unittest.TestCase):
    def test_carbon_2_3_4_radial_spaces_remain_physical(self):
        points = solve_carbon_active_space_convergence(
            radial_spaces=(2, 3, 4),
            basis_size=18,
            grid_points=800,
        )
        self.assertEqual([point.radial_orbitals for point in points], [2, 3, 4])
        for point in points:
            self.assertEqual(point.ground_term, "^3P")
            self.assertEqual(
                point.determinant_count,
                math.comb(6 * point.radial_orbitals, 2),
            )
            self.assertGreater(point.term_centers_cm1["^1D"], 0.0)
            self.assertGreater(point.term_centers_cm1["^1S"], point.term_centers_cm1["^1D"])

    def test_first_active_space_extension_is_not_singular(self):
        points = solve_carbon_active_space_convergence(
            radial_spaces=(2, 3),
            basis_size=18,
            grid_points=800,
        )
        for term in ("^1D", "^1S"):
            delta = abs(points[1].term_centers_cm1[term] - points[0].term_centers_cm1[term])
            self.assertLess(delta, 5000.0)


if __name__ == "__main__":
    unittest.main()
