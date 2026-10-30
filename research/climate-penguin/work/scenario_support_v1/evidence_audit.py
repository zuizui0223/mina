"""Cross-artifact evidence audit; an arithmetic pass is not goal completion."""
from pathlib import Path
import hashlib,json
import pandas as pd
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/research_synthesis_v1';OUT.mkdir(exist_ok=True)
read=lambda p:pd.read_csv(ROOT/'outputs'/p)
receipts=[
 'scenario_support_v1/validation.json','scenario_support_v1/joint_validation.json',
 'scenario_support_v1/recent_comparison/overlap_validation.json',
 'long_count_seaice_v1/validation.json','long_ice_timing_v1/validation.json',
 'conditional_response_v1/validation.json']
hashes=[]
for name in receipts:
    receipt=json.loads((ROOT/'outputs'/name).read_text())
    for field in ['inputs','input_sha256']:
        for relative,expected in receipt.get(field,{}).items():
            path=ROOT/relative.replace('\\','/')
            actual=hashlib.sha256(path.read_bytes()).hexdigest()
            assert actual==expected,(name,relative)
            hashes.append(dict(receipt=name,input=path.relative_to(ROOT).as_posix(),sha256=actual))
for name,field in [
 ('ross_ice_temporal_support_v1/validation.json','input_hashes'),
 ('salinity_cluster_sensitivity_v1/validation.json','hashes'),
 ('vegetation_influence_v1/validation.json','hashes'),
 ('ross_movement_pairs_v1/association_validation.json','hashes')]:
    receipt=json.loads((ROOT/'outputs'/name).read_text())
    for relative,expected in receipt[field].items():
        path=ROOT/'outputs'/relative.replace('\\','/')
        actual=hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual==expected,(name,relative)
        hashes.append(dict(receipt=name,input=path.relative_to(ROOT).as_posix(),sha256=actual))
pd.DataFrame(hashes).to_csv(OUT/'input_hash_audit.csv',index=False)

ross_support=read('ross_ensemble_ice_v1/interval_support.csv.gz')
assert len(ross_support)==8469 and ross_support.draws.sum()==4234500
ross_direction=read('ross_directional_exposure_v1/summary.csv')
selected=ross_direction[(ross_direction.product_class=='satellite')&(ross_direction.month==9)&(ross_direction.threshold==.5)&ross_direction.target.isin(['CRZE','ROYD'])]
assert len(selected)==6 and selected.mean_projected_km_day.lt(0).all()
assert selected.bird_years.sum()==170 and selected.positive_bird_years.sum()==29
movement=read('ross_movement_pairs_v1/associations.csv')
selected=movement[(movement.target_choice=='east')&(movement['product']=='satellite')&(movement.threshold==.5)&(movement.month==9)&(movement['mode']=='trip_date')&(movement.deleted_season=='none')]
assert len(selected)==1 and selected.n.item()==515 and selected.trips.item()==169
assert abs(selected.r.item()-(-.013487677204149985))<1e-10
salt_tests=read('salinity_cluster_sensitivity_v1/tests.csv')
assert len(salt_tests)==48 and not salt_tests.fdr_bh.lt(.05).any() and not salt_tests.fdr_by.lt(.05).any()
veg_influence=read('vegetation_influence_v1/comparisons.csv');assert len(veg_influence)==686
counts=read('long_count_seaice_v1/intervals.csv');tests=read('long_count_seaice_v1/associations.csv')
assert len(counts)==301 and counts.site_id.nunique()==33 and counts.region.nunique()==6
assert len(tests)==12 and tests.p.notna().sum()==10 and not tests.fdr_bh.lt(.05).any()
drift=read('drift_block_v1/cohort.csv');drift_tests=read('drift_block_v1/joint_tests.csv')
assert len(drift[drift.scope.eq('all_labels')])==152 and not drift_tests.fdr_bh.lt(.05).any()
climate=read('climate_penguin/macro_monthly_seaice_1991_2020.csv')
assert len(climate)==9600 and climate.complete_month.all()
scenarios=read('conditional_response_v1/conditional_summary.csv')
assert len(scenarios)==288 and (~scenarios.all_sites_physical).sum()==64
forward=read('conditional_response_v1/forward/predictions.csv')
assert len(forward)==198
route=read('chinstrap_winter_v1/route_ice_support.csv')
assert len(route)==114 and route.drift_status.eq('satellite_vector').sum()==0
nests=read('noaa_date_support_v1/nest_date_support.csv')
assert len(nests)==467 and nests.positive_at_first_observation.sum()==365
vegetation=read('vegetation_response_v1/site_species_cohort.csv')
assert len(vegetation)==246
wild=read('climate_penguin/wild_cluster_sensitivity_results.csv')
assert len(wild)==216 and not wild.q_wild_max_bh.lt(.05).any() and not wild.q_wild_max_by.lt(.05).any()
atlas=read('correlation_atlas_v1/correlations.csv');assert len(atlas)==21
salt=read('salinity_sensitivity_v1/specifications.csv');assert len(salt)==48
ndvi=read('vegetation_annual_ndvi_v1/ndvi_count_correlations.csv');assert len(ndvi)==4
four=read('four_environment_scenarios_v1/summary.csv');assert len(four)==288
geometry=read('environment_identifiability_v1/observed_geometry.csv');assert len(geometry)==48
water=read('surface_temperature_projection_v1/matched_site_changes.csv');assert len(water)==984
# New analyses use two explicit path bases in their receipts; do not guess paths.
new_receipts={
 'salinity_site_influence_v1/validation.json':ROOT,
 'salinity_scenario_component_v1/validation.json':ROOT/'outputs',
 'surface_temperature_projection_v1/alignment_validation.json':ROOT,
 'four_environment_scenarios_v1/validation.json':ROOT/'outputs',
 'environment_identifiability_v1/validation.json':ROOT,
 'september_snow_v1/association_validation.json':ROOT,
 'scenario_specification_comparison_v1/validation.json':ROOT/'outputs',
}
for name,base in new_receipts.items():
    receipt=json.loads((ROOT/'outputs'/name).read_text())
    for field in ['inputs','input_sha256']:
        for relative,expected in receipt.get(field,{}).items():
            path=base/relative.replace('\\','/')
            actual=hashlib.sha256(path.read_bytes()).hexdigest()
            assert actual==expected,(name,relative)
            hashes.append(dict(receipt=name,input=path.relative_to(ROOT).as_posix(),sha256=actual))
