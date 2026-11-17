#!/usr/bin/env python3
"""Original publisher NSIDC G02202 V4 Nov-Feb SIC on Youngflesh image centroids.

Approximates terra polygon extraction by 25km cell-center inclusion in
150km EPSG:3412 buffers, explicitly NOT an exact recreation of unpublished
original R/terra colony_sic.csv. No missing-to-zero substitution.
"""
import argparse,json,hashlib,re,zipfile,tempfile
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd
import xarray as xr
from pyproj import Transformer

SOURCE_BYTES=256425816
SOURCE_MD5="e29a2f68c84e3a515044d554540def2f"
RADIUS_M=150000.0
PATTERN=re.compile(r"^L0/SIC/seaice_conc_monthly_sh_(\d{6})_[^/]+\.nc$")
def verify_source(path):
    h=hashlib.md5()
    size=0
    with open(path,"rb") as f:
        while True:
            b=f.read(1024*1024)
            if not b:break
            size+=len(b);h.update(b)
    if (size,h.hexdigest())!=(SOURCE_BYTES,SOURCE_MD5):
        raise ValueError("Publisher Zenodo source bytes or original MD5 changed")
    return {"bytes":size,"md5":h.hexdigest()}

def source_native_25km_axes(x,y):
    """Guard when NetCDF dimension indexes, not native meter coordinates, are decoded.

    NSIDC south grid: 316 columns x 332 rows, 25km, documented outer
    boundaries x=-3950..3950km, y=4350..-3950km. Reconstruct cell
    CENTERS only when raw dimensions are 0..N-1 synthetic indexes.
    """
    x=np.asarray(x,dtype=float)
    y=np.asarray(y,dtype=float)
    if x.size!=316 or y.size!=332:
        raise ValueError("NSIDC V4 native south grid dimensions changed")
    raw_x=[float(x[0]),float(x[-1])]
    raw_y=[float(y[0]),float(y[-1])]
    derived=False
    if np.array_equal(x,np.arange(316,dtype=float)) and np.array_equal(y,np.arange(332,dtype=float)):
        x=-3_937_500+25_000*np.arange(316,dtype=float)
        y=+4_337_500-25_000*np.arange(332,dtype=float)
        derived=True
    elif np.isclose(abs(np.diff(x)).mean(),25,atol=1e-5) and np.max(np.abs(x))<5000:
        # Original file may encode km rather than meters. Require both axes.
        if not np.isclose(abs(np.diff(y)).mean(),25,atol=1e-5):
            raise ValueError("Inconsistent native metric-grid units")
        x=x*1000
        y=y*1000
        derived=True
    if max(np.abs(x))<1_000_000 or max(np.abs(y))<1_000_000:
        raise ValueError(f"Native grid cannot be interpreted in meters x={raw_x} y={raw_y}")
    if not np.isclose(np.median(np.abs(np.diff(x))),25_000,atol=5):
        raise ValueError("NSIDC original x-spacing is not 25 km")
    if not np.isclose(np.median(np.abs(np.diff(y))),25_000,atol=5):
        raise ValueError("NSIDC original y-spacing is not 25 km")
    print("NSIDC_NATIVE_GRID_QA",{"raw_x_ends":raw_x,"raw_y_ends":raw_y,
          "metric_x_ends":[float(x[0]),float(x[-1])],
          "metric_y_ends":[float(y[0]),float(y[-1])],
          "reconstructed_from_official_south_grid":derived},flush=True)
    return x,y,derived

def cells_within(x,y,xc,yc,radius=RADIUS_M):
    # Row y, column x. This is center-within geometry, NOT terra touches polygon.
    return (np.asarray(y)[:,None]-yc)**2+(np.asarray(x)[None,:]-xc)**2<=radius**2

