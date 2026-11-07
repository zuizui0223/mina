"""Independent direct regressions and per-site scenario arithmetic."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/conditional_response_v1'
cohort=pd.read_csv(ROOT/'outputs/relationship_response_v1/cohort.csv')
coef=pd.read_csv(OUT/'coefficients.csv');sites=pd.read_csv(OUT/'site_index_shifts.csv')
climate=pd.read_csv(OUT/'climate_transformations.csv');summary=pd.read_csv(OUT/'conditional_summary.csv')
for r in coef.itertuples():
    a=cohort[(cohort.scope==r.scope)&(cohort.species==r.species)]
    columns=['cam']+(['year'] if r.mode=='site_year' else [])
    dummy=pd.get_dummies(a[columns].astype(str),drop_first=True,dtype=float)
    x=np.column_stack([np.ones(len(a)),dummy,a[['airC','ice10']]])
    b=np.linalg.lstsq(x,a.y,rcond=None)[0][-2:]
    assert np.allclose(b,[r.air_coefficient,r.ice10_coefficient],atol=1e-8)
checked=sites.merge(coef,on=['scope','species','mode'],validate='many_to_one')
expected=checked.delta_air*checked.air_coefficient+checked.delta_ice10*checked.ice10_coefficient
assert np.allclose(checked.loc[checked.physical_ice,'index_shift'],expected[checked.physical_ice],atol=1e-9)
assert checked.loc[~checked.physical_ice,'index_shift'].isna().all()
for r in climate[climate.variable_id.eq('siconc')].itertuples():
    if r.future_model_mean<r.matched_model_baseline:
        fraction_loss=(r.matched_model_baseline-r.future_model_mean)/r.matched_model_baseline
        value=r.observed_mean*(1-fraction_loss)
    elif r.future_model_mean>r.matched_model_baseline:
        open_water_remaining=(100-r.future_model_mean)/(100-r.matched_model_baseline)
        value=100-(100-r.observed_mean)*open_water_remaining
    else:value=r.observed_mean
    assert np.isclose(value,r.bounded_future,atol=1e-9)
    assert 0<=value<=100
for r in summary.itertuples():
    a=sites.copy()
    for key in ['scope','species','mode','transform','source_id','experiment_id','period']:
        a=a[a[key].eq(getattr(r,key))]
    assert len(a)==r.species_sites
    if a.physical_ice.all():assert np.isclose(a.index_shift.mean(),r.mean_index_shift,atol=1e-9)
    else:assert np.isnan(r.mean_index_shift)
result={'passed':True,'direct_regressions':len(coef),'site_shift_checks':len(sites),'summary_checks':len(summary),'ice_transform_checks':int(climate.variable_id.eq('siconc').sum()),
 'scope':'arithmetic validation, not calibration or causal validation'}
(OUT/'independent_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(result)
