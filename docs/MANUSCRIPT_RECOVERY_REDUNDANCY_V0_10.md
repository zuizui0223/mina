# Manuscript spine v0.10 — Near-complete rebound is not exact spatial reversal

**Status:** superseded by `MANUSCRIPT_RECOVERY_REDUNDANCY_V0_11.md` after the prospective Signy Chinstrap ratio-free mechanism test failed.

## Working title

**Near-complete breeding rebound is not exact spatial reversal**

Alternatives:

- **A population can recover in number without retracing its disturbance exactly in space**
- **Aggregate breeding change and spatial allocation are not sign-locked**
- **Numerical rebound largely retraces loss but does not uniquely restore breeding-network composition**

## One ecological question

> **After a documented shared disturbance, does breeding abundance retrace the spatial pattern from which it was lost?**

Ross Island is the focal natural experiment.

The answer is:

> **mostly, but not exactly.**

That calibration matters.

## Ross focal natural experiment

Use the fixed six breeding components and three anchor states:

    1999 = last complete pre-shock state
    2001 = documented B-15A/C-16 disturbance trough
    2002 = immediate rebound.

Aggregate breeding abundance:

    1999  207,411
    2001   94,798
    2002  203,996.

Shock loss:

    112,613.

Immediate rebound:

    109,198.

Thus:

    96.97%

of the aggregate shock loss was regained, and the 2002 total reached:

    98.35%

of the 1999 total.

## How closely did the rebound reverse the loss?

The six-component loss and rebound vectors are strongly aligned:

    cosine = 0.99695.

Therefore the rebound **largely retraced** where breeding abundance had been lost.

Against an exact inverse-path reference that allocates the observed rebound in proportion to local shock losses:

    half-L1 mismatch = 10,270.6 breeding pairs
                     = 9.41% of rebound.

Observed-minus-inverse residuals:

    Royds          -1,312.7
    Bird South     -3,891.1
    Bird Middle      -930.5
    Bird North     -1,212.5
    Crozier West  +10,270.6
    Crozier East   -2,923.7.

Thus the mismatch is structured toward Crozier West.

Do not equate the 10,271-unit allocation difference with movement of 10,271 individual birds.

## Critical calibration: 9.41% is not exceptional within Ross

Three complete six-component down→up triplets exist in the frozen Ross series:

| sequence | loss restored | inverse-path mismatch | cosine |
|---|---:|---:|---:|
| 1989→1990→1991 | 34.8% | 9.12% | 0.9941 |
| 1999→2001→2002 | **97.0%** | **9.41%** | 0.9969 |
| 2002→2003→2004 | 122.1% | 10.63% | 0.9839 |

Therefore the focal mismatch magnitude is **ordinary-scale**, not exceptional.

The value of the focal episode comes from:

1. an independently documented regional disturbance;
2. near-complete aggregate rebound;
3. a pre-disturbance reference state;
4. known colony-specific disturbance/access geometry.

The paper must not claim an unusually large compositional anomaly.

## What is unusual in the focal transition

The immediate 2001→2002 compositional shift is the largest successive-transition six-component TV distance in the frozen Ross series:

    TV = 0.0975.

But the 1999→2002 reference-state mismatch:

    TV = 0.0497

is high rather than extreme relative to ordinary successive-year background.

So the correct story is:

> a large temporary disturbance/rebound pulse leaves a moderate residual compositional mismatch after the total nearly returns.

## Measurement boundary

The Ross series measures occupied nesting territories / breeding-pair abundance near incubation.

It does not directly measure total adult population size.

The historical source does not provide component-specific count uncertainty sufficient for a formal CI on the 9.41% mismatch.

A deterministic bounded-count sensitivity shows exact inverse reversal becomes feasible only under:
- ~22.7% common symmetric count perturbation if the observed aggregate rebound scale is fixed;
- ~13.8% if the common rebound scale is allowed to float.

These are robustness thresholds, not estimates of census error.

Keep them in supplement.

## Ross biological interpretation

2001 is a documented B-15A/C-16 disturbance trough.

Published work already shows spatially heterogeneous effects on:
- sea-ice persistence;
- access to open water;
- breeding participation/abandonment;
- breeding dispersal;
- apparent survival.

The immediate mismatch is therefore interpreted first as:

    shared disturbance
    × colony-specific access geometry
    → unequal local breeding response.

Do not invoke endogenous hysteresis as the primary mechanism.

Configuration memory remains a residual longer-term hypothesis.

## Prospective external sign test — Bird Island Gentoo

Frozen six-unit earliest/latest-complete comparison:

    1981→2024
    N +34.2%
    E +15.7%.

This is not a preidentified recovery interval.

Its role is narrow and important:

> **positive aggregate change can coincide with greater spatial evenness.**

Across 42 preallowed annual transitions:

    N↑ E↑  12
    N↑ E↓   9
    N↓ E↑   8
    N↓ E↓  13.

All four sign combinations occur.

