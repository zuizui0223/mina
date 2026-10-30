"""Joint three-variable support, using convex hulls and independent LP checks.

This assesses additive scenario sensitivity inputs, not calibrated forecasts.
Hull inclusion is geometric interpolation support, not causal identification.
"""
from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull
from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'outputs/scenario_support_v1'
cohort_file = ROOT / 'outputs/relationship_response_v1/cohort.csv'
scenario_file = OUT / 'observed_range_audit.csv'
cohort = pd.read_csv(cohort_file)
scenario = pd.read_csv(scenario_file)
keys = ['scope','species','cam','source_id','member_id','experiment_id','period']
assert not scenario.duplicated(keys+['variable_id']).any()
future = scenario.pivot(index=keys,columns='variable_id',values='observed_mean_plus_delta').reset_index()
assert future[['tas','siconc','sos']].notna().all().all()
rows = []
checks = 0
for (scope,species), f in future.groupby(['scope','species']):
    obs = cohort[(cohort.scope==scope)&(cohort.species==species)]
    x = obs[['airC','ice10','salt01']].to_numpy()*[1,10,.1]
    center, scale = x.mean(axis=0), x.std(axis=0,ddof=1)
    assert (scale>0).all()
    z = (x-center)/scale
    assert np.linalg.matrix_rank(z)==3
    hull = ConvexHull(z)
    # LP membership asks whether target equals a nonnegative weighted mixture
    # of actual observed climate vectors. This independently checks halfspaces.
    equality = np.vstack([z.T,np.ones(len(z))])
    for r in f.to_dict('records'):
        target = np.array([r['tas'],r['siconc'],r['sos']])
        t = (target-center)/scale
        violation = float(np.max(hull.equations[:,:3]@t+hull.equations[:,3]))
        inside = violation<=1e-8
        lp = linprog(np.zeros(len(z)),A_eq=equality,b_eq=np.r_[t,1.],bounds=(0,None),method='highs')
        assert lp.status in (0,2), lp.message
        assert inside==lp.success, (r,violation,lp.message)
        if lp.success:
            assert np.max(np.abs(equality@lp.x-np.r_[t,1.]))<1e-7
        checks+=1
        box = bool(((target>=x.min(axis=0)-1e-10)&(target<=x.max(axis=0)+1e-10)).all())
        physical = bool(0<=r['siconc']<=100 and 0<=r['sos']<=50)
        rows.append(dict(**r,observed_vectors=len(x),observed_sites=obs.cam.nunique(),
                         physical_input=physical,inside_marginal_box=box,inside_joint_hull=inside,
                         box_inside_but_joint_outside=bool(box and not inside),
                         max_standardized_facet_violation=violation))
result = pd.DataFrame(rows)
result.to_csv(OUT/'joint_support.csv',index=False)
summary = result.groupby(['scope','source_id','experiment_id','period'],as_index=False).agg(
    species_sites=('cam','size'), physical_inputs=('physical_input','sum'),
    inside_marginal_box=('inside_marginal_box','sum'),inside_joint_hull=('inside_joint_hull','sum'),
    box_inside_but_joint_outside=('box_inside_but_joint_outside','sum'))
summary.to_csv(OUT/'joint_support_summary.csv',index=False)
receipt = {'passed':True,'halfspace_and_linear_program_checks':checks,
           'variables':['September air temperature (C)','September sea ice (%)','September surface salinity (0.001 scale)'],
           'input_sha256':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in [cohort_file,scenario_file]},
           'limitations':['Additive changes retain the previous baseline mismatch; no bias-corrected climate or biological forecast',
           'Species-wide hull includes between-site variation; inclusion does not establish within-site temporal transportability',
           'Finite-sample hull is descriptive, not a confidence region, probability, or significance test',
           'Three environmental variables do not cover water temperature, drift, snow, vegetation or all predictors',
           'No clipping, model selection, or removal of invalid scenarios; all are reported']}
(OUT/'joint_validation.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(summary[summary.scope.eq('all_source_labels')&summary.period.eq('2081-2100')&summary.experiment_id.eq('ssp585')].to_string(index=False))
print('Independent geometric checks:',checks)
