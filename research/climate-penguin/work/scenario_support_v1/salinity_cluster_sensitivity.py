"""Restricted-null sign-flip sensitivity for the frozen 48 salinity specs.

Separate site/year tests, not calibrated joint two-way inference.
"""
from pathlib import Path
import argparse,hashlib,itertools,json
import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests

root=Path(__file__).resolve().parents[2]/'outputs'
parser=argparse.ArgumentParser();parser.add_argument('--group-by',choices=['cam','ocean_grid'],default='cam');args=parser.parse_args()
out=root/('salinity_cluster_sensitivity_v1' if args.group_by=='cam' else 'salinity_grid_cluster_v1');out.mkdir(exist_ok=True)
source=root/'relationship_response_v1/cohort.csv'
spec_source=root/'salinity_sensitivity_v1/specifications.csv'
d=pd.read_csv(source);specs=pd.read_csv(spec_source)
grid_source=root/'ocean_grid_replication_v1/observation_cells.csv'
if args.group_by=='ocean_grid':
    mapping=pd.read_csv(grid_source)
    assert mapping.n_cells.eq(1).all()
    d=d.merge(mapping[['scope','species','cam','year','cells']],on=['scope','species','cam','year'],validate='one_to_one')
    assert d.cells.notna().all()
spatial_label='site' if args.group_by=='cam' else 'grid'
controls={'none':[],'ice':['ice10'],'ice_water':['ice10','waterC'],
          'ice_water_air':['ice10','waterC','airC']}
rng=np.random.default_rng(20261030);rows=[];checks=0
for s in specs.itertuples():
    a=d[(d.scope==s.scope)&(d.species==s.species)].copy()
    z=pd.get_dummies(a.cam,dtype=float).to_numpy()
    if s.mode=='site_year':z=np.column_stack([z,pd.get_dummies(a.year,drop_first=True,dtype=float)])
    if controls[s.controls]:z=np.column_stack([z,a[controls[s.controls]].to_numpy()])
    u,_,_=np.linalg.svd(z,full_matrices=False);q=u[:,:np.linalg.matrix_rank(z)]
    x=a.salt01.to_numpy();y=a.y.to_numpy()
    rx=x-q@(q.T@x);ry=y-q@(q.T@y)
    h=rx/np.linalg.norm(rx);stat=float((h@ry)**2)
    beta=rx@ry/(rx@rx);r=rx@ry/np.sqrt((rx@rx)*(ry@ry))
    design=np.column_stack([z,x])
    assert np.linalg.matrix_rank(design)==q.shape[1]+1
    assert np.isclose(beta,s.coefficient_per_01,atol=1e-8)
    assert np.isclose(r,s.partial_r,atol=1e-8)
    rec=dict(scope=s.scope,species=s.species,mode=s.mode,controls=s.controls,
             n=len(a),sites=a.cam.nunique(),years=a.year.nunique(),partial_r=r,
             coefficient_per_01=beta,statistic=stat)
    spatial=a.cam if args.group_by=='cam' else a.cells
    rec['spatial_clusters']=spatial.nunique()
    for name,cluster in [(spatial_label,spatial),('year',a.year)]:
        labels,inv=np.unique(cluster,return_inverse=True);G=len(labels)
        exact=G<=12
        signs=np.array(list(itertools.product([-1.,1.],repeat=G))) if exact else rng.choice([-1.,1.],size=(9999,G))
        pseudo=ry[:,None]*signs[:,inv].T
        values=(h@pseudo)**2
        exceed=int(np.sum(values>=stat-1e-10))
        rec[name+'_p']=exceed/len(values) if exact else (exceed+1)/(len(values)+1)
        rec[name+'_enumerated']=exact;rec[name+'_draws']=len(values)
        for i in [0,len(values)//2,len(values)-1]:
            yp=q@(q.T@y)+pseudo[:,i]
            null=yp-z@np.linalg.lstsq(z,yp,rcond=None)[0]
            full=yp-design@np.linalg.lstsq(design,yp,rcond=None)[0]
            assert np.isclose(null@null-full@full,values[i],atol=1e-7)
            checks+=1
    rec['sensitivity_max_p']=max(rec[spatial_label+'_p'],rec['year_p']);rows.append(rec)
t=pd.DataFrame(rows);assert len(t)==48
for method in ['fdr_bh','fdr_by']:
    t[method]=multipletests(t.sensitivity_max_p,method=method)[1]
t.to_csv(out/'tests.csv',index=False)
v=dict(status='exploratory_cluster_sign_flip_sensitivity',spatial_group=args.group_by,family_size=48,seed=20261030,
       frozen_coefficient_and_correlation_matches=48,explicit_pseudo_regression_checks=checks,
       max_p_below_005=int(t.sensitivity_max_p.lt(.05).sum()),
       bh_below_005=int(t.fdr_bh.lt(.05).sum()),by_below_005=int(t.fdr_by.lt(.05).sum()),
       hashes={p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in ([source,spec_source]+([grid_source] if args.group_by=='ocean_grid' else []))},
       limits=['Separate site/year sign flips do not guarantee valid joint two-way inference',
               'Enumeration is exact over sign assignments, not proof of exact inferential calibration',
               'Nuisance estimation, cluster symmetry, few years and shared ocean grids limit calibration',
               '48-test family is exploratory and does not replace earlier broader families'])
(out/'validation.json').write_text(json.dumps(v,indent=2)+'\n')
print(json.dumps(v));print(t[(t.scope=='all_source_labels')&(t.controls=='ice_water_air')][['species','mode','partial_r',spatial_label+'_p','year_p','sensitivity_max_p','fdr_bh']].to_string(index=False))
