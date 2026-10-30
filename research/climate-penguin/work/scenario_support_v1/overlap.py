"""Co-period September level differences; not synchronized weather validation.

CMIP6 historical simulations are free-running. Matching calendar years restricts
the period, but does not imply matching internal variability or weather events.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/scenario_support_v1'
cohort_path=ROOT/'outputs/relationship_response_v1/cohort.csv'
mapping_path=ROOT/'outputs/climate_penguin/behavior_environment_coordinate_join.csv'
cohort=pd.read_csv(cohort_path)
raw=pd.read_csv(mapping_path)
assert not raw.source_row_1based.duplicated().any()
mapping=raw.set_index('source_row_1based').location_id
paths=sorted((ROOT/'outputs/cmip6_projection_v1').glob('monthly_*_historical.csv.gz'))
assert len(paths)==9
hist=pd.concat([pd.read_csv(p) for p in paths],ignore_index=True)
hist=hist[hist.month.eq(9)]
rows=[]
variables={'tas':('airC',1.),'siconc':('ice10',10.),'sos':('salt01',.1)}
for (model,member,var),h in hist.groupby(['source_id','member_id','variable_id']):
    lookup=h.set_index(['location_id','year']).value
    assert lookup.index.is_unique
    col,scale=variables[var]
    for r in cohort.to_dict('records'):
        if r['year'] not in h.year.unique():
            continue
        ids=[int(i) for i in str(r['source_rows']).split('|')]
        locs=mapping.loc[ids].tolist()
        values=[float(lookup.loc[(loc,r['year'])]) for loc in locs]
        assert np.isfinite(values).all()
        observed=r[col]*scale
        rows.append(dict(scope=r['scope'],species=r['species'],cam=r['cam'],year=r['year'],
                         source_id=model,member_id=member,variable_id=var,source_rows=r['source_rows'],
                         coordinate_count=len(set(locs)),observed=observed,model=float(np.mean(values)),
                         model_minus_observed=float(np.mean(values))-observed))
joined=pd.DataFrame(rows)
joined.to_csv(OUT/'overlap_annual_values.csv',index=False)
keys=['scope','species','cam','source_id','member_id','variable_id']
site=joined.groupby(keys,as_index=False).agg(n_years=('year','nunique'),first_year=('year','min'),last_year=('year','max'),
    observed_mean=('observed','mean'),model_mean=('model','mean'),mean_level_difference=('model_minus_observed','mean'))
site.to_csv(OUT/'overlap_site_levels.csv',index=False)
summary=site.groupby(['scope','species','source_id','variable_id'],as_index=False).agg(
    species_sites=('cam','size'),min_years=('n_years','min'),max_years=('n_years','max'),
    equal_site_observed_mean=('observed_mean','mean'),equal_site_model_mean=('model_mean','mean'),
    equal_site_level_difference=('mean_level_difference','mean'))
summary.to_csv(OUT/'overlap_level_summary.csv',index=False)
coverage=cohort.assign(overlaps_saved_historical=cohort.year.isin(hist.year.unique())).groupby(['scope','species'],as_index=False).agg(
    total_site_years=('year','size'),overlap_site_years=('overlaps_saved_historical','sum'))
coverage.to_csv(OUT/'overlap_coverage.csv',index=False)
# Independent join and aggregation from exploded original source identifiers.
expanded=cohort.copy()
expanded['source_id_row']=expanded.source_rows.astype(str).str.split('|')
expanded=expanded.explode('source_id_row')
expanded['location_id']=expanded.source_id_row.astype(int).map(mapping)
expanded=expanded.merge(hist,on=['location_id','year'],validate='many_to_many')
check=expanded.groupby(['scope','species','cam','year','source_id','member_id','variable_id'],as_index=False).value.mean()
checked=joined.merge(check,on=['scope','species','cam','year','source_id','member_id','variable_id'],validate='one_to_one')
assert len(checked)==len(joined)==len(check)
assert np.allclose(checked.model,checked.value,atol=1e-10,rtol=0)
receipt={'passed':True,'independently_checked_model_joins':len(checked),
         'input_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in paths+[cohort_path,mapping_path]},
         'interpretation':'short co-period level comparison, not weather prediction skill or calibrated bias correction',
         'unresolved':['2015-2020 model values absent from saved projections','short overlap cannot support independent calibration and validation','model internal variability not phase aligned with observations','logger and regional/ocean grid supports differ']}
(OUT/'overlap_validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(coverage.to_string(index=False))
print(summary[summary.scope.eq('all_source_labels')&summary.variable_id.eq('siconc')].to_string(index=False))
