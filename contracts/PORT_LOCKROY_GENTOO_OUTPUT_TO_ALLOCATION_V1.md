# Port Lockroy Gentoo ratio-free reproductive-output -> next-year allocation test v1

**Status:** pre-effect mechanism contract. Frozen from public BAS metadata before any sub-colony breeding-pair or chick-count magnitude is summarized for this question.

## Independent system

British Antarctic Survey / UK Polar Data Centre:

**Population numbers and breeding success of Gentoo penguins (*Pygoscelis papua*) at Port Lockroy, Goudier Island, 1996–2020**

DOI:

    10.5285/92e92c14-0ff2-4ce2-8305-83d5b3a4071d

Public metadata states that:

- breeding pairs are counted at defined sub-colonies;
- chicks are counted after hatching and again in crèches prior to fledging;
- the breeding population count is made one week after 95% of marked nests contain eggs;
- island-wide timing is established from a common chronology protocol;
- six sub-colonies are in visitor-exposed areas and four are controls.

This system is independent of Bird Island and the Ross Sea analyses.

## Why this route exists

The frozen Bird Island success-to-allocation test produced a strong positive association, but its primary predictor:

    chicks_t / nests_t

shares the current nest count with the share-change response and some operational ratios exceed a literal per-pair biological maximum.

This Port Lockroy test is designed **before outcome opening** to avoid that ratio/shared-denominator problem.

## Fixed biological question

Does local chick production contain information about the next breeding season's spatial allocation **beyond current local breeding abundance**?

Prediction:

> a sub-colony producing more late-stage chicks than expected for its current breeding abundance should have a larger breeding share in the following season, after controlling its current share.

## Fixed roster rule

Use every provider-defined sub-colony that:

1. has an identifiable stable sub-colony label;
2. has a breeding-pair field and a late/crèche chick-count field under the provider schema;
3. can be followed across seasons without outcome-dependent merging or splitting.

The support audit will record the exact provider-defined labels.

No sub-colony may be added, removed, merged or selected based on count magnitude, tourism category, trend or effect direction.

Require at least:

    6 fixed sub-colonies.

Otherwise SUPPORT FAIL.

Tourist/control status is metadata only and is **not** a primary predictor.

## Outcome-blind support audit

After this contract is committed, inspect only:

- file/sheet names;
- field names;
- sub-colony labels;
- season/year encoding;
- which rows contain structurally populated breeding-pair, hatch-chick and crèche-chick fields;
- duplicate sub-colony-season rows;
- explicit zero versus missing-value representation;
- visitor/control metadata if encoded.

Do **not** summarize:

- breeding-pair magnitudes;
- chick magnitudes;
- chick-per-pair ratios;
- local shares;
- correlations;
- regression coefficients.

## Primary chick endpoint

Use the provider's **late / crèche chick count prior to fledging**.

If the file does not distinguish late/crèche chicks from earlier hatch counts, SUPPORT FAIL for this mechanism route.

Do not switch to hatch chicks after seeing the effect.

## Transition eligibility

A start season t is eligible only if:

1. all fixed roster units have one usable breeding-pair count in t;
2. all fixed roster units have one usable late/crèche chick count in t;
3. all fixed roster units have one usable breeding-pair count in the immediately following season t+1;
4. all breeding-pair counts used to form shares are >0;
5. no gap is bridged.

Require at least:

    12 eligible start seasons.

Otherwise SUPPORT FAIL.

Eligibility is determined from structure/missingness only.

## Step 1 — ratio-free reproductive-output residual

For each eligible unit i and start season t define:

    C_it = late/crèche chick count
    B_it = breeding-pair count.

Use:

    X_it = log(1 + C_it)
    A_it = log(B_it).

Fit the frozen two-way fixed-effect model:

    X_it = a_i + d_t + gamma * A_it + Q_it

where:

- a_i = sub-colony fixed effects;
- d_t = start-season fixed effects;
- Q_it = residual reproductive output.

Q is the focal **ratio-free size-adjusted chick-output residual**.

This stage removes the dominant scaling of chick output with current breeder abundance without constructing chicks/B.

No alternative transform is primary.

## Step 2 — next-year spatial allocation

For each eligible transition define:

    p_it = B_it / sum_j B_jt
    p_i,t+1 = B_i,t+1 / sum_j B_j,t+1.

Response:

    Y_it = log(p_i,t+1).

Current-state covariate:

    L_it = log(p_it).

Fit:

    Y_it
      = alpha_i
      + tau_t
      + rho * L_it
      + beta * Q_it
      + error_it.

Primary prediction:

    beta > 0.

Interpretation:

higher-than-expected chick output at current breeding abundance predicts greater next-season breeding share, conditional on current share.

The response contains only next-year share; current breeding abundance enters as an explicit covariate rather than being shared in a predictor denominator.

## Frozen permutation inference

Use:

    B = 9999
    seed = 20261006.

Permutation object:

    the complete fixed-roster Q_t vector for each eligible start season.

For each permutation:

1. permute start-season labels of the complete Q vectors;
2. keep unit identities within each vector;
3. keep Y, current-share L, unit labels and response years unchanged;
4. refit the identical Step-2 model;
5. record beta_perm.

This preserves:
- the spatial covariance of reproductive-output residuals within a season;
- the empirical Q distribution;
- persistent unit identities in the response;
- the complete breeding-share trajectory.

It breaks only temporal alignment between reproductive-output state and next-season allocation.

Directional p:

    p = (1 + count(beta_perm >= beta_obs)) / 10000.

Primary support requires:

    beta_obs > 0
    and
    p <= 0.05.

Null or negative is terminal for this route.

## Required reporting

Report:

- exact fixed roster;
- eligible start seasons;
- number of unit-season rows;
- gamma from Step 1;
- beta and rho from Step 2;
- 9999-permutation p;
- permutation q05/median/q95;
- standardized beta for Q;
- leave-one-unit-out beta for every fixed unit.

No unfavorable unit may be removed.

## Prespecified negative controls / diagnostics

These are secondary and do not replace the primary result.

### A — previous-share change

Test whether Q_t predicts:

    log(p_it / p_i,t-1)

where structurally available.

A strong symmetric backward association would weaken a simple forward causal interpretation.

### B — hatch-chick endpoint

If an earlier post-hatch chick field is structurally available, repeat the same residual-output construction as a **secondary timing sensitivity**.

Do not select hatch versus crèche based on which is favorable.

### C — tourist/control interaction

Only if visitor/control category is encoded for every fixed unit, report a secondary interaction:

    beta_Q_by_exposure.

This is descriptive/mechanism sensitivity only.

## Interpretation boundary

A positive primary result supports:

> size-adjusted late chick output carries prospective information about next-season spatial breeding allocation in a second Gentoo system.

It is consistent with:
- persistent local habitat quality;
- breeding propensity/return decisions;
- density-dependent compensation;
- movement.

It does not establish:
- individual movement;
- causal win-stay/lose-switch behavior;
- juvenile recruitment at a one-year lag;
- a universal penguin mechanism.

A null result means the Bird Island mechanism signal does not prospectively transfer under a denominator-safer design.

## Relation to PR189

This is an optional mechanism extension.

The paper-level state/allocation result remains valid regardless of outcome:

    aggregate breeding change does not uniquely determine spatial allocation.

If Port Lockroy passes, it provides independent prospective support that local reproductive output predicts the contrast mode.

If it fails, retain Bird's signal as system-specific/ambiguous and do not search Port Lockroy for alternate lags, subsets or success metrics.