pd.DataFrame(hashes).to_csv(OUT/'input_hash_audit.csv',index=False)
overlay=read('ndvi_vegetation_overlay_v1/support_summary.csv');assert overlay.loc[overlay['mask'].eq('pixel_center'),'pairs_100_mapped_pixels'].item()==0
landsat=read('landsat_vegetation_support_v1/paired_qa_support.csv');assert len(landsat)==96
snow=read('september_snow_v1/september_summary.csv');assert len(snow)==1166
snow_tests=read('september_snow_v1/regional_correlations.csv');assert len(snow_tests)==36
scale=read('settlement_origin_refresh_v1/source_slope_crosscheck.csv')
assert len(scale)==32 and scale.matches.all() and scale.source_n.eq(scale.csv_n).all()
assert scale.csv_n.sum()==271 and (scale.csv_slope-scale.paper_slope).abs().max()<=.0005
spec=read('scenario_specification_comparison_v1/paired_specifications.csv')
assert len(spec)==288 and spec.comparison_available.sum()==224 and spec.opposite_sign.eq(True).sum()==112
yearspec=read('scenario_specification_comparison_v1/year_adjustment_comparisons.csv')
assert len(yearspec)==288 and yearspec.comparison_available.sum()==224 and yearspec.opposite_sign.eq(True).sum()==78
requirements=[
 {'requirement':'Existing data and frozen results preserved','status':'supported','evidence':['long_count_seaice_v1/intervals.csv','relationship_response_v1/cohort.csv'],'limit':'Different cohorts remain separate; new exploratory analyses do not overwrite frozen claims'},
 {'requirement':'Macro breeding-count/environment relationships','status':'supported_with_scope_limits','evidence':['long_count_seaice_v1/associations.csv'],'limit':'Adelie 33 sites / 301 annual intervals; timing-supported subset geographically concentrated'},
 {'requirement':'Sea-ice timing and drift versus observable behavior','status':'partial_identification','evidence':['long_ice_timing_v1/transition_support.csv','drift_block_v1/joint_tests.csv'],'limit':'Onset-date paired support 0-2 timing-supported intervals per definition; conditional drift association not transport assistance'},
 {'requirement':'Independent tracking and phenology availability/year alignment','status':'audited_with_unresolved_conditions','evidence':['chinstrap_winter_v1/route_ice_support.csv','noaa_date_support_v1/nest_date_support.csv','climate_penguin/phenology_audit.md'],'limit':'No adopted satellite drift at selected tracks; colony settlement calendar origin remains unconfirmed'},
 {'requirement':'Future warming/sea-ice conditional connection and uncertainty','status':'conditional_sensitivity_delivered_not_calibrated','evidence':['conditional_response_v1/conditional_summary.csv','conditional_response_v1/forward/summary.csv'],'limit':'Index shifts only; unvalidated climate transformation; broad coefficient and extrapolation uncertainty'},
 {'requirement':'Vegetation/snow and breeding-use sequence requested in research goal v2','status':'measured_support_with_unresolved_classification','evidence':['vegetation_annual_ndvi_v1/ndvi_count_correlations.csv','ndvi_vegetation_overlay_v1/support_summary.csv','vegetation_expansion_pixels_v1/one_two_date_comparison.csv','landsat_vegetation_support_v1/paired_qa_support.csv'],'limit':'Annual NDVI measured, but mapped vegetation overlap is sparse; expanded Sentinel comparison lacks two-date repeated support; Landsat support depends on Tier 2 geometry and Jan-Feb pooling; breeding-patch classification unverified'},
 {'requirement':'Mechanism and uncertainty claims separated without invented predictions','status':'supported','evidence':['conditional_response_v1/REPORT_JA.md','chinstrap_winter_v1/ROUTE_QC_JA.md'],'limit':'No causal transport effect, absolute return date, or future nest count claimed'}]
