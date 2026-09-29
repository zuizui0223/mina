# Paper 2 Empirical Coupling Diagnostic Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Test whether the frozen breeding-site traits predict empirical coupling to shared regional demographic variation before building the final state-space model.

**Architecture:** Use the 103-unit Gate 2C coupling cohort and fixed forcing groups. Harmonize observed nest counts with the already-frozen direct/image observation structure, remove each unit's secular linear trend, estimate a leave-one-out regional residual forcing from contemporaneous peer colonies, estimate site-specific coupling coefficients, then test frozen site traits and the predeclared area × heterogeneity crossover separately by species.

**Tech Stack:** Python 3.12, pandas, numpy, scipy/statsmodels, pyreadr, unittest, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-29-paper2-environmental-coupling-design.md`

## Global Constraints

- Source counts remain pinned to mapppdr commit `88c73a507e0921b2541c218c71eaf16721bc6502`.
- Primary window remains breeding seasons 1980–2025.
- Coupling cohort and forcing geography come only from `PAPER2_FORCING_SUPPORT_AUDIT_RESULT_V1.json`: 103 candidate units before coupling-estimation support.
- Site predictors remain exactly A = z(log1p ice-free area), H = z(Tier 2 richness), R = z(log1p relief), standardized within each species' complete-case diagnostic dataset.
- The only co-primary interaction is A × H.
- No alternative spatial radius, climate variable, quadratic term, year subset, or geographic partition may be selected after counts are opened.
- This is an empirical diagnostic, not the final one-stage demographic model.

## Diagnostic estimator

1. Map vantage to the frozen direct/image/unknown families.
2. Within each species, estimate the image log-count offset as the median across mixed site × species × season groups of:
   `median(log1p(image counts)) - median(log1p(direct counts))`.
3. Subtract that offset from image-based log counts; direct and unknown counts receive no mean adjustment.
4. Aggregate multiple observations within site × species × season by the median adjusted log count.
5. Within each unit, fit `adjusted_log_count ~ 1 + centered_season`; retain the linear slope as the secondary mean-trend diagnostic and use residuals for coupling.
6. For each focal unit-season, compute a leave-one-out regional forcing as the median residual among other units in the frozen forcing group observed in that same season. Require at least 3 peer units.
7. For each unit with at least 6 matched seasons, z-standardize its leave-one-out forcing across matched seasons and estimate `residual ~ 1 + forcing_z`. The slope is empirical `lambda`.
8. Join the frozen site traits. Do not impute missing breeding-option traits.
9. Species-specific primary regression: `lambda ~ A + H + R + A:H + forcing_group`.
10. Primary crossover statistic: `beta_AH`; also report `d lambda/dH` at A = -1 SD and +1 SD.
11. Test `beta_AH < 0` with 5,000 deterministic permutations of lambda within forcing group (seed 20260929). HC3 OLS estimates are reported descriptively.
12. Secondary baseline: regress the unit secular trend slope on the same trait matrix to distinguish response filtering from ordinary mean-trend association.

## Review Focus

- Leave-one-out forcing must never include the focal unit.
- A unit with fewer than 6 matched residual seasons cannot receive a coupling estimate.
- The image offset is estimated before trait joins and separately by species.
- Permutations must stay within forcing group and species.
- Missing A/H traits remain missing; no radius widening or imputation is allowed.

### Task 1: Freeze derived site traits and diagnostic contract
- Add the exact 122-site breeding-options and terrain tables from the already-validated workflow artifacts.
- Add `contracts/PAPER2_COUPLING_DIAGNOSTIC_V1.json`.

### Task 2: TDD the diagnostic estimators
- Synthetic tests for image-offset recovery, leave-one-out exclusion, minimum support, known lambda recovery, and interaction-regression design.

### Task 3: Run pinned MAPPPD outcome diagnostic
- Clone pinned mapppdr.
- Run tests, then diagnostic.
- Upload site-level lambda table and JSON result.

### Task 4: Freeze receipt and interpret
- Freeze workflow provenance.
- Report species-specific beta_AH, low/high-area H marginal effects, permutation p, sample sizes, and the corresponding mean-trend regression.
- Do not promote a final ecological claim unless the diagnostic is directionally coherent and not obviously driven by one forcing group.
