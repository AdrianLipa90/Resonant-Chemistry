import unittest

from reschem.relation_graph import bond_order_multiset, enumerate_relation_graphs

Z = {"H": 1, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9,
     "P": 15, "S": 16, "Cl": 17, "Kr": 36}


def unique_graph(zs):
    graphs = enumerate_relation_graphs(zs)
    if len(graphs) != 1:
        raise AssertionError(f"expected unique quotient graph, got {len(graphs)}")
    return graphs[0]


class RelationGraphTests(unittest.TestCase):
    def test_h2(self):
        self.assertEqual(bond_order_multiset(unique_graph([1, 1])), (1,))

    def test_f2(self):
        self.assertEqual(bond_order_multiset(unique_graph([9, 9])), (1,))

    def test_o2(self):
        self.assertEqual(bond_order_multiset(unique_graph([8, 8])), (2,))

    def test_n2(self):
        self.assertEqual(bond_order_multiset(unique_graph([7, 7])), (3,))

    def test_water(self):
        self.assertEqual(bond_order_multiset(unique_graph([8, 1, 1])), (1, 1))

    def test_ammonia(self):
        self.assertEqual(bond_order_multiset(unique_graph([7, 1, 1, 1])), (1, 1, 1))

    def test_methane(self):
        self.assertEqual(bond_order_multiset(unique_graph([6, 1, 1, 1, 1])), (1, 1, 1, 1))

    def test_co2(self):
        self.assertEqual(bond_order_multiset(unique_graph([6, 8, 8])), (2, 2))

    def test_hcn(self):
        self.assertEqual(bond_order_multiset(unique_graph([1, 6, 7])), (3, 1))

    def test_acetylene(self):
        self.assertEqual(bond_order_multiset(unique_graph([6, 6, 1, 1])), (3, 1, 1))

    def test_ethene(self):
        self.assertEqual(
            bond_order_multiset(unique_graph([6, 6, 1, 1, 1, 1])),
            (2, 1, 1, 1, 1),
        )

    def test_ethane(self):
        self.assertEqual(
            bond_order_multiset(unique_graph([6, 6, 1, 1, 1, 1, 1, 1])),
            (1, 1, 1, 1, 1, 1, 1),
        )

    def test_diborane_requires_later_three_centre_gate(self):
        self.assertEqual(enumerate_relation_graphs([5, 5, 1, 1, 1, 1, 1, 1]), ())

    def test_pcl5_requires_coordination_extension(self):
        self.assertEqual(enumerate_relation_graphs([15, 17, 17, 17, 17, 17]), ())

    def test_sf6_requires_coordination_extension(self):
        self.assertEqual(enumerate_relation_graphs([16, 9, 9, 9, 9, 9, 9]), ())

    def test_krf2_requires_closed_shell_extension(self):
        self.assertEqual(enumerate_relation_graphs([36, 9, 9]), ())


if __name__ == "__main__":
    unittest.main()
