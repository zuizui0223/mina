"""Invented MAPPPD census counts; do not infer ecology from these fixtures."""
import csv
import hashlib
import io
import sys
from pathlib import Path

import pytest

pytest.importorskip("requests")
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_mapppd_live_bulk_v7 as m


def fake_original():
    head=",".join(m.HEADER)
    lines=[
        ["Acuna Island","ACUN","48.2","-44.637","-60.761","adelie penguin","12","12","2021","2021","120","1","nests","ground",'<p id="a">Literature paper</p>'],
        ["Acuna Island","ACUN","48.2","-44.637","-60.761","adelie penguin","11","12","2022","2022","130","1","nests","ground",'<p id="b">Literature paper</p>'],
        ["Acuna Island","ACUN","48.2","-44.637","-60.761","adelie penguin","15","12","2023","2023","150","1","nests","ground",'<p id="c">Literature paper</p>'],
        ["Acuna Island","ACUN","48.2","-44.637","-60.761","adelie penguin","20","2","2025","2024","170","2","nests","ground",'<p id="d">Literature paper</p>'],
        ["Island Beta","BETA","48.2","-45.0","-61.1","chinstrap penguin","10","12","2023","2023","12","1","nests","ground",'<p id="e">Source, quoted</p>'],
        ["Island Beta","BETA","48.2","-45.0","-61.1","chinstrap penguin","10","12","2023","2023","11","2","nests","vessel",'<p id="f">Repeated same year</p>'],
        ["Island Gamma","GAMA","48.2","-45.2","-61.2","gentoo penguin","10","12","2024","2024","40","4","adults","ground","Older study"],
        ["Island Gamma","GAMA","48.2","-45.2","-61.2","gentoo penguin","18","12","2024","2024","14","3","nests","ground","Original nesting record"],
        ["Island Gamma","GAMA","48.2","-45.2","-61.2","gentoo penguin","18","11","2022","2022","14","3","nests","ground","Before frozen Oct/Nov ended"],
    ]
    out=io.StringIO(newline="")
    w=csv.writer(out)
    w.writerow(m.HEADER)
    w.writerows(lines)
    return out.getvalue().encode("utf-8")


def test_mutable_current_source_has_exact_public_csv_header_and_safe_citation_text():
    raw=fake_original()
    rows=m.source_rows(raw)
    assert len(rows)==9
    assert rows[0]["site_id"]=="ACUN"
    assert 'id="a"' in rows[0]["reference"]
    assert m.integer_or_none("170")==170
    assert m.integer_or_none("~100") is None
    assert m.integer_or_none("-5") is None
    assert m.integer_or_none("NaN") is None


def test_new_seasons_are_source_season_start_not_year_of_january_count():
    raw=fake_original()
    result,rows=m.audit(raw,{"ACUN"},{("ACUN","Pygoscelis adeliae",2021,120)},{})
    assert result["status"]=="MAPPPD_V44_CURRENT_PUBLIC_CENSUS_EXTENSION_QA_ONLY"
    assert result["original_csv_count_rows"]==9
    assert result["source_siteIDs_shared_with_APBP_v2_3"]==1
    assert result["source_siteIDs_absent_from_APBP_v2_3"]==2
    assert result["source_breeding_nest_rows_in_2022_2023_2024"]=={2022:1,2023:3,2024:2} or (
        result["source_breeding_nest_rows_in_2022_2023_2024"].get(2022)==2 and
        result["source_breeding_nest_rows_in_2022_2023_2024"].get(2023)==3 and
        result["source_breeding_nest_rows_in_2022_2023_2024"].get(2024)==2)
    assert result["n_primary_strict_consecutive_pairs_ending_2022_to_2024"]==3
    assert result["n_primary_strict_consecutive_pairs_bridging_2021_to_2022"]==1
    assert result["source_date_quality"]["NO_UNAMBIGUOUS_DEC_JAN_FEB_DATE"]==1
    assert result["n_new_2022_2024_duplicate_nest_groups"]==1
    assert result["ecological_effect_models_fitted"]==0
    assert len(rows)==9
    assert any(r["season"]==2024 and r["survey_year"]==2025 for r in rows)


def test_original_record_overlap_is_republication_not_an_independent_colony():
    raw=fake_original()
    result,_=m.audit(raw,{"ACUN"},{("ACUN","Pygoscelis adeliae",2021,120)},{})
    assert result["original_APBP_v2_3_exact_nest_count_source_overlaps"]==1
    assert result["n_distinct_primary_site_species_with_new_2022_2024_records"]==3


def test_source_rows_with_wrong_header_are_not_implicitly_another_database():
    raw=fake_original().replace(b"site_name,site_id,",b"Site name,SITE,")
    with pytest.raises(ValueError,match="SCHEMA_STOP"):
        m.source_rows(raw)


def test_input_count_is_not_made_up_from_missing_source():
    assert m.integer_or_none("") is None
    assert m.integer_or_none("10.2") is None
    assert m.integer_or_none("12-15") is None


def test_new_can_include_old_sites_without_claiming_2022_is_independent_publisher():
    assert 2022 in m.NEW_BREEDING_SEASONS
    assert 2024 in m.NEW_BREEDING_SEASONS
    assert 2025 not in m.NEW_BREEDING_SEASONS
    assert all(x in m.HEADER for x in ("site_id","count_type","season_starting","accuracy"))