requirements[4]['evidence'] += ['four_environment_scenarios_v1/summary.csv','surface_temperature_projection_v1/matched_site_changes.csv','environment_identifiability_v1/observed_geometry.csv']
requirements[4]['limit']='Two- and four-environment conditional index scenarios delivered; specification-dependent direction, extrapolation, unvalidated tos/potential-temperature proxy and climate transformations remain'
requirements[3]['evidence'] += ['settlement_origin_refresh_v1/source_slope_crosscheck.csv','return_tracking_refresh_v1/PRIMARY_SOURCES_JA.md','ross_phase_reference_v1/REPORT_JA.md']
requirements[3]['limit']='Day-scale supported by 32 published slope matches; absolute calendar origin still unknown. Independent route drift unavailable; published Ross seasonal contrast is not independent mechanism verification.'
requirements[4]['evidence'] += ['scenario_specification_comparison_v1/paired_specifications.csv','scenario_specification_comparison_v1/year_adjustment_comparisons.csv']
requirements[4]['limit']='Conditional changes on a supported day scale delivered; 112/224 model and 78/224 year-adjustment sign reversals. Absolute dates, causal effects and calibrated forecasts remain unproven.'
requirements[5]['evidence'] += ['september_snow_v1/september_summary.csv','september_snow_v1/regional_correlations.csv']
requirements.append({'requirement':'Updated v2 snow, lag and nonlinear hypothesis comparisons','status':'incomplete',
 'evidence':['climate_penguin/RESEARCH_GOAL_V2.md','nonlinear_association_v1/shape_sensitivity.csv','previous_september_v1/correlations.csv','previous_september_v1/cluster_sensitivity.csv'],
 'limit':'48 quadratic checks, current/previous September comparisons with 72 cluster sensitivity tests, and 36 regional snow comparisons delivered; local vegetation/snow sequence and mechanistic carryover remain unverified'})
requirements[-1]['evidence'] += ['september_snow_v1/regional_correlations.csv']
requirements[2]['evidence'] += ['ross_directional_exposure_v1/summary.csv','ross_movement_pairs_v1/associations.csv']
requirements[2]['limit']='Broad monthly associations and directional Ross exposure/movement comparison delivered. Ross September matched 515 intervals/169 bird-years, trip/date r=-0.01349; shared GLS position errors and short satellite support prevent independent assistance inference.'
requirements[3]['evidence'] += ['pointblue_full_positions_v1/trip_support.csv','ross_ensemble_ice_v1/validation.json','ross_ice_temporal_support_v1/colony_year_summary.csv','ross_movement_pairs_v1/independent_validation.json']
requirements[3]['limit']='Full Ross positions acquired and aligned: 188 retained bird-years, 8469 intervals. Satellite support concentrated in September 27-30; same published cohort, not independent replication. Day-scale supported, absolute calendar origin and independent return dates unresolved.'
requirements[5]['evidence'] += ['salinity_cluster_sensitivity_v1/tests.csv','vegetation_influence_v1/comparisons.csv']
requirements[5]['limit'] += '; 48 salinity sensitivity tests have no BH/BY discoveries; 686 static-vegetation sensitivity fits expose geographic/observation dependence, not annual vegetation effects'
for r in requirements:
    for name in r['evidence']:assert (ROOT/'outputs'/name).exists()
result={'audit_passed':True,'goal_complete':False,'verified_input_hash_references':len(hashes),'requirements':requirements,
 'next_unresolved_work':'Ross environmental direction and model-movement association are now computed; independent transport mechanism remains unidentified. Local vegetation/breeding-patch sequence, absolute calendar origin and calibrated extrapolation unresolved. Existing-data correlation and conditional scenario outputs delivered; do not treat these as causal transport or calibrated future nest-count predictions.'}
(OUT/'requirements_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'audit_passed':True,'goal_complete':False,'verified_hash_references':len(hashes),'requirement_rows':len(requirements)}))
