"""Synthetic data only, NO original animal response cells in unit tests."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import fit_bas_bird_maiviken_nests_v22 as v
import pytest

def bird(year,colony,count="SECRET",date=None):
    date=date or f"10/12/{year}"
    return {"Species":"Gentoo penguin","Colony":colony,
            "Date nests counted":date,"Number of nests":count}

def main(year,count="SECRET",day=None):
    return {"Season":f"{year}/{(year+1)%100:02d}",
            "Date of nest count":day or f"14/12/{year}",
            "Number of incubating nests":count}

def create(years,baseline="SECRET"):
    return ([bird(y,c,baseline) for y in years for c in ("Alpha","Beta","Gamma")],
            [main(y,baseline) for y in years])

def test_metadata_gate_does_not_read_original_count_secrets():
    b,m=create(range(2009,2019))
    cohort,windows,qa=v.source_metadata_only(b,m)
    assert qa["eligible_same_year_seasons"]==10
    assert qa["eligible_consecutive_year_colonymatched_windows"]==9
    assert qa["original_count_magnitudes_read"]==0
    assert v.nested_support_pass(qa)
    assert v.analyze_counts(cohort,windows)["status"]=="HOLD_NUMERIC_COMMON_YEAR_SUPPORT"

def test_full_synthetic_numeric_association_finite_without_p_value():
    b,m=create(range(2009,2019),baseline="100")
    for i,x in enumerate(b):
        x["Number of nests"]=str(100+(int(x["Date nests counted"][-4:])-2009)*10+(i%3))
    for x in m:
        x["Number of incubating nests"]=str(120+(int(x["Season"][:4])-2009)*11)
    data,win,_=v.source_metadata_only(b,m)
    model=v.analyze_counts(data,win)
    assert model["ecological_effect_fitted"]
    assert model["regional_wind_ice_prey_mechanism_estimated"] is False
    assert model["coastal_small_island_vs_large_main_island_growth_pearson_r"] is not None

def test_duplicate_colony_year_excluded_wholesale():
    b,m=create(range(2009,2018))
    b.append(bird(2011,"Alpha","999999"))
    _,win,qa=v.source_metadata_only(b,m)
    assert qa["bird_original_duplicate_colony_year_groups_excluded"]==1
    assert all(n>=3 for n in qa["shared_bird_colonies_per_window"].values())

def test_austral_day_parse_and_season_logic():
    assert v.start_year(v.parse_count_day("10/12/2010"))==2010
    assert v.start_year(v.parse_count_day("15/01/2011"))==2010
    assert v.parse_count_day("31/02/2011") is None
    assert v.season_year("2009/10")==2009
    assert v.season_year("2009/2010")==2009
    assert v.season_year("2009/18") is None
    assert v.raw_count("0")==0
    assert v.raw_count("") is None
    assert v.raw_count("NA") is None

def test_sign_concordance_cannot_turn_fake_missing_to_zero():
    assert v.raw_count("10") == 10
    assert v.raw_count("-1") is None
    assert v.raw_count("text") is None
