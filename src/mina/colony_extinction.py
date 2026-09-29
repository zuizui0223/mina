"""Palmer colony-code durable-extinction analysis."""
from __future__ import annotations
import argparse,json,math
from collections import defaultdict
from pathlib import Path
import numpy as np
from .lter import ISLANDS,load_colony_rows

N=100000; SEED=20260929

def event_years(rows,islands=ISLANDS,later=2):
    g=defaultdict(list)
    for r in rows:
        if str(r["island"]) in islands:g[(str(r["island"]),str(r["colony_code"]))].append(r)
    out={}
    for key,x in g.items():
        x=sorted(x,key=lambda r:int(r["year"]))
        y=np.array([int(r["year"]) for r in x]); c=np.array([float(r["breeding_pairs"]) for r in x])
        out[key]=None
        for i in range(1,len(x)):
            if y[i]-y[i-1]!=1 or c[i-1]<=0 or c[i]!=0:continue
            if len(c[i+1:])<later:continue
            if any(y[i+j]!=y[i]+j for j in range(1,later+1)):continue
            if np.all(c[i+1:]==0):out[key]=int(y[i]);break
    return out

def risk_rows(path,islands=ISLANDS,later=2,prior_min=1.0):
    rows=load_colony_rows(path); ev=event_years(rows,islands,later)
    g=defaultdict(list); totals=defaultdict(float)
    for r in rows:
        isl=str(r["island"])
        if isl not in islands:continue
        g[(isl,str(r["colony_code"]))].append(r); totals[(isl,int(r["year"]))]+=float(r["breeding_pairs"])
    out=[]
    for (isl,code),x in sorted(g.items()):
        by={int(r["year"]):float(r["breeding_pairs"]) for r in x}
        for y,c in sorted(by.items()):
            if c<prior_min or y+1 not in by:continue
            out.append(dict(island=isl,colony_code=code,start_year=y,end_year=y+1,
                prior_count=c,next_count=by[y+1],prior_share=c/totals[(isl,y)],
                event=int(ev[(isl,code)]==y+1)))
    return out

def sets(rows,event_required=True):
    g=defaultdict(list)
    for r in rows:g[(r["island"],r["start_year"])].append(r)
    out=[]
    for (isl,y),x in sorted(g.items()):
        if len(x)<2:continue
        v=np.log1p([r["prior_count"] for r in x]); sd=np.std(v,ddof=1)
        if sd<=0:continue
        z=(v-np.mean(v))/sd; e=np.array([r["event"] for r in x],int); k=int(e.sum())
        if event_required and (k==0 or k==len(x)):continue
        out.append(dict(island=isl,start_year=y,rows=x,z=z,event=e,k=k))
    return out

def contrast(s,e=None):
    e=s["event"] if e is None else np.asarray(e,int); z=s["z"]
    return float(np.mean(z[e==1])-np.mean(z[e==0]))

def permute(ss,n=N,seed=SEED):
    obs=float(np.mean([contrast(s) for s in ss])); rng=np.random.default_rng(seed); null=np.zeros(n)
    for s in ss:
        z=s["z"]; k=s["k"]; m=len(z)
        u=rng.random((n,m)); idx=np.argpartition(u,k-1,axis=1)[:,:k]
        a=z[idx].sum(1); total=z.sum()
        null+=a/k-(total-a)/(m-k)
    null/=len(ss)
    return dict(observed_contrast=obs,permutations=n,seed=seed,
        one_sided_lower_p=(1+int(np.sum(null<=obs)))/(n+1),
        null_mean=float(np.mean(null)),null_sd=float(np.std(null,ddof=1)),
        null_q025=float(np.quantile(null,.025)),null_q50=float(np.quantile(null,.5)),
        null_q975=float(np.quantile(null,.975)))

def logistic(rows):
    ss=sets(rows,False); flat=[]
    for s in ss:
        for r,z,e in zip(s["rows"],s["z"],s["event"]):flat.append((r["island"],r["start_year"],z,e))
    isls=sorted({x[0] for x in flat}); years=np.array([x[1] for x in flat],float); y=np.array([x[3] for x in flat],float)
    cols=[np.ones(len(flat)),np.array([x[2] for x in flat]),years-years.mean()]
    for isl in isls[1:]:cols.append(np.array([x[0]==isl for x in flat],float))
    X=np.column_stack(cols); b=np.zeros(X.shape[1]); conv=False
    for it in range(100):
        eta=X@b; p=1/(1+np.exp(-np.clip(eta,-700,700))); w=p*(1-p)
        step=np.linalg.solve(X.T@(w[:,None]*X),X.T@(y-p)); b+=step
        if np.max(np.abs(step))<1e-10:conv=True;break
    eta=X@b;p=1/(1+np.exp(-np.clip(eta,-700,700)));w=p*(1-p)
    se=np.sqrt(np.diag(np.linalg.inv(X.T@(w[:,None]*X))))
    return dict(n_rows=len(flat),n_events=int(y.sum()),converged=conv,iterations=it+1,
        z_prior_size_coefficient=float(b[1]),z_prior_size_se=float(se[1]),
        z_prior_size_odds_ratio=math.exp(float(b[1])),
        z_prior_size_or_95ci=[math.exp(float(b[1]-1.96*se[1])),math.exp(float(b[1]+1.96*se[1]))],
        year_centered_coefficient=float(b[2]))

