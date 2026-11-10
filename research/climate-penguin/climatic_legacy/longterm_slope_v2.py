#!/usr/bin/env python3
"""Frozen, post-hypothesis-generation site-slope association versus two SIC eras (v2)."""
from __future__ import annotations
from collections import Counter,defaultdict
from pathlib import Path
import csv,hashlib,json,calendar,math
import numpy as np

HERE=Path(__file__).parent
ROOT=HERE.parent
SOURCE=HERE/"source_extract_outputs"
OUT=HERE/"longterm_v2_outputs"
OUT.mkdir(exist_ok=True)
PINS={
 "counts":("outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv","fc134e364cf38699fa7611d7dee5fbbbcb370c0a"),
 "cohort":("outputs/warming_species_breeding_v1/historical_species_site_trends.csv","2b6c0793ea9f9ea9acf0771052cf7a2ad9ab335b"),
 "old_ice":("outputs/climate_penguin/macro_monthly_seaice_1991_2020.csv","4fcea71c2d8b1069b6ad143f6522061ed434daf5"),
 "coords":("outputs/sic_spatial_coherence_macro40_v1/macro40_site_coordinates.csv","5a211a0eaa63b6a5d3516353dd9431428618dbd3")
}
CLIMATE=("history","recent","equal","delta")
MODELS=("zero","global","region","history","recent","both","equal","delta")
SEED=20261108
def readcsv(path):
    with path.open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
def writecsv(path,items):
    if not items:return
    with path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,list(items[0]));w.writeheader();w.writerows(items)
def pin(name):
    rel,sha=PINS[name];p=ROOT/rel;b=p.read_bytes()
    observed=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if observed!=sha:raise ValueError(f"source blob modified: {rel} {observed}")
    return p
def numeric(v):
    if v is None or v=="":return None
    z=float(v);return z if np.isfinite(z) else None
def pearson(a,b):
    if len(a)<3 or np.std(a)<1e-10 or np.std(b)<1e-10:return None
    return float(np.corrcoef(a,b)[0,1])
def region_residual(x,regions):
    names=sorted(set(regions))
    A=np.column_stack([np.ones(len(regions))]+
                      [np.asarray([float(r==name) for r in regions]) for name in names[1:]])
    return np.asarray(x)-A@np.linalg.lstsq(A,np.asarray(x),rcond=None)[0]
def annual_ice():
    original=readcsv(pin("old_ice"))
    historical=readcsv(SOURCE/"historical_1979_1990_macro40_monthly.csv")
    qc=json.loads((SOURCE/"source_quality.json").read_text())
    if qc["status"]!="SOURCE_QC_PASS" or qc["unsupported_historical_site_months"]!=0:
        raise ValueError("previously frozen source gate failed")
    if len(original)!=9600 or len(historical)!=1920:raise ValueError("wrong source support")
    data={}
    for row in original:
        if int(row["inner_km"])!=0:continue
        key=(row["site_id"],int(row["year"]),int(row["month"]))
        if key in data:raise ValueError(f"duplicate source {key}")
        data[key]=numeric(row["sic_mean"]) if row["complete_month"]=="True" else None
    for row in historical:
        key=(row["site_id"],int(row["year"]),int(row["month"]))
        if key in data:raise ValueError("historical overlap not allowed")
        data[key]=numeric(row["nearshore_sic_pct"]) if row["supported"]=="True" else None
    annual={}
    sites={site for site,y,m in data}
    for site in sites:
        for y in list(range(1979,1991))+list(range(1991,2021)):
            vals=[data.get((site,y,m)) for m in (8,9,10,11)]
            if any(v is None for v in vals):annual[(site,y)]=None
            else:
                weights=np.array([calendar.monthrange(y,m)[1] for m in (8,9,10,11)],float)
                annual[(site,y)]=float(np.average(vals,weights=weights))
    return annual,qc
def era(annual,site,start,end):
    a=[annual.get((site,y)) for y in range(start,end+1)]
    if any(v is None for v in a) or len(a)!=end-start+1:return None
    return float(np.mean(a))
