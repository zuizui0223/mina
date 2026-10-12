"""Synthetic-only NZ census XLSX source schema tests. No Antarctic outcomes."""
import hashlib, importlib.util, json
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
import pytest

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"scripts/audit_nz_2026_ross_39_colony_census_source_v13.py"
spec=importlib.util.spec_from_file_location("nz_39",SRC)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def excel_col(num):
    st=""
    while num:
        num,rem=divmod(num-1,26)
        st=chr(65+rem)+st
    return st

def fixture_xlsx():
    years=list(range(1981,2025))
    rows=[
      ["Colony"]+[str(y) for y in years],
      ["Cape Royds"]+["100" if y==1981 else "NA" if y==2020 else "250" if y==2024 else "" for y in years],
      ["Cape Barne"]+["0" if y==2024 else "" for y in years],
      ["Cape Crozier"]+["350" if y==2001 else "" for y in years],
      ["Total"]+["450" if y==2001 else "" for y in years],
    ]
    xml=[]
    for idx,row in enumerate(rows,1):
        cells=[]
        for col,val in enumerate(row,1):
            if not val:continue
            ref=excel_col(col)+str(idx)
            cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{val}</t></is></c>')
        xml.append(f'<row r="{idx}">{"".join(cells)}</row>')
    data=('<?xml version="1.0" encoding="utf-8"?>'
          '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
          '<sheetData>'+"".join(xml)+'</sheetData></worksheet>')
    wb=('<?xml version="1.0" encoding="utf-8"?>'
        '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"'
        ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
        '<sheets><sheet name="Census" sheetId="1" r:id="rId1"/></sheets></workbook>')
    rel=('<?xml version="1.0" encoding="utf-8"?>'
         '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
         '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"'
         ' Target="worksheets/sheet1.xml"/></Relationships>')
    b=BytesIO()
    with ZipFile(b,"w") as z:
        z.writestr("xl/workbook.xml",wb)
        z.writestr("xl/_rels/workbook.xml.rels",rel)
        z.writestr("xl/worksheets/sheet1.xml",data)
    return b.getvalue()

def test_2026_missing_years_not_interpreted_as_zero(monkeypatch):
    raw=fixture_xlsx()
    monkeypatch.setattr(m,"SOURCE_MD5",hashlib.md5(raw).hexdigest())
    a=m.evaluate_xlsx(raw)
    assert a["n_named_nonaggregate_source_rows"]==3
    assert len(a["source_years"])==44
    assert a["contains_cape_barne_literal"]
    assert a["surveyed_positive_zero_missing_by_year"]["2024"]["EXPLICIT_ZERO_SOURCE"]==1
    assert a["surveyed_positive_zero_missing_by_year"]["2024"]["POSITIVE_NUMERIC_COUNT"]==1
    assert a["surveyed_positive_zero_missing_by_year"]["2024"]["MISSING_BLANK"]==1
    assert a["surveyed_positive_zero_missing_by_year"]["2020"]["TEXT_UNRESOLVED"]==1
    assert a["total_source_cells_expected"]==3*44
    assert a["total_reported_numeric_count_cells"]==4
    assert a["total_unresolved_source_text_cells"]==1
    assert sum(a["value_classes"].get(x,0) for x in ("MISSING_BLANK","TEXT_UNRESOLVED","EXPLICIT_ZERO_SOURCE","POSITIVE_NUMERIC_COUNT","OTHER_NONNEG_INTEGER_REVIEW"))==132
    assert a["numeric_survey_coverage_by_colony"]["Cape Royds"]["valid_2024_count"]==250
    assert a["numeric_survey_coverage_by_colony"]["Cape Barne"]["valid_2024_count"]==0
    assert a["numeric_survey_coverage_by_colony"]["Cape Crozier"]["valid_2024_count"] is None
    assert a["n_colonies_with_any_1981_to_2024_consecutive_year_pair"]==0
    assert a["source_count_zeros_not_conflated_with_missing"]
    assert a["Cape_Barne_missing_from_roster_if_absent_not_proof_of_2024_extinction"]
    assert a["no_new_ecological_model_fitted"]

def test_no_wrong_resource_hash_or_mirror_allowed():
    api={"success":True,"result":{
        "id":m.RESOURCE_ID,"hash":m.SOURCE_MD5,"format":"XLSX",
        "url":"https://datastore.landcareresearch.co.nz/dataset/foo.xlsx",
        "name":"Aerial Survey Data","size":12000}}
    out=m.official_metadata(json.dumps(api).encode())
    assert m.approved(out["url"])
    for bad in ("https://github.com/data.xlsx",
                "http://datastore.landcareresearch.co.nz/dataset/foo.xlsx"):
        api["result"]["url"]=bad
        with pytest.raises(ValueError):
            m.official_metadata(json.dumps(api).encode())
    api["result"]["url"]=out["url"]
    api["result"]["hash"]="WRONG"
    with pytest.raises(ValueError):
        m.official_metadata(json.dumps(api).encode())

def test_mismatched_original_md5_must_halt(monkeypatch):
    raw=fixture_xlsx()
    monkeypatch.setattr(m,"SOURCE_MD5","00000000000000000000000000000000")
    with pytest.raises(ValueError,match="MD5"):
        m.evaluate_xlsx(raw)

def test_repo_contract_does_not_authorize_movement_or_population_effect():
    z=json.loads((ROOT/"contracts/ROSS_NZ_2026_39_COLONY_SOURCE_GATE_V13.json").read_text())
    assert z["new_biological_effects_fitted"]==0
    assert z["frozen_pr189_untouched"]
    assert z["pr142_source_authentication_unmodified"]
    assert "Do not conclude Cape Barne absent solely because omitted from 39-colony survey roster." in z["strict_source_quality_gates"]
