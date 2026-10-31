"""Source identifiability, no ecological effect fitting."""
import importlib.util
from pathlib import Path
FILE=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/climate_penguin/audit_MAPPPD5_same_source_species_v1.py"
def module():
 spec=importlib.util.spec_from_file_location("penguin_same_site",FILE)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def mk(site,sp,cite,year=2015):
 return {"site_id":site,"species_id":sp,"publisher_citekey":cite,
  "publisher_vantage":"ground","start_year":str(year),"end_year":str(year+1),
  "source_region":"Peninsula","era5_grid_id":"-64.75|-64.0",
  "delta_September_ERA5_C":"0.5","delta_AugNov_ERA5_C":"0.3",
  "delta_log1p_nests":"0.1","month_census_verified":"False",
  "physical_island_polygon_verified":"False"}
def test_source_coobservations_not_assumed_independent_species_effects():
 x=module()
 rows=[mk("A","ADPE","same"),mk("A","CHPE","same"),
       mk("B","ADPE","first"),mk("B","GEPE","second")]
 p,r=x.analyze(rows)
 assert r["all_cross_species_same_site_year_pair_rows"]==2
 assert r["strict_same_citation_and_vantage_pair_rows"]==1
 assert r["strict_unique_original_site_IDs"]==1
 assert r["direct_species_comparison_source_gate"] is False
 assert r["climate_species_interaction_fitted"] is False
 assert r["p_values"] is None
def test_same_weather_grid_does_not_vary_by_species_at_same_site_year():
 x=module();a,b=mk("A","ADPE","a"),mk("A","CHPE","a")
 b["delta_September_ERA5_C"]="0.9"
 try:
  x.analyze([a,b])
  assert False
 except ValueError as e:
  assert "identical ERA5" in str(e)
