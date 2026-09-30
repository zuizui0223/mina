# Supporting Information — JBI integrated manuscript v0.5

**Manuscript:** *Dynamic colony history and limits of static island architecture for Antarctic penguin demographic coupling*

This Supporting Information is a provenance- and robustness-oriented companion to the anonymous main manuscript. It does not introduce a new primary endpoint or promote any sensitivity analysis above its frozen inferential role.

## Appendix S1. Analysis hierarchy, freezing status and claim boundaries

| Analysis | Primary role | Freezing / provenance status | Paper-level interpretation |
|---|---|---|---|
| Palmer breeding-component concentration | Establish spatial reorganization during decline | Frozen fixed-composition nulls before interpretation | Progressive concentration supported |
| Palmer late-season state lag profile | Test short-lived local history | V2 is a fixed-specification validation after a source-provenance repair; not fully outcome-blind confirmation | Lag-2 information supported; 4–5-year recruitment echo unsupported |
| Palmer state memory / bridge | Diagnose persistence of measured state | Frozen before memory/bridge outcomes; bridge is not causal mediation | Weak one-year state memory; past state retains incremental information |
| Palmer REPRO | Independent nest-level validation | Primary endpoint frozen before REPRO values; source-encoding repair frozen before model fit | Mean nest success does not replicate the colony-wide state signal |
| Palmer HUMPOP arrival | Test breeder-arrival process | Schema gate frozen before values; minimum-information gate fixed | STOP for insufficient information; no coefficient fitted |
| Antarctic V3 architecture test | Cross-species temporal-coupling transferability | Predictors/model/inference frozen before primary outcome test | Directionally concordant but non-confirmatory |
| Radius / metric variants | Robustness only | Sensitivity role frozen; no replacement of 2 km primary | Interaction is not scale invariant |
| Detectable-effect analysis | Interpret non-rejection | Retrospective operating characteristic | Very large common effects constrained; moderate effects unresolved |
| Ross Island resight extension | Future individual mechanism test | Behavioural rows unopened and access locked behind exact-header gate | Not part of the present evidentiary chain |

The manuscript therefore distinguishes **confirmed or fixed-specification local information**, **failed/STOP validations**, and **non-confirmatory macroecological transfer** rather than treating all analyses as equivalent evidence.

## Appendix S2. Palmer breeding-component concentration

Concentration was evaluated only for Cormorant, Humble and Litchfield islands, where the frozen colony-code roster allowed a fixed-composition null comparison. Effective colony number was

N_eff = 1 / sum_j(p_j^2),

where p_j is the fraction of breeding pairs in colony code j.

| Island | First N_eff | Last N_eff | Fractional change | Observed slope yr^-1 | CV20 null one-sided p |
|---|---:|---:|---:|---:|---:|
| Cormorant | 3.535 | 2.859 | −0.191 | −0.0310 | 0.0380 |
| Humble | 4.625 | 2.285 | −0.506 | −0.0855 | 0.000010 |
| Litchfield | 5.783 | 1.000 | −0.827 | −0.3681 | 0.000010 |

The joint plus-one probability under the severe 20% coefficient-of-variation Gamma–Poisson fixed-composition null was 0.000010. The concentration result does not identify a movement mechanism.

**Source receipt:** results/PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json.

## Appendix S3. Palmer late-season state and provenance repair

The colony-wide state was derived from the late-season chick census relative to contemporaneous colony size and standardized within island-season. The lag analysis removes shared island-transition growth, controls outcome-interval prior size and includes persistent colony identity.

| Lag | Rows | Coefficient | One-sided permutation p | Role |
|---|---:|---:|---:|---|
| 1 | 761 | 0.1004 | 0.000010 | Known-type association; mechanically coupled |
| 2 | 754 | 0.0409 | 0.00327 | Primary denominator-separated endpoint |
| 3 | 747 | 0.0511 | 0.00136 | Secondary lag |
| 4 | 738 | 0.0223 | 0.121 | Secondary lag |
| 5 | 730 | −0.0148 | 0.770 | Secondary lag |

The predeclared recruitment-echo contrast, mean(beta_4,beta_5) − mean(beta_2,beta_3), was −0.0422 (one-sided p = 0.988), opposite to the predicted delayed 4–5-year recruitment pattern.

