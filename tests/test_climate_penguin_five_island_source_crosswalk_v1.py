"""Immutable source joins for the five Palmer islands, not a causal estimate."""
import csv
import json
import math
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]/"research/climate-penguin"
MERGED=BASE/"outputs/climate_penguin/palmer_five_island_observed_counts_static_maps_source_crosswalk_v1.csv"

def rows(path):
    with Path(path).open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def test_original_source_crosswalk_identity_and_no_temporal_leakage():
    x=rows(MERGED)
    assert len(x)==5 and len({r["site_id"] for r in x})==5
    assert len({r["source_land_fid"] for r in x})==5
    assert len({r["same_ERA5_grid_id"] for r in x})==1
    assert {r["same_ERA5_grid_id"] for r in x}=={"-64.75|-64"}
    assert set(r["site_id"] for r in x)=={"CHIS","CORM","HUMB","LITC","TORG"}
    assert all(r["climate_independent_island_exposure"]=="false" for r in x)
    assert all(r["map_is_annual_vegetation_data"]=="false" for r in x)
    assert all(r["counts_are_full_island_nesting_capacity"]=="false" for r in x)
    for r in x:
        land=float(r["land_mapped_km2"])*1e6
        footprint=float(r["original_2024_mapped_all_classes_union_m2"])
        assert land>0 and 0<=footprint<=land
        assert math.isclose(footprint/land,float(r["static_map_covered_land_fraction"]),abs_tol=1e-6)
    l=next(r for r in x if r["site_id"]=="LITC")
    assert int(l["nests_1991"])==497 and int(l["nests_2006"])==4
    assert int(l["nests_2007"])==0 and int(l["nests_2017"])==0
    assert float(l["land_mapped_km2"])==max(float(r["land_mapped_km2"]) for r in x)
    assert int(l["nests_1991"])==min(int(r["nests_1991"]) for r in x)
    assert sum(int(r["nests_2007"])==0 for r in x)==1
    assert sum(int(r["nests_2017"])>0 for r in x)==4

def test_ERA5_source_grid_receipt_frozen_and_not_island_warming_effect():
    j=json.loads((BASE/"ORIGINAL_PALMER_FIVE_ISLAND_ERA5_GRID_RECEIPT_20261029.json").read_text(encoding="utf-8"))
    x=j["ERA5_actual_grid_support"]
    assert x["n_original_island_site_locations"]==5
    assert x["n_actual_era5_nearest_grids"]==1
    assert x["daily_source_day_count"]==10958
    assert x["max_absolute_same_day_temperature_between_island_sites_c"]==0.0
    assert x["all_five_share_identical_original_era5_source_grid"] is True
    assert x["causal_warming_effect_fitted"] is False
    assert x["distinct_island_microclimate_exposures_measured"] is False
    d=j["source_calibrated_design_summary"]
    assert d["Litchfield_has_largest_mapped_land_area"] is True
    assert d["Litchfield_has_smallest_1991_observed_breeding_count"] is True
    assert d["warming_anthropogenic_attribution_or_penguin_induced_greening_identified"] is False

def test_publisher_count_1998_1999_disagreement_kept_as_source_warning():
    j=json.loads((BASE/"ORIGINAL_LITCHFIELD_PALMER_EVENT_RECEIPTS_20261029.json").read_text(encoding="utf-8"))
    assert [r["year"] for r in j["palmer_five_island"]["receipt"]["litchfield_official_overlap_1991_2012"]["discrepancies"]]==[1998,1999]
    assert j["palmer_five_island"]["receipt"]["design_stop"]["island_mediator_or_diD_identifiable"] is False
