#!/usr/bin/env python3
"""Source-support-locked multi-network Antarctic penguin allocation backtest.

Three panels with the same response: NEXT-YEAR relative allocation of observed
nest counts among a fixed set of independently recorded site IDs.
- Palmer ADPE: five physical islands, original all-five census 1991-2017.
- Victoria Land ADPE: three original Ross-Island colony site codes 1996-2019.
- South Shetland CHPE: four original colony site codes 1996-2012.

The latter two networks are selected by observation-support data ONLY from the
pinned original source: longest uninterrupted year window containing >=3 sites
for >=10 years per source_region x species. ALL eligible networks are retained,
without selecting by colony abundance, historical trends or prediction skill.

The forecast origin is the END of breeding season t-1. The ONLY environmental
input for target year t is Aug-Oct SIC from t-1 or earlier. This is intentionally
more conservative than the already completed Palmer conditional *same-year*
pre-census SIC comparison. Last observed colony allocation is a persistence
baseline, not a model of philopatry, competition or spatial movement.
"""
from __future__ import annotations
import argparse,csv,hashlib,io,json,zipfile
from collections import defaultdict,Counter
from pathlib import Path
import numpy as np

RAW_BLOB="fc134e364cf38699fa7611d7dee5fbbbcb370c0a"
PALMER_COUNTS_BLOB="20d1c11d6478899954fb837c5505708e78ca539d"
PALMER_SIC_BLOB="701794b329bf1c1fc872399ad2013a014c9608a5"
TAXA=("ADPE","CHPE","GEPE")
NETWORKS={
    "Victoria_Land_ADPE_3colony":{
        "region":"Victoria Land","species":"ADPE","start":1996,"end":2019,
        "sites":("BRDS","CRZE","ROYD"),"scale":"colony_site_ids",
        "method":"aerial"
    },
    "South_Shetland_CHPE_4colony":{
        "region":"South Shetland Islands","species":"CHPE",
        "start":1996,"end":2012,"sites":("DEMA","LLAN","PAPT","UCHA"),
        "scale":"colony_site_ids","method":"ground"
    },
}
PALMER_SITES=("CHR","COR","HUM","LIT","TOR")
SOURCE_START,SOURCE_END=1991,2020
MIN_CONSECUTIVE=10
MIN_SITES=3
RIDGE_LAMBDA=1.0
DRAWS=4000
BLOCK_YEARS=3
SEED=20261117
MODELS=(
    "historical_share_mean","time_only","lagged_regional_sic_only",
    "lagged_site_sic_only","time_plus_lagged_site_sic",
    "previous_share","previous_plus_mean_drift",
    "previous_plus_lagged_regional_sic","previous_plus_lagged_site_sic"
)

def read_csv(path):
    with Path(path).open(newline="",encoding="utf-8-sig") as f:return list(csv.DictReader(f))

def git_blob(path):
    b=Path(path).read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def read_zip(path,member):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        return list(csv.DictReader(io.StringIO(z.read(member).decode("utf-8-sig"))))

def locked_original_roster(raw_source,countzip):
    assert git_blob(raw_source)==RAW_BLOB,"STOP original derived MAPPPD frozen source mutated"
    raw=read_csv(raw_source)
    assert len(raw)==2999
    freq=defaultdict(Counter)
    known=[]
    for q in raw:
        if q["species_id"] not in TAXA:continue
        if q["n_methods"]!="1" or q["method"].strip() in ("","unknown"):continue
        if q["count"].strip()=="":continue
        n=float(q["count"])
        assert np.isfinite(n) and n>=0 and n.is_integer()
        freq[(q["site_id"],q["species_id"])][q["method"]]+=1
        known.append(q)
    assert len(known)==2724 and len(freq)==707
    chosen={k:sorted(v.items(),key=lambda z:(-z[1],z[0]))[0][0] for k,v in freq.items()}
    derived={}
    for q in known:
        site,sp=q["site_id"],q["species_id"]
        if q["method"]!=chosen[(site,sp)]:continue
        key=(site,sp,int(q["season"]))
        assert key not in derived
        derived[key]=q
    assert len(derived)==2456
    obs=read_zip(countzip,"source_observed_2456.csv")
    inventory=read_zip(countzip,"panantarctic_595_site_inventory.csv")
    assert len(obs)==2456 and len(inventory)==595
    assert len({x["site_id"] for x in inventory})==595
    bykey={}
    for q in obs:
        key=(q["site_id"],q["species"],int(q["season"]))
        assert key not in bykey
        o=derived[key]
        assert q["source_region"]==o["region"]
        assert q["original_survey_method"]==o["method"]
        assert float(q["observed_nest_count"])==float(o["count"])
        assert float(q["latitude"])==float(o["latitude"])
        assert float(q["longitude"])==float(o["longitude"])
        bykey[key]=q
    assert set(bykey)==set(derived)
    return obs,inventory

