"""Invented geography and bird-free pairing fixture for v41."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from shapely.geometry import box
import audit_mapppd_v5_scar_land_continuity_v41 as m

def demo():
    geo={n:{"source_site":n,"region":"R",
             "latitude":-70+(i//2)*.1,"longitude":10+(i%2)*.1,
             "status":"EXACT_ONE_LAND_POLYGON","land_feature":(i//2),
             "is_separate_land":True} for i,n in enumerate("ABCDEF")}
    pairs=[{"site":n,"region":"R","species":"ADPE","year":2001,
            "citekey":"one","vantage":"ground"} for n in geo]
    return geo,pairs

def test_pair_kind_and_distance_bin_stratum_only():
    geo,rows=demo()
    pairs=m.make_pairs(rows,geo)
    assert any(x["kind"]=="within_same_land_polygon" for x in pairs)
    assert any(x["kind"]=="between_distinct_land_polygons" for x in pairs)
    result=m.summarize(pairs,geo,"TEST")
    assert result["bird_count_magnitudes_or_correlations_opened"]==0
    assert len(m.BINS)==3

def test_no_provisional_as_exact_polygon_sample():
    geo,rows=demo()
    geo["A"]["status"]="NEAR_UNIQUE_PROVISIONAL"
    exact=m.make_pairs(rows,geo,False)
    near=m.make_pairs(rows,geo,True)
    assert len(near)>=len(exact)
    assert all("A" not in r["pair"] for r in exact)
def test_frozen_geometry_source_and_no_fuzzy_names():
    assert m.GIS_SHA.startswith("66d82fa6")
    assert m.EXACT_SOURCE_TRANSITIONS==771
    assert m.EXACT_SOURCE_PAIR_SITES==95
    assert m.MIN_MATCHED_STRATA==12 and m.MIN_REGIONS==3
    assert m.BINS==((.5,15.),(15.,60.),(60.,100.))