Continuous annual changes are moderately correlated, so use:

    not sign-locked

not:

    statistically independent.

## Prospective external decline test — global Emperor penguins

Frozen 50-colony 2009→2018 posterior-median endpoint:

    N -12.4%
    E -12.8%.

Local signs:

    30 down
    20 up.

Thus decline-associated concentration does not require universal local decline.

The predeclared eight ice-region sensitivity contains all four N/E directional quadrants.

This independently reinforces:

> the sign of aggregate change does not fix the sign of spatial reallocation.

## Bird mechanism lead — explicitly unresolved

A frozen Bird chicks/nests → next-year share statistic passes strongly:

    beta = +0.324
    p = 0.0001.

But predictor and response share current nest abundance, and the operational ratio can exceed two because of count timing/late nesting.

Denominator controls and backward symmetry show substantial mechanical geometry.

A post-result ratio-free diagnostic remains positive but smaller:

    standardized beta ≈ 0.15
    permutation p = 0.0126.

Therefore:

> local reproductive output may carry prospective information about later allocation, but the mechanism is not confirmed.

Do not promote this to a main Results pillar.

Independent denominator-safer mechanism routes are being handled separately.

## Mathematical language

For local breeding abundance n_i:

    N = Σ n_i
    p_i = n_i/N.

With local log-change r_i:

    d log N/dt = r_bar
    d log p_i/dt = r_i - r_bar.

Use:

- common mode = aggregate change;
- contrast modes = relative local reallocation.

This is explanatory algebra, not novelty.

For zero-safe finite-state description:

    E = (||n||_1 / ||n||_2)^2.

## Prior-art boundary

Already established in broader ecology:
- aggregate versus local recovery mismatch;
- abundance versus composition mismatch;
- spatial synchrony/asynchrony;
- aggregate versus compositional variability;
- path dependence/hysteresis.

The paper's empirical niche is narrower:

> **spatial restoration of a within-species colonial breeding network against an explicit pre-disturbance abundance vector, followed by prospective external tests showing that aggregate and spatial directions are not sign-locked.**

## Evidence hierarchy

### Main

1. Ross documented natural disturbance/rebound.
2. Bird prospective positive-net-change sign test.
3. Emperor prospective decline sign test.

### Supporting

- Palmer/Signy differential attrition;
- Heard dominance reversal;
- Beaufort capacity-opening spread;
- Ross matched-N branch dependence;
- Bird mechanism signal with denominator audit;
- count-uncertainty and bounded-count sensitivity.

Do not make the main text a catalogue of penguin systems.

## Main figures

### Figure 1 — Ross natural experiment

1999, 2001, 2002, 2012:
- N;
- E;
- shares.

### Figure 2 — inverse-path restoration

For six components:
- observed rebound;
- exact inverse-path expected rebound;
- residuals.

Annotate:

    aggregate loss restored = 96.97%
    allocation mismatch = 9.41%
    cosine = 0.997.

Include a small inset with the other two down→up episodes to show the mismatch is not exceptional.

### Figure 3 — prospective sign tests

Bird:
    N↑ E↑

Emperor:
    global N↓ E↓
    regional all four quadrants.

### Figure 4 — compact common/contrast schematic

Keep mathematics visually secondary.

## Discussion opening

> Population recovery is often judged by whether abundance returns. On Ross Island, 97% of breeding abundance lost during a documented mega-iceberg disturbance returned within the immediate rebound. The loss and rebound vectors were almost collinear, showing that recovery largely retraced the disturbance spatially. Yet the rebound was not an exact inverse: about 9% of rebound allocation differed from proportional restoration of local losses, with the excess concentrated at Cape Crozier West. This mismatch was moderate rather than exceptional relative to other Ross abundance reversals.

Then:

> Prospectively frozen Gentoo and emperor-penguin tests showed why the sign of aggregate change cannot substitute for measuring spatial allocation.

## Strongest claim

> **Near-complete numerical rebound can be accompanied by a moderate, structured failure of exact spatial reversal among persistent breeding nodes.**

Broader claim:

> **Aggregate breeding change and spatial reallocation are not sign-locked.**

Do not claim:
- an exceptional Ross mismatch;
- recovery generally concentrates;
- recovery generally spreads;
- causal hysteresis;
- a universal mechanism selecting rebound nodes.

## Journal fit

**Ecology** remains the realistic target.

But the state/allocation paper is now calibrated rather than spectacular.

A mechanism result that prospectively predicts which breeding nodes receive the contrast-mode rebound would materially raise its importance.

## Next decisive step

Stop collecting sign examples.

The only major remaining scientific upgrade is:

> **predict the contrast mode prospectively from an independently measured local state.**

Priority predictors:
- mapped configuration / perimeter-to-area ratio;
- disturbance-induced access cost;
- usable capacity;
- local reproductive output measured independently of current-abundance denominator;
- movement or survival.

Those belong in a mechanism extension, not as post-hoc rescue.
