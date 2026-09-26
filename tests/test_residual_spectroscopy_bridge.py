import copy

from reschem.residual_spectroscopy_bridge import (
    attach_residual_diagnostics,
    validate_residual_packet,
)

def packet(cls="UNRESOLVED_STRUCTURED_CANDIDATE"):
    return {
        "schema":"GREMLIN_RESIDUAL_PRESERVING_SPECTROSCOPY_V0_2",
        "classification":cls,
        "analysis_sha256":"a"*64,
        "commitments":{"raw_sha256":"b"*64,"model_sha256":"c"*64,"residual_sha256":"d"*64},
        "metrics":{"consensus_peak_bin":17},
        "policy":{
            "raw_preserved":True,
            "residual_preserved":True,
            "analysis_copy_allowed":True,
            "destructive_denoising":False,
            "interpretation_last":True,
            "new_physics_from_residual_only":False,
            "time_fluctuation_claim_allowed":False,
        },
        "promotion_gates":["instrument control"],
    }

def test_bridge_preserves_spectrum_exactly():
    spectrum={"schema":"RESCHEM_TEST_SPECTRUM","levels":[0.0,1.2,2.4]}
    original=copy.deepcopy(spectrum)
    out=attach_residual_diagnostics(spectrum,packet())
    assert spectrum==original
    assert out["spectrum"]==original
    assert out["claims"]["spectrum_modified_by_residual_layer"] is False

def test_unresolved_structure_is_not_chemical_assignment():
    out=attach_residual_diagnostics({"levels":[1,2]},packet())
    assert out["residual_diagnostics"]["classification"]=="UNRESOLVED_STRUCTURED_CANDIDATE"
    assert out["claims"]["residual_is_chemical_assignment"] is False
    assert out["claims"]["new_physics_established"] is False

def test_unsafe_policy_fails_closed():
    value=packet()
    value["policy"]["destructive_denoising"]=True
    try:
        validate_residual_packet(value)
    except ValueError:
        pass
    else:
        raise AssertionError("unsafe packet accepted")
