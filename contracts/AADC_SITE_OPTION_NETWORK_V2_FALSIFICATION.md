# V2 falsification: survey-map density versus biological spatial options

**Status:** Post-result exploratory diagnostic, 2026-10-26. V1 positive spatial held-out density associations (Adélie +0.0107029 Brier, flying seabirds +0.0461476 Brier) are already known. The purpose is to challenge, NOT optimize or confirm those results. Do not relabel the V2 tests as blinded or permit a favorable variant to replace the V1 effect.

## Alternative explanations
1. 2025 publisher's expanded potential-site inventory reflects where new surveys/map definitions were added rather than longstanding potential breeding-space opportunities.
2. Source expert validation fields may encode retrospectively judged breeding presence or effort, making a nominal prediction model partly conditional on labels.
3. Strong density associations are merely background differences among original mapping regions/classes, rather than informative site-level variation.

## Locked falsification tests
- **R0 replay:** with exact V1 raw original AADC cohort, reproduce frozen 250-km-block holdout B0/B1 Brier values to <=1e-6 in both programmes. Stop on any mismatch rather than tuning thresholds.
- **R1 lean controls:** repeat on the identical V1 cohort with the same B0/B1, but remove three original expert-validation variables that could be informed by recorded occurrences. The primary 10-km radius remains the only evaluated ecological network addition here. Compare Brier and within-block direction; do not select the stronger of V1 and lean for a manuscript.
- **R2 fixed historical reference network:** restrict the analysis to the *same original geographic-site IDs included in both original 2021 (4,884) and 2025 (7,785) reference editions* (4,862 common). On precisely this biological cohort, compare B0 with (a) 2025 candidate 10-km neighbor count and (b) 2021-only candidate 10-km neighbor count computed from *all original 4,884 original 2021 locations*, including 22 IDs no longer in 2025. This isolates map-edition sensitivity while keeping folds, biological respondents, controls and site-history weights identical. Sources and 250-km blocks remain unchanged. Confirm historical network counts use original 2021 coordinates without inferred biological absences. No retuned radii.
- **R3 within-region site-level shuffle placebo:** for original full-sample V1 cohort, shuffle the one 2025 10-km density feature *as a source-site-constant value* within frozen 250-km geographic block × original source class (island/continent) × 2021 frame membership. Freeze 31 repeats, seed 20261026. Both original biological P/A and source programme remain fixed. Report the proportion of sites whose density feature actually changed (effective testability), and original Brier improvement percentile relative to the exploratory shuffled distribution; no inferential p-value or permutation-adjusted scientific significance claim. If <25% of distinct sites change in a programme, declare shuffle underpowered and do not interpret. Shuffle is a negative-control diagnostic, not a causal experiment.

A result that only survives one source reference edition or vanishes in the local site-shuffle falsification cannot support a biological option-network explanation. Even successful falsification screens cannot exclude original survey effort, mapping bias, nonlinear spatial confounding, true occupied sites affecting site definition, or historical/physical nesting capacity change. Confirmatory evidence requires independent prospective breeding surveys and versioned historical potential habitat, not an AADC refit.

## Never do
- Never call 2021-only site categories an independent physical island classification;
- Never treat NR as absence or 2025-only site IDs as new colony colonization;
- Never fit a favorable 2- or 50-km radius to rescue the 10-km result;
- Never modify the frozen Ecology PR189, V14 biological conclusion or original V1 outcome receipt.
