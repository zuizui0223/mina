#!/usr/bin/env python3
"""Independent HiGHS linear program for original nested Adélie site allocation.

Checks all 24 reported extrema using independent LP equality constraints for
2010s source-region or original 250km block nesting subtotal. No ecological
causality, new statistical p-values or independent field replication.
"""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
import pandas as pd
from scipy.optimize import linprog

KM=111.195
SHA='af310e2c8787074ef2bfd69b9a00aab1d863e8cdc3cd53edfd700b5e65460592'
LEVELS={'reporting_region':['source_region'],
        'region_and_250km_block':['source_region','polar_250km_block']}

def LP_bounds(g,keys,field):
    labels=g[keys].astype(str).agg('|'.join,axis=1)
    distinct=sorted(labels.unique())
    A=np.zeros((len(distinct),len(g)),float)
    b=np.zeros(len(distinct),float)
    for i,group in enumerate(distinct):
        mask=(labels==group).to_numpy()
        A[i,mask]=1
        b[i]=g.loc[mask,'n_late'].sum()
    score=g[field].to_numpy(float)
    minimum=linprog(score,A_eq=A,b_eq=b,bounds=(0,None),method='highs')
    maximum=linprog(-score,A_eq=A,b_eq=b,bounds=(0,None),method='highs')
    assert minimum.success and maximum.success
    assert np.max(abs(A@minimum.x-b))<1e-4
    assert np.max(abs(A@maximum.x-b))<1e-4
    return minimum.fun/g.n_late.sum(),-maximum.fun/g.n_late.sum()

def main():
    ap=argparse.ArgumentParser()
    folder=Path(__file__).resolve().parent
    ap.add_argument('--cohort-csv',type=Path,default=folder.parent/'latitudinal_scale_20261115'/'original_adelie_19_26_35_site_growth_cohorts.csv')
    ap.add_argument('--summary-csv',type=Path,default=folder/'observed_source_roster_exact_geographic_envelopes.csv')
    ap.add_argument('--permutation-csv',type=Path,default=folder/'growth_factor_permutation_source_diagnostics.csv')
    ap.add_argument('--out',type=Path,default=folder/'independent_LP_verification.json')
    args=ap.parse_args()
    assert hashlib.sha256(args.cohort_csv.read_bytes()).hexdigest()==SHA
    d=pd.read_csv(args.cohort_csv)
    expect=pd.read_csv(args.summary_csv).set_index('cohort')
    per=pd.read_csv(args.permutation_csv)
    assert len(d)==80 and len(expect)==3 and len(per)==6
    checks=0;maxerr=0.;cohorts=[]
    for cohort,g in d.groupby('cohort',sort=True):
        g=g.copy().reset_index(drop=True)
        g['south_lat']=-g.latitude
        old=np.average(g.south_lat,weights=g.n_early)
        ice_old=np.average(g.sic_early,weights=g.n_early)
        observed=KM*(np.average(g.south_lat,weights=g.n_late)-old)
        assert abs(observed-expect.loc[cohort,'observed_southward_count_weighted_km'])<1e-7
        for label,keys in LEVELS.items():
            a,b=LP_bounds(g,keys,'south_lat')
            c,d0=LP_bounds(g,keys,'sic_late')
            calculated={
              label+'_southward_min_km':KM*(a-old),
              label+'_southward_max_km':KM*(b-old),
              label+'_nearshore_ice_change_min_pp':c-ice_old,
              label+'_nearshore_ice_change_max_pp':d0-ice_old
            }
            for col,value in calculated.items():
                error=abs(value-float(expect.loc[cohort,col]))
                maxerr=max(maxerr,error)
                assert error<1e-7,(cohort,col,error)
                checks+=1
            assert calculated[label+'_southward_min_km']-1e-7 <= observed
            assert observed <= calculated[label+'_southward_max_km']+1e-7
            sample=per[(per.cohort==cohort)&(per.null_label==label)]
            assert len(sample)==1
            sample=sample.iloc[0]
            assert sample.null_min_km >= calculated[label+'_southward_min_km']-1e-7
            assert sample.null_max_km <= calculated[label+'_southward_max_km']+1e-7
            if label=='region_and_250km_block':
                assert calculated[label+'_southward_min_km']>0
                assert sample.fraction_of_source_constrained_random_reassignments_southward==1
        cohorts.append({'cohort':cohort,'n_sites':len(g),'source_geo_and_ice_both_LP_checked':True})
    assert checks==24
    receipt={'status':'PASS_INDEPENDENT_HIGHS_LINEAR_PROGRAM_EXTREMES',
             'checked_exact_bound_values':checks,
             'n_nested_cohort_rows':80,'n_cohorts':3,
             'max_absolute_difference':maxerr,
             'not_independent_field_observation_or_test_of_causality':True,'cohorts':cohorts}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(receipt))

if __name__=='__main__':main()
