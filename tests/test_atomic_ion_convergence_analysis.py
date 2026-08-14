import unittest

from reschem.atomic_ion_convergence_analysis import (
    matched_difference_trajectory,
    summarize_complete_scan,
)


def state(symbol, charge, base):
    return {
        "symbol": symbol,
        "charge": charge,
        "levels": [
            {"level":"L0","energy_hartree":base,"converged":True,"virial_abs_hartree":0.3},
            {"level":"L1","energy_hartree":base-0.1,"converged":True,"virial_abs_hartree":0.2},
            {"level":"L2","energy_hartree":base-0.15,"converged":True,"virial_abs_hartree":0.1},
        ],
    }


class AtomicIonConvergenceAnalysisTests(unittest.TestCase):
    def test_matched_difference_uses_same_level(self):
        neutral = state("Ne", 0, -10.0)
        cation = state("Ne", 1, -9.0)
        out = matched_difference_trajectory(neutral, cation, definition="E(cation)-E(neutral)")
        self.assertEqual([row["value_hartree"] for row in out["levels"]], [1.0, 1.0, 1.0])
        self.assertEqual([row["absolute_difference_drift_hartree"] for row in out["adjacent_difference_drift"]], [0.0, 0.0])

    def test_attachment_sign_convention_matches_v011(self):
        anion = state("F", -1, -10.5)
        neutral = state("F", 0, -10.0)
        out = matched_difference_trajectory(anion, neutral, definition="E(neutral)-E(anion)")
        self.assertAlmostEqual(out["levels"][0]["value_hartree"], 0.5)

    def test_complete_summary_has_three_centres_three_ligands(self):
        states = [
            state("Ne",0,-10), state("Ne",1,-9),
            state("Ar",0,-20), state("Ar",1,-19),
            state("Kr",0,-30), state("Kr",1,-29),
            state("F",0,-5), state("F",-1,-5.5),
            state("Cl",0,-6), state("Cl",-1,-6.4),
            state("Br",0,-7), state("Br",-1,-7.3),
        ]
        out = summarize_complete_scan(states)
        self.assertEqual(set(out["ionization_cost_trajectories"]), {"Ne","Ar","Kr"})
        self.assertEqual(set(out["attachment_gain_trajectories"]), {"F","Cl","Br"})
        self.assertIn("NO_CONVERGENCE_THRESHOLD", out["status"])

    def test_incomplete_scan_fails_closed(self):
        with self.assertRaises(ValueError):
            summarize_complete_scan([state("Ne",0,-10)])


if __name__ == "__main__":
    unittest.main()
