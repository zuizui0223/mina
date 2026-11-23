# Signy Chinstrap ratio-free reproductive-output -> next-year allocation v1

**Status:** pre-predictor mechanism contract. Frozen from BAS metadata before opening colony-level chick-output magnitudes for this question.

## Independent biological system

British Antarctic Survey / UK Polar Data Centre:

**Population size and breeding success of chinstrap penguins on Signy Island from 1978 to 2020**

DOI:

    10.5285/d0633a9b-8c56-4ae5-88bf-6ec6ba9017b9

Public metadata states:

- eleven Chinstrap colonies were surveyed annually;
- counts include occupied/incubating nests;
- chick counts were followed by fledgling/crèche counts;
- from 1996/97 onward monitoring follows standard CCAMLR CEMP methods;
- late chicks are counted when chicks have entered crèches prior to fledging.

This is a different species and breeding network from Bird Island Gentoo.

## Evidence-status boundary

The Signy breeding-count trajectory may overlap earlier population-trend work in this research program.

Therefore this route is **prospective with respect to the unopened local reproductive-output predictor**, not a fully outcome-blind discovery of the nest-count response.

Its role is independent mechanism triangulation.

## Standardized period

Use only CEMP-standard seasons from:

    1996/97 onward.

No pre-1996/97 observations enter the primary mechanism test.

## Fixed spatial roster

Support audit will identify the provider-defined colony labels in the standardized period.

Primary roster:

> every stable provider-defined Chinstrap colony label that can be followed without outcome-dependent merging/splitting.

Require:

    >= 6 fixed colonies.

No colony may be selected or dropped based on:
- abundance magnitude;
- trend direction;
- chick output;
- effect direction.

## Outcome-blind support audit

After this contract is committed, inspect only:

- file and column names;
- colony labels;
- season encoding;
- duplicate colony-season structure;
- structural presence/missingness of breeding-pair fields;
- structural presence/missingness of late/crèche chick fields;
- explicit zero versus missing representation.

Do **not** summarize:

- breeding-pair magnitudes;
- chick magnitudes;
- productivity ratios;
- share changes;
- coefficients;
- correlations.

## Breeding-abundance field

Use this frozen schema hierarchy:

1. provider-explicit total breeding-pair / total occupied+incubating nest field, if present;
2. otherwise, if the provider supplies separate mutually exclusive total nests with eggs and total nests without eggs fields, define:

       B_it = nests_with_eggs + nests_without_eggs.

If neither construction is structurally unambiguous, SUPPORT FAIL.

Do not choose between alternative count definitions based on effect direction.

## Reproductive-output field

Use only the provider's **late crèche / chicks expected to fledge** count.

Call it:

    C_it.

Do not substitute:
- hatch-stage chick count;
- egg count;
- chick mass;
- earlier chick count

after support inspection.

If a colony-level late endpoint is unavailable, SUPPORT FAIL.

## Transition eligibility

A start season t is eligible only if, for every fixed-roster colony:

1. B_it is structurally present and >0;
2. C_it is structurally present;
3. B_i,t+1 is structurally present and >0;
4. t+1 is the immediately following breeding season;
5. no gap is bridged.

Eligibility is determined only by structural support and zero status before chick magnitudes are summarized.

Require:

    >= 12 eligible start seasons.

Otherwise SUPPORT FAIL.

## Step 1 — ratio-free size-adjusted reproductive output

Define:

    X_it = log(1 + C_it)
    A_it = log(B_it).

Fit:

    X_it
      = a_i
      + d_t
      + gamma A_it
      + Q_it.

where:
- a_i = colony fixed effects;
- d_t = start-season fixed effects;
- Q_it = residual reproductive output.

Q is the focal predictor.

No chicks/B ratio is primary.

## Step 2 — next-season spatial allocation

For each eligible transition:

    p_it = B_it / sum_j B_jt
    p_i,t+1 = B_i,t+1 / sum_j B_j,t+1.

Response:

    Y_it = log(p_i,t+1).

Current-state covariate:

    L_it = log(p_it).

Primary model:

    Y_it
      = alpha_i
      + tau_t
      + rho L_it
      + beta Q_it
      + error_it.

Primary directional prediction:

    beta > 0.

Biological interpretation if supported:

> higher-than-expected late chick output at current breeding abundance predicts greater next-season breeding share, conditional on current share.

## Frozen permutation inference

Use:

    B = 9999
    seed = 20261006.

Permutation object:

    the complete fixed-roster Q_t vector for each eligible start season.

For each permutation:

1. permute start-season labels of complete Q vectors;
2. keep colony identities within each vector fixed;
3. keep Y, L, colony labels and response years unchanged;
4. refit the identical Step-2 model;
5. record beta_perm.

Directional p:

    p = (1 + count(beta_perm >= beta_obs)) / 10000.

Primary support requires:

    beta_obs > 0
    and
    p <= 0.05.

A null/negative result is terminal.

## Required reporting

Report:

- fixed colony roster;
- eligible start seasons;
- rows;
- gamma;
- beta;
- rho;
- standardized beta;
- permutation p and q05/median/q95;
- leave-one-colony-out beta for every colony.

No unfavorable colony may be removed.

## Prespecified diagnostics

### Backward control

Where structurally available, test whether Q_t predicts:

    log(p_it / p_i,t-1)

with analogous current-state adjustment.

A strong symmetric backward association weakens a simple forward mechanism interpretation.

### Predictor semantic audit

Report whether any raw field/value semantics make C_it non-comparable among colonies/years.

Do not redefine C after seeing beta.

## Interpretation boundary

A positive result supports:

> size-adjusted late reproductive output carries prospective information about next-season spatial allocation in Signy Chinstrap penguins.

It does not establish:
- individual movement;
- juvenile recruitment at one-year lag;
- causal win-stay/lose-switch behavior;
- a universal penguin mechanism.

A null result means the Bird post-result ratio-free signal does not transfer cleanly to this second-species network.

## Relation to PR189

The Ross/Bird/Emperor state-allocation paper remains valid regardless of outcome.

This route addresses the unresolved next question:

> **what predicts the contrast mode?**

If support fails, no earlier chick endpoint or alternate colony subset is substituted.
