## Table_1_observed_support

| year | n_Adelie | n_Chinstrap | n_Gentoo | sic_aug_nov | distance |
| --- | --- | --- | --- | --- | --- |
| 2001 | 50 | 50 | 10 | 23.433 | 0.444 |
| 2002 | 40 | 40 | 10 | 54.885 | 0.224 |
| 2003 | 39 | 40 | 9 | 21.901 | 0.110 |
| 2004 | 40 | 40 | 10 | 23.872 | 0.003 |
| 2005 | 40 | 40 | 7 | 45.130 | 0.415 |
| 2006 | 40 | 40 | 7 | 65.232 | 0.745 |
| 2007 | 40 | 40 | 8 | 66.683 | 0.830 |
| 2008 | 30 | 30 | 6 | 22.899 | 0.169 |
| 2009 | 30 | 30 | 6 | 44.641 | 0.344 |

## Table_2_effects_and_inference

| metric | n_years | r | slope_per_10pp | hc3_low | hc3_high | detrended_r | loo_min | loo_max | p_exact | p_max3 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fish | 9 | 0.784 | 0.118 | 0.019 | 0.217 | 0.766 | 0.689 | 0.888 | 0.013 | 0.034 |
| size_assumed_common_scale | 9 | 0.380 | 0.137 | -0.198 | 0.471 | 0.339 | 0.224 | 0.564 | 0.303 | 0.618 |
| stage_labels | 9 | 0.345 | 0.024 | -0.028 | 0.075 | 0.330 | 0.185 | 0.466 | 0.379 | 0.684 |

## Table_3_conditional_sensitivity

| reference_sic | reduction_pp | scenario_sic | in_range | conditional_gap_change | coefficient_only_ci_low | coefficient_only_ci_high | fractional_logit_change |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 48.683 | 5 | 43.683 | True | -0.059 | -0.108 | -0.009 | -0.067 |
| 48.683 | 10 | 38.683 | True | -0.118 | -0.217 | -0.019 | -0.129 |
| 48.683 | 20 | 28.683 | True | -0.236 | -0.433 | -0.038 | -0.234 |
| 48.683 | 30 | 18.683 | False | NA | NA | NA | NA |

## Table_S1_model_scenarios

