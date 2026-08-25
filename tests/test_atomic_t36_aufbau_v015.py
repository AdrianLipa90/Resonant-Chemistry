import hashlib
import json
import math
import unittest

from reschem.atomic_t36_aufbau_v015 import (
    BASIS_ID,
    CANDIDATE_SCHEMA,
    DERIVATION_ID,
    DIM,
    PNCS_MASS_BINDING_SCHEMA,
    PNCS_MASS_REALIZATION_SCHEMA,
    PNCS_REALIZATION_BINDING_SCHEMA,
    PNCS_REALIZATION_SCHEMA,
    basis_manifest,
    build_atomic_t36_candidate,
    complement_occupancy,
    occupancy_vector36,
    parse_electron_configuration,
    phase36_from_occupancy,
    phase36_sha256,
    spin_orbital_basis36,
)
from reschem.pncs_semantic_mass_bridge_v015 import phase_order_parameter


class AtomicT36AufbauV015Tests(unittest.TestCase):
    def test_basis_is_exactly_36_unique_spin_orbital_slots(self):
        slots = spin_orbital_basis36()
        self.assertEqual(len(slots), DIM)
        self.assertEqual(len({slot.label for slot in slots}), DIM)
        self.assertEqual([slot.index for slot in slots], list(range(DIM)))
        manifest = basis_manifest()
        self.assertEqual(manifest["basis_id"], BASIS_ID)
        self.assertEqual(manifest["dimension"], 36)

    def test_period2_configuration_parsing_and_hund_occupancy(self):
        parsed = parse_electron_configuration("1s^2 2s^2 2p^5")
        self.assertEqual(parsed["1s"], 2)
        self.assertEqual(parsed["2s"], 2)
        self.assertEqual(parsed["2p"], 5)
        occupancy = occupancy_vector36("1s^2 2s^2 2p^5")
        self.assertEqual(sum(occupancy), 9)
        slots = spin_orbital_basis36()
        occupied = {slot.label for slot, bit in zip(slots, occupancy) if bit}
        self.assertIn("2p:m-1:alpha", occupied)
        self.assertIn("2p:m+1:alpha", occupied)
        self.assertIn("2p:m-1:beta", occupied)
        self.assertIn("2p:m+0:beta", occupied)
        self.assertNotIn("2p:m+1:beta", occupied)

    def test_phase_realization_is_exact_t36_and_deterministic(self):
        occupancy = occupancy_vector36("1s^2 2s^2 2p^3")
        left = phase36_from_occupancy(occupancy)
        right = phase36_from_occupancy(occupancy)
        self.assertEqual(left, right)
        self.assertEqual(len(left), 36)
        self.assertTrue(all(math.isfinite(value) and 0.0 <= value < 2.0 * math.pi for value in left))
        self.assertEqual(phase36_sha256(left), phase36_sha256(right))

    def test_empty_and_full_reference_have_zero_order_parameter_with_runtime_tolerance(self):
        empty = phase36_from_occupancy([0] * 36)
        full = phase36_from_occupancy([1] * 36)
        self.assertLess(phase_order_parameter(empty), 1.0e-9)
        self.assertLess(phase_order_parameter(full), 1.0e-9)

    def test_global_occupancy_complement_preserves_order_parameter_with_runtime_tolerance(self):
        occupancy = occupancy_vector36("1s^2 2s^2 2p^3")
        complement = complement_occupancy(occupancy)
        left = phase_order_parameter(phase36_from_occupancy(occupancy))
        right = phase_order_parameter(phase36_from_occupancy(complement))
        self.assertLess(abs(left - right), 1.0e-9)

    def test_candidate_uses_electron_count_as_explicit_occupied_slot_phase_index(self):
        source = b'{"card_id":"ATOM:B:11:q+0"}\n'
        candidate = build_atomic_t36_candidate(
            atom_card_id="ATOM:B:11:q+0",
            electron_configuration="1s^2 2s^2 2p^1",
            electron_count=5,
            source_raw=source,
            source_locator="semantic_cards/B-11_neutral.json",
        )
        self.assertEqual(candidate["schema"], CANDIDATE_SCHEMA)
        self.assertEqual(candidate["phase_index"], 5)
        self.assertEqual(sum(candidate["occupancy36"]), 5)
        self.assertEqual(candidate["electron_count"], 5)
        self.assertEqual(candidate["spectral_input"], "NONE")
        self.assertEqual(candidate["epistemic_operator"], "CHYBA")
        self.assertFalse(candidate["canon_allowed"])

    def test_candidate_emits_pncs_v018_exact_receipt_shapes(self):
        source = b'atom-card-fixture-v015'
        candidate = build_atomic_t36_candidate(
            atom_card_id="ATOM:C:12:q+0",
            electron_configuration="1s^2 2s^2 2p^2",
            electron_count=6,
            source_raw=source,
            source_locator="semantic_cards/C-12_neutral.json",
        )
        v18 = candidate["pncs_v018"]
        self.assertEqual(v18["realization"]["schema"], PNCS_REALIZATION_SCHEMA)
        self.assertEqual(v18["binding"]["schema"], PNCS_REALIZATION_BINDING_SCHEMA)
        self.assertEqual(v18["realization"]["basis_id"], BASIS_ID)
        self.assertEqual(v18["realization"]["derivation_id"], DERIVATION_ID)
        self.assertTrue(v18["realization_id"].startswith("pncs:realization36:sha256:"))
        self.assertTrue(v18["binding_id"].startswith("pncs:binding36:sha256:"))
        self.assertEqual(v18["binding"]["phase36_sha256"], candidate["phase36_sha256"])

    def test_candidate_emits_pncs_v019_mass_receipt_and_reschem_bridge_parity(self):
        candidate = build_atomic_t36_candidate(
            atom_card_id="ATOM:N:14:q+0",
            electron_configuration="1s^2 2s^2 2p^3",
            electron_count=7,
            source_raw=b'atom-card-fixture-n14',
            source_locator="semantic_cards/N-14_neutral.json",
        )
        v19 = candidate["pncs_v019"]
        self.assertEqual(v19["mass_realization"]["schema"], PNCS_MASS_REALIZATION_SCHEMA)
        self.assertEqual(v19["binding"]["schema"], PNCS_MASS_BINDING_SCHEMA)
        self.assertTrue(v19["mass_realization_id"].startswith("pncs:mass:sha256:"))
        self.assertTrue(v19["mass_binding_id"].startswith("pncs:mass-binding:sha256:"))
        self.assertEqual(v19["binding"]["semantic_mass"], candidate["semantic_mass"])
        self.assertEqual(candidate["reschem_bridge"]["semantic_mass"], candidate["semantic_mass"])
        self.assertEqual(candidate["reschem_bridge"]["source_binding_id"], v19["mass_binding_id"])

    def test_source_content_id_is_raw_atom_card_sha256(self):
        raw = b'raw-atom-card-source\n'
        candidate = build_atomic_t36_candidate(
            atom_card_id="ATOM:O:16:q+0",
            electron_configuration="1s^2 2s^2 2p^4",
            electron_count=8,
            source_raw=raw,
            source_locator="semantic_cards/O-16_neutral.json",
        )
        digest = hashlib.sha256(raw).hexdigest()
        self.assertEqual(candidate["source_digest_sha256"], digest)
        self.assertEqual(candidate["content_id"], f"pncs:file:sha256:{digest}")

    def test_candidate_hash_is_compact_json_sha256_and_contains_no_observed_spectrum(self):
        candidate = build_atomic_t36_candidate(
            atom_card_id="ATOM:Ne:20:q+0",
            electron_configuration="1s^2 2s^2 2p^6",
            electron_count=10,
            source_raw=b'atom-card-fixture-ne20',
            source_locator="semantic_cards/Ne-20_neutral.json",
        )
        recorded = candidate["candidate_sha256"]
        body = dict(candidate)
        body.pop("candidate_sha256")
        expected = hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
        ).hexdigest()
        self.assertEqual(recorded, expected)
        text = json.dumps(candidate).lower()
        for forbidden in ("observed_wavelength", "observed_wavenumber", "oscillator_strength", "line_intensity"):
            self.assertNotIn(forbidden, text)


if __name__ == "__main__":
    unittest.main()
