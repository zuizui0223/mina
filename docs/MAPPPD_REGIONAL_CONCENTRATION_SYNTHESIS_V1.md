# MAPPPD regional breeding-site concentration synthesis v2

**Status:** reinterpretation of the already-frozen regional result. No new regional outcome test is opened.

## Question

What does the frozen MAPPPD regional result actually add to the replicated within-system concentration result?

The parent unit is **species × APBP region** and the components are fixed monitored site_id values. These are geographic monitoring networks, not assumed closed demographic populations.

## Frozen implementation

The regional analysis remains exactly as executed.

For each eligible network:

\[
E=1/\sum_j p_j^2
\]

and

\[
\log E_t = \alpha + \kappa_{obs}\log N_t.
\]

The fixed-composition null preserves the observed total trajectory while drawing site counts from time-invariant pooled shares. A second null adds the frozen observation-error structure. The focal calibrated effect is \(\Delta\kappa=\kappa_{obs}-\mathrm{median}(\kappa_{null})\).

No result below changes that contract.

## Structural support

Thirteen species × region groups were present in the frozen cohort. Seven passed the fixed-roster support gate, spanning all three Pygoscelis species and three APBP regions.

Four networks declined and three increased.

## Declining networks

| Species | Region | Sites | Seasons | raw kappa | calibrated delta kappa | p | Robust panel support |
|---|---|---:|---:|---:|---:|---:|---|
| Adélie | Central-west Antarctic Peninsula | 3 | 5 | 0.080 | +0.073 | 0.108 | no |
| Adélie | South Shetland Islands | 4 | 7 | 0.088 | +0.115 | 0.0148 | yes |
| Chinstrap | Central-west Antarctic Peninsula | 3 | 10 | 0.022 | +0.017 | 0.432 | no |
| Chinstrap | South Shetland Islands | 6 | 8 | 0.445 | +0.434 | 0.0152 | yes |

All four declining networks have positive null-calibrated abundance–concentration effects. The median calibrated effect is +0.094. The 4/4 sign count is descriptive only because panels within regions are not independent.

This supports a recurring **abundance-linked concentration direction among the declining regional subset**.

## Increasing networks are not merely context

| Species | Region | Sites | Seasons | first total | last total | first E | last E | raw kappa | calibrated delta kappa |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Adélie | Victoria Land | 11 | 5 | 387,917 | 516,140 | 4.85 | 3.56 | -0.358 | -0.355 |
| Gentoo | Central-west Antarctic Peninsula | 7 | 5 | 19,084 | 23,253 | 4.93 | 4.13 | -0.238 | -0.228 |
| Gentoo | South Shetland Islands | 5 | 7 | 11,910 | 19,544 | 3.90 | 3.86 | +0.024 | +0.020 |

All three increasing networks end with lower E.

In two panels, abundance rises while E falls substantially, so the abundance–space elasticity is negative. That is the opposite kappa direction from the declining panels even though the temporal endpoint is still greater concentration.

This matters because it separates:

1. **abundance-linked concentration** — positive kappa within a declining trajectory;
2. **temporal concentration** — E falling through time, which can occur even when abundance rises.

The frozen regional contract formally tests the first quantity, not the second.

## Revised interpretation

The MAPPPD result should no longer be summarized as simple cross-scale confirmation that decline causes concentration.

The stronger evidence hierarchy is:

### Confirmed within breeding systems

Five declining Palmer/Signy trajectories show concentration beyond proportional thinning/count error.

### Regional declining subset

All four declining networks have the same positive calibrated abundance–concentration direction; two South Shetland panels are individually supported.

### Regional trend boundary

All three increasing networks also end with lower E, and two do so despite substantial abundance growth.

Therefore:

> **regional concentration is not uniquely associated with decline in the eligible MAPPPD panels.**

This is a scope boundary, not a new confirmatory law.

## Relation to the slow-state / ratchet exploration

The prior bounded local exploration found that E recovered during only 8/31 abundance rebounds, but the prespecified ratchet criterion failed because rebound kappa was negative.

The increasing regional networks are descriptively compatible with weak reversibility or slow spatial recovery, but no regional ratchet or decline-versus-increase test was frozen before these outcomes were known.

Do not claim hysteresis.

The correct future hypothesis is:

> **Is breeding-space concentration directionally persistent across population growth and decline, such that numerical increase fails to reverse earlier spatial concentration?**

That question now requires a genuinely independent data source or a prospectively frozen macroecological test.

## Boundary

The seven regional panels contain only 3–11 sites and 5–10 complete seasons. Panels within the same APBP region are not independent.

No formal time-slope test, trend-asymmetry statistic, hysteresis test or decline-versus-increase comparison was preregistered for the MAPPPD panels.

The increasing panels therefore constrain interpretation but do not establish a trend-independent regional law.

## Strongest defensible synthesis

> **Non-proportional concentration during decline is strongly replicated within Antarctic Pygoscelis breeding systems. At the broader regional scale, the abundance-linked decline direction recurs within declining networks, but effective breeding-site number also decreases in all three increasing networks. Breeding-space organization is therefore not a simple transform of population trend, and decline-specific causation should not be inferred from the regional extension.**

## Stop rule

No new time-trend statistic, alternate region definition, radius, lag, threshold, or mechanism search is opened on these same seven panels.
