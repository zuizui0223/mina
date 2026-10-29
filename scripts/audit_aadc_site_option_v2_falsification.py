#!/usr/bin/env python3
"""V2 falsification of exploratory Antarctic potential-site density signal.

Existing AADC biological outcomes V14/V1 already examined. This is POST-RESULT,
not a preregistered causal test. No radius selection or source relabeling.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer
import requests
from scipy.spatial import cKDTree

from audit_aadc_original_workbook_headers_v11 import public_dataset_manifests
from join_aadc_original_site_occupancy_v13 import fetch_original_sources, rows_linked
from audit_aadc_geography_editions_v1 import parse_geo
from build_aadc_potential_site_network_v1 import site_point_network
from evaluate_aadc_site_option_network_p_a_v1 import (
    BLOCK_M, C, CONTINUOUS, MIN_BLOCK_SITES, MIN_BLOCKS, MIN_ROWS,
    fit_predict, original_sample
)

SEED = 20261026
N_PLACEBO = 31
ORIGINAL_BRIER = {
    "ADELIE":(0.2772532232306087,0.2665502779259641),
    "FLYING":(0.3583902619521141,0.3122426504175746),
}
BASE = [
    "year_scaled", "latitude", "longitude_sin", "longitude_cos", "log_area",
    "island", "log_station_distance", "station_distance_missing",
    "vantage_A", "vantage_S", "expert_occurrence", "expert_species",
    "expert_site", "original_site_id_in_2021",
]


def cohort(data:pd.DataFrame, programme:str):
    """Identical block/site-history filters as frozen V1."""
    sample = data.loc[data.source_programme.eq(programme)].copy()
    site_count = sample.groupby("block").site_id.nunique()
    allowed = set(site_count[site_count >= MIN_BLOCK_SITES].index)
    sample = sample.loc[sample.block.isin(allowed)].copy()
    if len(sample)<MIN_ROWS or sample.block.nunique()<MIN_BLOCKS:
        return None
    all_species=sorted(sample.species.unique())
    for name in all_species[1:]:
        sample[f"species_{name}"]=sample.species.eq(name).astype(float)
    sample["weight"] = 1 / sample.groupby(
        ["site_id","species"]).site_id.transform("size")
    return sample


def controls(sample:pd.DataFrame, lean:bool=False):
    remaining=[x for x in BASE
               if not lean or x not in (
                   "expert_occurrence","expert_species","expert_site")]
    return remaining + [
        f"species_{name}" for name in sorted(sample.species.unique())[1:]
    ]


def heldout_score(sample:pd.DataFrame, names:list[str]):
    """Same V1 leave-one-250km-block-out weighted Brier calculation."""
    by_block={}
    by_block_logloss={}
    for block in sorted(sample.block.unique()):
        train=sample.loc[sample.block.ne(block)]
        test=sample.loc[sample.block.eq(block)]
        y_train=train.outcome.to_numpy(dtype=int)
        w_train=train.weight.to_numpy(dtype=float)
        y_test=test.outcome.to_numpy(dtype=int)
        w_test=test.weight.to_numpy(dtype=float)
        if len(np.unique(y_train))!=2:
            raise ValueError("MODEL_STOP historical fold training single P/A class")
        prediction=fit_predict(train,test,y_train,w_train,names)
        by_block[block]=float(np.average(
            (y_test-prediction)**2,weights=w_test
        ))
        p=np.clip(prediction,1e-9,1-1e-9)
        by_block_logloss[block]=float(np.average(
            -(y_test*np.log(p)+(1-y_test)*np.log(1-p)),weights=w_test
        ))
    return {
        "Brier_by_block":by_block,
        "Brier_equal_block_mean":float(np.mean(list(by_block.values()))),
        "logloss_equal_block_mean":float(np.mean(list(by_block_logloss.values())))
    }


def comparison(sample:pd.DataFrame, extra:str, lean:bool=False,
               baseline:dict|None=None):
    base=controls(sample,lean)
    B0=baseline if baseline is not None else heldout_score(sample,base)
    B1=heldout_score(sample,base+[extra])
    changes={
        k:float(B0["Brier_by_block"][k]-B1["Brier_by_block"][k])
        for k in B0["Brier_by_block"]
    }
    return {
        "B0":B0, "B1":B1,
        "Brier_improvement_B0_minus_B1":B0["Brier_equal_block_mean"]-
                                        B1["Brier_equal_block_mean"],
        "spatial_blocks_with_lower_Brier":sum(x>0 for x in changes.values()),
        "spatial_blocks":len(changes),
        "improvement_by_spatial_block":changes,
        "source_site_n":int(sample.site_id.nunique()),
        "observation_n":len(sample),
        "one_site_species_history_total_weight_one":True,
    }


def historical_2021_point_neighbor_counts(old:dict,site_ids:set):
    """2021 geographic frame uses all its 4,884 original points as references."""
    transformer=Transformer.from_crs(4326,3031,always_xy=True)
    keys=sorted(old)
    xy=np.array([transformer.transform(old[k]["lon"],old[k]["lat"])
                 for k in keys],dtype=float)
    if not np.isfinite(xy).all():
        raise ValueError("GEOMETRY_STOP invalid original historical candidate coords")
    if not site_ids.issubset(set(old)):
        raise ValueError("SOURCE_STOP 2021 reference cohort missing original ID")
    neighbors=cKDTree(xy).query_ball_point(xy,r=10000,return_length=True)-1
    return {key:int(n) for key,n in zip(keys,neighbors) if key in site_ids}


def shuffle_site_fixed_within_source_groups(sample:pd.DataFrame,rng):
    """Shuffle one site-level scalar; preserve block, island class and source era."""
    frame=sample[[
        "site_id","block","island","original_site_id_in_2021",
        "log1p_neighbor_10km"
    ]].drop_duplicates("site_id")
    if frame.site_id.nunique()!=len(frame):
        raise ValueError("SOURCE_STOP site attributes drift within observations")
    assigned={}
    eligible=0
    for _keys,part in frame.groupby(
        ["block","island","original_site_id_in_2021"],dropna=False):
        ids=part.site_id.to_list()
        values=part.log1p_neighbor_10km.to_numpy(dtype=float)
        if len(values)>1:
            indices=rng.permutation(len(values))
            shuffled=values[indices]
            eligible+=len(ids)
        else:
            shuffled=values
        for ident,v in zip(ids,shuffled):
            assigned[ident]=float(v)
    permuted=sample.copy()
    permuted["permuted_10km"]=permuted.site_id.map(assigned)
    if permuted.permuted_10km.isna().any():
        raise ValueError("SOURCE_STOP site-level shuffle introduced NA")
    originals=frame.set_index("site_id").log1p_neighbor_10km
    changed=sum(abs(assigned[k]-float(v))>1e-12 for k,v in originals.items())
    return permuted,{
        "sites_in_non_singleton_source_groups":eligible,
        "site_ids_with_numerically_changed_covariate":changed,
        "fraction_sites_with_changed_covariate":changed/len(frame)
    }


def shuffled_placebo(sample:pd.DataFrame,observed:dict,replicates=N_PLACEBO,
                     seed=SEED):
    """Exploratory local-map diagnostic, not a p-value."""
    rng=np.random.default_rng(seed)
    b0=observed["B0"]["Brier_equal_block_mean"]
    true_gain=observed["Brier_improvement_B0_minus_B1"]
    scores=[]
    effective=[]
    for i in range(replicates):
        variant,diag=shuffle_site_fixed_within_source_groups(sample,rng)
        scored=heldout_score(variant,controls(variant)+["permuted_10km"])
        scores.append(b0-scored["Brier_equal_block_mean"])
        effective.append(diag["fraction_sites_with_changed_covariate"])
    arr=np.asarray(scores,dtype=float)
    return {
        "status":"POST_RESULT_SOURCE_MAP_NEGATIVE_CONTROL_ONLY",
        "fixed_seed":seed,"site_level_replicates":replicates,
        "site_shuffle_nested_in":"250km block x source class x 2021-reference-membership",
        "shuffled_effective_changed_site_fraction_median":float(np.median(effective)),
        "shuffled_effective_changed_site_fraction_min":float(np.min(effective)),
        "shuffle_testability_gate_25pct_pass":bool(np.median(effective)>=0.25),
        "observed_original_Brier_gain":true_gain,
        "permuted_Brier_gain_median":float(np.median(arr)),
        "permuted_Brier_gain_p10":float(np.percentile(arr,10)),
        "permuted_Brier_gain_p90":float(np.percentile(arr,90)),
        "exploratory_empirical_observed_gain_percentile":float(np.mean(arr<=true_gain)),
        "exploratory_number_permutations_gain_at_least_observed":int(
            np.sum(arr>=true_gain)),
        "scientific_p_value_or_causal_effect_estimated":False,
    }


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    with requests.Session() as session:
        manifest,manifest_info=public_dataset_manifests(session)
        original,receipts=fetch_original_sources(session,manifest)
    _sourceqa,surveys,geog=rows_linked(original)
    older,qaold=parse_geo(original["potential_geography_2021"],old=True)
    newer,qanew=parse_geo(original["potential_geography_2025"],old=False)
    if len(older)!=4884 or len(newer)!=7785:
        raise ValueError("SOURCE_STOP original site geography editions changed")
    tf=Transformer.from_crs(4326,3031,always_xy=True)
    locations=[]
    for site,g in newer.items():
        x,y=tf.transform(g["lon"],g["lat"])
        locations.append({"site_id":site,"source_class":g["feature"],
                          "x":x,"y":y})
    network,_netmeta=site_point_network(locations,set(older))
    data,_sample=original_sample(surveys,geog,network)

    report={
        "status":"AADC_10KM_OPTION_NETWORK_V2_POST_RESULT_FALSIFICATION",
        "biological_outcomes_previously_viewed":True,
        "original_2025_site_reference_count":len(newer),
        "original_2021_site_reference_count":len(older),
        "original_source_hashes":{k:v["original_SHA256"]
                                  for k,v in receipts.items()},
        "original_manifest_sha256":manifest_info["source_sha256"],
        "diagnostics":{}
    }
    for programme in ("ADELIE","FLYING"):
        sample=cohort(data,programme)
        if sample is None:
            report["diagnostics"][programme]={
                "status":"STOP_ORIGINAL_PROGRAMME_SAMPLE_SUPPORT"}
            continue
        original_replay=comparison(sample,"log1p_neighbor_10km")
        expect=ORIGINAL_BRIER[programme]
        observed=(
            original_replay["B0"]["Brier_equal_block_mean"],
            original_replay["B1"]["Brier_equal_block_mean"]
        )
        if not all(abs(a-b)<=1e-6 for a,b in zip(observed,expect)):
            raise ValueError(
                f"REPLAY_STOP previous V1 original result mismatch: {programme} {observed}"
            )
        lean=comparison(sample,"log1p_neighbor_10km",lean=True)
        shared_ids=set(older)&set(newer)
        shared=sample.loc[sample.site_id.isin(shared_ids)].copy()
        historic=cohort(shared,programme) if len(shared) else None
        if historic is not None:
            historic_oldcounts=historical_2021_point_neighbor_counts(
                older,set(historic.site_id))
            historic["log1p_historical_2021_neighbor_10km"]=historic.site_id.map(
                {k:math.log1p(v) for k,v in historic_oldcounts.items()})
            fixed_base=heldout_score(historic,controls(historic))
            old_2021_ref=comparison(
                historic,"log1p_historical_2021_neighbor_10km",
                baseline=fixed_base)
            new_2025_ref=comparison(
                historic,"log1p_neighbor_10km",baseline=fixed_base)
            edition={
                "status":"COMMON_2021_SITE_IDS_HISTORICAL_FRAME_CHALLENGE",
                "original_shared_cohort_source_sites":int(historic.site_id.nunique()),
                "2025_density_on_shared_cohort":new_2025_ref,
                "2021_density_on_identical_shared_cohort":old_2021_ref,
                "2021_reference_point_total":len(older),
                "historical_geo_coordinates_only_no_animal_data_in_predictor":True,
            }
        else:
            edition={"status":"STOP_SHARED_HISTORICAL_SITE_SPATIAL_SUPPORT"}
        placebo=shuffled_placebo(
            sample,original_replay,
            seed=SEED+(0 if programme=="ADELIE" else 1))
        report["diagnostics"][programme]={
            "original_v1_replay_exact":True,
            "original_v1_replay":original_replay,
            "R1_lean_survey_and_geography_controls":lean,
            "R2_2021_historical_geographic_frame":edition,
            "R3_stratified_site_level_density_shuffle":placebo,
        }
    report.update({
        "P_A_NR_handling":"Only explicit P/A with V13 exact certainty; NR never zero",
        "causation_identified":False,
        "exploratory_after_positive_v1":True,
        "retuning_after_diagnostics_permitted":False,
    })
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",
                     encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))


if __name__=="__main__":
    main()
