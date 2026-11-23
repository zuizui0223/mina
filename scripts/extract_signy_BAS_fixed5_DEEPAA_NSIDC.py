#!/usr/bin/env python3
"""BAS 1978–2020 source-original Signy fixed-colony census × DEEP-AA+NSIDC source-only overlap.
Not a demographic regression. Preserve measured zeros and source missing years.
"""
import argparse,calendar,csv,datetime,hashlib,io,json,math,re,zipfile
from collections import defaultdict
from pathlib import Path
import numpy as np,pandas as pd
from netCDF4 import Dataset
from pyproj import Geod,Transformer
from extract_adelie_2003_2022_DEEPAA_coastal_and_open import xyz,read_nc,spherical_pixel_area,R,DATA_MD5
from extract_adelie_2003_2022_NSIDC_v4_sic import download_year

BAS_SHA="9d21c2c5cee3901ec465b1e3661f68299ad25bc9fa2eae4ead149e4eac23a80f"
BAS_CSV_SHA="585f87928ed64d8982ef5bd86d8a785c38df65c39223d88ec17425854c786d62"
PARTS=("A1 + A60","A2","A3","A4","A64")
YEARS=list(range(2004,2010))+list(range(2013,2020))
def require(x,m):
    if not bool(x):raise ValueError("SOURCE GATE STOP: "+m)
def get_breeding_data(raw):
    b=Path(raw).read_bytes()
    require(hashlib.sha256(b).hexdigest()==BAS_SHA,"BAS original DOI archive changed")
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        require(z.testzip() is None,"BAS ZIP CRC bad")
        count=z.read(next(n for n in z.namelist() if n.endswith("/signy_adelie_breeding_success.csv")))
        gps=z.read(next(n for n in z.namelist() if n.endswith("/GPS Adelie Colony.csv")))
    require(hashlib.sha256(count).hexdigest()==BAS_CSV_SHA,"Signy original observations changed")
    original=list(csv.DictReader(io.StringIO(count.decode("utf-8-sig"))))
    positions=list(csv.DictReader(io.StringIO(gps.decode("utf-8-sig"))))
    require(len(original)==310,"original Signy 310 rows changed")
    cols=list(positions[0])
    latkey=next(x for x in cols if "LATITUDE GPS" in x)
    lonkey=next(x for x in cols if "LONGITUDE GPS" in x)
    point={x["COLONY"]:(float(x[latkey]),float(x[lonkey])) for x in positions}
    require(set(PARTS).issubset(point),"one Signy fixed-colony GPS missing")
    lat=float(np.mean([point[c][0] for c in PARTS]))
    lon=float(np.mean([point[c][1] for c in PARTS]))
    counts=defaultdict(dict)
    for row in original:
        y=int(row["SEASON"].split("-")[0])
        c=row["COLONY"]
        if y in YEARS and c in PARTS and row["TOTAL_NUMBER_OF_PAIRS"] not in ("NA","",None):
            require(c not in counts[y],"Duplicate original Signy fixed subgroup observation "+str((c,y)))
            counts[y][c]=float(row["TOTAL_NUMBER_OF_PAIRS"])
    require(list(sorted(y for y in counts if set(PARTS)<=set(counts[y])))==YEARS,
            "BAS fixed 5-subcolony 13-year observed series changed")
    return lat,lon,counts,point

