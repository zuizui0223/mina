# Bird Island Gentoo breeding-success -> next-year allocation test v1

**Status:** pre-effect mechanism contract. Frozen after the six-unit nest-count allocation result, but before any numerical chick-count or chicks-per-nest value from the BAS Version 2.0 dataset is summarized for this question.

## Independent response/predictor structure

Source:

**Breeding success of Gentoo penguins at Bird Island, South Georgia, from 1981 to 2025 - VERSION 2.0**

DOI:

    10.5285/8fedb5a0-b98c-4457-9d86-aae9c6d3ed8e

Provider methodology:

- occupied/incubating nests are counted around the standardized laying date;
- chicks are counted 98 days after peak laying;
- separate counts are maintained for the same six fixed breeding units used in the allocation analysis.

The nest-count trajectory has already been opened.

The numerical chick counts and derived local breeding-success values are **not** to be summarized until this contract and a support-only receipt are committed.

## Fixed breeding units

1. Johnson
2. Square Pond
3. Upper Natural Arch
4. Lower Natural Arch
5. Upper Mountain Cwm
6. Lower Mountain Cwm

Use the same mapping frozen in:

    contracts/BIRD_ISLAND_GENTOO_SIX_UNIT_RECOVERY_ALLOCATION_V1.md

No units may be added, merged or removed based on chick values or effect direction.

## Biological question

Does local reproductive performance predict how breeding abundance is reallocated among breeding units in the following season?

This tests a candidate predictor of the **contrast mode** rather than the aggregate mode.

The generated prediction is:

> a breeding unit with higher local chicks-per-nest performance in season t should, on average, gain relative breeding share by season t+1.

Possible biological routes include:
- greater return/breeding propensity after local success;
- lower breeding dispersal from successful sites;
- persistent local habitat quality.

The count-only analysis cannot distinguish these routes.

## Outcome-blind support audit

After this contract is committed, inspect only:

- which start years have nonmissing nest and chick fields for all six units;
- which following calendar years have nonmissing nest fields for all six units;
- whether duplicate unit-season rows exist;
- whether any nest denominator is zero;
- whether chick values are structurally missing versus numeric zero.

Do **not** calculate:
- chicks per nest;
- annual/local success summaries;
- share-change responses;
- correlations;
- regression coefficients.

## Fixed transition eligibility

A start season t is eligible only if:

1. all six fixed units have exactly one usable nest count in t;
2. all six fixed units have exactly one usable chick count in t;
3. all six fixed units have exactly one usable nest count in calendar year t+1;
4. all nest counts used as denominators are >0;
5. t+1 is the immediately following calendar year, not merely the next observed complete season.

No gaps are bridged.

No transition may be added or removed after chick magnitudes are opened except by these support rules.

Require at least 15 eligible start years. Otherwise record SUPPORT FAIL.

## Predictor

For unit i in start year t:

    S_it = chicks_it / nests_it.

This is the provider-aligned local breeding-success measure.

No transform is primary.

The two-way fixed-effect model itself removes:
- persistent unit differences;
- common year differences.

## Response: next-year compositional change

For each eligible transition:

    p_it = nests_it / N_t

where N_t is the total nest count across the six fixed units.

Define:

    Y_it = log(p_i,t+1 / p_it).

This is exactly the local log share change.

It removes the aggregate common multiplier:

    Y_it
      = log(n_i,t+1/n_it)
        - log(N_t+1/N_t).

Thus the response is the **contrast-mode change** of each breeding unit.

If any fixed unit has zero nest share at either endpoint of an otherwise eligible transition, record that transition as structurally ineligible before inspecting chick magnitudes. Do not add pseudo-counts.

## Primary model

Fit on all eligible unit-year rows:

    Y_it = alpha_i + tau_t + beta * S_it + error_it

where:

- alpha_i = breeding-unit fixed effects;
- tau_t = start-year fixed effects;
- beta = focal association.

The primary directional prediction is:

    beta > 0.

Interpretation:

higher breeding success at a unit predicts a greater next-year increase in that unit's share of the six-unit breeding network.

## Frozen permutation inference

Use:

    B = 9999
    seed = 20261006.

Permutation unit:

    entire six-unit S_t vector.

For every permutation:

1. permute the eligible start-year labels of the complete six-unit success vectors;
2. keep unit identities inside each success vector unchanged;
3. keep Y_it and its start-year labels unchanged;
4. refit the identical two-way fixed-effect model;
5. record beta_perm.

This preserves:
- the six-unit spatial covariance of breeding success within each year;
- persistent unit identities;
- the empirical distribution of annual success patterns;
- the complete response panel.

It breaks only the temporal alignment between breeding-success state in year t and the t->t+1 compositional response.

Directional p-value:

    p = (1 + count(beta_perm >= beta_obs)) / (9999 + 1).

Primary support requires:

    beta_obs > 0
    and
    p <= 0.05.

A null or negative result is terminal for this route.

## Secondary effect-size reporting

Regardless of significance, report:

- beta_obs;
- permutation p;
- standardized beta using the SD of S_it after two-way demeaning;
- number of eligible years and rows;
- leave-one-unit-out beta for each of six omissions;
- year-block permutation distribution 5th/50th/95th percentiles.

LOO is robustness only.

No unit may be excluded from the primary result because its LOO behavior is unfavorable.

## No outcome-dependent lag search

Primary lag is exactly one breeding season.

Do not test lags 2-6 years after observing the one-year result as a rescue for juvenile recruitment.

A juvenile-recruitment lag hypothesis would require a separate pre-effect contract and independent biological justification.

## Interpretation boundary

A positive result supports:

> local reproductive performance carries prospective information about next-season spatial allocation of breeding abundance.

It is consistent with site retention / breeding-propensity / persistent local-quality mechanisms.

It does **not** establish:
- individual movement;
- causal win-stay/lose-switch behavior;
- juvenile recruitment;
- a universal Gentoo mechanism;
- the Ross iceberg mechanism.

A null result means breeding-success differences do not explain the contrast mode at this one-season timescale under the frozen design.

## Relation to the current paper

This route is optional mechanism support.

The main paper-level empirical result remains valid regardless of outcome:

    aggregate change does not determine spatial allocation.

If this mechanism test passes, it supplies a first prospective predictor of the contrast mode.

If it fails, retain the paper as a state/allocation study and do not search the same dataset for a favorable lag or alternative productivity metric.
