#!/usr/bin/env python3
"""Original NOAA/NSIDC G02202 v6 1978–2026 monthly Antarctic SIC => site-year predictors.

Computes marine field predictors ONLY for 719 original APBP source location IDs,
with no bird counts, ecological effects, p-values or island-area interactions.
Precommitted exposure: Oct+Nov start season t, offshore 25–75 and 75–150km,
site-specific 1981–2010 climatology, at least 4 valid CDR ocean cells/month.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import tempfile
from urllib.parse import urlparse

import numpy as np
from netCDF4 import Dataset, num2date
from pyproj import Transformer
import requests

from audit_apbp_darwincore_source_v1 import (
    audited_schema,fetch_original,metadata,rows_for,safe_zip,
)

URL=(
    "https://noaadata.apps.nsidc.org/NOAA/G02202_V6/south/aggregate/"
    "sic_pss25_197811-202609_v06r00.nc"
)
DOI="10.7265/b18j-z797"
MAX_BYTES=140_000_000
EXPECTED_PUBLIC_BYTES=117_472_635
YEARS=tuple(range(1979,2023))
BASELINE_YEARS=tuple(range(1981,2011))
RADII=((25000,75000),(75000,150000))
MIN_CELLS=4
MIN_CLIMATOLOGY_YEARS=20
VAR="cdr_seaice_conc_monthly"


def download_nsidc(target):
    with requests.get(URL,timeout=(25,120),stream=True,
                      headers={"User-Agent":"mina-penguin-macro-NSIDC-CDR-v6-source/1.0"}) as response:
        response.raise_for_status()
        resolved=urlparse(response.url)
        if resolved.scheme!="https" or resolved.hostname!="noaadata.apps.nsidc.org":
            raise ValueError("SOURCE_STOP NOAA/NSIDC source redirected off publisher")
        n=0
        digest=hashlib.sha256()
        with target.open("wb") as file:
            for chunk in response.iter_content(65536):
                if not chunk: continue
                n+=len(chunk)
                if n>MAX_BYTES:
                    raise ValueError("SOURCE_STOP NOAA v6 monthly netCDF exceeded source limit")
                digest.update(chunk)
                file.write(chunk)
    if n<100_000_000:
        raise ValueError("SOURCE_STOP incomplete original monthly aggregate")
    return {"source_file_sha256":digest.hexdigest(),
            "source_file_bytes":n,"publisher_index_reported_bytes":EXPECTED_PUBLIC_BYTES,
            "version":"NOAA/NSIDC G02202 V6 Southern hemisphere"}



def original_apbp_source_sites():
    """Use original Event core, without importing rock/coastline GIS libraries."""
    from collections import defaultdict
    import io
    raw=fetch_original()
    assert hashlib.sha256(raw).hexdigest() == (
        "afa947f39d9ad7382266d5be64c70f9fe4e84ffb6e2838c1369e043caae09abf"
    ), "SOURCE_VERSION_STOP APBP original source drift"
    audited_schema(raw)
    with safe_zip(raw) as zz:
        table=next(t for t in metadata(zz) if t["rowtype"]=="Event")
        events=list(rows_for(zz,table))
    sites=defaultdict(list)
    for core_id,_,row in events:
        site=row.get("locationID","").strip()
        if not site:
            continue
        try:
            lat=float(row["decimalLatitude"])
            lon=float(row["decimalLongitude"])
        except (TypeError,ValueError,KeyError) as exc:
            raise ValueError("SOURCE_STOP missing original APBP site latitude/longitude") from exc
        if not (-90<=lat<=-60 and -180<=lon<=180):
            raise ValueError("SOURCE_STOP APBP coordinate outside Antarctic coverage")
        sites[site].append({"lon":lon,"lat":lat})
    if len(sites)!=719:
        raise ValueError("SOURCE_VERSION_STOP original APBP locationID count drift")
    # Within-location source coordinates must not be conflated if they disagree.
    def approx_distance(a,b):
        return 111195*math.hypot(a["lat"]-b["lat"],
                                  math.cos(math.radians(a["lat"]))*(a["lon"]-b["lon"]))
    if any(approx_distance(evs[0],e)>1000
           for evs in sites.values() for e in evs[1:]):
        raise ValueError("POINT_STOP site source coordinates drift over 1km")
    return sites


def netcdf_schema(source):
    if VAR not in source.variables or "time" not in source.variables:
        raise ValueError("SCHEMA_STOP missing CDR SIC or time: "+str(list(source.variables)[:25]))
    xname="x" if "x" in source.variables else "xgrid"
    yname="y" if "y" in source.variables else "ygrid"
    if xname not in source.variables or yname not in source.variables:
        raise ValueError("SCHEMA_STOP no projected x/y grid center vectors")
    x=np.asarray(source.variables[xname][:],dtype=float)
    y=np.asarray(source.variables[yname][:],dtype=float)
    grid=source.variables[VAR]
    if not (x.ndim==1 and y.ndim==1 and len(x)==316 and len(y)==332):
        raise ValueError("CRS_STOP original Antarctic grid is not expected 316×332")
    for name,values in ((xname,x),(yname,y)):
        if not np.all(np.isfinite(values)) or np.any(np.abs(np.abs(np.diff(values))-25000)>5):
            raise ValueError("CRS_STOP irregular original 25km "+name+" coordinates")
        attr=str(getattr(source.variables[name],"units","")).lower()
        if attr not in ("meters","meter","m"):
            raise ValueError("CRS_STOP original projected grid units are not meters")
    if grid.ndim!=3 or grid.shape[1:]!=(len(y),len(x)):
        raise ValueError("SCHEMA_STOP sea ice field dimension mismatch")
    if grid.shape[0]!=len(source.variables["time"]):
        raise ValueError("SCHEMA_STOP sea ice year dimension mismatch")
    unit=str(getattr(grid,"units","")).lower().strip()
    if unit not in ("1","fraction","fractional",""):
        raise ValueError("SCHEMA_STOP original SIC units not CF 0-1 fraction: "+unit)
    times=source.variables["time"]
    datevals=num2date(times[:],units=getattr(times,"units"),
                       calendar=getattr(times,"calendar","standard"),
                       only_use_cftime_datetimes=False,
                       only_use_python_datetimes=False)
    lookup={}
    for i,date in enumerate(datevals):
        ym=(int(date.year),int(date.month))
        if ym in lookup:
            raise ValueError("SCHEMA_STOP duplicate monthly timestamp")
        lookup[ym]=i
    return x,y,grid,lookup,{
        "variables":list(source.variables),
        "sea_ice_dimensions":grid.dimensions,
        "sea_ice_source_units":unit,
        "projection_grid":"EPSG:3412 (NOAA/NSIDC declared southern polar stereographic)",
        "original_x_vector_name":xname,
        "original_y_vector_name":yname,
        "months_in_original_file":len(lookup),
        "original_year_range":[min(y for y,m in lookup),max(y for y,m in lookup)],
    }


def offshore_windows(sites,x,y):
    to_grid=Transformer.from_crs("EPSG:4326","EPSG:3412",always_xy=True)
    X,Y=np.meshgrid(x,y,indexing="xy")
    windows={}
    for site,events in sorted(sites.items()):
        lon,lat=events[0]["lon"],events[0]["lat"]
        px,py=to_grid.transform(lon,lat)
        if not all(math.isfinite(v) for v in (px,py)):
            raise ValueError("POINT_STOP nonfinite APBP WGS84 projection to NOAA")
        squared=(X-px)**2+(Y-py)**2
        windows[site] = {
            f"{a//1000}_{b//1000}km":np.where((squared >= a*a)&(squared < b*b))
            for a,b in RADII
        }
    return windows


def monthly_slice(arr):
    if np.ma.isMaskedArray(arr):
        out=np.asarray(arr.filled(np.nan),dtype=float)
    else:
        out=np.asarray(arr,dtype=float)
    out[~np.isfinite(out)]=np.nan
    valid=out[np.isfinite(out)]
    if valid.size and (np.min(valid)<-1e-4 or np.max(valid)>1.0001):
        raise ValueError("GRID_STOP original SIC not scaled into valid 0–1 ocean fraction")
    if out.ndim!=2:
        raise ValueError("GRID_STOP sea ice month must be 2-D")
    return out


def site_month_stat(month,idx):
    vv=month[idx]
    finite=vv[np.isfinite(vv)]
    if len(finite)<MIN_CELLS:
        return {"sic":None,"valid_cells":len(finite)}
    return {"sic":float(finite.mean()),"valid_cells":len(finite)}


def seasons_values(month_data,windows):
    # month_data contains only exactly October+November for 1979–2022.
    out={}
    for site,rings in windows.items():
        site_rows={}
        for year in YEARS:
            item={}
            for band,ind in rings.items():
                octkey=(year,10)
                novkey=(year,11)
                if octkey not in month_data or novkey not in month_data:
                    item[band]=(None,0,0)
                    continue
                a=site_month_stat(month_data[octkey],ind)
                b=site_month_stat(month_data[novkey],ind)
                value=(a["sic"]+b["sic"])/2 if a["sic"] is not None and b["sic"] is not None else None
                item[band]=(value,a["valid_cells"],b["valid_cells"])
            site_rows[year]=item
        out[site]=site_rows
    return out


def climatology(data):
    climatology={}
    bands=(f"{a//1000}_{b//1000}km" for a,b in RADII)
    for site,years in data.items():
        climatology[site]={}
        for band in (f"{a//1000}_{b//1000}km" for a,b in RADII):
            baseline=[years[y][band][0] for y in BASELINE_YEARS
                      if y in years and band in years[y] and years[y][band][0] is not None]
            climatology[site][band]=(
                float(np.mean(baseline)) if len(baseline)>=MIN_CLIMATOLOGY_YEARS else None,
                len(baseline))
    return climatology


def receipt_rows(values,baselines):
    rows=[]
    for site,years in values.items():
        for t,season in years.items():
            result={"original_APBP_locationID":site,"breeding_start_year":t,
                    "source_NSIDC_version":"G02202_v6","marine_ice_data_type":"fraction_offshore_seaice"}
            for band,(v,oct_cells,nov_cells) in season.items():
                baseline,n=baselines[site][band]
                result.update({
                    f"sic_{band}_oct_nov_mean":round(v,7) if v is not None else None,
                    f"sic_{band}_baseline_1981_2010":round(baseline,7) if baseline is not None else None,
                    f"sic_{band}_anomaly":round(v-baseline,7) if v is not None and baseline is not None else None,
                    f"sic_{band}_nvalid_oct_cells":oct_cells,
                    f"sic_{band}_nvalid_nov_cells":nov_cells,
                    f"sic_{band}_nvalid_climatology_years":n,
                })
            rows.append(result)
    return rows


def audit_values(rows,original_schema,provenance):
    classes={}
    for band in ("25_75km","75_150km"):
        field=f"sic_{band}_anomaly"
        raw=f"sic_{band}_oct_nov_mean"
        matched=[x for x in rows if x[field] is not None]
        sites={x["original_APBP_locationID"] for x in matched}
        by_site={}
        for x in matched:
            by_site.setdefault(x["original_APBP_locationID"],[]).append(x[raw])
        constant_zero=sum(all(v==0 for v in vals) for vals in by_site.values())
        classes[band]={
            "site_years_with_baseline_and_valid_oct_nov":len(matched),
            "distinct_sites_with_any_climate_year":len(sites),
            "n_sites_all_summer_seaice_zero_in_observed_years":constant_zero,
            "n_source_years_covered":len(set(x["breeding_start_year"] for x in matched)),
            "climate_sample_fraction_of_all_site_years":round(len(matched)/len(rows),6),
            "exposure_range_in_valid_source_monthly_CDR":[
                min(x[raw] for x in matched),max(x[raw] for x in matched)] if matched else None,
            "observed_seaice_anomaly_range":[
                min(x[field] for x in matched),max(x[field] for x in matched)] if matched else None,
        }
    return {"status":"V5_ORIGINAL_NOAA_MONTHLY_SIC_SITE_YEAR_COVARIATES_NO_ECOLOGICAL_EFFECT",
            "source":provenance,"original_NSIDC_netcdf_schema":original_schema,
            "n_site_ids":len({row["original_APBP_locationID"] for row in rows}),
            "breeding_seasons_per_site":len(YEARS),
            "site_year_source_climate_rows":len(rows),
            "available_seaice_predictors":classes,
            "original_baseline_years":[1981,2010],
            "offshore_bands_km":[[25,75],[75,150]],
            "ocean_cell_minimum_per_month":MIN_CELLS,
            "original_apbp_DwCA_SHA256":"afa947f39d9ad7382266d5be64c70f9fe4e84ffb6e2838c1369e043caae09abf",
            "no_colony_breeding_abundance_values_read":True,
            "fitted_climate_abundance_models":0,
            "not_identifiable":"NSIDC 25km open-water/pack-ice SIC is not local sea-fast-ice nor observed foraging trip distance."}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out-json",required=True)
    p.add_argument("--out-csv",required=True)
    args=p.parse_args()
    output=Path(args.out_json)
    output.parent.mkdir(parents=True,exist_ok=True)
    result={"status":"HOLD_NSIDC_SOURCE_OR_PROJECTION","fitted_climate_abundance_models":0}
    try:
        sites=original_apbp_source_sites()
        if len(sites)!=719:
            raise ValueError("SOURCE_VERSION_STOP unexpected APBP source location count")
        with tempfile.TemporaryDirectory(prefix="noaa-cdr-v6-apbp-") as tmp:
            original=Path(tmp)/"original_south_monthly.nc"
            provenance=download_nsidc(original)
            with Dataset(original,"r") as ds:
                x,y,field,timemap,md=netcdf_schema(ds)
                windows=offshore_windows(sites,x,y)
                months={}
                for year in YEARS:
                    for m in (10,11):
                        index=timemap.get((year,m))
                        if index is not None:
                            months[(year,m)]=monthly_slice(field[index,:,:])
        values=seasons_values(months,windows)
        baselines=climatology(values)
        rows=receipt_rows(values,baselines)
        out=Path(args.out_csv)
        out.parent.mkdir(parents=True,exist_ok=True)
        with out.open("w",newline="",encoding="utf-8") as file:
            writer=csv.DictWriter(file,fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        result=audit_values(rows,md,provenance)
        result["derived_offshore_seaice_CSV_sha256"]=hashlib.sha256(out.read_bytes()).hexdigest()
    except Exception as e:
        result["error_type"]=type(e).__name__
        result["error"]=str(e)[:520]
    output.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if result["status"].startswith("HOLD"):
        raise SystemExit(2)


if __name__=="__main__":
    main()
