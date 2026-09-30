# Integrated Palmer–Antarctic Supplement spine v0.2

## Purpose

The Supplement preserves the analyses needed to audit the integrated manuscript
without allowing secondary or exploratory results to compete with the two core
claims:

1. Palmer decline is accompanied by within-island concentration beyond
   proportional thinning plus prespecified count error.
2. Static breeding-island architecture does not yield a confirmed transferable
   Antarctic-wide response rule.

No Supplement result may rescue a null main-text result.

## Supplementary Methods S1 — Data provenance and frozen sources

Document:

- Palmer LTER census DOI and checksum;
- MAPPPD/APBP pinned commit;
- Antarctic Ecosystem Inventory source and checksum;
- all derived predictor receipts;
- frozen temporal windows and site × species eligibility rules.

Include a machine-readable table mapping every manuscript number to its receipt.

## Supplementary Methods S2 — Palmer concentration nulls

Expand the fixed-composition null construction:

- cumulative colony-code composition;
- annual island-total preservation;
- Poisson, Gamma–Poisson CV10 and CV20 observation error;
- 100,000 simulations;
- island-specific and joint one-sided probabilities.

Include the full annual N_eff trajectories and raw slopes.

## Supplementary Results S3 — Palmer secondary demographic diagnostics

These analyses are retained for context but are not primary evidence.

### S3.1 Effective-colony-number / next-year growth association

Report the conditional association after lagged growth terms and all mechanical
coupling / circular-shift / year-block permutation checks.

Boundary:

- association may be reported;
- weak held-out predictive increment may be reported;
- do not call N_eff a validated predictor of future growth.

### S3.2 Hierarchical beta variability

Report within-island versus among-island variability and the count-error null.

Boundary:

- the observed hierarchy is descriptive context;
- severe count-error sensitivity reproduces the contrast;
- do not promote this to a separate ecological discovery.

### S3.3 Sea-ice and weather diagnostics

Retain the frozen weather/sea-ice analyses only as contextual diagnostics.

Boundary:

- they do not identify the latent Antarctic-wide forcing;
- they do not provide a causal mechanism for Palmer concentration;
- they are not used to rescue either main hypothesis.

### S3.4 Performance-linked redistribution, memory and independent Signy transfer test

Report the repaired fixed-specification Palmer lag profile:

- lag 1: beta = 0.1004, mechanically coupled and descriptive only;
- lag 2: beta = **0.0409**, one-sided p = **0.00327**;
- lag 3: beta = **0.0511**, p = **0.00136**;
- lag 4: beta = 0.0223, p = 0.121;
- lag 5: beta = -0.0148, p = 0.770.

Explicitly state that the Palmer lag-2/3 result is **fixed-specification
validation, not fully preregistered confirmation**, because the chick-season
provenance rule was repaired after the lag coefficients had been exposed.

Report performance-memory diagnostics:

- lag-1 performance-state rho = **0.0639**, p = **0.0258**;
- lag-2 rho = **0.0532**, p = **0.0485**;
- lag-3 rho = 0.0479, p = 0.0586;
- bridge coefficient for past performance after current measured performance,
  current group size and persistent colony identity = **0.0296**,
  p = **0.00726**.

Report the prospectively frozen P1–P3 mechanism follow-up:

- P1 poor-performance breeder share versus later island-total growth:
  beta = **+0.0275** with the frozen meaningful-negative-effect decision
  compatible with redistribution/replacement;
- direct poor-loss/good-gain compensation accounting has median compensation
  ratio 0 and does not show one-for-one transfer;
- P2 island-level reproductive performance versus later island-total growth:
  beta = **+0.0578**, but the meaningful-effect decision is inconclusive;
- P3 lose-switch asymmetry:
  delta = **−0.0126**, one-sided p = **0.579**, unsupported.

Then report the independently frozen Signy replication:

- official BAS/NERC source DOI:
  `10.5285/daf2c4fd-c1e3-4e65-851f-d11f02c5b69d`;
- frozen 1996/97–2019/20 standard-method window;
- primary lag-2 beta = **0.0213**, p = **0.279**, not replicated;
- atomic-label sensitivity beta = **0.0634**, p = **0.0603**;
- comment-flag-exclusion sensitivity beta = **0.0727**, p = **0.0207**;
- secondary Signy lose-switch delta = **0.0678**, p = **0.301**,
  unsupported.

Boundary:

- do not call Palmer win-stay/lose-switch;
- do not claim observed individual movement;
- do not call Signy a positive independent replication;
- the significant comment-filter sensitivity cannot replace the null frozen
  Signy primary result;
- the combined interpretation is local dynamic information with limited
  demonstrated transferability, not a general Antarctic mechanism.

## Supplementary Methods S4 — Paper 2 outcome-blind gate history

Provide a compact audit trail showing why the final V3 estimator was chosen.

Sequence:

