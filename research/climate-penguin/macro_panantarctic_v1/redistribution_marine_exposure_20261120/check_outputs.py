"""Independent scalar reconstruction from archived matched data and census records."""
from pathlib import Path
import numpy as np
import pandas as pd

p=Path(__file__).resolve().parent
d=pd.read_csv(p/'matched_rosters.csv');r=pd.read_csv(p/'decomposition.csv')
c=pd.read_csv(p/'observed_counts_used.csv');o=pd.read_csv(p/'omissions.csv')
windows={'long':((1993,2000),(2011,2020)),'polynya':((2004,2010),(2013,2020))}
assert not c.duplicated(['site_id','season']).any()
assert c.groupby('site_id').original_survey_method.nunique().max()==1
for row in r.itertuples():
    q=d[(d.comparison==row.comparison)&(d.radius==row.radius)]
    assert len(q)==row.sites
    n0=sum(q.n0);n1=sum(q.n1)
    early=sum(t.n0*getattr(t,row.variable+'0') for t in q.itertuples())/n0
    late=sum(t.n1*getattr(t,row.variable+'1') for t in q.itertuples())/n1
    # Two alternative sequential paths average to the symmetric components.
    cf01=sum(t.n0*getattr(t,row.variable+'1') for t in q.itertuples())/n0
    cf10=sum(t.n1*getattr(t,row.variable+'0') for t in q.itertuples())/n1
    assert np.allclose([early,late,(cf01-early+late-cf10)/2,(cf10-early+late-cf01)/2],[row.early,row.late,row.local,row.redistribution],atol=1e-10)
    if row.variable in ['salinity','sst_C']:
        v0=row.variable+'0';v1=row.variable+'1'
        assert q.groupby('wet_cell')[[v0,v1]].nunique().max().max()==1
        cells=q.groupby('wet_cell').agg({'n0':'sum','n1':'sum',v0:'first',v1:'first'})
        assert np.isclose((cells.n0*cells[v0]).sum()/cells.n0.sum(),early)
        assert np.isclose((cells.n1*cells[v1]).sum()/cells.n1.sum(),late)
    for t in q.itertuples():
        for j,(start,end) in enumerate(windows[row.comparison]):
            raw=c[(c.site_id==t.site_id)&c.season.between(start,end)]
            assert len(raw)>=2
            assert raw.observed_nest_count.median()==getattr(t,'n'+str(j))
            assert ';'.join(map(str,sorted(raw.season)))==getattr(t,'years'+str(j))
assert np.allclose(o.local+o.redistribution,o.total,atol=1e-10)
m=pd.read_csv(p/'monthly_polynya.csv')
assert m.coverage.ge(.8).all() and m['mean'].between(0,1).all()
assert not m.duplicated(['site_id','radius','year','month']).any()
print('PASS independent decomposition paths; census medians/years/methods; shared-cell aggregation; all omissions; native monthly coverage')
