"""Guards for small-sample exact-camera and cross-axis support."""
from __future__ import annotations
import csv
import importlib.util
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"research/climate-penguin/work/temporal_niche_cross_axis_v2/analyze.py"
spec=importlib.util.spec_from_file_location("niche_axis_v2",SCRIPT)
assert spec is not None and spec.loader is not None
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def test_real_source_niche_and_land_bridge(tmp_path):
    r=mod.run(output=tmp_path/"result.json")
    assert r["inputs"]=={"same_camera_rows":15,"land_source_pair_rows":13}
    a=r["camera_pair_results"]["Adelie-Chinstrap/SIGNc"]
    g=r["camera_pair_results"]["Adelie-Gentoo/PETEe"]
    assert (a["n"],g["n"])==(5,6)
    assert a["slope_days_per_10pp"]==pytest.approx(-1.543081439159629)
    assert g["slope_days_per_10pp"]==pytest.approx(-2.5732222173358537)
    assert a["permutation_two_sided_p"]==pytest.approx(28/120)
    assert g["permutation_two_sided_p"]==pytest.approx(311/720)
    q=r["pooled_camera_pair_fixed_effects"]
    assert q["slope_days_per_10pp"]==pytest.approx(-2.235022616080495)
    assert q["permutation_extreme"]==25258
    assert q["permutation_total"]==86400
    assert q["permutation_two_sided_p"]==pytest.approx(25258/86400)
    assert q["leave_one_season_out_slope_range_days_per_10pp"][1]<0
    assert q["causal_or_future_response_calibrated"] is False
    assert r["temporal_land_matched_site_years_total"]==2
    assert r["temporal_land_support"]["Adelie-Gentoo/PETEe"]["matched_site_years"]==[2017,2020]
    assert not r["temporal_land_support"]["Adelie-Chinstrap/SIGNc"]["land_candidate_found"]
    assert (tmp_path/"result.json").exists()

def test_duplicate_camera_season_is_rejected(tmp_path):
    rows=mod.read_csv(mod.INPUT)
    bad=tmp_path/"bad.csv"
    with bad.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows[:-1]+[dict(rows[-2])])
    with pytest.raises(ValueError,match="Duplicate pair"):
        mod.run(input_path=bad,output=tmp_path/"out.json")

def test_within_pair_centering_is_invariant():
    src=mod.read_csv(mod.INPUT)
    pairs=[("Adelie-Chinstrap","SIGNc"),("Adelie-Gentoo","PETEe")]
    groups=[[dict(r) for r in src if (r["pair"],r["camera"])==key] for key in pairs]
    baseline=mod.pooled_exact(groups)
    for r in groups[1]:
        r["gap_days"]=str(float(r["gap_days"])+100)
    shifted=mod.pooled_exact(groups)
    assert baseline["slope_days_per_10pp"]==pytest.approx(shifted["slope_days_per_10pp"])
    assert baseline["permutation_two_sided_p"]==pytest.approx(shifted["permutation_two_sided_p"])
