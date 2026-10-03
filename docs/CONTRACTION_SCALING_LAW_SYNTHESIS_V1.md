# Breeding-space contraction scaling synthesis v1

**Status:** bounded post-hoc exploration. This document does **not** reopen or modify the frozen Ecology Report.

## Main candidate quantitative rule

Across the five population trajectories, effective monitored breeding-component number \(E\) scales sublinearly with breeding-pair abundance \(N\):

\[
E \propto N^\kappa.
\]

All five population-specific annual log-log elasticities are positive and below one:

| Population | \(\kappa\) | level \(R^2\) |
|---|---:|---:|
| Cormorant Adélie | 0.069 | 0.586 |
| Humble Adélie | 0.203 | 0.906 |
| Litchfield Adélie | 0.465 | 0.898 |
| Signy Adélie | 0.289 | 0.344 |
| Signy chinstrap | 0.366 | 0.634 |

The population-fixed-effect common elasticity is **0.250** (within-population \(R^2=0.585\)). Leave-one-population-out common estimates remain positive and sublinear (**0.139–0.354**). The descriptive system estimates are **0.246** at Palmer and **0.339** at Signy.

The common exponent is not claimed as a universal quarter-power law. It is a compact description of these five nested population units and a hypothesis for independent testing.

### Intuitive translation

Using the descriptive common \(\kappa\approx0.25\):

- abundance at 50% of its initial level corresponds to about **84%** of initial effective breeding-component number;
- abundance at 25% corresponds to about **71%**;
- abundance at 10% corresponds to about **56%**.

Observed first crossings of the 50%-abundance threshold retain **62–92%** of initial \(E\) across all five populations (median **81%**).

This suggests **numerical decline generally precedes full spatial-compositional collapse**.

## No common collapse threshold

A second frozen stage compared a single log-linear scaling curve with a quadratic curve and hinges at 50%, 25% and 10% abundance remaining.

Equal-weight leave-one-population-out RMSE:

| Model | LOO RMSE |
|---|---:|
| single log-linear power law | **0.337** |
| hinge at 50% | 0.357 |
| hinge at 10% | 0.366 |
| hinge at 25% | 0.368 |
| quadratic | 0.390 |

The single log-linear model predicts held-out populations best. The frozen acceleration criterion therefore **fails**.

There is no evidence here for a shared 50%, 25% or 10% abundance threshold at which breeding space suddenly collapses.

At deep decline the trajectories instead diverge strongly. Among the three Palmer populations that crossed 10% of initial abundance, retained \(E\) at first crossing ranged from **17% to 76%**.

## The relationship is a long-term trajectory rule, not an annual response law

The level relationship is much stronger than year-to-year coupling:

- level common elasticity: **0.250**, within-population \(R^2=0.585\);
- first-difference common elasticity: **0.120**, within-population \(R^2=0.071\).

Annual abundance changes therefore explain little of annual \(E\) changes.

After removing linear calendar-year trends separately within each population, the pooled residual slope remains 0.303 (\(R^2=0.450\)), but this is not consistent across populations: Litchfield is strong whereas Humble and both Signy series are near zero. The robust statement is therefore **timescale separation**, not universal short-term coupling.

## Slow-state / historical-bottleneck exploration

Stage 4 compared four frozen predictors of normalized contraction:

| Predictor | Equal-weight LOO RMSE |
|---|---:|
| normalized calendar time | **0.260** |
| running minimum abundance | **0.320** |
| current abundance | 0.337 |
| trailing-3 abundance | 0.355 |

The frozen historical-bottleneck criterion is technically met because running minimum abundance predicts held-out trajectories better than both current abundance and the trailing-3 average. However, normalized calendar time performs better still.

Thus the data are more consistent with **slow structural progression during sustained decline** than with a simple instantaneous abundance-response rule. The running-minimum result is compatible with path dependence or persistence, but does not establish hysteresis or biological memory.

## Final transition-asymmetry search

The final bounded rule search asked whether breeding-space contraction reverses when abundance rebounds.

The prespecified ratchet rule **fails**, because the fitted rebound elasticity is negative rather than weakly positive:

- decline-transition slope: **\(k_{\downarrow}=0.220\)**;
- rebound-transition slope: **\(k_{\uparrow}=-0.055\)**.

The asymmetric transition model does predict held-out populations slightly better than a single symmetric transition slope (LOO RMSE **0.113** versus **0.118**), but it fails the frozen biological ratchet criterion.

The descriptive reason is notable:

- when abundance declined, \(E\) also declined in **47/75 = 63%** of transitions;
- when abundance rebounded, \(E\) increased in only **8/31 = 26%** of transitions.

Thus short-term abundance rebounds usually did **not** coincide with recovery of breeding-component diversity. This supports the interpretation of \(E\) as a relatively slow structural state, but no new post-hoc rule is opened from this observation.

## What does not explain \(\kappa\)

Four frozen candidate predictors of population-specific elasticity were evaluated with leave-one-population-out prediction.

Intercept-only LOO RMSE: **0.170**.

| Predictor | LOO RMSE | vs baseline |
|---|---:|---:|
| initial \(E\) | 0.182 | worse |
| initial evenness \(E_0/J\) | 0.184 | worse |
| decline depth | 0.265 | worse |
| component count \(J\) | 0.278 | worse |

No candidate predictor improves on the intercept-only baseline.

So the heterogeneity in contraction elasticity is **not simply explained** by initial component number, initial effective number, initial evenness or how deeply abundance eventually declined.

## Current synthesis

The strongest quantitative hypothesis from the bounded search is:

> **Breeding-space contraction is sublinear and slow: effective breeding-component structure erodes much more slowly than abundance, shows no shared collapse threshold, and responds weakly to year-to-year abundance rebounds.**

A compact candidate law for independent testing is:

\[
\frac{E_t}{E_0} \approx \left(\frac{N_t}{N_0}\right)^{0.25},
\]

with the crucial caveat that the exponent varies substantially among the five studied populations (0.069–0.465) and is not a claimed universal constant.

Ecologically, this suggests that **population abundance is a fast variable relative to breeding-space structure**. Breeding pairs can disappear rapidly while the multi-component breeding configuration persists, and short-term numerical recovery does not necessarily rebuild that configuration.

The mechanism remains unknown. Site fidelity, persistent habitat suitability, local extinction of breeding groups, recruitment, and other processes could all generate slow structural dynamics.

## Stop rule

This is the end of the bounded quantitative-rule search on these five trajectories.

No further lags, thresholds, exponent families, nonlinear transition models or predictor fishing should be opened on this dataset. The next valid step is **independent testing** of the candidate sublinear/slow-state rule in additional component-resolved colonial populations.
