"""Only fake geographical island and site-year metadata, no animal count outcomes."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_nz_ross_sea_island_groups_v34 as a
import audit_nz_ross_sea_census_source_v33 as base

def census():
    m={0:{0:"Colony",**{i+1:1981+i for i in range(15)}}}
    for i,name in enumerate(("Cape Bird North","Cape Bird Middle","Cape Anne",
                              "Coulman Island North","Cape Adare","Foyn Island")):
        m[i+1]={0:name,**{j:100+i+j for j in range(1,16)}}
    return m

def locations():
    v=[
    ["Cape Bird North","Ross Island","77°14'S","166°25'E"],
    ["Cape Bird Middle","Ross Island","77°14'S","166°25'E"],
    ["Cape Anne","Coulman Island","73°37'S","169°52'E"],
    ["Coulman Island North","Coulman Island","73°20'S","169°40'E"],
    ["Cape Adare","Adare Peninsula","71°18'S","170°09'E"],
    ["Foyn Island","Northern Ross Sea","73°30'S","171°00'E"],
    ]
    return {i:{j:value for j,value in enumerate(row)} for i,row in enumerate(v)}

def test_explicit_island_not_cape_or_peninsula():
    assert a.named_landmass("Cape Bird","Ross Island")[0]=="Ross Island"
    assert a.named_landmass("Cape Adare","Adare Peninsula")[0] is None
    assert a.named_landmass("Foyn Island","Northern Ross Sea")[0]=="Foyn Island"
    assert a.named_landmass("Aviation Islands","Southern Ross Sea")[0] is None

def test_source_name_exact_crosswalk_and_different_island_units():
    x=a.source_crosswalk(census(),locations())
    assert x["exact_colony_location_ID_matches"]==6
    assert x["n_distinct_explicit_named_source_island_candidate_groups"]==3
    assert x["n_named_islands_with_ge5_original_adjacent_growth_windows"]==3
    assert x["n_years_with_ge2_named_islands"]==14
    assert x["source_named_island_panel_gate"]
    assert x["stricter_multi_colony_island_comparison_gate"]
    assert x["original_count_magnitudes_opened"]==0

def test_coarse_dms_is_source_metadata_not_precision_claim():
    assert a.parse_angle("76°56'S")==-(76+56/60)
    assert a.parse_angle("167°03'E")==167+3/60
    assert a.parse_angle("oops") is None

def test_unknown_alias_is_unmatched_not_location_closeness():
    l=locations()
    l[5][0]="Foyn Island New"
    x=a.source_crosswalk(census(),l)
    assert "Foyn Island" in x["unmatched_original_census_colony_names"]
    assert "Foyn Island New" in x["location_names_without_exact_census_match"]
    assert not x["true_GIS_island_identities_or_boundaries_independently_verified"]

def test_fixed_hashes_and_observed_covid_gap():
    assert len(a.CENSUS_SHA)==64
    assert len(a.LOCATION_SHA)==64
    assert a.MIN_ISLAND_UNITS_WITH_FIVE_PAIRS==3
    assert a.MIN_MULTI_ISLAND_YEAR_WINDOWS==8
