"""Externally thresholded validation of large breeding-group loss."""
from __future__ import annotations
import argparse, json, math
from collections import defaultdict
from pathlib import Path
import numpy as np
from .lter import ISLANDS, load_colony_rows

THRESHOLD=50.0

def rows(path: str|Path):
    raw=load_colony_rows(path)
    by=defaultdict(list)
    for r in raw: by[(int(r["year"]),str(r["island"]))].append(r)
    state={}
    for key,local in by.items():
        counts=[float(r["breeding_pairs"]) for r in local]
        total=sum(counts)
        large=[x for x in counts if x>THRESHOLD]
        state[key]={
            "total":float(total),
            "large_group_count":len(large),
            "large_group_fraction":float(sum(large)/total) if total>0 else None,
        }
    years=sorted({y for y,_ in state})
    out=[]
    for year in years[:-1]:
        if year+1 not in years: continue
        for island in ISLANDS:
            a=state.get((year,island)); b=state.get((year+1,island))
            if a is None or b is None or a["total"]<=0: continue
            out.append({
                "start_year":year,"end_year":year+1,"island":island,
                "current_total":a["total"],
                "next_growth":math.log1p(b["total"])-math.log1p(a["total"]),
                "large_group_count":a["large_group_count"],
                "large_group_fraction":a["large_group_fraction"],
            })
    return out

def ztrain(a,b):
    m=float(np.mean(a)); s=float(np.std(a,ddof=1))
    if s<=0: raise ValueError("zero predictor variance")
    return (a-m)/s,(b-m)/s

def island_matrix(vals,levels):
    look={v:i for i,v in enumerate(levels)}
    x=np.zeros((len(vals),len(levels)))
    for j,v in enumerate(vals): x[j,look[v]]=1
    return x

def pred(row,kind):
    if kind=="count": return math.log1p(float(row["large_group_count"]))
    if kind=="fraction": return float(row["large_group_fraction"])
    raise ValueError(kind)

def design(train,test,full,kind):
    levels=tuple(i for i in ISLANDS if i in {str(r["island"]) for r in train})
    xtr=island_matrix([str(r["island"]) for r in train],levels)
    xte=island_matrix([str(r["island"]) for r in test],levels)
    for getter in (
        lambda r: math.log1p(float(r["current_total"])),
        lambda r: float(r["start_year"]),
    ):
        a=np.asarray([getter(r) for r in train]); b=np.asarray([getter(r) for r in test])
        za,zb=ztrain(a,b); xtr=np.column_stack([xtr,za]); xte=np.column_stack([xte,zb])
    if full:
        a=np.asarray([pred(r,kind) for r in train]); b=np.asarray([pred(r,kind) for r in test])
        za,zb=ztrain(a,b); xtr=np.column_stack([xtr,za]); xte=np.column_stack([xte,zb])
    return xtr,xte

def ols(x,y):
    beta,_,rank,_=np.linalg.lstsq(x,y,rcond=None)
    if rank!=x.shape[1]: raise ValueError("rank deficient large-group model")
    return beta

def loyo(data,kind):
    years=sorted({int(r["end_year"]) for r in data})
    err={"G0":[],"G1":[]}
    for year in years:
        train=[r for r in data if int(r["end_year"])!=year]
        test=[r for r in data if int(r["end_year"])==year]
        ytr=np.asarray([float(r["next_growth"]) for r in train])
        yte=np.asarray([float(r["next_growth"]) for r in test])
        for name,full in (("G0",False),("G1",True)):
            xtr,xte=design(train,test,full,kind)
            e=yte-xte@ols(xtr,ytr)
            err[name].extend((e**2).tolist())
    mse={k:float(np.mean(v)) for k,v in err.items()}
    return {"n_rows":len(data),"n_years":len(years),"mse":mse,"gain_G0_minus_G1":mse["G0"]-mse["G1"]}

def coefficient(data,kind):
    x,_=design(data,data,True,kind)
    y=np.asarray([float(r["next_growth"]) for r in data])
    return float(ols(x,y)[-1])

def analyze(path):
    data=rows(path)
    primary=loyo(data,"count"); beta=coefficient(data,"count")
    sens=loyo(data,"fraction"); sbeta=coefficient(data,"fraction")
    return {
        "schema_version":1,
        "analysis_id":"mina-palmer-large-breeding-group-threshold-v1",
        "threshold_pairs":THRESHOLD,
        "primary":{"predictor":"log1p count of groups >50 pairs","loyo":primary,"coefficient":beta,
                   "decision":"supported" if primary["gain_G0_minus_G1"]>0 and beta>0 else "not_supported"},
        "sensitivity_large_group_fraction":{"loyo":sens,"coefficient":sbeta},
        "interpretation_boundary":{"external_threshold_no_search":True,"predictive_not_causal":True}
    }

def main():
    p=argparse.ArgumentParser(); p.add_argument("--census",required=True,type=Path); p.add_argument("--out",required=True,type=Path)
    a=p.parse_args(); x=analyze(a.census); a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n")
    return 0
if __name__=="__main__": raise SystemExit(main())
