import unittest

from reschem.atomic_quality import virial_quality


class AtomicQualityTests(unittest.TestCase):
    def test_exact_virial_state_has_lambda_one(self):
        q = virial_quality(-100.0, 0.0)
        self.assertAlmostEqual(q.relative_defect, 0.0)
        self.assertAlmostEqual(q.uniform_scale_stationary_lambda, 1.0)
        self.assertAlmostEqual(q.uniformly_scaled_energy_hartree, -100.0)

    def test_cobalt_control_defect_is_small_dimensionlessly(self):
        q = virial_quality(-1380.575388932793, 1.7366581542591462)
        self.assertLess(q.relative_defect, 1.3e-3)
        self.assertGreater(q.relative_defect, 1.2e-3)
        self.assertLess(abs(q.uniform_scale_stationary_lambda - 1.0), 7e-4)

    def test_scaling_is_variationally_nonincreasing(self):
        q = virial_quality(-1380.575388932793, 1.7366581542591462)
        self.assertLessEqual(q.uniformly_scaled_energy_hartree, q.energy_hartree)


if __name__ == "__main__":
    unittest.main()
