#!/usr/bin/env python3
"""Source-pinned original BAS GPS days and same-day OSI SAF inputs for Circuitscape advanced mode.

DOES NOT calculate predictive performance. Source/ground geometry is made only from
original first-fix-derived island centers and same-day source-valid OSI ocean pixels.
"""
from __future__ import annotations
import csv, hashlib, json, math, sys
from collections import deque
from pathlib import Path
import numpy as np
import xarray as xr
from scipy.ndimage import label, generate_binary_structure

CLIMATE=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
OUT=HERE/"daily_outputs"
CASES=OUT/"cases"
CASES.mkdir(parents=True,exist_ok=True)
sys.path.insert(0,str(CLIMATE/"work/climate_penguin"))
import chinstrap_daily_SIC_three_island_year_pairs_v1 as original
import chinstrap_daily_ice_same_day_GPS_2013_v1 as satellite
import south_orkney_chinstrap_island_krill_v1 as colony
import signy_gps_krill_access_v1 as geography

SOURCE_ZIP=Path("build/chinstrap_gps_circuit_original/original_gps.zip")
ORIGINAL_DIR=Path("build/chinstrap_gps_circuit_original/original_sic")
PAIRYEARS=((2011,"LI"),(2013,"PI"),(2015,"MI"))
BETA=(("uniform",0.),("ice_penalty",2.),("ice_favor",-2.))
RADIUS_KM=210.
GROUND_BAND_KM=(175.,210.)
SOURCE_LIMIT_KM=35.
GPS_MATCH_KM=20.
NATIVE_SHAPE=(432,432)
NO=-9999.
STRUCT=generate_binary_structure(2,2)

def csvwrite(p,rows):
    if not rows:return
    with p.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader();w.writerows(rows)

def ascii_grid(path,a,x,y,fmt):
    """Copy exact 25-km source grid geometry; raster rows north-to-south."""
    b=np.asarray(a)
    if x[1]<x[0]:b=np.fliplr(b)
    if y[1]>y[0]:b=np.flipud(b)
    with path.open("w",encoding="ascii") as f:
        f.write(f"ncols {len(x)}\nnrows {len(y)}\nxllcorner {min(x)-12.5:.8f}\n"
                f"yllcorner {min(y)-12.5:.8f}\ncellsize 25\nNODATA_value -9999\n")
        np.savetxt(f,b,fmt=fmt)

def connected_component(src,mask):
    labels,n=label(mask,structure=STRUCT)
    ident=int(labels[src])
    return labels==ident if ident else np.zeros_like(mask,bool)

