# Ecology Report pre-submission reviewer stress test v1

## Purpose

This audit asks whether the current manuscript's central inference survives the most likely conceptual objections without adding new endpoints or rescue analyses.

## Objection 1 — “This is just the abundance–occupancy relationship”

**Risk:** High if the paper is framed as “fewer birds, fewer colonies.”

**Response:** The null explicitly includes abundance-dependent loss of low-count components. Observed annual totals define the latent annual-total trajectory; relative component shares are fixed; counts are then simulated under the frozen Poisson/Gamma–Poisson error family. Rejection therefore concerns directional redistribution beyond the contraction expected from lower abundance plus observation error.

**Status:** Addressed in Abstract, Introduction, Discussion and cover letter.

## Objection 2 — “N_eff is mathematically coupled to abundance”

**Risk:** Central.

**Response:** The fixed-composition simulations preserve the empirical decline as the latent annual-total trajectory, so any finite-count dependence of N_eff on total abundance is represented in the null. The observed slopes are compared against that abundance-dependent null rather than against zero.

**Boundary:** The observation-error family is stylized, not empirically calibrated; the manuscript says so.

**Status:** Addressed.

## Objection 3 — “N_eff is just number of occupied colonies”

**Risk:** Conceptual confusion.

**Response:** N_eff is inverse-Simpson effective component number, a Hill-number concentration metric. It can decline while all monitored components remain positive because it responds to relative shares. It is not occupied-site richness.

**Status:** Explicitly added to Methods.

## Objection 4 — “Breeding-space contraction implies measured physical area”

**Risk:** Especially at Palmer, where colony-code polygons are not versioned publicly.

**Response:** The manuscript defines breeding-space contraction operationally as loss of effective representation across monitored breeding components. Palmer codes are treated as monitored census units, not fixed GIS polygons. Torgersen GIS is independent physical triangulation only.

**Status:** Addressed.

## Objection 5 — “Palmer colony codes may have changed operational meaning”

**Risk:** Real but bounded.

**Response:** Official metadata define island-specific colony identifiers and historical mapping supports biological colony meaning, but a complete versioned polygon crosswalk is unavailable. Palmer is therefore discovery only; dominant-code trajectories are supplementary; the prospectively frozen Signy tests carry confirmatory weight.

**Status:** Addressed; provider inquiry drafted.

## Objection 6 — “The Signy Adélie result depends on A1/A60 pooling”

**Risk:** Moderate.

**Response:** Canonicalization was frozen before effect inspection. A later strict literal-roster robustness analysis independently supports concentration over 1998–2009. The earlier 22-season prospective test remains primary.

**Status:** Addressed.

## Objection 7 — “These are five pseudoreplicates, not five independent systems”

**Risk:** High if wording says five independent populations.

**Response:** The manuscript claims five population units across **two Antarctic systems and two species**, not five independent systems. Three Palmer units share regional environment; two Signy species share one island. These dependencies are stated explicitly.

**Status:** Addressed.

## Objection 8 — “No mechanism is identified”

**Risk:** Editorial rather than inferential.

**Response:** The paper is framed as a replicated ecological phenomenon. A separate Palmer redistribution mechanism failed frozen Signy replication and is explicitly not used. The Report's contribution is the state-space distinction between abundance loss and internal spatial composition, not a universal mechanism.

**Status:** Addressed.

## Objection 9 — “The result is driven by significance rather than biological magnitude”

**Risk:** Low.

**Response:** Main Figure 2 reports first-to-last N_eff declines (19–83%) alongside the severe CV20 null probabilities. Signy effects are −37% and −51%, not merely small significant slopes.

**Status:** Addressed.

## Objection 10 — “The null says totals are exactly fixed, but the code lets simulated totals vary”

**Risk:** Methodological wording error.

**Response:** Corrected before submission. Observed annual totals define the **latent expected annual totals**. Simulated component counts vary under Poisson/Gamma–Poisson error, conditioned on nonzero total where the observed census is positive. The manuscript no longer says simulated annual totals are exactly fixed.

**Status:** Addressed.

## Objection 11 — “Pooled shares are estimated using the whole time series”

**Risk:** Interpretive.

**Response:** The null requires one time-invariant composition. Cumulative shares provide the frozen fixed-composition estimate used consistently across the panel. The test does not choose a baseline year or tune shares to maximize the trend. No alternate share estimator is opened after outcome inspection.

**Boundary:** The paper does not claim that pooled shares are a mechanistic baseline or ancestral composition.

**Status:** Adequately bounded.

## Objection 12 — “Effective number of breeders is established genetic terminology”

**Risk:** Terminology.

**Response:** The manuscript uses “effective breeding-component number” and explicitly states that it is not genetic Ne or Nb. No abbreviation Nb is used for the spatial endpoint.

**Status:** Addressed.

## Editorial assessment after stress test

The strongest defensible novelty statement is:

> **Decline in total abundance and directional change in relative spatial composition are separable population-state changes; the latter recurred beyond a fixed-composition count-error null in prospectively frozen geographic and cross-species replications.**

The strongest surprise is:

> **The observed decline trajectory itself was insufficient to reproduce the degree of spatial concentration.**

The strongest general principle is:

> **Abundance decline constrains but does not determine the spatial trajectory of a structured population.**

No additional ecological analysis is required for these claims before initial submission.
