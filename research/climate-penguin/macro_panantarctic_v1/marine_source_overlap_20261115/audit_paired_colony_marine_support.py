#!/usr/bin/env python3
"""Original Adélie fixed-colony nesting and marine source support audit.

Source inputs are immutable source-audited GitHub Actions exports, not
species absences or invented ocean values. The original 588-site marine
source excludes six biologically observed Ross/Victoria Land colonies in
nested 19/26/35 Adélie nesting rosters; climate claims are thus conditional.
Original census and reanalysis time supports differ (1991-2000 vs 1993-2000),
so the marine analysis clearly labels its own 1993-2000 baseline. No p-values.
"""
from __future__ import annotations
import argparse, hashlib, io, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

MEAN_FIELDS = {
  'SIC_pp': 'mean_source_SIC_pp',
  'temperature_C': 'mean_GLORYS_thetao_C',
  'salinity_psu': 'mean_GLORYS_salinity',
  'thermal_ice_PC1': 'warm_direction_three_var_marine_PCA_score'
}
EXPECTED = {'all_three_decades': 19, 'two_plus_endpoint_years':26, 'one_plus_endpoint_year':35}
EXCLUDED = {'BRDM','BRDN','BRDS','CRZE','CRZW','ROYD'}
KM=111.195

def read_inputs(cohort_path:Path, marine_zip:Path):
    cohort = pd.read_csv(cohort_path)
    with zipfile.ZipFile(marine_zip) as z:
        assert z.testzip() is None
        ocean = pd.read_csv(z.open('original_588_site_1993_2020_actual_SIC_SSS_SST_PC1.csv'))
    assert cohort.shape[0] == 80
    assert cohort.groupby('cohort').size().to_dict() == EXPECTED
    assert cohort.species.eq('ADPE').all()
    assert not cohort.duplicated(['cohort','site_id']).any()
    assert ocean.shape[0] == 588*28
    assert ocean.site_id.nunique() == 588 and ocean.year.nunique() == 28
    assert not ocean.duplicated(['site_id','year']).any()
    assert ocean.groupby('site_id').year.nunique().eq(28).all()
    assert {(int(y),int(x)) for y,x in ocean[['GLORYS_cell_y','GLORYS_cell_x']].drop_duplicates().itertuples(index=False,name=None)}.__len__() == 378
    assert set(ocean.year) == set(range(1993,2021))
    assert (cohort[['n_early','n_late']]>=0).all().all()
    assert set(cohort.site_id) - set(ocean.site_id) == EXCLUDED
    assert ocean.groupby('site_id').source_region.nunique().eq(1).all()
    return cohort, ocean

def south_shift(z):
    if not len(z): return None
    early=z.n_early.to_numpy(float)
    late=z.n_late.to_numpy(float)
    if early.sum()<=0 or late.sum()<=0:return None
    south=-z.latitude.to_numpy(float)
    return KM*(np.average(south,weights=late)-np.average(south,weights=early))

def components(z,base_col,end_col):
    a=z[base_col].to_numpy(float);b=z[end_col].to_numpy(float)
    old=z.n_early.to_numpy(float);new=z.n_late.to_numpy(float)
    old=old/old.sum();new=new/new.sum()
    physical=float(np.sum((old+new)/2*(b-a)))
    reweight=float(np.sum((new-old)*(a+b)/2))
    value0=float(old@a);value1=float(new@b)
    assert abs((value1-value0)-(physical+reweight))<1e-10
    return dict(exposure_early=value0,exposure_late=value1,
                exposure_change=value1-value0,
                within_site_physical_change=physical,
                nesting_weight_reallocation=reweight,
                difference_identity_error=abs((value1-value0)-(physical+reweight)))

