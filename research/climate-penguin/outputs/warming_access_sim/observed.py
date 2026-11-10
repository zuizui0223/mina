from simulate import baseline, dyads, edges, prior, out, solve
import pandas as pd
import numpy as np
from scipy.optimize import brentq
import simulate
# Separate validation graph paths from the projection integrity check.
simulate.cache=PathCache=simulate.cache/'observed'
PathCache.mkdir(exist_ok=True)
rows=[]
for row in dyads.itertuples():
    spec=np.load(prior/row.key/'spec.npz')
    i,j,k,l=spec['cut'];mask=spec['mask'];obs=baseline[i:j,k:l]
    graph=edges(mask,spec['s'],spec['sink'])
    for beta in [2,-2]:
        ref=solve(graph,obs,beta)
        for year in range(2015,2021):
            target=np.load(prior/f'sic_{year}.npy')[i:j,k:l].astype(float)
            mean=target[mask].mean()
            shift=brentq(lambda v:np.clip(obs[mask]+v,0,100).mean()-mean,-101,101)
            homogeneous=np.clip(obs+shift,0,100)
            assert abs(homogeneous[mask].mean()-mean)<1e-8
            for mode,field in [('observed_pattern',target),('matched_mean',homogeneous)]:
                gain=np.log(ref/solve(graph,field,beta))
                rows.append(dict(pair=row.A+'-'+row.B,year=year,beta=beta,mode=mode,
                    sic_change=mean-obs[mask].mean(),signed_log_contrast=gain[0]-gain[1],absolute_log_contrast=abs(gain[0]-gain[1])))
pd.DataFrame(rows).to_csv(out/'observed_support.csv',index=False)
