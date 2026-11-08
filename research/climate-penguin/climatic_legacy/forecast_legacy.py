#!/usr/bin/env python3
"""Frozen chronological Adélie SIC 11–20y vs 1–10y forecast; no future biological projection."""
from __future__ import annotations
from collections import Counter, defaultdict
import calendar,csv,hashlib,json,math
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
HERE=Path(__file__).parent
SOURCE=HERE/"source_extract_outputs"
OUT=HERE/"prediction_outputs"
OUT.mkdir(exist_ok=True)
COUNT_PATH=ROOT/"outputs/long_count_seaice_v1/intervals.csv"
OLD_PATH=ROOT/"outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv"
NEW_PATH=SOURCE/"historical_1979_1990_macro40_monthly.csv"
PIN={
 str(COUNT_PATH.relative_to(ROOT)):"6d5982d6f241879de9a2da0232f0f05ec227d3a7",
 str(OLD_PATH.relative_to(ROOT)):"4fcea71c2d8b1069b6ad143f6522061ed434daf5"
}
MODELS=("zero","base","recent","legacy","both","recruit")
Q_SEED=20261108

def readcsv(p):
    with p.open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def writecsv(p,rows):
    if not rows:return
    with p.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def check_pin(path):
    b=path.read_bytes()
    sha=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    expected=PIN[str(path.relative_to(ROOT))]
    if sha!=expected:raise ValueError(f"source drift {path}: {sha}")
def finite(x):
    try:
        v=float(x)
        return v if math.isfinite(v) else None
    except (ValueError,TypeError):return None
def mean(xs):
    return float(sum(xs)/len(xs)) if xs else None
def make_ice():
    source=json.loads((SOURCE/"source_quality.json").read_text())
    if source["status"]!="SOURCE_QC_PASS":
        raise ValueError("source bridge QC did not pass; no biological score is permitted")
    check_pin(OLD_PATH)
    old=readcsv(OLD_PATH)
    monthly={}
    for r in old:
        if int(r["inner_km"])!=0:continue
        key=(r["site_id"],int(r["year"]),int(r["month"]))
        if key in monthly:raise ValueError("duplicate original monthly source")
        v=finite(r["sic_mean"]) if r["complete_month"]=="True" else None
        monthly[key]=v
    new=readcsv(NEW_PATH)
    assert len(new)==40*12*4
    for r in new:
        key=(r["site_id"],int(r["year"]),int(r["month"]))
        if key in monthly:raise ValueError("source extension overlaps archived daily")
        monthly[key]=finite(r["nearshore_sic_pct"]) if r["supported"]=="True" else None
    annual={}
    for site,y,m in monthly:
        if m!=8:continue
        vals=[monthly.get((site,y,k)) for k in (8,9,10,11)]
        annual[(site,y)]=(sum(v*calendar.monthrange(y,m0)[1] for v,m0 in zip(vals,(8,9,10,11)))/
                        sum(calendar.monthrange(y,m0)[1] for m0 in (8,9,10,11))) if all(v is not None for v in vals) else None
    return monthly,annual,source
def climate(annual,site,start,end):
    vals=[annual.get((site,y)) for y in range(start,end+1)]
    return mean(vals) if len(vals)==end-start+1 and all(x is not None for x in vals) else None
def cohort(annual):
    check_pin(COUNT_PATH)
    raw=readcsv(COUNT_PATH)
    if len(raw)!=301:raise ValueError("301-count source drift")
    rows=[]
    for x in raw:
        if not (x["species_id"]=="ADPE" and x["same_known_method"]=="True" and
                x["transition"]=="positive_positive" and int(x["gap"])==1):
            raise ValueError("frozen 301 interval cohort changed")
        t=int(x["start"]);site=x["site_id"];n0=finite(x["n_start"]);n1=finite(x["n_end"])
        if n0 is None or n1 is None or min(n0,n1)<=0:raise ValueError("nonpositive source count")
        y=math.log(n1/n0)
        if not math.isclose(y,float(x["log_growth"]),rel_tol=1e-9,abs_tol=1e-9):
            raise ValueError("source log ratio mismatch")
        d={"site_id":site,"region":x["region"],"start":t,"end":t+1,"y":y,
           "months_known_after_september":x["both_all_after_september"]=="True",
           "recent":climate(annual,site,t-10,t-1),
           "legacy":climate(annual,site,t-20,t-11),
           "recruit":climate(annual,site,t-7,t-3)}
        d["complete"]=all(d[k] is not None for k in ("recent","legacy","recruit"))
        rows.append(d)
    if len({x["site_id"] for x in rows})!=33:raise ValueError("original sites changed")
    records=[r for r in rows if r["start"]>=1999 and r["complete"]]
    if records:
        nsites=len(set(r["site_id"] for r in records))
        nreg=len(set(r["region"] for r in records))
        supported=(len(records)>=150 and nsites>=20 and nreg>=4)
    else:supported=False
    return rows,records,supported
