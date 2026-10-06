# Bird Island Gentoo breeding-success -> next-year allocation result v1

**Status:** frozen primary statistical PASS, with a post-effect interpretation audit that prevents a strong causal mechanism claim.

## Frozen test

The pre-effect contract fixed:

- six breeding units;
- 38 eligible start years;
- 228 unit-year rows;
- predictor: operational breeding-success index

      S_it = chicks_it / nests_it

- response:

      Y_it = log(p_i,t+1 / p_it)

- unit and start-year fixed effects;
- 9999 complete-six-unit year-vector permutations;
- seed 20261006;
- directional prediction beta > 0.

No alternative lag, unit subset or productivity metric replaces this primary test.

## Primary result

Observed:

    beta = +0.32383.

Permutation distribution:

    q05    = -0.09286
    median = +0.00002
    q95    = +0.09209.

No one of 9999 permutations equaled or exceeded the observed beta.

With the frozen plus-one rule:

    p = 0.0001.

Therefore the frozen statistical support criterion **passes**.

## Effect size

After unit/year demeaning, SD of S is:

    0.44697.

A +1 SD difference in the operational success index corresponds to:

    +0.14474

in next-year log share change.

Equivalent share multiplier:

    exp(0.14474) = 1.156.

So within the frozen model, a one-SD higher local success index is associated with roughly a **15.6% larger relative next-year share multiplier**.

The fully standardized coefficient / residual correlation is:

    0.579.

This is a large association.

## Leave-one-unit-out robustness

All six LOO coefficients remain positive:

| omitted unit | beta |
|---|---:|
| Johnson | 0.318 |
| Square Pond | 0.317 |
| Upper Natural Arch | 0.323 |
| Lower Natural Arch | 0.331 |
| Upper Mountain Cwm | 0.376 |
| Lower Mountain Cwm | 0.315 |

The primary association is therefore not driven by one breeding unit.

## Critical post-effect metric audit

The numerical predictor revealed an important semantic problem only after effect opening.

There are 9 eligible unit-year rows with:

    chicks / nests > 2.

Maximum:

    Upper Mountain Cwm, 2019
    nests = 23
    chicks = 181
    ratio = 7.87.

A literal per-pair reproductive output above two is not biologically interpretable for Gentoo penguins.

The BAS metadata states that nest counts are timed from marked nests at Johnson/Square Pond and that other colonies are counted within one day, whereas chicks are counted much later near fledging. Later nesting, count timing, and/or chick spatial redistribution can therefore make the row-level ratio an **operational monitoring index** rather than a literal fecundity measure.

Accordingly, do not write:

> each extra fledgling per breeding pair causes a later increase in colony share.

Use:

> higher operational breeding-success index predicts next-year relative allocation.

## Shared-denominator problem

The primary predictor contains current nest count in its denominator:

    chicks_t / nests_t.

The response also contains current nest share:

    log(p_t+1 / p_t).

Therefore error or transient depression in current nests can mechanically increase both:

- the success ratio;
- the subsequent share-change response.

The frozen permutation test does **not** protect against this same-year denominator coupling because permuting success vectors breaks the coupling in the null.

This matters for mechanism interpretation.

## Post-effect diagnostic 1 — current share

After the same unit/year demeaning:

    success index vs current log share
    residual r = -0.640
    coefficient = -1.021
    permutation p = 0.0001 in the negative direction.

Thus high success-index values occur strongly when the unit currently has low relative breeding share.

## Post-effect diagnostic 2 — backward symmetry

Using the same success index in year t against the **previous** share change:

    log(p_t / p_t-1),

gives:

    beta = -0.314
    residual r = -0.555.

The primary forward beta is:

    +0.324.

This near-symmetric geometry is consistent with a current-share trough followed by rebound.

It can arise from:

- real compensatory/density-dependent demography;
- shared-denominator/count effects;
- both.

It is not the signature expected from a simple time-invariant "high-quality sites win next year" story.

## Diagnostics that show the signal is not obviously only an artifact

These are **post-result** and cannot replace the primary contract.

### Control current log share

Adding current log share as a covariate after unit/year effects leaves:

    beta_success = +0.286
    permutation p = 0.0001.

### Ratio-free formulation

Use:

    log(1 + chicks_t)

as the predictor and control:

    log(nests_t)

along with unit/year effects.

This removes the literal chicks/nests ratio from the predictor.

Result:

    beta_chicks = +0.0833
    permutation p = 0.0126.

### Timing colonies only

Johnson and Square Pond are the colonies that define the provider's laying-time schedule.

Using only those two units:

    beta = +0.252
    permutation p = 0.0082.

### Remove years containing any ratio >2

Removing all six affected years leaves 32 start years:

    beta = +0.405
    permutation p = 0.0001.

These diagnostics make it difficult to dismiss the entire forward association as an extreme-ratio artifact.

But they are post-effect sensitivities, not independent confirmation.

## Biological interpretation

The strongest allowed statement is:

> **Local breeding-performance information predicts next-season redistribution of breeding abundance within Bird Island.**

A more specific but still cautious interpretation is:

> the signal is consistent with compensatory local dynamics: units in a low-share state tend to show higher breeding-performance indices and subsequently regain relative share.

The current data cannot distinguish among:

- density-dependent reproductive compensation;
- breeding propensity / return decisions;
- persistent local habitat quality;
- adult movement;
- phenological/count-timing effects;
- shared-denominator measurement coupling.

## What this does to the paper

This is useful **mechanism support**, but it should not replace the Ross natural experiment as the main result.

Main paper:

    aggregate change does not determine spatial allocation.

Bird mechanism inset / Discussion:

    a prospectively frozen local-performance metric carries strong information about next-year allocation, but the exact mechanism remains unresolved.

## Claim boundary

Safe:

- frozen beta > 0 and permutation p=0.0001;
- all LOO betas positive;
- predictive information persists in post-result ratio-free/current-share diagnostics;
- success index is strongly associated with low current share.

Not safe:

- causal win-stay/lose-switch behavior;
- juvenile recruitment;
- literal fecundity effect per pair;
- universal Gentoo mechanism;
- direct support for the Ross iceberg mechanism.
