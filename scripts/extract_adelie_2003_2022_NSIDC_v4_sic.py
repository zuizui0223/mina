#!/usr/bin/env python3
"""Independent NOAA/NSIDC v4 monthly measured SIC 100-km colony-mean source.
Only source-derived SIC values are archived (no original NetCDF redistribution).
"""
from __future__ import annotations
import argparse,calendar,datetime,hashlib,json,math,time,urllib.request
from urllib.parse import quote
from pathlib import Path
from io import BytesIO
import numpy as np,pandas as pd
from netCDF4 import Dataset
from pyproj import Transformer, Geod
from scipy.spatial import cKDTree
from extract_adelie_2003_2022_DEEPAA_coastal_and_open import (
   sites_from_original_census,YEARS,R,xyz)

SOURCE="https://coastwatch.pfeg.noaa.gov/erddap/griddap/nsidcG02202v4shmday.nc"
GRID_CRS="EPSG:3412" # NSIDC Southern Hemisphere original Hughes 1980 polar stereographic
GRID_SHA_PRECHECK="f3d4eb78dd6990de64d261090087bbe293424b6fad269f50c6840d55418f2c13"
def download_year(year):
    query=("cdr_seaice_conc_monthly"
      f"[(%d-06-01T00:00:00Z):1:(%d-10-01T00:00:00Z)]"%(year,year)
      +"[(4337500.0):1:(-3937500.0)]"
      +"[(-3937500.0):1:(3937500.0)]")
    url=SOURCE+"?"+quote(query,safe=":()/.-_?")
    for attempt in range(4):
        try:
            request=urllib.request.Request(url,headers={
              "User-Agent":"Independent-Antarctic-Ecology-Open-Data/1.0",
              "Accept":"application/x-netcdf,*/*"})
            with urllib.request.urlopen(request,timeout=200) as r:
                b=r.read(6_000_000)
                if len(b)>=6_000_000:raise ValueError("Source year NetCDF unexpectedly large")
            if not b.startswith((b"CDF",b"\x89HDF")):raise ValueError("Source year not NetCDF "+repr(b[:90]))
            return b,url
        except Exception:
            if attempt==3:raise
            time.sleep(3*(attempt+1))
    raise AssertionError("Unreachable")
