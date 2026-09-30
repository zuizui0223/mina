# Palmer history-dependent redistribution synthesis v1

## Current ecological result

The Palmer analyses now support a narrower and more defensible mechanism-level statement than either “place determines colony fate” or “penguins follow public information.”

The aggregate pattern is:

1. Palmer Adélie breeders progressively concentrate into fewer effective colony-code breeding groups during regional decline.
2. Larger groups have higher chick production per pair relative to a frozen proportional-productivity null.
3. Immediate pre-extinction chick-performance deficits are directionally negative but too sparse to confirm reproductive failure as the extinction trigger.
4. Relative colony reproductive performance predicts later within-island redistribution after island-transition mean growth, prior group size and persistent colony identity are removed.
5. This signal is supported at the denominator-separated lag-2 endpoint and at lag 3, but fades at lags 4–5; the predeclared 4–5-year recruitment-echo contrast is negative.
6. Measured reproductive-performance state has only weak one-year colony-specific memory and no confirmed two- or three-year memory under the repaired frozen null.
7. Past performance nevertheless retains incremental information about subsequent redistribution after measured next-year performance, prior size and colony identity are included.

The defensible synthesis is therefore:

> **Adélie breeding distributions are history-dependent: recent biological performance contains short-lived information about subsequent redistribution that is not reducible to static colony identity, current group size, or the measured persistence of reproductive performance itself.**

This is not yet an individual movement mechanism.

## What the pattern does and does not distinguish

A simple, spatially general “the same colonies remain environmentally good for several years” explanation is insufficient because measured performance autocorrelation fades quickly and is spatially heterogeneous, whereas the bridge coefficient remains positive under every single-island exclusion.

However, persistent local environment is not ruled out. Reproductive performance is an imperfect proxy for any latent environmental state, and conditioning on measured next-year performance is not causal mediation. An unmeasured environmental process or measurement error can leave information in past performance.

Likewise, the result is compatible with—but does not identify—adult retention, breeding dispersal, prospecting, or public-information use. Colony-level counts cannot reveal which individuals moved.

## Direct individual-level gate

Palmer census metadata documents standardized searches for returning previously banded penguins on Humble Island: two observers search every colony every two days throughout the field season. The public fledgling-weight table also contains band_number, island and colony identifiers. Historical Palmer publications report later adult resighting of individually banded fledglings.

As of 2026-09-30, no public table containing joinable longitudinal resight records (band_number × year × location/status) has been identified in the Palmer/Rutgers ERDDAP/catalog, EDI-indexed search, or the other public sources audited here.

Therefore direct movement inference is **DATA-DEPENDENCY BLOCKED**.

The frozen gate is:

contracts/PALMER_INDIVIDUAL_MOVEMENT_DATA_GATE_V1.json

No manuscript version should infer the carrier of the temporal history until that gate is opened with a qualifying resight source.

## Analysis to run if a resight source becomes available

### Adult retention / breeding dispersal

For a breeding adult observed in colony i in year t, test whether relative reproductive performance of colony i in t predicts same-colony return versus observed breeding dispersal in t+1.

The preferred framework is a multistate capture-recapture model because nondetection must not be equated with dispersal or mortality.

### Prebreeder settlement

If prospecting histories and first-breeding locations exist, test whether first settlement is biased toward colonies with high recent reproductive performance, while accounting for natal-colony affinity, age, sex and availability.

A delayed natal cohort correlation is not an adequate substitute: the previously frozen 4–5-year recruitment-echo prediction was not supported.

## Manuscript-level wording

Strong enough:

> Recent colony performance carries temporal information about subsequent within-island redistribution, producing a history-dependent breeding landscape during population decline.

Not allowed:

- Penguins were shown to use public information.
- Better-performing colonies attracted identifiable immigrants.
- Adults left poor colonies.
- Prospectors selected successful colonies.
- Static landscape no longer matters.

The clean conceptual link to Paper 2 is not “state beats place.” It is:

> **Static landscape architecture did not yield a transferable macroecological response rule, whereas within Palmer, dynamically updated colony state contains short-lived information about where breeders subsequently accumulate.**

That distinction preserves both the negative Paper 2 result and the known role of snow, geomorphology and other physical breeding conditions.


## HUMPOP colony-arrival route

An official PAL-LTER source repository (`PAL-LTER/pal-seabirds`) was identified. Its conversion code shows that HUMPOP is genuinely colony-level: raw `SEASON, DATE, ISL, LOC, TOTADULTS` are archived as `studyName, Date, Island, Colony, Adults`, and the same raw `LOC` field is used for colony identity in the adult census.

This source passed a prospectively frozen schema gate before arrival-count values were opened. The subsequent frozen test required exact raw colony-code matching, a first upward 50% crossing of each colony-season maximum, at least three colonies per predictor season, at least 10 predictor seasons, and at least 100 matched colony-seasons.

The information gate failed before any performance-arrival model was fit:

- 106 estimable 50% arrival endpoints;
- 84 exact performance × next-season arrival matches;
- 69 matched colony-seasons after the >=3-colony season rule;
- 18 predictor seasons;
- required minimum = 100 matched colony-seasons.

Therefore HUMPOP is **not a negative result**. It is a predeclared **STOP for insufficient information**. No coefficient, p-value, or direction for performance-linked arrival exists. The analysis may not be rescued by lowering the threshold, switching to the 25%/75% endpoints, or creating a post hoc colony-code crosswalk.

Receipt: `results/PALMER_HUMPOP_ARRIVAL_RESULT_V1.json`

This closes the aggregate arrival route. Direct discrimination among adult retention, breeding dispersal, prospecting and immigration still requires the unresolved longitudinal band-resight source.
