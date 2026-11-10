"""Deterministic, source-independent tests for spatially matched QA-pair selection."""
import importlib.util
from pathlib import Path
path=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/abandonment/palmer_january_common_qa.py"
spec=importlib.util.spec_from_file_location("qa_spatial",path)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_same_epsg3031_grid_and_qa_choice():
    assert len(m.OFFSETS_M)==25
    assert len(set(m.OFFSETS_M))==25
    a=[{"status":"ok","item_id":"a","date":"2007-01-05","clear_points":[0,1,2]},
       {"status":"ok","item_id":"b","date":"2007-01-11","clear_points":[2]}]
    b=[{"status":"ok","item_id":"c","date":"2008-01-15","clear_points":[0,2]},
       {"status":"ok","item_id":"d","date":"2008-01-12","clear_points":[2]}]
    pairs=m.choose_best_pair(a,b)
    assert len(pairs)==4
    assert pairs[0]["before_id"]=="a" and pairs[0]["after_id"]=="c"
    assert pairs[0]["same_grid_clear_points"]==2
    assert pairs[0]["indices"]==[0,2]
    assert sum(p["same_grid_clear_points"] for p in pairs)==5
    assert m.choose_best_pair([],b)==[]
