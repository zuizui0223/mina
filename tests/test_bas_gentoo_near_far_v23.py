"""V23 fully synthetic, no original bird data or source-derived outcomes."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import compare_bas_gentoo_near_far_v23 as mod

def test_signy_bad_season_and_duplicate_whole_year_exclusion():
    data=[
        {"SEASON":"2010-2011","SPECIES":"Gentoo penguin","TOTAL_NUMBER_OF_PAIRS":"100"},
        {"SEASON":"2011-2012","SPECIES":"Gentoo penguin","TOTAL_NUMBER_OF_PAIRS":"NA"},
        {"SEASON":"2012-2013","SPECIES":"Gentoo penguin","TOTAL_NUMBER_OF_PAIRS":"999"},
        {"SEASON":"2012-2013","SPECIES":"Gentoo penguin","TOTAL_NUMBER_OF_PAIRS":"999"},
        {"SEASON":"1998-8895","SPECIES":"Gentoo penguin","TOTAL_NUMBER_OF_PAIRS":"99"},
        {"SEASON":"2013-2014","SPECIES":"Snow petrel","TOTAL_NUMBER_OF_PAIRS":"10"},
    ]
    values,q=mod.signy_records(data)
    assert values[2010]==100 and values[2011] is None
    assert 2012 not in values
    assert q["duplicate_season_groups_excluded"]==1
    assert q["invalid_original_season_rows"]==1
    assert q["rows_not_explicitly_Gentoo"]==1

def test_common_window_gate_rejects_missing_instead_of_zero():
    growth={y:{"bird":float(y%5)+0.5,"maiviken":float(y%4)-0.5}
            for y in range(2009,2019)}
    signy={y:100.0+y for y in range(2009,2020)}
    signy[2011]=None
    a=mod.compare_near_far(growth,signy)
    assert a["common_adjacent_year_windows"]==8
    assert 2010 not in a["common_growth_start_years"]
    assert 2011 not in a["common_growth_start_years"]
    assert a["effect_computed"]

def test_too_few_complete_windows_means_no_sign_claim():
    growth={y:{"bird":y/100.,"maiviken":y/90.} for y in range(2009,2019)}
    signy={y:10.0 for y in range(2009,2016)}
    r=mod.compare_near_far(growth,signy)
    assert r["common_adjacent_year_windows"]==6
    assert not r["effect_computed"]
    assert "STOP_INSUFFICIENT" in r["status"]

def test_no_variance_rejected_and_one_window_removed_range():
    growth={y:{"bird":float(y%3),"maiviken":float(y%4)} for y in range(2009,2019)}
    same={y:1.0 for y in range(2009,2020)}
    r=mod.compare_near_far(growth,same)
    assert r["status"]=="STOP_ZERO_VARIANCE_IN_COMMON_YEAR_SERIES"
    assert mod.ORIGINAL_V22_R==0.5621534427494942
    assert mod.MIN_SAME_WINDOWS==8

def test_common_subset_delta_uses_three_exact_identical_years():
    growth={2009+i:{"bird":float((i*i)%7),"maiviken":float((3*i+1)%5)}
            for i in range(10)}
    signy={2009+i:100.+float((5*i*i)%17) for i in range(11)}
    r=mod.compare_near_far(growth,signy)
    assert r["effect_computed"]
    q=r["pearson_r"]
    assert set(q)=={"near_Bird_Maiviken","far_Bird_Signy","far_Maiviken_Signy"}
    assert abs(r["near_minus_mean_far_r"]-
               (q["near_Bird_Maiviken"]-
                (q["far_Bird_Signy"]+q["far_Maiviken_Signy"])/2))<1e-12
    assert len(r["annual_change_sign_agreement"])==3
    assert r["regional_sea_ice_wind_or_prey_causation_supported"] is False
