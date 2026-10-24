"""V36 invented signs, exact island grouping and source value guards ONLY."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import model_nz_ross_sea_gis_island_growth_v36 as m

def fake_census():
    sheet={0:{0:"Colony",**{y-1980:y for y in range(1981,2025)}}}
    for i,name in enumerate(("Cape Bird North","Beaufort Island","Coulman Island Middle",
                            "Inexpressible Island"),start=1):
        sheet[i]={0:name,**{y-1980:1000+i+y for y in range(1981,2025) if y!=2020}}
    return sheet

def test_source_rows_and_2020_gap_remain_distinct_from_zeros():
    raw,meta=m.source_colony_year_counts(fake_census())
    assert len(raw)==4
    assert meta["source_colony_source_years"]==44
    assert meta["original_2020_count_values_present"]==0
    assert m.original_numeric(0)==0.
    assert m.original_numeric(None) is None
    assert m.original_numeric(-999) is None
    assert m.original_numeric("NA") is None

def test_fixed_4_islands_13_windows_and_equal_year_weight():
    growth={
        "Ross Island":{1983:0.2,1984:0.2,1985:-0.1},
        "Beaufort Island":{1983:0.3,1984:-0.2,1985:0.},
        "Coulman Island":{1983:-0.3,1984:-0.4},
        "Inexpressible Island":{},
    }
    q=m.year_balanced_concordance(growth,(1983,1984,1985))
    assert q["years_with_two_nonzero_island_changes"]==2
    assert q["original_pair_comparisons"]==6
    assert q["original_pair_comparisons_same_sign"]==2
    assert abs(q["observed_year_balanced_agreement"]-(1/3))<1e-12
    assert m.ISLANDS==tuple(sorted(m.POLYGONS))
    assert len(m.SOURCE_WINDOWS)==13
    assert m.SOURCE_WINDOWS[:2]==(1983,1984)

def test_independent_null_is_reproducible_not_claimed_p_value():
    a={
       "Ross Island":{y:(1 if y%3 else -1) for y in m.SOURCE_WINDOWS},
       "Beaufort Island":{y:(-1 if y%4==0 else 1) for y in m.SOURCE_WINDOWS},
       "Coulman Island":{y:(1 if y%5==0 else -1) for y in m.SOURCE_WINDOWS},
       "Inexpressible Island":{y:(-1 if y%2 else 1) for y in m.SOURCE_WINDOWS},
    }
    p=m.null_year_shuffles(a,iterations=31,seed=22)
    q=m.null_year_shuffles(a,iterations=31,seed=22)
    assert p==q
    assert p["valid_shuffles"]==31
    assert p["null_not_temporal_autocorrelation_robust_or_an_inferential_p_value"]

def test_no_colony_can_become_separate_island():
    source={
       "Ross Island":{1983:(("Cape Bird North",True),("Cape Royds",True))},
       "Beaufort Island":{1983:(("Beaufort Island",False),)},
    }
    counts={
       "Cape Bird North":{1983:100,1984:105},
       "Cape Royds":{1983:20,1984:24},
       "Beaufort Island":{1983:15,1984:19}
    }
    growth,comps=m.growth_by_island(source,counts)
    assert len(growth)==2 and comps["Ross Island"][1983]==2
    exact,_=m.growth_by_island(source,counts,exact_only=True)
    assert "Beaufort Island" not in exact
    assert m.pearson([1.,2.,3.,4.],[4.,3.,2.,1.]) is None

def test_v35_metadata_must_match_exact_source_and_roster():
    v35={
       "status":"V35_ORIGINAL_NZ_ROSS_SEA_COASTLINE_ISLAND_PANEL_GEOMETRY_QA",
       "original_SCAR_ADD_medium_ZIP_SHA256":m.SOURCE_GIS_SHA,
       "publisher_census_sha256":m.SOURCE_CENSUS_SHA,
       "publisher_location_sha256":m.SOURCE_GEO_SHA,
       "original_group_to_GIS_landpolygonID":m.V35_GROUPS,
       "prespecified_original_GIS_locus_year_support":{
           "source_geography_and_calendar_gate_pass":True,
           "source_years_with_ge2_named_GIS_island_units":list(m.SOURCE_WINDOWS),
           "source_named_GIS_island_temporal_support":{
               **{island:{"original_same_colony_adjacent_year_window_count":5}
                  for island in m.ISLANDS},
               "Possession Island":{"original_same_colony_adjacent_year_window_count":0}
           }},
       "original_colony_geo_link_records":[]
    }
    panel,links=m.frozen_v35(v35)
    assert len(panel)==5
    v35["prespecified_original_GIS_locus_year_support"]["source_years_with_ge2_named_GIS_island_units"]=[1984]
    try:m.frozen_v35(v35);assert False
    except ValueError as err: assert "year roster" in str(err)