| model | member | scenario | period | location_id | observed_reference_sic | model_historical_sic | historical_model_bias_pp | model_future_sic | model_delta_sic_pp | delta_adjusted_sic | model_cell_distance_km | within_observed_diet_sic_range | observed_diet_sic_min | observed_diet_sic_max | fitted_reference_gap_ols | fitted_reference_gap_fractional_logit | conditional_future_gap_ols | conditional_gap_change_ols | change_coefficient_only_ci_low | change_coefficient_only_ci_high | conditional_future_gap_fractional_logit | conditional_gap_change_fractional_logit | estimand |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ACCESS-CM2 | r1i1p1f1 | ssp245 | 2041-2060 | loc020 | 48.683 | 22.159 | -26.524 | 5.076 | -17.083 | 31.600 | 51.522 | True | 21.901 | 66.683 | 0.456 | 0.440 | 0.255 | -0.201 | -0.370 | -0.032 | 0.234 | -0.206 | conditional gap at future mean SIC, not mean of future annual diet; fixed ecological relation assumption |
| ACCESS-CM2 | r1i1p1f1 | ssp245 | 2081-2100 | loc020 | 48.683 | 22.159 | -26.524 | 0.323 | -21.836 | 26.847 | 51.522 | True | 21.901 | 66.683 | 0.456 | 0.440 | 0.199 | -0.257 | -0.473 | -0.041 | 0.190 | -0.250 | conditional gap at future mean SIC, not mean of future annual diet; fixed ecological relation assumption |
| ACCESS-CM2 | r1i1p1f1 | ssp585 | 2041-2060 | loc020 | 48.683 | 22.159 | -26.524 | 3.300 | -18.859 | 29.823 | 51.522 | True | 21.901 | 66.683 | 0.456 | 0.440 | 0.234 | -0.222 | -0.409 | -0.035 | 0.216 | -0.224 | conditional gap at future mean SIC, not mean of future annual diet; fixed ecological relation assumption |
| ACCESS-CM2 | r1i1p1f1 | ssp585 | 2081-2100 | loc020 | 48.683 | 22.159 | -26.524 | 0.276 | -21.883 | 26.800 | 51.522 | True | 21.901 | 66.683 | 0.456 | 0.440 | 0.198 | -0.258 | -0.474 | -0.041 | 0.189 | -0.251 | conditional gap at future mean SIC, not mean of future annual diet; fixed ecological relation assumption |
| BCC-CSM2-MR | r1i1p1f1 | ssp245 | 2041-2060 | loc020 | 48.683 | 0.292 | -48.390 | 0.000 | -0.292 | 48.390 | 26.158 | True | 21.901 | 66.683 | 0.456 | 0.440 | 0.452 | -0.003 | -0.006 | -0.001 | 0.436 | -0.004 | conditional gap at future mean SIC, not mean of future annual diet; fixed ecological relation assumption |
| BCC-CSM2-MR | r1i1p1f1 | ssp245 | 2081-2100 | loc020 | 48.683 | 0.292 | -48.390 | 0.014 | -0.279 | 48.404 | 26.158 | True | 21.901 | 66.683 | 0.456 | 0.440 | 0.453 | -0.003 | -0.006 | -0.001 | 0.436 | -0.004 | conditional gap at future mean SIC, not mean of future annual diet; fixed ecological relation assumption |
| BCC-CSM2-MR | r1i1p1f1 | ssp585 | 2041-2060 | loc020 | 48.683 | 0.292 | -48.390 | 0.002 | -0.291 | 48.392 | 26.158 | True | 21.901 | 66.683 | 0.456 | 0.440 | 0.453 | -0.003 | -0.006 | -0.001 | 0.436 | -0.004 | conditional gap at future mean SIC, not mean of future annual diet; fixed ecological relation assumption |
| BCC-CSM2-MR | r1i1p1f1 | ssp585 | 2081-2100 | loc020 | 48.683 | 0.292 | -48.390 | 0.003 | -0.289 | 48.394 | 26.158 | True | 21.901 | 66.683 | 0.456 | 0.440 | 0.453 | -0.003 | -0.006 | -0.001 | 0.436 | -0.004 | conditional gap at future mean SIC, not mean of future annual diet; fixed ecological relation assumption |
| CESM2 | r4i1p1f1 | ssp245 | 2041-2060 | loc020 | 48.683 | 28.235 | -20.448 | 14.712 | -13.523 | 35.159 | 36.876 | True | 21.901 | 66.683 | 0.456 | 0.440 | 0.297 | -0.159 | -0.293 | -0.025 | 0.271 | -0.169 | conditional gap at future mean SIC, not mean of future annual diet; fixed ecological relation assumption |
| CESM2 | r4i1p1f1 | ssp245 | 2081-2100 | loc020 | 48.683 | 28.235 | -20.448 | 4.977 | -23.258 | 25.424 | 36.876 | True | 21.901 | 66.683 | 0.456 | 0.440 | 0.182 | -0.274 | -0.504 | -0.044 | 0.178 | -0.262 | conditional gap at future mean SIC, not mean of future annual diet; fixed ecological relation assumption |
| CESM2 | r4i1p1f1 | ssp585 | 2041-2060 | loc020 | 48.683 | 28.235 | -20.448 | 7.013 | -21.222 | 27.461 | 36.876 | True | 21.901 | 66.683 | 0.456 | 0.440 | 0.206 | -0.250 | -0.460 | -0.040 | 0.195 | -0.245 | conditional gap at future mean SIC, not mean of future annual diet; fixed ecological relation assumption |
| CESM2 | r4i1p1f1 | ssp585 | 2081-2100 | loc020 | 48.683 | 28.235 | -20.448 | 0.264 | -27.970 | 20.712 | 36.876 | False | 21.901 | 66.683 | 0.456 | 0.440 | NA | NA | NA | NA | NA | NA | conditional gap at future mean SIC, not mean of future annual diet; fixed ecological relation assumption |

## Table_S2_rolling_diagnostics

| model | n_test_years | mae | rmse |
| --- | --- | --- | --- |
| past_mean | 4 | 0.315 | 0.375 |
| ols | 4 | 0.179 | 0.232 |
| fractional_logit | 4 | 0.166 | 0.222 |
