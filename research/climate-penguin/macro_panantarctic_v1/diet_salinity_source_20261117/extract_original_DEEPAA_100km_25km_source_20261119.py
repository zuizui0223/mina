#!/usr/bin/env python3
"""Native Lin et al. DEEP-AA observed polynya × original 860 isotope-site geometry.
Source gate, no biological Y, no fishing for radius/lag significance.
Contract: POLYNYA_DIRECT_SOURCE_SUPPORT_GATE_20261119_JA.md.
Direct original DEEPAA v1.1.0-2023 ZIP MD5, exact 6.25 km daily Map + LonLat.nc.
"""
from __future__ import annotations
import argparse
import calendar
from collections import Counter,defaultdict
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from netCDF4 import Dataset
from pyproj import CRS, Geod, Proj, Transformer
from scipy.spatial import cKDTree

POLY_MD5="f3f958389cc5e67ac1c4e3a6ee164318"
POLY_SHA256="b05a36aa4e775d69c06e2ffa897a8de8a20318b65f6478298167f73cc9f7c3f9"
OPTICAL_SHA256="dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205"
SOURCE_CSV="matched_860_original_isotope_ocean_ice_site_seasons.csv"
DATE_RE=re.compile(r"(?<!\d)(20(?:0\d|1\d|2[012])\d{4})(?!\d)")
MONTHS=(6,7,8,9,10)
MAIN_RADIUS_KM=100
SECONDARY_RADIUS_KM=25
SOURCE_EPSG=3412
COORDS_EPSG=3031

def digest(path,algo):
    h=hashlib.new(algo)
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(2**21),b""):h.update(b)
    return h.hexdigest()

def get_zip_member(z,n):
    if n not in z.namelist():
        raise ValueError("Published upstream artifact member missing: "+n)
    return pd.read_csv(io.BytesIO(z.read(n)),low_memory=False)

def original_sites(a):
    if digest(a.isotope_zip,"sha256")!=OPTICAL_SHA256:
        raise ValueError("Original 860 site×season source checksum changed")
    with zipfile.ZipFile(a.isotope_zip) as z:
        if z.testzip():raise ValueError("original isotope ZIP CRC corruption")
        d=get_zip_member(z,SOURCE_CSV)
    if (len(d),d.site_id.nunique(),d.source_region.nunique())!=(860,88,13):
        raise ValueError("Original 860/88/13 denominator drift")
    if d.duplicated(["site_id","season"]).any():
        raise ValueError("Original site×season duplicate")
    d=d[["site_id","season","source_region","source_wet_grid_y","source_wet_grid_x"]].copy()
    d["site_id"]=d.site_id.astype(str)
    d["season"]=d.season.astype(int)
    with zipfile.ZipFile(a.centroid_zip) as z:
        if z.testzip():raise ValueError("original Youngflesh centroids ZIP CRC")
        center=get_zip_member(z,"source_site_projected_centroids.csv")
    with zipfile.ZipFile(a.atlas_zip) as z:
        if z.testzip():raise ValueError("original MAPPPD 595 atlas ZIP CRC")
        atlas=get_zip_member(z,"panantarctic_595_site_inventory.csv")
    for v in (center,atlas):
        v["site_id"]=v.site_id.astype(str)
        if v.site_id.duplicated().any():
            raise ValueError("Original coordinates contain repeated original site IDs")
    required={"easting","northing"}
    if not required.issubset(center.columns):
        raise ValueError("Original author Landsat centroid EPSG3031 not present")
    if not {"latitude","longitude"}.issubset(atlas.columns):
        raise ValueError("Original MAPPPD latitude longitude not present")
    original_ids=set(d.site_id)
    center=center.loc[center.site_id.isin(original_ids)].copy()
    if len(center)!=88:raise ValueError("Expected all 88 original geographical Landsat centers")
    trans=Transformer.from_crs(4326,COORDS_EPSG,always_xy=True)
    xa,ya=trans.transform(atlas.longitude.to_numpy(float),atlas.latitude.to_numpy(float))
    coords=np.column_stack([xa,ya])
    tree=cKDTree(coords)
    distance,nearest=tree.query(center[["easting","northing"]].to_numpy(float),k=2)
    center["nearest_id"]=atlas.site_id.to_numpy()[nearest[:,0]]
    center["nearest_distance_m"]=distance[:,0]
    center["second_nearest_distance_m"]=distance[:,1]
    if (center.site_id.ne(center.nearest_id).any()
          or (center.nearest_distance_m>2000).any()
          or (center.second_nearest_distance_m<=2000).any()):
        raise ValueError("Original image centroid does not one-to-one match MAPPPD source within 2km")
    pos=dict(zip(atlas.site_id,range(len(atlas))))
    original=center[["site_id","nearest_distance_m","second_nearest_distance_m"]].copy()
    original["colony_lon"]=original.site_id.map(lambda s:float(atlas.iloc[pos[s]].longitude))
    original["colony_lat"]=original.site_id.map(lambda s:float(atlas.iloc[pos[s]].latitude))
    if original[["colony_lat","colony_lon"]].isna().any().any():
        raise ValueError("Source original site geographical coordinates missing")
    if not original.colony_lat.between(-90,-50).all():
        raise ValueError("Geography source not Antarctic latitudes")
    assert set(original.site_id)==original_ids
    original=original.merge(d.groupby("site_id").source_region.first().reset_index(),
        on="site_id",validate="one_to_one")
    return d,original

