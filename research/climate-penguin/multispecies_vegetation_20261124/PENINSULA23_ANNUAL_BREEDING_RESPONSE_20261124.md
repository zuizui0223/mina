# Annual breeding changes and native winter polynya exposure at the fixed 23 sites

Executed locally 2026-11-24, exploratory association only. Source: original archived MAPPPD unambiguous table blob fc134e364cf38699fa7611d7dee5fbbbcb370c0a (codex/climate-penguin-progress), 559 records (23 sites, 43 site-species series, 1993–2020); unique observed count and single known ground method yields 542. Compact source input SHA256 (without trailing LF) 34e3df6d120b19ae404664753ea37ddbfab3ee68db6ff3532871f2fcf607ea81, FNV1a 682ff2e3. Previous locally verified physical source ZIP SHA256 1b7e9c4aa31bc5ce7cd63151e153a925be53b76962af9653dffec3443827f1bf, original artifacts 13829236358 and 14922509462. No restricted data. Same archived counting method is not necessarily same dates, coverage, or effort. No imputation of unsurveyed years. Actual count zeros preserved.

363 consecutive year observed pairs; 317 positive both years; 171 positive with current calendar-year polynya. Primary response log(N_t/N_(t-1)); site and year FE; equal total site weights, >=2 complete pairs/site, >=3 sites, full predictor rank and >=5 residual df. Current year June-Oct 100km polynya (+1pp), Aug-Nov SIC (+10pp), salinity (+0.1), temperature (+1°C). Year labels not verified breeding-season start. Separate species panels, not formal species effect contrasts. 168 primary pairs after repeat support. Only two regions, at most four blocks; no new inferential p-values. Weighted QR/FWL and full weighted dummy regression agreement max 1.988e-9.

| Species | n/sites | residual df | P100 slope | Baseline/full within-FE R2 |
|---|---:|---:|---:|---:|
| ADPE |23/5|4|not estimated|.269892 / unavailable|
| CHPE |66/11|37|-0.056033|.015988 / .057661|
| GEPE |79/14|48|+0.010320|.219089 / .221042|

CHPE site-deletion [-.089479,-.045921], all 11 valid; 3/4 block deletions estimable and negative; only 1/2 region deletions estimable. Radius25 coefficient +.000932; site-only -.010341. On common 57 rows, current P100 -.056124, prior-year P100 -.019667, change of P100 +.013479 (matching climate windows, different estimands). GEPE site omission [-.027628,+.059205] and region omission [-.021686,+.073117]. ADPE site-only +.088570 and zero-inclusive log1p FE -.002360 differ in support/estimand. Base-only all-period water temperature coefficients positive for all three (+1.182506, +.800113, +.915572 per C); in polynya-supported panels CHPE and GEPE temperature coefficients change sign under estimable region omission. Not a general water-temperature response.

## Forward historical transfer (not future climate forecast)

Train 2004–10, test 2013–20; known site intercepts from training, >=2 training pairs/site and >=1 test; no year FE in prediction; site-equal RMSE on identical test rows.

|Species|train/test pairs|sites|site-only|SIC/salinity/temp|+P100|
|---|---:|---:|---:|---:|---:|
|ADPE|9/6|2|insufficient|insufficient|insufficient|
|CHPE|20/19|5|.287949|.281091|.352202|
|GEPE|23/28|7|.423636|.656435|.740583|

No prediction improvement from polynya. Small geographic and temporal sample.

## Strict species-pair support

Reopened strict original pair source blob 7e86b2eb5f5a4e012f128101ebec02d51cbfe41c (PR214 branch), 172 rows at these sites. Same calendar year/site citation and method, not same date. Require adjacent common years, four positive counts, current complete winter, >=2 changes/site. Bipartite site-year FE rank computed via number of components. ADPE/CHPE 10 rows/3 sites: zero residual df before covariates; ADPE/GEPE 19/4: five before and one after four full-rank covariates; CHPE/GEPE 21/6: four before and zero after four full-rank covariates. No pair-specific regressions fitted. Therefore cannot distinguish species biology from sampled geographic support by comparing independent species slopes.

Decision: retain verified physical change (23/23 polynya increase), earlier optical isotope proxy association, observed breeding community redistribution, and local terrestrial findings as separate evidence levels. No supported annual demographic link or land nutrient/vegetation mediation. Do not tune lags or radii on this small sample. Prior manuscripts/main unchanged. Local reproduction bundle peninsula23_breeding_response_20261124.zip SHA256 c9a2896001b0694163019f8d581a61ac49c995403dc0c071f753cd071af60f6a; executed analyze.py SHA256 534d6f7e1e70d883155a7aaf4adad68a170b21b902260a3646ea1568853f11f3, compact input, all models/omissions/predictions and strict paired support.