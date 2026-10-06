# Penguin breeding-network loss-feedback screen v1

**Status:** exploratory analysis on already-exposed Palmer/Signy component histories. It cannot modify or delay the frozen Ecology submission.

## Question

After controlling for how small a focal breeding component already is, does loss of the surrounding breeding network make that component more likely to disappear next?

This is the first direct screen of the generated hypothesis:

> breeding-site loss may reduce the functional support of the remaining breeding network and thereby facilitate further local loss.

## Unit of analysis

A focal component-year transition is eligible when:
- the focal component has a numeric count > 0 at season t;
- the same component has a numeric count in the next **calendar-consecutive** season t+1;
- the monitored component roster is the already-frozen Palmer/Signy roster.

Outcome:

```
loss_next = 1 if focal count at t+1 == 0, else 0
```

No low-count threshold or pseudo-absence definition is allowed.

## Frozen populations

- Palmer Adélie: Cormorant, Humble, Litchfield stable-roster panels.
- Signy Adélie: A1+A60, A2, A3, A4, A64.
- Signy chinstrap: C15, C16, C17, C18, C46, C47, C79, C80, C81.

Irregular Signy gaps are excluded because the transition must be calendar-consecutive.

## Predictors measured at t

1. **local size**
   `log1p(focal_count)`

2. **surrounding breeder mass**
   `log1p(total_count - focal_count)`

3. **network integrity**
   fraction of the other frozen components that are still occupied (>0):

```
occupied_other_fraction =
number of other components with count > 0
/
(number of frozen components - 1)
```

4. **relative time**
   scaled 0-1 within each population panel.

All continuous predictors are standardized within population before pooling.

## Frozen model family

Use ridge logistic regression only; no predictor search.

- M0: local size + relative time
- Mmass: M0 + surrounding breeder mass
- Mintegrity: M0 + network integrity
- Mboth: M0 + surrounding breeder mass + network integrity

The key generated prediction is:

> if loss of neighbouring breeding components facilitates further loss, the standardized coefficient of network integrity should be **negative** for loss risk (higher integrity = lower risk), and Mintegrity/Mboth should improve held-population prediction over M0.

## Evaluation

Because the data are already exposed, do not report inferential p-values.

Report:
- eligible transitions;
- loss events;
- standardized coefficients;
- leave-one-population-out mean log loss for each model;
- leave-one-population-out Brier score for each model;
- improvement versus M0;
- result separately for all five trajectories and Palmer-only as a sensitivity, because Signy contributes few exact-zero events.

A useful descriptive signal requires both:
1. network-integrity coefficient < 0 in the pooled model; and
2. held-population log loss lower than M0.

If either fails, the network-loss-feedback hypothesis is not supported by this screen.

## Boundaries

This analysis cannot identify:
- individual emigration;
- social attraction;
- rescue effect;
- mortality versus breeding skipping;
- causal hysteresis.

Network integrity is an observational state variable, not a manipulation.