def main():
    if not SOURCE_ZIP.exists():raise ValueError("Original BAS version 2 GPS source ZIP missing")
    locations,shared,locked=original.original_source_days(SOURCE_ZIP)
    tracks,audit=colony.read_all_chinstrap(SOURCE_ZIP)
    centers=colony.island_source_centers(tracks)
    all_dates=sorted(set().union(*(set(shared[p]) for p in PAIRYEARS)))
    if len(all_dates)!=45 or [len(shared[p]) for p in PAIRYEARS]!=[6,14,25]:
        raise ValueError("Original GPS matched source date roster changed")
    (OUT/"original_frozen_gps_date_roster.json").write_text(json.dumps(locked,indent=2)+"\n")
    original_receipts=original.fetch_daily(shared,ORIGINAL_DIR)
    (OUT/"original_45_daily_SIC_receipts.json").write_text(json.dumps(original_receipts,indent=2)+"\n")
    receipts={r["date"]:r for r in original_receipts["source_original_daily_netcdfs"]}
    if set(receipts)!=set(all_dates):raise ValueError("GPS/OSI dates did not match")
    visitrows=[];cases=[];manifest=[]
    coords={}
    for year,other in PAIRYEARS:
        for date in shared[(year,other)]:
            receipt=receipts[date]
            file=ORIGINAL_DIR/receipt["file"]
            daily=satellite.open_day(file,receipt)
            sic=np.asarray(daily["values"]).reshape(NATIVE_SHAPE)
            with xr.open_dataset(file) as ds:
                lat=np.asarray(ds.lat.values).reshape(NATIVE_SHAPE)
                lon=np.asarray(ds.lon.values).reshape(NATIVE_SHAPE)
                x=np.asarray(ds.xc.values,dtype=float)
                y=np.asarray(ds.yc.values,dtype=float)
            if x.size!=432 or y.size!=432 or not np.allclose(abs(np.diff(x)),25) or not np.allclose(abs(np.diff(y)),25):
                raise ValueError("Original 25 km EASE2 geometry changed")
            valid=np.zeros(sic.size,dtype=bool)
            valid[daily["all_ids"]]=True
            valid=valid.reshape(NATIVE_SHAPE)
            for site in ("SI",other):
                center=centers[site,year]
                key=(site,year)
                if key not in coords:
                    d=np.asarray(geography.geodesic(lat,lon,center["center_lat"],center["center_lon"]),dtype=float)
                    coords[key]=d
                dist=coords[key]
                inrad=np.isfinite(dist)&(dist<=RADIUS_KM)
                rr,cc=np.nonzero(inrad)
                if len(rr)<30:raise ValueError("Source domain unreasonably small")
                minr,maxr=int(rr.min()),int(rr.max())+1
                minc,maxc=int(cc.min()),int(cc.max())+1
                sl=(slice(minr,maxr),slice(minc,maxc))
                d=dist[sl]
                ocean=valid[sl]&inrad[sl]
                orig_sic=sic[sl]
                full_candidates=np.where(valid&(dist<=SOURCE_LIMIT_KM),dist,np.inf)
                rid=int(np.argmin(full_candidates))
                seed_ok=np.isfinite(full_candidates.flat[rid])
                group=f"{year}_{other}_{date}_{site}"
                casebase=CASES/group
                casebase.mkdir(exist_ok=True)
                visit_sources=[(tag,fixes) for (ss,sy,tag,dd),fixes in locations.items()
                               if (ss,sy,dd)==(site,year,date)]
                if not visit_sources:raise ValueError("No original BAS GPS on a fixed paired day")
                seen={}
                for tag,fixes in visit_sources:
                    gps_pixels=satellite.sample(daily,fixes,GPS_MATCH_KM,False)
                    for index,ice_val in gps_pixels.items():
                        index=int(index)
                        if index in seen and not math.isclose(seen[index],ice_val,abs_tol=1e-10):
                            raise ValueError("Source GPS mapped to inconsistent daily SIC")
                        seen[index]=float(ice_val)
                first={"case_id":group,"season_start":year,"other_island":other,"date":date,
                       "island":site,"n_original_GPS_deployments_with_fixes":len(visit_sources),
                       "n_original_distinct_matched_GPS_pixels":len(seen),
                       "original_SIC_sha256":receipt["sha256"],"native_center_lat":center["center_lat"],
                       "native_center_lon":center["center_lon"],"source_node_exists":bool(seed_ok)}
                if not seed_ok:
                    cases.append({**first,"status":"COAST_SOURCE_UNAVAILABLE","n_ground_cells":0,
                                  "n_connected_ocean_cells":0,"n_source_valid_GPS_pixels_in_radial_domain":0})
                    continue
                sr,sc=divmod(rid,432)
                src=(sr-minr,sc-minc)
                if not ocean[src]:raise ValueError("source candidate not inside ocean mask")
                connect=connected_component(src,ocean)
                grounds=connect&(d>=GROUND_BAND_KM[0])&(d<=GROUND_BAND_KM[1])
                active=bool(grounds.sum()>=8)
                good_visits=0
                for gps_id,v in sorted(seen.items()):
                    gr,gc=divmod(gps_id,432)
                    in_crop=minr<=gr<maxr and minc<=gc<maxc
                    isconnected=bool(connect[gr-minr,gc-minc]) if in_crop else False
                    valid_rank=bool(isconnected and 10<=dist[gr,gc]<160 and not grounds[gr-minr,gc-minc])
                    good_visits+=valid_rank
                    visitrows.append({"case_id":group,"season_start":year,"other_island":other,
                        "date":date,"island":site,"native_source_pixel":gps_id,"original_daily_sic":v,
                        "source_cell_distance_km":float(dist[gr,gc]),
                        "in_source_connected_circuit":isconnected,
                        "within_fixed_score_distance_bins":bool(valid_rank)})
                cases.append({**first,"status":"READY" if active else "GROUND_BELT_UNAVAILABLE",
                    "source_native_flat_index":rid,"source_snap_km":float(dist.flat[rid]),
                    "native_min_row":minr,"native_min_col":minc,"n_ground_cells":int(grounds.sum()),
                    "n_connected_ocean_cells":int(connect.sum()),
                    "n_source_valid_GPS_pixels_in_radial_domain":good_visits,
                    "grid_shape_rows":maxr-minr,"grid_shape_cols":maxc-minc})
                if not active:continue
                sourcegrid=np.full(d.shape,NO)
                sourcegrid[src]=1.
                groundgrid=np.full(d.shape,NO)
                groundgrid[grounds]=0.
                distancegrid=np.where(connect,d,NO)
                xy=x[minc:maxc];yy=y[minr:maxr]
                ascii_grid(casebase/"source.asc",sourcegrid,xy,yy,"%d")
                ascii_grid(casebase/"grounds.asc",groundgrid,xy,yy,"%.0f")
                ascii_grid(casebase/"distance.asc",distancegrid,xy,yy,"%.9f")
                for name,beta in BETA:
                    resistance=np.full(d.shape,NO)
                    resistance[connect]=np.exp(beta*orig_sic[connect]/100.)
                    if not(np.isfinite(resistance[connect]).all() and np.all(resistance[connect]>0)):
                        raise ValueError("Nonfinite source resistance")
                    habitat=casebase/f"resistance_{name}.asc"
                    ascii_grid(habitat,resistance,xy,yy,"%.12f")
                    manifest.append({"case_id":group,"year":year,"other_island":other,"date":date,
                        "site":site,"scenario":name,"beta":beta,"resistance_raster":str(habitat.relative_to(OUT)),
                        "source_raster":str((casebase/"source.asc").relative_to(OUT)),
                        "ground_raster":str((casebase/"grounds.asc").relative_to(OUT)),
                        "distance_raster":str((casebase/"distance.asc").relative_to(OUT)),
                        "n_original_matched_GPS_pixels":len(seen),
                        "n_source_valid_GPS_pixels_in_fixed_distance_bins":good_visits})
            print(f"ORIGINAL_GPS_ICE_DATE_BUILT={date} site={site}",flush=True)
    if len(cases)!=90 or len(visitrows)==0:
        raise ValueError(f"Source-locked cases missing: {len(cases)}")
    csvwrite(OUT/"gps_original_source_pixel_visits.csv",visitrows)
    csvwrite(OUT/"island_day_source_domain_support.csv",cases)
    csvwrite(OUT/"fixed_270_circuit_scenario_manifest.csv",manifest)
    supported=[r for r in cases if r["status"]=="READY"]
    if len(manifest)!=3*len(supported):
        raise ValueError("Three hypothetical Circuitscape models not aligned")
    summary={"source_status":"READY_FOR_NATIVE_CIRCUITSCAPE" if len(supported)==90 else "SOURCE_SUPPORT_PARTIAL",
       "source_GPS_original_313_csv_sha256":locked["native_GPS_source_hash"],
       "source_GPS_original_deployments":len(tracks),
       "source_SIC_Doi":satellite.DOI,
       "source_days":len(all_dates),"original_paired_island_days":len(cases),
       "supported_island_days":len(supported),"source_supported_scenarios":len(manifest),
       "original_matched_GPS_unique_pixel_island_days":len(visitrows),
       "eligible_GPS_pixel_island_days":sum(r["n_source_valid_GPS_pixels_in_radial_domain"] for r in cases),
       "source_ice_sha256_per_day":{x["date"]:x["sha256"] for x in original_receipts["source_original_daily_netcdfs"]},
       "models":[name for name,beta in BETA],"science":
       "Hypothetical radial outward marine circuits; input geometry independent of within-day GPS outcome fixes"}
    (OUT/"source_and_model_preflight.json").write_text(json.dumps(summary,indent=2)+"\n")
    print("NATIVE_DAILY_PREP="+json.dumps({k:summary[k] for k in (
        "source_status","source_days","original_paired_island_days","supported_island_days",
        "source_supported_scenarios","eligible_GPS_pixel_island_days")}),flush=True)
    if len(supported)<60:raise SystemExit(2)
if __name__=="__main__":
    main()
