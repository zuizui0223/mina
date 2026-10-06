# Which penguin breeding component disappears next? — synthesis v1

**Status:** exploratory held-population forecast on already-exposed Palmer/Signy component histories. Not part of the frozen Ecology submission.

## Result

The strongest short-horizon predictor is unexpectedly simple: **current local component size**.

Across the five component-resolved trajectories:

- **579** eligible t-1 → t → t+1 component transitions;
- **22** exact-zero losses;
- **15** population-years in which one or more monitored components disappeared next year.

A ridge-logistic model using only current local size plus relative time produced a standardized local-size coefficient of:

```
beta_size = -1.999
```

and leave-one-population-out log loss:

```
0.11596
```

Within the 15 held-out event-years, this size model ranked an actual next-year loss as the **highest-risk currently occupied component in 14/15 years = 93.3%**. The median actual loss lay at the 100th percentile of predicted risk within its yearly risk set.

Palmer-only gives essentially the same result:

- beta_size = **-2.372**;
- top-1 event-year hit = **12/13 = 92.3%**.

## Recent decline does not help

The generated prediction was that recent local decline would identify components on an accelerating route to extinction beyond current size.

It failed.

Across all five trajectories:

```
beta_recent_growth = +0.049
```

rather than the predicted negative direction, and adding recent growth worsened held-population log loss:

```
Msize   0.11596
Mtrend  0.13289
```

Top-1 event-year hit also fell from **93.3% to 86.7%**.

Palmer-only is stronger in the same wrong direction:

```
beta_recent_growth = +0.161
Msize log loss      = 0.13642
Mtrend log loss     = 0.16374
top-1 hit           92.3% -> 84.6%
```

Thus the striking Torgersen example of an unusually steep 72→37 pair decline preceding early extinction is biologically informative but does not generalize here as a transferable annual trajectory rule.

## Relative share does not help either

Adding current regional/local-population share also worsened held-population prediction:

```
Mshare log loss = 0.13441
```

compared with 0.11596 for current size.

So the near-term loss ordering is not simply "the smallest share" after local absolute size is known.

## Ecological interpretation

This result changes the process story.

### Not a fixed refuge hierarchy

Palmer's initially dominant component ultimately disappears in all three populations, whereas the initial Signy core persists. Historical dominance therefore does not define a universal refuge.

### But a very strong moving state hierarchy

At any given year, the components that have already become locally small are overwhelmingly the ones that disappear next.

This suggests a **moving-margin process**:

> environmental and demographic processes progressively change the local size of breeding components; once a component reaches the current low-abundance margin, its short-term extinction hazard becomes high.

The important mechanistic question is therefore not primarily:

> why did this component decline unusually fast last year?

but:

> **what causes particular breeding components to be driven into the low-abundance margin while others retain enough local capacity to remain large?**

That moves the causal target upstream from the last annual step to local habitat quality/capacity, snow, geometry, reproductive performance, and longer-term demographic history.

## Connection to Torgersen physical evidence

The independent Torgersen reconstruction gives exactly this upstream environmental structure.

- larger historic sub-colonies disappeared later;
- south-facing sub-colonies disappeared earlier than similarly sized north-facing colonies;
- all 10 south-aspect historic sub-colonies were extinct by 2022, versus 8/13 north-aspect sub-colonies;
- a steep one-year decline can accelerate an individual case, but the broader extinction order is structured by size and aspect.

Thus a coherent two-timescale hypothesis emerges:

1. **slow local filtering** — snow/topography/capacity moves breeding components toward or away from the low-abundance margin;
2. **fast state-dependent pruning** — current low local abundance predicts which component disappears next.

## Forecast implication

A future physically mapped model should predict extinction in two layers:

```
environment / capacity -> current local state -> near-term extinction
```

The key test is whether physical habitat variables improve *out-of-system* prediction of which components become small **before** the simple current-size model already makes their disappearance obvious.

That is more informative than adding another short-lag abundance derivative to an already small colony.