def main(args):
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    sites,counts=sites_from_original_census(args.mapppd,out)
    geod=Geod(ellps="WGS84")
    rows=[]; receipts=[]; indexes=None;grid_checksum=None
    for year in YEARS:
        b,url=download_year(year)
        with Dataset("in-memory.nc",memory=b) as n:
            if not {"xgrid","ygrid","time","cdr_seaice_conc_monthly"}<=set(n.variables):
                raise ValueError("STOP NOAA original monthly variable missing")
            x=np.asarray(n.variables["xgrid"][:],float)
            y=np.asarray(n.variables["ygrid"][:],float)
            times=np.asarray(n.variables["time"][:],float)
            v=np.asarray(np.ma.filled(n.variables["cdr_seaice_conc_monthly"][:],np.nan),dtype=float)
            if v.shape!=(5,332,316):raise ValueError("STOP NOAA monthly native shape "+str(v.shape))
            if not np.all(np.diff(times)>0):raise ValueError("STOP non-monotone monthly time")
            if (year==2018):
                # Re-query same original 2018 June month subset independently to guard y and x axis order.
                check=hashlib.sha256(x.tobytes()+y.tobytes()).hexdigest()
                grid_checksum=check
            m=0
            if indexes is None:
                yy,xx=np.meshgrid(y,x,indexing="ij")
                lon,lat=Transformer.from_crs(GRID_CRS,4326,always_xy=True).transform(xx.ravel(),yy.ravel())
                valid=np.flatnonzero(np.isfinite(lon)&np.isfinite(lat)&(np.abs(lat)<=90))
                tree=cKDTree(xyz(lon[valid],lat[valid]))
                pool=tree.query_ball_point(xyz(sites.lon.to_numpy(float),sites.lat.to_numpy(float)),
                                            2*np.sin(100.7/(2*R)))
                indexes=[]
                for i,site in sites.iterrows():
                    a=valid[np.asarray(pool[i],dtype=int)]
                    _,_,dist=geod.inv(np.full(len(a),site.lon),np.full(len(a),site.lat),lon[a],lat[a])
                    a=a[np.asarray(dist)<=100000]
                    if len(a)<10:raise ValueError("STOP NOAA fewer than 10 25km grid cells near "+str(site.site_id))
                    indexes.append(a)
            else:
                # Never silently accept a changed grid layout.
                if len(x)!=316 or len(y)!=332:raise ValueError("STOP grid coordinate count changed")
            for im in range(5):
                date=datetime.datetime.utcfromtimestamp(float(times[im]))
                if (date.year,date.month)!=(year,im+6):raise ValueError("STOP selected NOAA year/month mismatch "+str((date,year,im)))
                flat=v[im].reshape(-1)
                for i,site in sites.iterrows():
                    ids=indexes[i]
                    vv=flat[ids]
                    good=vv[np.isfinite(vv)&(vv>=0)&(vv<=1)]
                    rows.append({"site_id":site.site_id,"year":year,"month":im+6,
                        "sic_100km_fraction":float(good.mean()) if len(good)>=5 else np.nan,
                        "n_25km_grid_cells_in_geodesic_circle":len(ids),
                        "n_valid_ocean_sic_pixels":int(len(good)),
                        "valid_grid_fraction":float(len(good)/len(ids))})
        receipts.append({"year":year,"source":url,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()})
        print("NOAA NSIDC v4 original continuous SIC",year,"months",5,flush=True)
    months=pd.DataFrame(rows)
    months.to_csv(out/"NSIDC_V4_CDR_monthly_43site_JunOct_2003_2022_100km.csv",index=False)
    years=months.groupby(["site_id","year"],as_index=False).agg(
       annual_sic_mean=("sic_100km_fraction","mean"),
       n_months=("sic_100km_fraction","count"),
       min_month_valid_pixels=("n_valid_ocean_sic_pixels","min"),
       min_month_valid_grid_frac=("valid_grid_fraction","min"))
    years["is_complete"]=years.n_months.eq(5)
    years["annual_sic_mean"]=years.annual_sic_mean.where(years.is_complete)
    years=years.rename(columns={"year":"season"})
    years.to_csv(out/"NSIDC_V4_CDR_annual_43site_JunOct_2003_2022_100km.csv",index=False)
    joined=counts.merge(years,on=["site_id","season"],how="left",validate="many_to_one")
    joined.to_csv(out/"observed_MAPPPD_nests_years_with_original_NSIDC_SIC.csv",index=False)
    report={
        "status":"PHYSICAL_SOURCE_CONTINUOUS_MEASURED_SIC_V4_EXTRACTED",
        "source":"NOAA/NSIDC G02202 V4, CoastWatch ERDDAP Southern hemisphere monthly 25 km",
        "source_url":SOURCE,"native_crs":GRID_CRS,"coordinate_digest_2018":grid_checksum,
        "years":YEARS,"months":[6,7,8,9,10],
        "n_sites":int(len(sites)),"n_siteyears":int(len(years)),
        "source_nest_season_records":int(len(counts)),
        "n_complete_monthly_sic_siteyears":int(years.is_complete.sum()),
        "n_source_nest_siteyears_with_complete_sic":int(joined.is_complete.fillna(False).sum()),
        "mean_sic_fraction_over_observed_months":float(months.sic_100km_fraction.mean()),
        "raw_year_request_shas":receipts,
        "no_original_NSIDC_netcdf_redistributed":True,
        "limitations":["25-km SIC measured independently from 6.25-km DEEP-AA polynya classes",
                       "Adjacent 100km buffers have overlapping grid-cell source support",
                       "At least five actual valid ocean pixels required per site-month",
                       "No outcome regression, adjusted effect, forward prediction or causality test"]
    }
    (out/"NSIDC_SOUTH_V4_CDR_SOURCE_QA_RECEIPT.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="raw_year_request_shas"},indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--mapppd",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args();main(a)