def site_scale(train,features):
    mu={};sd={}
    sites={r["site_id"] for r in train}
    for name in features:
        for site in sites:
            v=[r[name] for r in train if r["site_id"]==site]
            mu[(name,site)]=float(np.mean(v))
        an=np.array([r[name]-mu[(name,r["site_id"])] for r in train])
        sd[name]=float(np.std(an))
        if sd[name]<1e-10:sd[name]=1.0
    return mu,sd
def fit_predict(train,test,model):
    if model=="zero":return 0.
    features={
        "base":(),"recent":("recent",),"legacy":("legacy",),
        "both":("recent","legacy"),"recruit":("recruit",)
    }[model]
    sites=sorted(set(x["site_id"] for x in train))
    if test["site_id"] not in sites:raise ValueError("test site unseen")
    site_rest=sites[1:]
    mu,scale=site_scale(train,features)
    def vector(r):
        out=[1.0]
        out.extend(float(r["site_id"]==site) for site in site_rest)
        out.append((r["start"]-2000)/10)
        out.extend((r[f]-mu[(f,r["site_id"])])/scale[f] for f in features)
        return out
    X=np.array([vector(r) for r in train])
    b=np.array([r["y"] for r in train])
    penalty=np.array([0]+[3]*len(site_rest)+[3]+[8]*len(features))
    lhs=X.T@X+np.diag(penalty)
    w=np.linalg.solve(lhs,X.T@b)
    return float(np.array(vector(test))@w)
def metric(pred,model,part=None,weight="pooled"):
    if part is None:part=pred
    if not part:return None
    by=defaultdict(list)
    for x in part:
        err=abs(x["y"]-x["pred_"+model])
        by[x["start"] if weight=="year" else x["site_id"] if weight=="site" else "all"].append(err)
    return float(np.mean([np.mean(v) for v in by.values()]))
def metric_full(pred):
    groups={"pooled":pred,"without_Victoria_Land":[x for x in pred if x["region"]!="Victoria Land"],
            "timing_after_september":[x for x in pred if x["months_known_after_september"]],
            "terminal_2014_2018":[x for x in pred if x["start"]>=2014],
            "initial_training_sites":[x for x in pred if x["site_id"] in set(r["site_id"] for r in pred if r["start"]==2006)]}
    return {g:{"n":len(sub),"sites":len(set(x["site_id"] for x in sub)),
       "by_model":{m:{k:metric(pred,m,sub,weight=k) for k in ("pooled","year","site")} for m in MODELS}}
       for g,sub in groups.items()}
def corr(x,y):
    x=np.asarray(x);y=np.asarray(y)
    if len(x)<3 or np.std(x)<1e-9 or np.std(y)<1e-9:return None
    return float(np.corrcoef(x,y)[0,1])
def climate_collinearity(rows):
    sites=sorted(set(x["site_id"] for x in rows));ss=sites[1:]
    Z=np.array([[1]+[float(x["site_id"]==s) for s in ss]+[(x["start"]-2000)/10] for x in rows])
    X=np.array([x["recent"] for x in rows]);Y=np.array([x["legacy"] for x in rows])
    rx=X-Z@np.linalg.lstsq(Z,X,rcond=None)[0]
    ry=Y-Z@np.linalg.lstsq(Z,Y,rcond=None)[0]
    return {"raw_recent_legacy_r":corr(X,Y),"site_time_residual_r":corr(rx,ry)}
def bootstrap_delta(pred):
    rng=np.random.default_rng(Q_SEED)
    years=sorted(set(x["start"] for x in pred))
    sites=sorted(set(x["site_id"] for x in pred))
    y=np.array([x["start"] for x in pred]);s=np.array([x["site_id"] for x in pred])
    d=np.array([abs(x["y"]-x["pred_recent"])-abs(x["y"]-x["pred_legacy"]) for x in pred])
    vals=[]
    for _ in range(2000):
        yy=Counter(rng.choice(years,size=len(years),replace=True))
        ss=Counter(rng.choice(sites,size=len(sites),replace=True))
        w=np.array([yy[int(a)]*ss[str(b)] for a,b in zip(y,s)],dtype=float)
        if sum(w)>0:vals.append(float(np.sum(d*w)/np.sum(w)))
    return {"two_way_site_year_bootstrap_pooled_difference_ci95":
            [float(np.quantile(vals,.025)),float(np.quantile(vals,.975))] if len(vals)>500 else None,
            "replicates_valid":len(vals),"replicates_target":2000,"seed":Q_SEED,
            "caution":"Approximate due to shared climate pixels and only four test regions; not independent climate trials."}
