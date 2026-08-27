import math

from reschem.chemphotoelectromagnetic_bridge_v016 import (
    build_transition_lines,
    electric_dipole_strength,
    fingerprint_signature,
    half_interface_defect,
    lorentzian,
    relational_zero,
    spectrum,
    temporal_coherence,
    transition_angular_frequency,
)


def test_half_interface_exact_relational_zero():
    assert abs(half_interface_defect(0.5, 2.0 * math.pi)) < 1e-15
    assert relational_zero(0.5, 2.0 * math.pi)
    assert not relational_zero(0.45, 2.0 * math.pi, atol=1e-6)


def test_spinorial_2pi_is_half_of_4pi():
    assert math.isclose((2.0 * math.pi) / (4.0 * math.pi), 0.5)


def test_line_center_is_energy_gap_over_hbar():
    assert math.isclose(transition_angular_frequency(2.0, 5.5, hbar=0.5), 7.0)


def test_dipole_forbidden_channel_has_zero_strength():
    assert electric_dipole_strength(0.8, 0.0) == 0.0


def test_lorentzian_peaks_at_transition_center():
    center = 3.2
    gamma = 0.4
    assert lorentzian(center, center, gamma) > lorentzian(center + gamma, center, gamma)


def test_temporal_coherence_has_expected_phase_and_decay():
    c0 = temporal_coherence(0.0, 3.0, 0.2)
    c1 = temporal_coherence(1.0, 3.0, 0.2)
    assert abs(c0) == 1.0
    assert abs(c1) < abs(c0)


def test_distinct_chemical_state_graphs_give_distinct_line_fingerprints():
    couplings = {(0, 1): 1.0, (0, 2): 0.4}
    populations = (1.0, 0.0, 0.0)
    a = build_transition_lines((0.0, 1.0, 2.0), couplings, populations, linewidth=0.05)
    b = build_transition_lines((0.0, 1.15, 2.4), couplings, populations, linewidth=0.05)
    assert fingerprint_signature(a) != fingerprint_signature(b)


def test_spectrum_is_sum_of_positive_admitted_lines():
    lines = build_transition_lines(
        (0.0, 1.0, 2.0),
        {(0, 1): 1.0, (0, 2): 0.25},
        (1.0, 0.0, 0.0),
        linewidth=0.1,
    )
    vals = spectrum((0.5, 1.0, 1.5, 2.0), lines)
    assert all(v >= 0.0 for v in vals)
    assert vals[1] > vals[0]
    assert vals[3] > vals[2]
