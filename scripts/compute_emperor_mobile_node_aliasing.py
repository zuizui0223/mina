#!/usr/bin/env python3
"""Fixed-node aliasing metrics for mobile emperor-penguin colony locations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from pyproj import Transformer


RADII_KM=(0.5,1.0,2.0,5.0,10.0)
REQUIRED=("colony_id","season","obs_date","longitude","latitude")


def validate_input(df: pd.DataFrame) -> pd.DataFrame:
    missing=set(REQUIRED)-set(df.columns)
    if missing:
        raise ValueError(f"missing fields: {sorted(missing)}")
    x=df.copy()
    x["colony_id"]=x["colony_id"].astype(str)
    x["season"]=pd.to_numeric(x["season"],errors="raise").astype(int)
    x["obs_date"]=pd.to_datetime(x["obs_date"],errors="raise")
    x["longitude"]=pd.to_numeric(x["longitude"],errors="raise").astype(float)
    x["latitude"]=pd.to_numeric(x["latitude"],errors="raise").astype(float)
    if x[list(REQUIRED)].isna().any().any():
        raise ValueError("missing required values")
    return x


def project(df: pd.DataFrame) -> pd.DataFrame:
    x=validate_input(df)
    tr=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True)
    xx,yy=tr.transform(x["longitude"].to_numpy(),x["latitude"].to_numpy())
    x["x_m"]=np.asarray(xx,float)
    x["y_m"]=np.asarray(yy,float)
    return x


def build_date_states(df: pd.DataFrame) -> pd.DataFrame:
    x=project(df)
    rows=[]
    for (colony,season,date),g in x.groupby(["colony_id","season","obs_date"],sort=True):
        rows.append({
            "colony_id":colony,
            "season":int(season),
            "obs_date":pd.Timestamp(date),
            "n_groups":int(len(g)),
            "centroid_x_m":float(g["x_m"].mean()),
            "centroid_y_m":float(g["y_m"].mean()),
            "group_xy":[(float(a),float(b)) for a,b in zip(g["x_m"],g["y_m"])],
        })
    return pd.DataFrame(rows).sort_values(["colony_id","season","obs_date"]).reset_index(drop=True)


def add_anchor_distances(states: pd.DataFrame) -> tuple[pd.DataFrame,pd.DataFrame]:
    s=states.copy()
    out=[]
    anchors=[]
    for (colony,season),g in s.groupby(["colony_id","season"],sort=True):
        g=g.sort_values("obs_date")
        first=g.iloc[0]
        ax=float(first.centroid_x_m); ay=float(first.centroid_y_m)
        anchors.append({
            "colony_id":str(colony),"season":int(season),
            "anchor_date":pd.Timestamp(first.obs_date),
            "anchor_x_m":ax,"anchor_y_m":ay,
        })
        for _,row in g.iterrows():
            pts=np.asarray(row.group_xy,float)
            d=np.sqrt((pts[:,0]-ax)**2+(pts[:,1]-ay)**2)/1000.0
            out.append({
                "colony_id":str(colony),"season":int(season),
                "obs_date":pd.Timestamp(row.obs_date),
                "n_groups":int(row.n_groups),
                "is_anchor_date":bool(pd.Timestamp(row.obs_date)==pd.Timestamp(first.obs_date)),
                "min_group_distance_km":float(np.min(d)),
                "max_group_distance_km":float(np.max(d)),
                "date_centroid_distance_km":float(np.hypot(float(row.centroid_x_m)-ax,float(row.centroid_y_m)-ay)/1000.0),
            })
    return pd.DataFrame(out),pd.DataFrame(anchors)


def build_interannual(anchors: pd.DataFrame) -> pd.DataFrame:
    rows=[]
    for colony,g in anchors.groupby("colony_id",sort=True):
        g=g.sort_values("season").reset_index(drop=True)
        for i in range(1,len(g)):
            a=g.iloc[i-1]; b=g.iloc[i]
            gap=int(b.season)-int(a.season)
            rows.append({
                "colony_id":str(colony),
                "season_from":int(a.season),
                "season_to":int(b.season),
                "season_gap":gap,
                "consecutive":bool(gap==1),
                "anchor_displacement_km":float(np.hypot(float(b.anchor_x_m)-float(a.anchor_x_m),float(b.anchor_y_m)-float(a.anchor_y_m))/1000.0),
            })
    return pd.DataFrame(rows)


def _quantiles(values) -> dict:
    v=np.asarray(list(values),float)
    v=v[np.isfinite(v)]
    if len(v)==0:
        return {"q50":None,"q90":None,"q95":None}
    return {
        "q50":float(np.quantile(v,0.50)),
        "q90":float(np.quantile(v,0.90)),
        "q95":float(np.quantile(v,0.95)),
    }


def summarize(df: pd.DataFrame) -> dict:
    states=build_date_states(df)
    dates,anchors=add_anchor_distances(states)
    inter=build_interannual(anchors)
    consec=inter[inter["consecutive"]].copy() if len(inter) else inter
    post=dates[~dates["is_anchor_date"]].copy()

    alias={}
    for r in RADII_KM:
        key=str(r).rstrip("0").rstrip(".")
        alias[key]={
            "interannual_false_turnover_fraction":(
                float((consec["anchor_displacement_km"]>r).mean()) if len(consec) else None
            ),
            "interannual_false_turnover_n":(
                int((consec["anchor_displacement_km"]>r).sum()) if len(consec) else 0
            ),
            "interannual_transition_n":int(len(consec)),
            "within_season_false_absence_fraction":(
                float((post["min_group_distance_km"]>r).mean()) if len(post) else None
            ),
            "within_season_false_absence_n":(
                int((post["min_group_distance_km"]>r).sum()) if len(post) else 0
            ),
            "within_season_post_anchor_date_n":int(len(post)),
        }

    colony=[]
    for c in sorted(states["colony_id"].unique()):
        ci=consec[consec["colony_id"].eq(c)] if len(consec) else consec
        cp=post[post["colony_id"].eq(c)]
        colony.append({
            "colony_id":c,
            "seasons":int(anchors[anchors["colony_id"].eq(c)]["season"].nunique()),
            "observation_dates":int(states[states["colony_id"].eq(c)].shape[0]),
            "consecutive_transitions":int(len(ci)),
            "interannual_q95_km":_quantiles(ci["anchor_displacement_km"] if len(ci) else [])["q95"],
            "within_season_detection_q95_km":_quantiles(cp["min_group_distance_km"])["q95"],
        })

    return {
        "schema_version":1,
        "analysis_id":"mina-paper3-mobile-node-aliasing-v1",
        "support":{
            "colonies":int(states["colony_id"].nunique()),
            "seasons":int(anchors.shape[0]),
            "observation_dates":int(states.shape[0]),
            "consecutive_interannual_transitions":int(len(consec)),
            "post_anchor_dates":int(len(post)),
        },
        "identity_preserving_radii_km":{
            "interannual_anchor_displacement":_quantiles(consec["anchor_displacement_km"] if len(consec) else []),
            "within_season_min_group_distance":_quantiles(post["min_group_distance_km"] if len(post) else []),
        },
        "aliasing_curve":alias,
        "by_colony":colony,
        "boundary":[
            "Named-colony identity is supplied by the source and is not a statement of demographic closure.",
            "No abundance, breeding-success or environmental variable enters this analysis.",
            "Movement causation is not tested."
        ],
        "_dates":dates,
        "_anchors":anchors,
        "_interannual":inter,
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--input-csv",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-dates-csv",required=True,type=Path)
    p.add_argument("--out-anchors-csv",required=True,type=Path)
    p.add_argument("--out-interannual-csv",required=True,type=Path)
    a=p.parse_args()
    df=pd.read_csv(a.input_csv)
    r=summarize(df)
    dates=r.pop("_dates"); anchors=r.pop("_anchors"); inter=r.pop("_interannual")
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    dates.drop(columns=[],errors="ignore").to_csv(a.out_dates_csv,index=False)
    anchors.to_csv(a.out_anchors_csv,index=False)
    inter.to_csv(a.out_interannual_csv,index=False)
    print(json.dumps(r,indent=2,sort_keys=True))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
