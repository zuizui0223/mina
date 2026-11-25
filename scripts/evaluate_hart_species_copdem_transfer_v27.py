#!/usr/bin/env python3
"""V27 exploratory source-island-out-of-group penguin elevation/slope transfer.

Original BAS Hart identified nest points and independent public Copernicus
DEM DSM pixels from signed V26. Four sites nested in three candidate islands;
NO independent available habitat, nest outcome, or colonial competition fitted.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

from validate_bas_hart_original_multiisland_nest_points_v20 import (
    LOCALITIES,SPECIES,SITE_GAZETTEER_PARENT
)

PRIMARY=("ADELIE","CHINSTRAP")
MIN_LOCAL_TAXON=100
ORIGINAL_LOCALITY_ORDER=tuple(LOCALITIES)
ORIGINAL_ISLAND_GROUPS=tuple(sorted(set(SITE_GAZETTEER_PARENT.values())))
FIXED_C=.3


def valid_quantiles(x):
    a=np.asarray(x,dtype=float)
    a=a[np.isfinite(a)]
    return {
        "n":int(len(a)),
        "median":float(np.median(a)) if len(a) else None,
        "p10":float(np.percentile(a,10)) if len(a) else None,
        "p90":float(np.percentile(a,90)) if len(a) else None,
    }


def site_original_terrain(arrays,site):
    xy=np.asarray(arrays[site+"_xy"],dtype=float)
    labels=np.asarray(arrays[site+"_label"],dtype=np.uint8)
    elevation=np.asarray(arrays[site+"_DEM_elevation_m"],dtype=float)
    slope=np.asarray(arrays[site+"_DEM_slope_degrees"],dtype=float)
    if (xy.ndim!=2 or xy.shape[1]!=2 or
        len(xy)!=len(labels) or len(xy)!=len(elevation) or len(xy)!=len(slope)):
        raise ValueError("SOURCE_STOP source nest coordinate/terrain array identity drift")
    if not np.isfinite(xy).all():
        raise ValueError("GEOMETRY_STOP original nest point UTM location not finite")
    if not np.isin(labels,range(len(SPECIES))).all():
        raise ValueError("SOURCE_STOP original species code unknown")
    if np.isnan(elevation).mean()>.05 or np.isnan(slope).mean()>.05:
        raise ValueError("GEOGRAPHY_STOP >5% independent DEM missing at a frozen locality")
    if np.nanmin(slope)<0 or np.nanmax(slope)>90:
        raise ValueError("GEOGRAPHY_STOP independent slope outside physical 0–90 degrees")
    unique,reverse,count=np.unique(xy,axis=0,return_inverse=True,return_counts=True)
    keep=count[reverse]==1
    if np.mean(~keep)>=.1:
        raise ValueError("GEOGRAPHY_STOP duplicate mapped source nest points exceed V21 10% gate")
    xy=xy[keep]
    y=labels[keep]
    h=elevation[keep]
    sl=slope[keep]
    summary={
        "source_original_geo_coordinate_rows":len(labels),
        "original_coordinate_collision_source_nests_excluded":int(np.sum(~keep)),
        "original_source_point_n_after_collision_exclusion":len(y),
        "source_original_taxa_environment":{
            name:{
                "source_original_locations_n":int(np.sum(y==j)),
                "source_mapped_DEM_elevation_metres":valid_quantiles(h[y==j]),
                "source_mapped_DEM_slope_degrees":valid_quantiles(sl[y==j]),
            } for j,name in enumerate(SPECIES) if np.any(y==j)
        },
    }
    binary=np.isin(y,[0,1]) & np.isfinite(h) & np.isfinite(sl)
    xx=np.column_stack((h[binary],sl[binary]))
    yy=y[binary]
    species_count=[int(np.sum(yy==code)) for code in (0,1)]
    if any(n<MIN_LOCAL_TAXON for n in species_count):
        raise ValueError("SAMPLE_STOP source original Adélie/Chinstrap minimum of 100 per site failed")
    median=np.median(xx,axis=0)
    quartile=np.percentile(xx,[25,75],axis=0)
    iqr=quartile[1]-quartile[0]
    iqr=np.where(iqr>1e-7,iqr,1.)
    predictors=(xx-median)/iqr
    summary["original_A_C_source_nest_counts"]={
        PRIMARY[i]:species_count[i] for i in range(2)}
    summary["median_DSM_elevation_diff_Chinstrap_minus_Adelie_m"]=float(
        np.median(xx[yy==1,0])-np.median(xx[yy==0,0]))
    summary["median_DSM_slope_diff_Chinstrap_minus_Adelie_deg"]=float(
        np.median(xx[yy==1,1])-np.median(xx[yy==0,1]))
    summary["source_label_free_combined_AC_median_elev_slope"]=median.tolist()
    summary["source_label_free_combined_AC_IQR_elev_slope"]=iqr.tolist()
    summary["source_orthomosaic_full_survey_footprint_verified"]=False
    return predictors,yy,summary


def leave_one_island_terrain_transfer(site_predictors,site_labels):
    if sorted(site_predictors)!=sorted(ORIGINAL_LOCALITY_ORDER):
        raise ValueError("SAMPLE_STOP frozen four original localities changed")
    groups={k:SITE_GAZETTEER_PARENT[k] for k in ORIGINAL_LOCALITY_ORDER}
    unique=sorted(set(groups.values()))
    if len(unique)!=3:
        raise ValueError("SAMPLE_STOP source gazetteer island count changed")
    # Data records remain nested within original localities, then groups.
    records={}
    for island in unique:
        train=[k for k in ORIGINAL_LOCALITY_ORDER if groups[k]!=island]
        hold=[k for k in ORIGINAL_LOCALITY_ORDER if groups[k]==island]
        train_x=np.vstack([site_predictors[k] for k in train])
        train_y=np.concatenate([site_labels[k] for k in train])
        w=np.concatenate([
            np.full(len(site_labels[k]),0.,dtype=float) for k in train
        ])
        for parent in sorted(set(groups[k] for k in train)):
            subset=[k for k in train if groups[k]==parent]
            for k in subset:
                ii=train.index(k)
                mask=np.cumsum([0]+[len(site_labels[z]) for z in train])
                start,end=mask[ii],mask[ii+1]
                for code in (0,1):
                    select=site_labels[k]==code
                    w[start:end][select]=.5/(len(subset)*np.count_nonzero(select))
        if np.any(w<=0) or not np.isclose(np.sum(w),len(set(groups[k] for k in train))):
            raise ValueError("MODEL_STOP training source-island/site/taxon class weights inconsistent")
        classifier=LogisticRegression(C=FIXED_C,solver="lbfgs",max_iter=500)
        classifier.fit(train_x,train_y,sample_weight=w/np.mean(w))
        by_site={}
        for k in hold:
            y=np.asarray(site_labels[k],dtype=np.uint8)
            p=classifier.predict_proba(site_predictors[k])[:,1]
            balanced_brier=.5*float(np.mean((p[y==0])**2)) + .5*float(
                np.mean((1-p[y==1])**2))
            clip=np.clip(p,1e-12,1-1e-12)
            balanced_logloss=.5*float(np.mean(-np.log(1-clip[y==0]))) + .5*float(
                np.mean(-np.log(clip[y==1])))
            by_site[k]={
                "source_original_labelled_nests":len(y),
                "source_Adelie_nest_n":int(np.sum(y==0)),
                "source_Chinstrap_nest_n":int(np.sum(y==1)),
                "balanced_B0_intercept_0p5_Brier":.25,
                "balanced_B1_CopDEM_elevation_plus_slope_Brier":balanced_brier,
                "positive_Brier_gain_B0_minus_B1":.25-balanced_brier,
                "balanced_B1_logloss":balanced_logloss,
            }
        island_brier=float(np.mean([z["balanced_B1_CopDEM_elevation_plus_slope_Brier"] for z in by_site.values()]))
        records[island]={
            "original_source_heldout_locality_list":hold,
            "original_source_training_locality_list":train,
            "heldout_source_locality_Brier":by_site,
            "heldout_island_equal_source_locality_B1_Brier":island_brier,
            "heldout_island_equal_source_locality_B0_Brier":.25,
            "positive_Brier_gain":.25-island_brier,
            "source_coefficient_elevation_normalized":float(classifier.coef_[0,0]),
            "source_coefficient_slope_normalized":float(classifier.coef_[0,1]),
            "classifier_intercept":float(classifier.intercept_[0]),
            "unique_source_islands_in_training":len(set(groups[k] for k in train)),
        }
    gains=[v["positive_Brier_gain"] for v in records.values()]
    return {
        "original_source_parent_named_island_count":len(records),
        "original_localities_nested_within_heldout_islands":groups,
        "fixed_B0_class_balanced_Brier":.25,
        "fixed_CopDEM_species_terrain_ridge_strength_C":FIXED_C,
        "source_parent_island_heldout_cv_results":records,
        "source_island_equal_weighted_mean_Brier_gain":float(np.mean(gains)),
        "source_island_groups_with_positive_terrain_Brier_gain":sum(x>0 for x in gains),
        "source_three_island_exploratory_terrain_transfer_gate":bool(
            np.mean(gains)>0 and sum(x>0 for x in gains)>=2),
        "normalization_did_not_use_species_labels":True,
        "source_physical_island_parent_is_gazetteer_candidate_not_strict_GIS_ID":True,
        "raw_individual_nests_as_independent_island_replicates":False,
        "species_habitat_filter_causal_or_resource_competition_identified":False,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--v26",type=Path,required=True)
    ap.add_argument("--point-terrain",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    result={"status":"HOLD_HART_COPDEM_SPECIES_TERRAIN_V27",
            "source_terrain_island_causal_ecology_demonstrated":False}
    try:
        source=json.loads(args.v26.read_text(encoding="utf-8"))
        if source["status"]!="ORIGINAL_COPERNICUS_DEM30_TERRAIN_AT_HART_NEST_SITES_V26":
            raise ValueError("SOURCE_STOP original publisher DEM exposure result changed")
        digest=hashlib.sha256(args.point_terrain.read_bytes()).hexdigest()
        if digest!=source["derived_independent_environment_tied_to_original_nest_points_NPZ_SHA256"]:
            raise ValueError("SOURCE_STOP original V26 DEM/source position NPZ checksum changed")
        with np.load(args.point_terrain,allow_pickle=False) as archive:
            arrays={key:archive[key] for key in archive.files}
        if sorted(arrays)!=sorted(source["derived_environment_nest_point_array_keys"]):
            raise ValueError("SOURCE_STOP original V26 data array expected source keys changed")
        site_X={}
        site_y={}
        description={}
        for site in ORIGINAL_LOCALITY_ORDER:
            site_X[site],site_y[site],description[site]=site_original_terrain(arrays,site)
        response=leave_one_island_terrain_transfer(site_X,site_y)
        result={
            "status":"BAS_HART_INDEPENDENT_COPDEM_TERRAIN_SPECIES_TRANSFER_V27_EXPLORATORY",
            "original_source_dem_point_NPZ_SHA256":digest,
            "original_source_nest_count":source["source_original_colony_gps_points_all_sites_n"],
            "original_source_CopDEM_tile_references":source["source_original_dem_tiles"]["original_GLO30_tile_receipts"],
            "original_4_source_site_species_terrain_descriptors":description,
            "original_3_candidate_island_LOIO":response,
            "original_source_colonial_site_coverage_mask_verified":False,
            "source_full_available_vs_unavailable_nesting_land_contrast_observed":False,
            "source_spatial_terrain_resolution_coarser_than_original_nest_spacing":True,
            "source_original_2019_vs_2020_UAV_campaign_differs_across_islands":True,
            "independent_Antarctic_Treaty_area_islands_observed":0,
            "direct_interspecific_competition_or_coastal_barrier_causally_identified":False,
        }
    except Exception as ex:
        result["error_type"]=type(ex).__name__
        result["error"]=str(ex)[:1500]
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
