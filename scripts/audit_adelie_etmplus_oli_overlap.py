#!/usr/bin/env python3
"""Outcome-blind ETM+ / OLI overlap support audit for Antarctic guano sensor bridging."""
from __future__ import annotations

import argparse
import json
import math
import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests


def parse_dt(item):
    raw=(item.get("properties",{}) or {}).get("datetime") or (item.get("properties",{}) or {}).get("start_datetime")
    if not raw:
        return None
    try:
        return datetime.fromisoformat(str(raw).replace("Z","+00:00"))
    except ValueError:
        return None


def cloud(item):
    try:
        return float((item.get("properties",{}) or {}).get("eo:cloud_cover"))
    except (TypeError,ValueError):
        return math.nan


def search(session, endpoint, collection, lon, lat, start, end, cap=500):
    url=endpoint.rstrip("/")+"/search"
    payload={
        "collections":[collection],
        "intersects":{"type":"Point","coordinates":[float(lon),float(lat)]},
        "datetime":f"{start}T00:00:00Z/{end}T23:59:59Z",
        "limit":100,
    }
    items=[]
    method="POST"; next_url=url; body=payload
    for _ in range(20):
        for attempt in range(5):
            try:
                r=session.post(next_url,json=body,timeout=60) if method=="POST" else session.get(next_url,timeout=60)
                r.raise_for_status(); data=r.json(); break
            except Exception:
                if attempt==4: raise
                time.sleep(2**attempt)
        items.extend(data.get("features",[]))
        if len(items)>=cap: return items[:cap],False
        nxt=next((x for x in data.get("links",[]) if x.get("rel")=="next" and x.get("href")),None)
        if not nxt: return items,True
        next_url=nxt["href"]; method=str(nxt.get("method","GET")).upper(); body=nxt.get("body") if method=="POST" else None
    return items,False


def filter_items(items, platform, months, cloud_max):
    out=[]
    for item in items:
        props=item.get("properties",{}) or {}
        if str(props.get("platform","")).upper() not in {platform,platform.replace("_","-")}:
            continue
        dt=parse_dt(item)
        cc=cloud(item)
        if dt is None or dt.month not in months or math.isnan(cc) or cc>cloud_max:
            continue
        out.append({"id":str(item.get("id")),"datetime":dt,"cloud":cc})
    return sorted(out,key=lambda x:(x["datetime"],x["id"]))


def pair_scenes(etm, oli, max_days):
    candidates=[]
    for i,a in enumerate(etm):
        for j,b in enumerate(oli):
            dd=abs((a["datetime"]-b["datetime"]).total_seconds())/86400
            if dd<=max_days:
                candidates.append((dd,a["datetime"],b["datetime"],i,j))
    candidates.sort()
    used_e=set(); used_o=set(); pairs=[]
    for dd,_,__,i,j in candidates:
        if i in used_e or j in used_o: continue
        used_e.add(i); used_o.add(j)
        pairs.append({
            "etmplus_id":etm[i]["id"],
            "oli_id":oli[j]["id"],
            "etmplus_date":etm[i]["datetime"].date().isoformat(),
            "oli_date":oli[j]["datetime"].date().isoformat(),
            "absolute_day_difference":dd,
            "etmplus_cloud":etm[i]["cloud"],
            "oli_cloud":oli[j]["cloud"],
        })
    return pairs


def build_roster(forcing_csv, atlas_csv, expected):
    f=pd.read_csv(forcing_csv)
    forbidden=[c for c in f.columns if c.lower() in {"count","abundance","population_trend","n_eff","kappa"}]
    if forbidden: raise ValueError(f"forbidden outcome columns: {forbidden}")
    ad=f.loc[f["species_id"].astype(str).eq("ADPE"),["site_id"]].drop_duplicates()
    if len(ad)!=expected: raise ValueError(f"Adelie site drift: {len(ad)} != {expected}")
    a=pd.read_csv(atlas_csv)
    meta=a[["site_id","site_name","region","latitude","longitude"]].drop_duplicates("site_id")
    out=ad.merge(meta,on="site_id",how="left",validate="1:1")
    if out[["latitude","longitude"]].isna().any().any(): raise ValueError("missing coordinates")
    return out.sort_values("site_id").reset_index(drop=True)


