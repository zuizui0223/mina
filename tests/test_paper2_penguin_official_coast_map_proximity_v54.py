"""V54 post-result BAS official 2020 map proximity: no false V51 gate success."""
import sys
from pathlib import Path
import numpy as np
import pytest
from shapely.geometry import box

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import analyze_paper2_penguin_official_coast_map_proximity_v54 as a


def fixture():
    rng=np.random.default_rng(20261028)
    anchors={
        "Ashen_Hills":(535000,3592500),
        "Bellingshausen":(495000,3414580),
        "Beach_Point":(482000,3411000),
        "Hewison_Point":(482500,3411100),
    }
    coast={
        "Saunders":box(534800,3592300,535200,3592700),
        "Bellingshausen":box(494800,3414400,495200,3414800),
        "Thule":box(481800,3410800,482700,3411500)
    }
    original={}
    for name,anchor in anchors.items():
        n=250
        raw=np.asarray(anchor,dtype=float)+rng.normal(0,45,(n,2))
        raw[:7,0]+=320  # simulated points outside published coastline
        yy=np.tile([0,1],n//2).astype(np.uint8)
        elev=rng.normal(25,5,n)
        slope=rng.normal(11,4,n)
        original[name]={"xy":raw,"label":yy,"elev":elev,"slope":slope}
    return original,coast


def test_original_sha_and_island_source_provenance_are_immutable():
    assert a.SHA=="27b4cd2085b9c845abf7928c336cf82f0d37492bbe2c21522ac4c670750f6cff"
    assert a.SOURCE_SHAPE_INDEX=={"Saunders":458,"Bellingshausen":451,"Thule":450}
    assert a.SOURCE_SAMPLE_COUNTS["Hewison_Point"]==(22424,19203)
    assert a.v51.MIN_INSIDE_SOURCE==.95


def test_map_proximity_not_land_route_and_species_outside_reported(monkeypatch):
    d,coast=fixture()
    from shapely import contains_xy
    from shapely import points,distance
    expected={}
    for site,z in d.items():
        original=coast[a.v51.PARENT[site]]
        expected[site]=(len(z["xy"]),int(contains_xy(original,
                    z["xy"][:,0],z["xy"][:,1]).sum()))
    monkeypatch.setattr(a,"SOURCE_SAMPLE_COUNTS",expected)
    x,atlas=a.island_coast_map_only(d,coast)
    assert len(atlas)==4
    assert atlas["Hewison_Point"]["original_land_coast_excludes_source_nests_n"]>0
    assert x["Ashen_Hills"]["keep"].sum()==250
    assert (x["Ashen_Hills"]["D_coast"]>=0).all()
    assert atlas["Hewison_Point"]["original_species_descriptors"]["ADELIE"]["source_original_outside_2020_land_coast_distance"]["n"]>0
    assert atlas["Hewison_Point"]["original_species_descriptors"]["CHINSTRAP"]["source_original_map_distance_to_published_coast_metres"]["n"]==125
    fold=a.v51.source_heldout_predictive_qa(d,x)
    assert fold["original_frozen_holdout_groups_n"]==3
    assert len(fold["heldout_island_Brier"]["Thule"]["source_heldout_original_localities"])==2
    assert fold["individual_penguin_nests_independent_island_replicates"] is False


def test_missing_original_coast_source_Dem_coverage_stops_without_rescue(monkeypatch):
    d,coast=fixture()
    from shapely import contains_xy
    expected={k:(len(v["xy"]),int(contains_xy(coast[a.v51.PARENT[k]],
                 v["xy"][:,0],v["xy"][:,1]).sum()))
              for k,v in d.items()}
    monkeypatch.setattr(a,"SOURCE_SAMPLE_COUNTS",expected)
    d["Ashen_Hills"]["slope"][:80]=np.nan
    with pytest.raises(ValueError,match="DEM_COVERAGE"):
        a.island_coast_map_only(d,coast)


def test_source_only_distance_summary_no_false_observations():
    q=a.qsummary([1,2,3,4,5])
    assert q["n"]==5 and q["median"]==3
    assert a.qsummary([float("nan")])["median"] is None


def test_different_original_coast_raw_bytes_fail_source_sha_gate(monkeypatch):
    d,coast=fixture()
    monkeypatch.setattr(a.v52,"original_download",lambda:b"not the official bas coast")
    with pytest.raises(ValueError,match="SHA_CHANGED"):
        a.original_exact_coastal_geography(d)
