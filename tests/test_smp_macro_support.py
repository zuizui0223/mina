from pathlib import Path

from scripts.audit_smp_macro_support import audit


def _write(tmp_path: Path, rows: list[str]) -> Path:
    p=tmp_path/"smp.csv"
    p.write_text(
        "Species,SiteID,Site,MasterSite,Year,Method,Unit,Count,Accuracy,Estimate,Comments\n"
        + "\n".join(rows) + "\n",
        encoding="utf-8",
    )
    return p


def test_missing_row_is_not_zero_and_complete_year_requires_all_components(tmp_path):
    rows=[]
    for year in range(2000,2012):
        rows += [
            f"Kittiwake,A,A,Master,{year},1.1,AON,10,C,,",
            f"Kittiwake,B,B,Master,{year},1.1,AON,0,C,,",
        ]
        if year != 2005:
            rows.append(f"Kittiwake,C,C,Master,{year},1.1,AON,5,C,,")
    result=audit(_write(tmp_path,rows))
    panel=result["panels"][0]
    assert panel["n_components"]==3
    assert panel["explicit_zero_records"]==12
    assert panel["n_complete_years"]==11
    assert 2005 not in panel["complete_years"]
    assert panel["basic_support_gate_pass"] is True
    assert panel["final_eligible"] is False


def test_merged_comment_blocks_basic_support(tmp_path):
    rows=[]
    for year in range(2000,2012):
        for site in ("A","B","C"):
            comment="Total count after merging sites" if (site=="A" and year==2000) else ""
            rows.append(f"Kittiwake,{site},{site},Master,{year},1.1,AON,10,C,,{comment}")
    panel=audit(_write(tmp_path,rows))["panels"][0]
    assert panel["merged_or_aggregate_comment_rows"]==1
    assert panel["basic_support_gate_pass"] is False


def test_unit_inconsistency_blocks_basic_support(tmp_path):
    rows=[]
    for year in range(2000,2012):
        rows.append(f"Guillemot,A,A,Master,{year},1.1,IND,10,C,,")
        rows.append(f"Guillemot,B,B,Master,{year},1.1,IND,20,C,,")
        unit="AON" if year==2005 else "IND"
        rows.append(f"Guillemot,C,C,Master,{year},1.1,{unit},30,C,,")
    panel=audit(_write(tmp_path,rows))["panels"][0]
    assert sorted(panel["units"])==["AON","IND"]
    assert panel["basic_support_gate_pass"] is False
