# Frozen exploratory regional-sorting audit (2026-11-21)

Status: design locked before executing the new regional-sorting calculations, **but after the previously reported 17-site positive sea-ice/salinity redistribution signs were known**. This cannot be confirmatory preregistration.

## Question and data
Does recorded Adélie nesting reweighting among the same 17 colonies (1993–2000 to 2011–2020, source-method consistent counts, complete August–November ocean exposure) sort toward higher sea-ice exposure *within* fixed reporting regions, beyond the already known between-region shift?

Only input: existing `redistribution_marine_exposure_20261120/matched_rosters.csv`, comparison=`long`, radius=0. The matching site roster, source regions, ocean cell, two interval nest-count medians and environmental values are frozen; no substitutions of missing sites, years, or sensors. Six absent GLORYS cells prohibit a continent-wide estimate. Source observations are non-synchronous, and counts are not individual relocation tracks.

## Decomposition fixed before inspecting new test
Let n_it denote count medians, W_rt = sum_{i in r}n_it / sum_{all i}n_it; v_irt = n_it / sum_{i in r}n_it; Ebar_i=(E_i0+E_i1)/2. All four regions have positive group totals at both endpoints. The prior exact symmetric nest-reweighting term
R = sum_i (w_i1 - w_i0) Ebar_i
is separated exactly into

- Between-source-region = sum_r (W_r1 - W_r0) * sum_{i in r} (v_ir1+v_ir0)/2 * Ebar_i
- Within-source-region = sum_r (W_r1+W_r0)/2 * sum_{i in r} (v_ir1-v_ir0) * Ebar_i

This identity is tested numerically to 1e-10 for SIC, surface salinity and SST. Sign of SIC reweighting (positive) is the primary descriptive contrast; salinity and SST are pre-specified diagnostics, not independent confirmatory tests. Report both components and the fraction of SIC redistribution attributable to region vs within region; no attribution to individual migration/behavior.

## Conditional label-shuffling sensitivity, explicitly post hoc
Within each region, keep the early n0 and ocean values for each site fixed; for n0>0, let observed proportional growth g_i=n1_i/n0_i. Randomly permute the multiset of g values among the n0>0 sites *inside the same original region*. Construct n1*_i=n0_i*g_permuted and rescale all n1*_i in a region to preserve its original late regional nest-count sum; keep n0=n1=0 at zero. Region size and aggregate growth, every site's baseline abundance, physical environment and early spatial pattern stay fixed. The null assumes growth-factor exchangeability within region, which may fail when site size, occupancy and demography constrain growth; therefore randomization p values are *diagnostic tail frequencies*, not a causal random-assignment test.

Use integer xorshift32 seed 20261121, 49,999 random permutations, and +1 Monte Carlo tail correction, re-evaluating within-region reweighting for each of SIC, salinity and SST. Primary directional tail: P(within-region SIC >= observed); report two-sided centered tail as sensitivity. Also report the regional-constraint null for the full SIC R (the between component can still vary slightly via within-region environmental means). Use 2.5%, median, 97.5% null quantiles. Never optimize a radius/window, group definition, per-region exclusion or sign after seeing results. If the null does not separate the observed from the shuffle, explicitly conclude that no within-region sorting beyond regional growth and observed colony sizes was demonstrated.

No extra independent spatial replications are created by permuting; shared GLORYS cells and four regions limit interpretation. Retain the existing 17-site observed claims and their source support regardless of the new null verdict. Do not transfer any estimated historical growth rule into CMIP6 or infer future penguin nests.
