"""Bounded historical size vs subsequent breeding trends (descriptive only).
Usage: python historical_size_climate.py count_artifact.zip marine_artifact.zip out_dir
"""
import argparse, hashlib, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

COUNT_PIN='add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a'
MARINE_PIN='64a8e9832e254171139d78bb22351d6c9a3acf490356931b2635ed5b108d94b5'
KEY=['site_id','species']
GROUP=['species','source_region']
X=['historical_log1p_median_nests','delta_sic_pp','delta_thetao_C']
Y='later_log1p_nest_slope_per_decade'

def checked_zip(path,pin):
    if hashlib.sha256(path.read_bytes()).hexdigest()!=pin:raise ValueError('source archive digest mismatch')
    z=zipfile.ZipFile(path)
    if z.testzip() is not None:raise ValueError('source archive CRC')
    return z

def support(p):
    return dict(n_series=len(p),n_sites=int(p.site_id.nunique()),n_regions=int(p.source_region.nunique()),n_blocks=int(p.block.nunique()),n_strata=int(p.groupby(GROUP).ngroups),n_wet_cells=int(p.wet_cell.dropna().nunique()),n_two_visit_later_series=int((p.n_eval==2).sum()),by_species={str(k):int(v) for k,v in p.species.value_counts().items()})

def prepare(count_path,marine_path):
    with checked_zip(count_path,COUNT_PIN) as z:
        c=pd.read_csv(z.open('source_observed_2456.csv'));s=pd.read_csv(z.open('panantarctic_595_site_inventory.csv'))
    with checked_zip(marine_path,MARINE_PIN) as z:
        m=pd.read_csv(z.open('original_588_site_1993_2020_actual_SIC_SSS_SST_PC1.csv'))
    assert len(c)==2456 and len(s)==595 and len(m)==16464 and m.site_id.nunique()==588
    assert not c.duplicated(KEY+['season']).any() and s.site_id.is_unique and not m.duplicated(['site_id','year']).any()
    assert c.groupby(KEY).original_survey_method.nunique().eq(1).all() and c.groupby(KEY).ngroups==707
    assert c.observed_nest_count.ge(0).all() and (c.observed_nest_count%1==0).all()
    assert c.loc[c.observed_nest_count.eq(0),'observed_zero_is_actual_source_count'].astype(str).str.lower().eq('true').all()
    assert c.not_recorded_species_or_year_is_not_an_absence.astype(str).str.lower().eq('true').all()
    assert c.merge(s[['site_id','source_region']],on='site_id',validate='many_to_one').eval('source_region_x == source_region_y').all()
    assert set(m.year)==set(range(1993,2021)) and m.groupby('site_id').year.nunique().eq(28).all()
    assert m[['mean_source_SIC_pp','mean_GLORYS_thetao_C']].notna().all().all()
    assert m.mean_source_SIC_pp.between(0,100).all() and np.isfinite(m.mean_GLORYS_thetao_C).all()
    assert m.original_source_4_GLORYS_months.eq(4).all() and m.original_source_4_OSISAF_months.eq(4).all()
    assert m.groupby('site_id')[['GLORYS_cell_y','GLORYS_cell_x','source_region','source_250km_block']].nunique().eq(1).all().all()
    site=s[['site_id','source_region','polar_250km_fixed_grid_block']].rename(columns={'polar_250km_fixed_grid_block':'block'})
    a=c[c.season.between(1993,2010)]; b=c[c.season.between(2011,2020)]
    hist=a.groupby(KEY).agg(n_history=('season','size'),history_first=('season','min'),history_last=('season','max'),history_median=('observed_nest_count','median'))
    later=b.groupby(KEY).agg(n_eval=('season','size'),eval_first=('season','min'),eval_last=('season','max'))
    p=hist.join(later,how='inner').reset_index();p['eval_span']=p.eval_last-p.eval_first
    p=p[(p.n_history>=2)&(p.n_eval>=2)].merge(site,on='site_id',validate='many_to_one')
    m=m[m.year.between(2001,2020)].copy();m['period']=(m.year>=2011).astype(int)
    fields=['mean_source_SIC_pp','mean_GLORYS_thetao_C']
    mu=m.groupby(['site_id','period'])[fields].mean().unstack('period')
    diff=pd.DataFrame({'delta_sic_pp':mu[(fields[0],1)]-mu[(fields[0],0)],'delta_thetao_C':mu[(fields[1],1)]-mu[(fields[1],0)]}).reset_index()
    wet=m[['site_id','GLORYS_cell_y','GLORYS_cell_x','source_region','source_250km_block']].drop_duplicates()
    assert wet.site_id.is_unique
    wet['wet_cell']=wet.GLORYS_cell_y.astype(str)+':'+wet.GLORYS_cell_x.astype(str)
    check=wet.merge(site,on='site_id',validate='one_to_one');assert (check.source_region_x==check.source_region_y).all() and (check.source_250km_block==check.block).all()
    p=p.merge(diff,on='site_id',how='left',validate='many_to_one').merge(wet[['site_id','wet_cell']],on='site_id',how='left',validate='many_to_one')
    p['climate_complete']=p[X[1:]].notna().all(axis=1)
    p['span5']=p.eval_span>=5
    p['historical_log1p_median_nests']=np.log1p(p.history_median)
    def slope(g):
        y=g.season.to_numpy(float);n=np.log1p(g.observed_nest_count.to_numpy(float)); y=y-y.mean()
        if len(y)<2:return np.nan
        return 10*(y@(n-n.mean()))/(y@y)
    later_slope=b.groupby(KEY)[['season','observed_nest_count']].apply(slope).rename(Y).reset_index()
    p=p.merge(later_slope,on=KEY,validate='one_to_one')
    q=p[p.span5 & p.climate_complete].copy()
    q['stratum_size']=q.groupby(GROUP).site_id.transform('size')
    q['primary']=q.stratum_size>=3
    primary=q[q.primary].copy()
    assert (len(p),int(p.span5.sum()),len(q),len(primary))==(81,59,53,51)
    structure=dict(n_count_rows=len(c),n_sites=len(s),n_series=c.groupby(KEY).ngroups,n_climate_rows=16464,n_climate_sites=588,
        history2_eval2=support(p),history2_eval2_span5=support(p[p.span5]),climate_matched_span5=support(q),primary=support(primary),
        excluded_small_strata=q[~q.primary][KEY+GROUP[1:]].to_dict('records'),
        primary_strata=[dict(species=k[0],region=k[1],**support(g)) for k,g in primary.groupby(GROUP)])
    return p,q,primary,structure

