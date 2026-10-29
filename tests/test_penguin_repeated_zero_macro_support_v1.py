"""No synthetic extinct penguins invented when MAPPPD visits are missing."""
import importlib.util
from pathlib import Path
SCRIPT=Path(__file__).resolve().parents[1]/"research/climate-penguin/work/climate_penguin/audit_penguin_repeated_zero_macro_support_v1.py"
def load():
 sp=importlib.util.spec_from_file_location("penguin_zero_gate",SCRIPT)
 m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def test_actual_38_original_source_episodes_not_38_island_extinctions():
 m=load();rows,summary=m.audit()
 assert len(rows)==38
 assert summary["input_original_zero_episodes"]==38
 assert summary["original_source_species"]["ADPE"]["apparent_first_zero_episodes"]==8
 assert summary["original_source_species"]["CHPE"]["apparent_first_zero_episodes"]==21
 assert summary["original_source_species"]["GEPE"]["apparent_first_zero_episodes"]==4
 assert summary["original_source_species"]["EMPE"]["apparent_first_zero_episodes"]==1
 assert summary["original_source_species"]["MCPE"]["apparent_first_zero_episodes"]==4
 assert all(z["first_observed_zero_year"]>z["last_recorded_positive_year"] for z in rows)
 assert all(z["zero_visit_years_n"]>=2 for z in rows if z["repeat_zero_source_support"])
 assert all(z["Plantarctica_is_static_2024_composite"] for z in rows)
 assert not summary["source_panel_ready_for_ant_wide_causal_greening"]
 assert not summary["strict_island_status_qualified"]
 assert not summary["original_source_species"]["ADPE"]["passes_exploratory_macro_source_replication_floor"]

def test_litchfield_zero_snapshot_does_not_overwrite_original_official_reconstruction():
 m=load();rows,_=m.audit()
 l=[x for x in rows if x["site_id"]=="LITC" and x["species_id"]=="ADPE"]
 assert len(l)==1
 assert l[0]["last_recorded_positive_year"]==2005
 assert l[0]["first_observed_zero_year"]==2007
 assert l[0]["zero_visit_years_n"]==2
 assert l[0]["verified_colony_nest_polygon"] is False
