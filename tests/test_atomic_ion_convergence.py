import unittest
from types import SimpleNamespace

from reschem.atomic_ion_convergence import LEVELS, run_atomic_state_scan, state_label


class FakeSolver:
    def __init__(self):
        self.calls = []

    def __call__(self, z, charge, **kwargs):
        self.calls.append((z, charge, dict(kwargs)))
        level_index = [level.basis_size for level in LEVELS].index(kwargs["basis_size"])
        energy = -float(z * z) - 0.1 * charge - 0.01 / (level_index + 1)
        return SimpleNamespace(
            configuration=f"Z{z} q{charge}",
            energy_hartree=energy,
            converged=True,
            iterations=10 + level_index,
            virial_residual_hartree=0.3 / (level_index + 1),
            basis_size=kwargs["basis_size"],
            grid_points=kwargs["grid_points"],
        )


class AtomicIonConvergenceTests(unittest.TestCase):
    def test_three_frozen_levels_are_used_for_every_state(self):
        solver = FakeSolver()
        result = run_atomic_state_scan(9, -1, solver=solver)
        self.assertEqual([row["level"] for row in result["levels"]], ["L0", "L1", "L2"])
        self.assertEqual(len(solver.calls), 3)

    def test_levels_match_preregistered_numerical_ladder(self):
        self.assertEqual(
            [(x.basis_size, x.grid_points, x.zeta_min, x.radial_grid_max_bohr) for x in LEVELS],
            [(20,1000,0.02,120.0),(24,1400,0.01,180.0),(28,1800,0.005,240.0)],
        )

    def test_no_convergence_boolean_is_invented(self):
        result = run_atomic_state_scan(35, -1, solver=FakeSolver())
        self.assertNotIn("convergence_pass", result)
        self.assertNotIn("threshold", result)
        self.assertIn("NO_CONVERGENCE_THRESHOLD", result["status"])

    def test_adjacent_drift_is_raw_difference(self):
        result = run_atomic_state_scan(10, 0, solver=FakeSolver())
        levels = result["levels"]
        drifts = result["adjacent_energy_drift"]
        self.assertEqual(len(drifts), 2)
        self.assertAlmostEqual(
            drifts[0]["signed_energy_drift_hartree"],
            levels[1]["energy_hartree"] - levels[0]["energy_hartree"],
        )

    def test_state_labels(self):
        self.assertEqual(state_label(9, -1), "F-")
        self.assertEqual(state_label(10, 0), "Ne")
        self.assertEqual(state_label(10, 1), "Ne+")


if __name__ == "__main__":
    unittest.main()
