# Manuscript spine v0.9 — Near-complete rebound leaves a calibrated spatial mismatch

**Status:** preferred manuscript spine after Bird mechanism audit, Port Lockroy support failure, and Ross bounded-count sensitivity. Supersedes v0.8.

## Working title

**Near-complete breeding rebound does not guarantee spatial restoration**

Alternative:

**A population can recover in number without returning exactly in place**

## One ecological question

> **After a shared disturbance, does breeding abundance return to the same places from which it was lost?**

Ross Island is the focal natural experiment.

Bird Island Gentoo and global emperor penguins are prospective external sign tests, not coequal mechanistic case studies.

## Focal Ross result

1999 -> 2001 disturbance:

    aggregate breeding-count loss = 112,613.

2001 -> 2002 immediate rebound:

    aggregate gain = 109,198.

Therefore:

    96.97%

of the aggregate loss returned.

The shock-loss and rebound-gain vectors are strongly aligned:

    cosine = 0.99695.

So most rebound occurred in broadly the same spatial direction as the loss.

But against an exact inverse-path rebound scaled to the observed rebound total:

    half-L1 allocation mismatch = 10,270.6
                                = 9.41% of rebound.

The balancing excess is concentrated at Cape Crozier West.

This is the central calibrated effect size.

## Correct wording

Use:

> The rebound largely retraced the disturbance spatially, but about one tenth of rebound abundance was allocated differently from an exact inverse path.

Avoid:

- wholesale relocation;
- complete failure of spatial recovery;
- movement of 10,271 individual birds.

The response is occupied nesting territories / breeding-pair abundance.

## Measurement uncertainty

The historical Ross source does not supply component-specific count-error estimates sufficient for a formal CI on the 9.41% mismatch.

Therefore 9.41% is a descriptive effect size.

### Deterministic bounded-count sensitivity

A post-result robustness analysis asks how large symmetric multiplicative perturbations of the reported 1999/2001/2002 component counts must be before exact inverse-path restoration becomes algebraically feasible.

If the observed aggregate rebound scaling is retained:

    minimum common tolerance ~= 22.7%.

If the common inverse-path scaling is also allowed to float:

    minimum tolerance ~= 13.8%.

These are **not estimates of census error**.

They show only that exact reversal cannot be recovered under this simple bounded-perturbation model with arbitrarily small changes to the reported counts.

Keep this in the supplement.

## Ecological interpretation of Ross

2001 is an externally documented B-15A/C-16 disturbance trough.

Published work already shows colony-specific effects on:

- sea-ice persistence;
- routes/distance to open water;
- breeding participation and abandonment;
- breeding dispersal;
- apparent survival.

Thus the immediate asymmetry is interpreted first as:

    shared disturbance
    x colony-specific access geometry
    -> unequal local breeding response.

Configuration-mediated hysteresis remains a secondary longer-term hypothesis, not the primary explanation of the rebound pulse.

## Ross path is non-monotonic

1999 -> 2001:

    N down
    E up.

2001 -> 2002:

    N up
    E down.

2002 -> 2012:

    N up
    E modestly up.

The frozen 2001–2012 deconcentration prediction remains a formal FAIL.

## Prospective sign test 1 — Bird Island Gentoo

Frozen 1981 -> 2024 six-unit endpoint:

    N +34.2%
    E +15.7%.

This was not a preidentified disturbance/recovery phase.

Its role:

> positive aggregate change can accompany increased spatial redundancy.

Preallowed temporal audit across 42 transitions:

    N up / E up     12
    N up / E down    9
    N down / E up    8
    N down / E down 13.

Therefore aggregate and spatial signs are not deterministically locked.

Do not call them statistically independent; annual continuous changes are moderately correlated.

## Prospective sign test 2 — global emperor penguins

Frozen 50-colony 2009 -> 2018 posterior-median endpoint:

    N -12.4%
    E -12.8%.

Local signs:

    30 colonies down
    20 up.

Predeclared eight-region sensitivity contains all four N/E sign combinations.

