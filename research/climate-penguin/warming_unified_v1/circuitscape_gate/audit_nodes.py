#!/usr/bin/env python3
"""Outcome-blind Circuitscape focal-node resolution gate (not a Circuitscape solve)."""
from __future__ import annotations
import csv
import hashlib
import json
import math
import time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import urlparse

import numpy as np
import xarray as xr
from pyproj import Geod

ROOT=Path(__file__).resolve().parents[2]  # research/climate-penguin
HERE=Path(__file__).resolve().parent
OUT=HERE/"outputs"
CACHE=OUT/"cache"
OUT.mkdir(exist_ok=True,parents=True)
CACHE.mkdir(exist_ok=True,parents=True)
SITES=("ARDL","BISC","LION","LLAN","PCHA","PETE")
SAMPLES=((1993,9),(2018,9))
SOURCE_BLOB="5a211a0eaa63b6a5d3516353dd9431428618dbd3"
COORD_REL="outputs/sic_spatial_coherence_macro40_v1/macro40_site_coordinates.csv"
URL_ROOT="https://thredds.met.no/thredds/fileServer/osisaf/met.no/reprocessed/ice/conc_450a1_files/monthly"
NEAR_OCEAN_KM=60

def gitblob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()

def pinned_coords():
    data=(ROOT/COORD_REL).read_bytes()
    if gitblob(data)!=SOURCE_BLOB:
        raise ValueError("Original macro-coordinate Git blob changed")
    with (ROOT/COORD_REL).open(newline="",encoding="utf-8") as f:
        a=list(csv.DictReader(f))
    if len(a)!=40 or len({r["site_id"] for r in a})!=40:
        raise ValueError("40 distinct original sites changed")
    focal={r["site_id"]:r for r in a if r["site_id"] in SITES}
    if set(focal)!=set(SITES):raise ValueError("Six focal sites incomplete")
    return focal

def source(year,month):
    file=f"ice_conc_sh_ease2-250_cdr-v3p1_{year:04d}{month:02d}.nc"
    url=f"{URL_ROOT}/{year}/{file}"
    path=CACHE/file
    if not path.exists():
        error=None
        for attempt in range(3):
            try:
                with urlopen(Request(url,headers={"User-Agent":"mina-circuitscape-support-gate-v1/20261108"}),timeout=80) as response:
                    if urlparse(response.geturl()).hostname!="thredds.met.no":
                        raise ValueError("Source redirect changed hostname")
                    data=response.read(12000000)
                if not(data.startswith(b"CDF") or data.startswith(b"\x89HDF")):
                    raise ValueError("Original response not NetCDF")
                tmp=path.with_suffix(".partial")
                tmp.write_bytes(data)
                tmp.replace(path)
                break
            except Exception as exc:
                error=exc
                time.sleep(2*(attempt+1))
        if not path.exists():
            raise RuntimeError(f"Official original {file} could not be obtained: {error}")
    return {"year":year,"month":month,"url":url,"path":str(path),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),
            "bytes":path.stat().st_size}

