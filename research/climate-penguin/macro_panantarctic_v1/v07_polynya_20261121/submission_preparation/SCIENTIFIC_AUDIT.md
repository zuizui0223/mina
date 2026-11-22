# v0.7 independent scientific audit — 21 November 2026

## Outcome and scope

The central negative association survives the bounded uncertainty diagnostic, but the stronger claim about preceding versus following winters does not survive it. The manuscript should proceed after correcting the timing claim and displaying the uncertainty-method sensitivity prominently. No new ecological dataset, radius, lag, outcome, covariate selection, or favourable subset was searched. No canonical manuscript prose was edited by this reviewer.

Reviewed actual main manuscript §§1–5, Supplement S1–S7, the numerical verifier and receipt, and source tables. All findings refer to `v07_polynya_20261121/`. The original narrative already handles the exploratory direction, optical response, incompatible prior studies, unsuccessful prediction, selected chlorophyll support and untested later years unusually carefully; these qualifications should be retained.

## 1. HIGH: eight nonzero-information regions are highly unbalanced; the timing conclusion changes under the bounded jackknife sensitivity

### Evidence

Main §2.3 and Supplement S2 remove three zero-information regions, but do not report how the remaining information is distributed. With all model covariates removed, Victoria Land contributes 55.03% of design information for the M_P slope and Wilkes Land 19.01%. For M_SP those shares are 55.10% and 17.24%. The inverse concentration indices are 2.844 and 2.879. The P0−P1 contrast has a concentration index of 4.814, with 35.62% from Victoria Land and 19.80% from Wilkes Land. These indices describe design concentration; they are **not** inferential degrees of freedom or counts of independent observations.

This is a concrete reason that changing the nominal cluster count from eleven to eight does not settle small-sample inference. See MacKinnon, Nielsen & Webb (2023), *Cluster-robust inference: A guide to empirical practice*, Journal of Econometrics 232:272–299, DOI 10.1016/j.jeconom.2022.04.001, especially the discussion of partial leverage and reporting requirements. Primary source: https://doi.org/10.1016/j.jeconom.2022.04.001 (search retrieved full excerpts; direct DOI reopening was blocked).

### Bounded diagnostic performed

Preferred CR2/Satterthwaite could not be executed because R, Rscript and clubSandwich were absent. The parent specified the fallback before the new intervals were calculated. We used the CV3 delete-one-informative-region covariance, centred at the full coefficient vector, and t(7) intervals. Every leave-out fit reconstructs and QR-absorbs colony and region-by-season fixed effects. All retained slope designs have full rank. All eight informative regions and the original fixed model definitions are preserved. Original and R1,000 responses were evaluated symmetrically.

The formula is equation (18) of MacKinnon, Nielsen & Webb (2023), *Fast and reliable jackknife and bootstrap methods for cluster-robust inference*, Journal of Applied Econometrics 38:671–694, DOI 10.1002/jae.2969. Section 3 also discusses t(G−1) intervals and partialling out cluster fixed effects. The formula, reference distribution and distinction from the leave-out-mean-centred CV3J were checked in the publisher full text: https://onlinelibrary.wiley.com/doi/full/10.1002/jae.2969.

| Response / contrast | Estimate, ‰/10pp | Archived informative-8 CR1 interval | New CV3+t(7) interval |
|---|---:|---:|---:|
| Original, M_P | −1.003109 | [−1.504738, −0.501480] | [−1.675350, −0.330869] |
| Original, M_SP | −0.921609 | [−1.384327, −0.458891] | [−1.515075, −0.328143] |
| Original, P0−P1 | −0.687693 | [−1.346100, −0.029286] | [−1.470259, +0.094872] |
| R1,000 mean, M_P | −1.023340 | [−1.537077, −0.509604] | [−1.707188, −0.339493] |
| R1,000 mean, M_SP | −0.941136 | [−1.414810, −0.467462] | [−1.541839, −0.340432] |
| R1,000 mean, P0−P1 | −0.693269 | [−1.359810, −0.026727] | [−1.476340, +0.089802] |

The original timing contrast has two-sided p = 0.076315 under this diagnostic; the calibration-ensemble contrast p = 0.074589. These are unadjusted exploratory quantities, not confirmatory tests. Both main-model intervals remain below zero. Neither covariance approach accounts for the prior analysis sequence or guarantees finite-cluster coverage.

Reproducible script: `../diagnose_region_jackknife.py`; output `../source_inputs/region_jackknife_diagnostic.json`. There are 34 checks: unchanged full-versus-informative slopes, frozen coefficients, the 16 archived original-response omission estimates, and scalar-versus-matrix contrast covariance agreement. The output contains all 48 leave-out fits, exact coefficients, native-unit full covariance matrices, per-coefficient intervals and design information shares. `--root`/`--manuscript-dir` selects the manuscript directory; when copied beside the manuscript, the default resolves relative to the script. No inference is performed by the figure renderer.

