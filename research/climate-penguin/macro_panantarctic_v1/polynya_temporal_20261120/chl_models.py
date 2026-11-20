"""Frozen conditional pathway-consistency stage, never a causal mediation estimator."""
import json
import numpy as np
import pandas as pd
from run import HERE, CONTROLS, Y, residualize, save, write, fit

NAMES=['a_P0_to_log10Chl_per10pp','b_log10Chl_to_proxy','a_times_b_per10pp','delta_beta_P0_per10pp','P0_before_per10pp','P0_after_per10pp']

def estimates(gram,rhs):
    # Columns: five controls, P0, P1, C. RHS is isotope Y.
    k=7
    if np.linalg.matrix_rank(gram[:k,:k])<k or np.linalg.matrix_rank(gram)<k+1:
        raise ValueError('bootstrap fixed-effect design rank deficient')
    mediator=np.linalg.solve(gram[:k,:k],gram[:k,k])
    before=np.linalg.solve(gram[:k,:k],rhs[:k])
    after=np.linalg.solve(gram,rhs)
    a=mediator[5]*.1;b=after[7];p0=before[5]*.1;p1=after[5]*.1
    return np.array([a,b,a*b,p1-p0,p0,p1])

def bootstrap(x,y,groups,draws=None,nboot=4999):
    labels=sorted(set(groups));grams=[];rhs=[]
    for group in labels:
        mask=np.asarray(groups)==group;xx=x[mask];yy=y[mask]
        grams.append(xx.T@xx);rhs.append(xx.T@yy)
    grams=np.array(grams);rhs=np.array(rhs)
    if draws is None:draws=np.random.default_rng(20261120).integers(0,len(labels),size=(nboot,len(labels)))
    values=[];valid=[]
    for ids in draws:
        try:
            v=estimates(grams[ids].sum(axis=0),rhs[ids].sum(axis=0));values.append(v);valid.append(True)
        except (ValueError,np.linalg.LinAlgError):
            values.append(np.repeat(np.nan,len(NAMES)));valid.append(False)
    return np.array(values),np.array(valid)

def main():
    a=json.loads((HERE/'chlorophyll_screen_audit.json').read_text());assert a['passes_support']
    source=pd.read_csv(HERE/'chlorophyll_screen_support.csv');source=source[source.status.eq('ELIGIBLE')]
    d=pd.read_csv(HERE/'matched_analysis.csv').merge(source[['site_id','season','C']],on=['site_id','season'],validate='one_to_one')
    assert len(d)==a['confirmed_eligible_rows'] and np.isfinite(d.C).all()
    save(d,'chlorophyll_matched_analysis.csv')
    matrix=residualize(d[CONTROLS+['P0','P1','C',Y]],d);x=matrix[:,:8];y=matrix[:,8]
    norms=pd.DataFrame({'source_region':d.source_region,'x_ss':(x*x).sum(axis=1),'P0_ss':x[:,5]**2,'C_ss':x[:,7]**2}).groupby('source_region',as_index=False).sum();save(norms,'chlorophyll_region_information.csv')
    diag=dict(n=len(d),sites=d.site_id.nunique(),regions=d.source_region.nunique(),seasons=d.season.nunique(),rank=int(np.linalg.matrix_rank(x)),columns=8,condition_number_standardized=float(np.linalg.cond(x/np.where(x.std(axis=0)>0,x.std(axis=0),1))))
    write(diag,'chlorophyll_model_design.json')
    if diag['rank']<8:
        write(dict(status='NOT_IDENTIFIABLE',causal_mediation=False),'chlorophyll_model_verdict.json');return
    point=estimates(x.T@x,x.T@y)
    values,valid=bootstrap(x,y,d.source_region.to_numpy())
    boot=pd.DataFrame(values,columns=NAMES);boot['valid']=valid;save(boot,'chlorophyll_region_bootstrap.csv')
    ok=float(valid.mean())>=.9
    ci=np.quantile(values[valid],[.025,.975],axis=0) if ok else np.full((2,len(NAMES)),np.nan)
    result=pd.DataFrame(dict(term=NAMES,estimate=point,lower=ci[0],upper=ci[1]));save(result,'chlorophyll_pathway_coefficients.csv')
    compatible=bool(ok and ci[0,0]>0 and ci[1,1]<0 and ci[0,3]>0 and point[4]<0 and point[5]<=0)
    # Shared cohort Mjoint before C; distinguish selection effects from adjustment.
    base,_,_=fit(d,['P0','P1']);save(pd.DataFrame(base),'chlorophyll_subset_temporal_model.csv')
    out=dict(status='PATHWAY_CONSISTENCY_SUPPORTED' if compatible else ('PATHWAY_CONSISTENCY_NOT_ESTABLISHED' if ok else 'BOOTSTRAP_SUPPORT_INSUFFICIENT'),n=len(d),sites=d.site_id.nunique(),regions=d.source_region.nunique(),bootstrap_draws=4999,valid_bootstrap=int(valid.sum()),causal_mediation=False)
    write(out,'chlorophyll_model_verdict.json');print(result.to_string(index=False));print(json.dumps(out,indent=2))

if __name__=='__main__':main()
