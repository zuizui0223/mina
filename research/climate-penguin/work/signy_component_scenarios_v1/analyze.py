"""Conditional responses at future mean sea ice, with fixed local associations."""
from pathlib import Path
import argparse
import hashlib
import json

import numpy as np
import pandas as pd
from scipy.special import expit
import statsmodels.api as sm

ROOT=Path(__file__).resolve().parents[2]
WORK=Path(__file__).resolve().parent
RESPONSES={'frequency':'positive_mass_frequency',
           'composition':'conditional_fish_fraction',
           'mean_response':'mean_fish_fraction'}


def annual_ice(frame, years):
    years=list(years)
    data=frame[frame.year.isin(years)].copy()
    if set(data.units)!={'percent'}:
        raise ValueError('SIC units must be percent')
    if data.duplicated(['year','month']).any():
        raise ValueError('duplicate month')
    if set(data.year)!=set(years) or not data.groupby('year').month.apply(
            lambda values: len(values)==4 and set(values)=={8,9,10,11}).all():
        raise ValueError('four complete August-November months required for every year')
    if not np.isfinite(data.value).all() or not data.value.between(0,100).all():
        raise ValueError('invalid unadjusted SIC')
    return data.groupby('year').value.mean().reindex(years)


def support_info(values, limits):
    values=np.asarray(values,float)
    if values.size==0 or not np.isfinite(values).all():
        raise ValueError('finite climate values required')
    low,high=limits
    inside=(values>=low)&(values<=high)
    return {'n_years':len(values),'mean_sic':float(values.mean()),
            'annual_min_sic':float(values.min()),'annual_max_sic':float(values.max()),
            'mean_within_observed_range':bool(low<=values.mean()<=high),
            'n_in_observed_range':int(inside.sum()),
            'fraction_in_observed_range':float(inside.mean()),
            'n_outside_physical_range':int(((values<0)|(values>100)).sum())}


def fit_response(x,y):
    x,y=np.asarray(x,float),np.asarray(y,float)
    if len(x)!=len(y) or len(x)<3 or not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError('complete paired seasons required')
    if np.ptp(x)==0 or np.ptp(y)==0 or not ((0<=y)&(y<=1)).all():
        raise ValueError('nonconstant SIC and bounded varying response required')
    design=np.column_stack([np.ones(len(x)),x/10])
    ols=sm.OLS(y,design).fit()
    robust=ols.get_robustcov_results(cov_type='HC3',use_t=True)
    fractional=sm.GLM(y,design,family=sm.families.Binomial()).fit()
    if not fractional.converged or not np.isfinite(fractional.params).all():
        raise ValueError('fractional-logit fit failed')
    interval=robust.conf_int()[1]
    return {'n_seasons':len(x),'response_mean':float(y.mean()),
            'ols_params':ols.params.tolist(),'slope_per_10pp':float(ols.params[1]),
            'hc3_slope_95_low':float(interval[0]),'hc3_slope_95_high':float(interval[1]),
            'hc3_covariance':robust.cov_params().tolist(),'hc3_t_df':int(robust.df_resid),
            'fractional_logit_params':fractional.params.tolist(),
            'fractional_logit_converged':bool(fractional.converged)}


def fit_components(frame):
    if not np.allclose(frame.mean_fish_fraction,
                       frame.positive_mass_frequency*frame.conditional_fish_fraction,
                       rtol=1e-12,atol=1e-12):
        raise ValueError('observed component identity changed')
    return {key:fit_response(frame.sic_aug_nov,frame[column]) for key,column in RESPONSES.items()}


def change_interval(slope_interval,delta_sic):
    return tuple(float(value) for value in np.sort(np.asarray(slope_interval)*delta_sic/10))


