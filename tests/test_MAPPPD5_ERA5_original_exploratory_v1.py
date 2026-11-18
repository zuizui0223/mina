"""No network original outcome-cohort regression synthetic calibration."""
import importlib.util
from pathlib import Path
import pytest
pytest.importorskip("numpy")
pytest.importorskip("requests")
HERE=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/climate_penguin"
P=HERE/"fit_MAPPPD5_ERA5_original_exploratory_v1.py"
def get():
 s=importlib.util.spec_from_file_location("MAPPPD5_countclimate_model",P)
 obj=importlib.util.module_from_spec(s);s.loader.exec_module(obj);return obj

def test_fixed_effect_residualization_recovers_arbitrary_site_year_intercepts():
 m=get();rows=[]
 for i in range(8):
  for year in range(1992,2002):
   t=(i-3.5)*((year%3)-1) * .2 + .13*(year-1992)
   y=2.4*t+9*i+4*(year-1992)
   rows.append(dict(site_id=f"ID{i}",site_species=f"ID{i}|ADPE",
       era5_grid_id=f"G{i//2}",source_region="Victoria Land",species_id="ADPE",
       end_year=year,delta_September_ERA5_C=t,delta_log1p_nests=y))
 s=m.slope(rows,"delta_September_ERA5_C",["site_species","end_year"])
 assert s is not None and abs(s-2.4)<1e-9
 result=m.model_support(rows,"delta_September_ERA5_C",["site_species","end_year"])
 assert result["source_site_ids"]==8 and result["actual_ERA5_grid_ids"]==4
 assert result["leave_one_ERA5_grid_out_valid_refits"]==4
 assert abs(result["beta_delta_log1p_nests_per_plus1C_annual_environment_change"]-2.4)<1e-9

def test_small_species_group_returns_null_and_never_p_value():
 m=get();rows=[dict(site_id="ONLY",site_species="ONLY|CHPE",
        era5_grid_id="G",source_region="a",species_id="CHPE",
        end_year=y,delta_September_ERA5_C=.1*y,delta_log1p_nests=.7*y)
        for y in range(1991,2005)]
 r=m.model_support(rows,"delta_September_ERA5_C",["site_species"])
 assert r["beta_delta_log1p_nests_per_plus1C_annual_environment_change"] is None
 assert r["inferential_p_value"] is None
 assert r["calibrated_confidence_interval"] is None