def native_map_manifest(z):
    names=z.namelist()
    ll=[n for n in names if Path(n).name.lower()=="lonlat.nc"]
    if len(ll)!=1: raise ValueError("Expected exactly one source native LonLat.nc")
    name_by_day={}
    for name in names:
        if not name.lower().endswith(".nc") or name==ll[0]:continue
        m=DATE_RE.search(Path(name).name)
        if not m:raise ValueError("Native daily source date absent: "+name)
        k=m.group(1)
        dt=pd.Timestamp(k)
        ds=dt.strftime("%Y-%m-%d")
        if ds in name_by_day:raise ValueError("Duplicated source date: "+ds)
        name_by_day[ds]=name
    if len(name_by_day)<1000:raise ValueError("Not a true daily polynya dataset")
    return ll[0],name_by_day

def lonlat_grid(z,latlon_name):
    with Dataset("memory.nc","r",memory=z.read(latlon_name)) as f:
        if not {"Lat","Lon"}.issubset(f.variables):
            raise ValueError("Native grid missing LonLat variables")
        lat=np.ma.asarray(f.variables["Lat"][:],dtype=float).filled(np.nan)
        lon=np.ma.asarray(f.variables["Lon"][:],dtype=float).filled(np.nan)
    if lat.shape!=lon.shape or lat.ndim!=2:
        raise ValueError("Source native lon/lat shape mismatch")
    if lat.shape!=(1264,1328):
        raise ValueError(f"Source native DEEP-AA 6250 grid changed: {lat.shape}")
    is_ant=np.isfinite(lat)&np.isfinite(lon)&(lat>=-90)&(lat<=-50)
    if int(np.count_nonzero(is_ant))<800_000:
        raise ValueError("Source native Antarctic map geolocation insufficient")
    return lat,lon,is_ant

