#!/usr/bin/env python3
"""Sign-independent Syowa 7-seasons source-derived environment from original Southwell 2015 S1.
Duffy 25-km 44-year data NOT reused; original DEEP-AA 6.25 km and NSIDC v4 measured SIC.
No demographic model; 7 consecutive observed seasons span only 6 years, below >=8 year gate.
"""
from __future__ import annotations
import argparse,datetime,calendar,hashlib,json,re,zipfile
from collections import defaultdict
from pathlib import Path
import numpy as np,pandas as pd
from pyproj import Transformer,Geod
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from netCDF4 import Dataset
from extract_adelie_2003_2022_DEEPAA_coastal_and_open import read_nc,xyz,spherical_pixel_area,R,DATA_MD5
from extract_adelie_2003_2022_NSIDC_v4_sic import download_year

YRS=list(range(2004,2011))
def require(c,msg):
    if not c:raise ValueError("SYO-PHYSICAL-SOURCE-STOP: "+msg)
def get_metadata(args):
    pos=pd.read_csv(args.coords)
    counts=pd.read_csv(args.counts)
    require(len(pos)==8 and len(counts)==7,"Original Southwell fixed source 8 sites and 7 annual counts changed")
    require(list(counts.season.astype(int))==YRS,"Original Syowa 7 years changed")
    geo=pos.drop_duplicates(["latitude","longitude"]).reset_index(drop=True).copy()
    require(len(geo)==7,"Rounded original source coordinates are not 7 unique coordinates")
    geo["id"]=range(7)
    geod=Geod(ellps="WGS84")
    m=0.
    for i,row in geo.iterrows():
      for j,other in geo.iterrows():
        _,_,d=geod.inv(row.longitude,row.latitude,other.longitude,other.latitude)
        m=max(m,float(d))
    require(m<100000,"Original Syowa sites no longer lie within 100km")
    return geo,counts,{"original_sites":8,"unique_rounded_original_coordinates":7,
                       "maximum_separation_km":m/1000}
def deepaa(args,geo):
    h=hashlib.md5()
    with open(args.deepaa,"rb") as f:
        for chunk in iter(lambda:f.read(2**21),b""):h.update(chunk)
    require(h.hexdigest()==DATA_MD5,"Official DEEP-AA archive MD5 changed")
    with zipfile.ZipFile(args.deepaa) as z:
        require(z.testzip() is None,"Original DEEPAA CRC failure")
        ncs=[n for n in z.namelist() if n.lower().endswith(".nc")]
        lonlat=[n for n in ncs if n.lower().split("/")[-1]=="lonlat.nc"]
        require(len(lonlat)==1,"Native LonLat file not unique")
        lon,lat=read_nc(z.read(lonlat[0]),["Lon","Lat"])
        lon=np.asarray(lon,float);lat=np.asarray(lat,float)
        area=spherical_pixel_area(lon,lat)
        ok=np.flatnonzero(np.isfinite(lon.ravel()) & np.isfinite(lat.ravel())&
                          np.isfinite(area.ravel()) &(area.ravel()>0)&(abs(lat.ravel())<=90))
        tree=cKDTree(xyz(lon.ravel()[ok],lat.ravel()[ok]))
        ball=tree.query_ball_point(xyz(geo.longitude.to_numpy(),geo.latitude.to_numpy()),
                  2*np.sin(100.5/(2*R)))
        geod=Geod(ellps="WGS84")
        indices=[]
        for i,g in geo.iterrows():
            a=ok[np.asarray(ball[i],int)]
            _,_,distance=geod.inv(np.full(len(a),g.longitude),
                np.full(len(a),g.latitude),lon.ravel()[a],lat.ravel()[a])
            a=a[np.asarray(distance)<=100000]
            require(len(a)>50,"Too few Syowa DEEPAA source grid points")
            indices.append(a)
        dated={}
        for n in ncs:
            m=re.search(r"(?<!\d)(20\d{6})(?!\d)",n.split("/")[-1])
            if not m:continue
            s=m[1];d=datetime.date(int(s[:4]),int(s[4:6]),int(s[6:8]))
            if d.year in YRS and 6<=d.month<=10:
                require(d not in dated,"Duplicate native 20-day source file date")
                dated[d]=n
        require(len(dated)>=1000,"Missing original 2004-2010 DEEPAA days")
        first,=read_nc(z.read(dated[min(dated)]),["Map"])
        ocean=(np.asarray(first).ravel()!=-999)
        weights=[]
        for ix in indices:
            a=ix[ocean[ix]]
            w=area.ravel()[a].copy()
            require(w.sum()>0,"Zero Syowa source ocean area")
            weights.append((a,w))
        day_records=[]
        for d,n in sorted(dated.items()):
            a,=read_nc(z.read(n),["Map"])
            flat=np.asarray(a).ravel()
            for i,(ix,w) in enumerate(weights):
                v=flat[ix]
                valid=np.isfinite(v)&(v!=-999)
                share=float(w[valid].sum()/w.sum())
                coastal=(v>0)&(v%2==0)
                open_= (v>0)|(v==-1)|(v==-2)
                if share>=.80:
                    denom=w[valid].sum()
                    coastal_fraction=float(w[valid&coastal].sum()/denom)
                    open_fraction=float(w[valid&open_].sum()/denom)
                else:coastal_fraction=open_fraction=np.nan
                day_records.append({"site_source_round_id":int(i),"season":d.year,
                    "month":d.month,"date":d.isoformat(),"coastal_fraction":coastal_fraction,
                    "total_open_fraction":open_fraction,"valid_ocean_area_fraction":share})
    df=pd.DataFrame(day_records)
    return df,len(dated)