def audit(forcing_csv,atlas_csv,contract_path):
    c=json.loads(Path(contract_path).read_text(encoding="utf-8"))
    roster=build_roster(forcing_csv,atlas_csv,int(c["candidate_roster"]["expected_sites"]))
    session=requests.Session(); session.headers.update({"User-Agent":"mina-etm-oli-overlap/1.0"})
    start,end=c["window"]; months=set(map(int,c["season_months"])); cloud_max=float(c["scene_cloud_max_percent"])
    max_days=float(c["pairing"]["maximum_absolute_day_difference"]); min_pairs=int(c["pairing"]["minimum_pairs_per_site"])
    rows=[]; all_pairs=[]
    for i,s in roster.iterrows():
        items,complete=search(session,c["landsat"]["stac_endpoint"],c["landsat"]["collection"],s.longitude,s.latitude,start,end)
        etm=filter_items(items,c["landsat"]["etmplus_platform"],months,cloud_max)
        oli=filter_items(items,c["landsat"]["oli_platform"],months,cloud_max)
        pairs=pair_scenes(etm,oli,max_days)
        rows.append({
            **s.to_dict(),
            "etmplus_scenes":len(etm),
            "oli_scenes":len(oli),
            "scene_pairs":len(pairs),
            "passes_overlap_support":len(pairs)>=min_pairs,
            "catalog_complete":bool(complete)
        })
        for p in pairs:
            all_pairs.append({"site_id":s.site_id,"region":s.region,**p})
        print(f"[{i+1}/{len(roster)}] {s.site_id}: ETM={len(etm)} OLI={len(oli)} pairs={len(pairs)}",flush=True)
        time.sleep(0.03)
    sites=pd.DataFrame(rows); pairs_df=pd.DataFrame(all_pairs)
    passed=sites[sites["passes_overlap_support"].astype(bool)]
    regions=int(passed["region"].nunique())
    total_pairs=int(len(pairs_df))
    g=c["continuation_gate"]
    gate=bool(
        len(passed)>=int(g["minimum_sites_with_pairs"])
        and regions>=int(g["minimum_regions_with_pairs"])
        and total_pairs>=int(g["minimum_total_scene_pairs"])
    )
    receipt={
        "schema_version":1,
        "result_id":"mina-paper2-adelie-etmplus-oli-overlap-support-v1-result",
        "contract_id":c["contract_id"],
        "candidate_sites":int(len(sites)),
        "sites_with_required_pairs":int(len(passed)),
        "regions_with_required_pairs":regions,
        "total_scene_pairs":total_pairs,
        "by_region":[
            {
                "region":str(region),
                "candidate_sites":int(len(gr)),
                "sites_with_required_pairs":int(gr["passes_overlap_support"].sum()),
                "scene_pairs":int(pairs_df.loc[pairs_df.region.astype(str).eq(str(region))].shape[0]) if len(pairs_df) else 0
            }
            for region,gr in sites.groupby("region",dropna=False)
        ],
        "decision":{
            "antarctic_sensor_bridge_validation_supported":gate,
            "demographic_magnitudes_opened":False
        },
        "boundary":[
            "Metadata overlap is not spectral equivalence.",
            "SLC-off ETM+ gaps remain missing at the later pixel gate.",
            "No demographic outcome was used."
        ]
    }
    return sites,pairs_df,receipt


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--forcing-csv",required=True,type=Path)
    p.add_argument("--atlas-csv",required=True,type=Path)
    p.add_argument("--contract",required=True,type=Path)
    p.add_argument("--out-sites-csv",required=True,type=Path)
    p.add_argument("--out-pairs-csv",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    a=p.parse_args()
    sites,pairs,receipt=audit(a.forcing_csv,a.atlas_csv,a.contract)
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    sites.to_csv(a.out_sites_csv,index=False); pairs.to_csv(a.out_pairs_csv,index=False)
    a.out_json.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
