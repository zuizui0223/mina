"""V29 source presence only. No animal numerical counts inspected."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
import audit_aadc_three_island_season_v29 as v
from openpyxl import Workbook

def fake():
    wb=Workbook()
    ws=wb.active;ws.title=v.SHEET_MAIN
    ws.append(["Original AADC monitoring description"])
    ws.append(["Season*","Béchervaise","Verner","Petersen","Date"])
    for y in range(1990,2000):
        ws.append([f"{y}/{(y+1)%100:02d}",10000+y,100+y,"" if y==1995 else 200+y])
    return wb,ws

def test_unambiguous_year_and_numeric_missing_rule():
    assert v.source_year("1991/92")==1991
    assert v.source_year("1991-1992")==1991
    assert v.source_year(1990)==1990
    assert v.source_year("1991/94") is None
    assert v.source_year("NA") is None
    assert v.count_present(0) and v.count_present("42")
    assert not v.count_present(None) and not v.count_present("no survey")

def test_original_pair_gate_from_date_metadata_not_count_magnitudes():
    book,ws=fake()
    sets,meta=v.season_table(ws,3,1990,2004,{
        "Béchervaise":1,"Verner":2,"Petersen":3})
    out=v.compare(sets)
    assert out["all_three"]["common_original_seasons"]==9
    assert out["all_three"]["strict_consecutive_annual_windows"]==7
    assert out["all_three"]["frozen_next_stage_support_pass"]
    assert meta["original_bird_count_magnitudes_inspected"]==0
    assert "10000" not in str(meta)

def test_duplicate_year_dropped_whole_and_not_zero():
    book,ws=fake()
    ws.append(["1995/96",1500,50,75])
    sets,meta=v.season_table(ws,3,1990,2004,{"Béchervaise":1,"Verner":2,"Petersen":3})
    assert meta["season_labels_with_duplicate_source_rows_excluded"]==[1995]
    assert 1995 not in sets["Béchervaise"]
    assert v.count_present("NA") is False

def test_header_shape_masks_hide_count_magnitude():
    book,ws=fake()
    masks=v.sheet_text_mask(ws,10)
    assert "10000" not in str(masks)
    assert "SEASON_START_1990" in str(masks)
    assert v.YEAR_MIN==1990 and v.YEAR_MAX==2004
