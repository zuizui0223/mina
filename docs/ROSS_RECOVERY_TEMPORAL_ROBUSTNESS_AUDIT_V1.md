# Ross recovery temporal robustness audit v1

**Status:** post-result robustness audit. This does not alter the frozen V2 decision; it limits the interpretation of the observed E decline.

## Frozen result

Recovery years were fixed before count magnitudes were opened:

    2001, 2002, 2003, 2004, 2005, 2006, 2007, 2009, 2010, 2011, 2012.

Frozen V2 predicted numerical recovery with increasing E3.

Observed:

    N: 94,798 -> 351,119
    E3: 1.7286 -> 1.5428
    E6: 2.2919 -> 1.9702.

Therefore the frozen deconcentration prediction fails directionally.

## Temporal pattern

The E decline is **not a steady trend**.

Three-colony E:

| year | E3 |
|---|---:|
| 2001 | 1.7286 |
| 2002 | 1.5074 |
| 2003 | 1.4757 |
| 2004 | 1.4130 |
| 2005 | 1.5756 |
| 2006 | 1.4914 |
| 2007 | 1.5113 |
| 2009 | 1.4714 |
| 2010 | 1.4845 |
| 2011 | 1.4382 |
| 2012 | 1.5428 |

Six-component E shows the same broad structure.

## Descriptive temporal regression

Frozen-period OLS descriptions:

    log(E3) ~ year:
    slope = -0.00549 per year
    p = 0.246

    log(E6) ~ year:
    slope = -0.00589 per year
    p = 0.358

No significance threshold was frozen for V2 and these p-values are post-result descriptive diagnostics.

They show that the evidence does **not** support wording such as:

> E steadily or progressively eroded throughout recovery.

## Baseline sensitivity

Starting in 2002 instead of the frozen 2001 baseline:

    E3 2002 -> 2012:
    1.5074 -> 1.5428
    +2.35%

    log(E3) temporal slope from 2002:
    +0.00022 per year
    p = 0.948.

For E6:

    1.8190 -> 1.9702
    +8.31%

    log(E6) temporal slope from 2002:
    +0.00198 per year
    p = 0.663.

This alternative baseline is **not** substituted for the frozen test. It is reported only to show that the endpoint E decline is sensitive to the high-E 2001 starting year.

## Early recovery pulse

The largest redistribution occurs from 2001 to 2002.

### Total abundance

    94,798 -> 203,996
    +115%.

### Three-colony E

    1.7286 -> 1.5074
    -12.8%.

### Six-component E

    2.2919 -> 1.8190
    -20.6%.

All three biological colonies increased.

All six census components increased.

Cape Crozier share increased:

    70.8% -> 79.0%.

Thus the strongest supported temporal description is:

> **early numerical recovery was disproportionately allocated to Crozier, producing a rapid concentration pulse; the more concentrated composition then persisted with substantial year-to-year fluctuation.**

## Early-versus-late composition

Mean E3:

    2001-2004 = 1.5312
    2009-2012 = 1.4842
    difference = -3.1%.

Median E3:

    2001-2004 = 1.4916
    2009-2012 = 1.4779
    difference = -0.9%.

This reinforces that the dramatic 10.7% endpoint contrast should not be interpreted as a smooth phase-long decline.

## Consequence for claims

Supported:

- V2 recovery-deconcentration prediction failed.
- 2001->2012 endpoint composition is more concentrated.
- the largest change is an early recovery concentration pulse.
- concentration occurred while every frozen component increased.
- Crozier received disproportionate recovery growth.

Not supported:

- a statistically clear monotonic decline in E across the recovery phase;
- continuous erosion of redundancy from 2001 through 2012;
- a claim that each additional increase in N caused further concentration.

## Manuscript wording

Prefer:

> Numerical recovery did not restore spatial redundancy. An early recovery pulse was disproportionately concentrated at Cape Crozier, after which the lower-redundancy composition persisted.

Avoid:

> Spatial redundancy steadily declined during recovery.

## Relation to Heard

The Heard Island example independently shows why a phase-long monotonic interpretation is unsafe: total abundance increased continuously while E moved both upward and downward as dominance changed identity.

Together, Ross and Heard support a path-dependent view of spatial recovery rather than a monotonic recovery-concentration law.
