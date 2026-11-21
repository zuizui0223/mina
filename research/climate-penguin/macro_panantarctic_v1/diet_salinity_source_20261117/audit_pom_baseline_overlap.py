#!/usr/bin/env python3
"""Observational availability audit of Southern Ocean particulate organic matter
(POM) isotope baselines, against 860 source-matched penguin isotope-proxy seasons.

Do not fit a baseline-adjusted ecology coefficient from interpolation, historical
all-year averages, nearby non-contemporaneous cruises, or zero-filled absence.
Original-source gate and spatiotemporal support only, not trophic identification.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd
from pyproj import Geod

ISOSCAPE_GIT_BLOB="e44eb37cd772781b986e1a1776cf104eaaddd716"
SOURCE_URL="https://github.com/KatieSJG/SO_isoscape/blob/main/Appendix%20A.csv"
CITATION="St John Glew et al. (2021), Global Biogeochemical Cycles, DOI:10.1029/2020GB006901"
GEO=Geod(ellps="WGS84")
MONTHS={"Nov":11,"Dec":12,"Jan":1,"Feb":2}
RADII=(50,100,250,500)

def pinned_csv(path):
    raw=Path(path).read_bytes()
    h=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if h!=ISOSCAPE_GIT_BLOB:
        raise ValueError(f"Original POM source content SHA drift: {h} != {ISOSCAPE_GIT_BLOB}")
    d=pd.read_csv(path,encoding="utf-8-sig")
    expected={"SampleID","StudyID","Year","Month","Species","Lat","Long","dN15","dC13","C:N","Source"}
    if not expected.issubset(d.columns):raise ValueError("Publisher POM input columns changed")
    if len(d)!=3360:raise ValueError(f"Original POM total row count changed: {len(d)}")
    return d,h

def season_clean(d):
    d=d.copy()
    d["dN15"]=pd.to_numeric(d.dN15,errors="coerce")
    d["Lat"]=pd.to_numeric(d.Lat,errors="coerce")
    d["Long"]=pd.to_numeric(d.Long,errors="coerce")
    d["Year"]=pd.to_numeric(d.Year,errors="coerce")
    d=d.loc[(d.Species=="POM") & d.dN15.notna() & d.Lat.notna() &
            d.Long.notna() & d.Year.notna()].copy()
    if len(d)!=2718:raise ValueError(f"Original isotope nonmissing count drift {len(d)}")
    d["month_number"]=d.Month.map(MONTHS)
    d=d.loc[d.month_number.notna()].copy()
    d["season"]=d.Year.astype(int)-d.month_number.isin([1,2]).astype(int)
    d=d.loc[d.season.between(1996,2012)].copy()
    # Distinct samples are not independent cruises, stations, years, or provinces.
    d["station_key"]=(d.StudyID.astype(str)+"|"+
         d.Year.astype(int).astype(str)+"|"+d.month_number.astype(int).astype(str)+"|"+
         d.Lat.round(3).astype(str)+"|"+d.Long.round(3).astype(str))
    return d

def get_matched(zip_path,atlas_zip):
    with zipfile.ZipFile(zip_path) as z:
        m=pd.read_csv(z.open("matched_860_original_isotope_ocean_ice_site_seasons.csv"))
    with zipfile.ZipFile(atlas_zip) as z:
        a=pd.read_csv(z.open("panantarctic_595_site_inventory.csv"))
    if (len(m),m.site_id.nunique(),m.source_region.nunique())!=(860,88,13):
        raise ValueError("Frozen original 860 isotope cohort differs")
    a=a.loc[:,["site_id","latitude","longitude","source_region"]]
    if len(a)!=595 or a.site_id.nunique()!=595:raise ValueError("Original 595 atlas changed")
    if m.duplicated(["site_id","season"]).any():raise ValueError("Duplicate isotope season")
    m=m.merge(a.drop(columns="source_region"),how="left",on="site_id",validate="many_to_one")
    if m[["latitude","longitude"]].isna().any().any():
        raise ValueError("Original source colony geographic ID lost")
    return m

def compute(pom, matched, out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    records=[]
    dcols=["season","Lat","Long","dN15","StudyID","station_key"]
    seasons={int(s):group[dcols] for s,group in pom.groupby("season")}
    # Record source count support and exact distances; no end-point used to choose joins.
    detail=[]
    for row in matched.itertuples(index=False):
        p=seasons.get(int(row.season))
        rec={"site_id":row.site_id,"season":int(row.season),
             "source_region":row.source_region}
        for radius in RADII:
            rec[f"n_pom_samples_{radius}km"]=0
            rec[f"n_pom_stations_{radius}km"]=0
            rec[f"n_pom_studies_{radius}km"]=0
            rec[f"pom_mean_d15N_{radius}km"]=np.nan
        rec["nearest_same_season_POM_km"]=np.nan
        if p is not None and len(p)>0:
            _,_,dist_m=GEO.inv(
                np.full(len(p),float(row.longitude)),np.full(len(p),float(row.latitude)),
                p.Long.to_numpy(dtype=float),p.Lat.to_numpy(dtype=float))
            dist=np.asarray(dist_m,dtype=float)/1000.
            rec["nearest_same_season_POM_km"]=float(dist.min())
            for radius in RADII:
                ids=np.flatnonzero(dist<=radius)
                sub=p.iloc[ids]
                rec[f"n_pom_samples_{radius}km"]=len(sub)
                rec[f"n_pom_stations_{radius}km"]=int(sub.station_key.nunique())
                rec[f"n_pom_studies_{radius}km"]=int(sub.StudyID.nunique())
                if len(sub):
                    rec[f"pom_mean_d15N_{radius}km"]=float(sub.dN15.mean())
                # Diagnostic list only up to 250km, no pseudo-annual interpolation.
                if radius==250:
                    for z,d_km in zip(sub.itertuples(index=False),dist[ids]):
                        detail.append({"site_id":row.site_id,"season":int(row.season),
                           "source_region":row.source_region,"pom_study_id":z.StudyID,
                           "pom_station_key":z.station_key,"pom_d15N":z.dN15,
                           "distance_km":float(d_km)})
        records.append(rec)
    df=pd.DataFrame(records)
    if len(df)!=860 or df.duplicated(["site_id","season"]).any():
        raise ValueError("Unexpected duplicate site/season source")
    df.to_csv(out/"original_isotope_860_same_season_pom_spatial_coverage.csv",index=False)
    pd.DataFrame(detail).to_csv(out/"original_pom_matched_pairs_within_250km.csv",index=False)
    per_region=df.groupby("source_region").agg(
        source_penguin_site_seasons=("season","size"),
        distinct_penguin_sites=("site_id","nunique"),
        same_year_POM_50km=("n_pom_samples_50km",lambda x:int((x>0).sum())),
        same_year_POM_100km=("n_pom_samples_100km",lambda x:int((x>0).sum())),
        same_year_POM_250km=("n_pom_samples_250km",lambda x:int((x>0).sum())),
        at_least_3_POM_stations_100km=("n_pom_stations_100km",lambda x:int((x>=3).sum())),
    ).reset_index()
    per_region.to_csv(out/"original_pom_baseline_same_year_region_support.csv",index=False)
    byradius={}
    for radius in RADII:
        support=df.loc[df[f"n_pom_samples_{radius}km"]>0]
        three=df.loc[df[f"n_pom_stations_{radius}km"]>=3]
        byradius[str(radius)]={
            "matching_penguin_site_seasons":int(len(support)),
            "matching_penguin_sites":int(support.site_id.nunique()),
            "matching_penguin_regions":int(support.source_region.nunique()),
            "matching_penguin_seasons":int(support.season.nunique()),
            "with_at_least_3_distinct_POM_stations":int(len(three)),
            "with_at_least_3_distinct_POM_stations_regions":int(three.source_region.nunique()),
            "with_at_least_3_distinct_POM_stations_seasons":int(three.season.nunique()),
            "n_raw_POM_pairings_not_independent":int(df[f"n_pom_samples_{radius}km"].sum()),
        }
    r100=byradius["100"]
    baseline_adequate=(r100["with_at_least_3_distinct_POM_stations"]>=344
        and r100["with_at_least_3_distinct_POM_stations_regions"]>=3
        and r100["with_at_least_3_distinct_POM_stations_seasons"]>=6)
    report={
        "status":"OBSERVATIONAL_BASELINE_SUPPORT_GATE_ONLY_NO_SALINITY_DIET_CAUSAL_INFERENCE",
        "original_pom_source":SOURCE_URL,"citation":CITATION,
        "original_pom_all_source_rows":3360,"original_pom_nonmissing_d15N":2718,
        "novfeb_pom_records_in_penguin_start_seasons":int(len(pom)),
        "novfeb_pom_source_stations":int(pom.station_key.nunique()),
        "novfeb_pom_source_studies":int(pom.StudyID.nunique()),
        "penguin_original_site_seasons":len(df),
        "penguin_original_sites":int(df.site_id.nunique()),
        "penguin_original_regions":int(df.source_region.nunique()),
        "match_definition":"Same penguin start season and actual POM source month Nov-Dec of t or Jan-Feb of t+1, nearest true WGS84 geodesic.",
        "radii_km":byradius,
        "predeclared_100km_adequacy_gate":"at least 40% (344/860) site-seasons each >=3 POM stations, >=3 regions, >=6 different source seasons, before response regression",
        "can_fit_matched_baseline_adjusted_macro_model":bool(baseline_adequate),
        "seasonal_POM_climatology_is_not_time_resolved_baseline":True,
        "cannot_separate_isotope_baseline_from_prey_with_unmatched_rows":True,
        "never_interpolate_missing_baseline_as_measured_or_zero":True,
    }
    (out/"original_pom_baseline_overlap_verdict.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(report,indent=2,ensure_ascii=False))
    return report

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--pom-csv",required=True)
    p.add_argument("--original-860-zip",required=True)
    p.add_argument("--original-595-zip",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args()
    original,sha=pinned_csv(a.pom_csv)
    pom=season_clean(original)
    matched=get_matched(a.original_860_zip,a.original_595_zip)
    result=compute(pom,matched,a.out)
    result["pom_pinned_github_blob"]=sha
    (Path(a.out)/"original_pom_baseline_overlap_verdict.json").write_text(
        json.dumps(result,indent=2,ensure_ascii=False)+"\n")

if __name__=="__main__":
    main()
