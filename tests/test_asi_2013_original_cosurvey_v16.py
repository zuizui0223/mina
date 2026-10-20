"""Only invented site, dates and count values."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_asi_2013_original_cosurvey_v16 as a
import pytest

def row(sp="ADPE",date="12/12/2007",source="ASI",typ="N",count="SECRET"):
    return {"Site_ID":"ABCD","Region":"SH","Site_name":"invented","Latitude":"-64.5",
            "Longitude":"-60.5","Species":sp,"Date":date,"Season":"2007",
            "Counted_object":typ,"Accuracy":"2","Count":count,"Notes":"","Source":source}

def test_coevent_and_count_secrecy():
    rr=[row(),row("CHPE"),row("SOGP")]
    s=a.structural(rr)
    assert s["two_penguin_species"]["distinct_same_site_day_events"]==1
    assert s["penguin_flying_species"]["distinct_same_site_day_events"]==1
    assert s["numeric_original_Count_cells_opened"]==0
    assert s==a.structural([{**r,"Count":"123456789"} for r in rr])

def test_chicks_and_published_records_are_dropped_not_nested():
    s=a.structural([row(),row("CHPE",typ="C"),row("SOGP",source="other")])
    assert s["two_or_more_species"]["distinct_same_site_day_events"]==0

def test_source_duplicate_drop_entire_key():
    s=a.structural([row(),row("CHPE"),row("CHPE",count="999")])
    assert s["excluded_duplicate_source_groups"]==1
    assert s["excluded_duplicate_source_rows"]==2
    assert s["two_penguin_species"]["distinct_same_site_day_events"]==0

def test_partial_day_and_austral_clock_reject():
    assert a.eligible_metadata(row(date="12/xx/2007")) is None
    assert a.eligible_metadata(row(date="01/12/2008")) is not None
    assert a.eligible_metadata(row(date="01/12/2007")) is None
    assert a.eligible_metadata({**row(),"Accuracy":"5"}) is None

def test_original_md5_fails_closed():
    with pytest.raises(ValueError,match="MD5 mismatch"):
        a.fetch_original(lambda u:(u,b"unverified artificial original"))
    with pytest.raises(ValueError,match="redirect"):
        a.fetch_original(lambda u:("https://example.org/some.csv",b"x"))

def test_disagreeing_region_codes_on_one_source_site_are_all_dropped():
    v1=row()
    v2={**row("CHPE"),"Region":"NW"}
    result=a.structural([v1,v2])
    assert result["conflicting_region_source_site_IDs_excluded"]==1
    assert result["metadata_rows_at_region_conflicting_site_IDs_removed"]==2
    assert result["eligible_strict_ASI_exact_day_nest_rows"]==0
    assert result["numeric_original_Count_cells_opened"]==0
