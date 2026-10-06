# The low-abundance margin is established years before penguin breeding-component loss

**Status:** exploratory forecasting synthesis on already-exposed Palmer/Signy component histories. Not part of the frozen Ecology submission.

## Question

The one-year forecast showed that current local size almost perfectly orders which occupied component disappears next. Does that information appear only immediately before extinction, or is the future loss order already visible several years earlier?

## Result

Current local size remains strongly associated with exact-zero loss across all three frozen horizons.

| Horizon | eligible records | future-loss records | standardized size coefficient | event-year top-1 hit | top-2 hit | median loss-risk percentile |
|---|---:|---:|---:|---:|---:|---:|
| 1 year | 632 | 22 | **-1.99** | **93.3%** | 93.3% | 1.000 |
| 3 years | 566 | 62 | **-1.90** | **97.1%** | 100% | 1.000 |
| 5 years | 496 | 96 | **-1.68** | **95.8%** | 100% | 0.875 |

The longer-horizon top-1 percentages should not be interpreted as intrinsically "better" forecasts because a 3- or 5-year window can contain multiple future losses. The important result is the persistence of the strong negative size coefficient and the very high within-year risk ranking.

Thus components that will disappear several years later are already disproportionately small.

## Recent one-year trajectory adds little

On rows where recent growth is available:

- 1-year horizon: beta_recent = **+0.049**, log-loss change vs size model = **-0.0169** (worse);
- 3-year horizon: beta_recent = **-0.063**, log-loss change = **-0.0054** (worse);
- 5-year horizon: beta_recent = **-0.171**, log-loss improvement = only **+0.0005**.

So recent decline acquires the expected negative direction at longer horizons, but provides essentially no transferable predictive gain beyond current local size.

## Process interpretation

The low-abundance margin is not merely a final one-year threshold.

A more plausible chronology is:

```
slow local environmental / demographic filtering
        ↓
persistent low local abundance
        ↓
component remains among the smallest for several years
        ↓
eventual exact-zero loss
```

This fits the new mass-balance result that decline concentration is produced mainly by differential attrition rather than active aggregation.

## What future environmental prediction should target

A physical habitat model should **not** be judged mainly by whether it improves a one-year extinction forecast after current population size is known. At that point the biological state already contains most of the information.

The higher-value target is:

> **Which physical breeding patches are driven into a persistent low-abundance state years before extinction?**

That can be operationalized in an independent mapped dataset using a continuous response such as future log abundance, long-run proportional decline, or time to entry into a pre-frozen low-abundance state.

The environmental causal chain to test is therefore:

```
snow / aspect / elevation / usable breeding capacity
        ↓
multi-year suppression of local population state
        ↓
persistent position near the low-abundance margin
        ↓
selective patch loss
```

## Relation to island ecology

This makes the island-environment role more precise.

Island/subcolony geography need not trigger the final extinction event directly. Instead, physical breeding conditions can determine the **long-lived carrying state** of each patch. Patch extinction order then emerges because some locations are held at chronically smaller populations than others.

This is compatible with the independent Torgersen result that physical sub-colony size and snow-related aspect structure extinction timing.

## Recovery implication

If selective attrition leaves surviving components with spare capacity, numerical recovery should first increase those persistent occupied components. Rebuilding previously lost breeding space becomes a separate colonisation decision rather than the automatic reverse of decline.

This reinforces the **attrition–intensification asymmetry**:

- decline: local environmental filtering + unequal losses;
- recovery: gains absorbed by survivors before spatial expansion.
