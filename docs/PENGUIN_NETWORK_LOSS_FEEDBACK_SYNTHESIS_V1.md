# Penguin breeding-network loss-feedback screen — synthesis v1

**Status:** exploratory analysis on already-exposed Palmer/Signy component histories. Not part of the frozen Ecology submission.

## Question

Does loss of other breeding components make a still-occupied component more likely to disappear in the next year, after controlling for its own current size?

## Result

Across all five component-resolved trajectories:

- **632** eligible calendar-consecutive occupied component-year transitions;
- **22** exact-zero loss events.

The base ridge-logistic model used focal local size plus relative time.

Adding the fraction of other components still occupied produced a negative coefficient in the generated direction, but it was very small:

```
z(network integrity) = -0.073
```

and leave-one-population-out log loss worsened:

```
M0          = 0.10908
Mintegrity  = 0.11169
Mboth       = 0.11385
```

So the prespecified descriptive criterion failed.

Palmer-only gives the same conclusion:

```
M0 log loss         = 0.12768
Mintegrity           = 0.13157
network coefficient  = -0.0059
```

By contrast, focal local component size has a large negative standardized coefficient:

```
all five:   -1.99
Palmer:     -2.40
```

Small local components are much more likely to hit exact zero in the next year than large ones.

## Interpretation

The simple cascade hypothesis

> one breeding-component loss reduces whole-network integrity and thereby makes another component disappear

is **not supported** by this aggregate screen.

That matters because it removes an attractive but currently unsupported mechanism from the story.

The result points instead toward a more local extinction-order process:

> **which patch disappears next is primarily associated with the state of that patch itself, while coarse whole-network loss adds little predictive information.**

This fits the independent Torgersen pattern, where extinction timing is structured by subcolony size and snow-related topography.

## Important residual possibility

This screen uses only the **number of other occupied census components**, not a physical adjacency graph.

A true local rescue/social effect could still operate through:
- immediately neighbouring subcolonies;
- movement corridors;
- shared landing access;
- local snow geometry;
- local social density.

Such a mechanism would require mapped component polygons or individual movement data. It should not be inferred from the present network-integrity null.

## Consequence for the emerging mechanism

The current evidence now disfavors two simple stories:

1. **global social cascade:** whole-network erosion directly accelerates the next local extinction — not supported here;
2. **universal rich-get-richer:** initial colony share predicts later share gain — not supported in increasing MAPPPD networks.

The remaining stronger hypothesis is **capacity-mediated local sorting**:

- local size and habitat state determine when a breeding component becomes marginal;
- after losses, surviving sites contain spare capacity;
- recovery can therefore be absorbed within survivors;
- expansion to new/reoccupied sites becomes worthwhile only when local capacity again becomes limiting.

This is more consistent with published East Antarctic Adélie density dependence and the Beaufort Island habitat-expansion / reduced-emigration result than a simple whole-network social cascade.
