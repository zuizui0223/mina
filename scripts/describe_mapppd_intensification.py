#!/usr/bin/env python3
"""Descriptive decomposition of exposed increasing MAPPPD networks."""
from __future__ import annotations

import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd

from scripts.test_mapppd_regional_concentration import (
    load_rda, build_support
)
from scripts.run_paper2_real_v3_fit import (
    build_frozen_real_records, calibrate_observation
)
from scripts.simulate_paper2_observation_recovery import (
    build_frozen_observation_metadata
)
from scripts.simulate_paper2_integrated_recovery import collapse_same_season


def rank_desc(v):
    return pd.Series(-np.asarray(v, float)).rank(method="min").astype(int).to_numpy()


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    a=p.parse_args()

    obs=load_rda(a.mapppdr_dir/"data"/"penguin_obs.rda","penguin_obs")
    sites=load_rda(a.mapppdr_dir/"data"/"sites.rda","sites")
    metadata=build_frozen_observation_metadata(obs)
    support=[x for x in build_support(metadata,sites) if x["eligible"]]

    records=build_frozen_real_records(obs)
    cal=calibrate_observation(records)
    collapsed=collapse_same_season(
        records,
        delta_image=float(cal["delta_image"]),
        sigma1=float(cal["accuracy"]["1"]["sigma"]),
        sigma2plus=float(cal["accuracy"]["2-5"]["sigma"]),
    )
    collapsed=collapsed.copy()
    collapsed["adjusted_count"]=np.maximum(np.expm1(collapsed["state_hat"].to_numpy(float)),0.0)

    results=[]
    for panel in support:
        sp=panel["species_id"]; region=panel["region"]
        roster=panel["retained_sites"]; seasons=panel["complete_seasons"]
        x=collapsed[
            collapsed["species_id"].astype(str).eq(sp)
            & collapsed["site_id"].astype(str).isin(roster)
            & collapsed["season"].isin(seasons)
        ].copy()
        pivot=x.pivot(index="season",columns="site_id",values="adjusted_count").reindex(index=seasons,columns=roster)
        if pivot.isna().any().any():
            raise ValueError(f"incomplete panel {sp} {region}")
        totals=pivot.sum(axis=1)
        if len(totals)<2:
            continue
        years=np.asarray(seasons,float)
        yy=np.log(totals.to_numpy(float))
        slope=float(np.sum((years-years.mean())*(yy-yy.mean()))/np.sum((years-years.mean())**2))
        if slope<=0:
            continue

        first=pivot.iloc[0].to_numpy(float); last=pivot.iloc[-1].to_numpy(float)
        first_total=float(first.sum()); last_total=float(last.sum())
        first_share=first/first_total; last_share=last/last_total
        delta=last-first; share_delta=last_share-first_share
        irank=rank_desc(first); frank=rank_desc(last)
        order=np.argsort(-first)
        top_half_n=int(np.ceil(len(roster)/2))
        top_half=set(order[:top_half_n].tolist())
        gross_positive=float(delta[delta>0].sum())
        net=float(delta.sum())
        gross_top=float(sum(delta[i] for i in top_half if delta[i]>0))
        initial_dom=int(order[0])
        final_dom=int(np.argmax(last))

        site_rows=[]
        for i,site in enumerate(roster):
            site_rows.append({
                "site_id":str(site),
                "first_count":float(first[i]),
                "last_count":float(last[i]),
                "delta_count":float(delta[i]),
                "first_share":float(first_share[i]),
                "last_share":float(last_share[i]),
                "delta_share":float(share_delta[i]),
                "initial_rank":int(irank[i]),
                "final_rank":int(frank[i]),
                "count_increased":bool(delta[i]>0),
            })

        results.append({
            "species_id":sp,
            "region":region,
            "first_season":int(seasons[0]),
            "last_season":int(seasons[-1]),
            "n_sites":len(roster),
            "first_total":first_total,
            "last_total":last_total,
            "population_change_fraction":float(last_total/first_total-1),
            "sites_increased":int(np.sum(delta>0)),
            "sites_decreased":int(np.sum(delta<0)),
            "sites_unchanged":int(np.sum(delta==0)),
            "initial_dominant_site":str(roster[initial_dom]),
            "initial_dominant_first_share":float(first_share[initial_dom]),
            "initial_dominant_last_share":float(last_share[initial_dom]),
            "initial_dominant_delta_count":float(delta[initial_dom]),
            "initial_dominant_fraction_of_net_growth":(
                float(delta[initial_dom]/net) if net!=0 else None
            ),
            "final_dominant_site":str(roster[final_dom]),
            "final_dominant_initial_rank":int(irank[final_dom]),
            "gross_positive_gain":gross_positive,
            "initial_top_half_fraction_of_gross_positive_gain":(
                float(gross_top/gross_positive) if gross_positive>0 else None
            ),
            "sites":site_rows,
        })

    out={
        "schema_version":1,
        "analysis_id":"mina-mapppd-intensification-descriptive-v1",
        "status":"post_outcome_descriptive_only",
        "panels":results,
        "interpretation_boundary":[
            "No inferential p-values are computed.",
            "All retained sites were already in the fixed monitored roster; colonisation of empty habitat is not tested.",
            "Site-level count changes do not identify movement, recruitment, survival, or immigration.",
            "No alternate region, roster, season, threshold, or calibration is searched."
        ]
    }
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
