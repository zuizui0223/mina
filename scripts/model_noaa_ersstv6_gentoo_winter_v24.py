#!/usr/bin/env python3
"""V24 NOAA ERSSTv6 regionally smoothed winter SST versus BAS Gentoo growth.

Exploratory post-V23 effect; frozen source, geography, months and identical 8 windows.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import tempfile
from urllib.parse import urlparse
import requests
import numpy as np
from netCDF4 import Dataset,num2date
import audit_bas_south_georgia_source_v21 as v21
import fit_bas_bird_maiviken_nests_v22 as v22
import compare_bas_gentoo_near_far_v23 as v23

SOURCE="https://psl.noaa.gov/thredds/ncss/grid/Datasets/noaa.ersst.v6/sst.mnmean.nc"
REQUEST={
    "var":"sst",
    "north":"-52","south":"-62",
    "west":"312","east":"326",
    "time_start":"2009-01-01T00:00:00Z",
    "time_end":"2019-12-31T00:00:00Z",
    "accept":"netcdf4"
}
MAX_BYTES=12*1024*1024
SITES={
    "bird":(-54.000,321.950),
    "maiviken":(-54.246,323.490),
    "signy":(-60.7167,314.400)
}
WINTER_MONTHS=(7,8,9)
YEARS=tuple(range(2011,2020))
WINDOWS=tuple(range(2011,2019))
EXPECTED_V23_DELTA=1.0154800142899
SOURCE_URLS={
    "bird":"https://www.bas.ac.uk/polar-operations/sites-and-facilities/facility/bird-island/",
    "maiviken":"https://data.bas.ac.uk/full-record.php?id=GB/NERC/BAS/PDC/01487",
    "signy":"https://legacy.bas.ac.uk/about_bas/our_history/stations_and_refuges/signy.php"
}

def fetch_environment():
    response=requests.get(SOURCE,params=REQUEST,timeout=55,stream=True,
                          headers={"User-Agent":"mina-v24-NOAA-ERSSTv6-original-research/1.0",
                                   "Accept":"application/x-netcdf,application/octet-stream,*/*"})
    try:
        final=urlparse(response.url)
        if final.scheme!="https" or final.hostname not in {"psl.noaa.gov","www.psl.noaa.gov"}:
            raise ValueError("SOURCE_STOP redirected outside NOAA PSL")
        response.raise_for_status()
        chunks=[];size=0
        for chunk in response.iter_content(chunk_size=65536):
            size+=len(chunk)
            if size>MAX_BYTES:
                raise ValueError("SOURCE_STOP netCDF exceeds frozen 12MiB max")
            chunks.append(chunk)
        raw=b"".join(chunks)
        if not (raw.startswith(b"CDF") or raw.startswith(b"\x89HDF\r\n\x1a\n")):
            raise ValueError("SOURCE_STOP NOAA response not original netCDF: "+raw[:120].decode("utf-8","replace"))
        meta={"source_original_url":SOURCE,"request_params":REQUEST,"final_url":response.url,
              "mime":response.headers.get("Content-Type"),
              "sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),
              "format_verified_netcdf":True}
        return raw,meta
    finally:
        response.close()

def ocean_grid_cell(lat_axis,lon_axis,latitude,longitude):
    la=np.asarray(lat_axis,dtype=float)
    lo=np.asarray(lon_axis,dtype=float)
    if la.size<2 or lo.size<2 or np.any(~np.isfinite(la)) or np.any(~np.isfinite(lo)):
        raise ValueError("SOURCE_STOP incomplete or invalid SST axes")
    i=int(np.argmin(np.abs(la-latitude)))
    j=int(np.argmin(np.abs(lo-longitude)))
    if abs(float(la[i])-latitude)>1.1 or abs(float(lo[j])-longitude)>1.1:
        raise ValueError("SOURCE_STOP site too far from original SST grid center")
    return i,j,{"lat":float(la[i]),"lon_0_360":float(lo[j]),"source_lat_offset":float(la[i]-latitude),
                "source_lon_offset":float(lo[j]-longitude)}

def winters_from_netcdf(raw):
    with tempfile.TemporaryDirectory() as d:
        path=Path(d)/"original_NOAA_ERSSTv6_subset.nc"
        path.write_bytes(raw)
        with Dataset(str(path),"r") as ds:
            if "sst" not in ds.variables or "time" not in ds.variables:
                raise ValueError("SCHEMA_STOP monthly source missing SST/time")
            tvar=ds.variables["time"]
            times=num2date(tvar[:],units=tvar.units,
                            calendar=getattr(tvar,"calendar","standard"))
            lat_name="lat" if "lat" in ds.variables else "latitude"
            lon_name="lon" if "lon" in ds.variables else "longitude"
            if lat_name not in ds.variables or lon_name not in ds.variables:
                raise ValueError("SCHEMA_STOP source latitude/longitude missing")
            lat=ds.variables[lat_name][:]
            lon=ds.variables[lon_name][:]
            v=ds.variables["sst"]
            units=str(getattr(v,"units","")).lower()
            if not any(x in units for x in ("degc","celsius","degree_c","degrees_c")):
                raise ValueError("SCHEMA_STOP NOAA SST units not Celsius "+units)
            dim=tuple(v.dimensions)
            if len(dim)!=3 or set(dim)!={tvar.dimensions[0],ds.variables[lat_name].dimensions[0],
                                        ds.variables[lon_name].dimensions[0]}:
                raise ValueError("SCHEMA_STOP SST dimensions unexpected")
            a=np.ma.asarray(v[:])
            order=(dim.index(tvar.dimensions[0]),dim.index(ds.variables[lat_name].dimensions[0]),
                   dim.index(ds.variables[lon_name].dimensions[0]))
            data=np.ma.transpose(a,order)
            if data.shape!=(len(times),len(lat),len(lon)):
                raise ValueError("SOURCE_STOP original SST axes and data mismatch")
            points={};annual={}; missing={}; source_value_failures={}; grid_spacing={
                "lat_deg":float(np.median(np.abs(np.diff(lat)))),
                "lon_deg":float(np.median(np.abs(np.diff(lon))))
            }
            for site,(slat,slon) in SITES.items():
                i,j,geo=ocean_grid_cell(lat,lon,slat,slon)
                points[site]=geo
                byyear=defaultdict(dict)
                # Source-diagnostic only: distinguish actual original masks from
                # invalid numerical values without changing any accepted SST.
                invalid_reason=defaultdict(dict)
                for k,t in enumerate(times):
                    year,month=int(t.year),int(t.month)
                    if year not in YEARS or month not in WINTER_MONTHS:
                        continue
                    cell=data[k,i,j]
                    if np.ma.is_masked(cell):
                        invalid_reason[year][month]="ORIGINAL_NETCDF_MASK"
                        continue
                    value=float(cell)
                    if not math.isfinite(value):
                        invalid_reason[year][month]="NONFINITE_SOURCE_VALUE"
                        continue
                    if not -3<=value<=35:
                        invalid_reason[year][month]="OUTSIDE_FROZEN_PHYSICAL_RANGE"
                        continue
                    if month in byyear[year]:
                        raise ValueError("SOURCE_STOP source NOAA repeats month in selected original cell")
                    byyear[year][month]=value
                incomplete={year:sorted(set(WINTER_MONTHS)-set(byyear[year])) for year in YEARS
                            if len(byyear[year])!=3}
                missing[site]=incomplete
                source_value_failures[site]={
                    str(y):{str(m):reason for m,reason in months.items()}
                    for y,months in invalid_reason.items() if months
                }
                annual[site]={year:float(np.mean([byyear[year][m] for m in WINTER_MONTHS]))
                              for year in YEARS if len(byyear[year])==3}
            return annual,{
                "source_variable":"sst",
                "source_units":units,
                "original_gridded_cell_centers":points,
                "original_grid_spacing":grid_spacing,
                "unobserved_winter_months":missing,
                "source_missing_value_reasons_by_site_year_month":source_value_failures,
                "valid_winter_year_counts":{site:len(x) for site,x in annual.items()},
                "historical_NetCDF_time_axis_entries":len(times),
                "prebreeding_fixed_original_months":list(WINTER_MONTHS),
                "no_cell_search_after_environment_values":True
            }

def environmental_vs_growth(winter,original_growth):
    # All 9 winters at all 3 physical sites required. No partial-year rescue.
    if sorted(original_growth)!=list(WINDOWS):
        return {"status":"STOP_V23_GROWTH_WINDOWS_CHANGED","effect_computed":False}
    if any(set(d)!=set(YEARS) for d in winter.values()) or set(winter)!=set(SITES):
        return {"status":"STOP_INCOMPLETE_ORIGINAL_ERSST_WINTER_DATA","effect_computed":False}
    difference={site:{y:winter[site][y+1]-winter[site][y] for y in WINDOWS}
                for site in SITES}
    pairs=(("near_Bird_Maiviken","bird","maiviken"),
           ("far_Bird_Signy","bird","signy"),
           ("far_Maiviken_Signy","maiviken","signy"))
    r_env={key:v22.pearson([difference[a][y] for y in WINDOWS],
                           [difference[b][y] for y in WINDOWS]) for key,a,b in pairs}
    r_eco={site:v22.pearson([difference[site][y] for y in WINDOWS],
                            [original_growth[y][site] for y in WINDOWS]) for site in SITES}
    if any(x is None or not math.isfinite(x) for x in list(r_env.values())+list(r_eco.values())):
        return {"status":"STOP_ZERO_VARIANCE_IN_ENV_OR_BIRD_SERIES","effect_computed":False}
    delta=r_env["near_Bird_Maiviken"]-.5*(r_env["far_Bird_Signy"]+r_env["far_Maiviken_Signy"])
    return {
        "status":"NOAA_ERSSTV6_2009_2019_WINTER_REGIONAL_ASSOCIATIONS",
        "effect_computed":True,
        "original_winter_sst_years":list(YEARS),
        "fixed_original_growth_windows":list(WINDOWS),
        "original_regional_winter_sst_C_by_site_year":{
            site:{str(y):value for y,value in years.items()} for site,years in winter.items()
        },
        "winter_sst_year_change_C_by_site_window":{
            site:{str(y):value for y,value in years.items()} for site,years in difference.items()
        },
        "regional_winter_SST_change_pairwise_r":r_env,
        "regional_near_minus_mean_far_SST_change_r":delta,
        "own_site_winter_SST_change_vs_gentoo_growth_r":r_eco,
        "marine_SST_causal_effect_demonstrated":False,
        "independent_island_replication_count":3,
        "statistical_p_value_computed":False,
        "scientific_decision":"EXPLORATORY_COARSE_SST_COMPATIBILITY_ONLY_NOT_MECHANISM"
    }

def read_exact_bird_growth():
    orig={}
    for label,spec in v21.SOURCES.items():
        raw,meta=v21.get_raw(spec["url"])
        expected={"bird_island_v1":v22.SHA_BIRD,
                  "south_georgia_maiviken":v22.SHA_MAIN}[label]
        if meta["sha256"]!=expected:
            raise ValueError("SOURCE_STOP BAS site original changed")
        orig[label]=v22.rows_csv(raw)
    candidate,windows,source_qa=v22.source_metadata_only(
        orig["bird_island_v1"],orig["south_georgia_maiviken"])
    if not v22.nested_support_pass(source_qa):
        raise ValueError("SOURCE_STOP Bird/Maiviken original cohort changed")
    old=v22.analyze_counts(candidate,windows)
    if abs(old["coastal_small_island_vs_large_main_island_growth_pearson_r"]-v23.ORIGINAL_V22_R)>1e-10:
        raise ValueError("SOURCE_STOP frozen V22 original coefficient changed")
    grow=v23.preserved_v22_growth(candidate,windows)
    signy_raw,meta=v21.get_raw(v23.SIGNY_URL)
    if meta["sha256"]!=v23.SIGNY_SHA:
        raise ValueError("SOURCE_STOP Signy original changed")
    signy,source_qa=v23.signy_records(v22.rows_csv(signy_raw))
    reference=v23.compare_near_far(grow,signy)
    if not reference["effect_computed"] or abs(reference["near_minus_mean_far_r"]-EXPECTED_V23_DELTA)>1e-10:
        raise ValueError("SOURCE_STOP pinned original V23 near/far contrast drift")
    # Work strictly within the verified V23 eight-window source roster.
    limited=reference["common_growth_start_years"]
    if limited!=list(WINDOWS):
        raise ValueError("SOURCE_STOP exact V23 year roster changed")
    if any(signy.get(y) is None or signy.get(y+1) is None for y in WINDOWS):
        raise ValueError("SOURCE_STOP original Signy year missing in frozen windows")
    return {y:{**grow[y],"signy":math.log1p(signy[y+1])-math.log1p(signy[y])}
            for y in WINDOWS},reference

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--json",type=Path,required=True)
    args=ap.parse_args()
    result={"status":"HOLD_ORIGINAL_ENVIRONMENT_OR_BIRD","effect_computed":False}
    try:
        growth,v23qa=read_exact_bird_growth()
        raw,meta=fetch_environment()
        winters,qa=winters_from_netcdf(raw)
        ecology=environmental_vs_growth(winters,growth)
        result={
            "status":"V24_ORIGINAL_ERSSTV6_SOURCE_TEST_COMPLETED",
            "predeclared_frozen_contract":"contracts/NOAA_ERSSTV6_GENTOO_WINTER_V24.md",
            "source_receipt":meta,
            "source_geometry":qa,
            "original_V23_near_minus_far_r_reproduced":v23qa["near_minus_mean_far_r"],
            "environmental_comparison":ecology,
            "ecological_effect_fitted":ecology["effect_computed"],
            "scientific_decision":ecology.get("scientific_decision",ecology["status"])
        }
    except Exception as exc:
        result["error_type"]=type(exc).__name__
        result["error"]=str(exc)[:800]
    args.json.parent.mkdir(parents=True,exist_ok=True)
    args.json.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"]=="HOLD_ORIGINAL_ENVIRONMENT_OR_BIRD":
        raise SystemExit(2)

if __name__=="__main__":
    main()
