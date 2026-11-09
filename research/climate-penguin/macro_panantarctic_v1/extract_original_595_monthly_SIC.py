#!/usr/bin/env python3
"""Original native 25km OSI SAF monthly SIC for all 595 MAPPPD observed colonies.

Source-only 3-year×4-month pilot for Antarctic macroecology, NOT a fitted
biological climate effect. Use 1993-09 to freeze native ocean memberships before
looking at any penguin counts; all locations predeclared by 595-site macro atlas.
"""
from __future__ import annotations
import csv,hashlib,json,math,time
from collections import defaultdict
from pathlib import Path
from urllib.request import urlopen,Request
from urllib.parse import urlparse
import numpy as np
import xarray as xr
from pyproj import Geod
from scipy.spatial import cKDTree

HERE=Path(__file__).resolve().parent
OUT=HERE/"ice_595_outputs"
CACHE=OUT/"publisher_netcdf"
OUT.mkdir(parents=True,exist_ok=True)
CACHE.mkdir(parents=True,exist_ok=True)
SOURCE="https://thredds.met.no/thredds/fileServer/osisaf/met.no/reprocessed/ice/conc_450a1_files/monthly"
YEARS=(1993,2008,2018)
MONTHS=(8,9,10,11)
BASE=(1993,9)
KM=100.
COVERAGE=.80
MIN_OCEAN=3
GRID_SHAPE=(432,432)

def csvrows(path):
    with path.open(encoding="utf-8",newline="") as f:
        return list(csv.DictReader(f))

def write(path,data):
    if not data:raise ValueError("No original source records")
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]))
        w.writeheader();w.writerows(data)

def source(year,month):
    name=f"ice_conc_sh_ease2-250_cdr-v3p1_{year:04d}{month:02d}.nc"
    url=f"{SOURCE}/{year}/{name}"
    file=CACHE/name
    if not file.exists():
        last=None
        for trial in range(3):
            try:
                with urlopen(Request(url,headers={"User-Agent":"mina-panantarctic-595-site-OSI-450a1-v3p1-original"}),timeout=75) as f:
                    if urlparse(f.geturl()).hostname!="thredds.met.no":
                        raise ValueError("Official EUMETSAT source host changed")
                    data=f.read(25_000_001)
                if not data or len(data)>25_000_000 or not (data.startswith(b"CDF") or data.startswith(b"\x89HDF")):
                    raise ValueError("Not original source NetCDF or byte limit exceeded")
                temp=file.with_suffix(".partial")
                temp.write_bytes(data);temp.replace(file)
                break
            except Exception as exc:
                last=exc
                time.sleep(2*(trial+1))
        if not file.exists():
            raise RuntimeError(f"Publisher original month {name} unavailable: {type(last).__name__}: {last}")
    raw=file.read_bytes()
    return {"year":year,"month":month,"publisher_url":url,
            "original_file_basename":name,"sha256":hashlib.sha256(raw).hexdigest(),
            "bytes":len(raw),"path":file}

def read_source(rec):
    with xr.open_dataset(rec["path"]) as ds:
        if ds.attrs.get("product_version")!="3.1":
            raise ValueError("OSI source product_version drift")
        if any(k not in ds.variables for k in ("lat","lon","status_flag","ice_conc")):
            raise ValueError("OSI ocean variables missing")
        lat=np.asarray(ds["lat"].values).reshape(-1)
        lon=np.asarray(ds["lon"].values).reshape(-1)
        flag=np.asarray(ds["status_flag"].values[0]).reshape(-1)
        sic=np.asarray(ds["ice_conc"].values[0]).reshape(-1)
    if len(lat)!=432*432 or len(lon)!=len(lat) or len(flag)!=len(lat) or len(sic)!=len(lat):
        raise ValueError("Wrong source 25km Southern EASE2 raster dimension")
    flagint=np.where(np.isfinite(flag),flag,32767).astype(np.int64)
    valid=np.isfinite(sic)&np.isfinite(flag)&((flagint&3)==0)&(sic>=0)&(sic<=100)
    fingerprint=hashlib.sha256(np.ascontiguousarray(np.column_stack((lat,lon))).tobytes()).hexdigest()
    return lat,lon,sic,valid,fingerprint

