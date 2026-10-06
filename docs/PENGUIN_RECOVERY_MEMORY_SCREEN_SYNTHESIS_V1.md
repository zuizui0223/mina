# Penguin recovery-memory screen — synthesis v1

**Status:** exploratory support screen on already-exposed Palmer/Signy component data. It is not part of the submission paper.

## Result

Across the five component-resolved penguin trajectories, the exact-zero screen found:

- **22** positive → zero loss spells across **21** distinct breeding components;
- **1** completed reoccupation;
- **21** losses still unreoccupied by the end of the available panel;
- **0/21** eligible losses reoccupied within 2 years;
- **0/19** within 3 years;
- **0/18** within 5 years;
- **0/17** within 10 years.

The only completed return occurred in Palmer Humble component 1.1: first zero in **1998**, first positive again in **2014**, a **16-year** zero spell.

Its frozen loss-versus-return state contrast was:

```
H = -1.8585
exp(H) = 0.1559
```

Thus the only completed return occurred at a much **lower**, not higher, surrounding-population state than at loss.

## Decision

The generated threshold prediction

> a lost breeding component requires a higher surrounding population state to return than the state at which it was lost

is **not supported** by the one completed event, and the prespecified adequacy gate fails badly (1 completed spell versus required 10).

No threshold, pseudo-absence definition, roster, lag, or pooling rescue is opened.

## What survives

A different descriptive pattern is strong enough to motivate an independent test:

> **Once a monitored penguin breeding component reaches exact zero, short- to medium-term reoccupation is rare in the available Palmer/Signy records.**

This is not yet causal hysteresis. Most loss spells occur during sustained population decline, so the source population often never returns to the state at which the component disappeared.

## Next valid test

Use an independent site-occupancy data set with repeated presence/absence observations across a spatial network and ask:

1. how often true site extinction and recolonization occur;
2. whether recolonization depends on geographic connectivity to occupied sites;
3. whether previously occupied sites differ from otherwise suitable empty sites after controlling for physical isolation;
4. whether the same connectivity state has different occupancy consequences before versus after local loss.

The East Antarctic Adélie occupancy database (Southwell et al. 2016; DOI 10.4225/15/57590498D301C) is a natural candidate, but its support structure and observation completeness must be audited before any effect is estimated.
