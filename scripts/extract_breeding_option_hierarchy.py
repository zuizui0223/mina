#!/usr/bin/env python3
"""Outcome-blind hierarchical ecosystem diversity around Antarctic penguin sites."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pyreadr
import rasterio
from dbfread import DBF
from pyproj import Transformer
from rasterio.windows import from_bounds

MAPPPDR_COMMIT="88c73a507e0921b2541c218c71eaf16721bc6502"
PRIMARY_SPECIES=("ADPE","CHPE","GEPE")
RADII=(1000,2000,5000)
PRIMARY_RADIUS=2000
EXPECTED_TIF_MD5="cde880d73f7f18b44aecf5690aa2dc92"
EXPECTED_DBF_MD5="fa5363b1c0d882b4343e239d03dc2ba4"


def md5(path:Path)->str:
    h=hashlib.md5()
    with path.open("rb") as fh:
        for chunk in iter(lambda:fh.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()


def load_rda(path:Path,expected:str)->pd.DataFrame:
    x=pyreadr.read_r(str(path))
    if expected in x:
        frame=x[expected]
    elif len(x)==1:
        frame=next(iter(x.values()))
    else:
        raise ValueError(f"cannot resolve {expected}: {list(x)}")
    if not isinstance(frame,pd.DataFrame):
        raise TypeError(expected)
    return frame


def candidate_sites(root:Path)->pd.DataFrame:
    sites=load_rda(root/"data"/"sites.rda","sites")
    obs=load_rda(root/"data"/"penguin_obs.rda","penguin_obs")
    nest=obs[
        obs["species_id"].isin(PRIMARY_SPECIES)
        & (obs["type"]=="nests")
        & obs["count"].notna()
    ].copy()
    nest["year"]=pd.to_numeric(nest["year"],errors="coerce")
    nest=nest.dropna(subset=["year"])

    units=[]
    for (site_id,species_id),local in nest.groupby(["site_id","species_id"]):
        years=sorted(set(int(y) for y in local["year"]))
        if len(years)>=5 and max(years)-min(years)>=10:
            units.append((str(site_id),str(species_id)))
    if len(units)!=152:
        raise ValueError(f"candidate unit drift: {len(units)} != 152")
    ids=sorted({site_id for site_id,_ in units})
    out=sites[sites["site_id"].isin(ids)].copy()
    if len(out)!=122:
        raise ValueError(f"candidate site drift: {len(out)} != 122")
    return out[["site_id","site_name","region","ccamlr_id","latitude","longitude"]]


def vat_maps(path:Path):
    rows=[dict(r) for r in DBF(str(path),load=True,ignore_missing_memofile=True,char_decode_errors="ignore")]
    if len(rows)!=269:
        raise ValueError(f"VAT row drift: {len(rows)}")
    maps={}
    for row in rows:
        value=int(round(float(row["Value"])))
        maps[value]={
            "tier1":str(row["Name_Tier1"]),
            "tier2":str(row["Name_Tier2"]),
            "tier3":str(row["Name_Tier3"]),
        }
    if len({x["tier1"] for x in maps.values()})!=9:
        raise ValueError("Tier 1 name count drift")
    if len({x["tier2"] for x in maps.values()})!=33:
        raise ValueError("Tier 2 name count drift")
    if len({x["tier3"] for x in maps.values()})!=269:
        raise ValueError("Tier 3 name count drift")
    return maps


def shannon(labels:list[str])->float|None:
    if not labels:
        return None
    _,counts=np.unique(np.asarray(labels,dtype=object),return_counts=True)
    p=counts/counts.sum()
    return float(-(p*np.log(p)).sum())


def values_in_circle(src,x:float,y:float,radius:float)->np.ndarray:
    window=from_bounds(x-radius,y-radius,x+radius,y+radius,transform=src.transform)
    window=window.round_offsets().round_lengths()
    arr=src.read(1,window=window,masked=True,boundless=True)
    transform=src.window_transform(window)
    rows,cols=np.indices(arr.shape)
    xs=transform.c+(cols+0.5)*transform.a+(rows+0.5)*transform.b
    ys=transform.f+(cols+0.5)*transform.d+(rows+0.5)*transform.e
    circle=(xs-x)**2+(ys-y)**2<=radius**2
    valid=circle & (~np.ma.getmaskarray(arr))
    vals=np.asarray(arr.data[valid])
    vals=vals[np.isfinite(vals)]
    return vals.astype(int)


def summarize(vals:np.ndarray,maps:dict[int,dict[str,str]],pixel_area_m2:float):
    recognized=[int(v) for v in vals if int(v) in maps]
    if len(recognized)!=len(vals):
        unknown=sorted(set(int(v) for v in vals if int(v) not in maps))
        raise ValueError(f"unmapped raster values: {unknown[:20]}")
    out={
        "mapped_ice_free_pixel_count":len(recognized),
        "mapped_ice_free_area_ha":len(recognized)*pixel_area_m2/10000.0,
    }
    for tier in ("tier1","tier2","tier3"):
        labels=[maps[v][tier] for v in recognized]
        out[f"{tier}_richness"]=len(set(labels))
        out[f"{tier}_shannon"]=shannon(labels)
    return out


def corr(a:pd.Series,b:pd.Series)->float|None:
    x=pd.concat([a,b],axis=1).dropna()
    if len(x)<3:
        return None
    return float(x.iloc[:,0].corr(x.iloc[:,1]))


def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--mapppdr-dir",required=True,type=Path)
    p.add_argument("--raster",required=True,type=Path)
    p.add_argument("--vat-dbf",required=True,type=Path)
    p.add_argument("--out-json",required=True,type=Path)
    p.add_argument("--out-csv",required=True,type=Path)
    a=p.parse_args()

    if md5(a.raster)!=EXPECTED_TIF_MD5:
        raise ValueError("AEI raster md5 drift")
    if md5(a.vat_dbf)!=EXPECTED_DBF_MD5:
        raise ValueError("AEI VAT md5 drift")

    sites=candidate_sites(a.mapppdr_dir)
    maps=vat_maps(a.vat_dbf)
    records=[]

    with rasterio.open(a.raster) as src:
        transformer=Transformer.from_crs(4326,src.crs,always_xy=True)
        pixel_area=abs(float(src.transform.a*src.transform.e-src.transform.b*src.transform.d))
        for row in sites.to_dict(orient="records"):
            x,y=transformer.transform(float(row["longitude"]),float(row["latitude"]))
            rec={
                "site_id":str(row["site_id"]),
                "site_name":str(row["site_name"]),
                "region":str(row["region"]),
                "ccamlr_id":None if pd.isna(row["ccamlr_id"]) else str(row["ccamlr_id"]),
                "latitude":float(row["latitude"]),
                "longitude":float(row["longitude"]),
            }
            for radius in RADII:
                stats=summarize(values_in_circle(src,x,y,radius),maps,pixel_area)
                for key,value in stats.items():
                    rec[f"{key}_{radius}m"]=value
            records.append(rec)

    frame=pd.DataFrame(records)
    a.out_csv.parent.mkdir(parents=True,exist_ok=True)
    frame.to_csv(a.out_csv,index=False)

    coverage={}
    for radius in RADII:
        col=f"mapped_ice_free_pixel_count_{radius}m"
        n=int((frame[col]>0).sum())
        coverage[str(radius)]={
            "sites_with_data":n,
            "coverage_fraction":n/len(frame),
            "missing_site_ids":frame.loc[frame[col]<=0,"site_id"].tolist(),
        }

    primary=coverage[str(PRIMARY_RADIUS)]["coverage_fraction"]
    r_rich_shan=corr(frame[f"tier2_richness_{PRIMARY_RADIUS}m"],frame[f"tier2_shannon_{PRIMARY_RADIUS}m"])
    r_area_rich=corr(frame[f"mapped_ice_free_area_ha_{PRIMARY_RADIUS}m"],frame[f"tier2_richness_{PRIMARY_RADIUS}m"])

    result={
        "schema_version":1,
        "result_id":"mina-antarctic-breeding-options-hierarchy-result-v1",
        "candidate_site_species_units":152,
        "distinct_candidate_sites":len(frame),
        "primary_radius_m":PRIMARY_RADIUS,
        "coverage_by_radius":coverage,
        "primary_radius_coverage_fraction":float(primary),
        "gate_passed":bool(primary>=0.90),
        "hierarchy_unique_names":{"tier1":9,"tier2":33,"tier3":269},
        "collinearity_audit_2km":{
            "tier2_richness_vs_shannon_r":r_rich_shan,
            "ice_free_area_vs_tier2_richness_r":r_area_rich,
        },
        "decision":{
            "tier2_richness_primary":bool(r_rich_shan is None or abs(r_rich_shan)>=0.8),
            "tier2_shannon_sensitivity_only":bool(r_rich_shan is not None and abs(r_rich_shan)>=0.8),
            "tier3_sensitivity_only":true,
            "tier1_context_only":true
        },
        "derived_csv":a.out_csv.name,
        "boundary":[
            "Tier 2 Habitat Complex richness is a breeding-option proxy, not occupied nesting habitat.",
            "No penguin demographic outcome is used."
        ]
    }
    a.out_json.parent.mkdir(parents=True,exist_ok=True)
    a.out_json.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2,sort_keys=True))
    if not result["gate_passed"]:
        raise SystemExit("Hierarchy extraction failed frozen coverage gate")
    return 0


if __name__=="__main__":
    raise SystemExit(main())
