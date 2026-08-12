import unittest

from reschem.carbon_sparse_multichannel_ci import solve_carbon_sparse_multichannel_ci


class CarbonSparseMultichannelCITests(unittest.TestCase):
    def test_sparse_balanced_space_and_low_terms(self):
        result = solve_carbon_sparse_multichannel_ci(
            basis_size=16,
            grid_points=600,
            tolerance_hartree=2.0e-9,
            eigenpairs=24,
        )
        self.assertEqual(result.spin_orbitals, 24)
        self.assertEqual(result.even_determinants, 5346)
        self.assertGreater(result.hamiltonian_nnz, result.even_determinants)
        self.assertEqual(result.ground_term, "^3P")
        self.assertGreater(result.term_energy_cm1("^1D"), 0.0)
        self.assertGreater(result.term_energy_cm1("^1S"), result.term_energy_cm1("^1D"))


if __name__ == "__main__":
    unittest.main()
