import unittest
from types import SimpleNamespace

from reschem.closed_shell_atomic_control import (
    build_atomic_activation_control,
    generate_atomic_activation_control_atlas,
)


def fake_result(z, charge):
    # Synthetic deterministic energies only test bookkeeping algebra.
    base = -float(z * z)
    energy = base + 0.6 * charge + 0.1 * charge * charge
    n = 2 if z <= 10 else (3 if z <= 18 else 4)
    p_occ = 6 if z in (10, 18, 36) and charge == 0 else 5
    channel = {
        "subshell": f"{n}p",
        "n": n,
        "l": 1,
        "occupancy": p_occ,
        "alpha_occupancy": min(3, p_occ),
        "beta_occupancy": max(0, p_occ - 3),
        "radial_channels": {
            "alpha": {"mean_radius_bohr": 0.1 * z, "radial_sigma_bohr": 0.01 * z},
            "beta": {"mean_radius_bohr": 0.1 * z, "radial_sigma_bohr": 0.01 * z},
        },
    }
    return SimpleNamespace(
        result=SimpleNamespace(energy_hartree=energy, channel_summary=(channel,)),
        quality_pass=True,
    )


class AtomicActivationControlTests(unittest.TestCase):
    def test_control_vector_algebra(self):
        item = build_atomic_activation_control(36, 9, solver=fake_result)
        self.assertAlmostEqual(item.centre_ionization_cost_hartree, 0.7)
        self.assertAlmostEqual(item.ligand_attachment_gain_hartree, 0.5)
        self.assertAlmostEqual(item.charge_transfer_margin_hartree, 0.2)

    def test_outer_p_radius_is_taken_from_neutral_channels(self):
        item = build_atomic_activation_control(36, 17, solver=fake_result)
        self.assertAlmostEqual(item.centre_outer_p_mean_radius_bohr, 3.6)
        self.assertAlmostEqual(item.ligand_outer_p_mean_radius_bohr, 1.7)

    def test_no_model_prediction_field_is_created(self):
        item = build_atomic_activation_control(18, 9, solver=fake_result)
        data = item.to_dict()
        self.assertNotIn("prediction", data)
        self.assertNotIn("score", data)
        self.assertNotIn("threshold", data)

    def test_status_explicitly_says_control_not_molecular_energy(self):
        item = build_atomic_activation_control(10, 9, solver=fake_result)
        self.assertEqual(
            item.status,
            "CONVENTIONAL_ATOMIC_CONTROL_VECTOR_NOT_MOLECULAR_ENERGY",
        )

    def test_all_nine_v09_candidates_receive_vectors(self):
        atlas = generate_atomic_activation_control_atlas(solver=fake_result)
        self.assertEqual(len(atlas), 9)
        self.assertEqual(
            {(x.centre_symbol, x.ligand_symbol) for x in atlas},
            {
                ("Ne", "F"), ("Ne", "Cl"), ("Ne", "Br"),
                ("Ar", "F"), ("Ar", "Cl"), ("Ar", "Br"),
                ("Kr", "F"), ("Kr", "Cl"), ("Kr", "Br"),
            },
        )

    def test_quality_failure_is_preserved_not_rescued(self):
        def failed(z, charge):
            result = fake_result(z, charge)
            if z == 36 and charge == 1:
                result.quality_pass = False
            return result

        item = build_atomic_activation_control(36, 9, solver=failed)
        self.assertFalse(item.all_atomic_quality_pass)


if __name__ == "__main__":
    unittest.main()
