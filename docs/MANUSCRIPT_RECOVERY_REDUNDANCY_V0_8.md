# Manuscript spine v0.8 — Near-complete numerical rebound leaves a spatial mismatch

**Status:** preferred manuscript spine after calibrating the Ross inverse-path effect size and auditing historical count uncertainty. Supersedes v0.7.

## Working title

**Near-complete breeding rebound does not guarantee spatial restoration**

Alternatives:

- **A population can recover in number without returning in place**
- **Numerical rebound and spatial restoration diverge after disturbance**
- **Near-complete rebound leaves a structured spatial mismatch in a colonial breeding network**

## One ecological question

> **After a shared disturbance, does breeding abundance return to the same places from which it was lost?**

Ross Island supplies the focal natural experiment.

Bird Island Gentoo and global emperor penguins test whether the direction of spatial change is generally tied to the direction of aggregate change.

## Focal result in two numbers

Ross Island:

    1999 -> 2001 shock
    2001 -> 2002 immediate rebound.

Aggregate shock loss:

    112,613 occupied breeding territories.

Immediate rebound gain:

    109,198.

Therefore:

    96.97%

of the aggregate loss returned.

But against an exact inverse-path allocation, scaled to the observed rebound total:

    10,270.6 breeding pairs

would need to be reallocated among the six breeding components.

That is:

    9.41%

of the rebound.

This is the central effect size.

## What 9.41% means

The shock-loss and rebound-gain vectors are strongly aligned:

    cosine = 0.99695.

So the rebound broadly retraces the disturbance.

It is **not** wholesale relocation.

The exact inverse-path residuals are:

| component | observed rebound minus inverse-path expectation |
|---|---:|
| Royds | -1,313 |
| Bird South | -3,891 |
| Bird Middle | -931 |
| Bird North | -1,213 |
| Crozier West | **+10,271** |
| Crozier East | -2,924 |

Crozier West is the only positive excess component.

Thus the calibrated statement is:

> **The rebound largely retraced the disturbance, but roughly one tenth of rebound abundance was spatially reallocated toward Cape Crozier West relative to exact reversal.**

## Aggregate recovery versus spatial restoration

By 2002:

    N2002 / N1999 = 98.35%.

But:

    E3_2002 / E3_1999 = 93.66%
    E6_2002 / E6_1999 = 88.48%.

Local fractions of shock loss restored:

    Royds             38.7%
    Bird South        10.8%
    Bird Middle       34.9%
    Bird North        88.9%
    Crozier West     109.8%
    Crozier East      64.9%.

Therefore a nearly restored total coexists with heterogeneous local deficits and one overshoot.

## Measurement boundary

The 1999, 2001 and 2002 Ross anchors were collected with the same broad pre-2006 film/manual aerial-photo workflow.

There is no obvious count-method discontinuity across 2001–2002.

However, the historical source does not report:

- component-specific count standard errors;
- repeated-observer variance;
- year-specific detection probabilities;
- a validated count-error model for these exact photographs.

Therefore:

> **9.41% is a calibrated descriptive effect size, not an effect with a formal sampling-error CI.**

Do not write that the mismatch is statistically greater than census error.

Do not borrow a ±10% precision class from other Adélie aerial surveys as if it applied to these historical images.

## Why the natural experiment is still informative

2001 is a documented B-15A/C-16 disturbance trough.

The response is occupied breeding territories / breeding-pair abundance, not total adult population size.

Published Ross work shows that the mega-icebergs altered:

- sea-ice persistence;
- access distance/routes to open water;
- breeding participation/abandonment;
- breeding dispersal;
- apparent survival;

and did so differently among colonies.

The immediate asymmetry therefore has a plausible spatial filter:

    shared disturbance
    x
    colony-specific access geometry
    -> unequal local breeding response.

This mechanism is prior knowledge applied to the new allocation decomposition, not newly discovered here.

## Ross path is not monotonic

### 1999 -> 2001

    N down
    all six components down
    E up.

The shock temporarily equalizes the breeding distribution.

### 2001 -> 2002

    N up
    all six components up
    E sharply down.

The rebound reconcentrates toward Crozier.

### 2002 -> 2012

    N up
    E modestly up.

So Ross does not support a monotonic “recovery concentrates” law.

The frozen 2001–2012 deconcentration prediction remains a formal FAIL.

## Prospective external test 1 — Bird Island Gentoo

The six-unit roster and earliest/latest-complete endpoint rule were frozen before count magnitudes were opened.

1981 -> 2024:

    N: 3,331 -> 4,470
    +34.2%

    E: 3.569 -> 4.128
    +15.7%.

This interval was not a preidentified disturbance-recovery episode.

Its role is narrower:

> **positive aggregate change can accompany spatial equalization.**

