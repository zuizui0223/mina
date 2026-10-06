# Penguin extinction-horizon forecast v1

**Status:** exploratory forecasting analysis on already-exposed Palmer/Signy component histories. It cannot alter or delay the frozen Ecology submission.

## Question

How far in advance does current local breeding-component size identify the component that will reach exact zero?

The prior one-year forecast found that current size alone ranked an actual next-year loss #1 in 14/15 event-years. The present analysis freezes the same state variable across longer horizons before inspecting those longer-horizon outcomes.

## Frozen panels

Exactly the same component-resolved panels:
- Palmer Adélie: Cormorant, Humble, Litchfield.
- Signy Adélie: A1+A60, A2, A3, A4, A64.
- Signy chinstrap: C15, C16, C17, C18, C46, C47, C79, C80, C81.

No roster repair or low-count pseudo-absence threshold.

## Forecast horizons

- 1 year
- 3 years
- 5 years

A focal component-year t is eligible for horizon h only if:
1. focal count at t is >0;
2. every calendar year t+1 ... t+h is observed in the frozen panel.

Any irregular Signy gap censors that window.

Outcome:
```
loss_within_h = 1 if any exact numeric zero occurs in t+1 ... t+h
```

## Predictors

Primary state model:
```
Msize = z_within_population(log1p(count_t)) + z_within_population(relative_time)
```

Secondary trajectory model, on windows where t-1 is also calendar-consecutive:
```
Mtrend = Msize + z_within_population(log1p(count_t)-log1p(count_t-1))
```

No share, network, interaction, spline or threshold is added.

## Evaluation

Leave one population trajectory out.

For each horizon and model report:
- held-population log loss;
- Brier score;
- pooled standardized coefficients;
- event-year top-1 and top-2 hit fractions;
- median percentile rank of actual future losses within the current risk set.

For a population-year with multiple components that will be lost within the horizon, a top-1 hit is true if the highest predicted-risk currently occupied component is among those future losses.

## Generated predictions

1. Msize should be strongest at 1 year.
2. Ranking performance should weaken with forecast horizon if current low abundance is a proximal rather than long-range predictor.
3. Recent growth may become more informative at 3–5 years; it is considered descriptively useful only if its coefficient is negative and held-population log loss is lower than Msize at that same horizon.

No p-values are used.

## Interpretation

If current size remains highly predictive even at 5 years, the low-abundance margin develops well before final extinction and environment must be tested upstream of that margin.

If size performance deteriorates strongly by 3–5 years, that defines the lead time at which physical habitat/snow/capacity information has room to improve forecast skill.

## Boundaries

Operational census-unit zero is not necessarily physical habitat extinction.
Overlapping multi-year outcomes are used for forecasting, not independent inferential replicates.
This analysis does not identify movement, mortality, recruitment failure or breeding skipping.
