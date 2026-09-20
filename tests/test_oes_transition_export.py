import unittest

import numpy as np

from reschem.oes_transition_export import export_oes_transition_state


class OESTransitionExportTests(unittest.TestCase):
    def _payload(self):
        return export_oes_transition_state(
            species_label="He",
            nuclei=[
                {
                    "label": "He",
                    "atomic_number": 2,
                    "mass_u": 4.002603,
                    "position_bohr": (0.0, 0.0, 0.0),
                }
            ],
            initial_label="1S0",
            initial_energy_hartree=-2.9,
            final_label="1P1",
            final_energy_hartree=-2.1,
            transition_rdm=np.asarray([[0.0, 0.25 + 0.1j], [0.0, 0.0]], dtype=complex),
            source_commit="fixture",
            method="fixture-ci",
            orbital_basis_id="fixture-orbitals",
            backend_status="SIMULATED_REFERENCE",
            initial_multiplicity=1,
            final_multiplicity=1,
        )

    def test_export_is_oes_v01_json_ready_and_keeps_complex_rdm(self):
        payload = self._payload()
        self.assertEqual(payload["schema"], "OES_TRANSITION_STATE_V0_1")
        self.assertEqual(
            payload["spectral_inference"],
            "NOT_PERFORMED_BY_RESONANT_CHEMISTRY",
        )
        self.assertAlmostEqual(payload["transition_rdm"]["real"][0][1], 0.25, places=15)
        self.assertAlmostEqual(payload["transition_rdm"]["imag"][0][1], 0.1, places=15)
        self.assertNotIn("frequency_hz", payload)
        self.assertNotIn("oscillator_strength", payload)

    def test_export_fails_closed_on_missing_nuclear_framework(self):
        kwargs = {
            "species_label": "He",
            "nuclei": [],
            "initial_label": "i",
            "initial_energy_hartree": -1.0,
            "final_label": "f",
            "final_energy_hartree": -0.5,
            "transition_rdm": np.eye(1),
            "source_commit": "fixture",
            "method": "fixture",
            "orbital_basis_id": "basis",
            "backend_status": "SIMULATED_REFERENCE",
        }
        with self.assertRaisesRegex(ValueError, "at least one nuclear center"):
            export_oes_transition_state(**kwargs)


if __name__ == "__main__":
    unittest.main()