This is point-estimate evidence; no joint posterior E probability is claimed.

## Optional Bird mechanism lead — qualified

A separate Bird mechanism contract predeclared:

    chicks_t / nests_t
        ->
    next-year local share change.

Frozen result:

    beta = +0.324
    permutation p = 0.0001.

But the result is **not a clean confirmatory mechanism test** because:

1. predictor and response share current nest abundance in their denominator geometry;
2. the operational local ratio can exceed 2 due phenology/count timing;
3. denominator-only negative controls can generate a large positive association.

Post-result denominator-safer model:

    log next nests
        ~ log current nests
        + log(1 + chicks)
        + unit/year FE

still gives a smaller positive signal:

    standardized beta ~= 0.15
    permutation p = 0.0126.

This suggests but does not confirm that local chick output carries information beyond current breeding abundance.

An independent prospective Port Lockroy ratio-free replication was attempted but **SUPPORT FAIL** because late/crèche chick counts are not available at fixed sub-colony resolution.

Therefore:

> **the mechanism selecting which nodes receive the contrast-mode rebound remains unresolved.**

Do not promote the Bird success result to a core Results pillar.

## Mathematical language

For local breeding abundance n_i:

    N = sum_i n_i
    p_i = n_i/N.

With local instantaneous log-change r_i:

    d log N / dt = r_bar
    d log p_i / dt = r_i - r_bar.

Use this only as explanatory language:

- common mode = aggregate change;
- contrast modes = spatial reallocation.

The mathematics is established and is not the paper's novelty.

## Prior-art boundary

Already established:

- aggregate versus local recovery mismatch;
- abundance versus community-composition recovery mismatch;
- spatial synchrony/asynchrony;
- aggregate versus compositional variability;
- Allee effects/hysteresis.

The paper's niche is narrower:

> relative-abundance restoration among persistent breeding nodes of one species after a documented disturbance, plus prospective external tests showing no fixed aggregate/spatial sign relationship.

## Evidence hierarchy

### Main text pillars

1. Ross natural experiment + 9.41% inverse-path mismatch.
2. Bird prospective positive-net-change sign test.
3. Emperor prospective decline-side sign test.

### Discussion / supplement

- Palmer/Signy differential attrition;
- Heard dominance reversal;
- Beaufort capacity-release spread;
- Ross matched-N branch dependence;
- Bird success-to-allocation qualified mechanism lead;
- Port Lockroy mechanism support fail;
- configuration-memory hypothesis;
- bounded-count sensitivity.

## Main figures

1. Ross disturbance/rebound path.
2. Exact inverse-path observed vs expected rebound by six component.
3. Bird + Emperor prospective sign tests.
4. Small conceptual common/contrast diagram.

Do not make the paper visually look like a catalogue of seven penguin systems.

## Discussion opening

> Population recovery is often judged by whether abundance returns, but a recovered total does not require exact restoration of its spatial allocation. After a documented mega-iceberg disturbance on Ross Island, 97% of lost breeding abundance returned within the immediate rebound. The rebound largely retraced the preceding loss, yet about 9% of rebound abundance would have to be reallocated among breeding components to reproduce an exact inverse path, with the excess concentrated at Cape Crozier West.

Then:

> Prospectively frozen tests in Gentoo and emperor penguins showed that the direction of spatial change is not fixed by whether aggregate breeding abundance increases or declines.

## Strongest claim

> **Near-complete numerical rebound can leave a moderate, structured spatial mismatch among persistent breeding nodes.**

Broader supported statement:

> **The sign of aggregate breeding change does not uniquely determine the direction of spatial reallocation.**

Mechanism statement:

> **What determines which nodes receive the contrast-mode rebound remains open.**

## Journal fit

**Ecology** remains the appropriate ceiling and target.

The current package has:
- a natural disturbance/rebound experiment;
- calibrated effect size;
- transparent count-uncertainty boundary;
- deterministic robustness threshold;
- two prospective external sign tests;
- an explicitly unresolved mechanism.

That is stronger than overclaiming a mechanism from the Bird ratio result.
