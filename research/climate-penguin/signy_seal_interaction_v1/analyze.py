"""Frozen normalized-panel association; never infer source calendar or missing counts."""
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import t

FIELDS=["season_start","fur_seals_feb","antecedent_ice_days","chinstrap","gentoo","adelie"]
def z(x):
    x=np.asarray(x,float); sd=x.std(ddof=0)
    if not sd>0: raise ValueError("constant predictor")
    return (x-x.mean())/sd
def fit(y,x,years):
    n,k=x.shape
    if n<=k or np.linalg.matrix_rank(x)!=k: raise ValueError("rank/support")
    inv=np.linalg.inv(x.T@x); b=inv@x.T@y; e=y-x@b; u=x*e[:,None]
    dist=np.abs(years[:,None]-years[None,:])
    w=np.maximum(0,1-dist/3)
    cov=inv@(u.T@w@u)@inv*n/(n-k)
    se=np.sqrt(max(0,cov[1,1])); crit=t.ppf(.975,n-k)
    return {"beta":float(b[1]),"lo":float(b[1]-crit*se),"hi":float(b[1]+crit*se),"n":int(n)}
def run(d):
    if set(FIELDS)-set(d): raise ValueError("missing normalized fields")
    d=d[FIELDS].apply(pd.to_numeric,errors="raise").sort_values("season_start")
    if not np.isfinite(d.to_numpy()).all(): raise ValueError("missing/nonfinite: complete panel only")
    years=d.season_start.to_numpy()
    if (years%1!=0).any() or d.season_start.duplicated().any() or not ((years>=1996)&(years<=2019)).all(): raise ValueError("calendar/duplicate")
    if (d[FIELDS[1:]]<0).any().any() or (d.antecedent_ice_days>366).any() or (d.fur_seals_feb%1!=0).any(): raise ValueError("invalid count/ice/ratio")
    blocks=(years-1996)//4
    if len(d)<20 or len(set(blocks))<6: raise ValueError("frozen support gate")
    seal=z(np.log1p(d.fur_seals_feb)); ice=z(d.antecedent_ice_days)
    x=np.column_stack([np.ones(len(d)),seal,ice,years-years.mean()])
    y=(d.chinstrap-d.gentoo).to_numpy()
    main=fit(y,x,years)
    loo=[fit(y[blocks!=b],x[blocks!=b],years[blocks!=b])["beta"] for b in sorted(set(blocks))]
    slopes={sp:fit(d[sp].to_numpy(),x,years) for sp in ("chinstrap","gentoo","adelie")}
    adj=np.diff(years)==1
    def sensitivity(mode):
        try:
            if mode=="first_difference":
                xs=np.column_stack([np.ones(adj.sum()),np.diff(seal)[adj],np.diff(ice)[adj]])
                return fit(np.diff(y)[adj],xs,years[1:][adj])
            xs=np.column_stack([np.ones(adj.sum()),seal[:-1][adj],ice[1:][adj],years[1:][adj]-years.mean()])
            return fit(y[1:][adj],xs,years[1:][adj])
        except ValueError as e: return {"blocked":str(e)}
    supported=main["hi"]<0 and max(loo)<0
    return {"primary_chinstrap_minus_gentoo":main,"block_leave_one_out":loo,
            "absolute_species_slopes_descriptive":slopes,
            "adelie_minus_gentoo_descriptive":fit((d.adelie-d.gentoo).to_numpy(),x,years),
            "first_difference":sensitivity("first_difference"),"previous_february":sensitivity("previous_february"),
            "negative_relative_association_supported":bool(supported),
            "negative_chinstrap_absolute_slope":bool(slopes["chinstrap"]["beta"]<0),
            "common_years":years.astype(int).tolist(),"independent_islands":1,
            "causal_competition_or_vegetation_inference":False}
def selftest():
    rng=np.random.default_rng(55); yr=np.arange(1996,2020); seal=rng.integers(1000,20000,24); ice=rng.uniform(80,200,24)
    s=z(np.log1p(seal)); g=1+rng.normal(0,.03,24)
    d=pd.DataFrame(dict(season_start=yr,fur_seals_feb=seal,antecedent_ice_days=ice,chinstrap=g-.25*s,adelie=g-.1*s,gentoo=g))
    r=run(d)
    assert abs(r["primary_chinstrap_minus_gentoo"]["beta"]+.25)<1e-9 and r["negative_relative_association_supported"]
    for bad in (d.iloc[:19],pd.concat([d,d.iloc[:1]]),d.assign(fur_seals_feb=np.nan)):
        try: run(bad)
        except ValueError: continue
        raise AssertionError("gate failed")
    print("synthetic slope, duplicate, missingness and support tests passed")
def main():
    p=argparse.ArgumentParser();p.add_argument("--selftest",action="store_true");p.add_argument("--panel",type=Path);p.add_argument("--receipt",type=Path);p.add_argument("--out",type=Path)
    a=p.parse_args()
    if a.selftest: selftest(); return
    if not all((a.panel,a.receipt,a.out)): p.error("panel, source/calendar/roster receipt and out required")
    receipt=json.loads(a.receipt.read_text())
    import hashlib
    if receipt.get("status")!="REVIEWED_SOURCE_CALENDAR_ROSTER_PASS" or receipt.get("panel_sha256")!=hashlib.sha256(a.panel.read_bytes()).hexdigest(): raise ValueError("no valid reviewed receipt")
    result=run(pd.read_csv(a.panel)); result["panel_sha256"]=receipt["panel_sha256"]
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(result,indent=2)+"\n")
if __name__=="__main__": main()
