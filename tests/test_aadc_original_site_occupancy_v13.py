"""Synthetic-only test records: distinguish survey ignorance from real absence."""
from pathlib import Path
import io
import sys

import pytest
openpyxl=pytest.importorskip("openpyxl")
pytest.importorskip("xlrd")
pytest.importorskip("requests")
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import join_aadc_original_site_occupancy_v13 as v


def synthetic_sources():
    geog=[
        {"geog_site_id":"ISL1","geog_site_feature":"Island",
         "geog_site_area":1.25,"geog_site_area_cat3":"Small",
         "sub_group":"East Antarctic island group",
         "geog_site_latitude":-67.4,"geog_site_longitude":70.7,
         "distance_station":55,"distance_inland_coast":0},
        {"geog_site_id":"OUT1","geog_site_feature":"Continental rock",
         "geog_site_area":.9,"geog_site_area_cat3":"Small",
         "sub_group":"East Antarctic mainland",
         "geog_site_latitude":-68.0,"geog_site_longitude":70.4,
         "distance_station":23,"distance_inland_coast":5},
    ]
    base={"geog_site_id":"ISL1","season":2012,"year":2012,"month":12,
          "obs_number":1,"vantage":"Ground","site_expert_validation":"H",
          "species_expert_validation":"H","occurrence_expert_validation":"H"}
    peng=[
        {**base,"species_code":"ADE","occurrence":"Presence"},
        {**base,"species_code":"ADE","occurrence":"Absence","obs_number":2},
    ]
    flying=[
        {**base,"species_code":"SNP","occurrence":"Not reported"},
        {**base,"species_code":"SNP","occurrence":"Absence","geog_site_id":"OUT1"},
    ]
    rules=[
        {"species_code":"ADE","occurrence":"Presence","vantage":"Ground",
         "geog_site_area_cat3":"Small","rel_sp_detect":1,
         "rel_vantage_detect":1,"site_search_completeness":1,
         "product":1,"occurrence_cert_cat":"High"},
        {"species_code":"ADE","occurrence":"Absence","vantage":"Ground",
         "geog_site_area_cat3":"Small","rel_sp_detect":1,
         "rel_vantage_detect":1,"site_search_completeness":0.8,
         "product":0.8,"occurrence_cert_cat":"Medium"},
        {"species_code":"SNP","occurrence":"Not reported","vantage":"Ground",
         "geog_site_area_cat3":"Small","rel_sp_detect":0.1,
         "rel_vantage_detect":0.2,"site_search_completeness":0.1,
         "product":0.002,"occurrence_cert_cat":"Unknown"},
        {"species_code":"SNP","occurrence":"Absence","vantage":"Ground",
         "geog_site_area_cat3":"Small","rel_sp_detect":0.8,
         "rel_vantage_detect":0.5,"site_search_completeness":0.8,
         "product":0.32,"occurrence_cert_cat":"Low"},
    ]
    old=[{"Geog_Site_ID":"ISL1"}]
    return {"potential_geography_2021":old,
            "potential_geography_2025":geog,
            "penguin_original_search":peng,
            "flying_seabird_original_search":flying,
            "survey_certainty_rules":rules}


def test_original_current_and_previous_geographic_frames_do_not_invent_islands():
    data,events,sites=v.rows_linked(synthetic_sources())
    assert data["original_2025_geographic_site_count"]==2
    assert data["new_2025_siteIDs_absent_from_2021"]==1
    assert data["geog_siteIDs_shared_across_original_versions"]==1
    assert data["original_eight_seabird_source_observations"]==4
    assert len(events)==4
    assert len(sites)==2
    assert events[3]["source_geog_site_feature"]=="Continental rock"


def test_nonreporting_remains_unknown_even_with_low_detection_certainty():
    _,rows,_=v.rows_linked(synthetic_sources())
    unknown=next(x for x in rows if x["occurrence"]=="Not reported")
    assert unknown["occurrence_cert_cat"]=="Unknown"
    assert unknown["scientific_absence_is_not_inferred_from_nonreporting"] is True
    assert "assumed_absence" not in unknown
    assert all(row["scientific_absence_is_not_inferred_from_nonreporting"]
               for row in rows)


