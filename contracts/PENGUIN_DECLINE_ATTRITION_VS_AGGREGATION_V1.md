# Penguin decline: differential attrition versus aggregation v1

**Status:** post-outcome descriptive decomposition on already-exposed Palmer/Signy trajectories. No inferential p-values. This analysis cannot modify or delay the frozen Ecology submission.

## Biological question

When a declining penguin population becomes spatially concentrated, does concentration arise because breeders accumulate in surviving components, or because marginal components decline faster while surviving components merely decline more slowly?

These mechanisms make the same effective-number endpoint but imply different processes.

## Frozen panels

Use exactly the already-frozen component panels:

- Palmer Adélie: Cormorant, Humble, Litchfield stable-roster census panels.
- Signy Adélie: A1+A60, A2, A3, A4, A64.
- Signy chinstrap: C15, C16, C17, C18, C46, C47, C79, C80, C81.

Only calendar-consecutive annual transitions are used for annual change decomposition. Missing Signy seasons are gaps, not zeroes.

## Annual quantities

For each component i between t and t+1:

```
delta_i = n_i,t+1 - n_i,t
```

For each population-year:

```
gross_gain = sum(max(delta_i, 0))
gross_loss = sum(max(-delta_i, 0))
net_change = gross_gain - gross_loss
gain_loss_ratio = gross_gain / gross_loss
```

The effective component number is

```
E = 1 / sum(p_i^2)
```

with p_i = n_i / sum(n).

Primary descriptive subset:

```
net_change < 0 and delta_E < 0
```

i.e. years in which total abundance and effective breeding space both contract.

## Frozen outputs

For each population and pooled descriptively:

1. number of calendar-consecutive annual transitions;
2. number of total-decline transitions;
3. number of joint N-down/E-down transitions;
4. fraction of joint contraction transitions in which at least one component nevertheless grows in absolute count;
5. median and total-weighted gain/loss ratio during joint contraction;
6. gross positive gains and gross losses summed across joint contraction years;
7. fraction of components whose first-to-last share increases while their absolute count decreases;
8. first/last absolute count and share of the initial dominant component;
9. first/last absolute count and share of the final dominant component;
10. number of components with positive first-to-last absolute count change.

## Interpretation

- **Differential attrition signature:** E decreases mainly while all or nearly all components lose absolute breeders; components gain share by declining more slowly.
- **Aggregation-compatible signature:** substantial gross gains occur in some components while total N and E decline.

No threshold is used to classify the process. Report the continuous gain/loss ratios and the raw event counts.

## Boundaries

This decomposition cannot identify individual movement. Absolute growth in one component while another declines could reflect immigration, recruitment, survival differences or breeding participation. Conversely, absence of absolute gains rules out a need for aggregation to explain the concentration pattern but does not prove no movement occurred.
