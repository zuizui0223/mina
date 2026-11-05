"""Conditional diet-gap sensitivity, not validated future ecological forecasting."""
from pathlib import Path
import argparse,hashlib,json
import numpy as np
import pandas as pd
import statsmodels.api as sm

def run(out):
    out.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parents[2];outputs=root/'outputs'
    path=outputs/'niche_multiscale_v1/annual_distances.csv'
    d=pd.read_csv(path).query('variant=="full" and pair=="Gentoo-vs-others" and metric=="fish"').sort_values('year')
    assert len(d)==9
    x=d.sic_aug_nov.to_numpy();y=d.distance.to_numpy();X=sm.add_constant(x)
    ols=sm.OLS(y,X).fit();rob=ols.get_robustcov_results(cov_type='HC3',use_t=True)
    frac=sm.GLM(y,X,family=sm.families.Binomial()).fit()
    ipath=outputs/'climate_penguin/macro_monthly_seaice_1991_2020.csv'
    ice=pd.read_csv(ipath).query('site_id=="GOPT" and inner_km==0 and 1995<=year<=2014')
    assert len(ice)==80 and ice.complete_month.all() and not ice.duplicated(['year','month']).any()
    baseline=ice.sic_mean.mean();baseline_ols=float(ols.predict([1,baseline])[0]);baseline_frac=float(frac.predict([1,baseline])[0])
    support=pd.read_csv(outputs/'cmip6_projection_v1/seasonal_climatologies.csv').query('site_id=="GOPT" and variable_id=="siconc"')
    assert support.location_id.nunique()==1
    location=support.location_id.iloc[0]
    changes=[];manifest=[]
    for model,member in support[['source_id','member_id']].drop_duplicates().itertuples(index=False,name=None):
        monthly={}
        for experiment in ['historical','ssp245','ssp585']:
            p=outputs/f'cmip6_projection_v1/monthly_{model}_{member}_siconc_{experiment}.csv.gz'
            data=pd.read_csv(p).query('location_id==@location')
            assert set(data.units)=={'percent'}
            assert not data.duplicated(['year','month']).any() and data.month.isin([8,9,10,11]).all() and data.value.notna().all()
            assert data.groupby('year').size().eq(4).all()
            monthly[experiment]=data.groupby('year').value.mean()
            manifest.append(dict(file=str(p.relative_to(root)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
        hist=monthly['historical'].loc[1995:2014];assert len(hist)==20
        for exp in ['ssp245','ssp585']:
            for lo,hi in [(2041,2060),(2081,2100)]:
                annual=monthly[exp].loc[lo:hi];assert len(annual)==20
                delta=annual.mean()-hist.mean();future=baseline+delta
                supported=bool(x.min()<=future<=x.max())
                change_interval=np.sort(rob.conf_int()[1]*delta)
                row=dict(model=model,member=member,scenario=exp,period=f'{lo}-{hi}',location_id=location,
                         observed_reference_sic=baseline,model_historical_sic=hist.mean(),historical_model_bias_pp=hist.mean()-baseline,
                         model_future_sic=annual.mean(),model_delta_sic_pp=delta,delta_adjusted_sic=future,
                         model_cell_distance_km=float(support[support.source_id==model].distance_km.iloc[0]),
                         within_observed_diet_sic_range=supported,observed_diet_sic_min=x.min(),observed_diet_sic_max=x.max(),
                         fitted_reference_gap_ols=baseline_ols,fitted_reference_gap_fractional_logit=baseline_frac,
                         conditional_future_gap_ols=float(ols.predict([1,future])[0]) if supported else np.nan,
                         conditional_gap_change_ols=float(ols.params[1]*delta) if supported else np.nan,
                         change_coefficient_only_ci_low=change_interval[0] if supported else np.nan,
                         change_coefficient_only_ci_high=change_interval[1] if supported else np.nan,
                         conditional_future_gap_fractional_logit=float(frac.predict([1,future])[0]) if supported else np.nan,
                         conditional_gap_change_fractional_logit=float(frac.predict([1,future])[0])-baseline_frac if supported else np.nan,
                         estimand='conditional gap at future mean SIC, not mean of future annual diet; fixed ecological relation assumption')
                changes.append(row)
    scenarios=pd.DataFrame(changes);scenarios.to_csv(out/'conditional_scenarios.csv',index=False,lineterminator='\n')
    sensitivity=[]
    for reduction in [5,10,20,30]:
        future=baseline-reduction;supported=bool(x.min()<=future<=x.max())
        ci=np.sort(rob.conf_int()[1]*(-reduction))
        sensitivity.append(dict(reference_sic=baseline,reduction_pp=reduction,scenario_sic=future,in_range=supported,
            conditional_gap_change=float(-reduction*ols.params[1]) if supported else np.nan,coefficient_only_ci_low=ci[0] if supported else np.nan,coefficient_only_ci_high=ci[1] if supported else np.nan,
            fractional_logit_change=float(frac.predict([1,future])[0])-baseline_frac if supported else np.nan))
    pd.DataFrame(sensitivity).to_csv(out/'ice_reduction_sensitivity.csv',index=False,lineterminator='\n')
    # Four rolling origins, after earlier exploratory inspection of these data.
    predictions=[]
    for i in range(5,9):
        tx=x[:i];ty=y[:i];xx=sm.add_constant(tx)
        predictions.append(dict(year=int(d.iloc[i].year),observed=y[i],past_mean=ty.mean(),
            ols=float(sm.OLS(ty,xx).fit().predict([1,x[i]])[0]),
            fractional_logit=float(sm.GLM(ty,xx,family=sm.families.Binomial()).fit().predict([1,x[i]])[0]),n_training_years=i))
    pred=pd.DataFrame(predictions);pred.to_csv(out/'rolling_origin_predictions.csv',index=False,lineterminator='\n')
    scores=[dict(model=m,n_test_years=4,mae=float(np.mean(np.abs(pred[m]-pred.observed))),rmse=float(np.sqrt(np.mean((pred[m]-pred.observed)**2)))) for m in ['past_mean','ols','fractional_logit']]
    pd.DataFrame(scores).to_csv(out/'rolling_origin_scores.csv',index=False,lineterminator='\n')
    # Independent slope arithmetic and all four monthly values reconstructed above.
    beta=np.sum((x-x.mean())*(y-y.mean()))/np.sum((x-x.mean())**2)
    assert np.isclose(beta,ols.params[1]) and scenarios.shape[0]==12
    assert scenarios.loc[~scenarios.within_observed_diet_sic_range,'conditional_future_gap_ols'].isna().all()
    assert scenarios.loc[scenarios.within_observed_diet_sic_range,'conditional_future_gap_ols'].between(0,1).all()
    summary=dict(n_species=3,n_islands=1,n_years=9,observed_sic_range=[x.min(),x.max()],reference_sic=baseline,
        slope_per_10pp=ols.params[1]*10,hc3_slope_ci_per_10pp=(rob.conf_int()[1]*10).tolist(),
        n_supported_scenario_means=int(scenarios.within_observed_diet_sic_range.sum()),n_scenario_means=12,
        fitted_reference_gap_ols=baseline_ols,fitted_reference_gap_fractional_logit=baseline_frac,
        models_scores=scores,checks='monthly units/window support, 12 deltas, independent slope, no unsupported response, supported responses in [0,1] pass',
        limitations=['conditional sensitivity, not validated warming-causal forecast','linear annual association is assumed invariant for a future mean climate','fractional-logit alternative evaluated at future mean, not expected annual gap (nonlinearity)','model delta stationarity and coastal representation unvalidated','historical diet cohort 2001-2009; reference 1995-2014 gap is fitted, not observed','coefficient CI omits future climate, ecological drift and serial dependence','three climate models chosen by availability, not probability ensemble'])
    for p in [path,ipath]:manifest.append(dict(file=str(p.relative_to(root)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8',newline='\n')
    (out/'source_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8',newline='\n')
    print(json.dumps(summary,indent=2));print(scenarios[['model','scenario','period','model_delta_sic_pp','delta_adjusted_sic','conditional_gap_change_ols','conditional_gap_change_fractional_logit']].to_string(index=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);run(p.parse_args().out)
