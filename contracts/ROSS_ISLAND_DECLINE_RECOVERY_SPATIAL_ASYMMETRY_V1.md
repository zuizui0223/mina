# Ross Island Adélie decline–recovery spatial asymmetry v1

**Status:** effect contract frozen after schema/support audit and before inspection of breeding-pair magnitudes in the 2026 Ross Sea aerial census workbook.

## Independent system

Public Ross Sea Adélie aerial census, DOI `10.7931/kf06-x745`.

Primary fixed physical breeding components on Ross Island:
1. Cape Royds
2. Cape Bird South
3. Cape Bird Middle
4. Cape Bird North
5. Cape Crozier West
6. Cape Crozier East

These six rows have 37 common complete census years in the 1981–2024 workbook.

## Phase definition — frozen from external literature + support only

Published Ross Sea work defines the southern metapopulation as declining through approximately 1981–2000 and increasing during 2001–2012.

Because all six Ross Island components are not jointly observed before 1985 and year 2000 is incomplete for the six-row roster, freeze:

### Decline phase
```
1985–1999
```
All 15 years are structurally complete for the six components.

### Recovery phase
```
2001–2012
```
Use only structurally complete years. The support audit shows 2008 is incomplete, so the frozen retained years are:
```
2001, 2002, 2003, 2004, 2005, 2006, 2007, 2009, 2010, 2011, 2012
```

No year may be added/dropped after counts are opened.

## Metrics

For each retained year:

```
N_t = sum_i n_it
p_it = n_it / N_t
E_t = 1 / sum_i p_it^2
```

For each phase:

```
log(E_t) = alpha + kappa * log(N_t)
```

Also report first-to-last:
- N change;
- E change;
- share of each component;
- absolute component gains/losses;
- gross gain / gross loss decomposition.

## Eligibility gates

The biological phase test is interpretable only if:
- decline phase total abundance has negative temporal log slope;
- recovery phase total abundance has positive temporal log slope.

If either direction fails on the Ross Island six-component network, stop the corresponding interpretation. Do not change periods.

## Frozen predictions

### P1 — decline concentration
During the decline phase:
```
kappa_decline > 0
```
and end-of-phase E should be below start-of-phase E.

### P2 — weak spatial reversal during numerical recovery
During the recovery phase, numerical recovery should **not** simply reverse the decline path.

Primary directional criterion:
```
kappa_recovery < kappa_decline
```

Stronger generated pattern, if observed:
```
kappa_recovery <= 0
```
meaning abundance grows while effective breeding-component number fails to recover or declines.

### P3 — process asymmetry
Mass balance should differ between phases:
- decline concentration should be dominated by differential losses;
- recovery change should contain substantial absolute gains in persistent components.

Report continuous gross-gain/gross-loss ratios; no threshold is used to force classification.

## Fixed-composition context

For each phase, simulate a descriptive fixed-composition null that conditions on the observed annual total N trajectory and uses the phase-pooled component shares.

Report:
- observed kappa;
- median null kappa;
- observed-minus-null kappa;
- Monte Carlo tail probability in the direction of the frozen prediction.

Use 20,000 simulations and seed 20261006.

This null asks whether the abundance–space coupling exceeds that expected from proportional allocation across the fixed six-component roster. It is not a census-error model.

## Decision hierarchy

Strong independent support for decline–recovery spatial asymmetry requires:
1. both abundance-direction eligibility gates pass;
2. kappa_decline > 0;
3. kappa_recovery < kappa_decline;
4. the recovery-phase endpoint does not show a simple proportional restoration of E.

A negative recovery kappa is especially informative but is not required to rescue a failed criterion 3.

## Boundaries

- Ross Island six components are fixed physical census components, not identical in scale to Palmer LTER colony_code.
- The fixed-composition null is a proportional-allocation reference, not an empirically calibrated aerial-count error model.
- This analysis cannot identify individual movement.
- No colonisation claim is made; all six primary components are established components at phase start.
- Beaufort and newly discovered colonies are excluded from the primary test because their observation histories are sparser and colonisation vs discovery requires a separate search-effort design.
- Paper 1 is unaffected regardless of outcome.
