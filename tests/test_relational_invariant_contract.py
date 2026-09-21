import unittest

import numpy as np

from reschem.oes_transition_export import export_oes_transition_state
from reschem.relational_holonomy_spectroscopy import (
    gauge_equivalent_hamiltonian,
    gauge_transform_phases,
    phase_dressed_hamiltonian,
    spectral_eigenvalues,
    wilson_loop,
)
from reschem.relational_invariants import (
    INVARIANT_CONTRACT_ID,
    OES_ORBITAL_UNITARY_BASIS_PROFILE_ID,
    align_s_metric_subspace,
    s_metric_projector_residual,
)


class RelationalInvariantContractTests(unittest.TestCase):
    @staticmethod
    def _s_orthonormal_frame():
        s = np.diag([1.0, 2.0, 4.0, 7.0])
        raw = np.asarray(
            [
                [1.0, 0.2],
                [0.3, 1.0],
                [0.7, -0.4],
                [0.1, 0.6],
            ],
            dtype=float,
        )
        gram = raw.T @ s @ raw
        values, vectors = np.linalg.eigh(gram)
        c = raw @ vectors @ np.diag(1.0 / np.sqrt(values)) @ vectors.T
        return c, s

    def test_s_metric_projector_ignores_occupied_basis_rotation(self):
        current, s = self._s_orthonormal_frame()
        angle = 0.63
        rotation = np.asarray(
            [
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle), np.cos(angle)],
            ]
        )
        rotated = current @ rotation
        self.assertLess(s_metric_projector_residual(current, rotated, s), 1.0e-12)

    def test_s_metric_procrustes_is_gauge_fix_not_subspace_change(self):
        current, s = self._s_orthonormal_frame()
        angle = -0.91
        representation_rotation = np.asarray(
            [
                [np.cos(angle), -np.sin(angle)],
                [np.sin(angle), np.cos(angle)],
            ]
        )
        candidate = current @ representation_rotation

        before = np.linalg.norm(current - candidate)
        aligned, rotation = align_s_metric_subspace(current, candidate, s)
        after = np.linalg.norm(current - aligned)

        self.assertLess(after, before)
        self.assertLess(after, 1.0e-12)
        np.testing.assert_allclose(
            rotation.conjugate().T @ rotation, np.eye(2), atol=1.0e-12
        )
        self.assertLess(s_metric_projector_residual(candidate, aligned, s), 1.0e-12)

    def test_graph_vertex_rephasing_preserves_wilson_loop_and_spectrum(self):
        edges = ((0, 1), (1, 2), (2, 0))
        phases = np.asarray([0.2, -0.6, 0.9])
        chi = np.asarray([0.4, -0.3, 0.8])
        hoppings = (1.0, 0.7, 1.2)
        energies = (0.1, -0.2, 0.4)
        cycle = ((0, +1), (1, +1), (2, +1))

        transformed = gauge_transform_phases(phases, edges, chi)
        self.assertLess(abs(wilson_loop(phases, cycle) - wilson_loop(transformed, cycle)), 1.0e-12)

        h0 = phase_dressed_hamiltonian(energies, edges, hoppings, phases)
        h1 = phase_dressed_hamiltonian(energies, edges, hoppings, transformed)
        np.testing.assert_allclose(
            h1, gauge_equivalent_hamiltonian(h0, chi), atol=1.0e-12
        )
        np.testing.assert_allclose(
            spectral_eigenvalues(h0), spectral_eigenvalues(h1), atol=1.0e-12
        )

    def test_rc_to_oes_packet_declares_shared_contract(self):
        payload = export_oes_transition_state(
            species_label="H2",
            nuclei=(
                {
                    "label": "H1",
                    "atomic_number": 1,
                    "mass_u": 1.007825,
                    "position_bohr": (-0.7, 0.0, 0.0),
                },
                {
                    "label": "H2",
                    "atomic_number": 1,
                    "mass_u": 1.007825,
                    "position_bohr": (0.7, 0.0, 0.0),
                },
            ),
            initial_label="X",
            initial_energy_hartree=-1.2,
            final_label="A",
            final_energy_hartree=-0.8,
            transition_rdm=np.asarray([[0.0, 0.2j], [-0.2j, 0.0]]),
            source_commit="fixture",
            method="unit-test",
            orbital_basis_id="fixture-mo-v1",
            backend_status="SIMULATED_REFERENCE",
        )
        contract = payload["representation_contract"]
        self.assertEqual(contract["schema"], INVARIANT_CONTRACT_ID)
        self.assertEqual(contract["profile"], OES_ORBITAL_REPHASING_PROFILE_ID)


if __name__ == "__main__":
    unittest.main()
