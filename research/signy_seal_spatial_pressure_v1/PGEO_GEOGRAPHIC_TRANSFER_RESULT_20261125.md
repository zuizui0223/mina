# PGEO geographic transfer — executed result, 2026-11-25 JST

Status: **NO_GO_UNIVERSAL_POSITIVE_ADELIE_PRODUCTIVITY_RESPONSE**. Same BCO-DMO source and native P100/hydro inputs as the frozen contract 0dab128cda1d9cc1d52db69ef9d4badcdcf51c5d. New geographic comparisons, not verified independent original observation events. Original monitoring can overlap prior Signy/Cape analyses. The initial count assertion failed before any effect fit because 14+14+15+15+15+13+13+13=112, not 113. Corrected this clerical denominator only; no change to source/roster/model/candidate rules. With PGEO comparator, 127 species-site-year observations; 112 external, 8 series, 4 sites; primary external Adélie 42 observations, 3 sites. All 21 candidate site IDs, including PGEO, verified against the 5-km source coordinate rule; candidate-average exposure is a local-area proxy, not verified same colony footprint.

## Complete site-series results

Coefficients: offspring/nesting female per 1 percentage point P100, equal-year OLS. Ranges are single-year deletion slopes, not confidence intervals. Full adjustment adds SIC, SST and salinity to year + P100. All model gates passed, including full models and deletions; no p-values.

| Site | Species | n | Time-adjusted beta | LOO range | Hydro-adjusted beta | LOO range |
|---|---|---:|---:|---|---:|---|
| Admiralty Bay | ADPE | 14 | -0.006065 | [-0.140659,0.014808] | +0.163680 | [0.014516,0.194883] |
| Palmer | ADPE | 15 | +0.009016 | [0.000284,0.019913] | +0.023718 | [0.015320,0.032907] |
| Signy | ADPE | 13 | +0.006569 | [-0.031795,0.046137] | -0.118923 | [-0.162770,-0.051335] |
| Pointe Geologie (reference, not transfer) | ADPE | 15 | +0.080555 | [0.062106,0.103014] | +0.091346 | [0.058996,0.159120] |
| Admiralty Bay | GEPE | 14 | +0.023289 | [-0.104617,0.034571] | +0.146115 | [0.021325,0.175043] |
| Cape Shirreff | CHPE | 15 | -0.032700 | [-0.048710,-0.010922] | -0.092147 | [-0.203403,0.027329] |
| Cape Shirreff | GEPE | 15 | -0.022773 | [-0.047399,0.007343] | -0.063182 | [-0.160884,0.118498] |
| Signy | CHPE | 13 | +0.039387 | [0.030115,0.063301] | +0.056810 | [0.023351,0.091158] |
| Signy | GEPE | 13 | +0.030763 | [-0.002385,0.047560] | +0.069709 | [0.001338,0.136365] |

Primary equal-site mean Adélie slope +0.003173; global-year deletion range [-0.042271,0.018025], leave-site means [+0.000252,+0.007792]. Fully adjusted +0.022825; global-year deletion [-0.041286,0.034400], leave-site means [-0.047602,0.093699]. All three positive-site, all year-omission positive, and all candidate positive criteria fail under both models. Fully adjusted candidate slopes preserve site direction (Admiralty [0.152261,0.175295]; Palmer [0.023373,0.023889]; Signy [-0.125705,-0.115048]). Descriptive regional variation, no formal geographic interaction test or independent causal effects. No common cross-region positive effect.

## All four predeclared exact paired species contrasts

| Site | Contrast | n | Time beta | LOO range | Hydro beta | LOO range |
|---|---|---:|---:|---|---:|---|
| Admiralty Bay | GEPE-ADPE | 14 | +0.029355 | [0.015613,0.054514] | -0.017565 | [-0.052321,0.038588] |
| Signy | GEPE-ADPE | 13 | +0.024194 | [-0.019787,0.042199] | +0.188632 | [0.153371,0.225499] |
| Cape Shirreff | GEPE-CHPE | 15 | +0.009928 | [0.001310,0.021427] | +0.028965 | [-0.033159,0.176929] |
| Signy | GEPE-CHPE | 13 | -0.008624 | [-0.032501,0.015091] | +0.012899 | [-0.031682,0.045207] |

Signy adjusted GEPE-ADPE contrast is positive across candidate centres [0.184701,0.199977] and all single-year deletions, partial R2 0.655263, but time-only sign not stable, and does not replicate in Admiralty Bay after hydro adjustment. Direction consistent with the already known fixed-unit Signy analysis in PR217; underlying observations may overlap. Do not count it as independent confirmation. No universal species-specific response, no rescue by secondary tests. 

## Reproducibility and stop rule

Script pgeo_geographic_transfer.py commit 43f36b45afae88837bb6ffec6ebe19750e8a5b16, git blob 7b5d0b0242873c3b8988e3eb61181f26dff85654 exactly matches executed local file; SHA256 5070931053b9ae982496161891aa9b3c829f2e8e15fb4c39d1475e62a32ec82f. Run `OPENBLAS_NUM_THREADS=1 python research/signy_seal_spatial_pressure_v1/pgeo_geographic_transfer.py ARTIFACT_DIRECTORY OUTPUT_DIRECTORY`. Output result.json SHA256 06c2e155dda55910e04ba0e7bd4936a200eb43677fa36a50508f051e50a09de1, matched_series.csv SHA256 959c299b669fbb9d6c87c11634349f5e5b07c9532049fb0dbd2b367d3b7a0ffc. Exact rerun confirmed byte-identical outputs. All four artifact SHA256 and ZIP CRC, BCO member SHA, candidate support and FWL identity checked. Full unrounded coefficient/omission/candidate outputs regenerate from script. No raw observations copied to Git. 

Prioritize preserving current evidence and closing this transfer gate. No further radius/lag/subset/model search to recover positive universal sign. Do not combine with PGEO climate-to-spatial association as causal mediation; previous spatial bridge and temporal asymmetry fail. If undertaking future work, use independently documented local time series and exposure measurements, not more regressions on these eight series. Main and frozen manuscripts unchanged.
