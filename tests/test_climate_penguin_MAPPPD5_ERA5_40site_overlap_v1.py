"""Source-only climate support logic; no biological outcome or external requests."""
import importlib.util
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/"research/climate-penguin/work/climate_penguin/audit_MAPPPD5_ERA5_40site_overlap_v1.py"
def m():
 s=importlib.util.spec_from_file_location("macro_era5_overlap",P)
 x=importlib.util.module_from_spec(s);s.loader.exec_module(x);return x

def test_exact_source_pins_and_structural_limits():
 x=m()
 assert x.REQUIRED_PAIR_SHA=="dfb72e533ab1e14846cb6551f0e2a6aa90f007c955f0b19f9c90fca03aca6d14"
 assert x.REQUIRED_ERA5_SHA=="f2bad55bc9b714351b8bc30031b1518eece43138f77d4047657a3e145911e9a6"
 assert x.SITES.is_file()
 assert len([z for z in x.read(x.SITES) if z["cohort"]=="macro_40"])==40

def test_unpaired_years_not_joined_and_zero_months_not_imputed():
 x=m()
 roster=[{"site_id":f"ID{i}","latitude":"-64.7","longitude":"-64.0"} for i in range(40)]
 climate=[{"site_id":f"ID{i}","year":str(y),"month":str(mth),
           "complete_month":"True","air2m_mean_c":"-8.0",
           "returned_grid_latitude":"-64.75","returned_grid_longitude":"-64.0"}
          for i in range(40) for y in range(1991,2021) for mth in range(1,13)]
 def fakepair(i):
  return {"site_id":f"ID{i%40}","species_id":["ADPE","CHPE","GEPE"][i%3],
          "source_region":"Victoria Land","source_point_latitude":"-64.7",
          "source_point_longitude":"-64.0","start":"2005","end":"2006",
          "same_source_and_vantage":"True"}
 pairs=[fakepair(i) for i in range(771)]
 detail,gate=x.source_support(pairs,climate,roster)
 assert len(detail)==771
 assert all(z["paired_september_ERA5_complete"] for z in detail)
 assert gate["eligible_original_site_ids"]==40
 assert gate["actual_ERA5_grids_with_eligible_original_site_ids"]==1
 assert gate["chronological_pre_count_exposure_identifiable"] is False
 assert gate["physical_island_effect_identifiable"] is False
 # Provenance mismatch at one source candidate is not an eligible climate pair.
 pairs[0]["source_point_latitude"]="-63.0"
 detail,gate=x.source_support(pairs,climate,roster)
 assert gate["unmatched_fixed_coordinate_pairs"]==1
 assert gate["n_source_candidate_pairs_fitting_original_40_site_and_climate_window"]==770