def predict_response(fit,reference_sic,target_sic,limits):
    low,high=limits
    if not low<=reference_sic<=high:
        raise ValueError('reference outside observed support')
    if not np.isfinite(target_sic):
        raise ValueError('target SIC must be finite')
    reference=np.array([1.,reference_sic/10]);future=np.array([1.,target_sic/10])
    supported=bool(low<=target_sic<=high)
    result={'reference_sic':float(reference_sic),'target_sic':float(target_sic),
            'delta_sic_pp':float(target_sic-reference_sic),'within_observed_sic':supported,
            'reference_ols':float(reference@fit['ols_params']),
            'reference_fractional_logit':float(expit(reference@fit['fractional_logit_params']))}
    for name in ['future_ols','change_ols','change_ci_low','change_ci_high',
                 'future_fractional_logit','change_fractional_logit']:
        result[name]=np.nan
    if supported:
        change=fit['slope_per_10pp']*(target_sic-reference_sic)/10
        interval=change_interval((fit['hc3_slope_95_low'],fit['hc3_slope_95_high']),target_sic-reference_sic)
        result.update(future_ols=float(future@fit['ols_params']),change_ols=float(change),
                      change_ci_low=interval[0],change_ci_high=interval[1],
                      future_fractional_logit=float(expit(future@fit['fractional_logit_params'])))
        result['change_fractional_logit']=result['future_fractional_logit']-result['reference_fractional_logit']
    return result


def verify_inputs():
    manifest=json.loads((WORK/'INPUT_MANIFEST.json').read_text())
    for entry in manifest:
        if hashlib.sha256((ROOT/entry['path']).read_bytes()).hexdigest()!=entry['sha256']:
            raise ValueError('pinned input changed: '+entry['path'])
    return manifest


def climate_inputs(limits):
    outputs=ROOT/'outputs'
    observed=pd.read_csv(outputs/'climate_penguin/macro_monthly_seaice_1991_2020.csv')
    observed=observed.query('site_id=="GOPT" and inner_km==0 and 1995<=year<=2014').copy()
    if len(observed)!=80 or not observed.complete_month.eq(True).all():
        raise ValueError('incomplete observed reference climate')
    observed=observed.rename(columns={'sic_mean':'value'}).assign(units='percent')
    observed_annual=annual_ice(observed,range(1995,2015))
    reference=float(observed_annual.mean())
    metadata=pd.read_csv(outputs/'cmip6_projection_v1/seasonal_climatologies.csv')
    metadata=metadata.query('site_id=="GOPT" and variable_id=="siconc"')
    if set(metadata.location_id)!={'loc020'}:
        raise ValueError('unexpected GOPT location')
    scenarios=[];references=[];annual_rows=[]
    for (model,member),group in metadata.groupby(['source_id','member_id'],sort=True):
        if group.distance_km.nunique()!=1 or group.grid_cell_id.nunique()!=1:
            raise ValueError('grid location changed between experiments')
        series={}
        for experiment in ['historical','ssp245','ssp585']:
            path=outputs/f'cmip6_projection_v1/monthly_{model}_{member}_siconc_{experiment}.csv.gz'
            frame=pd.read_csv(path)
            frame=frame[frame.location_id.eq('loc020')]
            if set(frame.source_id)!={model} or set(frame.member_id)!={member} or set(frame.experiment_id)!={experiment} or set(frame.variable_id)!={'siconc'}:
                raise ValueError('climate source identifiers changed')
            series[experiment]=frame
        historical=annual_ice(series['historical'],range(1995,2015))
        historical_mean=float(historical.mean())
        offset=reference-historical_mean
        corrected_historical=historical+offset
        common={'model':model,'member':member,'location_id':'loc020',
                'model_cell_distance_km':float(group.distance_km.iloc[0]),
                'grid_cell_id':group.grid_cell_id.iloc[0]}
        references.append({**common,'observed_reference_sic':reference,
                           'model_historical_sic':historical_mean,
                           'historical_model_bias_pp':historical_mean-reference,
                           **support_info(corrected_historical,limits)})
        windows=[('historical','1995-2014',historical)]
        for experiment in ['ssp245','ssp585']:
            for first,last in [(2041,2060),(2081,2100)]:
                annual=annual_ice(series[experiment],range(first,last+1))
                corrected=annual+offset
                info=support_info(corrected,limits)
                scenarios.append({**common,'scenario':experiment,'period':f'{first}-{last}',
                    'observed_reference_sic':reference,'model_historical_sic':historical_mean,
                    'historical_model_bias_pp':historical_mean-reference,
                    'model_future_sic':float(annual.mean()),
                    'model_delta_sic_pp':float(annual.mean()-historical_mean),
                    'delta_adjusted_sic':float(corrected.mean()),
                    'within_observed_diet_sic_range':info['mean_within_observed_range'],
                    'future_annual_support_count':info['n_in_observed_range'],
                    'future_annual_support_fraction':info['fraction_in_observed_range'],
                    'future_annual_sic_min':info['annual_min_sic'],
                    'future_annual_sic_max':info['annual_max_sic'],
                    'future_annual_unphysical_count':info['n_outside_physical_range'],
                    'n_future_years':info['n_years']})
                windows.append((experiment,f'{first}-{last}',annual))
        for experiment,period,annual in windows:
            for year,value in annual.items():
                corrected=float(value+offset)
                annual_rows.append({**common,'experiment':experiment,'period':period,'year':int(year),
                    'model_annual_sic':float(value),'delta_adjusted_sic':corrected,
                    'within_observed_diet_sic_range':bool(limits[0]<=corrected<=limits[1]),
                    'within_physical_range':bool(0<=corrected<=100)})
    scenarios=pd.DataFrame(scenarios)
    old=pd.read_csv(outputs/'diet_niche_scenarios_v1/conditional_scenarios.csv')
    keys=['model','member','scenario','period']
    compared=scenarios.merge(old,on=keys,suffixes=('_new','_old'),validate='one_to_one')
    if len(compared)!=12:
        raise ValueError('expected twelve climate conditions')
    for column in ['observed_reference_sic','model_historical_sic','model_future_sic',
                   'model_delta_sic_pp','delta_adjusted_sic','model_cell_distance_km']:
        if not np.allclose(compared[column+'_new'],compared[column+'_old'],rtol=1e-12,atol=1e-12):
            raise ValueError('previous climate scenario differs: '+column)
    return reference,scenarios,pd.DataFrame(references),pd.DataFrame(annual_rows),observed_annual


