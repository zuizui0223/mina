# Manuscript spine v0.12 — Near-complete rebound is not exact spatial reversal

**Status:** preferred final state/allocation manuscript spine after both prospective clean mechanism routes failed. Mechanism searching in PR189 is closed. Supersedes v0.11.

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

## Mechanism status — explicitly unresolved

Bird Island produced a strong frozen statistical association:

    chicks_t / nests_t -> next-year share change
    beta = +0.324
    p = 0.0001.

But the predictor and response share current nest abundance in their denominator geometry, and the operational chicks/nests ratio can exceed two because of monitoring timing and late nesting. Denominator controls and backward symmetry show substantial mechanical structure.

A post-result ratio-free Bird diagnostic remained smaller and positive:

    standardized beta ≈ 0.15
    permutation p = 0.0126.

This was suggestive only.

### Prospective ratio-free replication — Signy Chinstrap

A separate mechanism contract was then frozen before late-fledgling magnitudes were summarized.

Provider semantics fixed a seven-colony core:

    C15, C18, C46, C47, C79, C80, C81.

Support yielded:

    15 consecutive eligible start seasons
    105 colony-season rows.

The predictor was late fledgling output residualized against current breeding abundance, colony and year.

The frozen next-season allocation model gave:

    beta_Q = -0.0225
    standardized beta = -0.064
    permutation p = 0.6837.

Six of seven leave-one-colony-out coefficients were negative.

Thus the prospective ratio-free second-species test **fails**.

Do not rescue it with:
- alternative lags;
- earlier chick counts;
- a different colony subset;
- a chicks/pair ratio.

Therefore:

> **local reproductive output is not an established predictor of the contrast mode, and the mechanism selecting rebound nodes remains unresolved.**

The Bird ratio result belongs only as a qualified measurement-sensitive lead, not as a mechanism result.

### Prospective denominator-independent configuration test — Ross subcolonies

A second clean route used mapped perimeter-to-area ratio, which does not contain current breeding abundance.

Support:

    491 consecutive-transition rows
    114 distinct subcolonies.

Frozen model:

    log(next active/current active)
      ~ colony x year FE
      + log(current active)
      + z(log perimeter-to-area)
      + z(log area).

Prediction:

    beta_P < 0.

Observed:

    beta_P = -0.0196
    +1 SD growth multiplier = 0.981
    permutation p = 0.1514.

All 114 leave-one-subcolony-out coefficients remained negative, but the frozen permutation criterion failed.

Colony-specific descriptive signs differed:

    Crozier -0.0288
    Royds   +0.0126.

This route is therefore also a **terminal FAIL**.

No alternative Schmidt terrain/geometry variable is searched as rescue.

### Final mechanism status

Bird:
    measurement-sensitive lead only.

Port Lockroy:
    SUPPORT FAIL.

Signy:
    prospective ratio-free FAIL.

Ross subcolony configuration:
    prospective denominator-independent FAIL.

Therefore:

> **the predictor of the contrast mode remains unresolved, and mechanism searching in PR189 stops here.**

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
- Signy prospective ratio-free mechanism FAIL;
- Ross subcolony configuration prospective FAIL;
- Port Lockroy mechanism SUPPORT FAIL;
- mechanism-closure record;
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

A future, genuinely independent mechanism project could raise its importance, but the current reproductive-output and configuration routes did not do so.

## Stop point for this paper

Do not add another mechanism screen to PR189.

The paper is complete at the state/allocation level:

- focal natural experiment;
- calibrated effect size;
- measurement boundary;
- prospective external sign tests;
- transparent failed mechanism attempts.

The next scientific project, if pursued, should start from a new prospectively measured predictor such as disturbance-induced access cost or individual movement/survival, not another post-hoc covariate in the already opened datasets.
