import math
import unittest

import numpy as np

from reschem.orientation_scan import (
    OrientationScanError,
    pp_orientation_control_point,
    rotate_fragment,
    rotation_matrix,
    scan_pp_orientation,
    xy2_rigid_orientation_coordinates,
)


class OrientationScanControlTests(unittest.TestCase):
    def test_rotation_matrix_is_proper_orthogonal(self):
        r = rotation_matrix((1.0, 2.0, -3.0), 0.71)
        np.testing.assert_allclose(r.T @ r, np.eye(3), rtol=0.0, atol=1e-12)
        self.assertAlmostEqual(float(np.linalg.det(r)), 1.0, places=12)

    def test_fragment_rotation_preserves_rigid_internal_geometry(self):
        coords = np.asarray(
            [
                [0.0, 0.0, 0.0],
                [2.0, 0.0, 0.0],
                [2.0, 1.0, 0.0],
                [2.0, 0.0, 1.0],
            ]
        )
        pivot = np.asarray([2.0, 0.0, 0.0])
        out = rotate_fragment(
            coords,
            (1, 2, 3),
            pivot=pivot,
            axis=(1.0, 0.0, 0.0),
            angle_rad=1.1,
        )
        np.testing.assert_allclose(out[0], coords[0], atol=0.0)
        for i in (1, 2, 3):
            self.assertAlmostEqual(
                np.linalg.norm(out[i] - pivot),
                np.linalg.norm(coords[i] - pivot),
                places=12,
            )
        self.assertAlmostEqual(
            np.linalg.norm(out[2] - out[3]),
            np.linalg.norm(coords[2] - coords[3]),
            places=12,
        )

    def test_xy2_scan_changes_only_orientation_control_coordinate(self):
        ryy, distance = 2.4, 3.7
        for theta in (0.0, math.pi / 7.0, math.pi / 2.0):
            xyz = xy2_rigid_orientation_coordinates(ryy, distance, theta)
            midpoint = 0.5 * (xyz[1] + xyz[2])
            self.assertAlmostEqual(
                np.linalg.norm(xyz[2] - xyz[1]), ryy, places=12
            )
            self.assertAlmostEqual(
                np.linalg.norm(xyz[0] - midpoint), distance, places=12
            )

    def test_symmetric_pp_gap_follows_two_abs_t_cos_theta(self):
        t0 = 0.08
        for theta in (0.0, math.pi / 6.0, math.pi / 3.0, math.pi / 2.0):
            point = pp_orientation_control_point(
                theta,
                epsilon_a_hartree=-0.3,
                epsilon_b_hartree=-0.3,
                coupling_hartree=t0,
            )
            expected = 2.0 * abs(t0 * math.cos(theta))
            self.assertAlmostEqual(point.gap_hartree, expected, places=12)

    def test_detuned_pp_gap_has_exact_closed_form(self):
        ea, eb, t0, theta = -0.2, 0.1, 0.05, 0.73
        point = pp_orientation_control_point(
            theta,
            epsilon_a_hartree=ea,
            epsilon_b_hartree=eb,
            coupling_hartree=t0,
        )
        delta = 0.5 * (ea - eb)
        expected = 2.0 * math.sqrt(
            delta * delta + (t0 * math.cos(theta)) ** 2
        )
        self.assertAlmostEqual(point.gap_hartree, expected, places=12)

    def test_ninety_degree_pp_control_removes_only_orientation_coupling(self):
        point = pp_orientation_control_point(
            math.pi / 2.0,
            epsilon_a_hartree=-0.2,
            epsilon_b_hartree=0.1,
            coupling_hartree=0.08,
        )
        self.assertAlmostEqual(point.coupling_hartree, 0.0, places=12)
        self.assertAlmostEqual(point.gap_hartree, 0.3, places=12)

    def test_scan_preserves_requested_angle_order(self):
        angles = (0.8, 0.1, 1.2)
        points = scan_pp_orientation(
            angles,
            epsilon_a_hartree=-0.1,
            epsilon_b_hartree=0.2,
            coupling_hartree=0.04,
        )
        self.assertEqual(tuple(p.angle_rad for p in points), angles)

    def test_fail_closed_domains(self):
        with self.assertRaises(OrientationScanError):
            rotation_matrix((0.0, 0.0, 0.0), 0.2)
        with self.assertRaises(OrientationScanError):
            rotate_fragment(
                [[0.0, 0.0, 0.0]],
                (),
                pivot=(0, 0, 0),
                axis=(0, 0, 1),
                angle_rad=0.2,
            )
        with self.assertRaises(OrientationScanError):
            rotate_fragment(
                [[0.0, 0.0, 0.0]],
                (0.5,),
                pivot=(0, 0, 0),
                axis=(0, 0, 1),
                angle_rad=0.2,
            )
        with self.assertRaises(OrientationScanError):
            xy2_rigid_orientation_coordinates(-1.0, 2.0, 0.0)
        with self.assertRaises(OrientationScanError):
            scan_pp_orientation(
                (),
                epsilon_a_hartree=0.0,
                epsilon_b_hartree=1.0,
                coupling_hartree=0.1,
            )


if __name__ == "__main__":
    unittest.main()
