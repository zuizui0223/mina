#!/usr/bin/env python3
"""Provider-native DEEP-AA recommended subset source gate; no optical isotope responses."""
from __future__ import annotations
import argparse
import calendar
import hashlib
import io
import json
import re
import zipfile
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
import numpy as np
import pandas as pd
from netCDF4 import Dataset

PROVIDER_RECORD="https://zenodo.org/records/13358042"
PROVIDER_DOI="10.5281/zenodo.13358042"
RECOMMENDED="SIC60_6.25km_20d.zip"
PROVIDER_MD5="f3f958389cc5e67ac1c4e3a6ee164318"
SOURCE_SHA="dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205"
SOURCE_CSV="matched_860_original_isotope_ocean_ice_site_seasons.csv"
DATE_RE=re.compile(r"(?<!\d)(20(?:0\d|1\d|2[012])\d{4})(?!\d)")
def checksum(path,alg):
    h=hashlib.new(alg)
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(2**21),b""):
            h.update(b)
    return h.hexdigest()

def schema_one(zipf,name):
    raw=zipf.read(name)
    try:
        f=Dataset("memory.nc","r",memory=raw)
        try:
            dims={k:len(d) for k,d in f.dimensions.items()}
            attrs={k:str(getattr(f,k))[:250] for k in f.ncattrs()}
            variables={}
            for k,v in f.variables.items():
                meta={"shape":list(v.shape),"dimensions":list(v.dimensions),"dtype":str(v.dtype),
                      "attrs":{t:str(getattr(v,t))[:250] for t in v.ncattrs()}}
                if 0<len(v.shape)<=2 and np.prod(v.shape)<5_000_000:
                    s=np.asarray(v[:])
                    if np.ma.isMaskedArray(v[:]):
                        s=np.ma.filled(v[:],np.nan).astype(float)
                    # A real pixel sampled from native file, to inspect ID/flags not infer metadata.
                    if s.ndim==2 and np.issubdtype(s.dtype,np.number):
                        p=s[::max(1,s.shape[0]//32),::max(1,s.shape[1]//32)]
                        meta["sample_finite_min_max"]=[float(np.nanmin(p)),float(np.nanmax(p))] if np.isfinite(p).any() else None
                        vals,cnts=np.unique(p[np.isfinite(p)],return_counts=True)
                        idx=np.argsort(-cnts)[:12]
                        meta["sample_top_values"]=[{"value":float(vals[i]),"count":int(cnts[i])} for i in idx]
                    elif s.ndim==1 and np.issubdtype(s.dtype,np.number):
                        meta["first_last"]=[float(s.flat[0]),float(s.flat[-1])]
                variables[k]=meta
            return {"member":name,"native_file_bytes":len(raw),"data_model":f.data_model,
                    "dimensions":dims,"global_attrs":attrs,"variables":variables}
        finally:
            f.close()
    except Exception as e:
        return {"member":name,"native_file_bytes":len(raw),"parse_error":str(e)}

def read_source_shape(p):
    if checksum(p,"sha256")!=SOURCE_SHA:
        raise ValueError("Original 860 optical isotope archive not SHA locked")
    with zipfile.ZipFile(p) as z:
        d=pd.read_csv(io.BytesIO(z.read(SOURCE_CSV)),low_memory=False)
    if (len(d),d.site_id.nunique(),d.source_region.nunique())!=(860,88,13):
        raise ValueError("860/88/13 original observational cohort drift")
    # Export only SITE/SEASON/GEO geography; no optical isotope outcomes.
    coords=[x for x in d.columns if any(y in x.lower() for y in
            ["latitude","longitude","easting","northing","centroid","x_coord","y_coord","geometry"])]
    out=d[["site_id","season","source_region"]+coords].copy()
    assert out[["site_id","season"]].duplicated().sum()==0
    return d, out, coords

def main(a):
    got=checksum(a.deepaa_zip,"md5")
    if got!=PROVIDER_MD5:raise ValueError(f"DEEP-AA recommended original ZIP md5 mismatch: {got}")
    _,cohort,coords=read_source_shape(a.original_zip)
    info=[]
    schemas=[]
    with zipfile.ZipFile(a.deepaa_zip) as z:
        invalid=z.testzip()
        if invalid:raise ValueError("DEEP-AA source original NetCDF ZIP CRC failed: "+invalid)
        zlist=z.namelist()
        for name in zlist:
            if not name.lower().endswith(".nc"):continue
            m=DATE_RE.search(Path(name).name)
            if not m: raise ValueError("Native daily filename DATE cannot be parsed: "+name)
            try:
                dt=date.fromisoformat(m.group(1)[:4]+"-"+m.group(1)[4:6]+"-"+m.group(1)[6:])
            except Exception as e:
                raise ValueError(f"Invalid original daily file date {name}: {e}")
            info.append({"day":dt.isoformat(),"file":name,"bytes":z.getinfo(name).file_size})
        if not info:raise ValueError("NO native daily NetCDF maps found in DEEP-AA source")
        dates=[x["day"] for x in info]
        if len(dates)!=len(set(dates)):
            raise ValueError("Multiple maps per source day; must resolve proper subset version")
        name_by_date={x["day"]:x["file"] for x in info}
        probe_dates=[dates[0],next((d for d in dates if d.startswith("2005-07")),dates[len(dates)//3]),
            next((d for d in dates if d.startswith("2010-07")),dates[len(dates)//2])]
        for d in dict.fromkeys(probe_dates):
            schemas.append(schema_one(z,name_by_date[d]))
    if any("parse_error" in x for x in schemas):
        raise ValueError("Unable to verify actual native DEEP-AA coordinate/variable semantics")
    by_year_month=Counter([x["day"][:7] for x in info])
    winter_support=[]
    for year in sorted(set(cohort.season.astype(int))):
        coverage=[]
        for month in range(6,11):
            n=by_year_month[f"{year:04d}-{month:02d}"]
            days=calendar.monthrange(year,month)[1]
            coverage.append({"month":f"{year:04d}-{month:02d}","observed_daily_maps":int(n),
                             "days_calendar":int(days),"fraction_of_calendar_days":n/days,
                             "complete_80pct":bool(n/days>=0.8)})
        winter_support.append({"source_isotope_season":int(year),
           "months":coverage,"all_five_months_gte_80pct":all(q["complete_80pct"] for q in coverage)})
    original_cohort_years=cohort.groupby("season",sort=True).agg(
       n_site_seasons=("site_id","size"),n_sites=("site_id","nunique"),
       n_regions=("source_region","nunique")).reset_index().to_dict("records")
    months_pass=[int(x["source_isotope_season"]) for x in winter_support if x["all_five_months_gte_80pct"]]
    out={
      "status":"VERIFIED_PROVIDER_NATIVE_MANIFEST_PREFLIGHT_NO_Y_FIT",
      "doi":PROVIDER_DOI,"record":PROVIDER_RECORD,"source_zip":RECOMMENDED,
      "source_expected_provider_md5":PROVIDER_MD5,"source_verified_md5":got,
      "source_sha256":checksum(a.deepaa_zip,"sha256"),
      "source_n_all_native_netCDF_daily_maps":len(info),
      "source_first_last_days":[min(dates),max(dates)],
      "original_isotope_rows":len(cohort),"original_site_seasons_undrifted":860,
      "original_88_site_geographic_columns":coords,
      "provider_source_native_file_samples":schemas,
      "original_source_isotope_cohort_season_counts":original_cohort_years,
      "winter_by_original_isotope_season":winter_support,
      "source_full_80pct_winter_years_before_response_open":months_pass,
      "did_not_access_or_test_optical_isotope_response":True,
      "no_isotope_mechanism_test_performed":True,
      "source_only_proxy_not_fish_fraction":True,
    }
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/"DEEPAA_NATIVE_SOURCE_MANIFEST_RECEIPT.json").write_text(
        json.dumps(out,indent=2,ensure_ascii=False,default=str)+"\n")
    pd.DataFrame(info).to_csv(a.out/"native_DEEPAA_actual_daily_files.csv",index=False)
    cohort.to_csv(a.out/"original_860_site_seasons_NO_OUTCOME_geography.csv",index=False)
    print(json.dumps({"status":out["status"],"source_sha256":out["source_sha256"],
      "native_files":len(info),"years_pass_winter":months_pass,
      "original_source_geographic_columns":coords,
      "native_samples":schemas},indent=2,ensure_ascii=False))
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--deepaa-zip",required=True,type=Path)
    p.add_argument("--original-zip",required=True,type=Path)
    p.add_argument("--out",required=True,type=Path)
    main(p.parse_args())
