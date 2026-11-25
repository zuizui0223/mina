"""D1: source-timed winter index; descriptive only, V1 remains blocked."""
import argparse,hashlib,json,sys,datetime as dt
from pathlib import Path
import numpy as np
import pandas as pd
import requests
import xarray as xr
from prepare_panel import read,num,source_extract,PINS,seal_gate,digest
from analyze import z,fit
from collections import defaultdict
import statistics
YEARS=[1996,1999,2000,2001,2004,2005,2006,2008,2009,2011,2012,2013,2015,2016,2017,2018,2019]
ROSTER={"Adelie":["A2","A3","A4"],"Chinstrap":["C15","C16","C17","C79","C80"],"Gentoo":["SIGNY_SOURCE_AGGREGATE"]}
# Transport-only revision: annual chunks, unchanged D1 window and mask.
HOSTS=["https://upwell.pfeg.noaa.gov","https://coastwatch.pfeg.noaa.gov"]
LATS=np.arange(-61.875,-60,0.25)
LONS=np.arange(-46.875,-44,0.25)
def fetch_year(y,out):
    from urllib.parse import quote
    query=f"ice[({y}-05-01T12:00:00Z):1:({y}-10-31T12:00:00Z)][(0.0)][(-61.875):1:(-60.125)][(-46.875):1:(-44.125)]"
    failures=[]
    for host in HOSTS:
        url=host+"/erddap/griddap/ncdcOisst21Agg_LonPM180.nc?"+quote(query,safe="[]():,")
        try:
            r=requests.get(url,timeout=(15,100));r.raise_for_status()
            f=out/f"oisst_{y}.nc";f.write_bytes(r.content)
            return {"year":y,"url":r.url,"sha256":digest(r.content),"bytes":len(r.content),"path":str(f),"previous_source_attempts":failures}
        except Exception as e: failures.append({"url":url,"error":str(e)[:600]})
    return {"year":y,"error":"transport_failed","attempts":failures}
def validate_year(record):
    y=record["year"]
    with xr.open_dataset(record["path"]) as ds:
        da=ds["ice"]
        if da.attrs.get("units") not in ("1","fraction"): raise ValueError("unverified fraction units "+str(da.attrs))
        if "zlev" in da.dims: da=da.squeeze("zlev",drop=True)
        da=da.transpose("time","latitude","longitude")
        if da.shape!=(184,8,12) or not np.allclose(da.latitude,LATS) or not np.allclose(da.longitude,LONS): raise ValueError("grid or day-count mismatch "+str(da.shape))
        dates=pd.DatetimeIndex(da.time.values).normalize()
        expected=pd.date_range(f"{y}-05-01",f"{y}-10-31")
        if dates.has_duplicates or not dates.equals(expected): raise ValueError("incomplete or unordered daily winter coverage")
        vals=da.values.astype(float)
        if ((vals[np.isfinite(vals)]<0)|(vals[np.isfinite(vals)]>1)).any(): raise ValueError("outside fraction range")
        return vals
def winter(out):
    from concurrent.futures import ThreadPoolExecutor
    # Only network fetches run concurrently; netCDF parsing stays serial.
    with ThreadPoolExecutor(max_workers=3) as pool:
        records=list(pool.map(lambda y:fetch_year(y,out),YEARS))
    arrays={}
    for record in records:
        if "error" in record: continue
        try:
            vals=validate_year(record)
            arrays[record["year"]]=vals
            record["days"]=len(vals)
            record["cells_with_any_data"]=int(np.isfinite(vals).any(axis=0).sum())
            record["cells_with_all_days"]=int(np.isfinite(vals).all(axis=0).sum())
        except Exception as e: record["error"]="validation_failed: "+str(e)
    audit={"transport":"annual_exact_window_chunks","year_receipts":records,"expected_years":YEARS,"validated_years":sorted(arrays)}
    path=out/"winter_source_audit.json"
    path.write_text(json.dumps(audit,indent=2)+"\n")
    if sorted(arrays)!=YEARS: raise ValueError("winter source incomplete: "+str([r["year"] for r in records if "error" in r])+"; see winter_source_audit.json")
    vals=np.concatenate([arrays[y] for y in YEARS],axis=0)
    mask=np.isfinite(vals).any(axis=0)
    audit.update(valid_ocean_cells=int(mask.sum()),grid_cells=int(mask.size),days=len(vals),units="fraction",winter="May–October",partial_cells=int((mask&~np.isfinite(vals).all(axis=0)).sum()))
    path.write_text(json.dumps(audit,indent=2)+"\n")
    if mask.sum()<1 or not np.isfinite(vals[:,mask]).all(): raise ValueError("time-varying missing cell; no imputation; see winter_source_audit.json")
    weights=np.broadcast_to(np.cos(np.deg2rad(LATS))[:,None],mask.shape)[mask]
    annual={y:float(np.average(arrays[y][:,mask],axis=1,weights=weights).mean()) for y in YEARS}
    return annual,audit
def main():
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    report={"status":"D1_BLOCKED","V1_status":"FROZEN_SUPPORT_GATE_BLOCKED","confirmatory_result":False,"numerical_join_executed":False}
    try:
        sr=read(a.source/"seals.zip","Signy_seal_annual_counts_by_area.csv","seals")
        # Official lineage establishes February for the study years; only empty month corrected.
        corrected=[dict(r,Month="FEB") if not r["Month"] and 1997<=int(r["Year"])<=2020 else r for r in sr]
        seals,sa=seal_gate(corrected)
        groups={}
        for sp in ROSTER:
            rr,_,m=source_extract(sp,a.source/(sp.lower()+".zip"))
            by={}
            for r in rr:
                if r["reported_chicks_per_pair"] is not None and r["nest_before_chicks"]:
                    by[r["season_start"],r["colony"]]=r["reported_chicks_per_pair"]
            groups[sp]=by
        if not all(y+1 in seals and all((y,k) in groups[sp] for sp,ks in ROSTER.items() for k in ks) for y in YEARS): raise ValueError("frozen year or roster not supported")
        report["structural_years"]=YEARS; report["fixed_roster"]=ROSTER
        ice,meta=winter(a.out);report["daily_source"]=meta
        panel=pd.DataFrame([dict(season_start=y,fur_seals_feb=seals[y+1],winter_sic=ice[y],**{sp.lower():statistics.median(groups[sp][y,k] for k in ROSTER[sp]) for sp in ROSTER}) for y in YEARS])
        panel.to_csv(a.out/"descriptive_panel.csv",index=False)
        years=panel.season_start.to_numpy();x=np.column_stack([np.ones(len(panel)),z(np.log1p(panel.fur_seals_feb)),z(panel.winter_sic),years-years.mean()])
        y=(panel.chinstrap-panel.gentoo).to_numpy();blocks=(years-1996)//4
        report.update(status="D1_DESCRIPTIVE_ONLY",numerical_join_executed=True,n=len(panel),panel_sha256=digest((a.out/"descriptive_panel.csv").read_bytes()),contrast=fit(y,x,years),leave_block_out=[fit(y[blocks!=b],x[blocks!=b],years[blocks!=b])["beta"] for b in sorted(set(blocks))],species_slopes={sp:fit(panel[sp].to_numpy(),x,years) for sp in ("chinstrap","gentoo","adelie")})
    except Exception as e: report["blocker"]=str(e)
    (a.out/"descriptive_receipt.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report))
if __name__=="__main__":main()
