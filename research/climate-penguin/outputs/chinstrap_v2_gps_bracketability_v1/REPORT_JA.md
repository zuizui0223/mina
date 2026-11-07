# Source GPS chronological coverage audit before TDR event geolocation

This source-verified v1 analysis addresses a key issue in using GPS points to locate subminute pressure-defined dives. The identical BAS Chinstrap Version2 source DOI is https://doi.org/10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92 and its exact canonical member hash is fixed. For each tracked original deployment, compute unique timestamps and the *elapsed time represented by each adjacent GPS gap*; do not mistake the fraction of many short gaps for the fraction of track time that can be assigned to a close GPS bracket.

**Quantitative source result**, duplicate source member and timestamps removed: **308 original nonempty deployments, 215,298 successive GPS-fix intervals**. Each island-year's % GPS intervals no more than 10 minutes vs % of GPS-record span inside such short intervals is:

| Island, season start | n GPS gaps | short gaps as % of gap *count* | short gaps as % of elapsed *track time* |
|---|---:|---:|---:|
| Laurie 2011 | 28,364 | 87.3% | **34.8%** |
| Powell 2013 | 41,415 | 85.7% | **32.1%** |
| Monroe 2015 | 24,277 | 85.9% | **43.6%** |
| Signy 2011 | 15,539 | 97.8% | **71.8%** |
| Signy 2013 | 18,780 | 87.6% | **39.6%** |
| Signy 2015 | 40,944 | 94.6% | **57.5%** |
| Signy 2018 | 45,979 | 86.5% | **30.0%** |

The time fraction weights gaps by their elapsed seconds (not independent Bernoulli samples). It says **nothing yet** about how many TDR dives overlap these GPS intervals; a source pressure file may cover only a subset of the GPS period. The difference between count-based and time-based support is sufficient to show why filtering to tightly bracketing GPS fixes can produce **island- and deployment-dependent sample selection**. Do not present the resulting dive-location subset as a random survey of all available offshore krill, or interpret differential attrition as a genuine foraging effect.

The 5-/10-/20-min GPS bracketing requirements are recorded before opening TDR dive outcomes. The strict original-deployment and clock-alignment gates are in \`contracts/CHINSTRAP_BAS_V2_GPS_TDR_DIVING_LOCATION_GATE_V1.json\`. The next stage must report **per-tag TDR-overlap time, fraction of dives with valid GPS brackets, and reasons for missing** before interpreting modelled krill at diving locations. Long gaps are not interpolated.

Source analysis uses prior original BAS GPS member SHA, explicit duplicate removal, and independent automated numeric receipts. No sea ice, salinity, krill abundance, nest numbers, N_eff or vegetation response is inferred.
