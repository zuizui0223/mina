#!/usr/bin/env python3
"""Original GLORYS12V1 monthly 1993–2020 marine salinity+thetao for all source
595 Antarctic colony IDs with >=2011-09 wet-grid match <=25 km.

The 40 original site wet cells and 34 true GLORYS+SIC 2011–2020 data are
independently source-reproduced before any new 18-region scientific inference.
Never conflate reanalysis marine point exposure with bird foraging conditions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict, Counter
from pathlib import Path

import fsspec
import numpy as np
import pandas as pd
import xarray as xr

EXPECTED_OLD_GIT_BLOBS={
    "original_manifest":"7d62ce17e77ae356ea62116d2446b0a8521c7ded",
    "original_GLORYS_2011_2021":"cafa0e6f934ad5e3ae67ca0c6cd52d1e29156dd6",
    "original_40_ocean_mapping":"5d0f90cab39e192645b3ff3406a40349a0ff22d0"
}
EXPECTED_SOURCE="https://s3.waw3-1.cloudferro.com/mdl-arco-time-025/arco/GLOBAL_MULTIYEAR_PHY_001_030/cmems_mod_glo_phy_my_0.083deg_P1M-m_202311/timeChunked.zarr"
MONTHS=(8,9,10,11)
YEARS=range(1993,2021)
EXPECTED_SITES=595
EXPECTED_OLD_VALID_SITES=34
MAX_SOURCE_DISTANCE_KM=25.0
MAX_ORIGINAL_OVERLAP_DIFFERENCE=1e-5


def readcsv(path):
    return pd.read_csv(path)


def pinned(path,expected):
    raw=path.read_bytes()
    sha=hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
    if sha!=expected:
        raise ValueError(f"Original marine source Git blob changed {path}: expected {expected}, got {sha}")
    return raw


def extract(args):
    meta=json.loads(pinned(args.manifest,EXPECTED_OLD_GIT_BLOBS["original_manifest"]))
    pinned(args.old40,EXPECTED_OLD_GIT_BLOBS["original_40_ocean_mapping"])
    pinned(args.old_ocean,EXPECTED_OLD_GIT_BLOBS["original_GLORYS_2011_2021"])
    if meta["store"]!=EXPECTED_SOURCE or meta["version"]!="202311":
        raise ValueError("GLORYS source original 202311 store identity changed")
    source=pd.read_csv(args.geography)
    original=pd.read_csv(args.atlas)
    if len(source)!=EXPECTED_SITES or len(original)!=EXPECTED_SITES:
        raise ValueError("Source 595-site geographic coverage drift")
    if set(source.site_id)!=set(original.site_id):
        raise ValueError("Original 595 site source ID crosswalk drift")
    eligible=source.loc[source.source_wet_2011_september_25km_gate.astype(str).str.lower()=="true"].copy()
    if len(eligible)<EXPECTED_OLD_VALID_SITES or eligible.site_id.nunique()!=len(eligible):
        raise ValueError("No original usable GLORYS source sites")
    if (eligible.true_geodesic_source_cell_distance_km>MAX_SOURCE_DISTANCE_KM).any():
        raise ValueError("Original 25km geodesic marine source gate changed")
    original40=pd.read_csv(args.old40)
    original40=original40.loc[original40.cohort=="macro_40"]
    expected_valid40=original40.loc[original40.grid_within_25km]
    if len(original40)!=40 or len(expected_valid40)!=EXPECTED_OLD_VALID_SITES:
        raise ValueError("Original 40 site source mapping count drift")
    old_sites=set(expected_valid40.site_id)
    if not old_sites.issubset(set(eligible.site_id)):
        raise ValueError("Previously supported GLORYS marine site lost")
    for r in expected_valid40.itertuples(index=False):
        q=eligible.loc[eligible.site_id==r.site_id].iloc[0]
        if (int(q.original_glorys_grid_y),int(q.original_glorys_grid_x))!=(int(r.grid_y),int(r.grid_x)):
            raise ValueError("Original GLORYS source grid cell changed from frozen 34-site reference")

    print("OPEN ORIGINAL GLORYS SOURCE "+meta["store"],flush=True)
    ds=xr.open_zarr(fsspec.get_mapper(meta["store"]),consolidated=True)
    depth=int(np.argmin(np.abs(ds.elevation.values)))
    depthval=float(ds.elevation.values[depth])
    if abs(depthval-meta["top_level_coordinate_m"])>1e-5:
        raise ValueError("Original GLORYS surface reference depth drift")
    time=pd.DatetimeIndex(ds.time.values)
    months=np.flatnonzero((time.year>=YEARS.start)&(time.year<YEARS.stop)
                          &np.isin(time.month,MONTHS))
    if len(months)!=len(YEARS)*4:
        raise ValueError(f"Original 1993–2020 GLORYS monthly source incomplete ({len(months)})")
    gridpoints=sorted({(int(r.original_glorys_grid_y),int(r.original_glorys_grid_x))
                       for r in eligible.itertuples(index=False)})
    indexes={k:i for i,k in enumerate(gridpoints)}
    lat_ix=np.asarray([k[0] for k in gridpoints],dtype=int)
    lon_ix=np.asarray([k[1] for k in gridpoints],dtype=int)
    old_grid=original40.set_index("site_id")
    for r in eligible.itertuples(index=False):
        if not np.isclose(float(ds.latitude.values[int(r.original_glorys_grid_y)]),
                          float(r.original_glorys_latitude),atol=2e-4):
            raise ValueError("GLORYS original native ocean latitude changed")
        if not np.isclose(float(ds.longitude.values[int(r.original_glorys_grid_x)]),
                          float(r.original_glorys_longitude),atol=2e-4):
            raise ValueError("GLORYS original native ocean longitude changed")

    selector={
        "time":xr.DataArray(months,dims="source_month"),
        "latitude":xr.DataArray(lat_ix,dims="source_wet_cell"),
        "longitude":xr.DataArray(lon_ix,dims="source_wet_cell"),
        "elevation":depth
    }
    arrays={}
    for var in ("so","thetao"):
        # Use unique original wet grid cells, not Nsites near-duplicates,
        # reducing both provider requests and pseudoreplication in metadata.
        sample=ds[var].isel(**selector).load()
        data=np.asarray(sample.transpose("source_month","source_wet_cell").values,dtype=np.float64)
        if data.shape!=(len(months),len(gridpoints)):
            raise ValueError("Unexpected full original month×wet-cell array shape")
        arrays[var]=data
        print(f"GLORYS_595_LOAD_VAR={var} months={len(months)} "
              f"unique_source_grid_cells={len(gridpoints)} finite={int(np.isfinite(data).sum())}",flush=True)
    old=pd.read_csv(args.old_ocean)
    old=old.loc[old.location_id.isin(set(original40.location_id))&
                old.year.between(2011,2020)&old.month.isin(MONTHS)]
    if len(old)!=40*10*4:
        raise ValueError("Original 40-site 2011–2020 source GLORYS cross-check records drift")
    old40_loc=original40.set_index("location_id")["site_id"].to_dict()
    old["site_id"]=old.location_id.map(old40_loc)
    old=old.loc[old.site_id.isin(old_sites)]
    if len(old)!=EXPECTED_OLD_VALID_SITES*40:
        raise ValueError("Original 34-site all-40-month source overlap drift")
    original_value_by={(r.site_id,int(r.year),int(r.month)):r
                       for r in old.itertuples(index=False)}
    if len(original_value_by)!=EXPECTED_OLD_VALID_SITES*40:
        raise ValueError("Original 34 wet-point ocean salinity/temperature site key duplicated")

    records=[]
    source_gaps=Counter()
    for r in eligible.itertuples(index=False):
        index=indexes[int(r.original_glorys_grid_y),int(r.original_glorys_grid_x)]
        for t,mi in enumerate(months):
            year,month=int(time[mi].year),int(time[mi].month)
            so=float(arrays["so"][t,index]);thetao=float(arrays["thetao"][t,index])
            valid=(np.isfinite(so) and np.isfinite(thetao)
                   and 20<=so<=42 and -4<=thetao<=25)
            if not valid:
                source_gaps[r.site_id]+=1
            records.append({
                "site_id":r.site_id,
                "source_region":r.source_region,
                "source_250km_block":r.source_250km_block,
                "year":year,"month":month,
                "surface_GLORYS_salinity":so if valid else None,
                "surface_GLORYS_thetao_C":thetao if valid else None,
                "source_original_wet_grid_y":int(r.original_glorys_grid_y),
                "source_original_wet_grid_x":int(r.original_glorys_grid_x),
                "source_geodesic_wet_cell_distance_km":float(r.true_geodesic_source_cell_distance_km),
                "source_both_ocean_variables_valid":bool(valid),
                "source_GLORYS_is_reanalysis_not_in_situ_observation":True,
            })
    all_=pd.DataFrame(records)
    if len(all_)!=len(eligible)*len(months) or all_.duplicated(["site_id","year","month"]).any():
        raise ValueError("Original 595 marine month/cohort key drift")
    q=all_.loc[all_.site_id.isin(old_sites)&all_.year.between(2011,2020)]
    if len(q)!=EXPECTED_OLD_VALID_SITES*40:
        raise ValueError("Not all 34 baseline wet GLORYS sites retained in 2011–2020")
    diffs={"surface_GLORYS_salinity":0.,"surface_GLORYS_thetao_C":0.}
    for rec in q.itertuples(index=False):
        original=original_value_by[rec.site_id,int(rec.year),int(rec.month)]
        for key,left,right in (
            ("surface_GLORYS_salinity",rec.surface_GLORYS_salinity,original.surface_salinity),
            ("surface_GLORYS_thetao_C",rec.surface_GLORYS_thetao_C,original.surface_potential_temperature_c)):
            if not np.isfinite([left,right]).all():
                raise ValueError("Frozen original 34-site salinity/temp source value changed to missing")
            deviation=abs(float(left)-float(right))
            diffs[key]=max(diffs[key],deviation)
            if deviation>MAX_ORIGINAL_OVERLAP_DIFFERENCE:
                raise ValueError(f"Frozen original 34×40 GLORYS source value {key} drift {deviation}")
    group=defaultdict(list)
    for rec in eligible.itertuples(index=False):
        group[rec.source_region].append(rec.site_id)
    byregion=[]
    for region,sites in sorted(group.items()):
        part=all_.loc[all_.source_region==region]
        byregion.append({
            "source_region":region,
            "original_595_colony_sites_nearest_GLORYS_wet_within25km":len(sites),
            "original_unique_GLORYS_wet_grid_cells":len({
                (int(z.original_glorys_grid_y),int(z.original_glorys_grid_x))
                for z in eligible.itertuples(index=False) if z.source_region==region}),
            "original_marine_month_records_1993_2020":len(part),
            "valid_original_marine_month_records_1993_2020":int(part.source_both_ocean_variables_valid.sum()),
            "n_original_sites_with_all_112_marine_months_valid":sum(source_gaps[s]==0 for s in sites),
            "regions_are_not_fully_independent_ocean_reanalysis_samples":True
        })
    args.out.mkdir(parents=True,exist_ok=True)
    target=args.out/"all_original_eligible_colony_GLORYS12_1993_2020_AugNov_monthly.csv"
    all_.to_csv(target,index=False)
    pd.DataFrame(byregion).to_csv(args.out/"all_18_original_region_GLORYS_monthly_coverage.csv",index=False)
    info={
        "status":"ORIGINAL_GLORYS_202311_ALL_ELIGIBLE_MACRO_595_COLONY_MONTHS_EXTRACTED_AND_34_LEGACY_SOURCE_REPRODUCED",
        "source":{
            "frozen_original_595_source_sites":EXPECTED_SITES,
            "n_original_wet_cell_25km_supported_sites":len(eligible),
            "n_source_18_region_labels":len(group),
            "n_unique_original_wet_source_GLORYS_cells":len(gridpoints),
            "source_product":meta["product"],
            "source_version":meta["version"],
            "source_store":meta["store"],
            "top_sea_level_m":depthval,
            "source_month_count":len(months),
            "source_real_month_years":[YEARS.start,YEARS.stop-1],
            "original_GLORYS_surface_reanalysis_records":len(all_),
            "n_original_site_months_with_both_marine_sources_valid":int(all_.source_both_ocean_variables_valid.sum()),
            "n_original_sites_with_all_112_source_months_complete":
                len(eligible)-len(source_gaps),
            "n_original_known_34_site_2011_2020_monthly_values_crosschecked":len(q),
            "max_abs_original_34_source_ocean_difference":diffs,
            "original_2011_09_ocean_mask_used_to_select_pixels":True,
            "all_40_known_GLORYS_native_ocean_pixel_identity_source_matched":True,
            "original_git_blobs":EXPECTED_OLD_GIT_BLOBS
        },
        "source_regions":byregion,
        "inference_limits":[
          "This is a Copernicus GLORYS12V1 reanalysis (data assimilation), not in situ salinity observations.",
          "Original nearshore fixed wet ocean grid point does not establish a foraging niche or accessible marine route.",
          "Two observed penguin colonies can share exactly the same ocean reanalysis cell; source geographical independence is lower.",
          "Only original 1993–2020 monthly Aug–Nov salinity and potential seawater temperature; no additional plant annual series.",
          "No ecological species absence from missing original census years or inaccessible marine source grid.",
          "No greenhouse warming causal attribution or biological future survival prediction is performed in this original source extractor."
        ]
    }
    (args.out/"original_595_GLORYS_1993_2020_source_and_34_site_overlap_receipt.json").write_text(
        json.dumps(info,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("GLORYS_595_1993_2020_SOURCE_AUDIT="+json.dumps(info["source"],ensure_ascii=False),flush=True)
    print("GLORYS_595_18_REGION_SOURCE_COVERAGE="+json.dumps(byregion,ensure_ascii=False),flush=True)
    return info


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--geography",type=Path,required=True)
    ap.add_argument("--atlas",type=Path,required=True)
    ap.add_argument("--old40",type=Path,required=True)
    ap.add_argument("--old-ocean",type=Path,required=True)
    ap.add_argument("--manifest",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    extract(ap.parse_args())


if __name__=="__main__":
    main()