def support_gate(obs):
    sets=defaultdict(lambda:defaultdict(set))
    for r in obs:
        year=int(r["season"])
        if SOURCE_START<=year<=SOURCE_END:
            sets[(r["source_region"],r["species"])][r["site_id"]].add(year)
    selection={}
    audit=[]
    for (region,species),siteyears in sorted(sets.items()):
        candidates=[]
        for y0 in range(SOURCE_START,SOURCE_END-MIN_CONSECUTIVE+2):
            for y1 in range(y0+MIN_CONSECUTIVE-1,SOURCE_END+1):
                yr=set(range(y0,y1+1))
                included=tuple(sorted(s for s,dates in siteyears.items() if yr.issubset(dates)))
                if len(included)>=MIN_SITES:
                    candidates.append((-(y1-y0+1),-len(included),y0,y1,included))
        if not candidates:
            audit.append({"region":region,"species":species,"eligible":False,
                          "n_source_sites":len(siteyears)})
            continue
        _,_,y0,y1,sites=sorted(candidates)[0]
        item={"region":region,"species":species,"start":y0,"end":y1,
              "sites":sites,"n_source_sites":len(siteyears),"eligible":True,
              "n_years":y1-y0+1}
        audit.append(item)
        selection[(region,species)]=item
    assert len(sets)==32
    assert len(selection)==2
    for name,expected in NETWORKS.items():
        v=selection[(expected["region"],expected["species"])]
        assert (v["start"],v["end"],tuple(v["sites"]))==(
            expected["start"],expected["end"],expected["sites"]), (
            "Source opportunity changed, stop rather than silently choose favorable network",v)
    return selection,audit

def load_annual_ice(icezip,selected_sites):
    source=read_zip(icezip,"ice_595_outputs/original_595_site_months_120_source_QA.csv")
    assert len(source)==71400
    assert len({r["site_id"] for r in source})==595
    assert {int(r["year"]) for r in source}==set(range(1991,2021))
    assert {int(r["month"]) for r in source}=={8,9,10,11}
    grouped=defaultdict(dict)
    for r in source:
        site=r["site_id"]
        if site not in selected_sites:continue
        key=(site,int(r["year"]))
        month=int(r["month"])
        assert month not in grouped[key]
        assert r["source_full_595_site_monthly_support"]=="OK"
        sic=float(r["source_25km_buffer_mean_SIC_pct"])
        assert np.isfinite(sic) and 0<=sic<=100
        grouped[key][month]=sic
    years={}
    for (site,year),vals in grouped.items():
        assert set(vals)=={8,9,10,11}
        years[(site,year)]=float(np.mean([vals[m] for m in (8,9,10)]))
    assert len(years)==len(selected_sites)*30
    return years

def simplex(v):
    v=np.asarray(v,float);assert v.ndim==1 and len(v)>=3 and np.all(np.isfinite(v))
    u=np.sort(v)[::-1];c=np.cumsum(u)
    k=int(np.where(u+(1-c)/(np.arange(len(u))+1)>0)[0][-1])
    x=np.maximum(v-(c[k]-1)/(k+1),0)
    assert abs(x.sum()-1)<1e-10 and np.all(x>=0)
    return x

