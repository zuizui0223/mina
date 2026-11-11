"""Same-place annual matches with additional constraints on background drift and warming."""
from itertools import product
import numpy as np,pandas as pd
from scipy.optimize import linear_sum_assignment
from acquire import R
q=pd.read_csv(R/"expanded_marine_intervals.csv").query("ice<0 and gap==1")
rows=[]
for (pair,site),g in q.groupby(["pair","site"]):
    a=g[g.salt>0];b=g[g.salt<0]
    for near,temperature in product([False,True],[False,True]):
        cost=np.full((len(a),len(b)),1e6)
        for i,x in enumerate(a.itertuples()):
            for j,y in enumerate(b.itertuples()):
                if abs(x.ice-y.ice)>5:continue
                if near and not 2<=abs(x.start-y.start)<=5:continue
                if temperature and abs(x.temp-y.temp)>0.2:continue
                cost[i,j]=abs(x.ice-y.ice)
        for i,j in zip(*linear_sum_assignment(cost)):
            if cost[i,j]>5:continue
            x,y=a.iloc[i],b.iloc[j]
            rows.append(dict(pair=pair,site=site,nonoverlap_2_to_5years=near,temperature_within_02C=temperature,
                             high_start=x.start,low_start=y.start,ice_mismatch=cost[i,j],difference=x.share-y.share))
t=pd.DataFrame(rows);t.to_csv(R/"marine_temporal_sensitivity.csv",index=False,lineterminator="\n")
print(t.groupby(["pair","nonoverlap_2_to_5years","temperature_within_02C"]).difference.agg(["count","mean"]))