def build(annual):
    roster=readcsv(pin("cohort"));source=readcsv(pin("counts"))
    coords=readcsv(pin("coords"))
    coord={r["site_id"]:r for r in coords}
    cohort={r["site_id"]:r for r in roster if r["species_id"]=="ADPE"}
    if len(cohort)!=39:raise ValueError("original 39-site cohort has drifted")
    bysite=defaultdict(list)
    for x in source:
        if x["species_id"]!="ADPE" or x["site_id"] not in cohort:continue
        if not 2001<=int(x["season"])<=2020:continue
        if x["method"]!=cohort[x["site_id"]]["method"] or x["n_methods"]!="1" or int(x["n_counts"])<1:continue
        if x["count"]=="":continue
        bysite[x["site_id"]].append(x)
    support=[];data=[]
    for site,meta in sorted(cohort.items()):
        r=sorted(bysite[site],key=lambda x:int(x["season"]))
        yrs=[int(x["season"]) for x in r]
        if len(yrs)!=len(set(yrs)):raise ValueError("duplicate site/species/method/season")
        supported=len(yrs)>=4 and (max(yrs)-min(yrs)>=10 if yrs else False)
        support.append({"site_id":site,"region":meta["region"],"method":meta["method"],
            "n_censuses":len(yrs),"first_year":min(yrs) if yrs else "",
            "last_year":max(yrs) if yrs else "",
            "count_span":max(yrs)-min(yrs) if yrs else 0,
            "supported":supported})
        if not supported:continue
        vals=[numeric(x["count"]) for x in r]
        if any(v is None or v<0 for v in vals):raise ValueError("invalid original nest count")
        yy=np.log1p(vals)
        yr=np.asarray(yrs,float)
        slope=float(np.dot(yr-yr.mean(),yy-yy.mean())/np.dot(yr-yr.mean(),yr-yr.mean())*10)
        # independent slope arithmetic check by numpy.polyfit
        if not math.isclose(slope,float(np.polyfit(yr,yy,1)[0])*10,abs_tol=1e-8,rel_tol=1e-8):
            raise ValueError("site trend independent arithmetic mismatch")
        v={"site_id":site,"region":meta["region"],"method":meta["method"],
           "n_censuses":len(yrs),"first_year":min(yrs),"last_year":max(yrs),
           "count_span":max(yrs)-min(yrs),"slope_log1p_per_decade":slope,
           "history":era(annual,site,1979,1990),"recent":era(annual,site,2001,2020),
           "equal":era(annual,site,2009,2020)}
        if any(v[k] is None for k in ["history","recent","equal"]):raise ValueError(f"missing SIC for fixed supported site {site}")
        v["delta"]=v["recent"]-v["history"]
        v["latitude"]=float(coord[site]["latitude"])
        v["longitude"]=float(coord[site]["longitude"])
        data.append(v)
    writecsv(OUT/"source_only_support.csv",support)
    if len(data)!=26 or sum(x["n_censuses"] for x in data)!=257:
        raise ValueError("source-only pre-frozen 26-site/257-year count support changed")
    regions=Counter(x["region"] for x in data)
    if len(data)<25 or len(regions)<3 or sum(v>=3 for v in regions.values())<3:
        raise ValueError("frozen support gate failed")
    return data,support,dict(regions)

def predict(train,x,model,regions):
    if model=="zero":return 0.
    if model=="global":return float(np.mean([q["slope_log1p_per_decade"] for q in train]))
    bases=[1.]+[float(x["region"]==r) for r in regions]
    terms={"region":[],"history":["history"],"recent":["recent"],
           "both":["history","recent"],"equal":["equal"],"delta":["delta"]}[model]
    means={key:np.mean([z[key] for z in train]) for key in terms}
    sds={key:np.std([z[key] for z in train]) for key in terms}
    for key in sds:
        if sds[key]<1e-10:sds[key]=1.
    def vector(z):
        return [1.]+[float(z["region"]==r) for r in regions]+[(z[k]-means[k])/sds[k] for k in terms]
    X=np.asarray([vector(z) for z in train],float)
    target=np.asarray([z["slope_log1p_per_decade"] for z in train],float)
    ridge=np.diag([0]+[4]*len(regions)+[8]*len(terms))
    beta=np.linalg.solve(X.T@X+ridge,X.T@target)
    return float(np.dot(vector(x),beta))

