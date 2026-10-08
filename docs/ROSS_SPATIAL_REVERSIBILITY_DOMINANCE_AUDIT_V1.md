# Ross spatial reversibility dominance audit v1

**Status:** post-result reviewer-defense calibration. No new ecological endpoint or hypothesis is introduced.

## Question

The focal loss/rebound cosine is:

    0.99695.

Because Cape Crozier West is the largest component of both the shock loss and rebound, could the apparent high spatial reversibility be only a consequence of that single dominant component?

## Normalized allocation overlap

Normalize the six-component shock-loss and rebound vectors to sum to one.

Their total-variation distance is:

    TV = 0.09405.

For two probability vectors:

    overlap = sum_i min(p_i, q_i)
            = 1 - TV.

Therefore normalized loss and rebound allocations overlap by:

    0.90595
    = 90.6%.

This is the same allocation discrepancy expressed by the frozen half-L1 mismatch:

    9.41% mismatch
    <=> 90.59% overlap.

## Remove the dominant Crozier West component

As a deliberately post-result reviewer diagnostic, remove Cape Crozier West from both vectors and renormalize the remaining five components.

For the remaining components:

    overlap = 83.22%
    TV      = 16.78%
    cosine  = 0.9656.

Thus broad loss/rebound alignment remains high after the dominant component is removed, although it is weaker than in the full six-component network.

## Interpretation

Safe:

> High Ross reversibility is strengthened by the dominant Crozier West component but is not solely an artifact of that one component; the other five components still show substantial normalized overlap.

Do not use this analysis to claim:
- a new confirmatory result;
- statistical significance of reversibility;
- independence from component-size structure.

This is a reviewer-defense calibration only.

## Manuscript role

Do not add another main-text result unless requested by review.

The main text can continue to report:

    cosine = 0.997
    inverse-path mismatch = 9.41%.

If a reviewer argues that cosine is trivially driven by Crozier West, report the five-component diagnostic in the response or supplement.
