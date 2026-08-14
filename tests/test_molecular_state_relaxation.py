import unittest

from reschem.molecular_state_relaxation import (
    ACTIVATED_SCALES,
    DIMER_INITIAL_DISTANCE_ANGSTROM,
    METHOD_POLICY,
    WEAK_COMPLEX_SCALE,
    add_relative_energies,
    dimer_bond_length_angstrom,
    ligand_dimer_seed,
    xy2_geometry_descriptors,
    xy2_seed_geometries,
)


class MolecularStateRelaxationTests(unittest.TestCase):
    def test_dimer_seed_is_common_two_angstrom(self):
        for ligand in ("F", "Cl", "Br"):
            seed = ligand_dimer_seed(ligand)
            self.assertAlmostEqual(
                dimer_bond_length_angstrom(seed.coordinates_angstrom),
                DIMER_INITIAL_DISTANCE_ANGSTROM,
            )

    def test_each_formula_has_five_frozen_starts(self):
        seeds = xy2_seed_geometries("Kr", "F", 1.4)
        self.assertEqual(len(seeds), 5)
        self.assertEqual(
            [seed.state_kind for seed in seeds],
            [
                "ACTIVATED_LINEAR_3C4E",
                "ACTIVATED_LINEAR_3C4E",
                "ACTIVATED_LINEAR_3C4E",
                "WEAK_COMPLEX_LINEAR_END_ON",
                "WEAK_COMPLEX_T_SHAPED",
            ],
        )

    def test_activated_scales_are_global_and_exact(self):
        self.assertEqual(ACTIVATED_SCALES, (1.0, 1.3, 1.6))
        seeds = xy2_seed_geometries("Ne", "Br", 2.3)[:3]
        for seed, scale in zip(seeds, ACTIVATED_SCALES):
            desc = xy2_geometry_descriptors(seed.coordinates_angstrom)
            self.assertAlmostEqual(desc["X_Y1_angstrom"], scale * 2.3)
            self.assertAlmostEqual(desc["X_Y2_angstrom"], scale * 2.3)
            self.assertAlmostEqual(desc["Y_X_Y_angle_degrees"], 180.0)

    def test_weak_linear_preserves_seed_dimer_and_global_separation(self):
        ryy = 2.0
        seed = xy2_seed_geometries("Ar", "Cl", ryy)[3]
        desc = xy2_geometry_descriptors(seed.coordinates_angstrom)
        self.assertAlmostEqual(desc["Y_Y_angstrom"], ryy)
        self.assertAlmostEqual(desc["X_Y1_angstrom"], WEAK_COMPLEX_SCALE * ryy)

    def test_t_shape_has_ninety_degree_centre_angle_only_for_symmetric_vectors(self):
        seed = xy2_seed_geometries("Ne", "F", 1.5)[4]
        desc = xy2_geometry_descriptors(seed.coordinates_angstrom)
        # At X, the two vectors to the ligand atoms form an acute angle; the
        # seed topology is defined by X-to-YY-midpoint perpendicularity, not
        # by forcing Y-X-Y to 90 degrees.
        self.assertGreater(desc["Y_X_Y_angle_degrees"], 0.0)
        self.assertLess(desc["Y_X_Y_angle_degrees"], 90.0)
        self.assertAlmostEqual(desc["Y_Y_angstrom"], 1.5)
        self.assertAlmostEqual(desc["X_to_YY_midpoint_angstrom"], 1.8 * 1.5)

    def test_method_policy_is_frozen_without_hessian_or_rescue(self):
        self.assertEqual(METHOD_POLICY["xc"], "b97m_v")
        self.assertEqual(METHOD_POLICY["nlc"], "vv10")
        self.assertEqual(METHOD_POLICY["basis"], "def2-tzvpd")
        self.assertEqual(METHOD_POLICY["scf_max_cycle"], 200)
        self.assertNotIn("hessian", METHOD_POLICY)
        self.assertNotIn("rescue", METHOD_POLICY)

    def test_relative_energy_is_within_formula_and_threshold_free(self):
        rows = add_relative_energies([
            {"status":"RELAXATION_RETURNED_FINAL_SCF_CONVERGED_NO_HESSIAN","final_energy_hartree":-10.0},
            {"status":"RELAXATION_RETURNED_FINAL_SCF_CONVERGED_NO_HESSIAN","final_energy_hartree":-9.99},
            {"status":"RELAXATION_EXCEPTION","final_energy_hartree":None},
        ])
        self.assertAlmostEqual(rows[0]["relative_energy_kcal_mol"], 0.0)
        self.assertGreater(rows[1]["relative_energy_kcal_mol"], 0.0)
        self.assertIsNone(rows[2]["relative_energy_kcal_mol"])

    def test_invalid_dimer_length_fails_closed(self):
        with self.assertRaises(ValueError):
            xy2_seed_geometries("Kr", "F", 0.0)


if __name__ == "__main__":
    unittest.main()
