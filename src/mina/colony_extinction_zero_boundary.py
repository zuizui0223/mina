"""Zero-boundary audit for Palmer durable colony extinction."""
from __future__ import annotations
import argparse,itertools,json
from pathlib import Path
import numpy as np
from .colony_extinction import risk_rows,sets,contrast

N=100000;SEED=20260930
MODELS={"poisson":0.0,"gamma_poisson_cv10":0.10,"gamma_poisson_cv20":0.20}

def subset_dist(s,cv):
    k=s["k"];m=len(s["rows"]);z=s["z"]
    prior=np.array([r["prior_count"] for r in s["rows"]],float)
    nxt=np.array([r["next_count"] for r in s["rows"]],float)
    rate=float(nxt.sum()/prior.sum());mu=rate*prior
    if cv==0:q=np.exp(-mu)
    else:
        shape=1/(cv*cv);q=(shape/(shape+mu))**shape
    q=np.clip(q,1e-300,1-1e-15);logod=np.log(q)-np.log1p(-q)
    combos=list(itertools.combinations(range(m),k))
    logw=np.array([logod[list(c)].sum() for c in combos]);w=np.exp(logw-logw.max());w/=w.sum()
    vals=[];total=z.sum()
    for c in combos:
        a=z[list(c)].sum();vals.append(a/k-(total-a)/(m-k))
    return np.asarray(vals),w,rate

def run(path,n=N,seed=SEED):
    ss=sets(risk_rows(path),True);obs=float(np.mean([contrast(s) for s in ss]));models={}
    for offset,(name,cv) in enumerate(MODELS.items()):
        rng=np.random.default_rng(seed+offset);null=np.zeros(n);rates=[]
        for s in ss:
            vals,w,rate=subset_dist(s,cv);rates.append(rate)
            null+=vals[rng.choice(len(vals),size=n,p=w)]
        null/=len(ss);p=(1+int(np.sum(null<=obs)))/(n+1)
        models[name]=dict(multiplicative_cv=cv,observed_contrast=obs,
            one_sided_lower_p=p,null_mean=float(np.mean(null)),null_sd=float(np.std(null,ddof=1)),
            null_q025=float(np.quantile(null,.025)),null_q50=float(np.quantile(null,.5)),
            null_q975=float(np.quantile(null,.975)),min_common_rate=float(np.min(rates)),
            median_common_rate=float(np.median(rates)),max_common_rate=float(np.max(rates)))
    passed=all(x["one_sided_lower_p"]<=.05 for x in models.values())
    return dict(schema_version=1,analysis_id="mina-palmer-colony-extinction-zero-boundary-audit-v1",
        n_event_risk_sets=len(ss),simulations=n,seed=seed,models=models,
        decision=dict(exceeds_zero_boundary=passed,size_selection_only=not passed),
        interpretation=dict(
            small_colonies_disappear_first_descriptively=True,
            size_ordering_stronger_than_proportional_zero_hitting=passed,
            social_facilitation_supported_by_size_effect_alone=False,
            next_question="Which colony-specific states make a colony small before it crosses the stochastic zero boundary?"))

def main():
    p=argparse.ArgumentParser();p.add_argument("--census",required=True,type=Path);p.add_argument("--out",required=True,type=Path)
    p.add_argument("--simulations",type=int,default=N);p.add_argument("--seed",type=int,default=SEED);a=p.parse_args()
    x=run(a.census,a.simulations,a.seed);a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(x,indent=2,sort_keys=True)+"\n");return 0
if __name__=="__main__":raise SystemExit(main())
