from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from scripts.audit_smp_component_eligibility import audit


def test_outcome_blind_smp_gate_passes_structural_fixture(tmp_path: Path):
    rows=[]
    for site in ("101","102","103"):
        for year in range(2000,2012):
            rows.append({
                "SMP_RecordID":f"{site}-{year}",
                "Species":"Kittiwake",
                "SMP_MasterSite":"Example Master",
                "SMP_SiteCode":site,
                "SMP_SiteName":f"Section {site}",
                "SMP_PlotName":"Whole Colony",
                "StartDate":f"15/06/{year}",
                "Method":"1.1",
                "Count_unit":"AON",
                "Accuracy":"ACC",
                "EstimateType":"",
                "Comments":"",
                "Count":str(1000+year),  # must not enter the structural audit
            })
    path=tmp_path/"fixture.csv"
    pd.DataFrame(rows).to_csv(path,index=False)
    result=audit(path,min_components=3,min_complete=10,min_span=12)
    assert result["summary"]["eligible_panel_count"]==1
    assert result["summary"]["decision"]=="marginal"
    assert "Count" in result["header_count_like_columns_present_but_not_loaded"]
    text=json.dumps(result)
    assert "1000" not in text


def test_method_drift_fails_primary_panel(tmp_path: Path):
    rows=[]
    for site in ("201","202","203"):
        for year in range(2000,2012):
            rows.append({
                "Species":"Guillemot",
                "SMP_MasterSite":"Drift Master",
                "SMP_SiteCode":site,
                "SMP_PlotName":"Whole Colony",
                "StartDate":f"10/06/{year}",
                "Method":"1.1" if year<2006 else "1.2",
                "Count_unit":"IND",
                "Accuracy":"ACC",
                "Count":"999999",
            })
    path=tmp_path/"drift.csv"
    pd.DataFrame(rows).to_csv(path,index=False)
    result=audit(path,min_components=3,min_complete=10,min_span=12)
    assert result["summary"]["eligible_panel_count"]==0
    panel=result["panels"][0]
    assert panel["compatible_single_unit_method"] is False


def test_plot_rows_are_excluded_from_primary_master_site_route(tmp_path: Path):
    rows=[]
    for site in ("301","302","303"):
        for year in range(2000,2012):
            rows.append({
                "Species":"Kittiwake",
                "SMP_MasterSite":"Plot Master",
                "SMP_SiteCode":site,
                "SMP_PlotName":"Plot A",
                "StartDate":f"12/06/{year}",
                "Method":"1.1",
                "Count_unit":"AON",
                "Accuracy":"ACC",
                "Count":"123",
            })
    path=tmp_path/"plot.csv"
    pd.DataFrame(rows).to_csv(path,index=False)
    result=audit(path,min_components=3,min_complete=10,min_span=12)
    assert result["summary"]["eligible_panel_count"]==0
