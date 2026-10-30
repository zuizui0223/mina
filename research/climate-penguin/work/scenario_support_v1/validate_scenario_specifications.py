"""Verify scenario comparison from source rows using dictionary lookups."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
root=Path(__file__).resolve().parents[2]/'outputs'
out=root/'scenario_specification_comparison_v1'
keys=['scope','species','mode','transform','source_id','experiment_id','period']
two=pd.read_csv(root/'conditional_response_v1/conditional_summary.csv')
four=pd.read_csv(root/'four_environment_scenarios_v1/summary.csv')
lookup={tuple(r[k] for k in keys):r['mean_index_shift'] for r in two.to_dict('records')}
assert len(lookup)==288
available=reversed_sign=0
for r in four.to_dict('records'):
    a=lookup[tuple(r[k] for k in keys)];b=r['mean_index_shift']
    if np.isfinite(a) and np.isfinite(b):
        available+=1; reversed_sign+=int((a<0<b) or (b<0<a))
    else: assert np.isnan(a) and np.isnan(b)
receipt=json.loads((out/'validation.json').read_text())
assert available==receipt['valid_pairs'] and reversed_sign==receipt['model_sign_reversals']
fe_available=fe_reversed=0
for source in [two,four]:
    basekeys=[k for k in keys if k!='mode']
    reference={tuple(r[k] for k in basekeys):r['mean_index_shift'] for r in source.to_dict('records') if r['mode']=='site'}
    for r in source.to_dict('records'):
        if r['mode']!='site_year': continue
        a=reference[tuple(r[k] for k in basekeys)];b=r['mean_index_shift']
        if np.isfinite(a) and np.isfinite(b):
            fe_available+=1;fe_reversed+=int((a<0<b) or (b<0<a))
        else: assert np.isnan(a) and np.isnan(b)
assert fe_available==receipt['valid_year_adjustment_pairs'] and fe_reversed==receipt['year_adjustment_sign_reversals']
ranges=pd.read_csv(out/'specification_ranges.csv')
for r in ranges.to_dict('records'):
    values=[]
    for source in [two,four]:
        mask=np.ones(len(source),dtype=bool)
        for k in ['scope','species','experiment_id','period','transform']: mask &= source[k].eq(r[k]).to_numpy()
        assert int(mask.sum())==6
        values.extend(source.loc[mask,'mean_index_shift'].dropna().tolist())
    assert len(values)==r['valid_specifications']
    if values:
        assert np.isclose(min(values),r['minimum_days']) and np.isclose(max(values),r['maximum_days'])
        assert sum(v<0 for v in values)==r['negative'] and sum(v>0 for v in values)==r['positive']
result=dict(passed=True,source_pairs_checked=288,year_adjustment_pairs_checked=288,range_groups_checked=len(ranges),scope='Source lookup, sign count and range reconstruction; not forecast calibration')
(out/'independent_validation.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