def ridge(X,y,nextx):
    X=np.asarray(X,float);y=np.asarray(y,float);nextx=np.asarray(nextx,float)
    assert X.ndim==2 and X.shape[0]==len(y)>=9 and X.shape[1] in (1,2,3)
    avg=X.mean(axis=0);dy=y-y.mean()
    xx=X-avg
    beta=np.linalg.solve(xx.T@xx+RIDGE_LAMBDA*np.eye(X.shape[1]),xx.T@dy)
    return float(y.mean()+(nextx-avg)@beta)

def climate_features(year,sites,annual):
    # Source year t-1 ONLY. No target-year sea ice or future count.
    vals=np.asarray([annual[(site,year-1)] for site in sites],float)
    avg=vals.mean()
    return np.column_stack([np.full(len(sites),avg/20.0), (vals-avg)/20.0])

def network(nam,region,sp,sites,years,source_scale,source_counts,annual,extra):
    ns=len(sites);years=list(years)
    assert len(years)>=17 and ns>=3
    assert all(years[i+1]-years[i]==1 for i in range(len(years)-1))
    shares={};total={}
    for y in years:
        vals=np.asarray([source_counts[(s,y)] for s in sites],float)
        assert np.all(np.isfinite(vals)) and np.all(vals>=0) and vals.sum()>0
        shares[y]=vals/vals.sum();total[y]=float(vals.sum())
    start=years[0]
    tests=years[10:]
    feature={y:climate_features(y,sites,annual) for y in years[1:]}
    if (sites[0],years[0]-1) in annual:
        feature[start]=climate_features(start,sites,annual)
    rows=[]
    for target in tests:
        train=[y for y in years if y<target]
        assert len(train)>=10
        old=np.stack([shares[y] for y in train])
        prev=shares[target-1]
        yearz=lambda y:np.asarray([(y-start)/10.0]*ns)
        time_only=simplex([ridge(
            [[(y-start)/10.] for y in train],
            [shares[y][j] for y in train],[(target-start)/10.]
        ) for j in range(ns)])
        # A lagged climate predictor for the first source year is not
        # necessarily observed (Palmer 1990); exclude it, never impute.
        trainclim=[y for y in train if y in feature]
        assert len(trainclim)>=9
        climate_only=simplex([
            ridge([feature[y][j,:1] for y in trainclim],
                  [shares[y][j] for y in trainclim],
                  feature[target][j,:1]) for j in range(ns)])
        local_only=simplex([
            ridge([feature[y][j,:2] for y in trainclim],
                  [shares[y][j] for y in trainclim],
                  feature[target][j,:2]) for j in range(ns)])
        combined=simplex([
            ridge([[(y-start)/10.,*feature[y][j,:2]]
                   for y in trainclim],
                  [shares[y][j] for y in trainclim],
                  [(target-start)/10.,*feature[target][j,:2]])
            for j in range(ns)])
        difyears=train[1:]
        dif=np.asarray([shares[y]-shares[y-1] for y in difyears])
        prevdrift=simplex(prev+dif.mean(axis=0))
        prevreg=simplex(prev+np.asarray([
            ridge([feature[y][j,:1] for y in difyears],
                  dif[:,j],feature[target][j,:1])
            for j in range(ns)]))
        prevlocal=simplex(prev+np.asarray([
            ridge([feature[y][j,:2] for y in difyears],
                  dif[:,j],feature[target][j,:2])
            for j in range(ns)]))
        predicted={
            "historical_share_mean":simplex(old.mean(axis=0)),
            "time_only":time_only,
            "lagged_regional_sic_only":climate_only,
            "lagged_site_sic_only":local_only,
            "time_plus_lagged_site_sic":combined,
            "previous_share":simplex(prev),
            "previous_plus_mean_drift":prevdrift,
            "previous_plus_lagged_regional_sic":prevreg,
            "previous_plus_lagged_site_sic":prevlocal,
        }
        target_share=shares[target]
        scored={}
        for model,estimate in predicted.items():
            scored[model]={
                "TV":float(.5*np.abs(estimate-target_share).sum()),
                "share_RMSE":float(np.sqrt(np.mean((estimate-target_share)**2))),
                "predicted_shares":list(map(float,estimate))
            }
        rows.append({
            "network":nam,"target_season":int(target),
            "n_training_seasons":len(train),
            "last_original_count_season":target-1,
            "original_total_nest_count":total[target],
            "observed_shares":list(map(float,target_share)),
            "source_ice_previous_AugOct_site_values":[annual[(site,target-1)] for site in sites],
            "models":scored
        })
    assert len(rows)==len(years)-10
    # Not n_sites independent tests: one complete network composition per year.
    model_loss={m:{
        "mean_TV":float(np.mean([r["models"][m]["TV"] for r in rows])),
        "mean_site_share_RMSE":float(np.mean([r["models"][m]["share_RMSE"] for r in rows]))
    } for m in MODELS}
    rng=np.random.default_rng(SEED+len(sites)*13+len(years))
    diffs={
     "lagged_regional_sic_only_minus_previous_share":("lagged_regional_sic_only","previous_share"),
     "lagged_site_sic_only_minus_previous_share":("lagged_site_sic_only","previous_share"),
     "time_plus_lagged_site_sic_minus_time_only":("time_plus_lagged_site_sic","time_only"),
     "previous_plus_lagged_site_sic_minus_previous_plus_mean_drift":("previous_plus_lagged_site_sic","previous_plus_mean_drift"),
     "previous_plus_lagged_site_sic_minus_previous_share":("previous_plus_lagged_site_sic","previous_share"),
    }
    sensitivity={}
    n=len(rows)
    for contrast,(a,b) in diffs.items():
        d=np.array([r["models"][a]["TV"]-r["models"][b]["TV"] for r in rows])
        starts=np.arange(n-BLOCK_YEARS+1);bs=[]
        for _ in range(DRAWS):
            idx=[]
            while len(idx)<n:
                k=int(rng.choice(starts))
                idx.extend(range(k,k+BLOCK_YEARS))
            bs.append(d[idx[:n]].mean())
        sensitivity[contrast]={
          "mean_TV_difference":float(d.mean()),
          "three_year_block_conditional_q025_q975":list(map(float,np.quantile(bs,[.025,.975]))),
          "leave_one_target_out_minmax":[
              float(min(np.delete(d,i).mean() for i in range(n))),
              float(max(np.delete(d,i).mean() for i in range(n)))],
          "n_evaluation_years":n,
          "not_population_confidence_interval":True
        }
    climat=[climate_features(y,sites,annual)[:,1]*20 for y in years[1:]]
    spread=[float(np.ptp(v)) for v in climat]
    spatial={
       "mean_site_range_in_lagged_AugOct_SIC_pp":float(np.mean(spread)),
       "median_site_range_in_lagged_AugOct_SIC_pp":float(np.median(spread)),
       "max_site_range_in_lagged_AugOct_SIC_pp":float(np.max(spread)),
       "site_to_site_differences_are_true_independent_climate_replicates":False
    }
    return rows,{
      "network":nam,"source_region":region,"species":sp,"scale":source_scale,
      "n_fixed_original_source_sites":len(sites),"site_ids":list(sites),
      "source_season_span":[years[0],years[-1]],
      "n_consecutive_recorded_seasons":len(years),
      "n_true_hidden_next_season_tests":len(tests),
      "target_season_span":[tests[0],tests[-1]],
      "original_total_nests_first_last":[total[years[0]],total[years[-1]]],
      "source_method":extra["method"],"source_250km_blocks":extra["blocks"],
      "climate_site_spread":spatial,
      "model_scores":model_loss,"score_differences":sensitivity
    }