def run(out):
    manifest=verify_inputs()
    prior=ROOT/'outputs/signy_diet_components_v1'
    frame=pd.read_csv(prior/'gentoo_primary_nine_seasons.csv').sort_values('year')
    if frame.year.tolist()!=list(range(2001,2010)) or frame.n_stomachs.sum()!=73:
        raise ValueError('original ecological cohort changed')
    limits=(float(frame.sic_aug_nov.min()),float(frame.sic_aug_nov.max()))
    reference,climates,reference_climates,annual_climates,observed_annual=climate_inputs(limits)
    fits=fit_components(frame)
    old=json.loads((prior/'summary.json').read_text())
    for response,fit in fits.items():
        expected=old['mean_response_association'] if response=='mean_response' else old['component_associations'][response]
        for key in ['slope_per_10pp','hc3_slope_95_low','hc3_slope_95_high']:
            if not np.isclose(fit[key],expected[key],rtol=1e-11,atol=1e-12):
                raise ValueError('previous response coefficient changed: '+response+' '+key)
    rows=[]
    for climate in climates.to_dict('records'):
        for response,fit in fits.items():
            rows.append({**climate,'response':response,
                         **predict_response(fit,reference,climate['delta_adjusted_sic'],limits)})
    predictions=pd.DataFrame(rows)
    reductions=pd.DataFrame([{'reduction_sic_pp':reduction,'response':response,
         **predict_response(fit,reference,reference-reduction,limits)}
         for reduction in [5.,10.,20.,30.] for response,fit in fits.items()])
    terms=pd.read_csv(prior/'annual_accounting_terms.csv').sort_values('year')
    if not np.array_equal(terms.year,frame.year):
        raise ValueError('accounting seasons changed')
    design=np.column_stack([np.ones(len(frame)),frame.sic_aug_nov/10])
    slopes={key:float(np.linalg.lstsq(design,terms[key],rcond=None)[0][1])
            for key in ['frequency','composition','covariation']}
    if not np.isclose(sum(slopes.values()),fits['mean_response']['slope_per_10pp'],rtol=1e-12,atol=1e-12):
        raise ValueError('accounting slope identity failed')
    accounting=[]
    for climate in climates.to_dict('records'):
        supported=climate['within_observed_diet_sic_range']
        factor=(climate['delta_adjusted_sic']-reference)/10
        parts={key+'_change':slope*factor if supported else np.nan for key,slope in slopes.items()}
        total=sum(parts.values())
        mean=fits['mean_response']['slope_per_10pp']*factor if supported else np.nan
        accounting.append({**climate,**parts,'sum_component_changes':total,
                           'mean_response_change':mean,'identity_error':total-mean})
    accounting=pd.DataFrame(accounting)
    supported=predictions[predictions.within_observed_sic]
    if len(predictions)!=36 or len(supported)!=33:
        raise ValueError('expected 36 rows with 33 supported responses')
    if not supported.future_ols.between(0,1).all() or not supported.future_fractional_logit.between(0,1).all():
        raise ValueError('fitted supported point outside response bounds; do not clip')
    if not predictions.loc[~predictions.within_observed_sic,'future_ols'].isna().all():
        raise ValueError('unsupported ecological prediction was retained')
    shape={}
    for response,group in supported.groupby('response',sort=False):
        shape[response]={'n_conditions':len(group),
            'n_negative_ols_changes':int(group.change_ols.lt(0).sum()),
            'n_negative_fractional_logit_changes':int(group.change_fractional_logit.lt(0).sum()),
            'max_absolute_future_level_difference':float((group.future_ols-group.future_fractional_logit).abs().max()),
            'max_absolute_change_difference':float((group.change_ols-group.change_fractional_logit).abs().max()),
            'ols_future_min':float(group.future_ols.min()),'ols_future_max':float(group.future_ols.max()),
            'ols_change_min':float(group.change_ols.min()),'ols_change_max':float(group.change_ols.max())}
    reference_predictions={key:predict_response(fit,reference,reference,limits)['reference_ols'] for key,fit in fits.items()}
    summary={'analysis_date':'2026-11-06','n_seasons':9,'n_stomachs':73,
        'reference_sic':reference,'observed_diet_sic_range':list(limits),
        'n_climate_models':3,'n_climate_conditions':12,'n_supported_mean_conditions':11,
        'n_supported_response_rows':len(supported),'ols_reference_responses':reference_predictions,
        'reference_product_of_fitted_components':reference_predictions['frequency']*reference_predictions['composition'],
        'shape_sensitivity':shape,'accounting_slopes_per_10pp':slopes,
        'maximum_accounting_change_identity_error':float(accounting.identity_error.abs().max()),
        'n_scenarios_with_all_future_years_in_support':int(climates.future_annual_support_count.eq(20).sum()),
        'n_supported_means_with_some_unsupported_future_years':int((climates.within_observed_diet_sic_range & climates.future_annual_support_count.lt(20)).sum()),
        'n_unphysical_corrected_annual_climate_values':int((~annual_climates.within_physical_range).sum()),
        'estimand':'separate conditional response at future mean SIC; not expected annual future diet or population change',
        'uncertainty':'OLS change intervals include only HC3 t7 coefficient uncertainty at a fixed climate delta; climate models are labelled conditions, not probability samples',
        'relation_assumption':'observed local SIC-response and measurement relationships remain invariant',
        'source_inputs':len(manifest)}
    out.mkdir(parents=True,exist_ok=True)
    for name,data in [('climate_scenarios',climates),('climate_reference',reference_climates),
                      ('annual_climate_support',annual_climates),('component_scenarios',predictions),
                      ('controlled_reductions',reductions),('slope_accounting_scenarios',accounting)]:
        data.to_csv(out/f'{name}.csv',index=False,lineterminator='\n')
    observed_annual.rename('sic_aug_nov').to_csv(out/'observed_reference_annual_sic.csv',lineterminator='\n')
    for name,value in [('fit_parameters',fits),('summary',summary),('source_manifest',manifest)]:
        (out/f'{name}.json').write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=ROOT/'outputs/signy_component_scenarios_v1')
    run(parser.parse_args().out)
