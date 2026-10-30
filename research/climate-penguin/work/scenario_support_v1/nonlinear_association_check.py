"""One quadratic term at a time on the fixed four-environment cohort.

Descriptive shape sensitivity, not significance selection or future extrapolation.
"""
from pathlib import Path
import hashlib,json
import numpy as np
import pandas as pd
import statsmodels.api as sm
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/nonlinear_association_v1'
F=['airC','ice10','salt01','waterC']


def fit(a,mode,feature,center,scale):
    z=pd.get_dummies(a.cam,dtype=float).to_numpy()
    if mode=='site_year':z=np.column_stack([z,pd.get_dummies(a.year,drop_first=True,dtype=float)])
    x=(a[F].to_numpy()-center)/scale
    i=F.index(feature);base=np.column_stack([z,x]);q=x[:,i]**2
    design=np.column_stack([base,q]);rank=np.linalg.matrix_rank(design)
    if rank!=np.linalg.matrix_rank(base)+1 or len(a)<=rank:return dict(status='not_identified')
    linear=sm.OLS(a.y.to_numpy(),base).fit();full=sm.OLS(a.y.to_numpy(),design).fit()
    rq=q-base@np.linalg.lstsq(base,q,rcond=None)[0]
    ry=a.y.to_numpy()-base@np.linalg.lstsq(base,a.y,rcond=None)[0]
    assert np.isclose(rq@ry/(rq@rq),full.params[-1],atol=1e-7)
    gain=(linear.ssr-full.ssr)/linear.ssr
    assert gain>=-1e-10
    lo,hi=np.quantile(x[:,i],[.1,.9])
    b1=full.params[-5+i];b2=full.params[-1]
    turning=-b1/(2*b2) if abs(b2)>1e-12 else np.nan
    return dict(status='estimated',curvature=float(b2),linear_standardized=float(b1),
                partial_r2=float(gain),slope_p10=float((b1+2*b2*lo)/scale[i]),
                slope_p90=float((b1+2*b2*hi)/scale[i]),
                turn_in_central_range=bool(lo<turning<hi),
                turning_value=float(turning*scale[i]+center[i]),residual_df=len(a)-rank)


def main():
    OUT.mkdir(exist_ok=True)
    src=ROOT/'outputs/relationship_response_v1/cohort.csv';d=pd.read_csv(src)
    rows=[];deletions=[];site_deletions=[]
    for (scope,sp),a in d.groupby(['scope','species']):
        center=a[F].mean().to_numpy();scale=a[F].std().to_numpy()
        for mode in ['site','site_year']:
            for feature in F:
                key=dict(scope=scope,species=sp,mode=mode,feature=feature)
                r=fit(a,mode,feature,center,scale);assert r['status']=='estimated'
                fits=[]
                for year in sorted(a.year.unique()):
                    q=fit(a[a.year!=year],mode,feature,center,scale)
                    deletions.append(dict(**key,deleted_year=int(year),**q))
                    if q['status']=='estimated':fits.append(q)
                r.update(key,n=len(a),sites=a.cam.nunique(),years=a.year.nunique(),
                         valid_year_deletions=len(fits),
                         curvature_delete_min=min(q['curvature'] for q in fits),
                         curvature_delete_max=max(q['curvature'] for q in fits),
                         r2_delete_min=min(q['partial_r2'] for q in fits),
                         r2_delete_max=max(q['partial_r2'] for q in fits))
                site_fits=[]
                for cam in sorted(a.cam.unique()):
                    q=fit(a[a.cam!=cam],mode,feature,center,scale)
                    site_deletions.append(dict(**key,deleted_cam=cam,**q))
                    if q['status']=='estimated':site_fits.append(q)
                r.update(valid_site_deletions=len(site_fits),
                         curvature_site_delete_min=min(q['curvature'] for q in site_fits),
                         curvature_site_delete_max=max(q['curvature'] for q in site_fits))
                rows.append(r)
    t=pd.DataFrame(rows);assert len(t)==48
    t.to_csv(OUT/'shape_sensitivity.csv',index=False)
    pd.DataFrame(deletions).to_csv(OUT/'year_deletions.csv',index=False)
    pd.DataFrame(site_deletions).to_csv(OUT/'site_deletions.csv',index=False)
    (OUT/'validation.json').write_text(json.dumps(dict(status='passed_descriptive_only',
        specifications=len(t),year_deletions=len(deletions),site_deletions=len(site_deletions),input_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
        limits=['Added quadratic term can only improve in-sample fit; no p-value or model-selection claim',
                'Shared species-level curve with site effects; not a separate within-site optimum',
                'Turning point not ecological optimum; no future quadratic prediction',
                'Full-cohort scaling held fixed in deletions; not out-of-sample validation']),indent=2)+'\n')
    print(t.query("scope=='all_source_labels'")[[
        'species','mode','feature','partial_r2','curvature','curvature_delete_min','curvature_delete_max','turn_in_central_range']].to_string(index=False))


if __name__=='__main__':main()
