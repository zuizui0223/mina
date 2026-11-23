# Ross inverse-path mismatch effect size v1

**Status:** post-result effect-size calibration of the 1999 -> 2001 shock and 2001 -> 2002 rebound.

## Why this metric is needed

Saying:

> the aggregate returned but the spatial distribution did not

is correct but can sound larger than the actual mismatch.

The loss and rebound vectors should therefore be compared directly.

For each of the six frozen breeding components define:

    L_i = n_i,1999 - n_i,2001

and:

    R_i = n_i,2002 - n_i,2001.

All L_i and R_i are positive.

## The rebound is strongly aligned with the shock loss

Shock-loss vector:

    Royds         2,253
    Bird South    4,515
    Bird Middle   1,499
    Bird North   15,019
    Crozier West 80,216
    Crozier East  9,111.

Rebound-gain vector:

    Royds           872
    Bird South      487
    Bird Middle     523
    Bird North   13,351
    Crozier West 88,054
    Crozier East  5,911.

Cosine similarity:

    cos(L,R) = 0.99695.

Thus the rebound points in almost the same six-dimensional direction as the shock loss.

Do **not** describe this as wholesale spatial relocation.

## Exact inverse-path reference

The observed rebound total is slightly smaller than the shock loss:

    total loss = 112,613
    total rebound = 109,198.

So the fair inverse-path null scales the loss vector to the observed rebound total:

    R_i* = 109,198 * L_i / 112,613.

Expected rebound under exact proportional reversal:

| component | expected inverse-path rebound |
|---|---:|
| Royds | 2,184.7 |
| Bird South | 4,378.1 |
| Bird Middle | 1,453.5 |
| Bird North | 14,563.5 |
| Crozier West | 77,783.4 |
| Crozier East | 8,834.7 |

Observed minus expected:

| component | residual |
|---|---:|
| Royds | -1,312.7 |
| Bird South | -3,891.1 |
| Bird Middle | -930.5 |
| Bird North | -1,212.5 |
| Crozier West | **+10,270.6** |
| Crozier East | -2,923.7 |

Cape Crozier West is the **only** component with positive excess rebound relative to the exact inverse path.

## Reallocation effect size

For two vectors with the same total, the minimum amount that must be moved among components to transform one allocation into the other is:

    M = 0.5 * sum_i |R_i - R_i*|.

Here:

    M = 10,270.6 breeding pairs.

As a fraction of the observed rebound:

    M / 109,198 = 0.09405.

So:

> **9.41% of the immediate rebound would need to be reallocated among breeding components to reproduce an exact spatial inverse of the shock.**

Equivalently, roughly one tenth of the rebound is compositionally misplaced relative to exact reversal.

## How to reconcile 9.41% with cosine 0.997

These metrics answer different questions.

Cosine asks:

> do loss and rebound point in the same broad direction?

Answer:

    yes, almost perfectly.

Half-L1 mismatch asks:

> how much of the rebound allocation would need to move among components to match exact reversal?

Answer:

    9.41%.

Therefore the calibrated ecological statement is:

> **The rebound largely retraced the disturbance spatially, but a moderate ~9% allocation shift toward Cape Crozier West was sufficient to leave the breeding network more concentrated despite near-complete aggregate restoration.**

This wording is preferable to:
- "the spatial distribution failed completely to recover";
- "breeders moved wholesale to Crozier";
- "recovery occurred in entirely different places."

## Biological meaning

The metric does not identify individual movement.

The positive Crozier West excess can reflect any combination of:

- breeding participation;
- abandonment/return;
- survival;
- recruitment;
- immigration/emigration.

Published iceberg/access studies provide the ecological context for why component-specific response differed.

## Manuscript role

This should replace raw E change as the **main effect-size statement** for the Ross natural experiment.

Use both:

    aggregate restoration = 96.97%
    inverse-path allocation mismatch = 9.41%.

Together they say:

> almost all total breeding abundance returned, and most of it returned in broadly the expected places, but about one tenth was redistributed relative to exact reversal.

That is a calibrated and defensible result.