def nsidc(geo):
    geod=Geod(ellps="WGS84")
    rows=[]
    idx=None;point_grid_checksum=None
    for y in YRS:
        b,url=download_year(y)
        with Dataset("memory.nc",memory=b) as n:
            x=np.asarray(n.variables["xgrid"][:],float)
            yy=np.asarray(n.variables["ygrid"][:],float)
            v=np.asarray(np.ma.filled(n.variables["cdr_seaice_conc_monthly"][:],np.nan),float)
            require(v.shape==(5,332,316),"NSIDC monthly Southern grid changed")
            if idx is None:
                Y,X=np.meshgrid(yy,x,indexing="ij")
                longitude,latitude=Transformer.from_crs(3412,4326,always_xy=True).transform(X.ravel(),Y.ravel())
                valid=np.flatnonzero(np.isfinite(longitude)&np.isfinite(latitude))
                tr=cKDTree(xyz(longitude[valid],latitude[valid]))
                balls=tr.query_ball_point(xyz(geo.longitude.to_numpy(),geo.latitude.to_numpy()),2*np.sin(100.5/(2*R)))
                idx=[]
                for i,g in geo.iterrows():
                    a=valid[np.asarray(balls[i],int)]
                    _,_,dist=geod.inv(np.full(len(a),g.longitude),np.full(len(a),g.latitude),
                        longitude[a],latitude[a])
                    a=a[np.asarray(dist)<=100000]
                    require(len(a)>=5,"NSIDC Syowa source grid <5 native pixels")
                    idx.append(a)
                point_grid_checksum=hashlib.sha256(x.tobytes()+yy.tobytes()).hexdigest()
            for month in range(6,11):
                flat=v[month-6].ravel()
                for i,a in enumerate(idx):
                    val=flat[a]
                    valid=val[np.isfinite(val)&(val>=0)&(val<=1)]
                    rows.append({"site_source_round_id":i,"season":y,"month":month,
                       "sic_fraction":float(valid.mean()) if len(valid)>=5 else np.nan,
                       "n_25km_valid_cells":int(len(valid))})
        print("SYO NSIDC source",y,"downloaded",len(b),"bytes",flush=True)
    return pd.DataFrame(rows),point_grid_checksum
