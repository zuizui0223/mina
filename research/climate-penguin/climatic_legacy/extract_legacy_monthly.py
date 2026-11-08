#!/usr/bin/env python3
"""Outcome-blind 1979-1990 original OSI SAF monthly SIC extraction with 1991-2020 bridge QC."""
from __future__ import annotations
import csv, hashlib, json, math, os, time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlparse
import numpy as np
import xarray as xr
from pyproj import Geod

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(__file__).parent/"source_extract_outputs"
CACHE=OUT/"cache"
OUT.mkdir(exist_ok=True);CACHE.mkdir(exist_ok=True)
PINS={
 "coordinates":("outputs/sic_spatial_coherence_macro40_v1/macro40_site_coordinates.csv","5a211a0eaa63b6a5d3516353dd9431428618dbd3"),
 "original_monthly":("outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv","4fcea71c2d8b1069b6ad143f6522061ed434daf5")
}
SOURCE="https://thredds.met.no/thredds/fileServer/osisaf/met.no/reprocessed/ice/conc_450a1_files/monthly"
OVERLAP=[(1991,8),(2001,9),(2020,11)]
MONTHS=(8,9,10,11)
PERIODS=[(y,m) for y in range(1979,1991) for m in MONTHS]
WORK=PERIODS+OVERLAP
MAX_BYTES=18000000

def pin_file(key):
    rel,expected=PINS[key]
    b=(ROOT/rel).read_bytes()
    digest=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if digest!=expected:raise ValueError("Git input blob drift "+rel+" "+digest)
    return ROOT/rel
def rows(path):
    with path.open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def output_csv(path, data):
    if not data:return
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(data[0]))
        w.writeheader();w.writerows(data)
