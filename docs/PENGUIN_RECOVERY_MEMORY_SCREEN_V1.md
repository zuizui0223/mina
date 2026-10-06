# Penguin recovery-memory screen v1

**Status:** exploratory support screen only. This does not modify or delay the submission paper.

## Question

After a monitored penguin breeding component becomes empty, does it reappear only when the surrounding breeding population is larger than when that component was lost?

This is the first numerical screen of the generated hypothesis that breeding-site loss can make later spatial recovery harder.

## Frozen endpoint

For a focal breeding component j, identify a completed exact-zero spell:

```
positive -> zero ... zero -> positive
```

Only calendar-consecutive observations are allowed through the complete spell. Missing-year gaps censor the spell.

Let

```
N_-j,t = total breeding pairs in the same monitored population excluding component j.
```

For the loss edge,

```
A_loss = mean[ log(1 + N_-j,last-positive), log(1 + N_-j,first-zero) ].
```

For the return edge,

```
A_return = mean[ log(1 + N_-j,last-zero), log(1 + N_-j,first-return) ].
```

Define

```
H = A_return - A_loss.
```

- H > 0: the component returned only at a higher surrounding population state than the state at loss.
- H = 0: approximately reversible on this state scale.
- H < 0: return occurred at a lower surrounding state.

## Data

Use only the already frozen component panels:
- Palmer Adelie: Cormorant, Humble, Litchfield stable-roster census panels.
- Signy Adelie: A1+A60, A2, A3, A4, A64 on the frozen complete-season panel.
- Signy chinstrap: C15, C16, C17, C18, C46, C47, C79, C80, C81 on the frozen complete-season panel.

Exact zeros are treated as observed absence only where the published count is numeric zero. Missing values are never converted to zero.

## Outputs

Report, without inferential p-values:
1. number of loss spells;
2. number completed by reoccupation;
3. number right-censored without return;
4. number censored by a calendar gap;
5. number of distinct components and populations contributing completed spells;
6. event-level H values;
7. median H and fraction H > 0;
8. exp(median H), interpreted only as the ratio of the geometric surrounding-state scale (1 + N_-j) at return versus loss.

## Adequacy gate

This already-exposed data family is considered sufficient for a *future formal design* only if it contains:
- at least 10 completed spells,
- at least 5 distinct components with completed spells,
- completed spells from at least 3 population trajectories.

Failure of this gate stops inference from these data. No alternate zero threshold, pseudo-absence threshold, pooling rule, lag, or roster may rescue it.

## Interpretation boundary

This screen cannot identify individual movement, conspecific attraction, social information, or causal hysteresis. A positive H pattern would only motivate an independent prospective same-site recovery test. Permanent losses are informative descriptively but are not assigned artificial H values.
