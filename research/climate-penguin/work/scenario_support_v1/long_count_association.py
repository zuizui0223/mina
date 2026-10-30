"""Exploratory fixed 12-comparison family for annual count/September ice changes.

2 distance bands x 2 fixed-effect specifications x 3 declared cohorts. All
positive same-method annual intervals are retained; timing unknown is explicit.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.stats.sandwich_covariance import cov_cluster_2groups
from statsmodels.stats.multitest import multipletests
from scipy.stats import t

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/long_count_seaice_v1'
OUT.mkdir(exist_ok=True)
sources=[ROOT/'outputs/climate_penguin'/x for x in ['historical_count_interval_timing.csv','macro_monthly_seaice_1991_2020.csv']]
d=pd.read_csv(sources[0]); ice=pd.read_csv(sources[1]); ice=ice[ice.month.eq(9)]
assert len(d)==301 and d.species_id.eq('ADPE').all()
assert d.gap.eq(1).all() and d.same_known_method.all() and (d[['n_start','n_end']]>0).all().all()
assert not d.duplicated(['site_id','species_id','start','end']).any()
assert ice.complete_month.all()
for band,name in [(0,'near'),(100,'offshore')]:
    for phase in ['start','end']:
        s=ice[ice.inner_km.eq(band)][['site_id','year','sic_mean']].rename(columns={'year':phase,'sic_mean':name+'_'+phase})
        d=d.merge(s,on=['site_id',phase],validate='many_to_one',how='left')
    d[name+'_change10']=(d[name+'_end']-d[name+'_start'])/10
d['log_growth']=np.log(d.n_end/d.n_start)
assert d[['near_change10','offshore_change10','log_growth']].notna().all().all()
d.to_csv(OUT/'intervals.csv',index=False)
cohorts={'all_annual':d,'timing_supported':d[d.both_all_after_september],
         'timing_supported_without_victoria':d[d.both_all_after_september & d.region.ne('Victoria Land')]}
rows=[]
for scope,a in cohorts.items():
    for feature in ['near_change10','offshore_change10']:
        for mode in ['site','site_year']:
            controls=[np.ones(len(a))]+[(a.site_id==s).astype(float).to_numpy() for s in sorted(a.site_id.unique())[1:]]
            if mode=='site_year':
                controls += [(a.end==y).astype(float).to_numpy() for y in sorted(a.end.unique())[1:]]
            original_z=np.column_stack(controls)
            # Keep the control span, removing redundant dummies before CR1's
            # parameter-count correction (important in sparse site/year panels).
            u,s,_=np.linalg.svd(original_z,full_matrices=False)
            z=u[:,:np.linalg.matrix_rank(original_z)]
            x=a[feature].to_numpy(); y=a.log_growth.to_numpy()
            rx=x-z@np.linalg.lstsq(z,x,rcond=None)[0]; ry=y-z@np.linalg.lstsq(z,y,rcond=None)[0]
            record=dict(scope=scope,feature=feature,fixed_effects=mode,n=len(a),sites=a.site_id.nunique(),
                regions=a.region.nunique(),end_years=a.end.nunique(),status='not_identified',coefficient=np.nan,
                partial_r=np.nan,p=np.nan,ci_low=np.nan,ci_high=np.nan)
            matrix=np.column_stack([z,x]); rank=np.linalg.matrix_rank(matrix)
            record['residual_df']=len(a)-rank
            if np.linalg.norm(rx)>1e-9 and len(a)-rank>0:
                fit=sm.OLS(y,matrix).fit()
                beta=float(rx@ry/(rx@rx))
                assert np.isclose(beta,fit.params[-1],atol=1e-9)
                record.update(coefficient=beta,partial_r=float(np.corrcoef(rx,ry)[0,1]),status='estimated')
                covariance,_,_=cov_cluster_2groups(fit,pd.factorize(a.site_id)[0],pd.factorize(a.end)[0],use_correction=True)
                variance=float(covariance[-1,-1]); df=min(a.site_id.nunique(),a.end.nunique())-1
                record.update(cluster_variance=variance,inference_df=df)
                if variance>0 and df>0:
                    se=np.sqrt(variance); critical=t.ppf(.975,df)
                    record.update(p=float(2*t.sf(abs(beta/se),df)),ci_low=beta-critical*se,ci_high=beta+critical*se)
                else:
                    record['status']='estimated_invalid_cluster_variance'
            rows.append(record)
result=pd.DataFrame(rows)
assert len(result)==12
for method in ['fdr_bh','fdr_by']:
    # Unavailable tests remain in the planned family conservatively as p=1.
    result[method]=multipletests(result.p.fillna(1).to_numpy(),method=method)[1]
result.to_csv(OUT/'associations.csv',index=False)
support=pd.concat([a.groupby('region').size().rename('intervals').reset_index().assign(scope=scope) for scope,a in cohorts.items()])
support.to_csv(OUT/'region_support.csv',index=False)
receipt={'status':'exploratory_association_not_demographic_or_transport_mechanism','family_size':12,
         'input_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
         'cohorts':{k:{'intervals':len(a),'sites':a.site_id.nunique(),'regions':a.region.nunique()} for k,a in cohorts.items()},
         'finite_p_values':int(result.p.notna().sum()),'bh_below_005':int((result.fdr_bh<.05).sum()),
         'by_below_005':int((result.fdr_by<.05).sum()),
         'inference':'CR1 site and end-year two-way clustered covariance; t df=min(clusters)-1; small cluster approximation',
         'limitations':['September concentration change is not melt timing or ice-assisted travel',
         'Growth combines survival, breeding participation, movement and count uncertainty',
         'Timing-supported subset is dominated by Victoria Land; no robust generalization from significance alone',
         'Within-year fixed effects can absorb real regional climate variation as well as nuisance variation',
         'Exploratory new 12-test family does not replace the earlier 216-test settlement family']}
(OUT/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(result[['scope','feature','fixed_effects','n','coefficient','partial_r','p','fdr_bh','fdr_by']].to_string(index=False))