A contract-preallowed temporal audit across 42 complete-season transitions finds:

    N up / E up     12
    N up / E down    9
    N down / E up    8
    N down / E down 13.

All four sign combinations occur.

Continuous annual delta log N and delta log E are moderately correlated, so do not call them statistically independent.

Say:

> their signs are not deterministically locked.

## Prospective external test 2 — global emperor penguins

Frozen frame:

    50 paired colonies
    2009 -> 2018
    posterior-median colony abundance index.

Result:

    N -12.4%
    E -12.8%.

Local signs:

    30 colonies down
    20 up.

Thus decline-associated concentration does not require universal local decline.

The predeclared eight-region sensitivity contains all four N/E sign combinations.

Across those eight regions the descriptive correlation between log N ratio and log E ratio is near zero, but n=8 and this is not an independence test.

## Mathematical language

Keep the algebra secondary.

For local breeding abundance n_i:

    N = sum_i n_i
    p_i = n_i/N.

With local instantaneous log-change r_i:

    d log N / dt = r_bar
    d log p_i / dt = r_i - r_bar.

Use:

- **common mode** for aggregate change;
- **contrast modes** for relative local change.

This language explains the data.

It is not claimed as a new theory.

For finite abundance vectors:

    E = (||n||_1 / ||n||_2)^2.

This zero-safe form is useful in the Emperor analysis because one baseline posterior median is zero.

## Prior-art boundary

Already established:

- aggregate versus local recovery mismatch in metapopulations;
- abundance versus composition mismatch in community recovery;
- spatial synchrony/asynchrony;
- aggregate versus compositional variability;
- Allee effects and hysteresis.

Our niche is narrower:

> **relative-abundance restoration among persistent spatial breeding nodes of one species after a documented disturbance, with prospective external tests of directional generality.**

## Evidence hierarchy

### Main text

1. Ross natural experiment and 9.41% inverse-path mismatch.
2. Bird prospective positive-net-change sign test.
3. Emperor prospective decline-side sign test.

### Supporting / supplement

- Palmer/Signy differential attrition;
- Heard dominance reversal;
- Beaufort capacity-release spread;
- Ross matched-N branch dependence;
- configuration-memory hypothesis.

Do not let supporting cases turn the paper into a catalogue.

## Main figures

### Figure 1 — Ross disturbance/rebound path

1999, 2001, 2002, 2012:
- total N;
- E;
- colony/component shares.

### Figure 2 — exact inverse-path mismatch

For each of six components:
- observed rebound gain;
- inverse-path expected rebound;
- residual.

Make the +10,271 Crozier West excess visually obvious.

### Figure 3 — external prospective sign tests

Bird:
    N ratio vs E ratio.

Emperor:
    global point plus eight regional points.

Quadrant lines at ratio = 1.

### Figure 4 — conceptual common/contrast decomposition

Small and late in the paper, not the lead figure.

## Results order

1. Define Ross disturbance and measurement boundary.
2. Show 96.97% aggregate restoration.
3. Quantify 9.41% inverse-path spatial mismatch.
4. Show shock/rebound/later path directions.
5. Place immediate asymmetry in known iceberg/access context.
6. Bird prospective sign test.
7. Emperor prospective sign test.
8. General synthesis.

## Discussion opening

> Population recovery is often judged by whether abundance returns, but a recovered total need not imply that abundance returned to the same places. After a documented mega-iceberg disturbance on Ross Island, 97% of the lost breeding abundance returned within the immediate rebound. The rebound was strongly aligned with the preceding loss, yet about 9% of rebound abundance would have to be reallocated among breeding components to reproduce an exact spatial inverse path, with the excess concentrated at Cape Crozier West.

Second paragraph:

> Prospective tests in Gentoo and emperor penguins showed that this spatial direction is not universal: positive aggregate change can coincide with greater spatial evenness, while decline can coincide with concentration or equalization across regions.

## Strongest claim

> **Near-complete numerical rebound can leave a moderate, structured spatial mismatch among persistent breeding nodes.**

Broader statement:

> **The sign of aggregate breeding change does not uniquely specify the direction of spatial reallocation.**

## Claim ceiling

Do not claim:
- statistically significant Ross mismatch without count-error data;
- wholesale spatial reorganization;
- recovery generally concentrates;
- recovery generally spreads;
- aggregate and spatial change are statistically independent;
- first discovery that abundance and composition differ;
- causal hysteresis.

## Journal fit

**Ecology** remains the strongest target.

The paper now has:
- a natural disturbance experiment;
- a calibrated effect size;
- explicit measurement limits;
- two prospective external sign tests;
- a restrained mechanistic interpretation.

A broader conceptual journal would still require prospective prediction of **which nodes receive the rebound**, not only proof that the rebound is imperfectly allocated.