def metrics(rows,by="site"):
    if not rows:return None
    out={}
    for model in MODELS:
        err=np.array([r["observed"]-r["pred_"+model] for r in rows],float)
        out[model]={"mae":float(np.mean(abs(err))),
          "rmse":float(np.sqrt(np.mean(err**2))),
          "bias":float(np.mean(err))}
    return out
def correlations(data):
    reg=[r["region"] for r in data];sl=[r["slope_log1p_per_decade"] for r in data]
    o={"H_C_r":pearson([r["history"] for r in data],[r["recent"] for r in data]),
       "H_C_region_residual_r":pearson(region_residual([r["history"] for r in data],reg),
                                         region_residual([r["recent"] for r in data],reg))}
    for k in CLIMATE:
        x=[r[k] for r in data]
        o["slope_"+k+"_r"]=pearson(sl,x)
        o["slope_"+k+"_region_residual_r"]=pearson(region_residual(sl,reg),region_residual(x,reg))
    return o
def bootstrap_geo(preds):
    rng=np.random.default_rng(SEED)
    reg=sorted(set(x["region"] for x in preds))
    diffs=np.asarray([abs(r["observed"]-r["pred_recent"])-abs(r["observed"]-r["pred_history"]) for r in preds])
    grp=np.asarray([x["region"] for x in preds])
    draws=[]
    for _ in range(2000):
        a=Counter(rng.choice(reg,len(reg),replace=True))
        weight=np.asarray([a[g] for g in grp],float)
        draws.append(float(np.sum(diffs*weight)/np.sum(weight)))
    return {"paired_recent_minus_historical_LOSO_MAE_region_bootstrap_95":[float(x) for x in np.quantile(draws,[.025,.975])],
            "region_replicates":2000,"seed":SEED,"n_regions":len(reg),
            "warning":"Four geographical region blocks, one singleton and highly shared marine grids: interval is a fragile sensitivity, not a calibrated CI."}
def scored_list(data,regions,outer="site"):
    out=[]
    for obs in data:
        if outer=="site":train=[v for v in data if v["site_id"]!=obs["site_id"]]
        elif outer=="region":train=[v for v in data if v["region"]!=obs["region"]]
        else:raise ValueError("invalid split")
        if not train:raise ValueError("empty train")
        row={"site_id":obs["site_id"],"region":obs["region"],"n_censuses":obs["n_censuses"],
             "first_year":obs["first_year"],"last_year":obs["last_year"],
             "observed":obs["slope_log1p_per_decade"],"n_train":len(train),
             "history":obs["history"],"recent":obs["recent"],"equal":obs["equal"],"delta":obs["delta"]}
        for m in MODELS:row["pred_"+m]=predict(train,obs,m,regions)
        out.append(row)
    return out
