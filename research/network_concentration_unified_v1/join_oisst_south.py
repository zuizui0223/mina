#!/usr/bin/env python3
"""Source-locked Antarctic OISST join for previously fixed MAPPPD 2-epoch rows.

Only NOAA observations + fixed original site coordinates; no outcome regression.
Missing original source, no wet source grid or a 1980-or-older endpoint => missing.
"""
from pathlib import Path
from collections import defaultdict, Counter
import csv,hashlib,math,json,time
import numpy as np
import requests,xarray as xr
from join_oisst_uk import rows,save,km,URL

BASE=Path(__file__).resolve().parent
DATA=BASE/"data"
OUT=BASE/"outputs"
MONTHS=(9,10,11)
MAX_KM=50
# Predetermined source regions, both marine subboxes rather than global full ocean.
SECTORS={
    "west_antarctic":dict(west=268,east=342,south=-79,north=-53),
    "victoria":dict(west=147,east=205,south=-83,north=-68),
}

def fetch_sector(name,bbox):
    params={"var":"sst","time_start":"1981-09-01T00:00:00Z",
            "time_end":"2022-12-31T23:59:59Z",
            "accept":"netcdf4",**bbox}
    for attempt in range(4):
        response=requests.get(URL,params=params,timeout=250,
              headers={"User-Agent":"mina-sst-reproducibility-study/1.0"})
        if response.status_code!=429:break
        if attempt==3:raise ValueError("PSL NOAA rate limit after bounded retries")
        delay=(30,65,120)[attempt]
        ra=response.headers.get("Retry-After","")
        if ra.isdigit():delay=max(delay,min(180,int(ra)))
        print(f"NOAA HTTP429 {name}, retry in {delay}s",flush=True)
        time.sleep(delay)
    response.raise_for_status()
    blob=response.content
    if len(blob)<400 or blob[:3] not in (b"CDF",b"\x89HD"):
        raise ValueError(f"NOAA response not NetCDF ({name}): {blob[:100]!r}")
    dest=BASE/"build"/"oisst"/f"south_{name}.nc"
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(blob)
    with xr.open_dataset(dest,decode_times=True) as ds:
        if "sst" not in ds or not {"time","lat","lon"}.issubset(ds.sst.dims):
            raise ValueError("NOAA grid format mismatch")
        lat=np.asarray(ds["lat"].values)
        lon=np.asarray(ds["lon"].values)
        dates=np.asarray(ds["time"].values)
        values=np.asarray(ds["sst"].values,dtype=float)
        if len(lat)>160 or len(lon)>360 or len(dates)>510:
            raise ValueError("NOAA subset too large or unexpected dimensions")
    tm={}
    for i,date in enumerate(dates):
        key=np.datetime_as_string(date,unit="D")[:7]
        if key in tm:raise ValueError("Duplicate monthly source datum")
        tm[key]=i
    expected={f"{y}-{m:02d}" for y in range(1981,2023) for m in MONTHS}
    if not expected.issubset(tm):
        raise ValueError("NOAA missing frozen autumn source months")
    receipt={"source_url":response.url,"sha256":hashlib.sha256(blob).hexdigest(),"bytes":len(blob)}
    return (lat,lon,tm,values),receipt

def sample(lat,lon,y0,y1,grid,bounds):
    if not bounds["south"]<=lat<=bounds["north"]:
        return None,"outside_frozen_sector_lat"
    glat,glon,tm,vals=grid
    pos=[tm[f"{y}-{m:02d}"] for y in (y0,y1) for m in MONTHS]
    delta=(glon-lon+180)%360-180
    distances=(glat[:,None]-lat)**2+(delta[None,:]*math.cos(math.radians(lat)))**2
    for place in np.argsort(distances,axis=None)[:160]:
        i,j=np.unravel_index(place,distances.shape)
        d=km(lat,lon,float(glat[i]),float(glon[j]))
        if d>MAX_KM:break
        six=vals[pos,i,j]
        if np.all(np.isfinite(six)) and np.all((six>=-3)&(six<=45)):
            return (float(np.mean(six[:3])),float(np.mean(six[3:])),d),"verified"
    return None,"no_same_wet_50km_six_months"

