"""QA-only source gate synthetic checks. Only special GIS workflow requires Shapely."""
import importlib.util
from pathlib import Path
import pytest
pytest.importorskip("shapely")
pytest.importorskip("pyproj")
HERE=Path(__file__).resolve().parents[1]
S=HERE/"research/climate-penguin/work/abandonment/palmer_L7_multiyear_source_gate_v1.py"
def m():
    s=importlib.util.spec_from_file_location("l7source",S)
    x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x

def test_QA_selection_is_predefined_not_spectral():
    x=m()
    assert x.SENSOR=="LE07"
    assert x.PRE==tuple(range(2003,2008))
    assert x.POST==tuple(range(2009,2014))
    assert x.MIN_YEARS==3 and x.MIN_SAME_POINTS==5
    base=lambda yr,item,date,mask:{"site_id":"LITC","image_year":str(yr),
        "item_id":item,"date":date,"status":"ok",
        "clear_25_bit_mask":str(mask),"breeding_season_start_year":str(yr-1)}
    a=[base(2006,"LE07_b","2006-03-10",7),
       base(2006,"LE07_a","2006-03-01",7),
       base(2006,"LE07_c","2006-02-15",1),
       base(2010,"LT05_wrong","2010-03-01",31),
       base(2009,"LE07_z","2009-02-28",3)]
    y=x.choose(a,(1<<25)-1)
    assert [z["item_id"] for z in y]==["LE07_a","LE07_z"]
    assert y[0]["selected_island_clear_points"]==3

def test_same_fixed_physical_positions_and_3year_gate():
    x=m()
    mask=(1<<7)-1
    rows=[]
    for yr in [2003,2004,2005,2009,2010,2011]:
        rows.append({"image_year":str(yr),"selected_island_clear_mask":mask})
    z=x.support(rows,mask)
    assert z["passes_site_source_gate"]
    assert z["same_fixed_point_count"]==7
    assert z["pre"]["years"]==3 and z["post"]["years"]==3
    rows[0]["selected_island_clear_mask"]=0
    zz=x.support(rows,mask)
    assert not zz["passes_site_source_gate"]

def test_calendar_day_handling_and_no_sensor_switch():
    x=m()
    assert x.nonleap_day("2008-02-29")==60
    assert x.nonleap_day("2007-03-01")==60
