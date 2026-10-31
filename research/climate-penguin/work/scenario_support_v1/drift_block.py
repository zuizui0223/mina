"""Exploratory joint east/north drift test conditional on September air and ice.

Fixed 12-test family; site and year sign flips are separate sensitivity tests,
not a guaranteed multiway-cluster bootstrap. No drift direction is selected.
"""
from pathlib import Path
import hashlib,json,itertools
import numpy as np
import pandas as pd
from statsmodels.stats.multitest import multipletests
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/drift_block_v1';OUT.mkdir(exist_ok=True)
source=ROOT/'outputs/climate_penguin/behavior_ocean_join.csv'
raw=pd.read_csv(source)
mapping={'air':'tmean_9','ice':'near_sic_mean_month9','east':'drift_m9_east_km_day','north':'drift_m9_north_km_day','y':'settlement'}
rng=np.random.default_rng(20261030)
rows=[];cohorts=[];draw_checks=0
for scope in ['all_labels','appendix_consistent']:
    d=raw[raw.drift_m9_screen_pass.eq(True)].copy()
    if scope=='appendix_consistent':d=d[d.appendix_range_consistent]
    d=d.dropna(subset=list(mapping.values()))
    for species,g in d.groupby('species'):
        a=g.groupby(['cam','season_start_year'],as_index=False).agg(**{k:(v,'mean') for k,v in mapping.items()},source_rows=('source_row_1based',lambda x:'|'.join(map(str,sorted(x)))))
        a['scope']=scope;a['species']=species;cohorts.append(a)
        for mode in ['site','site_year']:
            controls=[np.ones(len(a))]+[(a.cam==s).to_numpy(float) for s in sorted(a.cam.unique())[1:]]
            if mode=='site_year':controls += [(a.season_start_year==y).to_numpy(float) for y in sorted(a.season_start_year.unique())[1:]]
            z=np.column_stack(controls+[a.air.to_numpy(),a.ice.to_numpy()/10])
            u,_,_=np.linalg.svd(z,full_matrices=False);q=u[:,:np.linalg.matrix_rank(z)]
            x=a[['east','north']].to_numpy();y=a.y.to_numpy()
            rx=x-q@(q.T@x);ry=y-q@(q.T@y)
            rank=np.linalg.matrix_rank(rx,tol=1e-9)
            rec=dict(scope=scope,species=species,fixed_effects=mode,n=len(a),sites=a.cam.nunique(),years=a.season_start_year.nunique(),drift_rank=rank,residual_df=len(a)-q.shape[1]-rank)
            assert rank==2 and rec['residual_df']>0
            beta=np.linalg.lstsq(rx,ry,rcond=None)[0]
            direct=np.linalg.lstsq(np.column_stack([z,x]),y,rcond=None)[0][-2:]
            assert np.allclose(beta,direct,atol=1e-8)
            h=np.linalg.qr(rx)[0][:,:2]
            statistic=float(np.sum((h.T@ry)**2))
            rec.update(east_coefficient=beta[0],north_coefficient=beta[1],partial_R2=statistic/(ry@ry),statistic=statistic)
            for label,cluster in [('site',a.cam),('year',a.season_start_year)]:
                codes,inv=np.unique(cluster,return_inverse=True);G=len(codes)
                exact=G<=12
                signs=np.array(list(itertools.product([-1,1],repeat=G)),dtype=float) if exact else rng.choice([-1.,1.],size=(9999,G))
                pseudo=ry[:,None]*signs[:,inv].T
                # h is orthogonal to all null-model regressors, so refitting
                # the nuisance model does not change these projected scores.
                stats=np.sum((h.T@pseudo)**2,axis=0)
                count=int((stats>=statistic-1e-10).sum())
                rec[f'{label}_p']=count/len(stats) if exact else (count+1)/(len(stats)+1)
                rec[f'{label}_draws']=len(stats);rec[f'{label}_exact']=exact
                # Check the first draw by explicit null and full regressions.
                yp=q@(q.T@y)+pseudo[:,0]
                null=yp-z@np.linalg.lstsq(z,yp,rcond=None)[0]
                design=np.column_stack([z,x]);full=yp-design@np.linalg.lstsq(design,yp,rcond=None)[0]
                assert np.isclose(null@null-full@full,stats[0],atol=1e-7)
                draw_checks+=1
            rec['sensitivity_max_p']=max(rec['site_p'],rec['year_p'])
            rows.append(rec)
result=pd.DataFrame(rows);assert len(result)==12
for method in ['fdr_bh','fdr_by']:
    result[method]=multipletests(result.sensitivity_max_p,method=method)[1]
result.to_csv(OUT/'joint_tests.csv',index=False)
pd.concat(cohorts,ignore_index=True).to_csv(OUT/'cohort.csv',index=False)
receipt={'status':'exploratory_joint_drift_association','family_size':12,'seed':20261030,'direct_coefficient_checks':12,'explicit_resampled_regression_checks':draw_checks,
 'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'bh_below_005':int((result.fdr_bh<.05).sum()),
 'limitations':['Restricted-null cluster sign flips separately by site and year; maximum is a conservative sensitivity summary, not validated two-way inference',
 'Sign-flip symmetry and small-cluster approximations limit inferential calibration',
 'September means may overlap nominal settlement; calendar origin unresolved',
 'Offshore east/north ice motion is not bird movement, toward-colony transport, or migration aid',
 'Not pooled with or replacing the earlier 216-test marginal family']}
(OUT/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(result[['scope','species','fixed_effects','n','sites','partial_R2','site_p','year_p','sensitivity_max_p','fdr_bh']].to_string(index=False))
