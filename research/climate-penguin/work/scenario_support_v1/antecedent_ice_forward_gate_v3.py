"""One- and three-year antecedent sea-ice nests hindcast, exploratory v3.

Compare within-site climate anomalies to raw marine exposure, with only source
years before the nest-count interval used for predictors. Model fit uses earlier
observed annual count changes only; site climatologies use training years only.
The frozen source files are never overwritten. Python standard library only.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ICE = ROOT/"research/climate-penguin/outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv"
COUNTS = ROOT/"research/climate-penguin/outputs/long_count_seaice_v1/intervals.csv"
OUT = ROOT/"research/climate-penguin/outputs/antecedent_ice_forward_gate_v3"
EXPECTED = OUT/"expected_receipt.json"
TEST_YEARS = tuple(range(2005, 2019))
SPECS = {
    "site": ((), False),
    "lag1_raw": (("lag1",), False),
    "lag3_raw": (("lag3",), False),
    "lag1_within": (("lag1",), True),
    "lag3_within": (("lag3",), True),
    "lag3_within_sd": (("lag3","lag3sd"), True),
    "sept_within": (("sept",), True)
}


def load(ice_path=ICE, count_path=COUNTS):
    with open(ice_path, newline="", encoding="utf-8") as f:
        ice = list(csv.DictReader(f))
    series = {}
    for x in ice:
        if x["inner_km"] != "0":
            continue
        month = int(x["month"])
        if month not in (8,9,10,11):
            continue
        key = (x["site_id"], int(x["year"]))
        d = series.setdefault(key, {})
        if month in d:
            raise ValueError("duplicate site/year/month")
        days = int(x["days"])
        if (x["complete_month"] != "True" or int(x["supported_days"]) != days
            or int(x["expected_days"]) != days or not math.isfinite(float(x["sic_mean"]))):
            raise ValueError("incomplete or nonfinite sea-ice observation")
        d[month] = (float(x["sic_mean"]), days)
    yr = {}
    for key, months in series.items():
        if set(months) != {8,9,10,11}:
            raise ValueError("partial four-month sea-ice year")
        yr[key] = sum(v*d for v,d in months.values())/sum(d for v,d in months.values())

    with open(count_path, newline="", encoding="utf-8") as f:
        census = list(csv.DictReader(f))
    out = []
    for x in census:
        if x["species_id"]!="ADPE" or x["same_known_method"]!="True":
            raise ValueError("count source was reselected")
        y = int(x["start"])
        if int(x["gap"])!=1 or int(x["end"])!=y+1:
            raise ValueError("non-annual count interval")
        n0,n1=float(x["n_start"]),float(x["n_end"])
        if n0<=0 or n1<=0:
            raise ValueError("missing or nonpositive count")
        growth=float(x["log_growth"])
        if not math.isclose(growth, math.log(n1/n0),abs_tol=1e-10):
            raise ValueError("nest count ratio not reproducible")
        values=[yr.get((x["site_id"],y-i)) for i in (3,2,1)]
        if not all(v is not None and math.isfinite(v) for v in values):
            continue
        mean=sum(values)/3.0
        out.append({
            "id":x["site_id"],"reg":x["region"],"t":y,
            "y":growth,"timing":x["both_all_after_september"]=="True",
            "lag1":values[2],"lag3":mean,
            "lag3sd":math.sqrt(sum((v-mean)**2 for v in values)/3),
            "sept":float(x["near_start"])
        })
    out.sort(key=lambda a:(a["t"],a["id"]))
    return out,{"raw_ice_records":len(ice),"complete_near_years":len(yr),
                "count_records":len(census)}


def solve(A,b):
    n=len(b); mat=[list(row)+[b[i]] for i,row in enumerate(A)]
    for k in range(n):
        piv=max(range(k,n),key=lambda i:abs(mat[i][k]))
        if abs(mat[piv][k])<1e-13:
            raise ValueError("singular ridge regression")
        mat[piv],mat[k]=mat[k],mat[piv]
        den=mat[k][k]
        for j in range(k,n+1):
            mat[k][j]/=den
        for i in range(n):
            if i==k:
                continue
            val=mat[i][k]
            for j in range(k,n+1):
                mat[i][j]-=val*mat[k][j]
    return [r[n] for r in mat]


def fit(train, variables, within):
    sites=sorted({r["id"] for r in train})
    site_means={}
    scale=[]
    for v in variables:
        site_means[v]={}
        for site in sites:
            vv=[r[v] for r in train if r["id"]==site]
            site_means[v][site]=sum(vv)/len(vv)
        vals=[r[v]-site_means[v][r["id"]] if within else r[v] for r in train]
        mu=sum(vals)/len(vals)
        sd=math.sqrt(sum((a-mu)**2 for a in vals)/len(vals)) or 1.0
        scale.append((v,mu,sd))
    def X(r):
        return ([1.0,(r["t"]-2000.0)/10.0]
                + [float(r["id"]==s) for s in sites]
                + [((r[v]-site_means[v][r["id"]] if within else r[v])-mu)/sd
                   for v,mu,sd in scale])
    n=2+len(sites)+len(variables)
    A=[[0.0]*n for _ in range(n)]
    b=[0.0]*n
    for r in train:
        x=X(r)
        for i in range(n):
            b[i]+=x[i]*r["y"]
            for j in range(n):
                A[i][j]+=x[i]*x[j]
    for i in range(1,n):
        A[i][i]+=3.0 if i<2+len(sites) else 8.0
    beta=solve(A,b)
    return lambda r:sum(x*v for x,v in zip(X(r),beta))


def metrics(records):
    d={"n":len(records),"sites":len({r["id"] for r in records})}
    for k in ("zero",*SPECS):
        d[k+"_mae"]=sum(abs(r[k]-r["y"]) for r in records)/len(records)
    return d


def analyze(rows):
    preds,folds=[],[]
    for t in TEST_YEARS:
        tr=[r for r in rows if r["t"]<t]
        seen={r["id"] for r in tr}
        te=[r for r in rows if r["t"]==t and r["id"] in seen]
        if len(tr)<100 or len(te)<1:
            raise ValueError("training/test opportunity changed")
        models={name:fit(tr,variables,within)
                for name,(variables,within) in SPECS.items()}
        for r in te:
            row={"id":r["id"],"reg":r["reg"],"t":t,
                 "y":r["y"],"timing":r["timing"],"zero":0.0}
            for name,model in models.items():
                row[name]=model(r)
            preds.append(row)
        folds.append({"year":t,"train":len(tr),"test":len(te),
                      "timing":sum(r["timing"] for r in te)})
    group={
        "all":metrics(preds),
        "timing":metrics([r for r in preds if r["timing"]]),
        "nonVic":metrics([r for r in preds if r["reg"]!="Victoria Land"]),
        "timingNonVic":metrics([r for r in preds if r["reg"]!="Victoria Land" and r["timing"]])
    }
    year_equal={}
    for k in ("zero",*SPECS):
        year_equal[k]=sum(
            sum(abs(z[k]-z["y"]) for z in preds if z["t"]==t)
            /sum(z["t"]==t for z in preds)
            for t in TEST_YEARS
        )/len(TEST_YEARS)
    return {"source_usable":len(rows),"groups":group,"year_equal":year_equal,
            "folds":folds,"predictions":preds}


def verify(r,receipt):
    if r["source_usable"]!=receipt["source_usable"]:
        raise ValueError("source support changed")
    if [x["test"] for x in r["folds"]]!=receipt["test_per_year"] or \
       [x["train"] for x in r["folds"]]!=receipt["train_per_year"]:
        raise ValueError("rolling folds changed")
    for label,group in receipt["groups"].items():
        for k,val in group.items():
            observed=r["groups"][label][k]
            if k in ("n","sites"):
                if observed!=val:
                    raise ValueError(f"support mismatch {label}/{k}")
            elif not math.isclose(observed,val,abs_tol=1e-9,rel_tol=1e-9):
                raise ValueError(f"metric mismatch {label}/{k}")
    for k,val in receipt["year_equal"].items():
        if not math.isclose(r["year_equal"][k],val,abs_tol=1e-9,rel_tol=1e-9):
            raise ValueError(f"annual metric mismatch {k}")


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--check-receipt",action="store_true")
    args=ap.parse_args()
    rows,audit=load()
    result=analyze(rows)
    if args.check_receipt:
        verify(result,json.loads(EXPECTED.read_text(encoding="utf-8")))
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/"predictions.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=list(result["predictions"][0]))
        writer.writeheader();writer.writerows(result["predictions"])
    summary={k:v for k,v in result.items() if k!="predictions"}
    summary["source_audit"]=audit
    summary["original_ice_sha256"]=hashlib.sha256(ICE.read_bytes()).hexdigest()
    summary["original_count_sha256"]=hashlib.sha256(COUNTS.read_bytes()).hexdigest()
    summary["interpretation"]="Post-result, historical lag sensitivity; no population forecasts, inferential p-values or causal transfer to CMIP6."
    (OUT/"result.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"n":result["source_usable"],
                      "test":result["groups"]["all"]["n"],
                      "timing":result["groups"]["timing"]["n"],
                      "MAE":result["groups"]["all"],
                      "receipt_checked":bool(args.check_receipt)},ensure_ascii=False))


if __name__=="__main__":
    main()
