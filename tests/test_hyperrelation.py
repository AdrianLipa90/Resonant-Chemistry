import unittest

from reschem.hyperrelation import (
    enumerate_minimal_augmented_graphs,
    relation_load_half_units,
)


Z = {
    "H": 1,
    "B": 5,
    "C": 6,
    "O": 8,
    "F": 9,
    "Al": 13,
    "P": 15,
    "S": 16,
    "Cl": 17,
    "Ga": 31,
    "Br": 35,
    "Kr": 36,
}


def unique_graph(zs):
    graphs = enumerate_minimal_augmented_graphs(zs)
    if len(graphs) != 1:
        raise AssertionError(f"expected one quotient graph, got {len(graphs)}")
    return graphs[0]


class HyperrelationTests(unittest.TestCase):
    def test_two_centre_control_wins_without_augmentation(self):
        methane = unique_graph([Z["C"], Z["H"], Z["H"], Z["H"], Z["H"]])
        self.assertEqual(methane.augmentation_order, 0)
        self.assertEqual(len(methane.three_centre_bridges), 0)
        self.assertEqual(sorted(b.order for b in methane.pair_bonds), [1, 1, 1, 1])

        water = unique_graph([Z["O"], Z["H"], Z["H"]])
        self.assertEqual(water.augmentation_order, 0)
        self.assertEqual(len(water.three_centre_bridges), 0)

    def test_diborane_requires_exactly_two_minimal_bridges(self):
        graph = unique_graph([Z["B"], Z["B"]] + [Z["H"]] * 6)
        self.assertEqual(graph.augmentation_order, 2)
        self.assertEqual(len(graph.three_centre_bridges), 2)
        self.assertEqual(sorted(b.order for b in graph.pair_bonds), [1, 1, 1, 1])
        self.assertEqual(
            relation_load_half_units(graph),
            tuple(2 * degree for degree in graph.target_relation_degrees),
        )

    def test_diborane_bridge_centres_are_distinct_degree_one_centres(self):
        graph = unique_graph([Z["B"], Z["B"]] + [Z["H"]] * 6)
        bridge_indices = [edge.bridge for edge in graph.three_centre_bridges]
        self.assertEqual(len(set(bridge_indices)), 2)
        for edge in graph.three_centre_bridges:
            self.assertEqual(graph.atomic_numbers[edge.bridge], Z["H"])
            self.assertEqual(graph.atomic_numbers[edge.outer_a], Z["B"])
            self.assertEqual(graph.atomic_numbers[edge.outer_b], Z["B"])

    def test_aluminum_chloride_dimer_transfers_same_topology(self):
        graph = unique_graph([Z["Al"], Z["Al"]] + [Z["Cl"]] * 6)
        self.assertEqual(graph.augmentation_order, 2)
        self.assertEqual(len(graph.three_centre_bridges), 2)
        self.assertEqual(sorted(b.order for b in graph.pair_bonds), [1, 1, 1, 1])
        for edge in graph.three_centre_bridges:
            self.assertEqual(graph.atomic_numbers[edge.bridge], Z["Cl"])

    def test_aluminum_bromide_dimer_transfers_same_topology(self):
        graph = unique_graph([Z["Al"], Z["Al"]] + [Z["Br"]] * 6)
        self.assertEqual(graph.augmentation_order, 2)
        self.assertEqual(len(graph.three_centre_bridges), 2)

    def test_gallium_chloride_dimer_transfers_same_topology(self):
        graph = unique_graph([Z["Ga"], Z["Ga"]] + [Z["Cl"]] * 6)
        self.assertEqual(graph.augmentation_order, 2)
        self.assertEqual(len(graph.three_centre_bridges), 2)

    def test_coordination_extensions_remain_unresolved(self):
        self.assertEqual(
            enumerate_minimal_augmented_graphs([Z["P"]] + [Z["Cl"]] * 5),
            (),
        )
        self.assertEqual(
            enumerate_minimal_augmented_graphs([Z["S"]] + [Z["F"]] * 6),
            (),
        )

    def test_closed_shell_excitation_remains_unresolved(self):
        self.assertEqual(
            enumerate_minimal_augmented_graphs([Z["Kr"], Z["F"], Z["F"]]),
            (),
        )


if __name__ == "__main__":
    unittest.main()
