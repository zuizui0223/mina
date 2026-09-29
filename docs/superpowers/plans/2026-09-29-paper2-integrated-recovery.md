# Paper 2 Gate 2E-C Integrated Recovery Implementation Plan

**Goal:** Before opening real demographic count magnitudes, verify that the frozen Paper 2 estimator can recover shared forcing, site loadings, the A x H crossover, and the frozen observation nuisance structure from synthetic integer counts generated on the real record layout.

**Primary zero-safe observation scale:** `z = log1p(count)`.

**Why:** MAPPPD census values are abundance estimates with multiplicative accuracy categories rather than simple independent Poisson samples. `log1p` preserves the approximately multiplicative/lognormal interpretation at ordinary colony sizes while remaining finite for zero counts. This choice is frozen before inspecting any real count magnitude.

## Frozen primary forcing scales

- ADPE: CCAMLR.
- CHPE: APBP region.
- GEPE: species-wide.

If an ADPE or CHPE regional integrated recovery fails, the only allowed pre-outcome fallback is species-wide, which already passed Gate 2E-A.

## Synthetic process

For site i, group g and season t:

```
x[i,t+1] = x[i,t] + mu[i] + lambda[i] F[g,t] + e[i,t]
```

with Gate 2E-A values:

- forcing SD 0.08;
- loading residual SD 0.15;
- process SD 0.04;
- site drift mean -0.01;
- site drift SD 0.01.

Primary crossover scenario:

```
lambda = 1 - 0.35 * A*H + loading residual
```

Additional scenarios:

- null: gamma_A = gamma_H = gamma_AH = 0;
- simple buffering control: gamma_A = -0.25, gamma_H = gamma_AH = 0.

Mean loading is normalized to 1 within forcing group.

## Synthetic observation layer

For every real metadata record j:

```
z*[j] = x[i,t] + delta_image I(image) + error[j]
count[j] = max(0, round(exp(z*[j]) - 1))
z[j] = log1p(count[j])
```

Frozen truths:

- delta_image = log(1.15);
- sigma accuracy 1 = log(1.05);
- sigma pooled accuracy 2-5 = log(1.25);
- unknown vantage receives no image offset.

Observation calibration uses the Gate 2E-B estimator on the synthetic `z` values.

## Integrated fitting

1. Estimate shared image offset and the two accuracy scales from repeated same-season observations.
2. Method-correct each `z`.
3. Collapse repeated records within site x species x season by inverse estimated-variance weighting.
4. Convert adjacent observed seasons to interval changes.
5. Fit unknown forcing and site loadings with the frozen 8-iteration alternating least-squares estimator.
6. Regress normalized loadings on forcing-group structure + A + H + A:H.
7. Score recovery against synthetic truth only after fitting.

No true forcing, true loading, true state or true observation parameter is supplied to the estimator.

## Primary recovery gate

For each retained species scale:

- every forcing group median forcing correlation >= 0.70;
- every forcing group 5th-percentile forcing correlation >= 0.30;
- crossover median gamma_AH bias <= 0.10;
- crossover negative fraction >= 0.90;
- null absolute median gamma_AH <= 0.05 and 5th-95th interval contains zero;
- simple-buffering median gamma_A bias <= 0.10 and >=90% negative;
- simple-buffering absolute median gamma_AH <= 0.06;
- image-offset absolute median bias <= 0.03;
- accuracy-1 median relative sigma bias <= 0.15;
- accuracy-2-5 median relative sigma bias <= 0.30;
- finite estimate fraction = 1.

Use 100 deterministic-seed replicates per species, candidate scale and scenario.

## Secondary variance lane

Recovery of local process-variance effects is **not a blocker for the primary response-filter hypothesis**. A separate synthetic variance-identifiability diagnostic will determine whether the manuscript may distinguish genuine buffering from decoupling-with-local-instability. If that diagnostic fails, Result C is removed/demoted without changing the primary A x H test.

## Fail-closed rules

- No real count magnitude is opened.
- Do not change log1p, thresholds, simulation truths, 2 km predictors, temporal window, forcing geography, or interactions after synthetic results.
- Do not add a new forcing partition if integrated recovery fails.
- Do not use a species-specific image offset in the primary model.
- Do not rescue failure by dropping difficult seasons or sites beyond the already-frozen predictor/forcing eligibility rules.

## Tasks

1. TDD zero-safe count transform and weighted same-season collapse.
2. TDD integrated synthetic generator using real metadata layout.
3. TDD integrated fitting on dense synthetic fixtures.
4. Connect pinned Gate 2C, Gate 2E-A/B artifacts and pinned MAPPPD metadata.
5. Run 100-replicate null, crossover and simple-buffering scenarios.
6. Freeze result receipt.
7. Only if the primary integrated gate passes, define the real-outcome execution contract.
