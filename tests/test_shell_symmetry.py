import unittest

from reschem.shell_symmetry import (
    are_particle_hole_partners,
    particle_hole_orbit,
    principal_shell_transfer_invariant,
    shell_capacity,
    shell_signature,
    symmetry_family,
)


class TestShellSymmetry(unittest.TestCase):
    def test_capacities(self):
        self.assertEqual(shell_capacity(0), 2)
        self.assertEqual(shell_capacity(1), 6)
        self.assertEqual(shell_capacity(2), 10)
        self.assertEqual(shell_capacity(3), 14)

    def test_p_shell_involution(self):
        self.assertTrue(are_particle_hole_partners(1, 1, 5))
        self.assertTrue(are_particle_hole_partners(1, 2, 4))
        self.assertEqual(particle_hole_orbit(1, 3), (3,))

    def test_self_dual_centres(self):
        self.assertTrue(shell_signature(2, 1, 3).self_dual)
        self.assertTrue(shell_signature(3, 2, 5).self_dual)
        self.assertTrue(shell_signature(4, 3, 7).self_dual)

    def test_mirror_offsets(self):
        a = shell_signature(2, 1, 1)
        b = shell_signature(2, 1, 5)
        self.assertAlmostEqual(a.signed_offset_from_half, -b.signed_offset_from_half)
        self.assertAlmostEqual(a.absolute_offset_from_half, b.absolute_offset_from_half)

    def test_principal_shell_transfer(self):
        self.assertTrue(principal_shell_transfer_invariant(shell_signature(2, 1, 2), shell_signature(3, 1, 2)))
        self.assertFalse(principal_shell_transfer_invariant(shell_signature(2, 1, 2), shell_signature(3, 1, 4)))

    def test_family_partition(self):
        self.assertEqual(symmetry_family(1), ((0, 6), (1, 5), (2, 4), (3,)))
        self.assertEqual(len(symmetry_family(2)), 6)
        self.assertEqual(symmetry_family(2)[-1], (5,))


if __name__ == "__main__":
    unittest.main()