### Exact manuscript changes required

- Abstract timing sentence: “On the 358-record timing panel, the preceding-winter coefficient was more negative by 0.69‰, but the eight-region jackknife interval included zero (−1.47 to +0.09‰).”
- §3.2 heading: “The timing contrast is negative but imprecise.”
- §3.2: give both archived CR1 and new CV3 intervals and state that the evidence for a difference is sensitive to the uncertainty estimator. Keep all negative leave-out point estimates, explicitly as point-estimate stability.
- §§4.1 and 5: replace categorical “stronger” or an established seasonal distinction with “the timing point estimates suggest a preceding-winter association, but their difference remains uncertain.”
- Figures 2 and 3: display CV3 and archived informative-eight CR1 side by side; Figure 3 must visibly show both original and R1,000 timing intervals crossing zero under CV3.
- Supplement S2/Table S1: retain original nominal-eleven and informative-eight CR1 results and append the dated CV3 diagnostic. Do not overwrite the frozen result or reframe the new diagnostic as prespecified before the ecological analysis.

## 2. MEDIUM: report the same-sample salinity coefficient before interpreting a different sample

Main §3.3 and Table S2 correctly explain that +0.834‰ comes from the separate 860-row panel. However, the actual salinity coefficient from the main M_SP model is omitted even though the section assesses the relation between polynya and salinity. It is already in `reproduction_receipt.json`: +0.646206‰ per practical-salinity unit, informative-eight CR1 interval [+0.153713,+1.138700]. This should be supplied in Supplement S2, preferably with the new CV3 uncertainty from the unchanged M_SP fit; the audit JSON contains it.

Do not promote this to a new independent “second axis”. Reporting it simply completes the joint model and avoids using a broader-sample null interval in place of the coefficient actually adjusted for. Proposed main sentence: “In the same-sample joint model the salinity coefficient was positive (Table S2); this conditional association and the low residual correlation do not establish a distinct mechanism.” The separate 860-row estimate can remain clearly labelled context in the supplement. No refit or new model is needed.

## 3. MEDIUM: make the conditional estimand and remaining dependence explicit

Main §2.3 calls the summer terms controls, but they occur after the winter exposure. The draft already avoids causality; one short sentence should explain why these are conditional associations, not a total winter effect. Suggested addition: “Because the summer covariates occur after the winter exposure, this adjustment defines a conditional association and may remove parts of any winter-to-summer pathway.” This is a design implication, not proof that those variables mediate the association.

Regional covariance also assumes independent region-level errors. Shared satellite conditions, source calibration and broad environmental processes need not obey that assumption. Suggested limitation: “Neither regional clustering nor fixed effects guarantees removal of dependence shared across reporting regions or systematic error in the common optical calibration.” Do not initiate another clustering-method search solely to chase this limitation.

## Non-issues and boundaries

- The three zero-information regions are genuinely absorbed; there is no evidence that removing them changes slopes or SSE.
- The fixed-effect coefficient is a within-colony annual contrast conditional on region-season conditions; the prose does not incorrectly treat colony means as the source of identification.
- Temporal covariance is used correctly; the original draft does not commit the separate-significance-comparison error.
- The CR1 finite-sample convention omitting absorbed FE rank is explicitly disclosed. It should not be described as a code bug merely because software conventions differ.
- The study does not establish a quantity-versus-geometry effect, directly observed diet, later-period replication or independent source-pixel validation, and the draft already says so.
- Signy, feather matching and chlorophyll limitations are correctly separated by observational unit and inferential purpose.
- The source accepted-image discrepancy remains unresolved and correctly disclosed. This audit did not remove images post hoc.
- No method result in this audit repairs the failed original positive directional hypothesis or warrants a confirmatory claim.

## Primary methods sources

- https://doi.org/10.1016/j.jeconom.2022.04.001
- https://doi.org/10.1002/jae.2969 (Eq. 18; Section 3)
- https://jepusto.github.io/clubSandwich/articles/panel-data-CRVE.html (documentation; CR2 was not executed)

## Resolution in v0.7.1

All three actionable findings were integrated into the main manuscript, supplement and figure sources. CV3 intervals are prominently displayed with archived CR1 intervals retained; the timing difference is explicitly uncertain. The same439 salinity coefficient is now reported, and the conditional estimand and cross-region/common-calibration limitations are stated. This automated scientific audit does not constitute completed human author review.
