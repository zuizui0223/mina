from itertools import product
import pandas as pd
import numpy as np
from scipy.optimize import linear_sum_assignment
from acquire import R,S

import sys
extended="--expanded" in sys.argv
prefix="expanded_" if extended else ""
if extended:
    d=pd.read_csv(R/"expanded_panel.csv")
else:
    c=pd.read_csv(next(S.glob("observed_2species*.csv")))
    e=pd.read_csv(next(S.glob("original_GLORYS*.csv")))
    d=c.merge(e,on=["site_id","year","source_region","source_250km_block"],validate="many_to_one")
    assert len(d)==len(c)==39
    d["share"]=100*d.nests_source_gentoo/(d.nests_source_gentoo+d.nests_source_baseline_species)
rows=[]
for (pair,site),t in d.groupby(["species_pair","site_id"]):
    t=t.sort_values("year")
    for a,b in zip(t.itertuples(),t.iloc[1:].itertuples()):
        rows.append(dict(pair=pair,site=site,region=a.source_region,start=a.year,end=b.year,gap=b.year-a.year,
            ice=b.source_SIC_pp-a.source_SIC_pp,salt=b.source_glorys_salinity-a.source_glorys_salinity,
            temp=b.source_glorys_thetao_C-a.source_glorys_thetao_C,share=b.share-a.share))
q=pd.DataFrame(rows)
q.to_csv(R/(prefix+"marine_intervals.csv"),index=False,lineterminator="\n")
matches=[]; support=[]
for pair,t in q[q.ice<0].groupby("pair"):
    for scope,annual,cal in product(["site","region","pooled"],[True,False],[2,5,10]):
        f=t[t.gap==1] if annual else t
        a=f[f.salt>0].reset_index(drop=True);b=f[f.salt<0].reset_index(drop=True)
        # Maximal cardinality then minimum total difference, no reused intervals per design.
        cost=np.full((len(a),len(b)),1e6)
        for i,x in a.iterrows():
            for j,y in b.iterrows():
                dist=abs(x.ice-y.ice)
                if x.gap==y.gap and (scope=="pooled" or x[scope]==y[scope]) and dist<=cal:cost[i,j]=dist
        ix,jx=linear_sum_assignment(cost)
        deltas=[]
        for i,j in zip(ix,jx):
            if cost[i,j]>cal:continue
            x,y=a.iloc[i],b.iloc[j];delta=x.share-y.share;deltas.append(delta)
            matches.append(dict(pair=pair,scope=scope,annual=annual,cal=cal,ice_mismatch=cost[i,j],
                high_site=x.site,high_start=x.start,high_end=x.end,high_share=x.share,
                low_site=y.site,low_start=y.start,low_end=y.end,low_share=y.share,difference=delta))
        support.append(dict(pair=pair,scope=scope,annual=annual,cal=cal,up=len(a),down=len(b),matched=len(deltas),
            mean_difference=np.mean(deltas) if deltas else None))
pd.DataFrame(matches).to_csv(R/(prefix+"marine_matches.csv"),index=False,lineterminator="\n")
pd.DataFrame(support).to_csv(R/(prefix+"marine_support.csv"),index=False,lineterminator="\n")
print(pd.DataFrame(support).query("cal==5").to_string(index=False))
