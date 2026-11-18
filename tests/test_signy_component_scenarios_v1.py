"""Scientific edge cases for the conditional component scenarios."""
from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd
import pytest

PATH=Path(__file__).parents[1]/'research/climate-penguin/work/signy_component_scenarios_v1/analyze.py'


def analysis():
    assert PATH.exists(), 'Component scenario analysis not implemented'
    spec=importlib.util.spec_from_file_location('component_scenarios',PATH)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def monthly():
    return pd.DataFrame({'year':[2001]*4+[2002]*4,'month':[8,9,10,11]*2,
                         'value':[0.,0.,0.,100.,20.,40.,60.,80.], 'units':['percent']*8})


def test_climate_uses_four_equal_months_before_equal_years():
    annual=analysis().annual_ice(monthly(),[2001,2002])
    assert annual.loc[2001]==pytest.approx(25.)
    assert annual.loc[2002]==pytest.approx(50.)
    assert annual.mean()==pytest.approx(37.5)


@pytest.mark.parametrize('defect',['missing','duplicate','wrong_units'])
def test_climate_rejects_incomplete_duplicate_or_wrong_unit_support(defect):
    frame=monthly()
    if defect=='missing': frame=frame.iloc[:-1]
    elif defect=='duplicate': frame=pd.concat([frame,frame.iloc[[0]]],ignore_index=True)
    else: frame['units']='fraction'
    with pytest.raises(ValueError): analysis().annual_ice(frame,[2001,2002])


def test_supported_mean_does_not_imply_supported_climate_years():
    result=analysis().support_info([20.,60.],(30.,50.))
    assert result['mean_within_observed_range'] is True
    assert result['n_in_observed_range']==0
    assert result['fraction_in_observed_range']==0


def test_negative_climate_delta_scales_and_reorders_coefficient_interval():
    mod=analysis()
    assert mod.change_interval((.02,.2),-15.)==pytest.approx((-.3,-.03))
    assert mod.change_interval((-.04,.22),-10.)==pytest.approx((-.22,.04))


def test_outside_observed_support_withholds_both_response_shapes():
    mod=analysis()
    fit=mod.fit_response([10.,20.,30.,40.],[.2,.25,.45,.7])
    row=mod.predict_response(fit,25.,5.,(10.,40.))
    assert row['within_observed_sic'] is False
    assert np.isfinite(row['reference_ols'])
    for field in ['future_ols','change_ols','change_ci_low','change_ci_high',
                  'future_fractional_logit','change_fractional_logit']:
        assert np.isnan(row[field])


def test_overall_mean_is_predicted_separately_from_product_of_fitted_components():
    mod=analysis()
    frame=pd.DataFrame({'sic_aug_nov':[0.,1.,2.,3.],
                        'positive_mass_frequency':[.2,.4,.6,.8],
                        'conditional_fish_fraction':[.8,.2,.7,.3]})
    frame['mean_fish_fraction']=frame.positive_mass_frequency*frame.conditional_fish_fraction
    fits=mod.fit_components(frame)
    predicted={key:mod.predict_response(fit,1.5,1.5,(0.,3.))['future_ols'] for key,fit in fits.items()}
    assert predicted['mean_response']==pytest.approx(.225)
    assert predicted['frequency']*predicted['composition']==pytest.approx(.25)
    assert predicted['mean_response'] != pytest.approx(predicted['frequency']*predicted['composition'])
