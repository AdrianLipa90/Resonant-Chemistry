import math
import unittest
import numpy as np
from reschem.shell_nbody_topology import (
    NucleusAttractor, shell_capacity, particle_hole_partner, half_filled,
    projected_nuclear_winding, projected_pair_winding, permutation_parity,
    conformal_inverse, shell_topology_summary,
)

class TestShellNBodyTopology(unittest.TestCase):
    def test_shell_duality(self):
        self.assertEqual(shell_capacity(1), 6)
        self.assertEqual(particle_hole_partner(1, 1), 5)
        self.assertEqual(particle_hole_partner(1, 2), 4)
        self.assertTrue(half_filled(1, 3))

    def test_nuclear_winding(self):
        t = np.linspace(0, 2*np.pi, 2001)
        path = np.c_[np.cos(t), np.sin(t), np.zeros_like(t)]
        self.assertAlmostEqual(projected_nuclear_winding(path, NucleusAttractor(6)), 1.0, places=6)

    def test_pair_winding(self):
        t = np.linspace(0, 2*np.pi, 2001)
        a = np.c_[np.cos(t), np.sin(t), np.zeros_like(t)]
        b = np.zeros_like(a)
        self.assertAlmostEqual(projected_pair_winding(a, b), 1.0, places=6)

    def test_exchange_parity(self):
        self.assertEqual(permutation_parity([1,0,2]), -1)
        self.assertEqual(permutation_parity([1,2,0]), 1)

    def test_conformal_inverse(self):
        self.assertEqual(conformal_inverse(1.0), 2.0+0j)
        self.assertTrue(math.isinf(conformal_inverse(0.5).real))

    def test_summary(self):
        s = shell_topology_summary(2,1,3,[1,1,1],[0.5,-0.5],[0,1,2])
        self.assertTrue(s['half_filled_self_dual'])
        self.assertEqual(s['exchange_parity'], 1)

if __name__ == '__main__':
    unittest.main()