def main():
    monthly,annual,source=make_ice()
    all_rows,rows,support=cohort(annual)
    coverage={
      "original_intervals":len(all_rows),"original_sites":len(set(r["site_id"] for r in all_rows)),
      "eligible_t_1999_2018":len(rows),
      "eligible_sites":len(set(r["site_id"] for r in rows)),
      "eligible_regions":len(set(r["region"] for r in rows)),
      "missing_annual_sic_1979_2020":sum(v is None for v in annual.values()),
      "cohort_source_blob":PIN[str(COUNT_PATH.relative_to(ROOT))],
      "regions":dict(Counter(r["region"] for r in rows))}
    support_csv=[]
    for r in all_rows:
        support_csv.append({k:(v if v is not None else "") for k,v in r.items()})
    writecsv(OUT/"full_support_and_exposures.csv",support_csv)
    preds=[]
    if support:
        for t in range(2006,2019):
            train=[r for r in rows if r["start"]<t]
            known={r["site_id"] for r in train}
            tests=[r for r in rows if r["start"]==t and r["site_id"] in known]
            for x in tests:
                out={k:v for k,v in x.items() if k!="complete"}
                out["training_n"]=len(train)
                for model in MODELS:out["pred_"+model]=fit_predict(train,x,model)
                preds.append(out)
    coverage.update({"rolling_test_n":len(preds),
      "rolling_test_sites":len(set(r["site_id"] for r in preds)),
      "rolling_test_regions":len(set(r["region"] for r in preds)),
      "rolling_test_years":len(set(r["start"] for r in preds))})
    can_score=(support and len(preds)>=80 and coverage["rolling_test_sites"]>=10 and
               coverage["rolling_test_regions"]>=3 and coverage["rolling_test_years"]>=10)
    if not can_score:
        payload={"status":"NOT_TESTABLE_SUPPORT_GATE","coverage":coverage,"source_status":source["status"],
                 "reason":"Pre-frozen sample support minima not met","outcome_test_run":False}
        (OUT/"metrics.json").write_text(json.dumps(payload,indent=2)+"\n")
        print("LEGACY_RESULT="+json.dumps(payload),flush=True)
        raise SystemExit(3)
    writecsv(OUT/"rolling_chronological_predictions.csv",preds)
    metrics=metric_full(preds)
    boots=bootstrap_delta(preds)
    col=climate_collinearity(rows)
    m=metrics["pooled"]["by_model"]
    diffs={k:float(m["recent"][k]-m["legacy"][k]) for k in ["pooled","year","site"]}
    region_out=metrics["without_Victoria_Land"]["by_model"]
    reg_delta=(region_out["recent"]["pooled"]-region_out["legacy"]["pooled"]
               if region_out["recent"]["pooled"] is not None else None)
    better=lambda w: all(m["legacy"][w]<m[k][w] for k in ("zero","base","recent"))
    sign_positive=(diffs["pooled"]>0 and better("year") and better("site") and
       reg_delta is not None and reg_delta>0)
    positive_ci=(boots["two_way_site_year_bootstrap_pooled_difference_ci95"] is not None and
             boots["two_way_site_year_bootstrap_pooled_difference_ci95"][0]>0)
    identifiable=(col["site_time_residual_r"] is not None and abs(col["site_time_residual_r"])<=.95)
    if sign_positive and positive_ci and identifiable:verdict="LEGACY_OUT_OF_TIME_PREDICTION_SUPPORTED_BOUNDED"
    elif diffs["pooled"]>0 or diffs["year"]>0 or diffs["site"]>0:verdict="WEAK_OR_INCONCLUSIVE"
    else:verdict="LEGACY_PREDICTION_NOT_SUPPORTED"
    payload={"status":"COMPLETE_EXPLORATORY_FROZEN_LONG_LAG_COMPARISON",
      "verdict":verdict,"counts":coverage,
      "model_mae":metrics,"delta_recent_minus_legacy_positive_favors_legacy":diffs,
      "long_legacy_minus_recent_both_model_improvement":{
         k:m["recent"][k]-m["both"][k] for k in ("pooled","year","site")},
      "model_collinearity":col,"bootstrap":boots,"source_status":source["status"],
      "source_comparability":source["overlap_bridge"],
      "notes":["Exploratory overall programme; this specific test frozen before lag exposure scores were generated.",
               "Retrospective source-census chronology; climate influence and geographic redistribution remain unidentified.",
               "Positive-to-positive same-method count changes cannot estimate colony extinction or breeding dispersal.",
               "Same products but original 1991–2020 daily-based series joined to official 1979–1990 monthly series; source bridge QC is finite, not proof of exact equivalence.",
               "Never interpret long historical exposure prediction as 2050/2100 nest count forecast."]}
    (OUT/"metrics.json").write_text(json.dumps(payload,indent=2)+"\n")
    # Summarize only predeclared contrasts to action log (full rows in artifact)
    print("LEGACY_RESULT="+json.dumps({"verdict":verdict,"counts":coverage,
      "pooled_mae":{k:v["pooled"] for k,v in m.items()},
      "year_mae":{k:v["year"] for k,v in m.items()},
      "site_mae":{k:v["site"] for k,v in m.items()},
      "deltas":diffs,"without_victoria_delta":reg_delta,"resid_corr":col["site_time_residual_r"],
      "paired_bootstrap_ci95":boots["two_way_site_year_bootstrap_pooled_difference_ci95"]}),flush=True)

if __name__=="__main__":main()
