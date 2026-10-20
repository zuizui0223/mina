"""Synthetic-only tests: no original seabird response values."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_aadc_penguin_skua_joint_search_v15 as v
import pytest

def source(sid,sp,occ="P",season="201617",day="12"):
    return dict(geog_site_id=sid,species_code=sp,season=season,occurrence=occ,
                occurrence_cert_cat="5" if occ=="P" else "4",
                certainty_lookup="EXACT_CERTAINTY_RULE",vantage="G",
                day=day,month="12",year="2016",day_uncertainty="0",obs_number="1")

def test_same_original_site_and_same_season_not_neighbour_or_next_year():
    r=[source("X","ADP"),source("X","SK"),source("X","SP",season="201718")]
    d=v.structural_pairs(r,{"X":"1_2"})
    assert d["SK"]["paired_original_site_seasons"]==1
    assert d["SP"]["paired_original_site_seasons"]==0
    assert d["SK"]["same_exact_day_paired_site_seasons"]==1

def test_nr_and_both_consistent_and_conflicting_duplicate_groups_are_never_valid_pairs():
    penguin=source("X","ADP")
    skua=source("X","SK")
    unknown={**skua,"occurrence":"NR","occurrence_cert_cat":"2"}
    assert v.structural_pairs([penguin,unknown],{"X":"1_2"})["SK"]["paired_original_site_seasons"]==0
    for duplicate in [skua,{**skua,"occurrence":"A","occurrence_cert_cat":"4"}]:
        d=v.structural_pairs([penguin,skua,duplicate],{"X":"1_2"})
        assert d["SK"]["paired_original_site_seasons"]==0

def test_swapping_real_P_and_A_does_not_change_eligibility_support():
    orig=[source("X","ADP"),source("X","SK",occ="A")]
    flip=[{**r,"occurrence":"A" if r["occurrence"]=="P" else "P",
           "occurrence_cert_cat":"4" if r["occurrence"]=="P" else "5"} for r in orig]
    assert v.structural_pairs(orig,{"X":"1_2"})==v.structural_pairs(flip,{"X":"1_2"})
    assert v.decision(v.structural_pairs(orig,{"X":"1_2"}))["ecological_models_fit"]==0

def test_day_uncertainty_or_missing_day_blocks_exact_day_but_not_season():
    r=[source("X","ADP",day=""),source("X","SK")]
    d=v.structural_pairs(r,{"X":"1_2"})["SK"]
    assert d["paired_original_site_seasons"]==1
    assert d["same_exact_day_paired_site_seasons"]==0
    assert d["same_obsnumber_text_pairs_not_joint_survey"]==1
    assert d["P_A_biological_outcomes_tabulated"] is False

def test_source_clocks_and_bad_sha_fail_closed(tmp_path):
    assert v.season_valid("201617")
    assert not v.season_valid("201619")
    assert not v.season_valid("2016")
    assert not v.season_valid("192021")
    p=tmp_path/"fake.csv";p.write_text("k,v\n1,2\n")
    with pytest.raises(ValueError,match="SOURCE_STOP"):
        v.read_pinned(p,v.SITE_SHA)

def test_non_island_is_not_put_in_island_risk_set():
    geo=[dict(geog_site_id="A",geog_site_feature="island",geog_site_area="90",
              latitude="-66",longitude="46"),
         dict(geog_site_id="B",geog_site_feature="continent",geog_site_area="90",
              latitude="-66",longitude="46")]
    x=v.index_islands(geo)
    assert "A" in x and "B" not in x
