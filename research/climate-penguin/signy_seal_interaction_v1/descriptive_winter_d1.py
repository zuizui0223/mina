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
QUERY="ice[(1996-05-01T12:00:00Z):1:(2019-10-31T12:00:00Z)][(0.0)][(-61.875):1:(-60.125)][(-46.875):1:(-44.125)]"
HOSTS=["https://upwell.pfeg.noaa.gov","https://coastwatch.pfeg.noaa.gov"]
def winter(out):
    failures=[]
    for host in HOSTS:
        url=host+"/erddap/griddap/ncdcOisst21Agg_LonPM180.nc?"+QUERY
        try:
            r=requests.get(url,timeout=(20,180));r.raise_for_status()
            f=out/"noaa_oisst_daily.nc";f.write_bytes(r.content)
            with xr.open_dataset(f) as ds:
                da=ds["ice"]
                if da.attrs.get("units") not in ("1","fraction"): raise ValueError("unverified fraction units "+str(da.attrs))
                if "zlev" in da.dims: da=da.squeeze("zlev",drop=True)
                da=da.transpose("time","latitude","longitude")
                if not np.allclose(da.latitude,np.arange(-61.875,-60,0.25)) or not np.allclose(da.longitude,np.arange(-46.875,-44,0.25)): raise ValueError("grid mismatch")
                dates=pd.DatetimeIndex(da.time.values).normalize()
                if dates.has_duplicates: raise ValueError("duplicate days")
                ix=np.isin(dates.year,YEARS)&np.isin(dates.month,[5,6,7,8,9,10])
                selected=dates[ix]; expected=pd.DatetimeIndex([d for y in YEARS for d in pd.date_range(f"{y}-05-01",f"{y}-10-31")])
                if not selected.equals(expected): raise ValueError("incomplete or unordered daily winter coverage")
                vals=da.values[ix].astype(float); mask=np.isfinite(vals).any(axis=0)
                if mask.sum()<1 or not np.isfinite(vals[:,mask]).all(): raise ValueError("time-varying missing cell; no imputation")
                if ((vals[:,mask]<0)|(vals[:,mask]>1)).any(): raise ValueError("outside fraction range")
                weights=np.broadcast_to(np.cos(np.deg2rad(da.latitude.values))[:,None],mask.shape)[mask]
                daily=np.average(vals[:,mask],axis=1,weights=weights)
                annual={int(y):float(daily[selected.year==y].mean()) for y in YEARS}
                meta={"url":url,"sha256":digest(r.content),"valid_ocean_cells":int(mask.sum()),"grid_cells":int(mask.size),"days":len(selected),"units":"fraction","winter":"May–October", "previous_source_attempts":failures}
                return annual,meta
        except Exception as e: failures.append({"url":url,"error":str(e)[:1500]})
    raise ValueError(json.dumps(failures))
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
