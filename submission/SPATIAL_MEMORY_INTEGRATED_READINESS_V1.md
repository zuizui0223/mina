# Integrated spatial-memory manuscript — scientific readiness v1

**Date:** 2026-10-07

## Current canonical files

- Manuscript: `docs/MANUSCRIPT_SPATIAL_MEMORY_INTEGRATED_V0_4.md`
- Claim ledger: `results/SPATIAL_MEMORY_CLAIM_EVIDENCE_LEDGER_V2.json`
- Process-class contract: `contracts/SPATIAL_MEMORY_PROCESS_CLASSIFICATION_V1.md`
- Reviewer stress test: `docs/SPATIAL_MEMORY_INTEGRATED_REVIEWER_STRESS_TEST_V1.md`
- Novelty boundary: `docs/SPATIAL_MEMORY_NOVELTY_BOUNDARY_V1.md`
- Common counterfactual: `docs/PROPORTIONAL_SPATIAL_COUNTERFACTUALS_V1.md`
- Bibliography: `docs/REFERENCES_SPATIAL_MEMORY_INTEGRATED_V0_4.bib`
- Figure builder: `scripts/build_spatial_memory_integrated_figures.py`
- Figure captions: `docs/FIGURE_CAPTIONS_SPATIAL_MEMORY_INTEGRATED_V0_1.md`

## Scientific status

**Integrated framing: viable.**

The standalone Ross Ecology Report remains on hold.

The integrated manuscript has a defensible three-level claim structure:

1. **Direct:** aggregate abundance direction does not uniquely determine spatial reallocation.
2. **Empirical synthesis:** source-identified kinds of change show different spatial signatures in the available cases.
3. **Hypothesis:** observed breeding structure has an expressed component and a latent site-affiliated component; whether the old distribution can reappear depends on whether change acted mainly on breeding expression, the site-affiliated demographic pool, or breeding capacity.

Only levels 1 and 2 are manuscript conclusions. Level 3 is explicitly a hypothesis.

## Conceptual scaffold

\[
n_{i,t} \propto S_{i,t}q_{i,t},
\qquad
n_{i,t} \le K_{i,t}.
\]

- (S): latent site-affiliated demographic pool;
- (q): breeding expression / participation;
- (K): breeding capacity.

This is not fitted as a latent-state model.

## Evidence architecture

### Temporary breeding-state/access disturbance

Ross 1999→2001→2002.

- breeding abundance -54.3%;
- 96.97% of aggregate loss restored;
- loss/rebound cosine 0.99695;
- inverse-path mismatch 9.41%;
- independent later mark-recapture: breeder inter-colony movement <0.20%, breeder-to-nonbreeder transitions common.

Interpretation ceiling: strong inverse-path recovery is compatible with retained site affiliation.

### Persistent attrition

Palmer + independent Signy replication.

- concentration exceeds proportional thinning under each frozen null;
- empirical term should remain **persistent demographic attrition**, not directly measured vital-rate turnover.

### Capacity change

Beaufort.

- small/new unit gain = 3.15× proportional expectation;
- share increased 0.95%→1.48%;
- independent band/resighting study: Beaufort→Ross movement declined after local habitat became more available.

Interpretation ceiling: case-level conjunction, not mediation.

### Boundary evidence

Bird, Emperor, Heard.

Role: falsify a simple abundance-direction rule only.

## Prior-art boundary

Do not claim novelty for:

- ecological memory;
- unobservable breeding states, temporary emigration, or breeding propensity;
- spatial resilience;
- metapopulation recovery regimes;
- site fidelity;
- the fact that uneven local dynamics alter aggregate recovery.

The narrower contribution is:

> **aggregate recovery can hide structural loss, but the converse also matters: severe breeding-census collapse can overstate structural loss when a previous multi-node allocation remains recoverable.**

The Ross result is the focal empirical case for that converse; Palmer/Signy and Beaufort define contrasting ways in which the demographic pool or breeding landscape can actually be rewritten.

## Main scientific ceiling

The only major missing piece for a general causal law is an independent temporary-shock system with:

1. process class fixed before spatial outcome access;
2. pre-disturbance, trough, and rebound spatial counts;
3. preferably individual fidelity or state-transition information.

This evidence is **not required** to submit the present integrated empirical synthesis.

It **is required** before claiming a prospectively confirmed general law of process-dependent spatial memory.

## Stop rule

Do not search the current opened archives for another favorable shock example.

Do not add species merely to balance class counts.

Do not construct a common A/B/C omnibus score.

A future independent replication must be opened as a new prospective lane, not as rescue of this manuscript.

## Journal ceiling

Current framing is suitable for consideration as an Ecology full Article or Journal of Animal Ecology article, depending whether the final Introduction emphasizes spatial recovery or behavioural-demographic state.

The evidence is not currently sufficient for a Nature / Nature Ecology & Evolution claim of a general law.

## Figure QA

**Complete.**

The integrated five-figure workflow passed CI after the final label-layout correction.

- Figure 1: expressed / latent / capacity conceptual scaffold;
- Figure 2: Ross inverse-path rebound;
- Figure 3: Palmer + Signy persistent attrition;
- Figure 4: Beaufort capacity release;
- Figure 5: anti-sign-locking boundary cases.

The final attrition figure was simplified after visual inspection to remove explanatory text that competed with the bars. Captions now carry the inferential-status details.

## Main evidence table

Canonical table:

    docs/TABLE1_SPATIAL_MEMORY_EVIDENCE_V0_1.md

The table makes the non-exchangeability of the process-specific estimands explicit and prevents the manuscript from visually implying a three-class omnibus comparison. The process-specific tests are instead unified by the proportional spatial counterfactual: aggregate change with no additional reallocation.

## Target journal

Primary target: **Ecology — Article**.

Canonical target plan:

    submission/SPATIAL_MEMORY_ECOLOGY_ARTICLE_PLAN_V1.md

Backup only after a completed Ecology decision: **Journal of Animal Ecology — Research Article**.

The integrated manuscript is too multi-component for the narrower Ecology Report framing and should not be forced back into the 20-page Report format.

## Submission architecture

The program now has one active submission lane:

    submission/PENGUIN_MANUSCRIPT_CONSOLIDATION_V1.md

Palmer Paper 1 v1 and the standalone Ross Ecology Report remain frozen scientific provenance but are not concurrent submission candidates.

## Current action

Revise the integrated manuscript only for coherence, prior-art positioning, and compression.

No new ecological endpoint is required.
