"""Source-only, no-network guard for Landsat QA bit interpretation."""
import importlib.util
from pathlib import Path
root = Path(__file__).resolve().parents[1]
p = root / "research/climate-penguin/work/abandonment/palmer_landsat_local_qa_pilot.py"
s = importlib.util.spec_from_file_location("qa_pilot", p)
m = importlib.util.module_from_spec(s)
s.loader.exec_module(m)

def test_landsat_qa_flags():
    assert m.clear_land_qa(0)
    assert m.clear_land_qa(1 << 6)  # do not trust Clear bit 6 alone
    for bit in (0, 1, 3, 4, 5, 7):
        assert not m.clear_land_qa(1 << bit)
    assert 2008 in m.YEARS and len(m.GRID_M) == 5

def test_january_window_contract():
    q = m.build_source_query(2008, month=1)
    assert q["datetime"] == "2008-01-01T00:00:00Z/2008-01-31T23:59:59Z"
    d = m.build_source_query(2008)
    assert d["datetime"].startswith("2008-02-01")
    assert d["datetime"].endswith("2008-03-31T23:59:59Z")
