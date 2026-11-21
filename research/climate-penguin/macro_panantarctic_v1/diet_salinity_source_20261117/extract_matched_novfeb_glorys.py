#!/usr/bin/env python3
"""Actual Nov-Feb original GLORYS 202311 at source-verified Youngflesh site-seasons.
Physical exposure only: no diet response, no future population projection.
"""
from pathlib import Path
import argparse,json,zipfile
import numpy as np
import pandas as pd
import xarray as xr
import fsspec
from scipy.spatial import cKDTree
from pyproj import Transformer

SOURCE="https://s3.waw3-1.cloudferro.com/mdl-arco-time-025/arco/GLOBAL_MULTIYEAR_PHY_001_030/cmems_mod_glo_phy_my_0.083deg_P1M-m_202311/timeChunked.zarr"

def crosswalk(source_site_season,centroids,original_atlas,original_glorys):
    land=pd.read_csv(source_site_season); c=pd.read_csv(centroids)
    atlas=pd.read_csv(original_atlas); m=pd.read_csv(original_glorys)
    atlas["site_id"]=atlas.site_id.astype(str)
    land["site_id"]=land.site_id.astype(str)
    c["site_id"]=c.site_id.astype(str)
    xy=Transformer.from_crs("EPSG:4326","EPSG:3031",always_xy=True).transform(atlas.longitude,atlas.latitude)
    tree=cKDTree(np.column_stack(xy))
    status=[]
    for row in c.itertuples(index=False):
        d,k=tree.query([row.easting,row.northing],k=2)
        first=str(atlas.iloc[k[0]].site_id)
        status.append((row.site_id, bool(first==row.site_id and d[0]<=2000 and d[1]>2000)))
    good={k for k,v in status if v}
    if len(good)!=102:
        raise ValueError(f"Strict original geographical site support changed ({len(good)} vs 102)")
    land["season"]=pd.to_numeric(land.season,errors="raise").astype(int)
    land=land.loc[land.site_id.isin(good)&land.season.between(1993,2013)]
    m=m.loc[m.year==1997,["site_id","source_region","source_original_wet_grid_y","source_original_wet_grid_x"]]
    if m.site_id.duplicated().any():raise ValueError("Source site 1997 wetgrid duplicated")
    matched=land.merge(m,on="site_id",how="inner",validate="many_to_one")
    # Do not infer what was not surveyed: strictly original pixel-covered seasons only.
    expected=(892,99,92,14)
    cells=matched[["source_original_wet_grid_y","source_original_wet_grid_x"]].drop_duplicates()
    actual=(len(matched),matched.site_id.nunique(),len(cells),matched.source_region.nunique())
    if actual!=expected:raise ValueError(f"Original geometry cohort drift: expected {expected}, found {actual}")
    if matched.duplicated(["site_id","season"]).any():raise ValueError("Duplicate original Landsat site-season")
    return matched,cells