### S3.1 Provenance boundary

The first lag contract used the observation calendar date as the chick-season key. An earlier outcome-blind season-key contract had already established the PALYYZZ study identifier as the authoritative season key because two records carried inconsistent calendar dates. The V2 repair changed only the season-key provenance rule; lags, performance metric, model, sensitivities and decision thresholds were not tuned. Observed coefficients had been exposed before V2, so the manuscript labels the result **fixed-specification validation after provenance repair**, not fully preregistered confirmation.

**Source receipt:** results/PALMER_PERFORMANCE_REDISTRIBUTION_LAGS_RESULT_V2.json.

## Appendix S4. Measured state memory and bridge diagnostic

Colony-specific reproductive state had weak short persistence:

| State-memory lag | rho | One-sided p | Supported at 0.05 |
|---|---:|---:|:---:|
| 1 year | 0.0639 | 0.0378 | Yes |
| 2 years | 0.0532 | 0.0764 | No |
| 3 years | 0.0479 | 0.1106 | No |

A separate bridge diagnostic fitted lag-2 redistribution using past state S_t, measured current state S_t+1, outcome-interval prior size and colony fixed effects. The past-state coefficient was 0.0296 (n = 695, one-sided p = 0.00154).

This bridge model is a mechanism diagnostic, **not a causal mediation model**: S_t+1 is post-t, and unmeasured environmental persistence or measurement error can leave information in S_t. Individual public-information use is not identified.

**Source receipt:** results/PALMER_PERFORMANCE_MEMORY_RESULT_V1.json.

## Appendix S5. Independent REPRO validation and metric specificity

The independent REPRO endpoint was the mean number of chicks reaching crèche per monitored nest, standardized within island-season. At least five monitored nests were required per colony-season.

| Endpoint | beta | Null 95% interval | One-sided p | Inferential role |
|---|---:|---:|---:|---|
| Mean chicks reaching crèche, lag 1 | 0.0296 | −0.0744 to 0.0705 | 0.232 | Frozen primary |
| Mean chicks reaching crèche, lag 2 | −0.0164 | −0.1360 to 0.1140 | 0.629 | Frozen secondary |
| Proportion of nests with any crèched chick | 0.0679 | — | 0.0405 | Prespecified sensitivity; cannot rescue primary |

The primary nest-level measure therefore did not replicate the colony-wide state association.

A separately labelled post-result common-panel diagnostic retained 61 Humble colony-seasons. On this exact panel, the original colony-wide state coefficient was 0.1040 whereas mean nest success was 0.0291; the two standardized states correlated only r = 0.132. Adding mean nest success to the common-panel model left the colony-wide state coefficient nearly unchanged (0.1023). These diagnostics motivate the descriptive term **late-season colony-wide state** and prohibit treating the original predictor as generic nest reproductive success.

The positive binary-any-crèche sensitivity and all common-panel permutation values remain secondary/post hoc and cannot overturn the frozen failed REPRO primary endpoint.

**Source receipts:** results/PALMER_REPRO_REDISTRIBUTION_RESULT_V1.json; results/PALMER_REPRO_SAME_PANEL_METRIC_DIAGNOSTIC_RESULT_V1.json.

## Appendix S6. HUMPOP breeder-arrival process test stopped by the information gate

Official PAL-LTER conversion code established, before arrival values were used for a scientific decision, that HUMPOP preserves repeated Date, raw Colony and adult abundance fields at Humble Island. The schema gate therefore passed prospectively.

After documented duplicate-key handling, the frozen 50% arrival-midpoint endpoint produced 106 colony-season arrival estimates, 84 raw exact matches to the performance data and 69 panel rows after requiring at least three colonies per predictor season. Eighteen predictor seasons remained, but the frozen primary gate required at least 100 matched colony-seasons.

Therefore the analysis stopped with status STOP_insufficient_information.

- Primary model fit: **No**
- Permutation test run: **No**
- Performance-arrival coefficient estimated: **No**
- Post hoc threshold or colony-code rescue allowed: **No**

This result is **untested**, not a null performance-arrival effect.

**Source receipt:** results/PALMER_HUMPOP_ARRIVAL_RESULT_V1.json.

