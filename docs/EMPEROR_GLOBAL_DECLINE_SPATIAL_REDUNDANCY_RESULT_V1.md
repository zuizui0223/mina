# Global emperor penguin prospective decline-allocation result v1

**Status:** prospective external result. Contract and 50-colony support roster were frozen before endpoint magnitudes were summarized.

## Frozen frame

- species: emperor penguin (*Aptenodytes forsteri*)
- endpoint years: 2009 -> 2018
- fixed paired roster: **50 colonies**
- response: posterior median colony-level seasonal abundance index
- source: public LaRue et al. model output

## Decline gate

Across the fixed 50-colony roster:

    N2009 = 239177.8
    N2018 = 209571.5
    ratio = 0.8762
    change = -12.4%.

The frozen decline gate passes.

## Primary spatial result

    E2009 = 25.312
    E2018 = 22.079
    E ratio = 0.8723
    change = -12.8%
    delta log(E) = -0.1366.

Thus the global decline is accompanied by **spatial concentration** in the posterior-median colony distribution.

This is prospective external support for the decline-concentration direction outside Palmer/Signy.

## Local arithmetic

Point-estimate colony signs:

    down = 30/50
    up = 20/50.

Gross point-estimate changes:

    gross loss = 65903.6
    gross gain = 36297.4
    gain/loss ratio = 0.551.

Therefore this is not universal attrition.

It is **predominant/mixed attrition**: losses dominate globally while 20 colonies have higher posterior medians in 2018.

The dominant colony remains Coulman Island.

Composition turnover:

    TV = 0.240.

## Strongest proportional residuals

Largest positive residuals relative to exact proportional global decline:

- Dawson: 8798
- Mertz Glacier: 6362
- Drescher: 5532
- Smyley: 4565
- Cape Colbeck: 4043

Largest negative residuals:

- Halley: -15121
- Bear Peninsula: -3347
- Auster: -3171
- Stancomb: -3046
- Shackleton Ice Shelf: -2887

Halley is the largest negative contributor to the compositional shift.

## Important zero-baseline boundary

The fixed roster includes Ledda Bay with posterior median 0 in 2009.

Therefore the contract's multiplicative quantity:

    G_i = N2018/N2009

is undefined for that colony.

No colony is removed after effect opening.

Consequently:
- primary N, E, shares, TV and additive proportional residuals use all 50 colonies;
- the full-roster G_D identity is recorded as **not defined**;
- no positive-baseline subset is promoted as a replacement primary analysis.

This is a contract implementation limitation, not a biological failure.

## Predeclared regional sensitivity

All eight ice regions with >=3 colonies are reported.

| ice region | n | N direction | E direction | N ratio | E ratio |
|---|---:|---|---|---:|---:|
| Amundsen Sea | 6 | down | down | 0.905 | 0.780 |
| Bellingshausen Sea | 7 | up | down | 1.141 | 0.715 |
| Weddell Sea | 7 | down | up | 0.776 | 1.215 |
| Dronning Maud Land | 5 | up | up | 1.162 | 1.006 |
| West Indian Ocean | 9 | down | down | 0.652 | 0.805 |
| East Indian Ocean | 4 | down | down | 0.443 | 0.901 |
| Australia | 4 | down | down | 0.682 | 0.765 |
| Victoria Oates Land | 8 | up | down | 1.023 | 0.971 |

Crucially, the regional results include **all four sign combinations**:

- N down / E down;
- N down / E up;
- N up / E down;
- N up / E up.

Thus even within one species and one globally fitted data product, aggregate direction does not determine spatial-allocation direction at regional scale.

## Relation to Palmer/Signy

Palmer/Signy decline concentration was unusually pure: all 39 frozen components had lower endpoint counts.

The emperor result reproduces the global **N down / E down** direction but not the universal-local-loss mechanism.

This distinction is valuable:

> decline-associated concentration can arise under predominantly unequal losses without requiring every local colony to decline.

## Relation to Bird Island Gentoo

Bird temporal data show all four annual N/E sign combinations.

The emperor regional sensitivity independently reproduces all four combinations spatially across regions.

These two prospective/allowed analyses strongly support the general descriptive proposition:

> **the sign of aggregate breeding-abundance change and the sign of spatial-redundancy change are not locked together.**

## Claim boundary

- Abundance is a posterior median index, not direct occupied-nest counts.
- Local up/down labels are point-estimate signs, not posterior probabilities.
- No cross-colony posterior covariance is manufactured.
- No sea-ice mechanism is inferred from E.
- Global E decline does not imply every colony or every region concentrated.