def test_two_different_observed_statuses_with_same_site_species_season_are_conflicts():
    qa,_,_=v.rows_linked(synthetic_sources())
    assert qa["original_site_species_season_groups_with_conflicting_occurrence_categories"]==1
    assert qa["source_certainty_lookup_state"]["EXACT_CERTAINTY_RULE"]==4


def test_duplicated_rules_are_not_automatically_resolved_in_favor_of_absence():
    data=synthetic_sources()
    data["survey_certainty_rules"].append(
        {**data["survey_certainty_rules"][1],"occurrence_cert_cat":"High"})
    qa,rows,_=v.rows_linked(data)
    assert qa["original_certainty_key_QA"]["certainty_duplicate_original_keys"]["DUPLICATE_4_WAY_KEY"]==1
    assert any(x["certainty_lookup"]=="AMBIGUOUS_CERTAINTY_RULE" for x in rows)


def test_missing_site_is_unmatched_not_unoccupied():
    data=synthetic_sources()
    data["flying_seabird_original_search"][0]["geog_site_id"]="UNMAPPED"
    result,rows,_=v.rows_linked(data)
    assert result["source_observations_unmatched_to_2025_geography"]["flying_seabird_original_search"]==1
    assert any(x["source_geog_site_lookup"]=="NO_2025_SITE_MATCH"
               for x in rows)
    assert len(rows)==4


def test_original_geography_duplicate_id_stops_instead_of_selecting_one():
    data=synthetic_sources()
    data["potential_geography_2025"].append({
        **data["potential_geography_2025"][0],"geog_site_area":100})
    with pytest.raises(ValueError,match="duplicate"):
        v.rows_linked(data)


def test_original_xlsx_named_worksheet_is_read_and_numeric_id_preserved():
    book=openpyxl.Workbook()
    book.active.title="1_metadata"
    tab=book.create_sheet("2_search events")
    tab.append(["geog_site_id","occurrence","vantage","season"])
    tab.append(["0001","Presence","Ground",2012])
    f=io.BytesIO()
    book.save(f)
    headers,rows=v.sheet_source(f.getvalue(),"2_search events")
    assert headers==["geog_site_id","occurrence","vantage","season"]
    assert rows[0]["geog_site_id"]=="0001"
    assert v.source_id(rows[0]["geog_site_id"])=="0001"
    assert v.source_text(rows[0]["season"])=="2012"
    with pytest.raises(ValueError,match="exact original worksheet"):
        v.sheet_source(f.getvalue(),"InventedSheet")


def test_sheet_role_and_publisher_historic_counts_are_explicit():
    assert v.SOURCE_SPECS["potential_geography_2021"][-1]==4884
    assert v.SOURCE_SPECS["potential_geography_2025"][-1]==7785
    assert v.SOURCE_SPECS["penguin_original_search"][-1]==11089
    assert v.SOURCE_SPECS["flying_seabird_original_search"][-1]==22018
    assert v.SOURCE_SPECS["survey_certainty_rules"][-1]==216


def test_sparse_publisher_first_row_allows_blank_unlabelled_columns_only():
    wb=openpyxl.Workbook()
    wb.active.title="2_Geographic sites"
    sh=wb.active
    sh.append(["Geog_Site_ID","Geog_Site_Area",None,None])
    sh.append(["SITE004",2.3,"unlabelled original author source comment",None])
    buff=io.BytesIO()
    wb.save(buff)
    headers,rows=v.sheet_source(buff.getvalue(),"2_Geographic sites")
    assert len(headers)>=2
    assert rows[0]["Geog_Site_ID"]=="SITE004"
    assert rows[0]["Geog_Site_Area"]==2.3

def test_repeated_nonblank_header_still_fails_closed():
    wb=openpyxl.Workbook()
    wb.active.title="2_Geographic sites"
    wb.active.append(["Geog_Site_ID","Geog_Site_ID",None])
    wb.active.append(["SITE004","OVERRIDE",None])
    buf=io.BytesIO()
    wb.save(buf)
    with pytest.raises(ValueError,match="duplicate original nonblank"):
        v.sheet_source(buf.getvalue(),"2_Geographic sites")
