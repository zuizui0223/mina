"""D2: direct publisher-derived ice onset proxy; no confirmatory or causal claim."""
import argparse,datetime as dt,json,statistics
from pathlib import Path
import numpy as np
import pandas as pd
from prepare_panel import read,num,seal_gate,source_extract,digest,PINS
from analyze import z,fit
from descriptive_winter_d1 import YEARS,ROSTER

def onset(row,y):
    v=num(row["advance [a]"])
    if v is None or v%1: raise ValueError(f"invalid onset in {y}")
    if v==0:
        if any(num(row[k])!=0 for k in ("retreat [b]","ice_days [c]","persistence [d]")):
            raise ValueError(f"ambiguous no-event code {y}")
        return 0
    if not 46<=v<=411: raise ValueError(f"onset outside source sea-ice year {y}")
    cutoff=(dt.date(y,10,31)-dt.date(y,1,1)).days
    # First event known after 5 days, never use future timing to vary a censored value.
    return max(0,cutoff-(int(v)+4)+1)

def execute(source,out):
    report={"status":"D2_BLOCKED","V1_status":"FROZEN_SUPPORT_GATE_BLOCKED","D1_status":"D1_BLOCKED","confirmatory_result":False,"numerical_join_executed":False}
    try:
        sr=read(source/"seals.zip","Signy_seal_annual_counts_by_area.csv","seals")
        corrected=[dict(r,Month="FEB") if not r["Month"] and 1997<=int(r["Year"])<=2020 else r for r in sr]
        seals,sa=seal_gate(corrected)
        ir=read(source/"ice.zip","Signy_sea_ice_variables.csv","ice")
        iy={int(r["Year"]):r for r in ir}
        if len(iy)!=len(ir): raise ValueError("duplicate ice year")
        groups={}; meta={}
        for sp in ROSTER:
            rr,_,m=source_extract(sp,source/(sp.lower()+".zip"))
            meta[sp]=m
            groups[sp]={(r["season_start"],r["colony"]):r for r in rr if r["reported_chicks_per_pair"] is not None and r["nest_before_chicks"]}
        if not all(y+1 in seals and y in iy and all((y,k) in groups[sp] for sp,ks in ROSTER.items() for k in ks) for y in YEARS): raise ValueError("frozen year/roster incomplete")
        ice={y:onset(iy[y],y) for y in YEARS}
        timing={str(y):min(groups[sp][y,k]["chick_count_date"] for sp,ks in ROSTER.items() for k in ks) for y in YEARS}
        if any(dt.date.fromisoformat(t)<=dt.date(int(y),10,31) for y,t in timing.items()): raise ValueError("cutoff not before chick endpoints")
        report.update(structural_years=YEARS,fixed_roster=ROSTER,earliest_chick_date=timing,
            ice_source_sha256=PINS["ice"],seal_source_sha256=PINS["seals"],penguin_sources=meta,ice_proxy="elapsed days from confirmation of first sustained advance to Oct31, not actual ice duration")
        panel=pd.DataFrame([dict(season_start=y,fur_seals_feb=seals[y+1],ice_onset_proxy_days=ice[y],**{sp.lower():statistics.median(groups[sp][y,k]["reported_chicks_per_pair"] for k in ROSTER[sp]) for sp in ROSTER}) for y in YEARS])
        if not np.isfinite(panel.to_numpy()).all(): raise ValueError("nonfinite panel")
        years=panel.season_start.to_numpy()
        x=np.column_stack([np.ones(len(panel)),z(np.log1p(panel.fur_seals_feb)),z(panel.ice_onset_proxy_days),years-years.mean()])
        yy=(panel.chinstrap-panel.gentoo).to_numpy();blocks=(years-1996)//4
        result=fit(yy,x,years)
        loo=[fit(yy[blocks!=b],x[blocks!=b],years[blocks!=b])["beta"] for b in sorted(set(blocks))]
        slopes={sp:fit(panel[sp].to_numpy(),x,years) for sp in ("chinstrap","gentoo","adelie")}
        dest=out/"onset_panel.csv";panel.to_csv(dest,index=False)
        report.update(status="D2_DESCRIPTIVE_ONLY",numerical_join_executed=True,n=len(panel),panel_sha256=digest(dest.read_bytes()),contrast=result,leave_block_out=loo,species_slopes=slopes)
    except Exception as e: report["blocker"]=str(e)
    (out/"onset_receipt.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k not in ("penguin_sources","earliest_chick_date")}))
def selftest():
    r={"advance [a]":"100","retreat [b]":"330","ice_days [c]":"180","persistence [d]":"90"}
    assert onset(r,1999)==200
    assert onset(dict(r,**{"advance [a]":"304"}),1999)==0
    assert onset({k:"0" for k in r},1999)==0
    try: onset(dict(r,**{"advance [a]":""}),1999)
    except ValueError: pass
    else: raise AssertionError("missing onset accepted")
def main():
    p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True);p.add_argument("--out",type=Path,required=True)
    a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);selftest();execute(a.source,a.out)
if __name__=="__main__":main()
