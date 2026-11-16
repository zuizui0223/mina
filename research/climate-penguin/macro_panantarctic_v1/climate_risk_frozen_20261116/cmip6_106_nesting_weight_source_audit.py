#!/usr/bin/env python3
"""Source-verified CMIP6 106 physical coordinates × genuine original nesting support.

Uses the previously published 106-location, three-model physical-only atlas.
Biology is fixed 2011–2020 actually counted sites, method-selected 2,456 record
MAPPPD source. This DOES NOT estimate Antarctic-wide future population or the
independently reported 265-series PC1 response. Repeated location_id/site_id
rows never count twice in the observed nesting-weight denominator.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
import numpy as np,pandas as pd
from pyproj import Geod

EXPECTED_ATLAS_ROWS=424
EXPECTED_UNIQUE_ATLAS_LOCATIONS=106
EXPECTED_ORIGINAL_SITE_IDS=595
COHORTS=("any_atlas_unique_site","macro_40_predeclared")
MAX_GEO_ERROR_KM=1.0
G=Geod(ellps="WGS84")
def h(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def calculate(source, inventory, atlas):
    assert len(inventory)==EXPECTED_ORIGINAL_SITE_IDS and inventory.site_id.is_unique
    assert len(source)==2456 and not source.duplicated(["site_id","species","season"]).any()
    assert len(atlas)==EXPECTED_ATLAS_ROWS and atlas.location_id.nunique()==EXPECTED_UNIQUE_ATLAS_LOCATIONS
    assert atlas.groupby(["experiment","period"]).location_id.nunique().eq(106).all()
    assert set(atlas.experiment)=={"ssp245","ssp585"}
    assert set(atlas.period)=={"2041-2060","2081-2100"}
    assert atlas.cohort.notna().all()
    assert atlas[['latitude','longitude','tas_change_mean_degC',
                 'siconc_change_mean_pp','sos_change_mean_native001',
                 'marine_max_model_cell_distance_km']].notna().all().all()
    assert set(atlas.marine_all_3_models_within_50km.unique())<={0,1}
    assert atlas.groupby("location_id").site_id.nunique().eq(1).all()
    assert atlas.groupby("location_id").latitude.nunique().eq(1).all()

    early=source.loc[source.season.between(2011,2020)]
    # Historical source is method-selected but multiple species medians
    # at one site are not synchronized to a shared count year.
    baseline=early.groupby(["site_id","species"],as_index=False).agg(
         n_observed_seasons=("season","nunique"),
         median_real_nests=("observed_nest_count","median"))
    assert (baseline.median_real_nests>=0).all()
    weights=baseline.groupby("site_id",as_index=False).agg(
         source_species_with_real_counts=("species","nunique"),
         sum_species_nesting_medians_NOT_synchronous=("median_real_nests","sum"),
         real_site_species_observation_seasons=("n_observed_seasons","sum"))
    assert weights.site_id.nunique()>200 and len(weights)<595
    weight_total=float(weights.sum_species_nesting_medians_NOT_synchronous.sum())
    assert weight_total>0
    locs=atlas.drop_duplicates("location_id")
    match=locs.merge(inventory[["site_id","latitude","longitude","source_region"]],
                     how="left",on="site_id",suffixes=("","_source"),validate="many_to_one")
    goodcoords=match.latitude_source.notna()
    mismatch=np.full(len(match),np.nan,dtype=float)
    if goodcoords.any():
        k=goodcoords.to_numpy()
        mismatch[k]=G.inv(match.loc[k,"longitude"].to_numpy(float),
                         match.loc[k,"latitude"].to_numpy(float),
                         match.loc[k,"longitude_source"].to_numpy(float),
                         match.loc[k,"latitude_source"].to_numpy(float))[2]/1000
    match["coords_difference_km"]=mismatch
    match["coords_match_source_1km"]=match.coords_difference_km.le(MAX_GEO_ERROR_KM)
    # Pick exactly one original physical coordinate for each original site ID.
    # The rule uses source coordinate discrepancy and predeclared cohort, and
    # is independent of biological counts or future scenario outcome.
    match["cohort_precedence"]=(match.cohort!="macro_40").astype(int)
    match=match.sort_values(["site_id","coords_match_source_1km","coords_difference_km",
                              "cohort_precedence","location_id"],
                            ascending=[True,False,True,True,True])
    match["selected_one_location_per_site"]=~match.site_id.duplicated()
    match["usable_source_coords"]=match.coords_match_source_1km & match.selected_one_location_per_site
    choice=match.loc[match.usable_source_coords,
                     ["location_id","site_id","cohort","source_region","coords_difference_km"]].copy()
    choice=choice.merge(weights,on="site_id",how="left",validate="one_to_one")
    choice["has_real_baseline_nests"]=choice.sum_species_nesting_medians_NOT_synchronous.notna()
    unique_counts=choice.loc[choice.has_real_baseline_nests].copy()
    if unique_counts.site_id.duplicated().any():raise ValueError("Biological sites multiplied")
    count_total_unique=float(unique_counts.sum_species_nesting_medians_NOT_synchronous.sum())

    records=atlas.merge(choice,on=["location_id","site_id","cohort"],how="left",
                        suffixes=("","_joined"),validate="many_to_one")
    records["original_source_coords_matched"]=records.coords_difference_km.notna()
    records["actual_2011_2020_counts_available"]=records.has_real_baseline_nests.fillna(False)
    # Distinct cohort filters are source-only, not selected on physical delta.
    summary=[]
    for experiment in ("ssp245","ssp585"):
      for period in ("2041-2060","2081-2100"):
        frame=records[(records.experiment==experiment)&(records.period==period)].copy()
        assert len(frame)==106
        for cohort in COHORTS:
          subset=frame if cohort==COHORTS[0] else frame[frame.cohort=="macro_40"]
          for support in ("any_original_marine_cell","all_models_within_50km"):
            a=subset[subset.actual_2011_2020_counts_available].copy()
            if support=="all_models_within_50km":
                a=a[a.marine_all_3_models_within_50km.eq(1)]
            # Exactly one physical row per original site from choice, by construction.
            assert a.site_id.is_unique
            w=a.sum_species_nesting_medians_NOT_synchronous.to_numpy(float)
            full_nest_fraction=float(w.sum()/weight_total) if weight_total>0 else None
            q={"cohort":cohort,"experiment":experiment,"period":period,
               "physical_support":support,
               "n_original_physical_locations":len(subset),
               "n_original_biologically_counted_unique_sites":len(a),
               "n_source_regions":int(a.source_region.nunique()),
               "n_original_marine_fingerprints":int(a.marine_fingerprint.nunique()),
               "n_source_sites_with_any_2011_2020_counts":len(weights),
               "source_nest_median_weight_fraction":full_nest_fraction,
               "selected_site_equal_mean_sic_delta_pp":float(a.siconc_change_mean_pp.mean()) if len(a)>0 else None,
               "selected_site_nest_weighted_mean_sic_delta_pp":float(np.average(a.siconc_change_mean_pp,weights=w)) if w.sum()>0 else None,
               "selected_site_equal_mean_tas_delta_degC":float(a.tas_change_mean_degC.mean()) if len(a)>0 else None,
               "selected_site_nest_weighted_mean_tas_delta_degC":float(np.average(a.tas_change_mean_degC,weights=w)) if w.sum()>0 else None,
               "selected_site_equal_mean_sos_delta_source_units":float(a.sos_change_mean_native001.mean()) if len(a)>0 else None,
               "selected_site_nest_weighted_mean_sos_delta_source_units":float(np.average(a.sos_change_mean_native001,weights=w)) if w.sum()>0 else None,
               "n_models_agree_all3_sic_decrease":int((a.siconc_decrease_models==3).sum()),
               "source_only_selected_nest_weight_base_not_full_antarctic_population":True}
            summary.append(q)
    assert len(summary)==16
    # Count only unique locations/colony ids in original observation rosters.
    qc={"atlas_source_locations":106,
        "atlas_site_ids_unadjusted":int(locs.site_id.nunique()),
        "atlas_duplicate_site_id_locations":int(len(locs)-locs.site_id.nunique()),
        "n_atlas_source_site_ids_missing_from_595":int((~goodcoords).sum()),
        "n_location_ids_not_matching_original_595_coords_1km":int((~match.coords_match_source_1km).sum()),
        "n_site_ids_with_exactly_one_matched_original_location":int(len(choice)),
        "n_matched_source_site_ids_with_2011_2020_counts":int(len(unique_counts)),
        "n_original_observed_source_sites_2011_2020":int(len(weights)),
        "sum_observed_species_median_nests_ALL_counted_source_sites":weight_total,
        "sum_observed_species_median_nests_unique_atlas_matched":count_total_unique,
        "source_site_weight_fraction_exact_unique_atlas":count_total_unique/weight_total,
        "dataset_is_a_selected_106_physical_atlas_not_595_site_projection":True,
        "n_atlas_cohort_macro_40":int((locs.cohort=="macro_40").sum()),
        "does_not_estimate_forthcoming_population_nests":True,
        "does_not_confirm_surveyed_265_source_response":True,
        "source_duplicate_site_id_effectively_eliminated":True}
    return summary,records,match,qc

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-counts",required=True,type=Path)
    p.add_argument("--original-site-inventory",required=True,type=Path)
    p.add_argument("--existing-cmip6-atlas",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    counts=pd.read_csv(a.source_counts)
    inventory=pd.read_csv(a.original_site_inventory)
    atlas=pd.read_csv(a.existing_cmip6_atlas)
    result,records,locations,qc=calculate(counts,inventory,atlas)
    pd.DataFrame(result).to_csv(a.output/"106_atlas_40macro_real_nest_weighted_exposure.csv",index=False)
    records.to_csv(a.output/"106_source_atlas_location_and_actual_count_coverage.csv",index=False)
    locations.to_csv(a.output/"106_location_coordinate_identity_audit.csv",index=False)
    verdict={"status":"SELECTED_CMIP6_ATLAS_PHYSICAL_ONLY_NOT_PAN_ANTARCTIC",
             "source_sha256":{"counts":h(a.source_counts),"site_inventory":h(a.original_site_inventory),"published_physical_atlas":h(a.existing_cmip6_atlas)},
             "source_quality":qc,"scenarios":result,"no_extrapolated_whole_antarctic_nest_change":True,
             "no_265_regression_coefficient_transferred":True,
             "threshold_50km_is_model_grid_distance_not_biological_foraging_radius":True,
             "reanalysis_sos_units_are_original_source_units":True}
    (a.output/"106_selected_source_exposure_gate.json").write_text(json.dumps(verdict,ensure_ascii=False,indent=2)+"\n")
    print("SOURCE_106_NEST_EXPOSURE_AUDIT="+json.dumps({"quality":qc,"rows":result},ensure_ascii=False))
if __name__=="__main__":main()