1. observation-overlap audit;
2. direct/image offset identifiability;
3. accuracy 1 versus 2–5 precision grouping;
4. breeding-option missingness repair;
5. forcing-support gate;
6. predictor identifiability gate;
7. latent-factor schedule recovery;
8. observation-layer recovery;
9. integrated V1 failure;
10. hierarchical V2 recovery;
11. spatially adjusted V3 recovery;
12. cross-species V4 generality recovery;
13. H-main V5 recovery;
14. paper-level source robustness;
15. real-outcome unlock.

For every failed estimator, report the frozen failure receipt rather than
silently dropping it.

## Supplementary Results S5 — Observation model robustness

Report:

- same-season shared image/direct offset;
- exact-date 23-pair sensitivity;
- <=14-day 53-pair sensitivity;
- pooled accuracy-group SDs;
- exclude-unknown and raw-ground support/recovery audits.

Boundary:

- timing sensitivities are descriptive robustness checks;
- they never replace the primary same-season calibration.

## Supplementary Results S6 — Paper 2 secondary and interpretation diagnostics

### S6.1 A-only breeding-space hypothesis

Report the three gamma_A estimates, raw one-sided permutation p-values and Holm
adjustment.

Boundary: non-confirmatory; cannot rescue A×H.

### S6.2 Shannon sensitivity

Report 2 km Tier-2 Shannon fit.

Boundary: sensitivity-only; richness remains primary.

### S6.3 Radius sensitivity and joint multi-radius null

Report the 1/2/5 km point estimates and all frozen null probabilities:

- sign switch alone;
- observed-size contrast;
- joint sign switch + contrast;
- total range;
- ordered 2 < 1 < 5 plus range.

Boundary: joint p = 0.0810; no biological scale-dependence claim.

### S6.4 Retrospective detectable-effect analysis

Report the full -0.20 to -0.60 common-effect grid, Wilson intervals, isotonic
interpolation, MDE80 and MDE90.

Boundary:

- retrospective operating characteristic only;
- not equivalence;
- not an upper confidence bound;
- moderate effects near the observed magnitude remain unresolved.

## Supplementary Results S7 — Palmer reproductive-denominator semantics audit

This section exists to prevent a false mechanism claim.

Report:

- independent November adult-pair denominator versus legacy chick-table
  denominator mismatch;
- common-frame count-space association;
- island-specific and leave-one-island-out heterogeneity;
- strongest overdispersion sensitivity;
- ratio-regression denominator dependence;
- pre-extinction chick-success diagnostic.

Claim boundary:

> pooled chick allocation increases with colony size in count space, but the
> effect is strongly island-dependent and does not establish a Palmer-wide
> reproductive or Allee-like mechanism.

Explicitly state:

- small-first zero-hitting is mechanically expected under proportional
  allocation;
- pre-extinction reproductive decline is non-confirmatory;
- do not claim that concentration occurs because larger groups universally
  rear more chicks per pair.

## Exploratory analyses not incorporated into v0.2

The following open analysis remains outside the manuscript and Supplement until
separately reviewed:

- post-outcome size-ordered colony-code extinction hazard (#102).

The Palmer performance-linked lag analysis, performance-memory audit,
prospectively frozen P1–P3 follow-up and Signy independent replication are now
retained in S3.4 with their provenance and null-result boundaries explicit.
They do not alter the integrated manuscript's two core inferences.

## Supplementary Figures

Suggested layout:

- Fig. S1: full Palmer island trajectories and synchrony matrix;
- Fig. S2: raw N_eff trajectories and all count-error null variants;
- Fig. S3: N_eff-growth mechanical/circular/year-block diagnostics;
- Fig. S4: hierarchical beta and count-error sensitivity;
- Fig. S5: Paper 2 gate flowchart;
- Fig. S6: observation-offset overlap and timing sensitivity;
- Fig. S7: species-specific marginal-slope geometry;
- Fig. S8: Shannon sensitivity;
- Fig. S9: complete multi-radius null distributions;
- Fig. S10: full detectable-effect curve with Wilson intervals;
- Fig. S11: reproductive-denominator audit;
- Fig. S12: Palmer lag-1–5 performance-linked redistribution profile and
  performance-memory diagnostics;
- Fig. S13: Palmer versus Signy lag-2 coefficients with the frozen Signy
  sensitivity results.

## Supplementary Tables

- Table S1: all frozen data sources and fingerprints;
- Table S2: Palmer island-year census summary;
- Table S3: concentration-null results by island/error model;
- Table S4: Paper 2 unit eligibility by species;
- Table S5: all pre-outcome recovery gates and pass/fail decisions;
- Table S6: primary and secondary Paper 2 coefficients;
- Table S7: observation-source sensitivities;
- Table S8: radius/Shannon sensitivities;
- Table S9: denominator-semantics audit;
- Table S10: Palmer performance-memory and P1–P3 mechanism diagnostics;
- Table S11: Signy support gate, primary replication and frozen sensitivities.

## Terminal rule

The Supplement exists to make the inferential history auditable, not to create
additional positive conclusions. No Supplement analysis may be promoted in
response to a null or weak main-text result without a new, explicitly
post-outcome manuscript revision.
