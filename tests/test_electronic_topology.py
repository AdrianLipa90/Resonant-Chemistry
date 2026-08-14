import unittest

from reschem.electronic_topology import (
    TopologyEvidence,
    audit_electronic_topology,
    score_topology_predictions,
)


def ev(family, verdict):
    return TopologyEvidence(
        family=family,
        verdict=verdict,
        method_signature="SYNTHETIC_TEST_METHOD",
        provenance="tests/test_electronic_topology.py",
        raw_summary=f"synthetic {family} -> {verdict}",
    )


class ElectronicTopologyTests(unittest.TestCase):
    def test_two_independent_supports_admit_3c4e(self):
        audit = audit_electronic_topology(
            "XF2",
            [
                ev("ORBITAL_SUBSPACE", "SUPPORT_3C4E"),
                ev("FRAGMENTATION_ISOMER_ENERGY", "SUPPORT_3C4E"),
            ],
            local_minimum=True,
        )
        self.assertEqual(audit.status, "CONSISTENT_3C4E_MULTI_DIAGNOSTIC")

    def test_two_independent_supports_admit_vdw(self):
        audit = audit_electronic_topology(
            "XCl2",
            [
                ev("REAL_SPACE_FORCE", "SUPPORT_VDW"),
                ev("FRAGMENTATION_ISOMER_ENERGY", "SUPPORT_VDW"),
            ],
            local_minimum=True,
        )
        self.assertEqual(audit.status, "CONSISTENT_VDW_MULTI_DIAGNOSTIC")

    def test_single_qtaim_like_family_is_not_enough(self):
        audit = audit_electronic_topology(
            "XF2",
            [ev("REAL_SPACE_FORCE", "SUPPORT_3C4E")],
            local_minimum=True,
        )
        self.assertEqual(audit.status, "UNKNOWN_INSUFFICIENT_INDEPENDENT_EVIDENCE")

    def test_single_orbital_family_is_not_enough(self):
        audit = audit_electronic_topology(
            "XF2",
            [ev("ORBITAL_SUBSPACE", "SUPPORT_3C4E")],
            local_minimum=True,
        )
        self.assertEqual(audit.status, "UNKNOWN_INSUFFICIENT_INDEPENDENT_EVIDENCE")

    def test_conflict_is_not_forced(self):
        audit = audit_electronic_topology(
            "XY2",
            [
                ev("ORBITAL_SUBSPACE", "SUPPORT_3C4E"),
                ev("FRAGMENTATION_ISOMER_ENERGY", "SUPPORT_VDW"),
            ],
            local_minimum=True,
        )
        self.assertEqual(audit.status, "MIXED_CONFLICTING_EVIDENCE")

    def test_no_local_minimum_rejects_stable_topology_label(self):
        audit = audit_electronic_topology(
            "XY2",
            [
                ev("ORBITAL_SUBSPACE", "SUPPORT_3C4E"),
                ev("REAL_SPACE_FORCE", "SUPPORT_3C4E"),
            ],
            local_minimum=False,
        )
        self.assertEqual(audit.status, "REJECTED_NOT_LOCAL_MINIMUM")

    def test_unknown_local_minimum_blocks_positive_admission(self):
        audit = audit_electronic_topology(
            "XY2",
            [
                ev("ORBITAL_SUBSPACE", "SUPPORT_3C4E"),
                ev("REAL_SPACE_FORCE", "SUPPORT_3C4E"),
            ],
            local_minimum=None,
        )
        self.assertEqual(audit.status, "UNKNOWN_LOCAL_MINIMUM_NOT_ESTABLISHED")

    def test_duplicate_family_is_rejected(self):
        with self.assertRaises(ValueError):
            audit_electronic_topology(
                "XY2",
                [
                    ev("ORBITAL_SUBSPACE", "SUPPORT_3C4E"),
                    ev("ORBITAL_SUBSPACE", "SUPPORT_3C4E"),
                ],
                local_minimum=True,
            )

    def test_empty_provenance_is_rejected(self):
        with self.assertRaises(ValueError):
            TopologyEvidence(
                family="ORBITAL_SUBSPACE",
                verdict="SUPPORT_3C4E",
                method_signature="M",
                provenance="",
                raw_summary="raw",
            )

    def test_inconclusive_does_not_vote(self):
        audit = audit_electronic_topology(
            "XY2",
            [
                ev("ORBITAL_SUBSPACE", "SUPPORT_3C4E"),
                ev("REAL_SPACE_FORCE", "INCONCLUSIVE"),
                ev("FRAGMENTATION_ISOMER_ENERGY", "NOT_RUN"),
            ],
            local_minimum=True,
        )
        self.assertEqual(audit.informative_families, 1)
        self.assertEqual(audit.status, "UNKNOWN_INSUFFICIENT_INDEPENDENT_EVIDENCE")

    def test_score_excludes_preknown_and_unknown(self):
        a = audit_electronic_topology(
            "A",
            [
                ev("ORBITAL_SUBSPACE", "SUPPORT_3C4E"),
                ev("REAL_SPACE_FORCE", "SUPPORT_3C4E"),
            ],
            local_minimum=True,
        )
        b = audit_electronic_topology(
            "B",
            [ev("ORBITAL_SUBSPACE", "SUPPORT_3C4E")],
            local_minimum=True,
        )
        c = audit_electronic_topology(
            "C",
            [
                ev("REAL_SPACE_FORCE", "SUPPORT_VDW"),
                ev("FRAGMENTATION_ISOMER_ENERGY", "SUPPORT_VDW"),
            ],
            local_minimum=True,
        )
        score = score_topology_predictions(
            {"A": "3C4E", "B": "3C4E", "C": "VDW"},
            [a, b, c],
            excluded={"A"},
        )
        self.assertEqual(score["resolved_count"], 1)
        self.assertEqual(score["correct_count"], 1)
        self.assertEqual(score["unresolved"][0]["formula"], "B")


if __name__ == "__main__":
    unittest.main()
