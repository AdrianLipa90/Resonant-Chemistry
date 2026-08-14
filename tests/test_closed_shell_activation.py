import unittest

from reschem.closed_shell_activation import (
    activation_pair_loss_channel,
    candidate_formulae,
    closed_shell_activation_candidate,
    generate_closed_shell_activation_atlas,
)


Z = {
    "H": 1,
    "He": 2,
    "F": 9,
    "Ne": 10,
    "Cl": 17,
    "Ar": 18,
    "K": 19,
    "Br": 35,
    "Kr": 36,
}


class ClosedShellActivationTests(unittest.TestCase):
    def test_full_atlas_has_nine_candidates(self):
        atlas = generate_closed_shell_activation_atlas()
        self.assertEqual(len(atlas), 9)

    def test_centres_selected_by_shell_rule(self):
        centres = {candidate.centre_symbol for candidate in generate_closed_shell_activation_atlas()}
        self.assertEqual(centres, {"Ne", "Ar", "Kr"})

    def test_ligands_selected_by_shell_rule(self):
        ligands = {candidate.ligand_symbol for candidate in generate_closed_shell_activation_atlas()}
        self.assertEqual(ligands, {"F", "Cl", "Br"})

    def test_krf2_is_generated_generically(self):
        candidate = closed_shell_activation_candidate(Z["Kr"], Z["F"])
        self.assertIsNotNone(candidate)
        self.assertEqual(candidate.empirical_formula, "KrF2")
        self.assertEqual(candidate.base_relation_degree, 0)
        self.assertEqual(candidate.activated_relation_degree, 2)
        self.assertEqual(candidate.q_cs, 1)
        self.assertIn("THREE_CENTRE_FOUR_ELECTRON", candidate.topology)

    def test_nef2_and_arf2_are_not_deleted_posthoc(self):
        formulae = set(candidate_formulae())
        self.assertIn("NeF2", formulae)
        self.assertIn("ArF2", formulae)
        self.assertIn("KrF2", formulae)

    def test_first_shell_closed_shell_does_not_activate(self):
        self.assertIsNone(closed_shell_activation_candidate(Z["He"], Z["F"]))

    def test_half_filled_hydrogen_is_not_halogen_like_ligand(self):
        self.assertIsNone(closed_shell_activation_candidate(Z["Kr"], Z["H"]))

    def test_below_half_degree_one_ligand_is_blocked(self):
        self.assertIsNone(closed_shell_activation_candidate(Z["Kr"], Z["K"]))

    def test_nonclosed_centre_is_blocked(self):
        self.assertIsNone(closed_shell_activation_candidate(Z["K"], Z["F"]))

    def test_pair_loss_channel_is_generic(self):
        candidate = closed_shell_activation_candidate(Z["Kr"], Z["F"])
        channel = activation_pair_loss_channel(candidate)
        self.assertEqual(channel.parent, "KrF2")
        self.assertEqual(channel.lower, "Kr")
        self.assertEqual(channel.ligand_dimer, "F2")

    def test_all_candidates_are_structural_not_energetic_claims(self):
        for candidate in generate_closed_shell_activation_atlas():
            self.assertEqual(candidate.status, "MODEL_DEFINED_CLOSED_SHELL_3C4E_CANDIDATE")


if __name__ == "__main__":
    unittest.main()
