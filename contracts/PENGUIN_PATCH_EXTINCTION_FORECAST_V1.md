# Penguin patch-extinction forecast v1

**Status:** exploratory forecasting analysis on already-exposed Palmer/Signy component histories. It cannot modify or delay the frozen Ecology submission.

## Biological question

Among breeding components that are still occupied now, which one disappears next?

The purpose is to distinguish a static size rule from a dynamic trajectory rule.

Published Torgersen evidence provides the independent biological motivation: larger sub-colonies tended to go extinct later, but one sub-colony that fell from 72 to 37 breeding pairs in one year went extinct 3 and 11 years earlier than similarly sized south- and north-aspect colonies. This motivates testing whether recent local decline contains information beyond current local size.

## Unit

A focal component-year at season t is eligible if:

- counts at t-1, t and t+1 are numeric;
- t-1, t and t+1 are calendar-consecutive;
- focal count at t is >0.

Outcome:

```
loss_next = 1 if focal count at t+1 == 0, otherwise 0
```

No low-count pseudo-absence threshold is allowed.

## Frozen population panels

- Palmer Adélie: Cormorant, Humble, Litchfield stable-roster panels.
- Signy Adélie: A1+A60, A2, A3, A4, A64.
- Signy chinstrap: C15, C16, C17, C18, C46, C47, C79, C80, C81.

Irregular Signy intervals are excluded.

## Predictors at t

1. **current local size**
   `log1p(count_t)`

2. **recent local growth**
   `log1p(count_t) - log1p(count_t-1)`

3. **current local share**
   `count_t / total_population_t`

4. **relative time**
   0–1 within the population record.

All continuous predictors are standardized within population before pooling.

## Frozen model family

Use ridge logistic regression only.

- **Msize** = current local size + relative time
- **Mtrend** = Msize + recent local growth
- **Mshare** = Msize + current local share
- **Mstate** = Msize + recent local growth + current local share

No interactions, splines, thresholds or alternate lags.

Generated prediction:

> if extinction order contains dynamic information beyond current size, recent local growth should have a **negative** coefficient for loss risk and Mtrend/Mstate should outperform Msize in held-population prediction.

## Evaluation

### A. Leave-one-population-out prediction

For each model report:
- pooled standardized coefficients;
- held-population log loss;
- Brier score;
- improvement relative to Msize.

### B. "Which patch disappears next?" ranking

Using leave-one-population-out predictions, for every held population-year in which one or more focal components disappear at t+1:

- rank all occupied eligible components by predicted loss risk;
- report whether at least one actual loss is ranked #1;
- report top-2 hit;
- report percentile rank of each actual loss among the risk set.

Primary descriptive ranking endpoint:
- top-1 event-year hit fraction;
- median percentile rank of actual losses.

The dynamic-state hypothesis is considered descriptively supported only if:
1. recent-growth coefficient < 0 in Mtrend;
2. Mtrend held-population log loss < Msize;
3. Mtrend top-1 event-year hit fraction >= Msize.

If (1) or (2) fails, do not promote recent trajectory as a transferable predictor.

## Sensitivity

Repeat the same frozen model family on Palmer-only trajectories.

No alternate endpoint or threshold may rescue a failed result.

## Boundaries

This screen predicts operational census-component loss, not physical habitat destruction.
It cannot distinguish movement, mortality, breeding skipping or recruitment.
Current share is a demographic state, not a measure of habitat quality.
