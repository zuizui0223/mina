#!/usr/bin/env python3
"""Original MAPPPD observed-nest hierarchical Gaussian state-space backtest.

Latent log(1+nests): x_{s,t}=x_{s,t-1}+mu_{region,species}
                                + beta_species*ice5yr_anomaly_{site,t} + w_t
Observed log(1+nests): y_{s,t}=x_{s,t}+e_t.

The exact observed consecutive-difference likelihood has covariance
  diag(q*year_gap)+r*tridiag(2,-1), where q=annual process variance and
  r=observation variance. Fitting does not impute missing unobserved years as
  genuine census zeros. μ and β have fixed shrinkage priors. Model comparison
  is *out-of-time* and at fixed biological source support.

This is an abundance model of *observed nests*, NOT vital-rate IPM; no adult
survival, recruitment, individual dispersal, future nest forecasts or new p.
"""
from __future__ import annotations
import argparse,io,zipfile,hashlib,json
from pathlib import Path
import numpy as np,pandas as pd
from scipy.optimize import minimize
from scipy.linalg import cho_factor,cho_solve

START,END=1995,2020
CUTOFFS=(2010,2015)
SPECIES=('ADPE','CHPE','GEPE')
REFERENCE=range(1991,2001)
SEED=20261116
SHRINK_MU_SPECIES=0.07
SHRINK_MU_REGION=0.045
SHRINK_BETA_SPECIES=0.07
SIC_SCALE_PP=20.

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read_zip_csv(path,member):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        return pd.read_csv(io.BytesIO(z.read(member)))

def load_inputs(countzip,siczip):
    c=read_zip_csv(countzip,'source_observed_2456.csv')
    inventory=read_zip_csv(countzip,'panantarctic_595_site_inventory.csv')
    assert len(inventory)==595 and inventory.site_id.is_unique
    c=c.merge(inventory[['site_id','polar_250km_fixed_grid_block']],on='site_id',how='left',validate='many_to_one')
    assert c.polar_250km_fixed_grid_block.notna().all()
    d=read_zip_csv(siczip,'ice_595_outputs/original_595_site_months_120_source_QA.csv')
    assert len(c)==2456 and not c.duplicated(['site_id','species','season']).any()
    assert len(d)==71400 and d.site_id.nunique()==595
    assert set(d.year)==set(range(1991,2021)) and set(d.month)=={8,9,10,11}
    assert d.groupby(['site_id','year']).month.nunique().eq(4).all()
    annual=d.groupby(['site_id','year'],sort=False).agg(
         sic=('source_25km_buffer_mean_SIC_pct','mean'),
         coastal_pixel_coverage=('original_native_ocean_coverage_fraction','mean')).reset_index()
    assert len(annual)==595*30 and annual.sic.between(0,100).all()
    assert annual.coastal_pixel_coverage.between(0,1).all()
    annual=annual.sort_values(['site_id','year'])
    annual['ice5']=annual.groupby('site_id').sic.transform(lambda s:s.rolling(5,min_periods=5).mean())
    baseline=annual.loc[annual.year.isin(REFERENCE)].groupby('site_id').sic.mean()
    annual['ice5_anom_20pp']=(annual.ice5-annual.site_id.map(baseline))/SIC_SCALE_PP
    assert annual.loc[annual.year.between(START,END),'ice5_anom_20pp'].notna().all()
    c=c[c.season.between(START,END)].sort_values(['species','site_id','season']).copy()
    c['y']=np.log1p(c.observed_nest_count)
    c['group']=c.species+'|'+c.source_region
    assert (c.observed_nest_count>=0).all()
    return c,annual

def training_sequences(c,cutoff,annual):
    clim={i:{int(y):float(a) for y,a in zip(g.year,g.ice5_anom_20pp)}
          for i,g in annual.groupby('site_id',sort=False)}
    seqs=[]
    for (site,sp),g in c[c.season<=cutoff].groupby(['site_id','species'],sort=False):
        g=g.sort_values('season');t=g.season.to_numpy(int);y=g.y.to_numpy(float)
        if len(t)<2:continue
        dy=np.diff(y); gap=np.diff(t)
        ax=[]
        for i in range(len(t)-1):
            z=np.sum([clim[site][u] for u in range(t[i]+1,t[i+1]+1)])
            ax.append(z)
        seqs.append(dict(site=site,species=sp,region=g.source_region.iloc[0],
                    group=g.group.iloc[0],years=t,logcounts=y,
                    diff=dy,gap=gap,ice_path=np.array(ax)))
    return seqs,clim

def make_design(seqs,climate):
    groups=sorted({s['group'] for s in seqs})
    species=[x for x in SPECIES if any(s['species']==x for s in seqs)]
    labels=['sp_'+x for x in species]+['grp_'+x for x in groups]
    if climate: labels+=['beta_ice5_'+x for x in species]
    mapindex={s:i for i,s in enumerate(labels)}
    matrices=[]
    for seq in seqs:
        X=np.zeros((len(seq['diff']),len(labels)))
        X[:,mapindex['sp_'+seq['species']]]=seq['gap']
        X[:,mapindex['grp_'+seq['group']]]=seq['gap']
        if climate:X[:,mapindex['beta_ice5_'+seq['species']]]=seq['ice_path']
        matrices.append(X)
    sd=np.array([SHRINK_MU_SPECIES]*len(species)+[SHRINK_MU_REGION]*len(groups)
                  +([SHRINK_BETA_SPECIES]*len(species) if climate else []))
    return labels,matrices,sd

