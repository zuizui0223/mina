"""Within-colony changes in all observed positive-total paired censuses."""
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import t as student

R=Path(__file__).resolve().parent
def save(frame,name):
    frame.to_csv(R/name,index=False,lineterminator="\n")

def design(g,cols,site_effect=False,calendar=False):
    x=g[cols].copy()
    if calendar:x["midyear"]=(g.start+g.end)/2-2005
    if site_effect:x=pd.concat([x,pd.get_dummies(g.site,drop_first=True,dtype=float)],axis=1)
    return sm.add_constant(x,has_constant="add")

def fit(g,cols,site_effect=False,calendar=False):
    x=design(g,cols,site_effect,calendar)
    if np.linalg.matrix_rank(x)<x.shape[1]:raise ValueError("singular design")
    return sm.OLS(g.y,x).fit()

def main():
    prior=R.parent/"salinity_snow"
    pan=pd.read_csv(prior/"expanded_panel.csv")
    q=pd.read_csv(prior/"expanded_marine_intervals.csv").merge(
        pan[["species_pair","site_id","year","share"]].rename(columns=dict(species_pair="pair",site_id="site",year="start",share="initial")),on=["pair","site","start"],validate="one_to_one")
    assert len(q)==len(pan)-len(pan.groupby(["species_pair","site_id"]))==205
    for col in ["ice","temp","salt","share"]:
        q["y" if col=="share" else col+"_rate"]=q[col]/q.gap
    save(q,"intervals.csv")
    base=["initial","ice_rate","temp_rate"]; full=base+["salt_rate"]
    slopes=[];pred=[]
    for pair,group in q.groupby("pair"):
        for excluded in ["none",*sorted(group.region.unique())]:
            g=group if excluded=="none" else group[group.region!=excluded]
            for name,h,fe,cal in [("all",g,False,False),("annual",g[g.gap==1],False,False),
                                  ("site_and_time",g,True,True)]:
                if len(h)<len(full)+3 or h.site.nunique()<2:continue
                model=fit(h,full,fe,cal); robust=model.get_robustcov_results(cov_type="cluster",groups=h.site)
                idx=list(model.params.index).index("salt_rate")
                se=robust.bse[idx];beta=model.params.iloc[idx];margin=student.ppf(.975,h.site.nunique()-1)*se
                slopes.append(dict(pair=pair,excluded=excluded,spec=name,n=len(h),sites=h.site.nunique(),regions=h.region.nunique(),
                    beta=beta,lower=beta-margin,upper=beta+margin,partial_r2=(fit(h,base,fe,cal).ssr-model.ssr)/fit(h,base,fe,cal).ssr))
            if excluded=="none":continue
            test=group[group.region==excluded]
            for r in test.itertuples():
                for scope,train in [("region",g),("region_past",g[g.end<=r.start])]:
                    if len(train)<len(full)+2 or train.site.nunique()<2:continue
                    xx=design(train,full)
                    if np.linalg.matrix_rank(xx)<xx.shape[1]:continue
                    rec=dict(pair=pair,region=excluded,site=r.site,start=r.start,end=r.end,gap=r.gap,truth=r.y,persistence=0,scope=scope)
                    for label,cols in [("base",base),("salinity",full)]:
                        m=fit(train,cols)
                        rate=np.dot([1]+[getattr(r,c) for c in cols],m.params)
                        rec[label]=(np.clip(r.initial+r.gap*rate,0,100)-r.initial)/r.gap
                    pred.append(rec)
    slopes=pd.DataFrame(slopes);save(slopes,"slopes.csv");pred=pd.DataFrame(pred);save(pred,"predictions.csv")
    sums=[]
    def score(pair,scope,region,h):
        e={k:(h[k]-h.truth).abs() for k in ["persistence","base","salinity"]}
        sums.append(dict(pair=pair,scope=scope,region=region,n=len(h),sites=h.site.nunique(),
            **{k:v.mean() for k,v in e.items()},salt_minus_base=(e["salinity"]-e["base"]).mean(),
            endpoint_salt_minus_base=((e["salinity"]-e["base"])*h.gap).mean()))
    for (pair,scope),h in pred.groupby(["pair","scope"]):
        score(pair,scope,"pooled",h)
        for reg,v in h.groupby("region"):score(pair,scope,reg,v)
    save(pd.DataFrame(sums),"errors.csv")
    # Physical scenario: exact census coordinate only, one projection per site/model/period.
    o=R.parents[1]/"outputs"
    c=pd.read_csv(o/"cmip6_projection_v1/site_model_changes.csv").query("variable_id=='sos'")
    coords=pd.read_csv(o/"comparison_audit/mapppd_unambiguous_site_seasons.csv")[["site_id","latitude","longitude"]].drop_duplicates()
    m=c.merge(coords,on=["site_id","latitude","longitude"]).drop_duplicates(["site_id","source_id","period","experiment_id"])
    cases=q[["site","pair"]].drop_duplicates().merge(m,left_on="site",right_on="site_id")
    assert not cases.duplicated(["pair","site","source_id","period","experiment_id"]).any()
    keep=["pair","site","period","experiment_id","source_id","member_id","grid_cell_id","distance_km","change","change_units"]
    save(cases[keep],"scenario_salt.csv")
    sign=cases.groupby(["pair","site","period","experiment_id"]).change.agg(["count","min","max"]).reset_index()
    assert (sign["count"]==3).all()
    sign["unanimous"]=((sign["max"]<0)|(sign["min"]>0))
    save(sign,"scenario_agreement.csv")
if __name__=="__main__":main()