def extract(archive,centroids,matched,output):
    sha=verify_source(archive)
    cc=pd.read_csv(centroids)
    match=pd.read_csv(matched)
    assert (len(match),match.site_id.nunique())==(892,99), "Source-matched cohort drift"
    source=cc.loc[cc.site_id.isin(set(match.site_id))].copy()
    if len(source)!=99 or source.site_id.duplicated().any():
        raise ValueError("Original RDS site centroids not uniquely matched")
    transformer=Transformer.from_crs("EPSG:3031","EPSG:3412",always_xy=True)
    source["center_x3412"],source["center_y3412"]=transformer.transform(source.easting,source.northing)
    season_starts=sorted(match.season.unique().tolist())
    months=sorted({f"{int(season)}{m:02d}" for season in season_starts for m in (11,12)} |
                  {f"{int(season)+1}{m:02d}" for season in season_starts for m in (1,2)})
    if len(months)!=60:raise ValueError("Original season date set drift")
    with zipfile.ZipFile(archive) as z:
        months_in_zip={}
        for f in z.namelist():
            result=PATTERN.fullmatch(f)
            if result:
                date=result.group(1)
                if date in months:
                    if date in months_in_zip:raise ValueError("Multiple original SIC files in same date")
                    months_in_zip[date]=f
        if set(months_in_zip)!=set(months):
            raise ValueError("Missing original NSIDC source month(s): "+repr(sorted(set(months)-set(months_in_zip))))
        monthly=[]
        geographic={}
        monthlist=[]
        for month in months:
            with tempfile.TemporaryDirectory() as tmp:
                raw=Path(tmp)/"source_nsidc_month.nc"
                raw.write_bytes(z.read(months_in_zip[month]))
                with xr.open_dataset(raw,mask_and_scale=True) as ds:
                    if "cdr_seaice_conc_monthly" not in ds:
                        raise ValueError("Missing NOAA/NSIDC V4 true monthly sea ice")
                    variable=ds["cdr_seaice_conc_monthly"]
                    yname=next((x for x in variable.dims if x in ("ygrid","y")),None)
                    xname=next((x for x in variable.dims if x in ("xgrid","x")),None)
                    if not yname or not xname:raise ValueError("Unknown original 25km grid dimensions")
                    v=np.asarray(variable.squeeze(drop=True).transpose(yname,xname).values,dtype=float)
                    x=np.asarray(ds[xname].values,dtype=float)
                    y=np.asarray(ds[yname].values,dtype=float)
                    x,y,rebuilt=source_native_25km_axes(x,y)
                    if month==months[0]:
                        print("NSIDC_ORIGINAL_COORD_KIND",str(ds[xname].attrs),str(ds[yname].attrs),flush=True)
                    if v.shape!=(len(y),len(x)):raise ValueError("Source SIC dimensions drift")
                    if not (np.isfinite(x).all() and np.isfinite(y).all()):
                        raise ValueError("Invalid original polar grid coords")
                    # Missing/land/coastal flag values, if decoded to 2.51-2.55, are not valid concentrations.
                    v=np.where(np.isfinite(v)&(v>=0)&(v<=1),v,np.nan)
                    for r in source.itertuples(index=False):
                        k=r.site_id
                        if k not in geographic:
                            geographic[k]=cells_within(x,y,r.center_x3412,r.center_y3412)
                        mask=geographic[k]
                        if mask.shape!=v.shape:raise ValueError("Changed native SIC grid across source files")
                        val=v[mask]
                        good=val[np.isfinite(val)]
                        monthly.append({"site_id":k,"source_year":int(month[:4]),"source_month":int(month[-2:]),
                             "source_n_150km_cell_centers":int(mask.sum()),
                             "source_n_valid_ocean_cells":int(len(good)),
                             "source_sic150_center_mean_fraction":float(good.mean()) if len(good) else np.nan})
                    monthlist.append(months_in_zip[month])
            if len(monthly)%len(source)!=0:raise RuntimeError("Incomplete source month extraction")
            if month==months[0]:
                first=monthly[:len(source)]
                if not all(rec["source_n_150km_cell_centers"]>0 for rec in first):
                    raise ValueError("Source geographic mask cannot locate all 99 sites; NO zero-as-SIC interpretation")
                if not any(rec["source_n_valid_ocean_cells"]>=3 for rec in first):
                    raise ValueError("All 99 native source site-months lack valid ocean cells; diagnose coordinate orientation")
            print("ORIGINAL_NSIC_V4_MONTH:",month,flush=True)
    daily=pd.DataFrame(monthly)
    monthly_map={(r.site_id,r.source_year,r.source_month):r for r in daily.itertuples(index=False)}
    records=[]
    for r in match.itertuples(index=False):
        blocks=[monthly_map[(r.site_id,int(r.season),m)] for m in (11,12)]
        blocks += [monthly_map[(r.site_id,int(r.season)+1,m)] for m in (1,2)]
        values=[b.source_sic150_center_mean_fraction for b in blocks]
        valid=[b.source_n_valid_ocean_cells for b in blocks]
        records.append({
            "site_id":r.site_id,"season":int(r.season),
            "source_region":r.source_region,
            "author_SIC_150km_NovFeb_center_approx_fraction":float(np.mean(values)) if np.isfinite(values).all() else np.nan,
            "all_four_sic_months_valid":bool(np.isfinite(values).all()),
            "min_n_valid_25km_source_cells":int(min(valid)),
            "min_fraction_valid_ocean_cells":float(min(b.source_n_valid_ocean_cells/max(1,b.source_n_150km_cell_centers) for b in blocks)),
        })
    out=Path(output);out.mkdir(parents=True,exist_ok=True)
    derived=pd.DataFrame(records)
    derived.to_csv(out/"original_892_site_seasons_author_NSIDC_V4_NovFeb_150km_center_mean.csv",index=False)
    daily.to_csv(out/"original_99_sites_source_NSIDC_V4_monthly.csv",index=False)
    score={"status":"PUBLISHER_MD5_PINNED_NSIDC_V4_NOVFEB_150KM_CENTER_BUFFER_APPROX_NOT_TERRA_EXACT",
           "original_record_id":17409948,"source_zip":sha,"n_source_months":len(months),
           "n_original_site_months":len(daily),"n_original_site_seasons":len(derived),
           "n_matched_site_seasons_full_four_months":int(derived.all_four_sic_months_valid.sum()),
           "n_strict_geo_sites":int(derived.site_id.nunique()),"n_missing_months":len(months)-len(monthlist),
           "original_SIC_variable":"cdr_seaice_conc_monthly",
           "buffer_radius_m":RADIUS_M,"crs":"EPSG:3412",
           "uncertainty":"cell-center inclusion and valid ocean averages not necessarily exactly identical to terra::extract polygon means; missing and land flags excluded",
           "diet_salinity_association":"NOT ESTIMATED",
           "not_the_authors_unpublished_colony_SIC_table":True}
    (out/"nsidc150_source_receipt.json").write_text(json.dumps(score,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(score,indent=2,ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--archive",required=True)
    p.add_argument("--centroids",required=True)
    p.add_argument("--matched",required=True)
    p.add_argument("--out",required=True)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        x=np.array([-200e3,0,200e3]); y=x.copy()
        mask=cells_within(x,y,0,0)
        assert mask.shape==(3,3) and mask.sum()==1
        print("PASS 150km center-cell buffer geometry synthetic")
    else:
        extract(a.archive,a.centroids,a.matched,a.out)
