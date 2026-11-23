#!/usr/bin/env python3
"""Auditable DEEP-AA 6.25km 2003–2022 fixed 100km physical exposure screen.
No penguin outcome regression. Full daily months require 80% calendar-day coverage.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import date
from io import BytesIO
from pathlib import Path
import argparse,calendar,hashlib,json,math,re,zipfile
import numpy as np,pandas as pd
from pyproj import Geod
from scipy.io import netcdf_file
from scipy.spatial import cKDTree
from scipy.sparse import csr_matrix,coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.sparse import eye

DATA_MD5="f3f958389cc5e67ac1c4e3a6ee164318"
MAPPPD_SHA="d169c409cf278b137d6df35fbeb9ab3409bdea15f41c39bcaec549a4d4dbca89"
R=6371.0088
YEARS=[y for y in range(2003,2023) if y not in (2011,2012)]
MONTHS=range(6,11)
def audit_hash(path, expected, alg):
    h=hashlib.new(alg)
    with open(path,"rb") as f:
        for chunk in iter(lambda:f.read(2**21),b""):h.update(chunk)
    if h.hexdigest()!=expected:raise ValueError("STOP original checksum drift in "+str(path))
def xyz(lon,lat):
    a,b=np.deg2rad(lon),np.deg2rad(lat)
    return np.stack([np.cos(b)*np.cos(a),np.cos(b)*np.sin(a),np.sin(b)],axis=-1)
def spherical_pixel_area(lon,lat):
    v=xyz(lon,lat)*R
    return np.linalg.norm(np.cross(np.gradient(v,axis=0),np.gradient(v,axis=1)),axis=-1)
def read_nc(blob,keys):
    if blob[:3]==b"CDF":
        with netcdf_file(BytesIO(blob),mmap=False) as z:
            return [np.array(z.variables[k][:],copy=True) for k in keys]
    from netCDF4 import Dataset
    with Dataset("source.nc",memory=blob) as z:
        return [np.asarray(np.ma.filled(z.variables[k][:],-999)) for k in keys]
def group_sites(sites,radius):
    pos=xyz(sites.lon.to_numpy(float),sites.lat.to_numpy(float))
    # Connected components of pairwise centroid distances; overlaps of 100km
    # discs are possible within 200km, hence conservative 200km connectivity.
    pairs=cKDTree(pos).query_pairs(2*np.sin(radius/(2*R)),output_type="ndarray")
    if len(pairs):
        rw=np.r_[pairs[:,0],pairs[:,1]];cl=np.r_[pairs[:,1],pairs[:,0]]
        g=coo_matrix((np.ones(len(rw)),(rw,cl)),shape=(len(sites),len(sites))).tocsr()
    else:g=csr_matrix((len(sites),len(sites)))
    n,labels=connected_components(g,directed=False)
    return n,labels
def sites_from_original_census(path,out):
    audit_hash(path,MAPPPD_SHA,"sha256")
    df=pd.read_csv(path,low_memory=False)
    needed={"common_name","count_type","penguin_count","season_starting","site_id","longitude_epsg_4326","latitude_epsg_4326","cammlr_region","accuracy","vantage"}
    if not needed.issubset(df):raise ValueError("STOP MAPPPD source schema drift")
    base=df.loc[df.common_name.eq("adelie penguin")&df.count_type.eq("nests")&
       df.season_starting.isin(YEARS)&df.penguin_count.notna()].copy()
    if (len(base),base.site_id.nunique(),int(base.penguin_count.eq(0).sum()))!=(565,201,42):
        raise ValueError("STOP original MAPPPD census gate changed")
    base["season"]=base.season_starting.astype(int)
    years=base.groupby("site_id").agg(n=("season","nunique"),mn=("season","min"),mx=("season","max"),
        lon=("longitude_epsg_4326","median"),lat=("latitude_epsg_4326","median"),
        region=("cammlr_region","first"),name=("site_name","first")).reset_index()
    years["span"]=years.mx-years.mn
    primary=years[(years.n>=4)&(years.span>=8)].sort_values("site_id").copy()
    relaxed=years[(years.n>=3)&(years.span>=5)].sort_values("site_id").copy()
    if (len(primary),len(relaxed))!=(32,43):raise ValueError("STOP 32/43 census gate changed")
    relaxed["primary"]=relaxed.site_id.isin(set(primary.site_id))
    for rad in (100,200):
        n,lab=group_sites(primary,rad)
        if (rad,n) not in ((100,7),(200,6)):raise ValueError("STOP primary connectivity drift")
    for rad in (100,200):
        n,lab=group_sites(relaxed,rad)
        relaxed["block_%dkm"%rad]=lab
        if (rad,n) not in ((100,10),(200,5)):raise ValueError("STOP relaxed connectivity drift")
    raw=base[base.site_id.isin(relaxed.site_id)].copy()
    count=raw.groupby(["site_id","season"],as_index=False).agg(
        n_count_rows=("penguin_count","size"),nests_median=("penguin_count","median"),
        nests_min=("penguin_count","min"),nests_max=("penguin_count","max"),
        worst_accuracy=("accuracy","max"),n_vantages_this_year=("vantage","nunique"))
    count["nests_duplicate_conflict_over20pct"]=np.where(count.nests_min.gt(0),
         count.nests_max/(count.nests_min+1e-12)>1.2,
         count.nests_max.gt(0))
    count=count.merge(relaxed[["site_id","region","name","lat","lon","primary","block_100km","block_200km"]],
         on="site_id",validate="many_to_one")
    relaxed.to_csv(out/"site_support_43_source_only.csv",index=False)
    count.sort_values(["site_id","season"]).to_csv(out/"census_43_sites_2003_2022_source_only.csv",index=False)
    return relaxed.reset_index(drop=True),count
def extract(deep,source,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    audit_hash(deep,DATA_MD5,"md5")
    sites,count=sites_from_original_census(source,out)
    with zipfile.ZipFile(deep) as z:
        if z.testzip() is not None:raise ValueError("STOP DEEP-AA ZIP CRC failure")
        ncs=[x for x in z.namelist() if x.lower().endswith(".nc")]
        loc=[x for x in ncs if x.split("/")[-1].lower()=="lonlat.nc"]
        if len(loc)!=1:raise ValueError("STOP missing/non-unique DEEP-AA LonLat")
        lon,lat=read_nc(z.read(loc[0]),["Lon","Lat"])
        if lon.shape!=lat.shape or lon.ndim!=2:raise ValueError("STOP DEEP-AA lonlat grid shape")
        lat=np.asarray(lat,float);lon=np.asarray(lon,float)
        area=spherical_pixel_area(lon,lat)
        valid=np.flatnonzero(np.isfinite(lon.ravel())&np.isfinite(lat.ravel())&np.isfinite(area.ravel())&
                           (area.ravel()>0)&(np.abs(lat.ravel())<=90))
        tree=cKDTree(xyz(lon.ravel()[valid],lat.ravel()[valid]))
        near=tree.query_ball_point(xyz(sites.lon.to_numpy(),sites.lat.to_numpy()),
                                   2*np.sin(100.5/(2*R)))
        geod=Geod(ellps="WGS84"); indices=[]
        for i,site in sites.iterrows():
            ids=valid[np.asarray(near[i],dtype=int)]
            _,_,distance=geod.inv(np.full(len(ids),site.lon),np.full(len(ids),site.lat),
                                  lon.ravel()[ids],lat.ravel()[ids])
            ix=ids[np.asarray(distance)<=100000]
            if len(ix)<10:raise ValueError("STOP too few native grid cells for "+str(site.site_id))
            indices.append(ix)
        files={}
        dates_by_yearmonth=defaultdict(int)
        for nm in ncs:
            if nm==loc[0]:continue
            m=re.search(r"(?<!\d)(20\d{6})(?!\d)",nm.split("/")[-1])
            if not m:continue
            s=m[1]
            d=date(int(s[:4]),int(s[4:6]),int(s[6:8]))
            if 2003<=d.year<=2022 and d.month in MONTHS:
                if d in files:raise ValueError("STOP duplicate source satellite day "+str(d))
                files[d]=nm
                dates_by_yearmonth[(d.year,d.month)]+=1
        if not files:raise ValueError("STOP no polynya daily map files")
        earliest=next(iter(sorted(files)))
        first,=read_nc(z.read(files[earliest]),["Map"])
        if first.shape!=lat.shape:raise ValueError("STOP native mask grid drift")
        first=np.asarray(first).ravel()
        ocean=(np.isfinite(first))&(first!=-999)
        flat_area=area.ravel()
        nsites=len(sites)
        rw=[];cl=[];v=[]
        denom=[]
        for i,ix in enumerate(indices):
            ii=ix[ocean[ix]]
            denom_i=float(np.sum(flat_area[ii]))
            if denom_i<=0:raise ValueError("STOP zero local ocean area at "+str(sites.site_id.iat[i]))
            denom.append(denom_i)
            rw.extend([i]*len(ii))
            cl.extend(ii.tolist())
            v.extend((flat_area[ii]/denom_i).tolist())
        W=csr_matrix((v,(rw,cl)),shape=(nsites,first.size))
        # W @ binary category => area fraction of class in local ocean map.
        if np.max(np.abs(np.asarray(W.sum(axis=1)).ravel()-1))>1e-7:
            raise ValueError("STOP local area fractions do not sum to 1")
        rows=[];category_counts={}
        for n,(day,nm) in enumerate(sorted(files.items())):
            vals,=read_nc(z.read(nm),["Map"])
            if vals.shape!=lat.shape:raise ValueError("STOP native map grid shape changed")
            flat=np.asarray(vals).ravel()
            if n in (0,1,len(files)-1):
                codes,ct=np.unique(flat,return_counts=True)
                cats={"land":int(ct[codes==-999].sum()),
                      "fastice":int(ct[codes==-100].sum()),
                      "sea_open":int(ct[codes==-2].sum()),
                      "other_open":int(ct[codes==-1].sum()),
                      "pack_ice_zero":int(ct[codes==0].sum()),
                      "positive_polynya":int(ct[codes>0].sum())}
                category_counts[day.isoformat()]=cats
            coastal=(flat>0)&((flat%2)==0)
            openwater=(flat>0)|(flat==-1)|(flat==-2)
            fastice=flat==-100
            unclassified=~np.isfinite(flat)|(flat==-999)
            nvalid=1-np.asarray(W @ unclassified.astype(float)).reshape(-1)
            # Native Map land mask changes by a few percent through the archive.
            # Do NOT use the fixed first-day ocean denominator as if it were
            # observed on a partially masked day: renormalize to truly valid
            # source ocean cells, with a predeclared minimum 80% mapped support.
            co=np.asarray(W @ coastal.astype(float)).reshape(-1)
            op=np.asarray(W @ openwater.astype(float)).reshape(-1)
            fi=np.asarray(W @ fastice.astype(float)).reshape(-1)
            good=nvalid>=.80
            co=np.divide(co,nvalid,out=np.full(nsites,np.nan),where=good)
            op=np.divide(op,nvalid,out=np.full(nsites,np.nan),where=good)
            fi=np.divide(fi,nvalid,out=np.full(nsites,np.nan),where=good)
            for i in range(nsites):
                rows.append((sites.site_id.iat[i],day.year,day.month,day.isoformat(),
                             co[i],op[i],fi[i],nvalid[i]))
            if n%550==0:print("Processed DEEP-AA",n+1,"of",len(files),"source days",flush=True)
    daily=pd.DataFrame(rows,columns=["site_id","season","month","date","coastal_frac",
                                     "all_open_frac","fastice_frac","source_valid_ocean_fraction"])
    monthly=daily.groupby(["site_id","season","month"],as_index=False).agg(
        coastal_frac=("coastal_frac","mean"),all_open_frac=("all_open_frac","mean"),
        fastice_frac=("fastice_frac","mean"),n_valid_days=("coastal_frac","count"),
        n_native_days=("date","nunique"))
    monthly["min_valid_days"]=monthly.apply(lambda r:math.ceil(.8*calendar.monthrange(int(r.season),int(r.month))[1]),axis=1)
    monthly["meets_80pct_days"]=monthly.n_valid_days>=monthly.min_valid_days
    keep=monthly.loc[monthly.meets_80pct_days].groupby(["site_id","season"]).agg(
        n_valid_months=("month","nunique"),coastal_frac=("coastal_frac","mean"),
        all_open_frac=("all_open_frac","mean"),fastice_frac=("fastice_frac","mean")).reset_index()
    keep=keep.loc[keep.n_valid_months==5].copy()
    # Make every site×calendar winter explicit, including partial 2011/12 missing years.
    all_years=pd.MultiIndex.from_product([sites.site_id,range(2003,2023)],names=["site_id","season"]).to_frame(index=False)
    all_years=all_years.merge(keep,on=["site_id","season"],how="left",validate="one_to_one")
    all_years=all_years.merge(sites[["site_id","region","name","lat","lon","primary","block_100km","block_200km"]],
                             on="site_id",validate="many_to_one")
    all_years["has_complete_source_winter"]=all_years.n_valid_months.eq(5)
    all_years["coastal_frac_pp"]=100*all_years.coastal_frac
    all_years["all_open_frac_pp"]=100*all_years.all_open_frac
    all_years["coastal_share_of_openwater"]=np.where(all_years.all_open_frac.gt(0),
             all_years.coastal_frac/all_years.all_open_frac,np.nan)
    if (all_years.coastal_frac>all_years.all_open_frac+1e-7).any():
        raise ValueError("STOP coastal pixels exceed total open water")
    if all_years.loc[all_years.season.isin((2011,2012)),"has_complete_source_winter"].any():
        raise ValueError("STOP expected DEEP-AA 2011/2012 source hiatus not observed")
    all_years.to_csv(out/"DEEPAA_2003_2022_43sites_100km_physical_by_winter.csv",index=False)
    monthly.to_csv(out/"DEEPAA_2003_2022_43sites_100km_physical_by_month.csv",index=False)
    daily.to_csv(out/"DEEPAA_2003_2022_43sites_100km_physical_by_day.csv.gz",index=False,compression="gzip")
    counts=count.merge(all_years[["site_id","season","has_complete_source_winter",
                     "coastal_frac","all_open_frac","fastice_frac","coastal_frac_pp","all_open_frac_pp",
                     "coastal_share_of_openwater"]],
                     on=["site_id","season"],how="left",validate="many_to_one")
    counts.to_csv(out/"observed_MAPPPD_nest_site_years_with_DEEPAA_physical_only.csv",index=False)
    fy=all_years.loc[all_years.season.isin(YEARS)&all_years.has_complete_source_winter]
    primary=fy.loc[fy.primary]
    phys_summary={
        "run_status":"SOURCE_ONLY_SEPARATE_COASTAL_POLYNYA_AND_ALL_OPEN_WATER",
        "original_source":"DEEP-AA SIC60_6.25km_20d.zip MD5="+DATA_MD5,
        "original_census":"MAPPPD v5 original AllCounts CSV SHA="+MAPPPD_SHA,
        "period":"2003-2022; Jun-Oct, 2011 and 2012 incomplete",
        "n_daily_native_polynya_maps_in_winter_months":len(files),
        "dynamic_ocean_mask_valid_fraction_minimum":0.8,
        "ocean_area_denominator":"daily available original ocean cells within fixed 100-km geodesic buffer; relative area computed from original valid pixel area",
        "october_2003_days_available":dates_by_yearmonth.get((2003,10),0),
        "n_expected_complete_5month_source_winters":17,
        "n_matched_any_winter_43_sites":len(fy),
        "n_matched_any_winter_32_primary_sites":len(primary),
        "n_mapped_primary_sites":int(primary.site_id.nunique()),
        "coastal_pct_mean_primary":float(primary.coastal_frac_pp.mean()),
        "coastal_within_site_sd_pp_median_primary":float(primary.groupby("site_id").coastal_frac_pp.std().median()),
        "coastal_zero_sitewinters_primary":int(primary.coastal_frac.eq(0).sum()),
        "allopen_pct_mean_primary":float(primary.all_open_frac_pp.mean()),
        "source_monthly_day_coverage":{f"{yr}-{mon:02d}":int(n) for (yr,mon),n in sorted(dates_by_yearmonth.items())},
        "example_source_map_category_counts":category_counts,
        "valid_site_years_by_year":fy.groupby("season").site_id.nunique().astype(int).to_dict(),
        "n_census_source_43_obs":len(counts),
        "n_census_primary_source_obs":int(counts.primary.sum()),
        "matched_census_source_obs_with_complete_winter":int(counts.has_complete_source_winter.fillna(False).sum()),
        "independent_regions_primary_200km":6,
        "continuous_measured_sea_ice_concentration":"NOT_IN_THIS_EXTRACT; independent NSIDC mandatory before ecology fit",
        "limitations":["Winter 2003 is not complete (only 15/31 October days); winter 2011/12 has documented product hiatus", "The 60%-SIC class map gives binary open water, not continuous observed SIC",
                       "7 blocks at 100km but 6 blocks at 200km buffer-overlap support",
                       "No independent penguin prey, demographics or method-standardized census response analysed",
                       "No spatial radius/window/hypothesis retuned from results"]
    }
    (out/"DEEPAA_SOURCE_PHYSICAL_AND_SUPPORT_GATE.json").write_text(json.dumps(phys_summary,indent=2)+"\n")
    print(json.dumps({k:v for k,v in phys_summary.items() if k!="source_monthly_day_coverage"},indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--deepaa",required=True)
    p.add_argument("--mapppd",required=True)
    p.add_argument("--out",required=True)
    a=p.parse_args();extract(a.deepaa,a.mapppd,a.out)