def region_demeaned_r(x,y,regions):
    q=pd.DataFrame({'x':x,'y':y,'region':list(regions)})
    q['dx']=q.x-q.groupby('region').x.transform('mean')
    q['dy']=q.y-q.groupby('region').y.transform('mean')
    if q.dx.std()<1e-12 or q.dy.std()<1e-12:return None
    return float(q.dx.corr(q.dy))

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--original-cohort-csv',type=Path,required=True)
    p.add_argument('--original-marine-zip',type=Path,required=True)
    p.add_argument('--out-dir',type=Path,required=True)
    args=p.parse_args();args.out_dir.mkdir(parents=True,exist_ok=True)
    roster,marine=read_inputs(args.original_cohort_csv,args.original_marine_zip)
    avail=set(marine.site_id)
    roster=roster.copy();roster['GLORYS_source_wet_within_25km']=roster.site_id.isin(avail)
    roster['site_count_share_early']=roster.n_early/roster.groupby('cohort').n_early.transform('sum')
    roster['site_count_share_late']=roster.n_late/roster.groupby('cohort').n_late.transform('sum')
    roster.to_csv(args.out_dir/'original_80_cohort_source_glorys_eligibility.csv',index=False,float_format='%.13g')
    cohorts=[];components_rows=[];regions=[];site_marine=[];sens=[]
    all_marine=marine[list(MEAN_FIELDS.values())+['site_id','year']]
    for cohort,frame in roster.groupby('cohort',sort=True):
        good=frame[frame.GLORYS_source_wet_within_25km].copy()
        bad=frame[~frame.GLORYS_source_wet_within_25km].copy()
        assert len(frame)==EXPECTED[cohort] and len(bad)==6
        assert set(bad.site_id)==EXCLUDED
        assert bad.source_region.nunique()==1 and bad.source_region.iloc[0]=='Victoria Land'
        counts=dict(cohort=cohort,n_original_colonies=len(frame),n_marine_matched_sites=len(good),
          n_no_nearby_wet_glorys_sites=len(bad),n_original_reporting_regions=frame.source_region.nunique(),
          n_marine_reporting_regions=good.source_region.nunique(),
          source_census_sum_early=float(frame.n_early.sum()),source_census_sum_late=float(frame.n_late.sum()),
          marine_support_nest_share_early=float(good.n_early.sum()/frame.n_early.sum()),
          marine_support_nest_share_late=float(good.n_late.sum()/frame.n_late.sum()),
          unavailable_source_census_share_early=float(bad.n_early.sum()/frame.n_early.sum()),
          unavailable_source_census_share_late=float(bad.n_late.sum()/frame.n_late.sum()),
          full_source_southward_countweighted_km=south_shift(frame),
          marine_subset_southward_countweighted_km=south_shift(good),
          full_minus_marine_southward_shift_km=south_shift(frame)-south_shift(good),
          all_original_satellite_SIC_support_exists_at_excluded_sites=True,
          GLORYS_absence_is_not_biological_absence=True)
        cohorts.append(counts)
        year_sources=all_marine.loc[all_marine.site_id.isin(good.site_id)]
        assert len(year_sources)==len(good)*28
        base=year_sources[year_sources.year.between(1993,2000)].groupby('site_id')[list(MEAN_FIELDS.values())].mean()
        assert year_sources[year_sources.year.between(1993,2000)].groupby('site_id').year.nunique().eq(8).all()
        for label,a,b in [('1993-2000_to_2011-2020',2011,2020),('1993-2000_to_2011-2018_source_hold',2011,2018)]:
            last=year_sources[year_sources.year.between(a,b)].groupby('site_id')[list(MEAN_FIELDS.values())].mean()
            assert last.shape[0]==len(good)
            good2=good.set_index('site_id').join(base.add_suffix('_early')).join(last.add_suffix('_late'))
            assert good2[list(v+'_early' for v in MEAN_FIELDS.values())+list(v+'_late' for v in MEAN_FIELDS.values())].notna().all().all()
            good2=good2.reset_index()
            for key,col in MEAN_FIELDS.items():
                result=dict(cohort=cohort, climate_window=label,variable=key,
                    n_same_original_sites=len(good2),
                    source_census_early_window='1991-2000',source_census_late_window='2011-2020',
                    climate_baseline_window='1993-2000', climate_late_window=f'{a}-{b}',
                    **components(good2,col+'_early',col+'_late'))
                # Site-equal ecological correlation and region-centered correlation: exploratory.
                delta=good2[col+'_late']-good2[col+'_early']
                response=np.log1p(good2.n_late)-np.log1p(good2.n_early)
                result['pooled_site_equal_correlation_to_log_nest_change']=float(delta.corr(response))
                result['within_source_region_site_equal_correlation_to_log_nest_change']=region_demeaned_r(delta,response,good2.source_region)
                components_rows.append(result)
                if key in ('thermal_ice_PC1','temperature_C','SIC_pp'):
                    for region in sorted(good2.source_region.unique()):
                        q=good2[good2.source_region!=region]
                        if len(q)<3:continue
                        d=components(q,col+'_early',col+'_late')
                        sens.append(dict(cohort=cohort,climate_window=label,variable=key,
                            deleted_source_region=region,n_sites_after_omission=len(q),
                            **d))
            for row in good2.itertuples():
                record=dict(cohort=cohort,climate_window=label,site_id=row.site_id,
                    source_region=row.source_region,polar_250km_block=row.polar_250km_block,
                    n_early=row.n_early,n_late=row.n_late,
                    reference_nest_early_window='1991-2000',reference_nest_late_window='2011-2020')
                for col in MEAN_FIELDS.values():
                    record[col+'_early']=getattr(row,col+'_early');record[col+'_late']=getattr(row,col+'_late')
                site_marine.append(record)
        for r in bad.itertuples():
            regions.append(dict(cohort=cohort,site_id=r.site_id,source_region=r.source_region,
               original_latitude=r.latitude,observed_nest_median_1990s=r.n_early,
               observed_nest_median_2010s=r.n_late,
               source_GLORYS_nearest_wet_grid_25km_gate=False,
               original_1991_2020_satellite_SIC_not_missing_due_to_glorys=True))
    cohorts_df=pd.DataFrame(cohorts)
    components_df=pd.DataFrame(components_rows)
    assert len(cohorts_df)==3 and len(components_df)==24
    assert set(cohorts_df.n_marine_matched_sites)=={13,20,29}
    assert np.max(components_df.difference_identity_error)<1e-10
    assert (components_df[components_df.variable=='thermal_ice_PC1'].query("climate_window=='1993-2000_to_2011-2018_source_hold'").within_site_physical_change>0).all()
    assert (components_df[components_df.variable=='thermal_ice_PC1'].query("climate_window=='1993-2000_to_2011-2018_source_hold'").nesting_weight_reallocation<0).all()
    for df,file in ((cohorts_df,'three_cohort_glorys_observability_gate.csv'),
                    (components_df,'three_cohort_marine_original_axis_kitagawa_components.csv'),
                    (pd.DataFrame(site_marine),'original_marine_matched_site_climate_windows.csv'),
                    (pd.DataFrame(regions),'six_source_census_sites_excluded_from_GLORYS.csv'),
                    (pd.DataFrame(sens),'leave_region_out_marine_PC1_temp_ice_components.csv')):
        df.to_csv(args.out_dir/file,index=False,float_format='%.13g')
    info=dict(status='PASS_3_REAL_ADÉLIE_SOURCE_COHORTS_TRUE_WET_CELL_SUPPORT_GATE',
        known_breeding_sites=595,original_marine_eligibility=588,physical_years=28,
        original_marine_site_years=len(marine),n_original_GLORYS_cells=378,
        n_nested_true_colony_source_rows=len(roster),
        original_marine_zip_sha256=hashlib.sha256(args.original_marine_zip.read_bytes()).hexdigest(),
        source_original_cohort_csv_sha256=hashlib.sha256(args.original_cohort_csv.read_bytes()).hexdigest(),
        original_decade_count_periods=['1991-2000','2011-2020'],
        source_physical_periods=['1993-2000','2011-2020','2011-2018 (sensitivity)'],
        original_six_source_glorys_missing_sites=sorted(EXCLUDED),
        source_Glorys_absent_never_imputed_as_no_ice_or_no_penguin=True,
        source_PC1_reanalysis_not_independent_annual_warming=True,
        source_missingness_not_random_controlled=True,
        source_offshore_grid_is_not_foraging_route=True,
        interregional_coverage_changes_climate_result_not_panantarctic_causality=True,
        cohort_support=cohorts_df.to_dict(orient='records'),
        primary_marine_PCA1_rows=components_df[components_df.variable=='thermal_ice_PC1'].to_dict(orient='records'))
    (args.out_dir/'original_marine_source_support_audit.json').write_text(json.dumps(info,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(dict(status=info['status'],cohort_support=info['cohort_support'],
         primary_marine_PCA1_rows=info['primary_marine_PCA1_rows']),indent=2))

if __name__=='__main__':main()