def main(args):
    out=Path(args.out);out.mkdir(parents=True,exist_ok=True)
    geo,counts,metadata=get_metadata(args)
    days,n_days=deepaa(args,geo)
    monthly=days.groupby(["site_source_round_id","season","month"],as_index=False).agg(
       coastal_fraction=("coastal_fraction","mean"),
       total_open_fraction=("total_open_fraction","mean"),
       n_valid_days=("coastal_fraction","count"),n_native_days=("date","nunique"))
    monthly["min_days"]=monthly.apply(lambda r:calendar.monthrange(int(r.season),int(r.month))[1]*.8,axis=1)
    monthly["complete"]=monthly.n_valid_days>=monthly.min_days
    summary=monthly.loc[monthly.complete].groupby(["site_source_round_id","season"],as_index=False).agg(
       coastal=("coastal_fraction","mean"),total_open=("total_open_fraction","mean"),n_months=("month","nunique"))
    require(len(summary)==49 and summary.n_months.eq(5).all(),"Missing any original seven Syowa site winters")
    ocean=summary.groupby("season",as_index=False).agg(
       coastal=("coastal","mean"),total_open=("total_open","mean"))
    ic,grid_sha=nsidc(geo)
    require(len(ic)==7*7*5 and ic.sic_fraction.notna().all(),"Original Syowa NSIDC missing")
    annual=ic.groupby(["season","site_source_round_id"],as_index=False).sic_fraction.mean()
    sic=annual.groupby("season",as_index=False).sic_fraction.mean()
    ocean=ocean.merge(sic,on="season",validate="one_to_one")
    result=counts.merge(ocean,on="season",validate="one_to_one")
    for k in ("coastal","total_open","sic_fraction"):
        result[k+"_pp"]=100*result[k]
    result["geo_unique_centres_n"]=7
    result.to_csv(out/"Syowa_original_2004_2010_7winters_DEEPAA_NSIDC_unfit.csv",index=False)
    geo.to_csv(out/"Syowa_7_source_coords_geocoded.csv",index=False)
    monthly.to_csv(out/"Syowa_7coords_2004_2010_DEEPAA_months.csv",index=False)
    ic.to_csv(out/"Syowa_7coords_2004_2010_NSIDC_months.csv",index=False)
    audit={"status":"VERIFIED_SYOWA_SOURCE_REGIONAL_AND_PHYSICAL_NOT_ELIGIBLE_8YR_SPAN",
         "publication_source":"Southwell et al. 2015 PLOS ONE S1 Table 4",
         "original_breeding_regions":1,"years":YRS,"n_pairs_observations":7,
         "n_site_source_coordinates_unique":7,
         "region_census_source_sites_nominal":8,
         "original_8site_coords_max_distance_km":metadata["maximum_separation_km"],
         "original_DEEPAA_source_days":n_days,
         "annual_coastal_fraction_pct":[round(v,6) for v in result.coastal_pp],
         "annual_NSIDC_sic_pct":[round(v,6) for v in result.sic_fraction_pp],
         "n_with_nonzero_coastal":int(result.coastal.gt(0).sum()),
         "observed_coastal_SD_pp":float(result.coastal_pp.std(ddof=1)),
         "NSIDC_grid_sha":grid_sha,
         "physical_year_match_7years":True,
         "n_independent_geographical_new_regions":1,
         "meets_fixed_census_four_year_requirement":True,
         "meets_fixed_eight_year_timespan_requirement":False,
         "n_qualified_pan_antarctic_clusters_still":7,
         "population_response_fitted":False,
         "source_definition_caution":"Regional corrected total of 8 stable colonies; 7 spatial coordinate values after rounded duplication; use 7 unique physical footprints to avoid arbitrary double weighting"}
    (out/"SYO_SOURCE_ONLY_CENSUS_AND_PHYSICS_RECEIPT.json").write_text(json.dumps(audit,indent=2)+"\n")
    print(json.dumps(audit,indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for x in ("counts","coords","deepaa","out"):
        p.add_argument("--"+x,required=True)
    main(p.parse_args())