def gls_fit(seqs,climate):
    labels,Xs,sd=make_design(seqs,climate)
    D=len(labels)
    ridge=np.diag(1/sd**2)
    def profiled(qr,ret=False):
        q,r=np.exp(qr)
        L=ridge.copy()
        h=np.zeros(D)
        logdet=0.
        for seq,X in zip(seqs,Xs):
            k=len(seq['diff']);S=np.diag(q*seq['gap']+2*r)
            off=-r
            if k>1:
                idx=np.arange(k-1);S[idx,idx+1]=off;S[idx+1,idx]=off
            try: chol=cho_factor(S,lower=True,check_finite=False)
            except np.linalg.LinAlgError:return np.inf
            Wx=cho_solve(chol,X,check_finite=False)
            Wy=cho_solve(chol,seq['diff'],check_finite=False)
            L+=X.T@Wx
            h+=X.T@Wy
            logdet+=2*np.log(np.diag(chol[0])).sum()
        theta=np.linalg.solve(L,h)
        penalty=theta@ridge@theta
        rss=0.
        for seq,X in zip(seqs,Xs):
            k=len(seq['diff']);S=np.diag(q*seq['gap']+2*r)
            if k>1:
                ix=np.arange(k-1);S[ix,ix+1]=-r;S[ix+1,ix]=-r
            resid=seq['diff']-X@theta
            ch=cho_factor(S,lower=True,check_finite=False)
            rss+=resid@cho_solve(ch,resid,check_finite=False)
        nll=logdet+rss+penalty
        if ret:return dict(theta=theta,labels=labels,q=q,r=r,nll=nll,
                       series=len(seqs),n_diffs=sum(len(s['diff']) for s in seqs),
                       objective_method='profiled penalized exact Gaussian state-space difference likelihood')
        return nll
    fit=minimize(profiled,x0=np.log([.1,.1]),method='L-BFGS-B',
                 bounds=[(np.log(.0001),np.log(3.0))]*2,
                 options={'maxiter':70,'ftol':1e-7})
    obj=profiled(fit.x,True)
    obj['converged']=bool(fit.success)
    obj['message']=str(fit.message)
    return obj

def get_prediction(model,site,sp,reg,t0,t1,clim):
    vals=dict(zip(model['labels'],model['theta']))
    mu=vals.get('sp_'+sp,0)+vals.get('grp_'+sp+'|'+reg,0)
    drift=mu*(t1-t0)
    if 'beta_ice5_'+sp in vals:
        drift+=vals['beta_ice5_'+sp]*np.sum([clim[site][y] for y in range(t0+1,t1+1)])
    return float(drift)

def filtered_last_state(model,seq,clim):
    """Use Kalman filtering, rather than the last noisy observation, to initialize a future state.

    Diffuse first-state prior collapses to the first original observed count
    with posterior variance r. Recursions condition on every real training count.
    """
    years=seq['years'];values=seq['logcounts']
    x=float(values[0]);P=float(model['r'])
    for i in range(1,len(years)):
        step=get_prediction(model,seq['site'],seq['species'],seq['region'],
                            int(years[i-1]),int(years[i]),clim)
        prior=x+step
        var=P+model['q']*float(years[i]-years[i-1])
        gain=var/(var+model['r'])
        x=prior+gain*(float(values[i])-prior)
        P=(1-gain)*var
    assert np.isfinite(x) and P>0
    return x,P

