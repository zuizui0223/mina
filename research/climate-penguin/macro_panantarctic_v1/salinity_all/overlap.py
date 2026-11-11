"""Annual same-colony overlap check, unrestricted ice sign, without regression extrapolation."""
from itertools import product
from scipy.optimize import linear_sum_assignment
import numpy as np,pandas as pd
from analyze import R,save
q=pd.read_csv(R/"intervals.csv").query("gap==1")
rows=[]
for (pair,site),g in q.groupby(["pair","site"]):
    a=g[g.salt>0].reset_index(drop=True);b=g[g.salt<0].reset_index(drop=True)
    if a.empty or b.empty:continue
    for ice_tol,temp_tol in [(2,.1),(5,.2),(10,.4)]:
        ice=abs(a.ice.to_numpy()[:,None]-b.ice.to_numpy())
        temp=abs(a.temp.to_numpy()[:,None]-b.temp.to_numpy())
        cost=np.where((ice<=ice_tol)&(temp<=temp_tol),ice/ice_tol+temp/temp_tol,1e6)
        for i,j in zip(*linear_sum_assignment(cost)):
            if cost[i,j]>=1e6:continue
            x=a.iloc[i];y=b.iloc[j]
            rows.append(dict(pair=pair,site=site,region=x.region,ice_tol=ice_tol,temp_tol=temp_tol,
                up_start=x.start,down_start=y.start,up_ice=x.ice,down_ice=y.ice,up_temp=x.temp,down_temp=y.temp,
                up_salt=x.salt,down_salt=y.salt,up_share=x.share,down_share=y.share,difference=x.share-y.share))
d=pd.DataFrame(rows);save(d,"annual_matches.csv")
print(d.groupby(["pair","ice_tol"]).agg(n=("site","size"),sites=("site","nunique"),regions=("region","nunique"),avg=("difference","mean"),median=("difference","median")))