def original_native_pixel_sites(original,lat,lon,mask):
    normal_lon=np.where(np.isfinite(lon),((lon+180)%360)-180,np.nan)
    latflat=lat.ravel()
    lonflat=normal_lon.ravel()
    maskflat=mask.ravel()
    trueidx=np.flatnonzero(maskflat)
    xf,yf=Transformer.from_crs(4326,SOURCE_EPSG,always_xy=True).transform(
        lonflat[trueidx],latflat[trueidx])
    xy=np.column_stack([xf,yf])
    if not np.isfinite(xy).all():
        raise ValueError("Native polar stereographic projection not finite")
    tree=cKDTree(xy)
    p=Proj(CRS.from_epsg(SOURCE_EPSG))
    tf=Transformer.from_crs(4326,SOURCE_EPSG,always_xy=True)
    geo=Geod(ellps="WGS84")
    membership={}
    polygons=[]
    for r in original.itertuples(index=False):
        clon=((float(r.colony_lon)+180)%360)-180
        clat=float(r.colony_lat)
        ox,oy=tf.transform(clon,clat)
        shortlist=tree.query_ball_point([ox,oy],r=155000)
        cand=trueidx[np.asarray(shortlist,dtype=np.int64)]
        if len(cand)==0:raise ValueError(f"No DEEPAA native grid near site {r.site_id}")
        _,_,dist=geo.inv(np.full(len(cand),clon),np.full(len(cand),clat),
                          lonflat[cand],latflat[cand])
        dist=np.asarray(dist,dtype=float)
        keep=dist<=100000
        cand100=cand[keep]
        cand25=cand[dist<=25000]
        if len(cand100)<80 or len(cand25)<4:
            raise ValueError(f"Actual grid cell support insufficient near original site {r.site_id}: {len(cand100)}, {len(cand25)}")
        for radius,c in [(100,cand100),(25,cand25)]:
            factor=np.asarray(p.get_factors(lonflat[c],latflat[c]).areal_scale,dtype=float)
            if not np.isfinite(factor).all() or (factor<=0).any():
                raise ValueError("Actual EPSG:3412 area-scale factor invalid")
            weight=1/factor
            membership[(str(r.site_id),radius)]=(c,weight)
            polygons.append({"site_id":str(r.site_id),"source_region":str(r.source_region),
              "radius_km":radius,"source_native_geolocated_pixels":len(c),
              "full_nominal_pixel_area_km2":float(np.sum(weight)*6.25**2),
              "colony_lat":clat,"colony_lon":clon})
    return membership,pd.DataFrame(polygons)

def valid_daily_days(mapping,source_seasons):
    cnt=Counter(k[:7] for k in mapping)
    valid_winter={}
    for yr in sorted(set(source_seasons)):
        months=[]
        for mm in MONTHS:
            all_days=calendar.monthrange(yr,mm)[1]
            real=cnt[f"{yr:04d}-{mm:02d}"]
            months.append({"month":f"{yr:04d}-{mm:02d}",
                           "real_daily_files":int(real),"calendar_days":int(all_days),
                           "passes_month_80pct":bool(real/all_days>=.8)})
        valid_winter[int(yr)]=all(v["passes_month_80pct"] for v in months)
    return valid_winter