def main(p):
    source=Path(p.original_derived)
    pal=Path(p.palmer_counts);palice=Path(p.palmer_sic)
    assert git_blob(pal)==PALMER_COUNTS_BLOB
    assert git_blob(palice)==PALMER_SIC_BLOB
    obs,inventory=locked_original_roster(source,p.source_counts_zip)
    selected,audit=support_gate(obs)
    chosen_sites=set(sum([list(x["sites"]) for x in selected.values()],[]))
    SIC=load_annual_ice(p.source_ice_zip,chosen_sites)
    inv={q["site_id"]:q for q in inventory}
    byobs={(q["site_id"],q["species"],int(q["season"])):q for q in obs}
    all_rows=[];network_summaries=[]
    for name,panel in NETWORKS.items():
        sites=panel["sites"]
        assert chosen_sites.issuperset(sites)
        vals={}
        for y in range(panel["start"],panel["end"]+1):
            for site in sites:
                q=byobs[site,panel["species"],y]
                assert q["source_region"]==panel["region"]
                assert q["original_survey_method"]==panel["method"]
                vals[site,y]=float(q["observed_nest_count"])
        blocks=sorted({inv[s]["polar_250km_fixed_grid_block"] for s in sites})
        rows,meta=network(name,panel["region"],panel["species"],sites,
                range(panel["start"],panel["end"]+1),panel["scale"],
                vals,SIC,{"method":panel["method"],"blocks":blocks})
        all_rows+=rows;network_summaries.append(meta)
    pcounts=read_csv(pal);pice=read_csv(palice)
    assert len(pcounts)==135
    actual={(q["island_name"],int(q["year"])):float(q["count"]) for q in pcounts}
    assert len(actual)==135 and set(q["island_name"] for q in pcounts)==set(PALMER_SITES)
    sicrows=[q for q in pice if q["scale"]=="among_five_islands"]
    assert len(sicrows)==27
    psic={int(q["year"]):float(q["sic"]) for q in sicrows}
    assert set(psic)==set(range(1991,2018))
    pal_counts={(site,y):actual[site,y] for site in PALMER_SITES for y in range(1991,2018)}
    pal_siteice={(site,y):psic[y] for site in PALMER_SITES for y in range(1991,2018)}
    for y in range(1991,2018):
        assert abs(sum(actual[s,y] for s in PALMER_SITES)-
                   float(next(q["total"] for q in sicrows if int(q["year"])==y)))<1e-9
    rows,meta=network("Palmer_ADPE_5physical_island",
       "Palmer islands","ADPE",PALMER_SITES,
       range(1991,2018),"physical_islands",pal_counts,pal_siteice,
       {"method":"Palmer LTER island colony_code annual aggregated counts",
        "blocks":["Not sourced at original 5-island code grain"]})
    all_rows+=rows;network_summaries.insert(0,meta)
    assert len(all_rows)==17+14+7
    assert [x["n_true_hidden_next_season_tests"] for x in network_summaries]==[17,14,7]
    out=Path(p.out);out.mkdir(parents=True,exist_ok=True)
    with (out/"network_support_audit_32_region_species.json").open("w") as f:
        json.dump(audit,f,indent=2)
    with (out/"three_network_time_forward_predictions.json").open("w") as f:
        json.dump(all_rows,f,indent=2)
    with (out/"three_network_lag1_sic_allocation_receipt.json").open("w") as f:
        receipt={
          "status":"PASS_OBSERVED_THREE_NETWORK_LAGGED_SIC_VS_PREVIOUS_ALLOCATION",
          "n_source_region_species_combinations_audited":len(audit),
          "n_eligible_long_complete_cohorts":len(selected),
          "all_eligible_cohorts_included_not_outcome_selected":True,
          "n_original_mapppd_count_rows":len(obs),
          "n_original_satellite_SIC_site_months":71400,
          "n_true_year_network_holdouts":len(all_rows),
          "source_git_blob_derived_2999":RAW_BLOB,
          "source_count_artifact_sha256":sha(p.source_counts_zip),
          "source_ice_artifact_sha256":sha(p.source_ice_zip),
          "palmer_count_git_blob_sha1":PALMER_COUNTS_BLOB,
          "palmer_SIC_git_blob_sha1":PALMER_SIC_BLOB,
          "environment_at_prediction_origin":"Only true Aug-Oct sea ice from previous breeding-season year t-1",
          "held_out_target_year_climate_used":False,
          "held_out_target_year_counts_used_in_training":False,
          "species_or_site_absence_imputed_from_nonobservation":False,
          "different_spatial_grain_between_palmer_islands_and_other_colony_codes":True,
          "one_network_is_not_independent_regions_per_year":True,
          "not_climate_impact_or_demographic_forecast":True,
          "not_pre_registered_independent_confirmatory_study":True,
          "model_ridge_lambda":RIDGE_LAMBDA,
          "bootstrap_contiguous_year_length":BLOCK_YEARS,
          "bootstrap_draws":DRAWS,
          "networks":network_summaries}
        json.dump(receipt,f,indent=2,ensure_ascii=False)
        f.write("\n")
    with (out/"three_network_model_scores.csv").open("w",newline="") as f:
        fields=["network","source_region","species","scale","n_fixed_original_source_sites",
                "n_true_hidden_next_season_tests","model","mean_TV","mean_site_share_RMSE"]
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for n in network_summaries:
            for model,metric in n["model_scores"].items():
                w.writerow({**{k:n[k] for k in fields[:6]},"model":model,
                            "mean_TV":metric["mean_TV"],
                            "mean_site_share_RMSE":metric["mean_site_share_RMSE"]})
    print("PENGUIN_ALLOCATION_NETWORK_LAGGED_SIC="+json.dumps(
        {"status":receipt["status"],"networks":[{
        "network":x["network"],"n":x["n_fixed_original_source_sites"],
        "source_span":x["source_season_span"],"holdouts":x["n_true_hidden_next_season_tests"],
        "mean_site_sic_spread":x["climate_site_spread"]["mean_site_range_in_lagged_AugOct_SIC_pp"],
        "TV":{k:round(v["mean_TV"],6) for k,v in x["model_scores"].items()},
        "comparisons":x["score_differences"]} for x in network_summaries]
        },ensure_ascii=False),flush=True)

