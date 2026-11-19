#!/usr/bin/env python3
"""Actual 1996/1999-2012 original indexed ocean physical A/B candidates only.

NO isotope outcomes. NO fish fractions. NO C=200m mechanism fit.
- A: winter Jun-Oct sea-surface salinity (brine/polynya candidate, not label)
- B: Nov-Feb TEOS-10 sigma0(near 50m) - sigma0(surface)
Only original actual wet grid for each isotope source site×season.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import fsspec
import gsw
import numpy as np
import pandas as pd
import xarray as xr

from preflight_original_82_wetcells_glorys_depths_20261119 import (
    source_cohort, select_levels, ZARR_URL,
)

def make_months(seasons):
    winter={(int(y), int(m)) for y in seasons for m in range(6, 11)}
    summer={(int(y), 11) for y in seasons} | {(int(y), 12) for y in seasons}
    summer |= {(int(y)+1, 1) for y in seasons} | {(int(y)+1, 2) for y in seasons}
    months=sorted(winter | summer)
    if (len(winter), len(summer),len(months)) != (75,60,135):
        raise ValueError("Original seasons winter/summer month denominator drift")
    return months

def get_native_months(ds, cells, month_index, depth_idx):
    ys=cells.source_wet_grid_y.to_numpy(dtype=int)
    xs=cells.source_wet_grid_x.to_numpy(dtype=int)
    indexing={
        "time":xr.DataArray(month_index,dims="source_month"),
        "latitude":xr.DataArray(ys,dims="wetcell"),
        "longitude":xr.DataArray(xs,dims="wetcell"),
        "elevation":xr.DataArray(depth_idx,dims="depth"),
    }
    arrays={}
    for name in ("so","thetao"):
        r=ds[name].isel(**indexing).transpose(
            "source_month","wetcell","depth").load().values
        r=np.asarray(r,dtype=float)
        if r.shape != (135,82,2):
            raise ValueError(f"Original physics shape drift: {name} {r.shape}")
        arrays[name]=r
    return arrays

def actual_density(so,theta,ds,cells,actual_depths):
    ys=cells.source_wet_grid_y.to_numpy(dtype=int)
    xs=cells.source_wet_grid_x.to_numpy(dtype=int)
    lat=np.asarray(ds.latitude.values[ys],dtype=float)
    lon=np.asarray(ds.longitude.values[xs],dtype=float)
    z=np.asarray(actual_depths,dtype=float)
    # gsw requires sea pressure for practical salinity -> Absolute Salinity.
    pressure=gsw.p_from_z(-z[None,:],lat[:,None])
    latfull=np.broadcast_to(lat[None,:,None],so.shape)
    lonfull=np.broadcast_to(lon[None,:,None],so.shape)
    pfull=np.broadcast_to(pressure[None,:,:],so.shape)
    native_valid=(np.isfinite(so)&np.isfinite(theta)&
                  (so>=20)&(so<=42)&(theta>=-4)&(theta<=25))
    with np.errstate(invalid="ignore"):
        SA=gsw.SA_from_SP(so,pfull,lonfull,latfull)
        CT=gsw.CT_from_pt(SA,theta)
        sigma=gsw.sigma0(SA,CT)
    sigma=np.asarray(sigma,dtype=float)
    sigma[~native_valid]=np.nan
    return sigma,native_valid

def physical_season(cohort,cells,months,actual_depths,arrays,sigma,valid):
    lookup={v:i for i,v in enumerate(months)}
    output=[]
    # 82 unique ocean wetcells × 15 source season years, no outcome.
    for y in sorted(cohort.season.astype(int).unique()):
        winter=[lookup[(y,m)] for m in range(6,11)]
        summer=[lookup[(y,11)],lookup[(y,12)],
                lookup[(y+1,1)],lookup[(y+1,2)]]
        for ci,c in cells.iterrows():
            av=valid[winter,ci,0]
            bv=valid[summer,ci,0]
            cv=valid[summer,ci,1]
            ss=arrays["so"]
            tt=arrays["thetao"]
            cnt_a=int(np.sum(av))
            cnt_b=int(np.sum(bv))
            cnt_c=int(np.sum(cv))
            a=float(np.mean(ss[winter,ci,0])) if cnt_a==5 else np.nan
            b=float(np.mean(ss[summer,ci,0])) if cnt_b==4 else np.nan
            t=float(np.mean(tt[summer,ci,0])) if cnt_b==4 else np.nan
            strat=float(np.mean(sigma[summer,ci,1]-sigma[summer,ci,0])) if (cnt_b==4 and cnt_c==4) else np.nan
            output.append({
                "season":int(y),
                "source_wet_grid_y":int(c.source_wet_grid_y),
                "source_wet_grid_x":int(c.source_wet_grid_x),
                "winter_JunOct_surface_so":a,
                "summer_NovFeb_surface_so":b,
                "summer_NovFeb_surface_thetao":t,
                "summer_NovFeb_sigma0_50m_minus_0m":strat,
                "source_winter_0m_months":cnt_a,
                "source_summer_0m_months":cnt_b,
                "source_summer_50m_months":cnt_c,
                "B_complete_TEOS10_density":bool(cnt_b==4 and cnt_c==4),
                "actual_top_model_depth_m":float(actual_depths[0]),
                "actual_50m_model_depth_m":float(actual_depths[1]),
            })
    phys=pd.DataFrame(output)
    if len(phys)!=82*15 or phys.duplicated(
        ["season","source_wet_grid_y","source_wet_grid_x"]).any():
        raise ValueError("Original one wetcell×season physical denominator drift")
    return phys

def source_link(cohort,phys):
    metadata=["site_id","season","source_region","source_wet_grid_y",
              "source_wet_grid_x","GLORYS_NovFeb_salinity"]
    d=cohort[metadata].merge(
        phys,on=["season","source_wet_grid_y","source_wet_grid_x"],
        validate="many_to_one",how="left")
    if (len(d),d.site_id.nunique(),d.source_region.nunique())!=(860,88,13):
        raise ValueError("Original source observational rows altered")
    if d[["source_winter_0m_months","source_summer_0m_months"]].isna().any().any():
        raise ValueError("Unmatched real source physics")
    # A second original-source independent extraction of Nov-Feb surface must
    # agree with the previously SHA-pinned original 860 marine exposure.
    dif=(d.summer_NovFeb_surface_so-d.GLORYS_NovFeb_salinity).abs()
    if dif.isna().any() or dif.max()>1e-4:
        raise ValueError(f"Original NovFeb same-cell salinity reconstruction mismatch: max {dif.max()}")
    d=d.drop(columns="GLORYS_NovFeb_salinity")
    return d,float(dif.max())

def main(a):
    cohort,cells,regions,source_sha=source_cohort(a.original_isotope_zip)
    seasons=sorted(cohort.season.astype(int).unique())
    months=make_months(seasons)
    ds=xr.open_zarr(fsspec.get_mapper(ZARR_URL),consolidated=True)
    idx, actual = select_levels(ds)
    chosen_levels=idx[:2]
    month_lookup={(d.year,d.month):i for i,d in enumerate(pd.DatetimeIndex(ds.time.values))}
    if not all(m in month_lookup for m in months):
        raise ValueError("Original physical winter/summer source months missing")
    ocean=get_native_months(ds,cells,[month_lookup[m] for m in months],chosen_levels)
    sigma,valid=actual_density(ocean["so"],ocean["thetao"],ds,cells,actual[:2])
    phys=physical_season(cohort,cells,months,actual[:2],ocean,sigma,valid)
    linked,max_diff=source_link(cohort,phys)
    # Export explicitly pre-outcome PHYSICAL variables, no copied Y or DI.
    summary_region=linked.groupby("source_region",sort=True).agg(
        site_seasons=("site_id","size"),
        original_sites=("site_id","nunique"),
        complete_winter=("winter_JunOct_surface_so","count"),
        complete_summer_surface=("summer_NovFeb_surface_so","count"),
        complete_summer_density50=("summer_NovFeb_sigma0_50m_minus_0m","count")
    ).reset_index()
    receipt={
        "status":"PHYSICAL_AB_82CELL_WINTER_SALINITY_AND_50M_DENSITY_SOURCE_ONLY",
        "isotope_outcomes_used_in_any_calculation":False,
        "no_cdw_200m_biological_mechanism_regression":True,
        "original_cohort_rows":860,
        "original_sites":88,
        "original_wetcells":82,
        "source_reporting_regions":13,
        "source_seasons":seasons,
        "source_model":ZARR_URL,
        "source_archive_sha256":source_sha,
        "source_months_actual":len(months),
        "original_cell_by_season_physical_rows":len(phys),
        "actual_depth_levels_m":actual[:2],
        "original_NovFeb_surface_so_agreement_max_abs":max_diff,
        "winter_so_complete_original_site_seasons":int(linked.winter_JunOct_surface_so.count()),
        "summer_so_complete_original_site_seasons":int(linked.summer_NovFeb_surface_so.count()),
        "50m_density_complete_original_site_seasons":int(linked.summer_NovFeb_sigma0_50m_minus_0m.count()),
        "50m_density_complete_wetcells":int(phys.groupby(
            ["source_wet_grid_y","source_wet_grid_x"]
        ).B_complete_TEOS10_density.all().sum()),
        "regions_support":summary_region.to_dict("records"),
        "physics_only_not_polynya_identification_or_freshwater_attribution":True,
        "no_future_diet_projection":True,
    }
    a.out.mkdir(parents=True,exist_ok=True)
    phys.to_csv(a.out/"source_82_cells_15seasons_winter_salinity_summer_density.csv",index=False)
    linked.to_csv(a.out/"source_860_site_seasons_A_B_physics_only_NO_OUTCOME.csv",index=False)
    summary_region.to_csv(a.out/"source_13regions_A_B_physical_support.csv",index=False)
    (a.out/"source_AB_physical_exposure_receipt.json").write_text(
        json.dumps(receipt,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(receipt,indent=2,ensure_ascii=False))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--original-isotope-zip",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    main(p.parse_args())
