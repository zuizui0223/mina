"""V25 invented source histories only; never access original bird magnitude here."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import compare_bas_bird_signy_longterm_v25 as v

def original_bird(c,y,n="SECRET"):
    return {"Species":"Gentoo penguin","Colony":c,
            "Date nests counted":f"20-Oct-{y%100:02d}","Number of nests":n}
def original_signy(y,n="SECRET"):
    return {"SEASON":f"{y}-{(y+1)%100:02d}","SPECIES":"Gentoo penguin",
            "TOTAL_NUMBER_OF_PAIRS":n}

def test_fixed_colony_year_metadata_before_any_number():
    b=[original_bird(c,y) for y in range(1982,2019) for c in v.FIXED_COLONIES]
    s=[original_signy(y) for y in range(1982,2019)]
    bi,si,window,qa=v.metadata_cohort(b,s)
    assert qa["no_nesting_count_magnitudes_used_before_gate"]
    assert qa["eligible_candidate_adjacent_bird_signy_year_windows"]==36
    assert len(bi)==37*7
    assert "SECRET" not in str(qa)
    values,errors=v.numeric_growth(bi,si,window)
    assert not values and errors["unknown_original_Signy_pair_count"]==36

def test_duplicate_year_and_colony_whole_group_drop():
    b=[original_bird(c,y) for y in range(2010,2013) for c in v.FIXED_COLONIES]
    b.append(original_bird("Johnson",2010,"999999"))
    s=[original_signy(y) for y in range(2010,2013)]
    bi,si,win,qa=v.metadata_cohort(b,s)
    assert qa["bird_original_duplicate_colony_season_groups_dropped"]==1
    assert ("Johnson",2010) not in bi
    assert len(win)==2

def test_bad_signy_year_is_not_converted_to_a_biological_zero():
    b=[original_bird(c,2012) for c in v.FIXED_COLONIES]
    s=[original_signy(2012),{"SEASON":"1998-8895","SPECIES":"Gentoo",
                             "TOTAL_NUMBER_OF_PAIRS":"999"}]
    bi,si,w,qa=v.metadata_cohort(b,s)
    assert qa["signy_invalid_original_season_labels"]==1
    assert len(si)==1

def test_short_V23_effect_verification_required_before_historical_claim():
    good={y:{"bird":float(y%3),"signy":float(y%5),"matched_colonies":7}
          for y in range(1982,2019)}
    r=v.describe(good)
    assert r["status"]=="STOP_ORIGINAL_V23_SHORT_EFFECT_NOT_REPRODUCED"
    assert not r["effect_computed"]

def test_history_size_and_original_roster_are_frozen():
    assert v.FIRST==1982 and v.LAST==2019
    assert v.MIN_STRUCTURAL_WINDOWS==20
    assert v.MIN_BIRD_COLONIES==5
    assert v.SHORT_EPOCH_YEARS==tuple(range(2011,2019))
    assert len(v.FIXED_COLONIES)==7
