# Signy conditional diet-component scenarios

2026-11-06. Conditional responses of the existing nine-season, 73-stomach Signy gentoo cohort at the pinned future mean SIC conditions. The three responses are recorded positive fish-mass frequency p, conditional fish fraction c, and all-stomach mean fish fraction m.

Read [REPORT_JA.md](REPORT_JA.md), [Figure 1 PNG](Figure_1_component_scenarios.png) / [PDF](Figure_1_component_scenarios.pdf), and [summary.json](summary.json).

## Interpretation

The 12 climate conditions are three models × two SSPs × two periods. Eleven mean conditions are inside observed diet SIC support, giving 33 finite response rows. Each response is fitted separately with equal-season OLS; fractional logit supplies a response-shape sensitivity. The overall mean is not constructed by multiplying fitted p and fitted c.

The estimand is a response at future **mean SIC**, not an average of future annual diets. Climate differences are not probability intervals. BCC's near-zero historical ice limits its possible raw decline. Corrected annual climate is retained for support diagnostics, including one physically invalid historical value; it is not silently clipped or used to generate annual diet predictions. Coefficient-only HC3 t7 change intervals do not include future climate uncertainty or relation drift.

## Reproduce

Run from the repository root in the existing Python environment (numpy, pandas, scipy, statsmodels, matplotlib). All raw climate and previously derived diet inputs are already tracked; their hashes are fixed in [INPUT_MANIFEST.json](../../work/signy_component_scenarios_v1/INPUT_MANIFEST.json).

```bash
python research/climate-penguin/work/signy_component_scenarios_v1/analyze.py
python research/climate-penguin/work/signy_component_scenarios_v1/plot.py
python research/climate-penguin/work/signy_component_scenarios_v1/independent/climate_inputs.py
python research/climate-penguin/work/signy_component_scenarios_v1/independent/compare_climate.py
python research/climate-penguin/work/signy_component_scenarios_v1/independent/diet_responses.py
python research/climate-penguin/work/signy_component_scenarios_v1/independent/compare_responses.py
python -m pytest tests/test_signy_component_scenarios_v1.py -q
python research/climate-penguin/work/diet_niche_manuscript_v1/verify_assets.py
```

## Outputs

| File | Meaning |
|---|---|
| [climate_scenarios.csv](climate_scenarios.csv) | All 12 future mean conditions and annual support counts |
| [climate_reference.csv](climate_reference.csv) | Three historical model means, biases, locations and annual support |
| [annual_climate_support.csv](annual_climate_support.csv) | 300 model-year corrected climate values; diagnostic only |
| [observed_reference_annual_sic.csv](observed_reference_annual_sic.csv) | 20 observed reference climate years |
| [component_scenarios.csv](component_scenarios.csv) | 12 × 3 response conditions; future values, contrasts and coefficient-only intervals |
| [controlled_reductions.csv](controlled_reductions.csv) | Fixed 5, 10, 20 and 30 SIC pp reductions; 30 pp withheld |
| [slope_accounting_scenarios.csv](slope_accounting_scenarios.csv) | Exact algebraic allocation of the m contrast, not causal shares |
| [fit_parameters.json](fit_parameters.json) | Separate OLS, HC3 and fractional-logit fits |
| [source_manifest.json](source_manifest.json) | 16 pinned input hashes |
| [VALIDATION.json](VALIDATION.json) | Tests, independent calculations, figure and link checks |

All response values in CSVs are fractions on the 0–1 scale; SIC is percent and its differences are percentage points. The report and figure multiply responses by 100 for display. Missing future values mean the climate condition is outside observed support, not zero fish or zero change. Existing [three-species results](../diet_niche_manuscript_v1/MANUSCRIPT_JA.md), [observed component results](../signy_diet_components_v1/REPORT_JA.md), and [Palmer transfer limits](../palmer_signy_diet_external_v1/REPORT_JA.md) retain their distinct estimands.