def main():
    annual,qc=annual_ice()
    data,support,regions=build(annual)
    names=sorted(regions)
    # outcome validation only after both source and eligibility gates passed
    loso=scored_list(data,names,"site")
    loro=scored_list(data,names,"region")
    base=metrics(loso);geo=metrics(loro)
    byRegion={r:metrics([x for x in loso if x["region"]==r]) for r in names}
    byLORO={r:metrics([x for x in loro if x["region"]==r]) for r in names}
    sub=[x for x in data if x["region"]!="Victoria Land"]
    subFold=scored_list(sub,[r for r in names if r!="Victoria Land"],"site")
    subMetric=metrics(subFold)
    # Equal-region weighting: average the region-specific mean absolute errors, not row-weighted.
    region_equal={m:float(np.mean([byRegion[r][m]["mae"] for r in names])) for m in MODELS}
    cor=correlations(data)
    interval=bootstrap_geo(loso)
    delta_loso=base["recent"]["mae"]-base["history"]["mae"]
    delta_equal=base["equal"]["mae"]-base["history"]["mae"]
    delta_region_equal=region_equal["recent"]-region_equal["history"]
    delta_without_victoria=subMetric["recent"]["mae"]-subMetric["history"]["mae"]
    region_deltas={r:byLORO[r]["recent"]["mae"]-byLORO[r]["history"]["mae"] for r in names}
    collinear=(cor["H_C_region_residual_r"] is not None and abs(cor["H_C_region_residual_r"])>=.95)
    strong=(
      delta_loso>0 and delta_equal>0 and delta_region_equal>0 and delta_without_victoria>0
      and all(v>0 for r,v in region_deltas.items() if regions[r]>=2)
      and all(base["history"]["mae"]<base[k]["mae"] for k in ("zero","global","region","recent"))
      and interval["paired_recent_minus_historical_LOSO_MAE_region_bootstrap_95"][0]>0 and not collinear
    )
    if strong:verdict="BOUNDED_EXPLORATORY_HISTORICAL_PREDICTIVE_ASSOCIATION"
    elif collinear or delta_loso>0 or delta_equal>0 or delta_region_equal>0 or delta_without_victoria>0:
        verdict="WEAK_INCONCLUSIVE_OR_NONIDENTIFIABLE"
    else:verdict="NOT_SUPPORTED"
    result={"status":"COMPLETE_EXPLORATORY_LONGTERM_SITE_SLOPE_TEST_V2",
      "verdict":verdict,
      "design":"FROZEN_LONGTERM_SLOPE_V2_20261108.md (committed before computing new slope associations)",
      "n_sites":len(data),"n_censuses":sum(r["n_censuses"] for r in data),"region_support":regions,
      "time_window":{"slope":"2001–2020 observed same-method census seasons, 4 or more over >=10 years",
        "historical":"1979–1990 (12y)","recent":"2001–2020 (20y)","equal_recent":"2009–2020 (12y)"},
      "spatial_LOSO_metrics":base,"geographic_LORO_metrics":geo,
      "LOSO_by_region":byRegion,"LORO_by_region":byLORO,
      "region_equal_LOSO_MAE":region_equal,
      "victoria_removed_refit_LOSO":subMetric,
      "correlations":cor,"uncertainty":interval,
      "contrasts_mae_positive_favors_historical":{
        "historical_minus_recent_LOSO_gain":delta_loso,
        "historical_minus_equal_recent_LOSO_gain":delta_equal,
        "historical_minus_recent_LOSO_region_equal_gain":delta_region_equal,
        "historical_minus_recent_Victoria_out_refit_gain":delta_without_victoria,
        "LORO_by_heldout_region_gain":region_deltas},
      "near_perfect_region_adjusted_collinearity":bool(collinear),
      "source_status":qc["status"],"source_bridge":qc["overlap_bridge"],
      "source_pins":{k:v[1] for k,v in PINS.items()},
      "interpretation_warnings":[
       "Outcome and long-lag hypothesis arose after prior analyses: not an independent preregistration.",
       "Only 26 sites with strong Victoria Land overrepresentation; climate pixels shared among nearby sites.",
       "Site-level spatial association does not establish site-level delayed climate response or penguin migration rates.",
       "Periods compared are 12y versus 20y; equal-12y sensitivity was fixed beforehand.",
       "Do not reinterpret as 2050/2100 population forecasts or confirmed climate debt."]
    }
    writecsv(OUT/"longterm_site_slope_and_exposures.csv",data)
    writecsv(OUT/"site_out_predictions.csv",loso)
    writecsv(OUT/"region_out_predictions.csv",loro)
    (OUT/"longterm_metrics.json").write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print("LONGTERM_V2_RESULT="+json.dumps({
      "verdict":verdict,"n_sites":len(data),"n_censuses":result["n_censuses"],"regions":regions,
      "LOSO_MAE":{k:v["mae"] for k,v in base.items()},
      "LORO_MAE":{k:v["mae"] for k,v in geo.items()},
      "LOSO_region_equal_MAE":region_equal,
      "LOSO_no_victoria_MAE":{k:v["mae"] for k,v in subMetric.items()},
      "correlations":cor,
      "contrasts":result["contrasts_mae_positive_favors_historical"],
      "bootstrap_CI":interval["paired_recent_minus_historical_LOSO_MAE_region_bootstrap_95"]
    },ensure_ascii=False),flush=True)
if __name__=="__main__":main()