def centered(p):
    p=p.copy();n=p.groupby(GROUP).site_id.transform('size');p=p[n>=3].copy()
    if len(p)<12 or p.groupby(GROUP).ngroups<2:return None
    g=p.groupby(GROUP);w=1/g.site_id.transform('size').to_numpy(float);w=w/w.sum()
    x=p[X].to_numpy(float)-g[X].transform('mean').to_numpy(float);y=p[Y].to_numpy(float)-g[Y].transform('mean').to_numpy(float)
    return p,w,x,y

def solve(centered_panel,scale=None):
    if centered_panel is None:return {'status':'BLOCKED_SUPPORT'}
    p,w,x,y=centered_panel
    if scale is None:scale=np.sqrt(w@(x*x))
    if np.any(scale<=0) or not np.isfinite(scale).all():return {'status':'BLOCKED_SCALE'}
    x=x/scale; A=x*np.sqrt(w)[:,None]; B=y*np.sqrt(w); rank=np.linalg.matrix_rank(A);cond=float(np.linalg.cond(A));var=float(B@B)
    if rank<3 or cond>30 or var<=0:return dict(status='BLOCKED_RANK_CONDITION_OR_RESPONSE',rank=int(rank),condition_number=cond)
    def model(cols):
        a=A[:,cols];beta=np.linalg.lstsq(a,B,rcond=None)[0];res=B-a@beta
        # Independent normal-equation arithmetic check, no separate raw extraction.
        other=np.linalg.solve(a.T@a,a.T@B);assert np.allclose(other,beta,rtol=1e-10,atol=1e-10)
        return dict(beta={X[i]:float(v) for i,v in zip(cols,beta)},within_weighted_R2=float(1-(res@res)/var))
    rms=np.sqrt(np.sum(A*A,axis=0));corr=(A.T@A)/np.outer(rms,rms)
    return dict(status='DESCRIPTIVE_ONLY',**support(p),rank=int(rank),condition_number=cond,within_weighted_response_variance=var,scale=dict(zip(X,map(float,scale))),weighted_predictor_correlation=corr.tolist(),size_only=model([0]),climate_only=model([1,2]),full=model([0,1,2]))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('counts',type=Path);ap.add_argument('marine',type=Path);ap.add_argument('out',type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    p,q,primary,structure=prepare(a.counts,a.marine);fit=solve(centered(primary));out={'status':fit['status'],'source_artifact_pins':{'13669533413':COUNT_PIN,'13829236358':MARINE_PIN},'structure':structure,'fit':fit,'causal_or_predictive_claim':False,'new_independent_census_data':False}
    if fit['status']=='DESCRIPTIVE_ONLY':
        scale=np.array([fit['scale'][x] for x in X]);dels={}
        for col in ['block','source_region']:
            dels[col]=[dict(omitted=str(k),**solve(centered(primary[primary[col]!=k]),scale)) for k in sorted(primary[col].unique())]
        out['deletions']=dels
        out['deletion_ranges']={}
        for key,values in dels.items():
            v=[r for r in values if r['status']=='DESCRIPTIVE_ONLY'];out['deletion_ranges'][key]={'n_success':len(v),'n_total':len(values),'full_beta_ranges':{x:[min(r['full']['beta'][x] for r in v),max(r['full']['beta'][x] for r in v)] for x in X} if v else None}
    # The source archive is not republished; this is the fixed derived per-series table.
    q.to_csv(a.out/'derived_series.csv',index=False)
    (a.out/'result.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='deletions'},indent=2,allow_nan=False))
if __name__=='__main__':main()
