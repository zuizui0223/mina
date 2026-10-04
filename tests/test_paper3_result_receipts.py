import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INTER=ROOT/"results"/"PAPER3_ZENODO_INTERANNUAL_ALIASING_RECEIPT_V2.json"
SAR=ROOT/"results"/"PAPER3_SAR_2024_WITHIN_SEASON_VALIDATION_RECEIPT_V1.json"

def test_interannual_radius_curve_is_complete_and_monotone():
    x=json.loads(INTER.read_text(encoding="utf-8"))
    curve=x["interannual_result"]["aliasing_curve"]
    assert set(curve)=={"0.5","1","2","5","10"}
    radii=["0.5","1","2","5","10"]
    counts=[curve[r]["false_turnover_n"] for r in radii]
    assert counts==sorted(counts,reverse=True)
    assert counts==[26,24,16,8,4]
    assert all(curve[r]["transition_n"]==27 for r in radii)

def test_interannual_support_and_quantiles():
    x=json.loads(INTER.read_text(encoding="utf-8"))
    r=x["interannual_result"]
    assert r["annual_anchors"]==30
    assert r["consecutive_transitions"]==27
    assert abs(r["identity_preserving_radii_km"]["q95"]-14.517938991470851)<1e-12
    assert abs(r["maximum_transition"]["displacement_km"]-63.2080783515073)<1e-12

def test_independent_sar_within_season_result():
    x=json.loads(SAR.read_text(encoding="utf-8"))
    assert x["support"]["colonies"]==6
    assert x["support"]["post_anchor_dates"]==48
    assert x["within_season_aliasing"]["radius_km_0_5"]["false_absence_n"]==1
    for key in ("radius_km_1","radius_km_2","radius_km_5","radius_km_10"):
        assert x["within_season_aliasing"][key]["false_absence_n"]==0