def get_daily_source(zip_path,lat,lon):
    import zipfile
    geod=Geod(ellps="WGS84")
    with zipfile.ZipFile(zip_path) as z:
        require(z.testzip() is None,"DEEP-AA original CRC failed")
        ncs=[n for n in z.namelist() if n.lower().endswith(".nc")]
        loc=[n for n in ncs if n.split("/")[-1].lower()=="lonlat.nc"]
        require(len(loc)==1,"DEEP-AA lonlat native missing")
        lons,lats=read_nc(z.read(loc[0]),["Lon","Lat"])
        area=spherical_pixel_area(lons,lats).ravel()
        lo=lons.ravel();la=lats.ravel()
        good=np.flatnonzero(np.isfinite(lo)&np.isfinite(la)&(np.isfinite(area))&(area>0)&(np.abs(la)<=90))
        from scipy.spatial import cKDTree
        c=cKDTree(xyz(lo[good],la[good])).query_ball_point(xyz(np.array([lon]),np.array([lat]))[0],
                2*np.sin(100.5/(2*R)))
        ix=good[np.asarray(c,int)]
        _,_,dist=geod.inv(np.full(len(ix),lon),np.full(len(ix),lat),lo[ix],la[ix])
        ix=ix[np.asarray(dist)<=100000]
        require(len(ix)>=10,"Signy 100km source insufficient grid")
        files={}
        for n in ncs:
            if n==loc[0]:continue
            m=re.search(r"(?<!\d)(20\d{6})(?!\d)",n.split("/")[-1])
            if not m:continue
            t=m[1];date=datetime.date(int(t[:4]),int(t[4:6]),int(t[6:8]))
            if date.year in YEARS and date.month in range(6,11):files[date]=n
        require(files,"No valid Signy DEEPAA dates")
        first,=read_nc(z.read(files[min(files)]),["Map"])
        original_ocean=np.asarray(first).ravel()[ix]!=-999
        pix=ix[original_ocean];weights=area[pix]
        require(weights.sum()>0,"No Signy ocean pixels")
        days=[]
        for day,n in sorted(files.items()):
            arr,=read_nc(z.read(n),["Map"]);v=np.asarray(arr).ravel()[pix]
            valid=np.isfinite(v)&(v!=-999)
            fvalid=float(weights[valid].sum()/weights.sum())
            co=(v>0)&((v%2)==0)
            allop=(v>0)|(v==-1)|(v==-2)
            rows={"season":day.year,"month":day.month,"date":day.isoformat(),
                  "fraction_source_ocean_valid":fvalid,
                  "coastal_fraction":float(weights[co&valid].sum()/weights[valid].sum()) if fvalid>=0.8 else np.nan,
                  "allopen_fraction":float(weights[allop&valid].sum()/weights[valid].sum()) if fvalid>=0.8 else np.nan}
            days.append(rows)
        return pd.DataFrame(days),len(pix)

def retrieve_monthly_sic(lat,lon):
    from scipy.spatial import cKDTree
    geod=Geod(ellps="WGS84");records=[];initial=None
    for year in YEARS:
        raw,url=download_year(year)
        with Dataset("source.nc",memory=raw) as ds:
            x=np.asarray(ds["xgrid"][:],float);y=np.asarray(ds["ygrid"][:],float)
            values=np.ma.filled(ds["cdr_seaice_conc_monthly"][:],np.nan).astype(float)
            require(values.shape==(5,332,316),"Original NSIDC dimensions drift")
            if initial is None:
                yy,xx=np.meshgrid(y,x,indexing="ij")
                llon,llat=Transformer.from_crs(3412,4326,always_xy=True).transform(xx.ravel(),yy.ravel())
                good=np.flatnonzero(np.isfinite(llon)&np.isfinite(llat))
                idxs=cKDTree(xyz(llon[good],llat[good])).query_ball_point(
                    xyz(np.array([lon]),np.array([lat]))[0],2*np.sin(100.5/(2*R)))
                ids=good[np.asarray(idxs,int)]
                _,_,dd=geod.inv(np.full(len(ids),lon),np.full(len(ids),lat),llon[ids],llat[ids])
                initial=ids[np.asarray(dd)<=100000]
                require(len(initial)>8,"Signy 25km too few native SIC cells")
            for month in range(6,11):
                flat=values[month-6].ravel()[initial]
                good=flat[np.isfinite(flat)&(flat>=0)&(flat<=1)]
                records.append({"season":year,"month":month,
                     "sic_fraction":float(good.mean()) if len(good)>4 else np.nan,
                     "n_valid_sic_grid_cells":len(good)})
    return pd.DataFrame(records)

