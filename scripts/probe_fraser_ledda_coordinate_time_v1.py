"""Outcome-sealed Ledda 2011/2014 independent Fraser HDF5 geolocation and clock gate.

Select 1-km grid cell based EXCLUSIVELY on projected x/y and independent
stored 2-D lat/lon, not on bird locations after movement or ice classes.
Read only x, y, time, date_alt, global/time metadata, and 2-D location values
at 2 candidate cells. NEVER read Fast_Ice_Time_series variable.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import sys

import h5py
import numpy as np
from pyproj import Transformer

sys.path.insert(0,str(Path(__file__).resolve().parent))
import probe_fraser_remote_hdf5_schema_v1 as remote

SITE_LAT = -74.228
SITE_LON = -130.784
YEARS = (2011,2014)
PROJECTIONS = ("EPSG:3412","EPSG:3031")
MAX_LOCATION_RESIDUAL_KM = 3.0


def haversine_km(lat1, lon1, lat2, lon2):
    p=math.pi/180
    a=math.sin((lat2-lat1)*p/2)**2 + math.cos(lat1*p)*math.cos(lat2*p)*math.sin((lon2-lon1)*p/2)**2
    return 6371.0088*2*math.asin(min(1.0,math.sqrt(max(0.,a))))


def safe_attr(a):
    """Scalar/string metadata only. No arbitrary structured array payload."""
    if isinstance(a, bytes):
        return a.decode("utf-8","replace")[:180]
    if isinstance(a,str):
        return a[:180]
    if isinstance(a,np.ndarray):
        if a.size > 12:
            return {"status":"OMITTED_LONG_METADATA","shape":list(a.shape)}
        return [safe_attr(z) for z in a.tolist()]
    if isinstance(a,(np.integer,np.floating,int,float,bool)):
        return a.item() if hasattr(a,"item") else a
    return str(a)[:100]


def get_public_metadata(obj,fields):
    return {k:safe_attr(obj.attrs[k]) for k in fields if k in obj.attrs}


def examine_axis_only(f, *, site_lon=SITE_LON,site_lat=SITE_LAT):
    x=np.asarray(f["x"][:])
    y=np.asarray(f["y"][:])
    time=np.asarray(f["time"][:])
    date_alt=np.asarray(f["date_alt"][:])
    if x.shape!=(5625,) or y.shape!=(4700,) or time.shape!=(24,) or date_alt.shape!=(24,):
        raise ValueError("Unexpected independently frozen HDF5 dimensions")
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError("Nonfinite axes")
    # NetCDF polar grids may store y north-to-south in DESCENDING order.
    # Strictly monotonic in EITHER direction is required; the sign is not
    # chosen using physical ice or penguin observation outcomes.
    dx = np.diff(x)
    dy = np.diff(y)
    x_up = bool(np.all(dx>0))
    x_down = bool(np.all(dx<0))
    y_up = bool(np.all(dy>0))
    y_down = bool(np.all(dy<0))
    if not (x_up or x_down) or not (y_up or y_down):
        raise ValueError("Neither increasing nor decreasing regular axes")
    cases=[]
    for projection in PROJECTIONS:
        X,Y=Transformer.from_crs("EPSG:4326",projection,always_xy=True).transform(site_lon,site_lat)
        col=int(np.argmin(np.abs(x-X)))
        row=int(np.argmin(np.abs(y-Y)))
        ll_lat=float(f["latitude"][row,col])
        ll_lon=float(f["longitude"][row,col])
        err=haversine_km(site_lat,site_lon,ll_lat,ll_lon)
        cases.append({
            "EPSG":projection,
            "projected_easting_m":float(X),
            "projected_northing_m":float(Y),
            "nearest_cell_row":row,
            "nearest_cell_col":col,
            "nearest_cell_x_m":float(x[col]),
            "nearest_cell_y_m":float(y[row]),
            "independent_cell_lat":ll_lat,
            "independent_cell_lon":ll_lon,
            "geodetic_residual_km":err,
        })
    cases.sort(key=lambda z:z["geodetic_residual_km"])
    choice=cases[0]
    return {
        "x": {"first":float(x[0]),"last":float(x[-1]),"direction":"increasing" if x_up else "decreasing","signed_step_m_median":float(np.median(dx))},
        "y": {"first":float(y[0]),"last":float(y[-1]),"direction":"increasing" if y_up else "decreasing","signed_step_m_median":float(np.median(dy))},
        "time_values":time.tolist(),
        "date_alt_values":date_alt.tolist(),
        "time_attrs":get_public_metadata(f["time"],("units","calendar","long_name","description")),
        "date_alt_attrs":get_public_metadata(f["date_alt"],("long_name","description","units")),
        "geodetic_options":cases,
        "coordinate_candidate":choice,
        "coordinate_verified":choice["geodetic_residual_km"]<=MAX_LOCATION_RESIDUAL_KM,
        "selected_cell_dependent_on_ice_state":False,
        "physical_ice_class_values_read":0,
    }


def probe(year):
    if year not in YEARS:
        raise ValueError("Frozen years only")
    out={"year":year,"status":"NOT_RUN","physical_ice_values_read":0}
    fileobj=None
    try:
        fileobj=remote.LimitedHTTPRangeFile(remote.URL.format(year=year))
        with h5py.File(fileobj,"r") as f:
            outcome=examine_axis_only(f)
            out.update(outcome)
            out["status"]="COORD_TIME_VERIFIED" if outcome["coordinate_verified"] else "HOLD_GEODETIC_RESIDUAL"
    except Exception as e:
        out["status"]="HOLD_COORD_TIME_NOT_VERIFIED"
        out["error_type"]=type(e).__name__
        out["error_message"]=str(e)[:250]
    finally:
        out["http_206_range_requests"]=fileobj.request_count if fileobj else 0
        out["http_download_bytes"]=fileobj.bytes_network if fileobj else 0
        if fileobj:
            fileobj.close()
    return out


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args()
    scans=[probe(y) for y in YEARS]
    data={
        "audit_id":"fraser-ledda-2011-2014-preoutcome-geocoordinate-time-v1",
        "contract":"contracts/EMPEROR_LEDDA_FRASER_HDF5_TIME_GEO_GATE_V1.json",
        "source":"https://doi.org/10.26179/5d267d1ceb60c",
        "Ledda_site_wgs84":[SITE_LAT,SITE_LON],
        "results":scans,
        "total_http_download_bytes":sum(z["http_download_bytes"] for z in scans),
        "all_frozen_years_validated":all(z["status"]=="COORD_TIME_VERIFIED" for z in scans),
        "physical_ice_cell_values_read":0,
        "penguin_biology_new_values_read":0,
        "causal_fit_executed":False,
        "decision":"READY_TO_FREEZE_EXACT_PIXEL_TIME_COMPOSITE" if all(z["status"]=="COORD_TIME_VERIFIED" for z in scans) else "HOLD_COORDINATE_TIME_NOT_VERIFIED",
    }
    payload=json.dumps(data,ensure_ascii=False,indent=2)+"\n"
    args.out.write_text(payload,encoding="utf8")
    print(payload,end="")


if __name__=="__main__":
    main()
