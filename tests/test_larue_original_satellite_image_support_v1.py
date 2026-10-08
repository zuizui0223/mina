"""Synthetic ZIP/XML parsing and No/ice ambiguity controls; no 2022+ data."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location(
    "raw_satellite",
    ROOT/"scripts/audit_larue_original_satellite_image_support_v1.py"
)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)


def artificial_xlsx(path: Path):
    main = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    wb=(
      f'<workbook xmlns="{main}" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
      '<sheets><sheet name="images" sheetId="1" r:id="rId1"/></sheets></workbook>'
    )
    rel=(
      '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
      '<Relationship Id="rId1" Target="worksheets/sheet1.xml" /></Relationships>'
    )
    shared=(
      f'<sst xmlns="{main}">'
      '<si><t>site_id</t></si><si><t>img_year</t></si>'
      '<si><t>bpresent</t></si><si><t>area_m2</t></si>'
      '<si><t>UMBE</t></si><si><t>No</t></si><si><t>Yes</t></si>'
      '</sst>'
    )
    sheet=(
      f'<worksheet xmlns="{main}"><sheetData>'
      '<row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="s"><v>1</v></c>'
      '<c r="C1" t="s"><v>2</v></c><c r="D1" t="s"><v>3</v></c></row>'
      '<row r="2"><c r="A2" t="s"><v>4</v></c><c r="B2"><v>2012</v></c>'
      '<c r="C2" t="s"><v>5</v></c><c r="D2"><v>0</v></c></row>'
      '<row r="3"><c r="A3" t="s"><v>4</v></c><c r="B3"><v>2013</v></c>'
      '<c r="C3" t="s"><v>6</v></c><c r="D3"><v>15</v></c></row>'
      '</sheetData></worksheet>'
    )
    with ZipFile(path,"w") as z:
      z.writestr("xl/workbook.xml",wb)
      z.writestr("xl/_rels/workbook.xml.rels",rel)
      z.writestr("xl/sharedStrings.xml",shared)
      z.writestr("xl/worksheets/sheet1.xml",sheet)


def test_parse_without_changing_true_survey_status(tmp_path):
    path=tmp_path/"synthetic.xlsx"
    artificial_xlsx(path)
    rows=M.sheet_records(path.read_bytes(),check_source=False)
    assert len(rows)==2
    assert rows[0]["site_id"]=="UMBE"
    assert rows[0]["img_year"]==2012
    assert rows[0]["bpresent"]=="No"
    assert rows[0]["area_m2"]=="0"
    assert rows[1]["img_year"]==2013
    assert rows[1]["bpresent"]=="Yes"
    assert rows[1]["area_m2"]=="15"


def test_reject_wrong_blob_hash(tmp_path):
    path=tmp_path/"synthetic.xlsx"
    artificial_xlsx(path)
    try:
        M.sheet_records(path.read_bytes())
    except ValueError as err:
        assert "GIT_BLOB_MISMATCH" in str(err)
    else:
        raise AssertionError("Unpinned public source mistakenly accepted")


def test_historical_nine_event_summary_stays_noncausal():
    posterior=json.loads((
        ROOT/"results/EMPEROR_LARUE_2024_50_BY_10_POSTERIOR_ZERO_AUDIT_V1.json"
    ).read_text(encoding="utf8"))
    rows=[
        {"site_id":"UMBE","img_year":2012,"bpresent":"No","area_m2":"0"},
        {"site_id":"UMBE","img_year":2013,"bpresent":"Yes","area_m2":"15"},
    ]
    report=M.summarize(rows,posterior)
    assert report["already_exposed_model_posterior_0_to_positive_events"]==9
    assert report["zero_year_events_with_bpresent_No"]==1
    assert report["zero_year_events_with_independent_verified_physically_available_absent_colony"]==0
    assert report["all_refuge_colonization_criteria_met"] is False
    assert not report["absence_vs_no_ice_separated_using_bpresent_alone"]
    assert report["new_causal_effect_estimated"] is False

def test_frozen_original_599_images_and_nine_transitions():
    d=json.loads((
        ROOT/"results/EMPEROR_LARUE_RAW_SATELLITE_TRANSITION_SUPPORT_V1.json"
    ).read_text(encoding="utf8"))
    assert d["raw_image_rows_2009_2018"] == 599
    assert d["raw_bpresent_values_in_2009_2018"] == {
        "yes":502,"no":20,"NA":77
    }
    assert d["n_prev_year_original_no"] == 8
    assert d["n_prev_year_original_yes"] == 1
    assert d["n_next_year_original_yes"] == 7
    assert d["n_next_year_original_no"] == 1
    assert d["n_next_year_original_NA"] == 1
    assert d["n_raw_no_to_yes_pairs"] == 6
    assert d["n_next_year_outside_original_date_and_area_window"] == 3
    assert d["n_raw_no_to_yes_qualifying_date_area_only"] == 5
    assert d["n_independently_verified_prior_fast_ice_present_and_birds_survey_absent"] == 0
    assert not d["causal_option_social_attraction_test_completed"]
    assert len(d["nine_posterior_transition_image_matches"]) == 9


def test_posterior_means_and_raw_bpresent_are_not_same_measure():
    d=json.loads((
        ROOT/"results/EMPEROR_LARUE_RAW_SATELLITE_TRANSITION_SUPPORT_V1.json"
    ).read_text(encoding="utf8"))
    events=d["nine_posterior_transition_image_matches"]
    laza=next(e for e in events if e["site_id"]=="LAZA")
    assert laza["prior_original_bpresent"]=="yes"
    assert laza["prior_raw_area_m2_zero"]
    amun=next(e for e in events
              if e["site_id"]=="AMUN" and e["posterior_zero_year"]==2012)
    assert amun["next_original_bpresent"]=="NA"
    ledd=next(e for e in events
              if e["site_id"]=="LEDD" and e["posterior_zero_year"]==2014)
    assert ledd["next_original_bpresent"]=="no"
    assert not ledd["next_date_and_pixel_filter_valid"]
    rupe=next(e for e in events if e["site_id"]=="RUPE")
    assert rupe["next_original_bpresent"]=="yes"
    assert rupe["next_image_date"]=="2017-12-11"
    assert not rupe["next_date_and_pixel_filter_valid"]