def daily_source_only(z,mapping,original,cohort,member):
    years=sorted(set(cohort.season.astype(int)))
    full=valid_daily_days(mapping,years)
    accepted={yr for yr,ok in full.items() if ok}
    if not accepted:
        raise ValueError("Native date coverage has no complete winter source")
    by_year={yr:sorted(x for x in mapping if int(x[:4])==yr and int(x[5:7]) in MONTHS) for yr in accepted}
    daily=[]
    sea_valid_counts=[]
    observed_positive=defaultdict(set)
    for yr,all_days in by_year.items():
        participating=set(cohort.loc[cohort.season.eq(yr),"site_id"])
        if not participating:continue
        for day in all_days:
            with Dataset("day.nc","r",memory=z.read(mapping[day])) as f:
                arr=np.ma.asarray(f.variables["Map"][:],dtype=float).filled(np.nan)
            if arr.shape!=(1264,1328):
                raise ValueError("Native day grid shape/axis differs from geo grid")
            a=arr.ravel()
            for site in sorted(participating):
                for radius in (100,25):
                    idx,weight=member[(site,radius)]
                    pixels=a[idx]
                    # Non-marine NaN/-999 missing are never denominator.
                    valid=np.isfinite(pixels) & (pixels!=-999)
                    vals=pixels[valid]
                    if ((vals<0)&(~np.isin(vals,[-1,-2,-100]))).any():
                        raise ValueError("Unexpected negative DEEP-AA categorical values")
                    coastal=(vals>0)&((vals.astype(np.int64)%2)==0)
                    denom=float(np.sum(weight[valid]))
                    if denom<=0:
                        ratio=np.nan
                    else:
                        ratio=float(np.sum(weight[valid][coastal])/denom)
                        if not 0<=ratio<=1:
                            raise ValueError("Coastal polynya fraction outside 0..1")
                    if coastal.any():
                        observed_positive[(site,yr,radius)].update(idx[valid][coastal].tolist())
                    daily.append({"site_id":site,"season":int(yr),
                      "source_day":day,"source_month":day[:7],"radius_km":radius,
                      "original_valid_native_marine_pixels":int(valid.sum()),
                      "source_geolocation_pixels":int(len(idx)),
                      "original_coastal_polynya_pixels":int(coastal.sum()),
                      "daily_coastal_polynya_marine_area_fraction":ratio})
        print(json.dumps({"actual_source_processed_winter":yr,"daily_maps":len(all_days),
            "site_memberships":len(participating),"cumulative_site_day_radius_rows":len(daily)}),flush=True)
    d=pd.DataFrame(daily)
    if d.duplicated(["site_id","season","source_day","radius_km"]).any():
        raise ValueError("Daily site coordinates or source day duplicated")
    # Require at least 80% of *actual calendar days* per month with real marine observations
    months=[]
    for (site,yr,radius,mo),part in d.groupby(["site_id","season","radius_km","source_month"],sort=False):
        count=int(part.daily_coastal_polynya_marine_area_fraction.notna().sum())
        required=calendar.monthrange(yr,int(mo[5:7]))[1]
        months.append({"site_id":site,"season":yr,"radius_km":radius,"source_month":mo,
            "observed_days_with_actual_marine_denominator":count,
            "calendar_days":required,
            "all_month_days_pass_80pct":bool(count/required>=.8),
            "month_coastal_polynya_area_fraction":float(part.daily_coastal_polynya_marine_area_fraction.mean()) if count else np.nan,
            "month_n_distinct_native_positive_pixels":len(set().union(*[
                 observed_positive.get((site,yr,radius),set())]))})
    m=pd.DataFrame(months)
    winters=[]
    for (site,yr,radius),sub in m.groupby(["site_id","season","radius_km"],sort=False):
        covered=set(sub.source_month)
        expected={f"{yr:04d}-{v:02d}" for v in MONTHS}
        complete=covered==expected and sub.all_month_days_pass_80pct.all()
        winters.append({"site_id":site,"season":int(yr),"radius_km":int(radius),
            "source_is_actual_observed_complete_five_month_winter":bool(complete),
            "source_winter_JunOct_months_with_real_marine_denominator":int(sub.all_month_days_pass_80pct.sum()),
            "direct_DEEPAA_coastal_polynya_fraction":float(sub.month_coastal_polynya_area_fraction.mean()) if complete else np.nan,
            "source_native_distinct_coastal_polynya_pixels_over_winter":len(observed_positive.get((site,yr,radius),set()))})
    w=pd.DataFrame(winters)
    return d,m,w,full

