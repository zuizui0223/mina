# Frozen source-year sensitivity of exact four-region permutation ranks

2026-11-21 | Draft PR #214 | Already observed: parent23 source-median ranks 2/24; complete17 source-median ranks 3/24. Before looking at the resampled rank outcomes, freeze this robustness calculation.

Input: original observed_counts_used.csv for 513 true source site×year Adélie records, existing 23 observed SIC-complete sites with matching 17 complete GLORYS sites, original dates, original source survey methods and no imputed missing year. Confirm every original site×early/late median and true zero vs unobserved year exactly as in resample_source_census_years_SIC23_vs17_20261121.py.

Resample annual observed census counts within each original site × early (1993–2000) or late (2011–2020) period with replacement, using a single stateful xorshift32 stream with seed 20261121 and exactly 4,999 source-year draws. Use the same random draw for source23 and its nested source17. For each draw and each cohort, recalculate the four region growth ratios from the resampled medians; reassign these growth ratios to the four original source reporting regions under **all 24 alphabetical-order permutations**, holding that draw's region baseline counts and its late within-region site proportions fixed. Compute the original identity between-region term, exact rank from high (1 highest) among 24, number at least as high, and positive between-term flag. Never discard draws on the basis of the resulting rank.

Primary descriptive robustness: fraction of 4,999 draws whose identity rank is in top 2/24 for source23, plus 2.5/50/97.5 rank quantiles. Predeclared secondary results: source17 fraction in top 2 and top 3, cross-cohort rank concordance, and fraction with positive between terms. No new climate regressor, region definition, site exclusions, change of seed, or redefinition of a top-ranked alignment after observing outcomes.

Conditional on source observed years and only four nonexchangeable reporting regions. This is **not an ecological population confidence interval or proof of adaptive tracking**. If the top-two rank fails in many census-year draws, report that the apparent conditional alignment is not stable and do not promote it to an ecological main claim. Even if top-two ranks are stable, no cause of region growth or migration is identified.

Do not alter v0.5/main/Ecology Report/Paper2; put diagnostic in supplemental report until the robustness is known.
