import unittest

from reschem.pncs_semantic_mass_bridge_v015 import (
    ALPHA_M,
    BRIDGE_SCHEMA,
    KAPPA,
    MASS_CONTRACT_ID,
    PNCSSemanticMassBridgeError,
    RUNTIME_SOURCE_SHA256,
    AtomicPNCSSemanticMassBinding,
    binding_from_manifest_entry,
    phase_order_parameter,
    semantic_mass_value,
)


class PNCSSemanticMassBridgeV015Tests(unittest.TestCase):
    def test_constants_match_frozen_pncs_v019_contract(self):
        self.assertAlmostEqual(KAPPA, 0.009193150006360484, places=15)
        self.assertAlmostEqual(ALPHA_M, 0.0072973113787402075, places=15)
        self.assertEqual(MASS_CONTRACT_ID, "PNV_SEMANTIC_MASS_V1")
        self.assertEqual(
            RUNTIME_SOURCE_SHA256,
            "0b4df86cd01db313ea46ebac0eceee9cf6df0673391edd1a3fb2667c30464a32",
        )

    def test_all_zero_phase_has_unit_order_parameter_and_exact_mass(self):
        phase = (0.0,) * 36
        self.assertAlmostEqual(phase_order_parameter(phase), 1.0, places=15)
        self.assertEqual(semantic_mass_value(1, phase), 0.2949745210)
        self.assertEqual(semantic_mass_value(6, phase), 0.2953099474)

    def test_phase_index_and_phase_shape_fail_closed(self):
        with self.assertRaises(PNCSSemanticMassBridgeError):
            semantic_mass_value(0, (0.0,) * 36)
        with self.assertRaises(PNCSSemanticMassBridgeError):
            semantic_mass_value(1, (0.0,) * 35)

    def test_binding_produces_provenance_overlay(self):
        binding = AtomicPNCSSemanticMassBinding(
            atom_card_id="ATOM:C:12:q+0",
            phase_index=6,
            phase36=(0.0,) * 36,
            realization_id="pncs:realization:test",
            realization_binding_id="pncs:realization-binding:test",
            source_binding_id="pncs:mass-binding:test",
        )
        payload = binding.payload
        self.assertEqual(payload["schema"], BRIDGE_SCHEMA)
        self.assertEqual(payload["semantic_mass"], 0.2953099474)
        self.assertEqual(payload["epistemic_operator"], "CHYBA")
        self.assertFalse(payload["canon_allowed"])
        self.assertEqual(len(payload["phase36_sha256"]), 64)
        self.assertEqual(len(payload["bridge_sha256"]), 64)

        overlay = binding.overlay_record
        semantic_mass = overlay["tir"]["semantic_axes"]["values"]["semantic_mass"]
        self.assertEqual(semantic_mass["value"], binding.semantic_mass)
        self.assertEqual(semantic_mass["phase_index"], 6)
        self.assertEqual(semantic_mass["mass_contract_id"], MASS_CONTRACT_ID)
        self.assertIn("pncs-v0.19:pncs:mass-binding:test:", semantic_mass["provenance"])

    def test_manifest_requires_explicit_phase_index_and_exact_t36(self):
        entry = {
            "atom_card_id": "ATOM:C:12:q+0",
            "phase_index": 6,
            "phase36": [0.0] * 36,
            "realization_id": "pncs:realization:test",
            "realization_binding_id": "pncs:realization-binding:test",
            "source_binding_id": "pncs:mass-binding:test",
        }
        binding = binding_from_manifest_entry(entry)
        self.assertEqual(binding.phase_index, 6)
        self.assertEqual(len(binding.phase36), 36)

        bad = dict(entry)
        bad.pop("phase_index")
        with self.assertRaises(PNCSSemanticMassBridgeError):
            binding_from_manifest_entry(bad)


if __name__ == "__main__":
    unittest.main()
