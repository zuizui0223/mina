"""Synthetic publisher metadata only. Biological values are never used."""
import sys
from pathlib import Path
import io
import json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_aadc_three_island_original_v28 as mod
import pytest
from openpyxl import Workbook

def test_exact_eds_ids_and_metadata_guard():
    item=[dict(eds_id="1103",uuid="12345678-1234-1234-1234-123456789012",
               dataset_name="Bechervaise three islands population counts",
               metadata_entry_id="population_counts_BI"),
          dict(eds_id="5516",uuid="12345678-1234-1234-1234-123456789013",
               dataset_name="MacRobertson Land penguin demography",
               metadata_entry_id="AAS_4518_MacRobertson_Land_Adelie_Penguins")]
    x=mod.listed_datasets(json.dumps(item).encode())
    assert x["1103"]["eds_id"]=="1103" and x["5516"]["eds_id"]=="5516"
    item[0]["dataset_name"]="unrelated marine fish"
    item[0]["metadata_entry_id"]="unrelated"
    with pytest.raises(ValueError,match="identity mismatch"):
        mod.listed_datasets(json.dumps(item).encode())

def test_historical_and_environment_filename_selection():
    names=[{"name":"1990/penguin_counts.xls","size":90000},
           {"name":"population/individual resights 2003.xls","size":900},
           {"name":"Time series demography and environmental covariates.xls","size":50000}]
    a,_=mod.object_candidates("1103",names)
    assert len(a)==3
    b,_=mod.object_candidates("5516",names)
    assert b==["Time series demography and environmental covariates.xls"]

def test_realistic_excel_text_headers_and_no_count_values_exposed():
    wb=Workbook()
    ws=wb.active
    ws.title="Island records"
    ws.append(["Season","Béchervaise Island Counts","Verner Island Counts","Petersen Island Counts"])
    ws.append([1991,10000,100,200])
    wb2=io.BytesIO();wb.save(wb2)
    report=mod.spreadsheet_probe(wb2.getvalue(),"source.xlsx")
    t=str(report)
    assert "Béchervaise Island Counts" in t
    assert "10000" not in t
    assert report["original_occupied_nests_opened"]==0

def test_source_binary_and_manifest_drift_fail_closed():
    with pytest.raises(ValueError,match="not ZIP"):
        mod.spreadsheet_probe(b"<html>wrong</html>","source.xlsx")
    with pytest.raises(ValueError,match="not OLE2"):
        mod.spreadsheet_probe(b"no","source.xls")
    with pytest.raises(ValueError,match="too many"):
        mod.object_candidates("1103",[{"name":f"{i}.xls"} for i in range(15)])
