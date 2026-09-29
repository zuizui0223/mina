# Paper 2 Gate 2E-C v2 — Hierarchical Integrated Recovery Plan

**Goal:** Replace the failed two-stage Gate 2E-C v1 estimator with a one-stage/coordinate-descent linear-Gaussian state-space estimator while preserving all frozen simulation truths and recovery thresholds.

## Frozen facts

- V1 failure receipt: `results/PAPER2_INTEGRATED_RECOVERY_RESULT_V1.json`.
- Real counts remain locked.
- Same 1980–2025 schedules, 2 km predictors, forcing scales, scenarios, nuisance truths, 100 replicates, and recovery gates.
- No threshold relaxation.

## Model

For annual latent state `x_it`:

```
z_ij ~ Normal(x_it + method_j, v_j)
x_i,t+1 - x_it ~ Normal(mu_i + lambda_i F_g,t, tau^2)
lambda_i ~ Normal(1 + Xc_i gamma, sigma_lambda^2)
```

where `Xc` contains A, H and A×H centered within the frozen forcing group.

## Coordinate updates

1. Calibrate shared observation nuisance from all synthetic count records.
2. Collapse same-season records only to an observation `z_hat` **plus its observation variance**.
3. Smooth each site's annual latent state by weighted least squares using observation rows and process-transition rows.
4. Update annual forcing from smoothed increments; center within group and adjust site drift to preserve fitted increments.
5. Update each site's drift/loading by weighted ridge regression toward the trait-predicted loading.
6. Normalize loadings to mean 1 within group and rescale forcing.
7. Update gamma from group-centered trait structure.
8. Update residual loading SD.
9. Profile process SD on a fixed grid using observed-interval likelihood:
   `Var(delta_obs) = duration*tau^2 + v_start + v_end`.
10. Repeat exactly 12 iterations.

## TDD

- Dense near-noiseless count data recover forcing and gamma_AH.
- Null data remain centered.
- Simple buffering recovers gamma_A without inventing gamma_AH.
- Group loading means stay 1.
- Process SD is not initialized at the synthetic truth.
- Zero counts remain finite through log1p.
- V2 evaluation uses the exact V1 pass/fail thresholds.

## Execution

- Primary scales: ADPE=CCAMLR, CHPE=APBP region, GEPE=species-wide.
- Mandatory species-wide sensitivity.
- 100 replicates × null/crossover/simple-buffering.
- Record a new V2 receipt; never overwrite the V1 failure receipt.
