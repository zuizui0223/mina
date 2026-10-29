#!/usr/bin/env python3
"""Exploratory AADC original P/A spatial-CV using independently built site network.

The earlier V14 AADC outcomes were already examined: this is not blind
confirmation. Models are separate for ADP and seven flying source species.
No environmental causal, competition or dispersal interpretation is implied.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer
import requests
from sklearn.linear_model import LogisticRegression

from audit_aadc_original_workbook_headers_v11 import public_dataset_manifests
from join_aadc_original_site_occupancy_v13 import fetch_original_sources,rows_linked
from audit_aadc_geography_editions_v1 import parse_geo
from build_aadc_potential_site_network_v1 import site_point_network
from audit_aadc_penguin_skua_joint_search_v15 import season_valid, direct_eligible

# Preserve the seven original flying-species codes from the frozen V14 sample.
FLYING = frozenset({"SGP", "SK", "AP", "CP", "SF", "SP", "WSP"})


def select_unique_source_eligible(surveys):
    """Same strict V15/V1 source-group rule, without unrelated rock-GIS imports."""
    from collections import defaultdict
    groups = defaultdict(list)
    for row in surveys:
        species = str(row.get("species_code", "")).strip()
        programme = str(row.get("source_study", "")).strip()
        site = str(row.get("geog_site_id", "")).strip()
        season = str(row.get("season", "")).strip()
        if not site or species not in (FLYING | {"ADP"}) or not season_valid(season):
            continue
        if species == "ADP" and programme != "penguin_original_search":
            continue
        if species in FLYING and programme != "flying_seabird_original_search":
            continue
        groups[(site,species,season,programme)].append(row)
    return [rows[0] for rows in groups.values()
            if len(rows) == 1 and direct_eligible(rows[0])]


BLOCK_M=250000
MIN_BLOCK_SITES=5
MIN_BLOCKS=3
MIN_ROWS=50
C=0.3
PRIMARY_NEIGHBORS="10km"
RADII=("10km","2km","50km")
CONTINUOUS=(
    "year_scaled","latitude","longitude_sin","longitude_cos",
    "log_area","log_station_distance","log1p_neighbor_10km",
    "log1p_neighbor_2km","log1p_neighbor_50km"
)


def original_sample(survey,geo,network):
    """Original V13 P/A source filters, original site identifiers and survey stage."""
    valid=select_unique_source_eligible(survey)
    candidate={r["geog_site_id"]:r for r in geo}
    net={r["geog_site_id"]:r for r in network}
    rows=[]
    trans=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    invalid=Counter()
    for r in valid:
        sid=r["geog_site_id"]
        g=candidate.get(sid)
        n=net.get(sid)
        if not g or not n:
            invalid["NO_GEO_NETWORK_MATCH"]+=1
            continue
        try:
            area=float(g["geog_site_area"])
            lat=float(g["latitude"])
            lon=float(g["longitude"])
            if not (np.isfinite(area) and area>0 and -90<=lat<=-60 and -180<=lon<=180):
                invalid["AREA_OR_COORD"]+=1
                continue
        except (ValueError,TypeError):
            invalid["AREA_OR_COORD"]+=1
            continue
        if g["geog_site_feature"] not in ("island","continent"):
            invalid["SITE_CLASS"]+=1
            continue
        sp=r["species_code"]
        programme="ADELIE" if sp=="ADP" else "FLYING"
        year=int(r["season"][:4])
        x,y=trans.transform(lon,lat)
        region=f"{math.floor(x/BLOCK_M)}_{math.floor(y/BLOCK_M)}"
        station_value=pd.to_numeric(r.get("source_distance_station",""),errors="coerce")
        station_missing=not np.isfinite(station_value) or station_value<0
        lon_rad=math.radians(lon)
        rows.append({
            "site_id":sid,
            "species":sp,
            "source_programme":programme,
            "block":region,
            "year_scaled":(year-2000)/20,
            "latitude":lat,
            "longitude_sin":math.sin(lon_rad),
            "longitude_cos":math.cos(lon_rad),
            "log_area":math.log10(area),
            "island":float(g["geog_site_feature"]=="island"),
            "log_station_distance":math.log1p(station_value) if not station_missing else np.nan,
            "station_distance_missing":float(station_missing),
            "vantage_A":float(r["vantage"]=="A"),
            "vantage_S":float(r["vantage"]=="S"),
            "expert_occurrence":float(r["occurrence_expert_validation"]=="Y"),
            "expert_species":float(r["species_expert_validation"]=="Y"),
            "expert_site":float(r["site_expert_validation"]=="Y"),
            "original_site_id_in_2021":float(n["original_site_id_present_in_2021_edition"]),
            "log1p_neighbor_10km":math.log1p(n["other_original_potential_site_centres_within_10km"]),
            "log1p_neighbor_2km":math.log1p(n["other_original_potential_site_centres_within_2km"]),
            "log1p_neighbor_50km":math.log1p(n["other_original_potential_site_centres_within_50km"]),
            "outcome":int(r["occurrence"]=="P"),
        })
    data=pd.DataFrame(rows)
    if data.empty:
        raise ValueError("SAMPLE_STOP no source-eligible P/A rows")
    return data,{"original_source_eligible_P_A_records":len(valid),
                 "original_source_after_area_geography_network_join":len(data),
                 "original_source_rows_rejected_after_geography_join":dict(invalid)}


def fit_predict(train,test,y,w,names):
    """Fit one geography-heldout fold; impute/standardize only on training."""
    numeric=train[names].to_numpy(dtype=float)
    held=test[names].to_numpy(dtype=float)
    med=np.nanmedian(numeric,axis=0)
    med[~np.isfinite(med)]=0
    numeric=np.where(np.isfinite(numeric),numeric,med)
    held=np.where(np.isfinite(held),held,med)
    center=np.zeros(len(names),dtype=float)
    scale=np.ones(len(names),dtype=float)
    for j,n in enumerate(names):
        if n in CONTINUOUS:
            center[j]=np.mean(numeric[:,j])
            scale[j]=max(float(np.std(numeric[:,j])),1e-10)
    numeric=(numeric-center)/scale
    held=(held-center)/scale
    if len(np.unique(y))<2:
        raise ValueError("MODEL_STOP train cohort missing one of original P/A classes")
    tw=w/np.mean(w)
    model=LogisticRegression(C=C,solver="lbfgs",max_iter=500,tol=1e-6)
    model.fit(numeric,y,sample_weight=tw)
    return model.predict_proba(held)[:,1]


def evaluate_programme(data,programme):
    sample=data.loc[data.source_programme.eq(programme)].copy()
    original_sites=int(sample.site_id.nunique())
    source_rows=len(sample)
    rawblocks=sample.groupby("block").site_id.nunique()
    allowed=set(rawblocks[rawblocks>=MIN_BLOCK_SITES].index)
    sample=sample.loc[sample.block.isin(allowed)].copy()
    if len(sample)<MIN_ROWS or sample.block.nunique()<MIN_BLOCKS:
        return {
            "status":"STOP_NOT_ENOUGH_ORIGINAL_INDEPENDENT_SPATIAL_SUPPORT",
            "pre_250km_gate_source_rows":source_rows,
            "pre_250km_gate_original_sites":original_sites,
            "post_250km_gate_source_rows":len(sample),
            "post_250km_gate_original_sites":int(sample.site_id.nunique()),
            "post_250km_gate_250km_blocks":int(sample.block.nunique()),
            "ecological_effect_fitted":False,
        }
    all_species=sorted(sample.species.unique())
    dummies=[f"species_{s}" for s in all_species[1:]]
    for name,code in zip(dummies,all_species[1:]):
        sample[name]=sample.species.eq(code).astype(float)

    base=["year_scaled","latitude","longitude_sin","longitude_cos",
          "log_area","island","log_station_distance","station_distance_missing",
          "vantage_A","vantage_S","expert_occurrence","expert_species",
          "expert_site","original_site_id_in_2021",*dummies]
    cols={"B0_source_area_and_effort":base,
          "B1_plus_10km_candidate_sites":base+["log1p_neighbor_10km"],
          "SENS_plus_2km_candidate_sites":base+["log1p_neighbor_2km"],
          "SENS_plus_50km_candidate_sites":base+["log1p_neighbor_50km"]}
    n_hist=sample.groupby(["site_id","species"]).site_id.transform("size")
    sample["weight"]=1/n_hist
    block_scores={k:{} for k in cols}
    block_logloss={k:{} for k in cols}
    classes={}
    for block in sorted(sample.block.unique()):
        training=sample.loc[sample.block.ne(block)]
        held=sample.loc[sample.block.eq(block)]
        yt=training.outcome.to_numpy(dtype=int)
        yh=held.outcome.to_numpy(dtype=int)
        wt=training.weight.to_numpy(dtype=float)
        wh=held.weight.to_numpy(dtype=float)
        if len(np.unique(yt))<2:
            return {
                "status":"STOP_TRAIN_SPLIT_SINGLE_OUTCOME_CLASS",
                "heldout_250km_block":block,
                "ecological_effect_fitted":False,
            }
        for model,names in cols.items():
            p=fit_predict(training,held,yt,wt,names)
            block_scores[model][block]=float(np.average((yh-p)**2,weights=wh))
            p=np.clip(p,1e-9,1-1e-9)
            block_logloss[model][block]=float(np.average(
                -(yh*np.log(p)+(1-yh)*np.log(1-p)),weights=wh))
    macro={m:float(np.mean(list(v.values()))) for m,v in block_scores.items()}
    macro_logloss={m:float(np.mean(list(v.values()))) for m,v in block_logloss.items()}
    improvements={b:block_scores["B0_source_area_and_effort"][b]-
                    block_scores["B1_plus_10km_candidate_sites"][b]
                  for b in sorted(sample.block.unique())}
    required=math.ceil(2*len(improvements)/3)
    positive=sum(v>0 for v in improvements.values())
    gain=macro["B0_source_area_and_effort"]-macro["B1_plus_10km_candidate_sites"]
    return {
        "status":"EXPLORATORY_ORIGINAL_SURVEY_SPATIAL_CV_COMPLETED",
        "pre_250km_gate_source_rows":source_rows,
        "pre_250km_gate_original_sites":original_sites,
        "post_250km_gate_source_rows":len(sample),
        "post_250km_gate_original_sites":int(sample.site_id.nunique()),
        "post_250km_gate_250km_blocks":len(improvements),
        "unique_site_species_histories":int(sample.groupby(["site_id","species"]).ngroups),
        "source_species_list":all_species,
        "source_P_A_class_presence":{str(k):int(v) for k,v in sample.outcome.value_counts().items()},
        "macro_equal_block_site_history_weighted_Brier":macro,
        "macro_equal_block_site_history_weighted_logloss":macro_logloss,
        "B0_minus_B1_10km_primary_Brier_gain":gain,
        "primary_blockwise_Brier_gain":improvements,
        "number_primary_blocks_with_Brier_gain":positive,
        "minimum_fixed_primary_support_blocks":required,
        "exploratory_source_frame_predictive_support":bool(gain>0 and positive>=required),
        "post_outcome_parameter_selection_permitted":False,
        "original_survey_site_is_independent_island":False,
        "model_identifies_physical_island_or_sea_barrier_causation":False,
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,required=True)
    a=parser.parse_args()
    with requests.Session() as session:
        manifest,mi=public_dataset_manifests(session)
        sources,receipts=fetch_original_sources(session,manifest)
    _v13summary,rawsurveys,geog=rows_linked(sources)
    original_sites,qa=parse_geo(sources["potential_geography_2025"],old=False)
    older,_=parse_geo(sources["potential_geography_2021"],old=True)
    transformer=Transformer.from_crs(4326,3031,always_xy=True)
    locations=[]
    for site,x in original_sites.items():
        X,Y=transformer.transform(x["lon"],x["lat"])
        locations.append({"site_id":site,"source_class":x["feature"],"x":X,"y":Y})
    network,nmeta=site_point_network(locations,set(older))
    data,source_sample=original_sample(rawsurveys,geog,network)
    outcomes={
        p:evaluate_programme(data,p) for p in ("ADELIE","FLYING")
    }
    report={
        "status":"AADC_DATABASE_NATIVE_CANDIDATE_SITE_DENSITY_EXPLORATORY_BIOLOGY_V1",
        "source_sample":source_sample,
        "programmes":outcomes,
        "original_source_workbook_SHA256":{
            k:v["original_SHA256"] for k,v in receipts.items()},
        "independent_2025_network_geographic_site_count":
            nmeta["author_original_geographic_site_total"],
        "previous_V14_P_A_outcomes_already_viewed":True,
        "result_is_preregistered_independent_replication":False,
        "negative_or_positive_result_does_not_prove_island_causation":True,
        "source_2025_potential_sites_are_time_invariant_historical_accessible_habitat":False,
        "no_source_nonreporting_recoded_as_absence":True,
    }
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,ensure_ascii=False))


if __name__=="__main__":
    main()
