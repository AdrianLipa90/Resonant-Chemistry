import unittest

from reschem.compound_state_ensemble import (
    closed_shell_xy2_state_ensemble,
    generate_closed_shell_state_ensemble_atlas,
    group_states_by_formula,
)


Z = {"F":9,"Ne":10,"Cl":17,"Ar":18,"Br":35,"Kr":36,"K":19}


class CompoundStateEnsembleTests(unittest.TestCase):
    def test_every_v09_formula_has_three_competing_states(self):
        grouped = group_states_by_formula()
        self.assertEqual(len(grouped), 9)
        self.assertTrue(all(len(states) == 3 for states in grouped.values()))

    def test_full_atlas_has_27_unranked_states(self):
        atlas = generate_closed_shell_state_ensemble_atlas()
        self.assertEqual(len(atlas), 27)
        self.assertTrue(all(state.prior_rank is None for state in atlas))
        self.assertTrue(all(state.prior_probability is None for state in atlas))

    def test_same_state_kinds_for_ne_ar_kr(self):
        expected = {
            "ACTIVATED_LINEAR_3C4E",
            "WEAK_COMPLEX_LINEAR_END_ON",
            "WEAK_COMPLEX_T_SHAPED",
        }
        for centre in (Z["Ne"], Z["Ar"], Z["Kr"]):
            kinds = {x.state_kind for x in closed_shell_xy2_state_ensemble(centre, Z["F"])}
            self.assertEqual(kinds, expected)

    def test_krf2_is_not_special_cased(self):
        kr = closed_shell_xy2_state_ensemble(Z["Kr"], Z["F"])
        ne = closed_shell_xy2_state_ensemble(Z["Ne"], Z["F"])
        self.assertEqual([x.state_kind for x in kr], [x.state_kind for x in ne])
        self.assertEqual([x.geometry_seed for x in kr], [x.geometry_seed for x in ne])

    def test_non_v09_composition_has_no_closed_shell_ensemble(self):
        self.assertEqual(closed_shell_xy2_state_ensemble(Z["K"], Z["F"]), ())

    def test_formula_is_identical_across_competing_states(self):
        for formula, states in group_states_by_formula().items():
            self.assertEqual({state.formula for state in states}, {formula})

    def test_weak_complex_states_do_not_claim_3c4e_topology(self):
        states = closed_shell_xy2_state_ensemble(Z["Ar"], Z["Br"])
        for state in states:
            if state.state_kind.startswith("WEAK_COMPLEX"):
                self.assertNotIn("THREE_CENTRE", state.topology_family)

    def test_all_states_are_explicitly_unranked(self):
        for state in generate_closed_shell_state_ensemble_atlas():
            self.assertEqual(state.status, "UNRANKED_RELATIONAL_STATE_CANDIDATE")


if __name__ == "__main__":
    unittest.main()
