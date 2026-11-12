"""Linear within-colony change associations and held-region, optionally forward-time evaluation."""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
from scipy.stats import t
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R.parent/"salinity_all"))
from analyze import fit,design
Q=pd.read_csv(R.parent/"salinity_all/intervals.csv")
models={"initial":["initial"],"ice":["initial","ice_rate"],"sst":["initial","temp_rate"],"joint":["initial","ice_rate","temp_rate"]}
def save(d,k):pd.DataFrame(d).to_csv(R/k,index=False,lineterminator="\n")
def main():
    slopes=[];pred=[];scores=[]
    for pair,g in Q.groupby("pair"):
        for omit in ["none",*sorted(g.region.unique())]:
            train=g if omit=="none" else g[g.region!=omit]
            for spec,h,fixed in [("full",train,False),("annual",train[train.gap==1],False),("colony_time",train,True)]:
                for label,cols in models.items():
                    if label=="initial" or h.site.nunique()<2:continue
                    x=design(h,cols,fixed,fixed)
                    if len(h)<=x.shape[1] or np.linalg.matrix_rank(x)<x.shape[1]:continue
                    mod=fit(h,cols,fixed,fixed);cov=mod.get_robustcov_results(cov_type="cluster",groups=h.site)
                    for v in cols[1:]:
                        se=cov.bse[x.columns.get_loc(v)];b=mod.params[v];m=t.ppf(.975,h.site.nunique()-1)*se
                        slopes.append(dict(pair=pair,omit=omit,spec=spec,model=label,variable=v,n=len(h),sites=h.site.nunique(),
                            beta=b,lower=b-m,upper=b+m,ice_temp_r=h.ice_rate.corr(h.temp_rate)))
            if omit=="none":continue
            test=g[g.region==omit]
            for scope in ["region","past_region"]:
                for start,part in test.groupby("start"):
                    h=train if scope=="region" else train[train.end<=start]
                    x=design(h,models["joint"]) if len(h) else None
                    if len(h)<6 or h.site.nunique()<2 or np.linalg.matrix_rank(x)<4:continue
                    p=part[["pair","region","site","start","end","gap","initial","y"]].copy()
                    p=p.rename(columns={"initial":"start_share"})
                    p["scope"]=scope;p["persistence"]=0
                    for label,cols in models.items():
                        rate=design(part,cols).to_numpy()@fit(h,cols).params.to_numpy()
                        p[label]=(np.clip(p.start_share+p.gap*rate,0,100)-p.start_share)/p.gap
                    pred.append(p)
    preds=pd.concat(pred);save(preds,"predictions.csv");save(slopes,"slopes.csv")
    for (pair,scope),g in preds.groupby(["pair","scope"]):
        for region,h in [("pooled",g),*g.groupby("region")]:
            for model in ["persistence",*models]:
                e=(h[model]-h.y).abs()
                scores.append(dict(pair=pair,scope=scope,region=region,model=model,n=len(h),sites=h.site.nunique(),
                    mae=e.mean(),endpoint_mae=(e*h.gap).mean(),equal_site_mae=e.groupby(h.site).mean().mean()))
    save(scores,"scores.csv")
if __name__=="__main__":main()