def split_holdouts(c,cutoff):
    groups=[]
    for (site,sp),g in c.groupby(['site_id','species'],sort=True):
        tr=g[g.season<=cutoff].sort_values('season')
        ts=g[g.season.between(cutoff+1,min(cutoff+10,END))].sort_values('season')
        if len(tr)<3 or tr.season.max()-tr.season.min()<5 or len(ts)==0:continue
        groups.append(dict(cutoff=cutoff,site_id=site,species=sp,
            source_region=tr.source_region.iloc[0],
            original_250km_block=tr.polar_250km_fixed_grid_block.iloc[0],
            t_last=int(tr.season.iloc[-1]),y_last=float(tr.y.iloc[-1]),
            n_last=int(tr.observed_nest_count.iloc[-1]),
            t_test=int(ts.season.iloc[0]),y_test=float(ts.y.iloc[0]),
            n_test=int(ts.observed_nest_count.iloc[0]),
            n_training=len(tr),training_span=int(tr.season.max()-tr.season.min())))
    return pd.DataFrame(groups)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--counts-source-zip',required=True,type=Path)
    p.add_argument('--ice-source-zip',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--repeat',type=int,default=0,help='Leave 0: deterministic source test; no post-hoc tuning')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    c,annual=load_inputs(a.counts_source_zip,a.ice_source_zip)
    rows=[];fitted={};holdouts=[]
    for cut in CUTOFFS:
        seqs,clim=training_sequences(c,cut,annual)
        held=split_holdouts(c,cut)
        assert len(held)>30
        m0=gls_fit(seqs,False)
        m1=gls_fit(seqs,True)
        result={'cutoff':cut,'n_train_diff':m0['n_diffs'],'n_train_site_species':m0['series'],
                'n_test':len(held),'n_original_test_regions':int(held.source_region.nunique()),
                'species_test_counts':held.species.value_counts().to_dict(),
                'SSM_no_climate':{k:v for k,v in m0.items() if k!='theta'},
                'SSM_climate_5yr':{k:v for k,v in m1.items() if k!='theta'},
                'beta_5yr_sic':{k:float(v) for k,v in zip(m1['labels'],m1['theta']) if k.startswith('beta_')},
                'source_censor':'genuine count observations only; observed count zero retained'}
        fitted[str(cut)]=result
        model_sequences={(q['site'],q['species']):q for q in seqs}
        for v in held.itertuples(index=False):
            base=v.y_last
            seq=model_sequences[(v.site_id,v.species)]
            x0,P0=filtered_last_state(m0,seq,clim)
            x1,P1=filtered_last_state(m1,seq,clim)
            d0=get_prediction(m0,v.site_id,v.species,v.source_region,v.t_last,v.t_test,clim)
            d1=get_prediction(m1,v.site_id,v.species,v.source_region,v.t_last,v.t_test,clim)
            holdouts.append({**v._asdict(),
             'model_persistence_log_n':base,
             'model_region_species_ssm_log_n':x0+d0,
             'model_5year_ice_ssm_log_n':x1+d1,
             'posterior_filtered_last_nonclimate_log_n':x0,
             'posterior_filtered_last_climate_log_n':x1,
             'posterior_filtered_last_nonclimate_variance':P0,
             'posterior_filtered_last_climate_variance':P1,
             'gap_years':v.t_test-v.t_last})
    scored=pd.DataFrame(holdouts)
    preds=['model_persistence_log_n','model_region_species_ssm_log_n','model_5year_ice_ssm_log_n']
    validation=[]
    for cut,sub in list(scored.groupby('cutoff'))+[('both_repeated_sites_not_independent',scored)]:
        for pred in preds:
            e=sub[pred]-sub.y_test
            validation.append(dict(cutoff=cut,model=pred,n=len(sub),
                n_sites=sub.site_id.nunique(),n_source_regions=sub.source_region.nunique(),
                n_species=sub.species.nunique(),
                MAE_log1p=float(np.mean(np.abs(e))),
                RMSE_log1p=float(np.sqrt(np.mean(e*e))),
                mean_signed_error=float(np.mean(e)),
                median_gap_years=float(sub.gap_years.median()),
                source_conditioned_only=True))
    metrics=pd.DataFrame(validation)
    assert scored.original_250km_block.notna().all()
    metrics.to_csv(a.output/'population_dynamics_original_retrospective_scores.csv',index=False)
    scored.to_csv(a.output/'population_dynamics_original_hidden_censuses.csv',index=False)
    annual[['site_id','year','sic','ice5','ice5_anom_20pp']].to_csv(
       a.output/'595_original_annual_5year_ice_anomalies.csv',index=False)
    m={"status":"EMPIRICAL_STATE_SPACE_RETROSPECTIVE_VALIDATION_ONLY",
       "count_source_zip_sha256":sha(a.counts_source_zip),
       "SIC_source_zip_sha256":sha(a.ice_source_zip),
       "model_equations":{
         "process":"x[i,t]=x[i,t-1]+mu[species,source_region]+beta[species]*5yr_sic_anomaly[i,t]+N(0,q)",
         "measurement":"log1p(real observed nests[i,t])=x[i,t]+N(0,r)",
         "estimation":"exact consecutive-difference covariance diag(q*gap)+r*tridiag(2,-1) with fixed Gaussian shrinkage priors"},
       "sampling":"observed census years only; missing years never zero; one representative census method per colony species from original 2456",
       "ice_definition":"Original OSI SAF four-month Aug-Nov site mean, five preceding years; anomaly vs fixed 1991–2000 site mean scaled by 20 percentage points",
       "horizon":"one first actually observed count after 2010 or 2015 cutoff, up to ten future years",
       "future_2050_2100_nests_estimated":False,
       "individual_survival_recruitment_emigration_identifiable":False,
       "fitted":fitted,"scores":validation}
    (a.output/'population_dynamics_model_verdict.json').write_text(json.dumps(m,ensure_ascii=False,indent=2)+'\n')
    print('MODEL_BACKTEST='+json.dumps({'score':validation,'fitted':{
      k:{'n_train':v['n_train_site_species'],'n_test':v['n_test'],'beta_ice':v['beta_5yr_sic']}
         for k,v in fitted.items()}},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
