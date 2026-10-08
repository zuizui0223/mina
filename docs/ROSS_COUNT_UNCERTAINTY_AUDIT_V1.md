# Ross count-uncertainty audit v1

**Status:** post-result measurement-boundary audit for the 1999–2002 inverse-path effect size.

## Question

Is the calibrated 9.41% inverse-path allocation mismatch demonstrably larger than uncertainty in the aerial census counts?

The current public evidence does **not** permit a formal uncertainty interval for that mismatch.

## What is known about the Ross census

Lyver et al. (2014) report that Ross Island colonies were photographed annually:

- by helicopter;
- at approximately 2,000–2,500 ft above ground;
- as close as possible to 1 December;
- within a 25 November–8 December window.

At that stage the photographed colony was represented mainly by one member of each breeding pair occupying/incubating at a nesting territory, with few non-breeders.

Before 2006:

- film negatives were developed;
- photographs were mosaicked manually;
- occupied territories were marked/dotted and counted manually.

Therefore the 1999, 2001 and 2002 anchor years all use the same broad pre-2006 film/manual workflow.

There is no obvious camera/count-system discontinuity at 2001–2002.

## What is not reported

The source paper does **not** provide, for the 1999/2001/2002 component counts:

- repeated-observer count variance;
- a component-specific standard error;
- confidence intervals around the raw aerial count;
- a year-specific detection probability;
- a full sampling model for manual count error.

The paper explicitly notes that the historical manual method was difficult to verify later.

It also notes that survey timing within the roughly two-week window may explain a small part of annual variation through breeding phenology.

Therefore no statistically defensible CI can currently be attached to:

    9.41% inverse-path allocation mismatch.

## Calibrated effect size

The six-component shock/rebound decomposition gives:

    shock loss = 112,613
    rebound gain = 109,198
    aggregate loss restored = 96.97%.

Loss/gain vector cosine:

    0.99695.

Against the exact inverse-path allocation scaled to the observed rebound total:

    half-L1 reallocation = 10,270.6 pairs
    = 9.41% of rebound.

Observed-minus-inverse-path residuals:

- Royds: -1,312.7
- Bird South: -3,891.1
- Bird Middle: -930.5
- Bird North: -1,212.5
- Crozier West: +10,270.6
- Crozier East: -2,923.7.

The positive excess is entirely at Crozier West.

## Why the pattern is not merely a uniformly tiny discrepancy

Although the network-level mismatch is about 9% of rebound, component residuals are uneven.

Relative to observed 2002 counts, approximate absolute residual magnitudes are:

- Royds: 58.6%
- Bird South: 51.0%
- Bird Middle: 39.5%
- Bird North: 4.0%
- Crozier West: 7.0%
- Crozier East: 21.1%.

Thus several smaller components differ from inverse-path expectation by far more than a few percent.

However, these ratios are **not** measurement-error tests. A residual relative to an ecological counterfactual is not the same thing as count uncertainty.

## External precision context — not transferable as a CI

Other Adélie aerial/ground studies using modern standardized methods often classify counts within roughly ±10% precision or report small mean aerial-ground differences.

Those estimates cannot simply be imposed on the Ross historical series because:

- methods differ;
- the Ross manual film counts do not report equivalent repeated-count precision;
- phenological availability error is separate from image-counting error.

Therefore no borrowed ±10% error model is used.

## Consequence for claims

Safe:

> The observed count vector differs from exact inverse-path rebound by 9.41% of the rebound total.

Safe:

> The 1999, 2001 and 2002 anchors were collected under the same broad aerial-photo/manual-count regime.

Safe:

> The mismatch is structured, with the balancing positive excess at Crozier West.

Not safe:

> The 9.41% mismatch is statistically greater than census error.

Not safe:

> Count uncertainty is negligible.

Not safe:

> The mismatch represents movement of 10,271 individual breeders.

## Manuscript wording

Use:

> The immediate rebound was strongly aligned with the preceding loss (cosine = 0.997), but 9.4% of rebound abundance would have to be reallocated among breeding components to reproduce an exact inverse path. The historical aerial series does not provide component-specific count uncertainty sufficient to attach a confidence interval to this mismatch.

This is the appropriate measurement boundary.

## What would close the uncertainty question

A formal uncertainty analysis would require one of:

1. archived replicate/manual recounts of the 1999, 2001 and 2002 photographs;
2. observer-specific count records;
3. a validated detection/counting-error model for those exact historical images;
4. re-digitization and independent recounting of the archived imagery.

Absent one of these, treat 9.41% as a calibrated descriptive effect size.
