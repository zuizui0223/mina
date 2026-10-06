#!/usr/bin/env python3
"""Descriptive comparison of demographic state, static area and isolation."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path

import numpy as np
import pandas as pd


def haversine_km(lat1, lon1, lat2, lon2):
    r=6371.0088
    p1,p2=math.radians(lat1),math.radians(lat2)
    dp=math.radians(lat2-lat1); dl=math.radians(lon2-lon1)
    a=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*r*math.asin(math.sqrt(a))


def spearman(x,y):
    a=pd.Series(np.asarray(x,float)).rank(method="average")
    b=pd.Series(np.asarray(y,float)).rank(method="average")
    return float(a.corr(b))


def desc_rank(values, descending=True):
    s=pd.Series(np.asarray(values,float))
    return s.rank(method="min",ascending=not descending).astype(int).to_numpy()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--site-changes-csv",required=True,type=Path)
    ap.add_argument("--traits-csv",required=True,type=Path)
    ap.add_argument("--out-json",required=True,type=Path)
    a=ap.parse_args()

    changes=pd.read_csv(a.site_changes_csv)
    traits=pd.read_csv(a.traits_csv)
    panels=[]

    for (species_id, region), local in changes.groupby(["species_id","region"],sort=True):
        df=local.merge(traits,on="site_id",how="left",validate="one_to_one")
        if df["mapped_ice_free_area_ha_2000m"].isna().any():
            raise ValueError("missing frozen static trait")

        # Nearest-neighbour distance within exactly the retained network.
        nn=[]
        for i,row in df.iterrows():
            ds=[]
            for j,other in df.iterrows():
                if i==j: continue
                ds.append(haversine_km(
                    float(row.latitude),float(row.longitude),
                    float(other.latitude),float(other.longitude)
                ))
            nn.append(min(ds))
        df["nearest_neighbor_km"]=nn
        df["log1p_ice_free_area"]=np.log1p(df["mapped_ice_free_area_ha_2000m"].astype(float))
        df["initial_pairs_per_mapped_ha"]=(
            df["first_count"].astype(float)/df["mapped_ice_free_area_ha_2000m"].astype(float)
        )

        rho_state=spearman(df["first_share"],df["delta_share"])
        rho_area=spearman(df["log1p_ice_free_area"],df["delta_share"])
        # Smaller distance = more connected, so use negative NN distance as connectivity.
        rho_connect=spearman(-df["nearest_neighbor_km"],df["delta_share"])
        rho_density=spearman(df["initial_pairs_per_mapped_ha"],df["delta_share"])

        final_idx=int(np.argmax(df["last_share"].to_numpy(float)))
        area_rank=desc_rank(df["mapped_ice_free_area_ha_2000m"],True)
        initial_share_rank=desc_rank(df["first_share"],True)
        connected_rank=desc_rank(-df["nearest_neighbor_km"],True)

        rows=[]
        for i,row in df.iterrows():
            rows.append({
                "site_id":str(row.site_id),
                "site_name":str(row.site_name),
                "first_share":float(row.first_share),
                "last_share":float(row.last_share),
                "delta_share":float(row.delta_share),
                "mapped_ice_free_area_ha_2000m":float(row.mapped_ice_free_area_ha_2000m),
                "nearest_neighbor_km":float(row.nearest_neighbor_km),
                "initial_pairs_per_mapped_ha":float(row.initial_pairs_per_mapped_ha),
                "initial_share_rank":int(initial_share_rank[i]),
                "ice_free_area_rank":int(area_rank[i]),
                "connectivity_rank_nearest":int(connected_rank[i]),
            })

        panels.append({
            "species_id":str(species_id),
            "region":str(region),
            "n_sites":int(len(df)),
            "rho_delta_share_vs_initial_share":rho_state,
            "rho_delta_share_vs_log1p_ice_free_area":rho_area,
            "rho_delta_share_vs_nearest_site_connectivity":rho_connect,
            "rho_delta_share_vs_initial_pairs_per_mapped_ha":rho_density,
            "final_dominant_site":str(df.iloc[final_idx].site_id),
            "final_dominant_was_initial_dominant":bool(initial_share_rank[final_idx]==1),
            "final_dominant_initial_share_rank":int(initial_share_rank[final_idx]),
            "final_dominant_ice_free_area_rank":int(area_rank[final_idx]),
            "final_dominant_connectivity_rank_nearest":int(connected_rank[final_idx]),
            "sites":rows,
        })

    out={
        "schema_version":1,
        "analysis_id":"mina-mapppd-static-vs-state-growth-v1",
        "status":"post_outcome_descriptive_only_no_p_values",
        "panels":panels,
        "boundary":[
            "Mapped ice-free area within 2 km is not occupied or unoccupied nesting capacity.",
            "Nearest retained-site distance is a simple geographic descriptor, not realised dispersal connectivity.",
            "No inferential p-values, pooled model, alternate radius, kernel or predictor search is performed.",
            "The analysis cannot identify individual movement or colonisation."
        ]
    }
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(out,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
