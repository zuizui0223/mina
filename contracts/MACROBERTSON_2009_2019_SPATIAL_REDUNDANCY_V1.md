# Western Mac.Robertson Land spatial-redundancy recovery test v1

**Status:** pre-effect contract. Frozen from public metadata and publication-level description before opening the 2009/10 or 2019/20 site-level occupied-nest estimates.

## Independent system

Australian Antarctic Division / Emmerson & Southwell dataset:

**Population counts, resights and demography of Adelie Penguins in Mac. Robertson Land, Antarctica, 1991–2019**

Dataset citation in the associated publication:

    Emmerson, L. & Southwell, C. (2022)
    DOI 10.26179/s2qa-s344

Public metadata states that western Mac.Robertson Land spans approximately 250 km of coastline and contains the Adélie breeding-site metapopulation considered in the study.

The population-estimate file is named:

    W Mac. Robertson Land Adelie penguin population estimates.xls

and contains standardized occupied-nest estimates for:

    2009/10
    2019/20

with 1000 bootstrap estimates used to propagate timing/methodology uncertainty.

This system is geographically independent of Ross Island and Palmer/Signy.

## Biological question

Across an independent multi-site Adélie breeding network, did the 2009/10 -> 2019/20 change in total occupied nests restore/spread spatial redundancy, preserve composition, or concentrate breeding abundance?

No direction is assumed.

## Outcome-blind support gate

Before inspecting occupied-nest magnitudes, inspect only:

- workbook/sheet names;
- column names;
- site identifiers/names;
- whether 2009/10 and 2019/20 estimates are present;
- missingness;
- bootstrap structure / replicate indexing;
- method/precision metadata.

The primary test is eligible only if:

1. at least 3 distinct breeding sites have standardized occupied-nest estimates in both 2009/10 and 2019/20;
2. site identity is stable across endpoints;
3. missing values can be distinguished from zero;
4. the standardized estimates correspond to the same occupied-nest target metric in both periods.

If fewer than 3 paired sites exist, record SUPPORT FAIL.

No site may be added/dropped after magnitudes are opened except by this fixed paired-support rule.

## Fixed roster

Primary roster:

    all breeding sites with structurally supported standardized occupied-nest estimates at both endpoints.

Site selection is based only on paired availability, not count magnitude or direction.

## Primary point estimates

For endpoint t:

    N_t = sum_i n_it
    p_it = n_it / N_t
    E_t = 1 / sum_i p_it^2.

Primary effect:

    delta_logE = log(E_2019_20 / E_2009_10).

Also report:

    N_ratio = N_2019_20 / N_2009_10
    TV = 0.5 * sum_i |p_i1 - p_i0|
    dominant site identity at both endpoints.

Use the source-standardized median occupied-nest estimate for each site if bootstrap medians are supplied.

## Recovery eligibility gate

Interpret the route as a breeding-recovery allocation test only if:

    N_2019_20 > N_2009_10.

If not:

- record recovery gate FAIL;
- do not search for a different interval;
- retain the spatial comparison descriptively but do not call it recovery.

## Exact proportional-allocation decomposition

For every paired site:

    G_i = n_i1 / n_i0
    G_bar = N1 / N0.

With:

    H0 = sum_i p_i0^2
    w_i0 = p_i0^2 / H0
    G_D = sqrt(sum_i w_i0 G_i^2).

Verify:

    E1/E0 = (G_bar/G_D)^2.

Also calculate proportional endpoint residuals:

    expected_i1 = N1 * p_i0
    residual_i = n_i1 - expected_i1.

## Local arithmetic

Report:

- number and fraction of sites with n_i1 > n_i0;
- number and fraction with n_i1 < n_i0;
- gross positive change;
- gross negative change;
- whether the dominant site changed identity.

No local site is described as colonised/extinct from a single zero/absence unless search history independently supports that interpretation.

## Bootstrap uncertainty

The primary decision is based on the standardized point-estimate composition.

Uncertainty propagation is secondary and depends on the documented bootstrap structure.

### If a common bootstrap replicate index is explicitly preserved across sites within each survey

For each replicate b:

    compute N_b, E_b and delta_logE_b

using the corresponding site estimates.

Report the 2.5%, 50% and 97.5% bootstrap quantiles.

### If bootstrap draws are not jointly indexed across sites

Do **not** pretend they are a joint spatial bootstrap.

Report site-level uncertainty and the point-estimate E result only.

Do not create an independence-based Monte Carlo rescue after opening values.

## Decision logic

### A — recovery gate passes, E decreases

Independent external support that breeding recovery can concentrate across a multi-site network.

If every paired site's occupied-nest estimate also increases:

> strong external support for concentration without endpoint local decline.

If some sites decline:

> mixed local arithmetic; do not call it pure differential amplification.

### B — recovery gate passes, E increases

Independent counterexample to a universal concentration rule.

Supports conditional/path-dependent spatial recovery.

### C — recovery gate passes, E approximately unchanged

Composition is close to proportional at the endpoint.

Report the continuous delta_logE; no equivalence threshold is invented post hoc.

### D — recovery gate fails

No recovery-allocation conclusion.

## Relation to Ross

Ross generated a shock/rebound path:

    disturbance equalization
    -> asymmetric immediate rebound
    -> partial later re-expansion.

This Mac.Robertson test does **not** test that exact temporal mechanism because it has two widely separated endpoints.

It tests the more general outcome question:

> can an independent recovering breeding network end with lower, similar, or higher abundance-weighted spatial redundancy?

## Relation to hysteresis mechanism

This route is count-only.

It cannot test configuration memory, Allee effects, capacity or movement without additional independent covariates.

No mechanism is inferred from the sign of delta_logE alone.

## Boundaries

- Response is standardized occupied nests / breeding abundance, not total adult population.
- Site-level standardization inherits the source study's phenology/methodology corrections and uncertainty.
- No alternative years, site subsets or abundance transforms may replace the frozen primary analysis after values are opened.
- This contract is independent of the older Bechervaise/Verner/Petersen three-island V1 route, which remains DATA ACCESS BLOCKED.