def write_csv(path,rows):
    if not rows:return
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def main():
    g=Geod(ellps="WGS84")
    coords=pinned_coords()
    pairs=[]
    for i,a in enumerate(SITES):
        for b in SITES[i+1:]:
            p,q=coords[a],coords[b]
            _,_,dist=g.inv(float(p["longitude"]),float(p["latitude"]),float(q["longitude"]),float(q["latitude"]))
            pairs.append({"site_a":a,"site_b":b,"WGS84_geodesic_km":dist/1000,
                "within_25km":dist<25000,"within_50km":dist<50000})
    write_csv(OUT/"six_focal_site_pairwise_distance.csv",pairs)
    samples=[];nodes=[];grid_fingerprint=None
    for year,month in SAMPLES:
        sample=source(year,month)
        with xr.open_dataset(sample["path"]) as ds:
            if ds.attrs.get("product_version","")!="3.1":
                raise ValueError("Wrong OSI SAF product_version")
            for var in ("lat","lon","status_flag","ice_conc"):
                if var not in ds:raise ValueError(f"Required original variable missing: {var}")
            lat=np.asarray(ds.lat.values).ravel()
            lon=np.asarray(ds.lon.values).ravel()
            flag=np.asarray(ds.status_flag.values[0]).ravel()
            ice=np.asarray(ds.ice_conc.values[0]).ravel()
            if len(lat)!=432*432 or len(lon)!=len(lat) or len(ice)!=len(lat):
                raise ValueError("Unexpected native EASE2 pixel grid")
            fi=np.where(np.isfinite(flag),flag,32767).astype(np.int32)
            valid_ocean=np.isfinite(flag)&((fi&3)==0)&np.isfinite(ice)
            mask_sha=hashlib.sha256(np.ascontiguousarray(np.column_stack((lat,lon))).tobytes()).hexdigest()
            if grid_fingerprint is not None and grid_fingerprint!=mask_sha:
                raise ValueError("Original native satellite grid differs between fixed dates")
            grid_fingerprint=mask_sha
            sample.update({"valid_ocean_source_pixels":int(valid_ocean.sum()),"original_grid_shape":[432,432],
                           "native_geo_sha256":mask_sha})
            for site in SITES:
                row=coords[site]
                _,_,dist=g.inv(np.full_like(lon,float(row["longitude"])),np.full_like(lat,float(row["latitude"])),lon,lat)
                candidate=np.where(valid_ocean&np.isfinite(dist)&(dist<=NEAR_OCEAN_KM*1000),dist,np.inf)
                idx=int(np.argmin(candidate))
                ok=np.isfinite(candidate[idx])
                if ok:
                    rec={"site_id":site,"year":year,"month":month,"matched_original_marine_pixel":True,
                      "node_flat_index":idx,"node_y":idx//432,"node_x":idx%432,
                      "node_latitude":float(lat[idx]),"node_longitude":float(lon[idx]),
                      "node_to_original_site_km":float(dist[idx]/1000),
                      "node_source_SIC_pct":float(ice[idx])}
                else:
                    rec={"site_id":site,"year":year,"month":month,"matched_original_marine_pixel":False,
                       "node_flat_index":"","node_y":"","node_x":"","node_latitude":"","node_longitude":"",
                       "node_to_original_site_km":"","node_source_SIC_pct":""}
                nodes.append(rec)
        samples.append(sample)
        print("SOURCE_SAMPLE="+json.dumps({"year":year,"month":month,
          "bytes":sample["bytes"],"valid_ocean_source_pixels":sample["valid_ocean_source_pixels"],
          "sha256":sample["sha256"]}),flush=True)
    write_csv(OUT/"six_coastal_node_source_assignments.csv",nodes)
    issues=[];groups={}
    for y,m in SAMPLES:
        grouped={}
        for node in [r for r in nodes if r["year"]==y and r["month"]==m and r["matched_original_marine_pixel"]]:
            grouped.setdefault(node["node_flat_index"],[]).append(node["site_id"])
        collided=[sorted(v) for v in grouped.values() if len(v)>1]
        groups[f"{y}-{m:02d}"]={"distinct_selected_source_cells":len(grouped),
            "unresolved_shared_pixel_groups":collided,
            "coastal_cells_per_site":{x["site_id"]:x["node_flat_index"] for x in nodes if x["year"]==y and x["month"]==m}}
        if collided:issues.append(f"{y}-{m:02d}: source marine pixels merge sites {collided}")
    result={"status":"SOURCE_NODES_SUPPORTED_ONLY_PHYSICAL_MODEL" if all(r["matched_original_marine_pixel"] for r in nodes)
        else "SOURCE_NODES_INCOMPLETE",
        "analysis_type":"CIRCUITSCAPE_FEASIBILITY_NO_CIRCUIT_SOLVE_NO_BREEDING_MOVEMENT_INFERENCE",
        "pin":{COORD_REL:SOURCE_BLOB},
        "source_samples":samples,
        "n_sites":len(SITES),"n_site_pairs":len(pairs),
        "geodesic_pairs_below_25km":sum(int(r["within_25km"]) for r in pairs),
        "geodesic_pairs_below_50km":sum(int(r["within_50km"]) for r in pairs),
        "site_pair_geodesic_nearest_km":min(x["WGS84_geodesic_km"] for x in pairs),
        "per_sample_coastal_node_support":groups,
        "site_node_max_offset_km":max(float(x["node_to_original_site_km"]) for x in nodes if x["matched_original_marine_pixel"]),
        "issues":issues,
        "interpretation":["Node assignment to OSI SAF source-valid ocean grid is a modeling choice, not confirmed safe physical access.",
         "Sites with the same native ocean pixel cannot yield a distinct pairwise resistance in that sampled grid.",
         "Only two fixed months were inspected; no demographic, phenology, movement or full-year history was tested.",
         "Direct multi-year individual breeding-colony resight tracks are not present among archived qualifying public sources.",
         "Previous 45 GPS-day binary low-SIC connectivity showed no graph disconnections, but relative current density is untested.",
         "Species-specific sea-ice-to-movement resistance remains a free scenario parameter, not an empirical coefficient."],
        "scientific_decision":"GO for exploratory environmental connectivity modeling only; NO-GO for verified breeding dispersal/philopatry inference."}
    (OUT/"circuitscape_node_support.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("CIRCUITSCAPE_NODE_GATE="+json.dumps({k:result[k] for k in
          ("status","n_sites","n_site_pairs","geodesic_pairs_below_25km",
           "geodesic_pairs_below_50km","site_pair_geodesic_nearest_km",
           "per_sample_coastal_node_support","site_node_max_offset_km",
           "scientific_decision")},ensure_ascii=False),flush=True)
    if result["status"]=="SOURCE_NODES_INCOMPLETE":raise SystemExit(2)

if __name__=="__main__":main()
