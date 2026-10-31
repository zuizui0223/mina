"""Synthetic paired species source model, no external original count opening."""
import importlib.util
from pathlib import Path
import pytest
pytest.importorskip("numpy")
S=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/climate_penguin/fit_MAPPPD5_matched_species_ERA5_v1.py"
def mod():
 spec=importlib.util.spec_from_file_location("paired_species_climate",S)
 o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o);return o

def test_site_and_year_fixed_effect_relative_species_slope():
 m=mod();rows=[]
 for i in range(5):
  for year in range(2005,2014):
   x=.15*(i-2)*(year%3-1)+.05*(year-2005)
   y=3*x+10*i+2*(year-2005)
   rows.append({"site_id":f"ID{i}","source_region":"A" if i<3 else "B",
     "grid":f"G{i//2}","end_year":year,
     "relative_growth":y,"delta_September_ERA5_C":x})
 z=m.model(rows,"delta_September_ERA5_C",True)
 assert z["status"]=="EXPLORATORY_COEFFICIENT_FITTED_NOT_CAUSAL"
 assert abs(z["per_1C_climate_coefficient"]-3)<1e-9
 assert z["p_value"] is None
 assert z["confidence_interval"] is None

def test_insufficient_site_region_remains_not_estimable():
 m=mod();rows=[{"site_id":"ONLY","source_region":"A",
    "grid":"GRID","end_year":year,
    "relative_growth":.2*year,"delta_September_ERA5_C":.4*year}
    for year in range(1991,2021)]
 z=m.model(rows,"delta_September_ERA5_C",False)
 assert z["status"]=="SOURCE_SUPPORT_BELOW_PREDECLARED_GROUP_GATE"
 assert z["per_1C_climate_coefficient"] is None