def main(a):
    if digest(a.deepaa_zip,"md5")!=POLY_MD5 or digest(a.deepaa_zip,"sha256")!=POLY_SHA256:
        raise ValueError("DEEP-AA exact original source archive changed")
    cohort,original=original_sites(a)
    with zipfile.ZipFile(a.deepaa_zip) as z:
        if z.testzip(): raise ValueError("DEEP-AA source ZIP CRC failed")
        name,mapping=native_map_manifest(z)
        lat,lon,mask=lonlat_grid(z,name)
        member,polygon=original_native_pixel_sites(original,lat,lon,mask)
        daily,monthly,winter,season_days=daily_source_only(z,mapping,original,cohort,member)
    fullseason=cohort[["site_id","season","source_region"]].merge(
        winter.loc[winter.radius_km.eq(100)].drop(columns="radius_km"),
        how="left",on=["site_id","season"],validate="one_to_one")
    if len(fullseason)!=860:
        raise ValueError("Original 860 observation row count drift")
    n=fullseason.direct_DEEPAA_coastal_polynya_fraction.notna()
    observed=fullseason.loc[n].copy()
    per_region=observed.groupby("source_region",sort=True).agg(
        n_observations=("site_id","size"),n_original_sites=("site_id","nunique"),
        n_complete_winters=("season","nunique"),
        n_nonzero_season_exposure=("direct_DEEPAA_coastal_polynya_fraction",lambda s:int((s>0).sum())),
        n_unique_site_season_pixels=("source_native_distinct_coastal_polynya_pixels_over_winter","sum")).reset_index()
    names=("Victoria Land","Wilkes Land","Southwest Antarctic Peninsula")
    trio={x:int(observed.loc[observed.source_region.eq(x)].site_id.nunique()) for x in names}
    checks={
        "at_least_30_original_sites":bool(observed.site_id.nunique()>=30),
        "at_least_6_original_regions":bool(observed.source_region.nunique()>=6),
        "at_least_4_complete_winters":bool(observed.season.nunique()>=4),
        "at_least_3_independent_sites_in_each_prespecified_region":bool(all(v>=3 for v in trio.values()))
    }
    status=("PASS_DIRECT_POLYNYA_MACRO_SUPPORT_SOURCE_ONLY_NO_Y_FIT"
            if all(checks.values()) else "NO_GO_DIRECT_POLYNYA_MACRO_SUPPORT")
    receipt={"status":status,
      "provider_source":"Lin et al. DEEP-AA v1.1.0-2023 published 6.25km daily 20-day polynya source",
      "source_zenodo":"https://zenodo.org/records/13358042",
      "provider_md5":POLY_MD5,"provider_sha256":POLY_SHA256,
      "original_isotope_sha256":OPTICAL_SHA256,
      "independent_original_isotope_site_seasons":860,"original_n_site":88,
      "actual_source_daily_maps_all_years":len(mapping),
      "native_lonlat_coordinate_grid_shape":[1264,1328],
      "source_original_mapppd_and_original_landsat_3031_geography_validated_max_2km":True,
      "source_geodesic_radius_100km_primary_25km_descriptive":True,
      "source_EPSG":SOURCE_EPSG,
      "source_pixel_area_weighting":"native_6.25km_projected_cell_area_km2 divided by source polar-stereographic areal_scale",
      "source_winter_definition":"June-October in the original breeding-season start year",
      "source_native_calendar_winter_complete_years":[int(k) for k,v in season_days.items() if v],
      "real_complete_100km_observations":int(n.sum()),
      "real_complete_100km_original_sites":int(observed.site_id.nunique()),
      "real_complete_100km_source_regions":int(observed.source_region.nunique()),
      "real_complete_100km_distinct_winters":sorted(observed.season.astype(int).unique().tolist()),
      "three_prespecified_regions_original_sites":trio,
      "n_nonzero_exposure_site_seasons":int((observed.direct_DEEPAA_coastal_polynya_fraction>0).sum()),
      "source_original_regions":per_region.to_dict("records"),
      "frozen_gate_checks":checks,
      "no_outcome_opened_or_fitted":True,
      "not_direct_diet_measurement":True,
      "no_filled_missing_2011_2012":True,
      "coastal_polynya_only_not_open_sea_or_open_ocean_polynya":True,
      "no_future_climate_penguin_projection":True}
    a.out.mkdir(parents=True,exist_ok=True)
    fullseason.to_csv(a.out/"source_original_860_site_seasons_true_DEEPAA100km_no_optical_Y.csv",index=False)
    polygon.to_csv(a.out/"source_original_88_site_polynya_25km_100km_native_grid_geography.csv",index=False)
    daily.to_csv(a.out/"source_original_actual_daily_site_polynya_exposure_100km_25km.csv",index=False)
    monthly.to_csv(a.out/"source_original_actual_monthly_polynya_100km_25km.csv",index=False)
    winter.to_csv(a.out/"source_original_actual_winter_polynya_100km_25km.csv",index=False)
    per_region.to_csv(a.out/"source_region_real_polynya_geographic_support.csv",index=False)
    (a.out/"DEEPAA_ACTUAL_860_SOURCE_GEO_TIME_GATE.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(receipt,indent=2,ensure_ascii=False),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--deepaa-zip",type=Path,required=True)
    p.add_argument("--isotope-zip",type=Path,required=True)
    p.add_argument("--centroid-zip",type=Path,required=True)
    p.add_argument("--atlas-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args())