def main(a):
    out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    lat,lon,counts,positions=get_breeding_data(a.signy_zip)
    hh=hashlib.md5()
    with Path(a.deepaa).open("rb") as f:
        for c in iter(lambda:f.read(2**21),b""):hh.update(c)
    require(hh.hexdigest()==DATA_MD5,"Original DEEPAA MD5")
    day,nix=get_daily_source(a.deepaa,lat,lon)
    mon=day.groupby(["season","month"],as_index=False).agg(
       coastal=("coastal_fraction","mean"),allopen=("allopen_fraction","mean"),
       days=("coastal_fraction","count"),native_days=("date","nunique"))
    mon["required_days"]=mon.apply(lambda r:math.ceil(.8*calendar.monthrange(int(r.season),int(r.month))[1]),axis=1)
    mon["valid"]=mon.days>=mon.required_days
    require(mon.valid.all() and len(mon)==len(YEARS)*5,"One Signy winter source month failed coverage 80%")
    winter=mon.groupby("season",as_index=False).agg(coastal=("coastal","mean"),
             allopen=("allopen","mean"),n_complete_months=("valid","sum"))
    require((winter.n_complete_months==5).all(),"Signy missing months")
    nsidc=retrieve_monthly_sic(lat,lon)
    require(len(nsidc)==len(YEARS)*5 and nsidc.sic_fraction.notna().all(),
        "Signy original NSIDC SIC missing")
    s=nsidc.groupby("season",as_index=False).agg(sic=("sic_fraction","mean"),n_sic_months=("month","size"))
    winter=winter.merge(s,on="season",validate="one_to_one")
    winter["northpoint_fixed5_pairs"]=[sum(counts[y][c] for c in PARTS) for y in winter.season]
    winter["site"]="Signy Island North Point"
    winter["site_lat"]=lat;winter["site_lon"]=lon
    winter["coastal_pp"]=100*winter.coastal
    winter["allopen_pp"]=100*winter.allopen
    winter["sic_pp"]=100*winter.sic
    winter.to_csv(out/"BAS_Signy_original_13winters_DEEPAA_NSIDC_physical_unfit.csv",index=False)
    mon.to_csv(out/"BAS_Signy_DEEPAA_13winters_monthly_support.csv",index=False)
    nsidc.to_csv(out/"BAS_Signy_NSIDC_v4_13winters_monthly.csv",index=False)
    summary={
        "status":"SIGNY_INDEPENDENT_COLONY_BLOCK_SOURCE_PHYSICAL_GATE",
        "location_original_gps_mean":[lat,lon],"fixed_monitored_subcolonies":PARTS,
        "original_breeding_pair_observations":len(winter),
        "matched_winter_years":YEARS,
        "source_DEEPAA_native_pixel_count":nix,
        "coastal_pp_by_year":{str(int(x.season)):float(x.coastal_pp) for x in winter.itertuples()},
        "coastal_nonzero_winters":int((winter.coastal>0).sum()),
        "coastal_sd_pp":float(winter.coastal_pp.std(ddof=1)),
        "nsidc_ice_sd_pp":float(winter.sic_pp.std(ddof=1)),
        "corr_coastal_vs_sic":float(winter[["coastal","sic"]].corr().iloc[0,1]) if winter.coastal.std()>0 else None,
        "nests_not_fitted":True,"independent_geographic_block_count_increase":1,
        "cautions":["North Point fixed five monitored subcolonies, not total Signy island population",
           "2010 and 2020 pairs missing in original BAS, not measured zeros",
           "Signy subcolony observations are one 100km environmental source, not five independent replicates",
           "External BAS source uses breeding pairs, not fully comparable to MAPPPD nests without survey scope mapping"]}
    (out/"BAS_Signy_independent_physical_overlap_receipt.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    for x in ("signy_zip","deepaa","out"):
        p.add_argument("--"+x.replace("_","-"),dest=x,required=True)
    main(p.parse_args())
