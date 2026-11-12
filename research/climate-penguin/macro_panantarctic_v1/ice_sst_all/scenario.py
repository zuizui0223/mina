"""Physical forcing changes plus a conditional response contrast; not a nest-share forecast."""
from pathlib import Path
import numpy as np,pandas as pd
from scipy.spatial import Delaunay
from relations import R,Q,save
def main():
    src=pd.concat([pd.read_csv(f) for f in (R/"forcing").glob("*.csv") if not f.name.startswith("support_") and f.name.endswith(("_tos.csv","_siconc.csv"))],ignore_index=True)
    keys=["source_id","member_id","site_id","variable_id"]
    base=src[src.experiment_id=="historical"][keys+["seasonal_mean","grid_cell_id"]].rename(columns={"seasonal_mean":"baseline"})
    proj=src[src.experiment_id!="historical"].merge(base,on=keys+["grid_cell_id"],validate="many_to_one")
    assert len(proj)==600 and (src.complete_years==20).all()
    proj["delta"]=proj.seasonal_mean-proj.baseline
    save(proj,"physical.csv")
    units=proj.pivot(index=["source_id","member_id","site_id","experiment_id","period"],columns="variable_id",values="delta").reset_index()
    slopes=pd.read_csv(R/"slopes.csv").query("spec=='full' and model=='joint'").pivot(index=["pair","omit"],columns="variable",values="beta")
    output=[]
    for pair,g in Q.groupby("pair"):
        hull=Delaunay(g[["ice","temp"]].drop_duplicates().to_numpy())
        for row in units[units.site_id.isin(g.site)].itertuples():
            b=slopes.loc[(pair,"none")]
            ice=b.ice_rate*row.siconc;sst=b.temp_rate*row.tos
            held=slopes.loc[pair].drop("none");loo=held.ice_rate*row.siconc+held.temp_rate*row.tos
            output.append(dict(pair=pair,site=row.site_id,model=row.source_id,ssp=row.experiment_id,period=row.period,
                ice=row.siconc,sst=row.tos,within_historical_delta_hull=hull.find_simplex([[row.siconc,row.tos]])[0]>=0,
                ice_component=ice,sst_component=sst,conditional_net=ice+sst,loo_min=loo.min(),loo_max=loo.max()))
    d=pd.DataFrame(output);save(d,"conditional_contrasts.csv")
    for pair,g in d.groupby("pair"):
        print(pair,len(g),"within hull",g.within_historical_delta_hull.sum(),"opposing",((g.ice_component*g.sst_component)<0).sum())
        v=g.groupby(["site","ssp","period"]).conditional_net.agg(["min","max"]);print("net signs agree",((v["min"]>0)|(v["max"]<0)).sum(),"/",len(v))
    print(units.groupby(["experiment_id","period"])[["siconc","tos"]].agg(["min","median","max"]).round(3))
    print("joint loss and warm",((units.siconc<0)&(units.tos>0)).sum(),len(units))
if __name__=="__main__":main()
