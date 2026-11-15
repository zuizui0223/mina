#!/usr/bin/env python3
"""Independent original 588x28 marine / observed-census 80-row crosscheck.

Checks all climate decomposition rows against direct matrix arithmetic and
both original source-file row counts. Never equates unmatched GLORYS sites
with penguin or actual marine absence. No formal p-value or attribution.
"""
import argparse,zipfile,numpy as np,pandas as pd,json
from pathlib import Path
ap=argparse.ArgumentParser()
ap.add_argument('--marine-zip',type=Path,required=True)
ap.add_argument('--cohort-csv',type=Path,required=True)
ap.add_argument('--out-dir',type=Path,required=True)
a=ap.parse_args()
with zipfile.ZipFile(a.marine_zip) as z:
    source=pd.read_csv(z.open('original_588_site_1993_2020_actual_SIC_SSS_SST_PC1.csv'))
cohort=pd.read_csv(a.cohort_csv)
results=pd.read_csv(a.out_dir/'three_cohort_marine_original_axis_kitagawa_components.csv')
cohorts=pd.read_csv(a.out_dir/'three_cohort_glorys_observability_gate.csv')
assert (len(source),len(cohort),len(results),len(cohorts))==(16464,80,24,3)
cols={'SIC_pp':'mean_source_SIC_pp','temperature_C':'mean_GLORYS_thetao_C',
  'salinity_psu':'mean_GLORYS_salinity','thermal_ice_PC1':'warm_direction_three_var_marine_PCA_score'}
errs=[];verification=[]
for entry in cohorts.itertuples(index=False):
    c=cohort[cohort.cohort==entry.cohort]
    good=c[c.site_id.isin(source.site_id)]
    excluded=c[~c.site_id.isin(source.site_id)]
    assert len(excluded)==6 and excluded.source_region.eq('Victoria Land').all()
    assert abs(excluded.n_late.sum()/c.n_late.sum()-entry.unavailable_source_census_share_late)<1e-12
    def south(z):
        u=z.n_early.to_numpy(float);v=z.n_late.to_numpy(float);lat=z.latitude.to_numpy(float)
        return 111.195*(sum(-lat*v)/sum(v)-sum(-lat*u)/sum(u))
    errs.extend([abs(south(c)-entry.full_source_southward_countweighted_km),
                 abs(south(good)-entry.marine_subset_southward_countweighted_km)])
    for win,finish in [('1993-2000_to_2011-2020',2020),('1993-2000_to_2011-2018_source_hold',2018)]:
        group=source[source.site_id.isin(good.site_id)]
        early=group[group.year.between(1993,2000)].groupby('site_id')[list(cols.values())].mean()
        late=group[group.year.between(2011,finish)].groupby('site_id')[list(cols.values())].mean()
        ordered=good.set_index('site_id').sort_index(); old=ordered.n_early.to_numpy(float);new=ordered.n_late.to_numpy(float)
        u=old/old.sum();v=new/new.sum()
        for label,col in cols.items():
            source_a=early.loc[ordered.index,col].to_numpy(float);source_b=late.loc[ordered.index,col].to_numpy(float)
            # Independent crossed counterfactual formulation rather than
            # direct Kitagawa components() used in the original calculation.
            e00=u@source_a; e01=u@source_b; e10=v@source_a; e11=v@source_b
            climate=(e01-e00+e11-e10)/2
            allocation=(e10-e00+e11-e01)/2
            row=results[(results.cohort==entry.cohort)&(results.climate_window==win)&(results.variable==label)]
            assert len(row)==1
            ref=row.iloc[0]
            diffs=[e00-ref.exposure_early,e11-ref.exposure_late,e11-e00-ref.exposure_change,
                climate-ref.within_site_physical_change,allocation-ref.nesting_weight_reallocation]
            errs.extend(abs(d) for d in diffs)
            assert max(abs(d) for d in diffs)<1e-10
        verification.append({'cohort':entry.cohort,'climate_window':win,'verified_variables':list(cols),
            'n_original_site_years':len(group),'n_GLORYS_sites':len(ordered)})
assert len(verification)==6
assert max(errs)<1e-10
out={'status':'PASS_SOURCE_80_NEST_RECORDS_588x28_MARINE_FULLY_RECOMPUTED',
   'original_source_site_years':len(source),'original_colony_cohort_rows':len(cohort),
   'verified_original_cohort_site_support_rows':len(cohorts),
   'verified_component_rows':len(results),'verified_comparison_cohort_windows':len(verification),
   'max_absolute_independent_numeric_error':max(errs),
   'checks':verification,
   'limits':['No sea-state values invented for six unlinked source colony locations',
             'Original nest count 1991-2000 vs marine source 1993-2000 supports differ',
             'GLORYS source is a reanalysis, not penguin foraging observations',
             'Original six wet-cell-excluded sites are still genuine observed nesting colonies',
             'No pooled statistical significance, causal effects or future demographic forecast']}
(a.out_dir/'independent_validation.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