## Appendix S7. Antarctic-wide primary inference

The Antarctic analysis used the frozen V3 model and 9,999 block-preserving permutations. The paper-level statistic was the median area × habitat-heterogeneity coefficient gamma_AH across Adélie, chinstrap and gentoo penguins.

| Species | gamma_AH | Raw p | Holm-adjusted p |
|---|---:|---:|---:|
| Adélie | −0.304 | 0.2162 | 0.2162 |
| Chinstrap | −1.184 | 0.0661 | 0.1689 |
| Gentoo | −0.318 | 0.0563 | 0.1689 |

The observed cross-species median was −0.318. Under the frozen permutation null, 946 of 9,999 permutations were at least as extreme in the preregistered negative direction, giving p = 0.0947. Null quantiles were Q05 = −0.424, median = 0.0027 and Q95 = 0.366.

No species-specific Holm-adjusted test rejected at 0.05. The result class is **directionally concordant but non-confirmatory**.

**Source receipt:** results/PAPER2_V3_PERMUTATION_INFERENCE_RESULT_V1.json.

## Appendix S8. Spatial-support and trait sensitivities

The primary 2 km Tier 2 habitat-complex richness interaction was not scale invariant.

| Variant | Cross-species median gamma_AH | Species with negative interaction |
|---|---:|---:|
| 1 km Tier 2 richness | −0.058 | 2 |
| 2 km Tier 2 richness, primary | −0.318 | 3 |
| 5 km Tier 2 richness | +0.107 | 0 |
| 2 km Tier 2 Shannon diversity | −0.163 | 2 |

No sensitivity variant received a new primary p-value or replaced the frozen 2 km richness analysis. A separate joint block-preserving radius diagnostic assigned probability 0.081 to the observed 2 km negative → 5 km positive sign switch together with an observed-size contrast. Thus the manuscript treats radius as a robustness issue, not established ecological scale dependence.

**Source receipts:** results/PAPER2_SCALE_TRAIT_SENSITIVITY_RESULT_V1.json; results/PAPER2_RADIUS_SIGN_SWITCH_NULL_RESULT_V1.json.

## Appendix S9. Detectable-effect boundary for the Antarctic primary test

The retrospective operating-characteristic analysis reused the frozen real observation layout and 9,999-permutation rejection rule.

| True common gamma_AH | Detection fraction |
|---:|---:|
| −0.30 | 0.047 |
| −0.35 | 0.117 |
| −0.40 | 0.380 |
| −0.45 | 0.597 |
| −0.50 | 0.810 |
| −0.55 | 0.927 |
| −0.60 | 0.967 |

Interpolated effect magnitudes for 80% and 90% detection were MDE80 = 0.498 and MDE90 = 0.539. The observed absolute cross-species median, 0.318, lies below both thresholds.

Accordingly, non-rejection is informative against very large common interactions but does **not** establish absence or equivalence for effects near the observed magnitude.

**Source receipt:** results/PAPER2_DETECTABLE_EFFECT_RESULT_V1.json.

## Appendix S10. Evidence ledger for manuscript claims

| Manuscript statement | Permitted status |
|---|---|
| Palmer decline included progressive within-island concentration | Supported under frozen concentration nulls |
| Late-season colony-wide state contains short-lived information about later redistribution | Supported under fixed-specification lag-2 validation; provenance caveat required |
| A 4–5-year natal recruitment echo explains the Palmer signal | Not supported |
| Measured state alone explains the full lag signal | Not established |
| Mean monitored-nest reproductive success independently replicates the signal | Not supported |
| HUMPOP shows performance-linked breeder arrival | Not tested; information gate failed |
| Individual public-information use was demonstrated | Not established |
| Static island architecture has a confirmed cross-species effect on temporal coupling | Not confirmed |
| The observed moderate Antarctic interaction is absent | Not established |
| Radius reversal demonstrates ecological scale dependence | Not established |
| Prior Antarctic geography/habitat studies are contradicted | Not claimed |
| Ross Island individual settlement confirms the mechanism | No; prospective analysis remains outside the evidentiary chain |

All Ross Island behavioural data access and model execution remain excluded from the submitted evidence until their independent exact-header and information gates are satisfied.
