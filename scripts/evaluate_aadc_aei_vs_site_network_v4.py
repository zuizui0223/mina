#!/usr/bin/env python3
"""V4 exploratory AADC original P/A: site-density vs independent AEI habitat.

Original AADC biology has been opened in V14 and V1/V2; this is a retrospective
model-comparison diagnostic, NOT a causal or prospectively independent test.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from pyproj import Transformer
import requests

from audit_aadc_original_workbook_headers_v11 import public_dataset_manifests
from join_aadc_original_site_occupancy_v13 import fetch_original_sources,rows_linked
from audit_aadc_geography_editions_v1 import parse_geo
from build_aadc_potential_site_network_v1 import site_point_network
from evaluate_aadc_site_option_network_p_a_v1 import (
    original_sample, C, CONTINUOUS as OLD_CONTINUOUS
)
from audit_aadc_site_option_v2_falsification import cohort,controls

MODELS=("M0_original_geography_area_effort",
        "M1_plus_original_10km_candidate_map_density",
        "M2_plus_independent_AEI_2km_habitat",
        "M3_site_map_density_plus_independent_AEI_habitat")
AEI_PREDICTORS=("log1p_nonanimal_AEI_area_ha_2km",
                "nonanimal_AEI_tier2_richness_2km")
CONTINUOUS=set(OLD_CONTINUOUS)|set(AEI_PREDICTORS)
COVERAGE_MIN_BLOCKS=3
COVERAGE_MIN_ROWS=50


def read_source_atlas(summary_file:Path,features_file:Path):
    summary=json.loads(summary_file.read_text(encoding="utf-8"))
    if summary.get("status")!="AADC_7785_INDEPENDENT_AEI_HABITAT_ATLAS_V3":
        raise ValueError("SOURCE_STOP independent source AEI habitat summary missing")
    actual=hashlib.sha256(features_file.read_bytes()).hexdigest()
    if actual!=summary["derived_7785_site_habitat_feature_CSV_SHA256"]:
        raise ValueError("SOURCE_STOP actual derived AEI habitat CSV SHA drift")
    if summary.get("source_original_AADC_2025_geographic_site_count")!=7785:
        raise ValueError("SOURCE_STOP original AADC cohort changed")
    if summary.get("original_AEI_raster_MD5")!="cde880d73f7f18b44aecf5690aa2dc92":
        raise ValueError("SOURCE_STOP AEI original raster bytes not verified")
    with features_file.open(newline="",encoding="utf-8") as file:
        records=list(csv.DictReader(file))
    if len(records)!=7785 or len(set(r["original_geographic_site_id"] for r in records))!=7785:
        raise ValueError("SOURCE_STOP original source geographic site features count/ID mismatch")
    clean=[]
    for r in records:
        ident=r["original_geographic_site_id"]
        raw_area=r["nonanimal_mapped_icefree_area_projected_ha"]
        raw_rich=r["nonanimal_tier2_habitat_richness"]
        yes=r["independently_mapped_habitat_coverage"]
        if yes not in ("True","False"):
            raise ValueError("SOURCE_STOP expected explicit independent habitat coverage flag")
        if yes=="True":
            area=float(raw_area)
            rich=float(raw_rich)
            if not (np.isfinite(area) and area>0 and np.isfinite(rich) and rich>=1):
                raise ValueError("SOURCE_STOP independently mapped AEI usable coverage inconsistent")
            excluded=int(r["outcome_label_linked_pixels_excluded"])
            if excluded<0:
                raise ValueError("SOURCE_STOP impossible original AEI excluded pixels")
            clean.append({
                "geog_site_id":ident,
                "log1p_nonanimal_AEI_area_ha_2km":float(np.log1p(area)),
                "nonanimal_AEI_tier2_richness_2km":rich,
                "source_AEI_habitat_covered":True,
            })
        else:
            if raw_area.strip() or raw_rich.strip():
                raise ValueError("SOURCE_STOP uncovered AEI class trait was fabricated")
            clean.append({
                "geog_site_id":ident,
                "log1p_nonanimal_AEI_area_ha_2km":np.nan,
                "nonanimal_AEI_tier2_richness_2km":np.nan,
                "source_AEI_habitat_covered":False,
            })
    return pd.DataFrame(clean),summary


def eligible_habitat_sample(source_data:pd.DataFrame, atlas:pd.DataFrame):
    if atlas.geog_site_id.duplicated().any():
        raise ValueError("SOURCE_STOP duplicate original geographic site in habitat atlas")
    joined=source_data.merge(
        atlas,on="geog_site_id",how="left",validate="many_to_one")
    if joined.geog_site_id.isna().any() or joined.source_AEI_habitat_covered.isna().any():
        raise ValueError("SOURCE_STOP original AADC survey site absent from habitat atlas")
    available=joined.loc[joined.source_AEI_habitat_covered].copy()
    if any(available[n].isna().any() for n in AEI_PREDICTORS):
        raise ValueError("SOURCE_STOP missing independent habitat metric in matched cohort")
    sample_qa={
        "source_original_P_A_rows_with_site_area_and_geography":len(source_data),
        "source_P_A_rows_with_independent_AEI_habitat":len(available),
        "source_distinct_sites_with_independent_AEI_habitat":int(available.geog_site_id.nunique()),
        "source_missing_habitat_rows_excluded_not_zero_filled":len(joined)-len(available),
        "only_non_animal_derived_AEI_classes_enter_predictors":True,
    }
    return available,sample_qa


def fit_heldout(training,held,names):
    raw=training[names].to_numpy(dtype=float)
    tst=held[names].to_numpy(dtype=float)
    if not len(raw) or not len(tst):
        raise ValueError("SAMPLE_STOP empty original source block split")
    median=np.nanmedian(raw,axis=0)
    median[~np.isfinite(median)]=0
    raw=np.where(np.isfinite(raw),raw,median)
    tst=np.where(np.isfinite(tst),tst,median)
    center=np.zeros(len(names))
    scale=np.ones(len(names))
    for i,key in enumerate(names):
        if key in CONTINUOUS:
            center[i]=np.mean(raw[:,i])
            scale[i]=max(float(np.std(raw[:,i])),1e-10)
    raw=(raw-center)/scale
    tst=(tst-center)/scale
    y=training.outcome.to_numpy(dtype=int)
    if len(set(y))<2:
        raise ValueError("MODEL_STOP one original field class in training split")
    w=training.weight.to_numpy(dtype=float)
    model=LogisticRegression(C=0.3,solver="lbfgs",max_iter=500,tol=1e-6)
    model.fit(raw,y,sample_weight=w/np.mean(w))
    return model.predict_proba(tst)[:,1]


def compare_models(ready:pd.DataFrame,programme:str):
    d=cohort(ready,programme)
    if d is None or d.block.nunique()<COVERAGE_MIN_BLOCKS or len(d)<COVERAGE_MIN_ROWS:
        return {
            "status":"STOP_AEI_SOURCE_COVERAGE_GEOGRAPHIC_SUPPORT",
            "original_covered_site_n":int(
                ready.loc[ready.source_programme.eq(programme)].site_id.nunique()),
            "new_ecological_effect_fitted":False
        }
    base=controls(d)
    cols={
        MODELS[0]:base,
        MODELS[1]:base+["log1p_neighbor_10km"],
        MODELS[2]:base+list(AEI_PREDICTORS),
        MODELS[3]:base+["log1p_neighbor_10km"]+list(AEI_PREDICTORS),
    }
    scores={k:{} for k in cols}
    logs={k:{} for k in cols}
    for block in sorted(d.block.unique()):
        train=d.loc[d.block.ne(block)]
        test=d.loc[d.block.eq(block)]
        y=test.outcome.to_numpy(dtype=int)
        w=test.weight.to_numpy(dtype=float)
        for model,names in cols.items():
            p=fit_heldout(train,test,names)
            scores[model][block]=float(np.average((y-p)**2,weights=w))
            p=np.clip(p,1e-9,1-1e-9)
            logs[model][block]=float(np.average(
                -(y*np.log(p)+(1-y)*np.log(1-p)),weights=w))
    means={k:float(np.mean(list(v.values()))) for k,v in scores.items()}
    meanlog={k:float(np.mean(list(v.values()))) for k,v in logs.items()}
    differences={}
    pairs={
        "source_candidate_density_beyond_M0":(MODELS[0],MODELS[1]),
        "AEI_habitat_beyond_M0":(MODELS[0],MODELS[2]),
        "AEI_habitat_beyond_candidate_density":(MODELS[1],MODELS[3]),
        "candidate_density_beyond_AEI_habitat":(MODELS[2],MODELS[3]),
    }
    required=int(np.ceil(2*len(scores[MODELS[0]])/3))
    for name,(base_id,plus_id) in pairs.items():
        per={b:scores[base_id][b]-scores[plus_id][b]
             for b in scores[base_id]}
        improvement=means[base_id]-means[plus_id]
        better=sum(x>0 for x in per.values())
        differences[name]={
            "macro_equal_spatial_block_Brier_gain":float(improvement),
            "geographic_blocks_with_lower_Brier":better,
            "minimum_directional_blocks":required,
            "exploratory_predictive_direction_supported":bool(
                improvement>0 and better>=required),
            "block_specific_Brier_gain":per,
        }
    return {
        "status":"EXPLORATORY_AEI_VS_CANDIDATE_SITE_NETWORK_SPATIAL_CV",
        "source_original_sites":int(d.site_id.nunique()),
        "source_species_site_histories":int(
            d.groupby(["site_id","species"]).ngroups),
        "source_P_A_rows":len(d),
        "eligible_250km_spatial_blocks":int(d.block.nunique()),
        "source_species_codes":sorted(d.species.unique()),
        "original_observed_presence_absence_rows":{
            str(k):int(v) for k,v in d.outcome.value_counts().items()
        },
        "matched_samples_models":list(cols),
        "equal_spatial_block_Brier_by_model":means,
        "equal_spatial_block_logloss_by_model":meanlog,
        "Brier_gains":differences,
        "original_site_history_weights_sum_to_independent_history_count":True,
        "causal_island_or_phylogenetic_function_effect_identified":False,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--atlas-summary",type=Path,required=True)
    parser.add_argument("--atlas-features",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    atlas,source_atlas=read_source_atlas(args.atlas_summary,args.atlas_features)
    with requests.Session() as session:
        manifests,index=public_dataset_manifests(session)
        originals,receipts=fetch_original_sources(session,manifests)
    _qa,surveys,geog=rows_linked(originals)
    old,_=parse_geo(originals["potential_geography_2021"],old=True)
    new,_=parse_geo(originals["potential_geography_2025"],old=False)
    if len(old)!=4884 or len(new)!=7785:
        raise ValueError("SOURCE_STOP original AADC geographical frame changed")
    original_geography_sha=receipts["potential_geography_2025"]["original_SHA256"]
    if original_geography_sha!=source_atlas["AADC_publisher_workbook_SHA256"]["potential_geography_2025"]["original_SHA256"]:
        raise ValueError("SOURCE_STOP original source geography mismatch between model and AEI atlas")
    converter=Transformer.from_crs(4326,3031,always_xy=True)
    locations=[]
    for site,r in new.items():
        x,y=converter.transform(r["lon"],r["lat"])
        locations.append({"site_id":site,"source_class":r["feature"],"x":x,"y":y})
    network,_=site_point_network(locations,set(old))
    data,qa=original_sample(surveys,geog,network)
    original_qa_record_n=len(data)
    data=data.rename(columns={"site_id":"geog_site_id"})
    ready,coverage=eligible_habitat_sample(data,atlas)
    ready=ready.rename(columns={"geog_site_id":"site_id"})
    cohort_reports={
        group:compare_models(ready,group) for group in ("ADELIE","FLYING")
    }
    result={
        "status":"AADC_AEI_INDEPENDENT_BREEDING_OPTIONS_V4_RETROSPECTIVE_BIOLOGY",
        "fixed_source_V3_habitat_atlas_CSV_SHA256":source_atlas["derived_7785_site_habitat_feature_CSV_SHA256"],
        "fixed_original_AEI_raster_MD5":source_atlas["original_AEI_raster_MD5"],
        "source_original_AADC_survey_and_site_workbooks_sha256":{
            k:v["original_SHA256"] for k,v in receipts.items()},
        "source_original_AADC_public_manifest_SHA256":index["source_sha256"],
        "source_original_P_A_filter_report":qa,
        "matched_habitat_coverage_report":coverage,
        "source_programme_results":cohort_reports,
        "ecological_inference_preregistered":False,
        "previous_AADC_V14_V1_V2_outcomes_already_seen":True,
        "source_potential_site_centres_not_independent_island_polygon_or_nests":True,
        "source_static_AEI_does_not_measure_historical_breeding_space":True,
        "NR_inferred_as_absence":False,
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",
                        encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))


if __name__=="__main__":
    main()
