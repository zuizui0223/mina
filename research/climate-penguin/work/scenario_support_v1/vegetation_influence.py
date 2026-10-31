"""Frozen vegetation associations: region/block deletion and count support."""
from pathlib import Path
import json,hashlib
import numpy as np
import pandas as pd

root=Path(__file__).resolve().parents[2]/'outputs'
src=root/'vegetation_response_v1/site_species_cohort.csv'
spec=root/'vegetation_response_v1/associations.csv'
out=root/'vegetation_influence_v1';out.mkdir(exist_ok=True)
d=pd.read_csv(src);specs=pd.read_csv(spec);records=[]

def fit(g,endpoint,adjustment):
    g=g.dropna(subset=['log1p_mapped_area_m2',endpoint,'region'])
    if not len(g):return dict(n=0,regions=0,r=np.nan,slope=np.nan,df=0)
    z=pd.get_dummies(g.region,dtype=float).to_numpy() if adjustment=='region_fixed_effects' else np.ones((len(g),1))
    x=g.log1p_mapped_area_m2.to_numpy();y=g[endpoint].to_numpy()
    v=np.column_stack([x,y]);res=v-z@np.linalg.lstsq(z,v,rcond=None)[0]
    xx=res[:,0]@res[:,0];yy=res[:,1]@res[:,1]
    rank=np.linalg.matrix_rank(np.column_stack([z,x]));df=len(g)-rank
    valid=xx>1e-12 and yy>1e-12 and df>0
    r=res[:,0]@res[:,1]/np.sqrt(xx*yy) if valid else np.nan
    slope=res[:,0]@res[:,1]/xx if valid else np.nan
    if valid:assert np.isclose(slope,np.linalg.lstsq(np.column_stack([z,x]),y,rcond=None)[0][-1],atol=1e-8)
    return dict(n=len(g),regions=g.region.nunique(),r=r,slope=slope,df=df)

for s in specs.itertuples():
    a=d[d.species_id==s.species].copy()
    if s.cohort=='positive_detections':a=a[a.positive_mapped_detection]
    a=a.dropna(subset=[s.endpoint,'log1p_mapped_area_m2'])
    key=dict(cohort=s.cohort,species=s.species,endpoint=s.endpoint,adjustment=s.adjustment)
    full=fit(a,s.endpoint,s.adjustment)
    assert full['n']==s.n and np.isclose(full['r'],s.pearson_r,atol=1e-9)
    records.append(dict(**key,comparison='full',removed='',**full))
    for axis in ['region','spatial_block']:
        for val in sorted(a[axis].unique()):
            records.append(dict(**key,comparison='delete_'+axis,removed=val,**fit(a[a[axis]!=val],s.endpoint,s.adjustment)))
    for label,mask in [('at_least_3_seasons',a.observed_seasons.ge(3)),('ground_only',a.all_counts_ground)]:
        records.append(dict(**key,comparison=label,removed='',**fit(a[mask],s.endpoint,s.adjustment)))
    # All tied largest sites are removed; this is a declared sensitivity, not trimming to improve r.
    records.append(dict(**key,comparison='remove_largest_count',removed='',**fit(a[a.count_median<a.count_median.max()],s.endpoint,s.adjustment)))
t=pd.DataFrame(records);t.to_csv(out/'comparisons.csv',index=False)
keys=['cohort','species','endpoint','adjustment','comparison']
summary=t.groupby(keys).agg(fits=('r','size'),estimable=('r','count'),r_min=('r','min'),r_max=('r','max'),minimum_n=('n','min'),maximum_n=('n','max')).reset_index()
summary.to_csv(out/'summary.csv',index=False)
v=dict(passed=True,original_specs=len(specs),fits=len(t),estimable=int(t.r.notna().sum()),
       hashes={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [src,spec]},
       limits=['Deletion ranges are not confidence intervals or significance tests',
               'Static vegetation detection area, not annual greening or habitat selection',
               'Subset changes also change geography and observation support'])
(out/'validation.json').write_text(json.dumps(v,indent=2)+'\n');print(json.dumps(v))
print(summary[(summary.cohort=='positive_detections')&(summary.adjustment=='region_fixed_effects')].to_string(index=False))
