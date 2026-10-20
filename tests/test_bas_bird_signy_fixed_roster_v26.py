"""Original V26 methods verified using synthetic source data, never bird outcomes."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import check_bas_bird_signy_fixed_roster_v26 as v

def bird(c,year,n="SECRET"):
    return {"Species":"Gentoo penguin","Colony":c,
            "Date nests counted":f"20-Oct-{year%100:02d}","Number of nests":n}
def signy(year,n="SECRET"):
    return {"SPECIES":"Gentoo penguin","SEASON":f"{year}-{(year+1)%100:02d}",
            "TOTAL_NUMBER_OF_PAIRS":n,"DATE_PAIR_COUNT":f"21-Oct-{year%100:02d}"}
def tables():
    b=[bird(c,year) for year in range(1982,2020) for c in v.v25.FIXED_COLONIES]
    s=[signy(year) for year in range(1982,2020)]
    return v.v25.metadata_cohort(b,s)

def test_baseline_is_first_source_year_not_best_correlating_colony():
    b,s,w,_=tables()
    baseline=v.frozen_baseline_roster(w)
    assert baseline==tuple(sorted(v.v25.FIXED_COLONIES))
    cohort,qa=v.candidate_fixed_windows(b,s,w,baseline)
    assert qa["original_Bird_nest_or_Signy_pair_count_values_read"] is False
    assert qa["eligible_fixed_roster_metadata_windows"]==37
    assert "SECRET" not in str(qa)
    assert list(cohort[1982])==list(baseline)

def test_no_missing_count_is_turned_into_zero_by_support_check():
    b,s,w,_=tables()
    baseline=v.frozen_baseline_roster(w)
    cohort,_=v.candidate_fixed_windows(b,s,w,baseline)
    out,error=v.numeric_fixed_roster(b,s,cohort,baseline)
    assert not out
    assert error["unknown_Signy_original_pair_count"]==37

def test_fixed_roster_requires_ALL_earliest_colonies_in_both_years():
    b,s,w,_=tables()
    baseline=v.frozen_baseline_roster(w)
    b.pop((baseline[0],1990))
    fixed,_=v.candidate_fixed_windows(b,s,w,baseline)
    assert 1989 not in fixed and 1990 not in fixed
    assert 1991 in fixed

def test_robustness_stop_and_source_date_diagnostic_not_effect_filter():
    b,s,w,_=tables()
    baseline=v.frozen_baseline_roster(w)
    datecheck=v.stage_date_diagnostics(b,s,list(w),baseline)
    assert datecheck["no_source_dates_used_as_outcome_selection"]
    assert datecheck["original_date_comparability_by_period"]["earlier"]["parsed"]>0
    assert datecheck["original_date_comparability_by_period"]["modern"]["parsed"]>0
    growth={year:{"bird":float(year%3),"signy":float(year%4)} for year in range(1998,2019)}
    model=v.describe(growth)
    assert model["status"]=="HOLD_INSUFFICIENT_FIXED_ROSTER_NUMERIC_SUPPORT"

def test_cannot_expand_island_replication_from_nested_colonies():
    assert v.MIN_WINDOWS==24
    assert v.MIN_EARLY==8 and v.MIN_MODERN==12
    assert v.SPLIT_YEAR==1997
    assert v.EXPECTED_V25_ALL==0.165616495725728
    assert v.EXPECTED_V25_SHORT==-0.33420933224382615
    assert len(v.v25.FIXED_COLONIES)==7