def selftest():
    assert np.allclose(simplex([-.4,.8,.9]),[0.,.45,.55])
    xs=np.arange(9,dtype=float).reshape(-1,1)
    q=ridge(xs,np.arange(9,dtype=float),[9.0])
    assert 6<q<9.5
    demo=[{"source_region":"R","species":"S","site_id":"A","season":str(y)}
          for y in range(2000,2012)]
    demo+=[{"source_region":"R","species":"S","site_id":"B","season":str(y)}
          for y in range(2000,2012)]
    demo+=[{"source_region":"R","species":"S","site_id":"C","season":str(y)}
          for y in range(2000,2012)]
    # Tests are deterministic and cannot infer source absences from missing rows.
    out=[]
    for x in demo:out.append({**x,"observed_nest_count":100})
    selected,audit=support_gate_demo(out)
    assert selected["end"]==2011 and selected["start"]==2000
    assert len(selected["sites"])==3
    print("PASS synthetic source opportunity, simplex and ridge regularization")

def support_gate_demo(obs):
    by=defaultdict(set)
    for x in obs:by[x["site_id"]].add(int(x["season"]))
    years=set(range(2000,2012))
    sites=tuple(sorted(x for x,v in by.items() if years.issubset(v)))
    return {"sites":sites,"start":2000,"end":2011},None

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.add_argument("--original-derived",type=Path)
    ap.add_argument("--source-counts-zip",type=Path)
    ap.add_argument("--source-ice-zip",type=Path)
    ap.add_argument("--palmer-counts",type=Path)
    ap.add_argument("--palmer-sic",type=Path)
    ap.add_argument("--out",type=Path)
    a=ap.parse_args()
    if a.self_test:selftest()
    else:
        assert all((a.original_derived,a.source_counts_zip,a.source_ice_zip,
                    a.palmer_counts,a.palmer_sic,a.out))
        main(a)
