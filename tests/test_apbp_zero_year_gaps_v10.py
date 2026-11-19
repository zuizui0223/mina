"""Synthetic census chronology; no independent ecological turnover inferred."""
from pathlib import Path
import sys

import pytest
pd=pytest.importorskip("pandas")
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_apbp_reported_zero_year_gaps_v10 as m


def fake_source():
    sp="Pygoscelis adeliae"
    rows=[
        ("S1",sp,"2001-12-10",10),
        ("S1",sp,"2003-01-11",5),  # season 2002: adjacent positive
        ("S1",sp,"2005-12",0),     # season 2005: 3-year gap
        ("S1",sp,"2010-12",3),     # season 2010: 5-year gap
        ("S2",sp,"2019",9),        # year-only not dated nesting season
        ("S2",sp,"2019-12",8),
        ("S2",sp,"2020-12",0),
        ("S2",sp,"2020-12-20",0),  # same-season duplicate -> entire group omitted
        ("S3",sp,"2000-02-20",0),
        ("S3",sp,"2001-02-20",0),
    ]
    return pd.DataFrame([
        {"site_id_original":site,"scientificName_accepted":s,"event_date":date,
         "nest_numeric_candidate":n,"eligibility":"ELIGIBLE_NEST_RECORD_ONLY"}
        for site,s,date,n in rows
    ])


def test_monthly_and_daily_original_dates_are_distinguished_from_year_only():
    unique,qa=m.dated_seasons(fake_source())
    assert qa["same_site_species_year_groups_with_multiple_original_surveys"]==1
    assert qa["same_site_species_year_duplicate_rows_omitted"]==2
    assert len(unique)==7
    assert sorted(unique.loc[unique.site_id_original.eq("S1"),"breeding_start_year"])==[2001,2002,2005,2010]
    assert 2019 not in unique.loc[unique.site_id_original.eq("S2"),"breeding_start_year"].tolist() or len(unique.loc[unique.site_id_original.eq("S2")])==1


def test_exact_neighbor_versus_long_gap_and_no_invented_unobserved_zeros():
    unique,qa=m.dated_seasons(fake_source())
    observed=m.successive_observed_records(unique)
    report=m.summarise(unique,observed,qa,"FAKE_SHA_FOR_TEST")
    assert report["exactly_one_breeding_season_behind_pairs"]==2
    assert report["exact_1year_original_measured_state_transitions"]["positive_to_positive"]==1
    assert report["exact_1year_original_measured_state_transitions"]["zero_to_zero"]==1
    assert report["reported_positive_zero_switches_exact_1year"]==0
    assert report["reported_positive_zero_switches_any_gap"]==2
    assert report["reported_switch_gap_min"]==3
    assert report["reported_switch_gap_max"]==5
    assert report["novel_island_causal_mechanism_found"] is False


def test_all_same_season_duplicate_source_rows_excluded_never_choose_favorable_record():
    df=fake_source()
    # Duplicate 2003 survey for S1 makes its whole 2002 season ineligible.
    duplicate=df.loc[df.event_date.eq("2003-01-11")].copy()
    duplicate.loc[:,"nest_numeric_candidate"]=500
    unique,meta=m.dated_seasons(pd.concat([df,duplicate],ignore_index=True))
    assert 2002 not in unique.loc[unique.site_id_original.eq("S1"),"breeding_start_year"].tolist()
    assert meta["same_site_species_year_groups_with_multiple_original_surveys"]==2


def test_missing_year_not_negative_breeding_count():
    assert m.state(0,0)=="zero_to_zero"
    assert m.state(0,1)=="reported_zero_to_positive"
    assert m.state(15,0)=="positive_to_reported_zero"
    with pytest.raises(ValueError):
        m.state(-1,0)
