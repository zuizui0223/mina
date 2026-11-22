#!/usr/bin/env python3
"""Palmer LTER five-island nest-share time-forward forecast comparison.

1991-2017 genuine simultaneous Adélie breeding-pair source census across CHR,
COR, HUM, LIT, TOR; original same-source Aug-Oct nearshore SIC at Litchfield.
Train only previous years for targets 2001..2017. No 2050/2100 population
forecast and no causal inference: previous measured site shares are an
information baseline, NOT proof of natal philopatry or spatial mechanism.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path
import numpy as np

ISLANDS=("CHR","COR","HUM","LIT","TOR")
YEARS=tuple(range(1991,2018))
TEST=tuple(range(2001,2018))
SEED=20261117
N_BLOCK=3
B=4000
SOURCE_COUNTS_SHA="20d1c11d6478899954fb837c5505708e78ca539d"
SOURCE_ICE_SHA="701794b329bf1c1fc872399ad2013a014c9608a5"
MODELS=(
  "historical_mean","time_only","ice_only","time_plus_ice",
  "previous_share","previous_share_plus_drift","previous_share_plus_ice"
)

def git_blob_sha(p:Path)->str:
    b=p.read_bytes()
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()

def read_csv(path:Path):
    with path.open("r",newline="",encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def load(counts_file,ice_file):
    assert git_blob_sha(counts_file)==SOURCE_COUNTS_SHA, "STOP changed source counts"
    assert git_blob_sha(ice_file)==SOURCE_ICE_SHA, "STOP changed source SIC"
    original=read_csv(counts_file)
    observed=read_csv(ice_file)
    assert len(original)==5*27
    assert len({(r["island_name"],r["year"]) for r in original})==len(original)
    assert {r["island_name"] for r in original}==set(ISLANDS)
    assert {int(r["year"]) for r in original}==set(YEARS)
    m={}
    n_component_changes={}
    for z in original:
        year=int(z["year"]);island=z["island_name"]
        n=float(z["count"]);components=int(z["components"])
        assert n>=0 and np.isfinite(n) and components>0
        assert float(n).is_integer()
        m[(year,island)]=float(n)
        n_component_changes.setdefault(island,set()).add(components)
    ice=[r for r in observed if r["scale"]=="among_five_islands"]
    assert len(ice)==27 and {int(r["year"]) for r in ice}==set(YEARS)
    SIC={}
    for z in ice:
        year=int(z["year"]);v=float(z["sic"])
        assert 0<=v<=100 and np.isfinite(v)
        SIC[year]=v
        assert abs(sum(m[(year,k)] for k in ISLANDS)-float(z["total"]))<1e-9
    counts={y:np.array([m[(y,k)] for k in ISLANDS],float) for y in YEARS}
    totals={y:float(counts[y].sum()) for y in YEARS}
    assert totals[1991]==6689 and totals[2017]==140
    assert all(totals[y]>0 for y in YEARS)
    assert all(m[(y,"LIT")]==0 for y in range(2007,2018))
    shares={y:counts[y]/totals[y] for y in YEARS}
    assert all(np.isclose(v.sum(),1) for v in shares.values())
    return shares,SIC,totals,{k:sorted(x) for k,x in n_component_changes.items()}

def simplex(values):
    """Euclidean simplex projection; no information about future counts."""
    v=np.asarray(values,float)
    assert len(v)==5 and np.all(np.isfinite(v))
    u=np.sort(v)[::-1]
    cs=np.cumsum(u)
    rho=int(np.where(u+(1.0-cs)/(np.arange(len(u))+1)>0)[0][-1])
    theta=(cs[rho]-1)/(rho+1)
    w=np.maximum(v-theta,0.)
    assert np.all(w>=0) and abs(w.sum()-1)<1e-10
    return w

def ridge_predict(X,y,next_x,lam=1.):
    """Fixed ridge lambda=1 on centered slopes; intercept unpenalized."""
    X=np.asarray(X,float);y=np.asarray(y,float)
    next_x=np.asarray(next_x,float)
    assert X.ndim==2 and y.ndim==1 and len(X)==len(y)
    assert X.shape[1] in (1,2) and len(X)>=9
    xm=X.mean(axis=0);ym=float(y.mean())
    xx=X-xm
    beta=np.linalg.solve(xx.T@xx+lam*np.eye(X.shape[1]),xx.T@(y-ym))
    return float(ym+(next_x-xm)@beta)

def features(year,sic):
    return [(year-1991)/10.,(sic[year]-50)/20.]

def time_forward(shares,sic,totals):
    rows=[]
    for target in TEST:
        trained=[y for y in YEARS if y<target]
        assert len(trained)>=10
        prev=shares[target-1]
        # Climate nowcast at t: ice from Aug-Oct (before observed Nov census);
        # it is not a forecast of climate, and NEVER a held-out nest outcome.
        ft=np.array([features(y,sic) for y in trained])
        tx=np.array(features(target,sic))
        historic=np.array([shares[y] for y in trained])
        historical=simplex(historic.mean(axis=0))
        baseline_time=simplex([
            ridge_predict(ft[:,[0]],historic[:,i],tx[[0]]) for i in range(5)])
        baseline_ice=simplex([
            ridge_predict(ft[:,[1]],historic[:,i],tx[[1]]) for i in range(5)])
        baseline_time_ice=simplex([
            ridge_predict(ft,historic[:,i],tx) for i in range(5)])
        # At origin, last-year allocation state is completely observed.
        pprev=simplex(prev)
        # Historical training transitions use t' and t'-1 only; target
        # year and any later year are not included in either model fit.
        tdiff=[y for y in trained if y>1991]
        dy=np.array([shares[y]-shares[y-1] for y in tdiff])
        xdiff=np.array([[(sic[y]-sic[y-1])/20.] for y in tdiff])
        target_sic_step=np.array([(sic[target]-sic[target-1])/20.])
        config_drift=simplex(pprev+dy.mean(axis=0))
        config_ice=simplex(pprev+np.array([
             ridge_predict(xdiff,dy[:,i],target_sic_step) for i in range(5)]))
        predictions={
            "historical_mean":historical,
            "time_only":baseline_time,
            "ice_only":baseline_ice,
            "time_plus_ice":baseline_time_ice,
            "previous_share":pprev,
            "previous_share_plus_drift":config_drift,
            "previous_share_plus_ice":config_ice
        }
        truth=shares[target]
        per={name:{
            "TV":float(0.5*np.abs(x-truth).sum()),
            "RMSE":float(np.sqrt(np.mean((x-truth)**2))),
            "forecast":list(map(float,x)),
        } for name,x in predictions.items()}
        for k in MODELS:
            assert k in per and 0<=per[k]["TV"]<=1
        rows.append({
            "test_year":int(target),"training_years":int(len(trained)),
            "most_recent_source_census_year":int(target-1),
            "physical_SIC_AugOct_percent":float(sic[target]),
            "original_census_total_pairs":float(totals[target]),
            "observed_share":list(map(float,truth)),
            "models":per
        })
    assert len(rows)==17
    return rows

def quantile(z,p):
    return float(np.quantile(np.asarray(z),p))

def block_sensitivity(rows):
    # Overlapping forward-in-time 3-year year-block resampling is a
    # CONDITIONAL temporal sensitivity for this one nonstationary island
    # network; it is not 4000 independent observed seasons.
    rng=np.random.default_rng(SEED)
    n=len(rows); starts=np.arange(n-N_BLOCK+1)
    metrics={
     "ice_only_minus_previous_share":("ice_only","previous_share"),
     "time_plus_ice_minus_time_only":("time_plus_ice","time_only"),
     "previous_share_plus_ice_minus_previous_share_plus_drift":
         ("previous_share_plus_ice","previous_share_plus_drift"),
     "previous_share_plus_ice_minus_previous_share":
         ("previous_share_plus_ice","previous_share"),
    }
    res={}
    for name,(a,b) in metrics.items():
        deltas=np.array([r["models"][a]["TV"]-r["models"][b]["TV"] for r in rows])
        bootstrap=[]
        for _ in range(B):
            idx=[]
            while len(idx)<n:
                start=int(rng.choice(starts))
                idx.extend(range(start,start+N_BLOCK))
            idx=idx[:n]
            bootstrap.append(float(deltas[idx].mean()))
        res[name]={
            "point_mean_TV_delta":float(deltas.mean()),
            "num_test_years":n,
            "block_length_years":N_BLOCK,
            "draws":B,
            "conditional_q025_q975":[quantile(bootstrap,.025),quantile(bootstrap,.975)],
            "positive_delta_means_first_model_worse":True
        }
    return res

def run(count_file,ice_file,out):
    out.mkdir(parents=True,exist_ok=True)
    shares,sic,totals,changes=load(count_file,ice_file)
    score=time_forward(shares,sic,totals)
    assert all(row["original_census_total_pairs"]>0 for row in score)
    maetv={
        k:float(np.mean([r["models"][k]["TV"] for r in score]))
        for k in MODELS
    }
    rmse={k:float(np.mean([r["models"][k]["RMSE"] for r in score])) for k in MODELS}
    assert maetv["previous_share"]<maetv["ice_only"]
    # Phase sensitivity is frozen at the recorded 2007 Litchfield transition
    # to true zero. It is NOT a change-point fitted from forecasting errors.
    def phase_summary(sub):
        return {
            "n_years":len(sub),
            "years":[sub[0]["test_year"],sub[-1]["test_year"]],
            "mean_TV":{name:float(np.mean([z["models"][name]["TV"] for z in sub]))
                       for name in MODELS}
        }
    phase={
       "2001_2006_before_LIT_observed_zero":phase_summary(
             [z for z in score if z["test_year"]<=2006]),
       "2007_2017_after_LIT_observed_zero":phase_summary(
             [z for z in score if z["test_year"]>=2007])
    }
    comparison_ablation={
      "climate_only_minus_observed_previous_share":{
        "leave_one_target_year_out_min":float(min(
            np.mean([x["models"]["ice_only"]["TV"]-x["models"]["previous_share"]["TV"]
                     for x in score if x is not z]) for z in score)),
        "leave_one_target_year_out_max":float(max(
            np.mean([x["models"]["ice_only"]["TV"]-x["models"]["previous_share"]["TV"]
                     for x in score if x is not z]) for z in score)),
      },
      "adding_ice_to_configuration_drift":{
        "leave_one_target_year_out_min":float(min(
            np.mean([x["models"]["previous_share_plus_ice"]["TV"]-
                     x["models"]["previous_share_plus_drift"]["TV"]
                     for x in score if x is not z]) for z in score)),
        "leave_one_target_year_out_max":float(max(
            np.mean([x["models"]["previous_share_plus_ice"]["TV"]-
                     x["models"]["previous_share_plus_drift"]["TV"]
                     for x in score if x is not z]) for z in score)),
      },
    }
    summary={
        "status":"ORIGINAL_PALMER_5ISLAND_TRUE_FORWARD_ALLOCATION_SIC_COMPARISON",
        "source_counts_git_blob_sha1":SOURCE_COUNTS_SHA,
        "source_ice_git_blob_sha1":SOURCE_ICE_SHA,
        "n_original_years":27,
        "n_original_distinct_physical_islands":5,
        "n_original_island_years":135,
        "n_temporal_test_years":17,
        "test_years":[2001,2017],
        "source_total_pairs_first_last":[totals[1991],totals[2017]],
        "source_number_of_component_counts_by_island":changes,
        "physical_ice_source":"Litchfield 0-100km OSI SAF Aug-Oct; one shared regional SIC per year",
        "score":"equal-year total variation distance among five simultaneously observed islands (lower better)",
        "models":{
          k:{"test_mean_total_variation":maetv[k],"test_mean_island_share_RMSE":rmse[k]}
          for k in MODELS
        },
        "year_block_sensitivity":block_sensitivity(score),
        "fixed_observed_LIT_zero_transition_phase_sensitivity":phase,
        "target_year_omission_sensitivity":comparison_ablation,
        "no_independent_island_climate_replicates":True,
        "previous_share_is_observed_state_not_neutral_spatial_configuration_causality":True,
        "not_a_prospective_climate_forecast":True,
        "island_component_count_changes_not_uniform_observation_areas":True,
        "no_species_transfer_or_future_nests":True
    }
    csvfile=out/"original_palmer_5island_source_one_year_forecast_scores.csv"
    fields=["test_year","training_years","most_recent_source_census_year",
            "physical_SIC_AugOct_percent","original_census_total_pairs"]+list(MODELS)
    with csvfile.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in score:
            w.writerow({**{k:r[k] for k in fields[:5]},
                        **{k:r["models"][k]["TV"] for k in MODELS}})
    (out/"original_palmer_5island_source_prediction_rows.json").write_text(
        json.dumps(score,indent=2,ensure_ascii=False)+"\n")
    (out/"original_palmer_5island_forward_verdict.json").write_text(
        json.dumps(summary,indent=2,ensure_ascii=False)+"\n")
    print("SOURCE_PALMER_ALLOCATION_FORECAST="+json.dumps(summary,ensure_ascii=False),flush=True)

def self_test():
    assert np.allclose(simplex([-.3,.5,.7,.1,0]),simplex([-.3,.5,.7,.1,0]))
    assert abs(simplex([1,1,1,1,1]).sum()-1)<1e-12
    y=np.array([1.,2.,3.,4.,5.,6.,7.,8.,9.,10.])
    x=np.arange(10,dtype=float).reshape(-1,1)
    p=ridge_predict(x,y,[10],lam=1.)
    assert 10<p<11.6 and np.isfinite(p)
    print("PASS synthetic no-future feature, ridge and five-island simplex arithmetic")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--counts-source",type=Path)
    p.add_argument("--ice-source",type=Path)
    p.add_argument("--output",type=Path)
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:self_test()
    else:
        assert all((a.counts_source,a.ice_source,a.output))
        run(a.counts_source,a.ice_source,a.output)
