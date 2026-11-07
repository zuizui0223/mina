"""Recompute indicators with scalar runs; verify paired scenario bookkeeping."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]/'outputs'
OUT=ROOT/'daily_ice_candidate_scenarios_v1'
features=pd.read_csv(OUT/'annual_features.csv');checks=0
for experiment in ['historical','ssp245','ssp585']:
    with np.load(ROOT/'daily_future_ice_v1'/f'daily_{experiment}.npz') as a:
        dates=pd.to_datetime(a['dates']);values=a['values'];loc=a['location_ids']
    for r in features[features.experiment_id==experiment].itertuples():
        seq=values[dates.year==r.year,list(loc).index(r.location_id)]
        assert sum(float(x)<30 for x in seq[:61])==r.augsep_low30_days
        starts=[i for i in range(116) if all(float(x)<15 for x in seq[i:i+7])]
        status='already_low' if 0 in starts else ('observed_transition' if starts else 'no_observed_transition')
        assert status==r.transition_status
        if status=='observed_transition':assert starts[0]==r.low15_transition_day_from_aug1
        else:assert pd.isna(r.low15_transition_day_from_aug1)
        checks+=1
assert checks==6336
p=ROOT/'paired_species_future_v1'
t=pd.read_csv(p/'site_gap_changes.csv');s=pd.read_csv(p/'scenario_gap_changes.csv')
np.testing.assert_allclose(t.second_shift_days-t.first_shift_days,t.gap_change_days,atol=1e-10)
assert len(s)==72 and len(t)==240
keys=['first','second','mode','source_id','member_id','experiment_id','period']
recomputed=t.groupby(keys).gap_change_days.mean().reset_index().merge(s,on=keys,validate='one_to_one',suffixes=('_direct','_saved'))
np.testing.assert_allclose(recomputed.gap_change_days_direct,recomputed.gap_change_days_saved,atol=1e-10)
receipt=dict(passed=True,daily_feature_scalar_checks=checks,paired_site_difference_checks=len(t),paired_scenarios=72,
    scope='Recompute from saved daily arrays and component outputs, not independent climate-model validation')
(OUT/'independent_validation.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
