"""Observed predictor separation and future shifts relative to observed residual spread."""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import statsmodels.api as sm
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/environment_identifiability_v1'
FEATURES=['airC','ice10','salt01','waterC']


def main():
    OUT.mkdir(exist_ok=True)
    cp=ROOT/'outputs/relationship_response_v1/cohort.csv'
    bp=ROOT/'outputs/four_environment_scenarios_v1/coefficients.csv'
    sp=ROOT/'outputs/four_environment_scenarios_v1/site_components.csv'
    cohort=pd.read_csv(cp);coeff=pd.read_csv(bp);future=pd.read_csv(sp)
    rows=[];scenarios=[]
    for b in coeff.to_dict('records'):
        a=cohort[(cohort.scope==b['scope'])&(cohort.species==b['species'])]
        z=pd.get_dummies(a.cam,dtype=float).to_numpy()
        if b['mode']=='site_year':z=np.column_stack([z,pd.get_dummies(a.year,drop_first=True,dtype=float)])
        x=a[FEATURES].to_numpy();y=a.y.to_numpy()
        rx=x-z@np.linalg.lstsq(z,x,rcond=None)[0]
        # Unit-norm columns remove the arbitrary physical scaling from condition number.
        condition=np.linalg.cond(rx/np.sqrt((rx**2).sum(axis=0)))
        for i,f in enumerate(FEATURES):
            other=np.delete(x,i,axis=1);nuisance=np.column_stack([z,other])
            xr=x[:,i]-nuisance@np.linalg.lstsq(nuisance,x[:,i],rcond=None)[0]
            yr=y-nuisance@np.linalg.lstsq(nuisance,y,rcond=None)[0]
            ss=xr@xr;base=rx[:,i]@rx[:,i]
            beta=float(xr@yr/ss)
            assert np.isclose(beta,b[f],atol=1e-7)
            full=sm.OLS(y,np.column_stack([nuisance,x[:,i]])).fit()
            assert np.isclose(full.params[-1],beta,atol=1e-7)
            partial=float(np.corrcoef(xr,yr)[0,1])
            sd=float(np.std(xr,ddof=1))
            rec=dict(scope=b['scope'],species=b['species'],mode=b['mode'],feature=f,n=len(a),
                     raw_sd=float(a[f].std()),fixed_effect_residual_sd=float(np.std(rx[:,i],ddof=1)),
                     conditional_residual_sd=sd,residual_fraction=float(ss/base),vif=float(base/ss),
                     standardized_condition_number=float(condition),partial_r=partial,coefficient=beta,
                     index_per_conditional_sd=beta*sd)
            rows.append(rec)
            t=future[(future.scope==b['scope'])&(future.species==b['species'])&(future['mode']==b['mode'])]
            for key,g in t.groupby(['source_id','experiment_id','period','transform']):
                # All physical sites remain; no exclusion based on support or effect size.
                if not g.physical_ice.all():continue
                delta=g['delta_'+f].mean()
                scenarios.append(dict(scope=b['scope'],species=b['species'],mode=b['mode'],feature=f,
                    **dict(zip(['source_id','experiment_id','period','transform'],key)),
                    mean_environment_change=float(delta),conditional_residual_sd=sd,
                    change_over_residual_sd=float(delta/sd),mean_component=float(delta*beta)))
    d=pd.DataFrame(rows);s=pd.DataFrame(scenarios)
    assert len(d)==48
    assert np.allclose(d.vif*d.residual_fraction,1)
    d.to_csv(OUT/'observed_geometry.csv',index=False)
    s.to_csv(OUT/'future_scale_comparison.csv',index=False)
    (OUT/'validation.json').write_text(json.dumps(dict(status='passed_descriptive_diagnostics',
        specifications=len(d),future_feature_summaries=len(s),
        inputs={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [cp,bp,sp]},
        interpretation='VIF is variance inflation, not causal confounding. Change/residual-SD is not a z score, p value or prediction interval.'),indent=2)+'\n')
    print(d.query("scope=='all_source_labels' and feature=='waterC'").to_string(index=False))
    print(s.query("scope=='all_source_labels' and feature=='waterC' and transform=='bounded' and experiment_id=='ssp585' and period=='2081-2100'")
          [['species','mode','source_id','change_over_residual_sd']].to_string(index=False))


if __name__=='__main__':main()
