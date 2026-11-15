#!/usr/bin/env python3
"""Validate source-joined marine and original nesting count accounting tables.

Runs from checked-in auditable subset of genuine parent-source products; no
synthetic ocean values, invented absences, climate-causal p-values or forecast.
This verifies derived algebra. Parent-source full 588x28 reconstruction was
independently checked locally against original Actions artifact #13829236358.
"""
from pathlib import Path
import numpy as np,pandas as pd
here=Path(__file__).resolve().parent
roster=pd.read_csv(here/'original_80_cohort_source_glorys_eligibility.csv')
site=pd.read_csv(here/'original_marine_matched_site_climate_windows.csv')
cohort=pd.read_csv(here/'three_cohort_glorys_observability_gate.csv')
components=pd.read_csv(here/'three_cohort_marine_original_axis_kitagawa_components.csv')
omit=pd.read_csv(here/'leave_region_out_marine_PC1_temp_ice_components.csv')
assert len(roster)==80 and roster.groupby('cohort').size().to_dict()=={
    'all_three_decades':19,'two_plus_endpoint_years':26,'one_plus_endpoint_year':35}
assert roster.GLORYS_source_wet_within_25km.dtype==bool
assert len(site)==124 and len(components)==24 and len(cohort)==3 and len(omit)==84
assert (site[['n_early','n_late']]>=0).all().all()
assert not site.duplicated(['cohort','climate_window','site_id']).any()
expected_missing={'BRDM','BRDN','BRDS','CRZE','CRZW','ROYD'}
assert set(roster.loc[~roster.GLORYS_source_wet_within_25km,'site_id'])==expected_missing
assert roster.loc[~roster.GLORYS_source_wet_within_25km,'source_region'].eq('Victoria Land').all()
max_error=0.0
checks=0
variables={
    'SIC_pp':'mean_source_SIC_pp',
    'temperature_C':'mean_GLORYS_thetao_C',
    'salinity_psu':'mean_GLORYS_salinity',
    'thermal_ice_PC1':'warm_direction_three_var_marine_PCA_score'}
def recheck(z,variable):
    orig=variables[variable]
    A=z[orig+'_early'].to_numpy(float);B=z[orig+'_late'].to_numpy(float)
    n0=z.n_early.to_numpy(float);n1=z.n_late.to_numpy(float)
    w0=n0/n0.sum();w1=n1/n1.sum()
    # Independent crossed-state formulation of two-factor exact identity
    s00=w0@A;s10=w1@A;s01=w0@B;s11=w1@B
    return {'exposure_early':s00,'exposure_late':s11,'exposure_change':s11-s00,
        'within_site_physical_change':(s01-s00+s11-s10)/2,
        'nesting_weight_reallocation':(s10-s00+s11-s01)/2}
for r in cohort.itertuples():
    obs=roster.loc[roster.cohort.eq(r.cohort)]
    available=obs.loc[obs.GLORYS_source_wet_within_25km]
    assert len(available)==r.n_marine_matched_sites
    assert len(obs)==r.n_original_colonies
    assert abs(obs.loc[~obs.GLORYS_source_wet_within_25km,'n_late'].sum()/obs.n_late.sum()-r.unavailable_source_census_share_late)<1e-10
    x=-obs.latitude.to_numpy(float)
    orig_south=111.195*(np.average(x,weights=obs.n_late)-np.average(x,weights=obs.n_early))
    assert abs(orig_south-r.full_source_southward_countweighted_km)<1e-8
    for period,z in site.loc[site.cohort.eq(r.cohort)].groupby('climate_window'):
        assert set(z.site_id)==set(available.site_id)
        assert (z.set_index('site_id').sort_index().n_early.to_numpy()==available.set_index('site_id').loc[sorted(z.site_id),'n_early'].to_numpy()).all()
        for var in variables:
            o=components.loc[components.cohort.eq(r.cohort)&components.climate_window.eq(period)&components.variable.eq(var)]
            assert len(o)==1
            got=recheck(z,var)
            for key,num in got.items():
                err=abs(num-float(o.iloc[0][key]));max_error=max(max_error,err)
                assert err<1e-8,(r.cohort,period,var,key,err)
                checks+=1
            if var not in ('SIC_pp','temperature_C','thermal_ice_PC1'):continue
            for region in sorted(z.source_region.unique()):
                sub=z.loc[z.source_region.ne(region)]
                m=omit.loc[omit.cohort.eq(r.cohort)&omit.climate_window.eq(period)&omit.variable.eq(var)&omit.deleted_source_region.eq(region)]
                assert len(m)==1 and len(sub)==int(m.iloc[0].n_sites_after_omission)
                again=recheck(sub,var)
                for key,num in again.items():
                    err=abs(num-float(m.iloc[0][key]));max_error=max(max_error,err)
                    assert err<1e-8,(r.cohort,period,var,region,key,err)
                    checks+=1
assert checks>500
print(f'PASS {len(roster)} source colony-cohort rows, {len(site)} matched marine window rows, {len(components)} decomposition rows, {len(omit)} geographic omissions, {checks} cross-state numerical identities; maximum error {max_error:.3g}. Original ocean inputs not invented.')
