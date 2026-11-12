from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment
R=Path(__file__).resolve().parent
def save(rows,name):
    pd.DataFrame(rows).to_csv(R/name,index=False,lineterminator="\n")
def share(g,a):return 100*g/(g+a)
def main():
    prior=R.parent/"salinity_snow"
    t=pd.read_csv(prior/"expanded_panel.csv").query("species_pair=='ADPE__GEPE'")
    d=pd.read_csv(prior/"expanded_marine_intervals.csv").query("pair=='ADPE__GEPE' and gap==1 and ice<0").copy()
    for end in ["start","end"]:
        e=t[["site_id","year","GEPE","ADPE"]].rename(columns={"site_id":"site","year":end,"GEPE":"g_"+end,"ADPE":"a_"+end})
        d=d.merge(e,on=["site",end],validate="one_to_one")
    assert len(d)==28
    g0,g1,a0,a1=(d[v] for v in ["g_start","g_end","a_start","a_end"])
    d["delta_g"]=g1-g0;d["delta_a"]=a1-a0
    # Average the two orders of changing species counts in the observed share.
    d["g_component"]=(share(g1,a0)-share(g0,a0)+share(g1,a1)-share(g0,a1))/2
    d["a_component"]=d.share-d.g_component
    assert np.allclose(d.a_component,(share(g0,a1)-share(g0,a0)+share(g1,a1)-share(g1,a0))/2)
    save(d,"annual_ice_loss.csv")
    pairs=[];summary=[]
    for ice_tol,cut,allow_cooling in [(5,.2,False),(2,.2,False),(10,.2,False),(5,.1,False),(5,.3,False),(5,.2,True)]:
        run=[]
        for site,v in d.groupby("site"):
            hot=v[v.temp>cut];low=v[(v.temp<=cut)&((v.temp>=0)|allow_cooling)]
            dist=np.abs(hot.ice.to_numpy()[:,None]-low.ice.to_numpy())
            dt=hot.temp.to_numpy()[:,None]-low.temp.to_numpy()
            cost=np.where((dist<=ice_tol)&(dt>=cut),dist,1e6)
            for i,j in zip(*linear_sum_assignment(cost)):
                if cost[i,j]>ice_tol:continue
                x,y=hot.iloc[i],low.iloc[j]
                row=dict(ice_tol=ice_tol,cut=cut,allow_cooling=allow_cooling,site=site,region=x.region,hot_start=x.start,mild_start=y.start)
                for col in ["ice","temp","share","delta_g","delta_a","g_component","a_component"]:
                    row["hot_"+col]=x[col];row["mild_"+col]=y[col];row["diff_"+col]=x[col]-y[col]
                pairs.append(row);run.append(row)
        summary.append(dict(ice_tol=ice_tol,cut=cut,allow_cooling=allow_cooling,n=len(run),sites=len({s["site"] for s in run}),difference=np.mean([s["diff_share"] for s in run]) if run else None))
    save(pairs,"matched.csv");save(summary,"sensitivity.csv")
    f=pd.read_csv(R.parent/"ice_sst_all/conditional_contrasts.csv").query("pair=='ADPE__GEPE'")
    rows=[];coverage=[]
    for ice_tol,temp_tol in [(5,.2),(2,.1),(10,.4)]:
        for scenario in f.itertuples():
            g=d[(d.site==scenario.site)&(d.temp>0)&((d.ice-scenario.ice).abs()<=ice_tol)&((d.temp-scenario.sst).abs()<=temp_tol)]
            rec=dict(ice_tol=ice_tol,temp_tol=temp_tol,site=scenario.site,model=scenario.model,ssp=scenario.ssp,period=scenario.period,ice=scenario.ice,sst=scenario.sst)
            coverage.append(dict(rec,analogues=len(g)))
            for v in g.itertuples():rows.append(dict(rec,start=v.start,end=v.end,obs_ice=v.ice,obs_sst=v.temp,obs_share=v.share))
    save(rows,"analogue_links.csv");save(coverage,"all_scenarios.csv")
    print(pd.DataFrame(summary));print(pd.DataFrame(pairs).query("ice_tol==5 and cut==.2 and not allow_cooling").T)
    a=pd.DataFrame(rows).query("ice_tol==5")
    print(a.to_string(index=False))
if __name__=="__main__":main()