def xyz(lon,lat):
    a=np.deg2rad(lon);b=np.deg2rad(lat)
    return np.column_stack((np.cos(b)*np.cos(a),np.cos(b)*np.sin(a),np.sin(b)))

def frozen_membership(sites,lat,lon,valid):
    geod=Geod(ellps="WGS84")
    mask=np.isfinite(lat)&np.isfinite(lon)
    flat=np.flatnonzero(mask)
    tree=cKDTree(xyz(lon[mask],lat[mask]))
    coords=xyz(np.array([float(z["longitude"]) for z in sites]),
               np.array([float(z["latitude"]) for z in sites]))
    # Use an overbroad spherical cap; WGS84 Geod removes all beyond 100km.
    radius=2*math.sin((KM+1)/(2*6371.0))
    neighbor=tree.query_ball_point(coords,radius)
    source={}
    for site,cand in zip(sites,neighbor):
        ix=flat[np.asarray(cand,dtype=np.int64)]
        if len(ix):
            _,_,distance=geod.inv(np.full(len(ix),float(site["longitude"])),
                                  np.full(len(ix),float(site["latitude"])),
                                  lon[ix],lat[ix])
            ix=ix[(np.isfinite(distance))&(distance<=KM*1000)]
        ix=ix[valid[ix]]
        # Original baseline marine pixels frozen for every later month.
        source[site["site_id"]]=np.array(sorted(map(int,ix)),dtype=np.int32)
    return source

