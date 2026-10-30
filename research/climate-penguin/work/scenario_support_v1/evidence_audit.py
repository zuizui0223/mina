"""Cross-artifact evidence audit; an arithmetic pass is not goal completion."""
from pathlib import Path
import hashlib,json
import pandas as pd
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'outputs/research_synthesis_v1';OUT.mkdir(exist_ok=True)
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
pd.DataFrame(hashes).to_csv(OUT/'input_hash_audit.csv',index=False)
read=lambda p:pd.read_csv(ROOT/'outputs'/p)
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
requirements.append({'requirement':'Updated v2 snow, lag and nonlinear hypothesis comparisons','status':'incomplete',
 'evidence':['climate_penguin/RESEARCH_GOAL_V2.md','nonlinear_association_v1/shape_sensitivity.csv','previous_september_v1/correlations.csv','previous_september_v1/cluster_sensitivity.csv'],
 'limit':'48 quadratic checks and current/previous September comparisons with 72 cluster sensitivity tests delivered; validated annual snow/vegetation sequence and mechanistic carryover identification remain incomplete'})
for r in requirements:
    for name in r['evidence']:assert (ROOT/'outputs'/name).exists()
result={'audit_passed':True,'goal_complete':False,'verified_input_hash_references':len(hashes),'requirements':requirements,
 'next_unresolved_work':'Validated vegetation/breeding-patch measurements, calendar origin and return-route identification, and climate-scenario calibration remain unresolved; correlation-first results and conditional index scenarios delivered'}
(OUT/'requirements_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'audit_passed':True,'goal_complete':False,'verified_hash_references':len(hashes),'requirement_rows':len(requirements)}))
