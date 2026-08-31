import json
from pathlib import Path

from reschem.nuclear.deuteron_control import (
    DEFAULT_INTERACTION_PATH,
    DEFAULT_NUCLEON_PACKET_PATH,
    MalflietTjonTriplet,
    solve_deuteron_mt_triplet,
)


def test_provenance_packets_have_expected_identity():
    interaction = json.loads(Path(DEFAULT_INTERACTION_PATH).read_text(encoding="utf-8"))
    nucleons = json.loads(Path(DEFAULT_NUCLEON_PACKET_PATH).read_text(encoding="utf-8"))
    assert interaction["interaction_id"] == "MALFLIET_TJON_TRIPLET_CONTROL_V0_1"
    assert interaction["evidential_class"] == "CONTROL_MODEL_REPRODUCTION"
    assert nucleons["status"] == "SOURCE_BOUND_EXTERNAL_EMPIRICAL"
    assert nucleons["provenance_class"] == "EXTERNAL_EMPIRICAL"


def test_mt_triplet_control_reproduces_bound_state():
    result = solve_deuteron_mt_triplet(n_points=8000, r_max_fm=30.0)
    assert result.bound_state_count_in_sample == 1
    assert result.second_level_energy_mev > 0.0
    assert abs(result.binding_residual_mev) < 5.0e-4
    assert abs(result.single_nucleon_rms_residual_fm) < 1.0e-2


def test_mt_triplet_grid_converges():
    coarse = solve_deuteron_mt_triplet(n_points=4000, r_max_fm=30.0)
    fine = solve_deuteron_mt_triplet(n_points=8000, r_max_fm=30.0)
    assert abs(fine.binding_energy_mev - coarse.binding_energy_mev) < 2.0e-4


def test_physical_pn_kinematics_is_close_to_mt_benchmark_convention():
    result = solve_deuteron_mt_triplet(n_points=2000, r_max_fm=30.0)
    assert 469.0 < result.physical_pn_reduced_mass_mev < 470.0
    assert abs(result.physical_hbar2_over_2mu_mev_fm2 - 41.47) < 2.0e-3


def test_provider_is_parameter_fixed():
    provider = MalflietTjonTriplet.from_json()
    assert provider.V_A_mev_fm == -626.885
    assert provider.mu_A_inv_fm == 1.55
    assert provider.V_R_mev_fm == 1438.72
    assert provider.mu_R_inv_fm == 3.11
    assert provider.hbar2_over_m_mev_fm2 == 41.47
