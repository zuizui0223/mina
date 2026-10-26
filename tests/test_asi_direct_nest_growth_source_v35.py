"""Synthetic original ASI counted nests annual stage/phase support only."""
from __future__ import annotations
import sys,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from analyze_asi_direct_nest_growth_source_v35 import (
    austral_season_day,source_annual_observed_pairs,summarise
)


def artificial_source():
    data=[]
    mapdata={}
    for i in range(562):
        sid=f"S{i//3:03d}"
        year=2010+i%3
        data.append({
          "Site_ID":sid,"Species":"ADPE","Season":str(year),
          "Count":str(100+(i%3)*10),
          "Region":"CW","Date":f"12/01/{year}",
          "Accuracy":"1"
        })
        mapdata[sid]={
          "original_source_region":"CW",
          "source_geographical_parent_land_status":"EXACT_ONE_SOURCE_LAND_POLYGON",
          "source_exact_original_SCAR_land_FID":"10"
        }
    return data,mapdata


def test_same_seasonal_phase_comparable_counts_only_one_year_apart():
    assert austral_season_day("12/01/2010",2010)==30
    assert austral_season_day("12/01/2011",2011)==30
    assert austral_season_day("01/01/2012",2011)==61
    assert austral_season_day("12/xx/2011",2011) is None
    assert austral_season_day("12/01/2009",2011) is None
    observations,locations=artificial_source()
    pairs,gaps=source_annual_observed_pairs(observations,locations)
    assert len(pairs)==374
    assert gaps=={1:374}
    assert all(x["source_dated_paired_within_30_days_of_same_austral_phase"] for x in pairs)
    assert all(x["original_exact_SCAR_source_land_FID"]=="10" for x in pairs)
    assert pairs[0]["original_one_year_log_count_ratio"]==math.log(110/100)
    summary=summarise(pairs,gaps)
    assert summary["source_direct_adjacent_pairs_strict_land_and_phenology_30_days"]["one_year_observed_source_pairs"]==374
    assert summary["source_direct_adjacent_pairs_strict_land_and_phenology_30_days"]["original_parent_SCAR_land_feature_FID_n"]==1
    assert summary["pre_island_causal_effect_source_gate_passed"] is False


def test_missing_author_original_austral_date_not_fabricated_growth():
    observations,locations=artificial_source()
    observations[1]["Date"]="xx/xx/2011"
    pairs,gaps=source_annual_observed_pairs(observations,locations)
    assert len(pairs)==374
    assert sum(x["source_dated_paired_within_30_days_of_same_austral_phase"] for x in pairs)==372
    assert len(locations)>1
