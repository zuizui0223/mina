#!/usr/bin/env python3
"""Diagnose historical Landsat source IDs that fail the frozen C2 scene crosswalk."""
from __future__ import annotations

import argparse
import io
import json
import time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests


def strip_metaheader(text):
    return text.split("*/",1)[1].lstrip("\r\n ") if "*/" in text else text


def read_reference(text):
    df=pd.read_csv(io.StringIO(strip_metaheader(text)),sep="\t")
    return pd.DataFrame({
        "source_file":df.iloc[:,1].astype(str),
        "published_d":pd.to_numeric(df.iloc[:,2],errors="coerce"),
        "latitude":pd.to_numeric(df.iloc[:,7],errors="coerce"),
        "longitude":pd.to_numeric(df.iloc[:,8],errors="coerce"),
    })


def parse_source(name):
    s=str(name)
    year=int(s[9:13]); doy=int(s[13:16])
    date=(datetime(year,1,1)+timedelta(days=doy-1)).date().isoformat()
    return {"published_path":int(s[3:6]),"published_row":int(s[6:9]),"date":date}


def _ival(props,*keys):
    for k in keys:
        if props.get(k) is None: continue
        try:return int(props[k])
        except (TypeError,ValueError):pass
    return None


def search_point(session,endpoint,collection,lon,lat,date):
    payload={
        "collections":[collection],
        "intersects":{"type":"Point","coordinates":[float(lon),float(lat)]},
        "datetime":f"{date}T00:00:00Z/{date}T23:59:59Z",
        "limit":100
    }
    r=session.post(endpoint.rstrip("/")+"/search",json=payload,timeout=60)
    r.raise_for_status()
    out=[]
    for item in r.json().get("features",[]):
        p=item.get("properties",{}) or {}
        if str(p.get("platform","")).upper() not in {"LANDSAT_7","LANDSAT-7"}: continue
        out.append({
            "item_id":str(item.get("id")),
            "wrs_path":_ival(p,"landsat:wrs_path","wrs:path","landsat:path"),
            "wrs_row":_ival(p,"landsat:wrs_row","wrs:row","landsat:row"),
        })
    return sorted(out,key=lambda x:x["item_id"])


def select_points(local,nmax):
    s=local.sort_values(["latitude","longitude"]).reset_index(drop=True)
    if len(s)<=nmax:return s
    idx=sorted({round(i*(len(s)-1)/(nmax-1)) for i in range(nmax)})
    return s.iloc[idx].reset_index(drop=True)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--contract",required=True,type=Path)
    ap.add_argument("--out-json",required=True,type=Path)
    ap.add_argument("--out-csv",required=True,type=Path)
    a=ap.parse_args()
    c=json.loads(a.contract.read_text(encoding="utf-8"))
    r=requests.get(c["published_reference"]["download"],headers={"Accept":c["published_reference"]["accept"],"User-Agent":"mina-guano-unmatched-diagnostic/1.0"},timeout=120)
    r.raise_for_status()
    ref=read_reference(r.text)
    session=requests.Session();session.headers.update({"User-Agent":"mina-guano-unmatched-diagnostic/1.0"})
    rows=[]; summary=[]
    for source in c["source_files"]:
        local=ref[ref.source_file.eq(source)].copy()
        if local.empty: raise ValueError(f"source not in reference: {source}")
        parsed=parse_source(source)
        pts=select_points(local,int(c["diagnostic"]["sample_points_per_source_file_max"]))
        candidate_counts={}
        for i,p in pts.iterrows():
            items=search_point(session,c["landsat"]["stac_endpoint"],c["landsat"]["collection"],p.longitude,p.latitude,parsed["date"])
            if not items:
                rows.append({"source_file":source,**parsed,"sample_index":i,"latitude":p.latitude,"longitude":p.longitude,"candidate_item_id":None,"candidate_wrs_path":None,"candidate_wrs_row":None})
            for item in items:
                rows.append({
                    "source_file":source,**parsed,"sample_index":i,
                    "latitude":p.latitude,"longitude":p.longitude,
                    "candidate_item_id":item["item_id"],
                    "candidate_wrs_path":item["wrs_path"],
                    "candidate_wrs_row":item["wrs_row"],
                })
                key=f"{item['wrs_path']}/{item['wrs_row']}|{item['item_id']}"
                candidate_counts[key]=candidate_counts.get(key,0)+1
            time.sleep(0.05)
        ranked=sorted(candidate_counts.items(),key=lambda kv:(-kv[1],kv[0]))
        summary.append({
            "source_file":source,
            **parsed,
            "published_pixels":int(len(local)),
            "sample_points":int(len(pts)),
            "candidate_hits":ranked,
            "all_sample_points_share_top_candidate":bool(ranked and ranked[0][1]==len(pts))
        })
    out=pd.DataFrame(rows)
    receipt={
        "schema_version":1,
        "result_id":"mina-paper2-published-guano-unmatched-scene-diagnostic-v1",
        "contract_id":c["contract_id"],
        "sources":summary,
        "decision":{
            "crosswalk_gate_changed":False,
            "demographic_magnitudes_opened":False
        },
        "boundary":[
            "Diagnostic only; no failed historical source is automatically relabeled.",
            "A consistent alternate C2 row may motivate a separately frozen archival alias rule, not silent rescue."
        ]
    }
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    out.to_csv(a.out_csv,index=False)
    a.out_json.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(receipt,indent=2,sort_keys=True))


if __name__=="__main__":
    main()
