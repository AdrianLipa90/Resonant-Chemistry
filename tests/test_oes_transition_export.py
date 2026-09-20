import numpy as np
import pytest

from reschem.oes_transition_export import export_oes_transition_state


def _payload():
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


def test_export_is_oes_v01_json_ready_and_keeps_complex_rdm():
    payload = _payload()
    assert payload["schema"] == "OES_TRANSITION_STATE_V0_1"
    assert payload["spectral_inference"] == "NOT_PERFORMED_BY_RESONANT_CHEMISTRY"
    assert payload["transition_rdm"]["real"][0][1] == pytest.approx(0.25)
    assert payload["transition_rdm"]["imag"][0][1] == pytest.approx(0.1)
    assert "frequency_hz" not in payload
    assert "oscillator_strength" not in payload


def test_export_fails_closed_on_missing_nuclear_framework():
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
    with pytest.raises(ValueError, match="at least one nuclear center"):
        export_oes_transition_state(**kwargs)