def describe(rows,ss):
    pair=[(r,int(e)) for s in ss for r,e in zip(s["rows"],s["event"])]
    ev=np.array([r["prior_count"] for r,e in pair if e],float); sv=np.array([r["prior_count"] for r,e in pair if not e],float)
    ratios=[]
    for s in ss:
        c=np.array([r["prior_count"] for r in s["rows"]],float);e=s["event"]
        ratios.append(float(c[e==1].mean()/c[e==0].mean()))
    order=sorted(rows,key=lambda r:(r["prior_count"],r["island"],r["start_year"],r["colony_code"]))
    qs={}
    for i,idx in enumerate(np.array_split(np.arange(len(order)),4),1):
        x=[order[int(j)] for j in idx]
        qs[f"Q{i}"]=dict(n=len(x),events=sum(r["event"] for r in x),
            event_rate=float(np.mean([r["event"] for r in x])),
            median_prior_count=float(np.median([r["prior_count"] for r in x])))
    return dict(event_prior_count_median=float(np.median(ev)),event_prior_count_mean=float(ev.mean()),
        survivor_prior_count_median=float(np.median(sv)),survivor_prior_count_mean=float(sv.mean()),
        median_riskset_event_to_survivor_mean_count_ratio=float(np.median(ratios)),
        geometric_mean_riskset_event_to_survivor_mean_count_ratio=math.exp(float(np.mean(np.log(ratios)))),
        prior_count_quartiles=qs)

def one(path,islands=ISLANDS,later=2,prior_min=1,n=N,seed=SEED):
    r=risk_rows(path,islands,later,prior_min); ss=sets(r,True)
    return dict(n_risk_rows=len(r),n_durable_events=sum(x["event"] for x in r),
        n_comparable_event_risk_sets=len(ss),n_comparable_events=sum(s["k"] for s in ss),**permute(ss,n,seed))

def analyze(path,n=N,seed=SEED):
    r=risk_rows(path); ss=sets(r,True); primary=one(path,n=n,seed=seed)
    sens=dict(two_zero_rule=one(path,later=1,n=n,seed=seed),
        exclude_litchfield=one(path,tuple(x for x in ISLANDS if x!="LIT"),n=n,seed=seed),
        prior_count_ge_2=one(path,prior_min=2,n=n,seed=seed))
    loo={}
    for isl in ISLANDS:
        rr=risk_rows(path,tuple(x for x in ISLANDS if x!=isl)); s=sets(rr,True)
        loo[isl]=dict(observed_contrast=float(np.mean([contrast(x) for x in s])),
            n_comparable_event_risk_sets=len(s),n_durable_events=sum(x["event"] for x in rr))
    return dict(schema_version=1,analysis_id="mina-palmer-colony-extinction-hazard-v1",
        primary=primary,descriptives=describe(r,ss),secondary_logistic=logistic(r),
        sensitivities=sens,leave_one_island_out=loo,
        decision=dict(small_group_vulnerability_exchangeability_test_supported=
            primary["observed_contrast"]<0 and primary["one_sided_lower_p"]<=.05,
            mechanism_requires_zero_boundary_audit=True),
        interpretation_boundary=dict(colony_code_is_not_assumed_physical_patch=True,
            shared_island_year_context_is_conditioned_by_risk_set=True,
            size_effect_alone_does_not_identify_social_facilitation=True,
            regional_decline_cause_not_identified=True))

def main():
    p=argparse.ArgumentParser();p.add_argument("--census",required=True,type=Path);p.add_argument("--out",required=True,type=Path)
    p.add_argument("--permutations",type=int,default=N);p.add_argument("--seed",type=int,default=SEED);a=p.parse_args()
    x=analyze(a.census,a.permutations,a.seed);a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n");return 0
if __name__=="__main__":raise SystemExit(main())
