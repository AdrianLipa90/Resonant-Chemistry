import math
import unittest

from reschem.knot_conformal_analysis import (
    electron_hole_pairs,
    inverse_conformal_value,
    normalized_cyclic_gaps,
    signed_winding,
    trajectory,
)


class KnotConformalAnalysisTests(unittest.TestCase):
    def test_unknot_has_zero_winding_about_half(self):
        values = trajectory({0: 1.0}, samples=512, anchor=0.5)
        self.assertEqual(signed_winding(values), 0)

    def test_inverse_map_raises_on_anchor(self):
        with self.assertRaises(ZeroDivisionError):
            inverse_conformal_value(0.5, anchor=0.5)

    def test_cyclic_gaps_normalize(self):
        gaps = normalized_cyclic_gaps((0.0, math.pi / 2, math.pi, 3 * math.pi / 2))
        self.assertEqual(len(gaps), 4)
        self.assertTrue(all(math.isclose(gap, 0.25) for gap in gaps))
        self.assertTrue(math.isclose(sum(gaps), 1.0))

    def test_p_shell_electron_hole_pairs_are_intrinsic(self):
        pairs = electron_hole_pairs({"B": 1, "C": 2, "N": 3, "O": 4, "F": 5})
        self.assertIn(("B", "F"), pairs)
        self.assertIn(("C", "O"), pairs)
        self.assertIn(("N", "N"), pairs)


if __name__ == "__main__":
    unittest.main()