def main():
    sites=csvrows(HERE/"outputs"/"panantarctic_595_site_inventory.csv")
    if len(sites)!=595 or len({r["site_id"] for r in sites})!=595:
        raise ValueError("Primary full source 595-site geometry changed")
    old=csvrows(HERE.parent/"outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv")
    if len(old)!=9600:raise ValueError("Old 40-site SIC reference coverage changed")
    oldmap={(z["site_id"],int(z["year"]),int(z["month"])):z for z in old
            if z["inner_km"]=="0" and z["complete_month"]=="True"}
    order=[BASE]+[(y,m) for y in YEARS for m in MONTHS if (y,m)!=BASE]
    receipts=[];lines=[];frozen=None;gridfp=None
    for year,month in order:
        receipt=source(year,month)
        lat,lon,sic,valid,fp=read_source(receipt)
        if gridfp is None:
            gridfp=fp
            frozen=frozen_membership(sites,lat,lon,valid)
        elif gridfp!=fp:
            raise ValueError("Publisher source geolocation differs across 12 months")
        receipt={k:v for k,v in receipt.items() if k!="path"}
        receipt["native_grid_geo_sha256"]=gridfp
        receipt["original_ocean_valid_pixel_count"]=int(valid.sum())
        receipts.append(receipt)
        supported=0
        for site in sites:
            ix=frozen[site["site_id"]]
            ocean=int(len(ix))
            obs=valid[ix]
            count=int(obs.sum())
            coverage=count/ocean if ocean else 0.
            ready=(ocean>=MIN_OCEAN and count>0 and coverage>=COVERAGE)
            mean=float(np.mean(sic[ix[obs]])) if ready else None
            old_ref=oldmap.get((site["site_id"],year,month))
            old_value=float(old_ref["sic_mean"]) if old_ref and old_ref["sic_mean"]!="" else None
            if ready:supported+=1
            lines.append({
              "site_id":site["site_id"],"source_region":site["source_region"],
              "year":year,"month":month,
              "original_reference_ocean_pixels_within_100km":ocean,
              "original_valid_same_pixels_this_month":count,
              "original_native_ocean_coverage_fraction":coverage,
              "source_25km_buffer_mean_SIC_pct":mean if ready else "",
              "source_40_site_daily_derived_monthly_SIC_pct":old_value if old_value is not None else "",
              "source_full_595_site_monthly_support": "OK" if ready else
                   ("BASELINE_MARINE_PIXELS_FEWER_THAN_3" if ocean<MIN_OCEAN else "MONTHLY_OCEAN_QA_INCOMPLETE"),
              "not_an_absence_or_future_penguin_forecast":True})
        print(f"PANANTARCTIC_OSI_MONTH={year}-{month:02d} source_supported_sites={supported}/595 sha256={receipt['sha256']}",flush=True)
    if len(lines)!=595*len(order):raise ValueError("Monthly source panel incomplete")
    bysite=defaultdict(list)
    for r in lines:bysite[r["site_id"]].append(r)
    if len(bysite)!=595:raise ValueError("Lost a site from frozen 595 source cohort")
    original40=set(z["site_id"] for z in old)
    cross=[z for z in lines if z["site_id"] in original40 and
           z["source_full_595_site_monthly_support"]=="OK" and
           z["source_40_site_daily_derived_monthly_SIC_pct"]!=""]
    def corr(x,y):
        a=np.asarray(x,dtype=float);b=np.asarray(y,dtype=float)
        return float(np.corrcoef(a,b)[0,1]) if len(a)>=3 else None
    diff=[float(z["source_25km_buffer_mean_SIC_pct"])-float(z["source_40_site_daily_derived_monthly_SIC_pct"]) for z in cross]
    status={
        "status":"PANANTARCTIC_NATIVE_MONTHLY_ICE_MACRO_SOURCE_PILOT_COMPLETE",
        "original_publisher":"EUMETSAT OSI SAF OSI-450a1 v3.1 monthly original 25km Southern EASE2",
        "monthly_scene_years":list(YEARS),"months":list(MONTHS),
        "n_original_source_netCDF_files":len(receipts),
        "n_frozen_breeding_site_codes":len(bysite),
        "n_site_month_records":len(lines),
        "n_sites_with_baseline_100km_ocean_grid_at_least3":sum(len(x)>=MIN_OCEAN for x in frozen.values()),
        "n_sites_with_complete_QA_supported_all_12months":sum(
             len(x)==12 and all(r["source_full_595_site_monthly_support"]=="OK" for r in x)
             for x in bysite.values()),
        "n_source_supported_site_months":sum(z["source_full_595_site_monthly_support"]=="OK" for z in lines),
        "n_native_ocean_reference_cells_by_site":{
             "min":min(map(len,frozen.values())),
             "median":float(np.median([len(z) for z in frozen.values()])),
             "max":max(map(len,frozen.values()))},
        "n_original_40site_same_site_month_source_crosscheck":len(cross),
        "existing_40site_daily_derived_vs_monthly_mean_SIC_pearson_r":corr(
             [float(z["source_25km_buffer_mean_SIC_pct"]) for z in cross],
             [float(z["source_40_site_daily_derived_monthly_SIC_pct"]) for z in cross]),
        "original_40site_product_difference_median_abs_pp":float(np.median(np.abs(diff))) if diff else None,
        "original_native_grid_geo_sha256":gridfp,
        "source_notes":[
          "This is fixed 1993/2008/2018 × Aug-Nov publisher source QA, NOT a 30year time-series correlation.",
          "Marine native ocean pixels fixed using 1993 September to avoid resnapping to preferred climate years.",
          "Original mapped site is a source breeding locality, not a biological habitat absence.",
          "Existing 40-site means came from a daily-derived OSI ice series and need not equal native monthly product.",
          "The source is a continental spatial-environment expansion, not a future CMIP6 model or vegetation change."
        ]}
    write(OUT/"original_595_site_months_12_source_QA.csv",lines)
    write(OUT/"original_595_sites_marine_native_reference_cells.csv",
          [{"site_id":z["site_id"],"region":z["source_region"],
            "n_frozen_native_ocean_pixels":len(frozen[z["site_id"]]),
            "native_original_25km_flat_pixel_ids":";".join(str(i) for i in frozen[z["site_id"]])}
           for z in sites])
    (OUT/"original_monthly_source_receipts.json").write_text(json.dumps(receipts,indent=2)+"\n")
    (OUT/"original_595_native_monthly_SIC_pilot_summary.json").write_text(
         json.dumps(status,indent=2)+"\n")
    print("PANANTARCTIC_595_ORIGINAL_MONTHLY_SIC="+json.dumps(status),flush=True)

if __name__=="__main__":
    main()
