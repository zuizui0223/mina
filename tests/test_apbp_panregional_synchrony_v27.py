"""Invented Pygoscelis observations only."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_apbp_panregional_synchrony_v27 as v

def row(site,sp,yr,mo,lat=-65,lon=43,method="ground",n="SECRET"):
    return {"eligibility":"ELIGIBLE_NEST_RECORD_ONLY","scientificName_accepted":sp,
            "site_id_original":site,"event_date":f"{yr}-{mo:02d}-12",
            "decimalLatitude":str(lat),"decimalLongitude":str(lon),
            "samplingProtocol":method,"source_associatedReferences":"Reference",
            "nest_numeric_candidate":n}

def test_calendar_and_season():
    assert v.season_month("2018-12-01")==(2018,12)
    assert v.season_month("2019-01")==(2018,1)
    assert v.season_month("2019-02-28")==(2018,2)
    assert v.season_month("2019")==None
    assert v.season_month("2018-10-01")==None

def test_same_month_and_method_or_drop():
    sp="Pygoscelis adeliae"
    a=[row("A",sp,2010,12),row("A",sp,2011,12),
       row("B",sp,2010,12),row("B",sp,2012,1),
       row("C",sp,2010,12,method="ship"),row("C",sp,2011,12,method="ground")]
    g,r=v.metadata(a)
    assert r["strict_same_month_same_protocol_adjacent_site_changes"]==1
    assert r["transition_metadata_exclusions"]["month_changed"]==1
    assert r["transition_metadata_exclusions"]["protocol_changed_or_unreported"]==1
    assert r["original_biological_count_values_accessed"]==0

def test_duplicate_group_discarded_without_outcome_selection():
    sp="Pygoscelis papua"
    q=[row("A",sp,2002,12),row("A",sp,2002,12),
       row("A",sp,2003,12)]
    chosen,qa=v.metadata(q)
    assert qa["duplicate_source_groups_excluded"]==1
    assert qa["source_rows_in_duplicate_groups"]==2
    assert qa["strict_same_month_same_protocol_adjacent_site_changes"]==0

def test_absent_source_not_zero():
    assert v.source_count({"nest_numeric_candidate":"0"})==0
    assert v.source_count({"nest_numeric_candidate":""}) is None
    assert v.source_count({"nest_numeric_candidate":"NA"}) is None

def test_one_geographic_block_does_not_pass():
    sp="Pygoscelis adeliae"
    q=[row(str(i),sp,y,12,-66+i*.001,43+i*.001) for i in range(5)
       for y in [2010,2011]]
    chosen,qa=v.metadata(q)
    assert not qa["frozen_macro_gate_pass"]
    assert not chosen
