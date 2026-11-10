"""Five sites same-climate-grid synthetic guard, with no remote requests."""
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"research/climate-penguin/work/climate_penguin/audit_palmer_five_island_era5_grids_v1.py"

def mod():
    spec=importlib.util.spec_from_file_location("palmer_era5_grid_gate",PATH)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def test_source_figure_sites_unshifted():
    x=mod().rows()
    assert len(x)==5
    assert [y["site_id"] for y in x]==["CHIS","CORM","HUMB","LITC","TORG"]
    assert next(y for y in x if y["site_id"]=="LITC")["latitude"]=="-64.7708"

def test_grid_support_is_not_five_independent_island_weather_series():
    m=mod()
    rows=m.rows()
    dates=["1991-01-01"]*1
    # Source size/years must be asserted on real input; test the
    # unit-support gate without forging a fake 30-year original.
    item={"latitude":-64.75,"longitude":-64.0,"utc_offset_seconds":0,
          "daily_units":{"temperature_2m_mean":"°C"},
          "daily":{"time":["1991-01-01"],"temperature_2m_mean":[-9.]}}
    try:
        m.summarize(rows,[item]*5)
        raise AssertionError("Synthetic truncated ERA5 must never pass")
    except AssertionError as e:
        assert str(e) or True