def fetch_month(t):
    y,m=t
    name=f"ice_conc_sh_ease2-250_cdr-v3p1_{y:04d}{m:02d}.nc"
    url=f"{SOURCE}/{y}/{name}"
    path=CACHE/name
    if not path.exists():
        last=None
        for attempt in range(4):
            try:
                with urlopen(Request(url,headers={"User-Agent":"mina-legacy-v1/20261108"}),timeout=90) as f:
                    if urlparse(f.geturl()).hostname!="thredds.met.no":raise ValueError("untrusted redirect")
                    raw=f.read(MAX_BYTES+1)
                if not 0<len(raw)<=MAX_BYTES or not (raw.startswith(b"\x89HDF") or raw.startswith(b"CDF")):
                    raise ValueError("bad netCDF or size")
                tmp=path.with_suffix(".part");tmp.write_bytes(raw);tmp.replace(path)
                break
            except Exception as e:
                last=e;time.sleep(attempt+1)
        if not path.exists():raise RuntimeError(f"{name}: {last}")
    data=path.read_bytes()
    return {"year":y,"month":m,"url":url,"path":str(path),
            "sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data)}
def main():
    coords=rows(pin_file("coordinates"))
    if len(coords)!=40 or len(set(x["site_id"] for x in coords))!=40:raise ValueError("site IDs not unique")
    original=rows(pin_file("original_monthly"))
    if len(original)!=9600:raise ValueError("existing 40*30*4*2 climate source changed")
    old={}
    for r in original:
        if int(r["inner_km"])!=0:continue
        key=(r["site_id"],int(r["year"]),int(r["month"]))
        if key in old:raise ValueError("duplicate old monthly record "+str(key))
        old[key]=float(r["sic_mean"]) if r["complete_month"]=="True" and r["sic_mean"] else None
    print("SOURCE_REQUEST="+json.dumps({"months_1979_1990":len(PERIODS),"overlap":OVERLAP,"sites":len(coords)}),flush=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        manifests=list(pool.map(fetch_month,WORK))
    manifests.sort(key=lambda x:(x["year"],x["month"]))
    (OUT/"source_manifest.json").write_text(json.dumps(manifests,indent=2)+"\n")
    geod=Geod(ellps="WGS84")
    masks=None;master_lat=None;master_lon=None;new=[];matched=[];invalid=0
    for j,e in enumerate(manifests):
        with xr.open_dataset(e["path"],decode_times=False) as ds:
            if str(ds.attrs.get("product_version"))!="3.1":raise ValueError("product version changed")
            for name in ["lat","lon","ice_conc","status_flag"]:
                if name not in ds:raise ValueError("monthly schema changed: "+name)
            lat=np.asarray(ds["lat"].values);lon=np.asarray(ds["lon"].values)
            if masks is None:
                master_lat=lat;master_lon=lon;masks={}
                for site in coords:
                    _,_,dist=geod.inv(np.full(lon.shape,float(site["longitude"])),
                             np.full(lat.shape,float(site["latitude"])),lon,lat)
                    ix=np.flatnonzero((dist.ravel()>=0)&(dist.ravel()<100000))
                    if not len(ix):raise ValueError("empty 0–100 km mask")
                    masks[site["site_id"]]=ix
            elif not(np.allclose(lat,master_lat,equal_nan=True) and np.allclose(lon,master_lon,equal_nan=True)):
                raise ValueError("coastal grid geometry changed")
            ice=np.asarray(ds["ice_conc"].values[0]).ravel()
            flag=np.asarray(ds["status_flag"].values[0]).ravel()
            flags=np.where(np.isfinite(flag),flag,32767).astype(np.int32)
            ocean=np.isfinite(flag)&((flags&3)==0)
            for site in coords:
                sid=site["site_id"];ix=masks[sid];oi=ix[ocean[ix]]
                viable=oi[np.isfinite(ice[oi])]
                supported=(len(oi)>0 and len(viable)/len(oi)>=0.8)
                v=float(ice[viable].mean()) if supported and len(viable) else None
                if v is not None and not 0<=v<=100.001:raise ValueError("SIC out of range")
                if not supported:invalid+=1
                record={"site_id":sid,"year":e["year"],"month":e["month"],
                    "nearshore_sic_pct":v if v is not None else "",
                    "n_cells_within_100km":len(ix),"n_ocean_cells":len(oi),
                    "n_valid_cells":len(viable),"supported":bool(supported)}
                if (e["year"],e["month"]) in OVERLAP:
                    ov=old.get((sid,e["year"],e["month"]))
                    if ov is not None and v is not None:
                        matched.append({"site_id":sid,"year":e["year"],"month":e["month"],
                            "original_daily_based_sic_pct":ov,"new_monthly_based_sic_pct":v,
                            "monthly_minus_daily_pp":v-ov})
                else:new.append(record)
        if (j+1)%12==0 or j==len(manifests)-1:print(f"SOURCE_EXTRACT_PROGRESS={j+1}/{len(manifests)}",flush=True)
    if len(new)!=48*40:raise ValueError("monthly extraction row count")
    output_csv(OUT/"historical_1979_1990_macro40_monthly.csv",new)
    output_csv(OUT/"overlap_bridge_differences.csv",matched)
    ab=np.asarray([abs(x["monthly_minus_daily_pp"]) for x in matched])
    dif=np.asarray([x["monthly_minus_daily_pp"] for x in matched])
    overlap_qc={"n":len(matched),"sites":len(set(x["site_id"] for x in matched)),
            "median_absolute_pp":float(np.median(ab)) if len(ab) else None,
            "p90_absolute_pp":float(np.quantile(ab,.90)) if len(ab) else None,
            "mean_signed_pp":float(np.mean(dif)) if len(dif) else None,
            "max_absolute_pp":float(ab.max()) if len(ab) else None}
    # Frozen before use of new penguin outcomes. Diagnostic thresholds make no biological assertions.
    bridge_ok=(len(matched)>=90 and overlap_qc["sites"]>=30 and
               overlap_qc["median_absolute_pp"]<=3 and overlap_qc["p90_absolute_pp"]<=10 and
               abs(overlap_qc["mean_signed_pp"])<=3)
    missing=sum(1 for x in new if not x["supported"])
    old_months={int(r["year"]) for r in original}
    out={"status":"SOURCE_QC_PASS" if bridge_ok else "SOURCE_QC_HOLD",
      "source":"OSI-450-a1 v3.1 (same product as original daily 1991–2020)",
      "source_doi":"10.15770/EUM_SAF_OSI_0023",
      "new_years":"1979–1990","months":[8,9,10,11],"n_historical_site_months":len(new),
      "unsupported_historical_site_months":missing,
      "unsupported_fraction":missing/len(new),"overlap_bridge":overlap_qc,
      "source_blobs":{k:v[1] for k,v in PINS.items()},
      "n_original_monthly_rows":len(original),"n_old_source_years":len(old_months),
      "outcome_data_examined":False,"sensor_warning":"SMMR 48-hour cadence before July 1987; publisher monthly product used without day-imputation"}
    (OUT/"source_quality.json").write_text(json.dumps(out,indent=2)+"\n")
    print("SOURCE_QC_RESULT="+json.dumps(out),flush=True)
    if not bridge_ok:raise SystemExit(3)

if __name__=="__main__":
    main()