def extract(matched,cells,out):
    ds=xr.open_zarr(fsspec.get_mapper(SOURCE),consolidated=True)
    if not all(v in ds for v in ["so","thetao"]):raise ValueError("Original GLORYS source variable missing")
    depth=int(np.argmin(abs(ds.elevation.values)))
    if abs(float(ds.elevation.values[depth]))>2:raise ValueError("Surface depth not top wet level")
    seasons=np.sort(matched.season.unique())
    months=sorted({(int(y),mon) for y in seasons for mon in [11,12]} |
                  {(int(y)+1,mon) for y in seasons for mon in [1,2]})
    dts=pd.DatetimeIndex(ds.time.values)
    lookup={(d.year,d.month):i for i,d in enumerate(dts)}
    if not all(a in lookup for a in months):raise ValueError("Missing original GLORYS season-month")
    ti=[lookup[a] for a in months]
    cells=cells.sort_values(["source_original_wet_grid_y","source_original_wet_grid_x"]).reset_index(drop=True)
    ys=cells.source_original_wet_grid_y.to_numpy(dtype=int)
    xs=cells.source_original_wet_grid_x.to_numpy(dtype=int)
    coords={
        "time":xr.DataArray(ti,dims="source_month"),
        "latitude":xr.DataArray(ys,dims="wetcell"),
        "longitude":xr.DataArray(xs,dims="wetcell"),
        "elevation":depth,
    }
    arrays={}
    for name in ["so","thetao"]:
        v=ds[name].isel(**coords).load()
        arr=np.asarray(v.transpose("source_month","wetcell"),dtype=float)
        if arr.shape!=(len(months),len(cells)):raise ValueError(f"Source shape {name} {arr.shape}")
        arrays[name]=arr
    source=[]
    for i,(year,mon) in enumerate(months):
        for j,row in cells.iterrows():
            source.append({"source_year":year,"source_month":mon,
                "source_original_wet_grid_y":int(row.source_original_wet_grid_y),
                "source_original_wet_grid_x":int(row.source_original_wet_grid_x),
                "GLORYS_surface_salinity":float(arrays["so"][i,j]),
                "GLORYS_surface_thetao_C":float(arrays["thetao"][i,j])})
    grid=pd.DataFrame(source)
    grid["valid"]=(grid.GLORYS_surface_salinity.between(20,42) & grid.GLORYS_surface_thetao_C.between(-4,25))
    if not grid.valid.all():
        raise ValueError("Original-source matched Nov-Feb has invalid GLORYS cells; NO imputation")
    seasonal=[]
    idx=grid.set_index(["source_original_wet_grid_y","source_original_wet_grid_x","source_year","source_month"])
    for r in matched.itertuples(index=False):
        cells_=[]
        for yr,mo in [(r.season,11),(r.season,12),(r.season+1,1),(r.season+1,2)]:
            cells_.append(idx.loc[(r.source_original_wet_grid_y,r.source_original_wet_grid_x,yr,mo)])
        raw=pd.DataFrame(cells_)
        seasonal.append({"site_id":r.site_id,"season":int(r.season),"source_region":r.source_region,
            "source_wet_grid_y":int(r.source_original_wet_grid_y),
            "source_wet_grid_x":int(r.source_original_wet_grid_x),
            "source_n_landsat_pixels":int(r.n_original_landsat_records),
            "GLORYS_NovFeb_salinity":float(raw.GLORYS_surface_salinity.mean()),
            "GLORYS_NovFeb_thetao_C":float(raw.GLORYS_surface_thetao_C.mean()),
            "all_four_original_months_valid":len(raw)==4})
    output=pd.DataFrame(seasonal)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    output.to_csv(out/"original_892_matched_site_season_NovFeb_GLORYS.csv",index=False)
    grid.to_csv(out/"unique_wet_cell_NovFeb_GLORYS_monthly.csv",index=False)
    receipt={"status":"ORIGINAL_NOVFEB_GLORYS_SOURCE_MATCHED_TO_AUTHOR_IMAGE_SEASONS_NO_DI",
        "GLORYS_product":"GLORYS12V1 202311 original source","original_source_url":SOURCE,
        "n_original_sic_independent_census_sites":"NOT_MEASURED",
        "source_image_site_seasons":len(output),"distinct_sites":int(output.site_id.nunique()),
        "distinct_wet_grid_cells":int(len(cells)),"distinct_regions":int(output.source_region.nunique()),
        "source_months":len(months),"source_unique_wet_months":len(grid),
        "seasons":seasons.tolist(),
        "not_original_150km_sic":True,"not_diet_effect":True,"no_imputed_missing_years":True}
    (out/"original_novfeb_glorys_receipt.json").write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(receipt,indent=2,ensure_ascii=False))
    return receipt

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--source-seasons",required=True)
    p.add_argument("--centroids",required=True)
    p.add_argument("--atlas",required=True)
    p.add_argument("--glorys",required=True)
    p.add_argument("--out",required=True)
    args=p.parse_args()
    cohort,cells=crosswalk(args.source_seasons,args.centroids,args.atlas,args.glorys)
    extract(cohort,cells,args.out)
