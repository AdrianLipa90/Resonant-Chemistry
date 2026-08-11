import unittest

from reschem.ci_helium import solve_helium_radial_ci
from reschem.state_observables import helium_ci_one_body_observables


class HeliumStateObservableTests(unittest.TestCase):
    def test_trace_is_two_electrons(self):
        obs = helium_ci_one_body_observables(points=199, spatial_orbitals=5)
        self.assertAlmostEqual(obs.trace, 2.0, places=10)

    def test_observable_energy_matches_ci_solver(self):
        obs = helium_ci_one_body_observables(points=199, spatial_orbitals=5)
        ci = solve_helium_radial_ci(points=199, spatial_orbitals=5)
        self.assertAlmostEqual(obs.energy_hartree, ci.ci_energy_hartree, places=11)

    def test_correlation_produces_nonzero_one_body_entropy(self):
        obs = helium_ci_one_body_observables(points=199, spatial_orbitals=5)
        self.assertGreater(obs.one_body_entropy_nats, 0.0)
        self.assertGreater(obs.one_body_linear_entropy, 0.0)
        self.assertLess(obs.natural_occupations[0], 2.0)
        self.assertGreater(obs.natural_occupations[1], 0.0)


if __name__ == "__main__":
    unittest.main()