def main():
    primary=[r for r in rows(DATA/"network_species.csv") if
       r["dataset_id"]=="MAPPPD" and r["analysis_role"]=="macro_primary" and r["null_status"]=="computed"]
    pairs=[r for r in rows(DATA/"network_species_pairs.csv") if
       r["dataset_id"]=="MAPPPD" and r["analysis_role"]=="macro_primary" and r["null_status"]=="computed"]
    if (len(primary),len(pairs))!=(12,5):
        raise ValueError("Fixed MAPPPD candidate cohort changed")
    eligible_p=[r for r in primary if int(r["year0"])>=1981]
    eligible_q=[r for r in pairs if int(r["year0"])>=1981]
    if (len(eligible_p),len(eligible_q))!=(6,3):
        raise ValueError("OISST period candidate gate changed")
    required={("network_species",r["row_id"]):int(r["K"]) for r in eligible_p}
    required.update({("network_species_pairs",r["pair_row_id"]):int(r["K_pair"]) for r in eligible_q})
    coords=defaultdict(dict)
    for unit in rows(DATA/"unit_endpoints.csv"):
        key=(unit["analysis_unit"],unit["row_id"])
        if key not in required:continue
        if unit["dataset_id"]!="MAPPPD" or unit["count_status"] not in ("observed_positive","observed_zero"):
            raise ValueError("Original MAPPPD source unit invalid")
        pt=(float(unit["latitude"]),float(unit["longitude"]))
        cid=unit["component_id"]
        if cid in coords[key] and coords[key][cid]!=pt:
            raise ValueError("Original same-site coordinates changed")
        coords[key][cid]=pt
    for key,k in required.items():
        if len(coords[key])!=k:raise ValueError(f"Original K differs {key}: {len(coords[key])} != {k}")
    climates=rows(DATA/"network_climate_intake.csv")
    lookup={(r["analysis_unit"],r["row_id"]):r for r in climates}
    sectors={};source_receipts={};stats=Counter();results=[]
    for name,box in SECTORS.items():
        sectors[name],source_receipts[name]=fetch_sector(name,box)
        time.sleep(20)
    cache={}
    for unit,group,key_col in (("network_species",eligible_p,"row_id"),
                                ("network_species_pairs",eligible_q,"pair_row_id")):
        for row in group:
            key=(unit,row[key_col])
            name="victoria" if row["network_id"]=="MAPPPD::Victoria Land" else "west_antarctic"
            sea=sectors[name];bbox=SECTORS[name]
            y0=int(row["year0"]);y1=int(row["year1"])
            before=[];after=[];distance=[];missing=[]
            for pt in coords[key].values():
                cachekey=(name,*pt,y0,y1)
                if cachekey not in cache:
                    cache[cachekey]=sample(*pt,y0,y1,sea,bbox)
                r,status=cache[cachekey]
                if r is None:missing.append(status)
                else:
                    before.append(r[0]);after.append(r[1]);distance.append(r[2])
            dest=lookup[key]
            if missing:
                reason=Counter(missing).most_common(1)[0][0]
                if dest["delta_sst_C_per_decade"]:
                    raise ValueError("Previously verified SST disappeared")
                dest.update(spatial_status=reason,source_id="",
                    temporal_status="source_endpoint_months_verified",
                    verification_status="not_matched")
                stats[reason]+=1
            else:
                value=10*(float(np.mean(after))-float(np.mean(before)))/(y1-y0)
                old=dest["delta_sst_C_per_decade"]
                if old and not math.isclose(float(old),value,abs_tol=1e-10):
                    raise ValueError("Source time series changed existing result")
                dest.update(delta_sst_C_per_decade=f"{value:.12g}",
                    source_id="NOAA_PSL_OISST_v2.1_monthly_SON",
                    spatial_status="verified_source_ocean_cell",
                    temporal_status="source_endpoint_months_verified",
                    verification_status="verified_same_definition_sst")
                reason="verified";stats["verified_"+unit]+=1
            results.append({"analysis_unit":unit,"row_id":row[key_col],"n_sites":len(coords[key]),
                "n_wet_sites":len(distance),"max_wet_distance_km":f"{max(distance):.3f}" if distance else "",
                "status":reason})
    save(DATA/"network_climate_intake.csv",climates)
    save(DATA/"oisst_south_join_qa.csv",results)
    report={"status":"SOUTH_SEASONAL_SST_SOURCE_JOIN_NO_TESTS",
        "source_doi":"10.25921/RE9P-PT57","season":"Sep-Nov both original years",
        "eligible_main":len(eligible_p),"eligible_pairs":len(eligible_q),
        "source_tiles":source_receipts,"stats":dict(stats),
        "unchanged_not_covered_main":12-len(eligible_p),
        "unchanged_not_covered_pairs":5-len(eligible_q),
        "raw_original_site_counts_published":False}
    OUT.mkdir(exist_ok=True)
    (OUT/"STEP2_OISST_SOUTH_JOIN.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(report,ensure_ascii=False))

if __name__=="__main__":main()
