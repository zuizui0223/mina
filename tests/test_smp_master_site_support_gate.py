from __future__ import annotations

import csv
from pathlib import Path

import pytest
pytest.importorskip("pandas")

from scripts.gate_smp_master_site_support_v1 import analyze


def _write(path: Path, rows: list[dict[str, object]]) -> None:
    fields = [
        "Species","Country","SiteID","Site","MasterSite","Year",
        "Method","Unit","Accuracy","Estimate","Comments","Plot","Count",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def _base_rows(n_sites: int = 3, years=range(2000, 2010)):
    rows = []
    for s in range(1, n_sites + 1):
        for y in years:
            rows.append({
                "Species": "Northern Fulmar",
                "Country": "Scotland",
                "SiteID": f"S{s}",
                "Site": f"Site {s}",
                "MasterSite": "Synthetic Master",
                "Year": y,
                "Method": "1",
                "Unit": "AOS",
                "Accuracy": "C",
                "Estimate": "",
                "Comments": "",
                "Plot": "(Whole Colony)",
                "Count": 1000 + 10*s + y,  # must never appear in output
            })
    return rows


def test_three_sites_ten_complete_years_pass(tmp_path: Path):
    p = tmp_path / "smp.csv"
    _write(p, _base_rows())
    result = analyze(p)
    assert result["eligible_panel_count"] == 1
    panel = result["eligible_panels"][0]
    assert panel["n_sites"] == 3
    assert panel["n_complete_years"] == 10
    assert panel["first_complete_year"] == 2000
    assert panel["last_complete_year"] == 2009
    text = str(result)
    assert "3010" not in text
    assert "count magnitudes" in text


def test_two_sites_fail(tmp_path: Path):
    p = tmp_path / "smp.csv"
    _write(p, _base_rows(n_sites=2))
    result = analyze(p)
    assert result["eligible_panel_count"] == 0


def test_estimate_plot_and_merged_rows_are_not_primary(tmp_path: Path):
    rows = _base_rows()
    # Add a fourth apparent site with three kinds of disallowed records.
    for i, y in enumerate(range(2000, 2010)):
        row = {
            "Species": "Northern Fulmar",
            "Country": "Scotland",
            "SiteID": "S4",
            "Site": "Site 4",
            "MasterSite": "Synthetic Master",
            "Year": y,
            "Method": "1",
            "Unit": "AOS",
            "Accuracy": "C",
            "Estimate": "",
            "Comments": "",
            "Plot": "(Whole Colony)",
            "Count": 999,
        }
        if i % 3 == 0:
            row["Accuracy"] = "E"
            row["Estimate"] = "MID"
        elif i % 3 == 1:
            row["Plot"] = "4"
        else:
            row["Comments"] = "Total count after merging sites"
        rows.append(row)
    p = tmp_path / "smp.csv"
    _write(p, rows)
    result = analyze(p)
    assert result["eligible_panel_count"] == 1
    assert result["eligible_panels"][0]["retained_site_ids"] == ["S1", "S2", "S3"]


def test_method_drift_excludes_site(tmp_path: Path):
    rows = _base_rows(n_sites=4)
    for row in rows:
        if row["SiteID"] == "S4" and int(row["Year"]) >= 2005:
            row["Method"] = "2"
    p = tmp_path / "smp.csv"
    _write(p, rows)
    result = analyze(p)
    assert result["eligible_panel_count"] == 1
    assert result["eligible_panels"][0]["retained_site_ids"] == ["S1", "S2", "S3"]
