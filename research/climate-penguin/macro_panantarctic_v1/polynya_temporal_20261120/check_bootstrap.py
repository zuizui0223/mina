"""Validate nested-region bootstrap via explicit duplicated region copies."""
import numpy as np
import pandas as pd
from run import CONTROLS, Y, residualize
from chl_models import bootstrap, estimates

rng=np.random.default_rng(3)
d=pd.DataFrame([(f'r{r}',f'r{r}s{s}',t) for r in range(8) for s in range(4) for t in range(6)],columns=['source_region','site_id','season'])
d['region_year']=d.source_region+'_'+d.season.astype(str)
for v in CONTROLS+['P0','P1']:d[v]=rng.normal(size=len(d))
d['C']=.7*d.P0+.2*d.P1+rng.normal(size=len(d))
d[Y]=-1*d.C-.2*d.P0+rng.normal(size=len(d))
cols=CONTROLS+['P0','P1','C',Y];m=residualize(d[cols],d)
draws=rng.integers(0,8,(6,8));fast,valid=bootstrap(m[:,:8],m[:,8],d.source_region.to_numpy(),draws=draws)
assert valid.all()
for j,ids in enumerate(draws):
    copies=[]
    for copy_id,region in enumerate(ids):
        q=d[d.source_region.eq(f'r{region}')].copy()
        q.site_id=q.site_id+'copy'+str(copy_id);q.region_year=q.region_year+'copy'+str(copy_id)
        copies.append(q)
    q=pd.concat(copies,ignore_index=True);z=residualize(q[cols],q)
    slow=estimates(z[:,:8].T@z[:,:8],z[:,:8].T@z[:,8])
    assert np.allclose(slow,fast[j],atol=1e-9)
point=estimates(m[:,:8].T@m[:,:8],m[:,:8].T@m[:,8])
assert point[0]>0 and point[1]<0 and point[3]>0
print('PASS region-copy bootstrap equivalence, pathway sign convention and full contrast units')
