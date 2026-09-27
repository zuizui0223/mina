# Critical audit response v1

Date: 2026-09-27

This document records the response to the strongest pre-submission critique of
the mina manuscript. It is an internal scientific audit, not a response to an
external peer reviewer.

## 1. The only positive result had no uncertainty

### Critique

The original colony-network result reduced LOYO MSE only from 0.07311 to
0.07208 (gain +0.00103), but no null distribution was reported.

### Action

Frozen synchronized year-block permutation diagnostic:

- 20,000 permutations;
- same C0/C1 models and LOYO folds;
- response, island, abundance and year fixed;
- only N_eff year alignment permuted;
- cross-island N_eff covariance retained within donor-year blocks;
- five-island and four-island availability phases permuted separately.

### Result

- observed gain: **+0.00102884**
- null mean: **−0.0002016**
- null SD: **0.002358**
- null 95th percentile: **+0.004417**
- observed percentile: **73.78%**
- one-sided p: **0.26224**

### Consequence

**The predictive claim is withdrawn.** N_eff is not a robust held-out-year
predictor under this uncertainty diagnostic.

The full-data beta remains unusual under the same block null (p≈0.00010), so a
conditional association remains to be evaluated separately.

## 2. PC1 = 96.4% is not a novelty claim

### Critique

Five strongly declining standardized time series will naturally produce a high
common component. Long-term coherence with weaker short-term synchrony already
belongs to the established Moran-effect / scale-dependent synchrony literature.

### Action

Manuscript v0.4:

- treats PC1 and annual-growth correlation as **descriptive dynamical context**;
- explicitly cites Abbott (2007), Desharnais et al. (2018), Anderson et al.
  (2019), Sheppard et al. (2019) and Reuman et al. (2025);
- removes language implying that the long-term/annual contrast is itself a
  surprising synchrony phenomenon.

### Revised role

The biological question is now what a shared regional decline becomes locally:
persistence, extinction/vacancy, species replacement, or contraction of the
internal breeding network.

## 3. N_eff and growth are mechanically coupled through the same census

### Critique

N_eff(t), current abundance N(t), and growth from t to t+1 share census counts,
so counting noise and zeroing of small colonies could induce a coefficient.

### Action

Frozen count-error coupling diagnostic:

- topology-growth alignment destroyed with the same year-block topology null;
- Poisson colony counts;
- fixed Gamma-Poisson CV10% and CV20% sensitivities;
- coupled fit shares current-year simulated counts between N_eff and growth
  denominator;
- decoupled fit uses an independent current-total draw;
- no post-result noise-family or CV tuning.

### Result

Observed beta = **+0.1168**.

Probability of a coupled simulated beta >= observed:

- Poisson: **0.00080**
- Gamma-Poisson CV10%: **0.00060**
- Gamma-Poisson CV20%: **0.00640**

Median paired coupling bias relative to observed beta:

- Poisson: **−2.3%**
- CV10%: **+0.8%**
- CV20%: **+8.8%**

### Consequence

Simple shared count error under these fixed stylized models is not sufficient to
generate the observed-scale coefficient. This does **not** restore the failed
predictive result. N_eff remains only a conditional association, and the noise
models are not empirically calibrated observer-error distributions.

## 4. JAE fit became too weak

### Critique

Three bounded negative mechanism tests plus one small positive predictive result
placed too much weight on procedural integrity for a JAE first shot.

### Action

The N_eff permutation result triggered a formal JAE submission hold.

Current targeting:

1. **Ecosphere** first shot;
2. **Ecology and Evolution** fallback.

The archived JAE files remain provenance only and are not submission ready.

## 5. Manuscript details weakened presentation

### Duplicate Discussion wording

Removed in v0.4.

### Palmer Penguins audit as Introduction motivation

Removed from the primary Introduction and Methods rationale. The ODSP/Palmer
Penguins history remains repository provenance but is no longer used to justify
the ecological manuscript.

## Revised central claim

> A shared regional decline across neighbouring externally subsidized breeding
> islands resolves into heterogeneous local ecological endpoints. The tested
> simple environmental formulations do not identify the mechanism of that
> divergence. Within-island colony organization is conditionally associated
> with demographic state, but its small held-out predictive gain is compatible
> with synchronized year-block permutation noise.

## Remaining high-value evidence gap

The strongest next scientific addition would be genuinely independent:

- a colony-code ↔ GIS polygon crosswalk that connects LTER census units to
  mapped habitat; or
- replication of the colony-organization association in another monitored
  penguin archipelago.

No further climate-window, precipitation-month, threshold, topology-index or
count-error-model tuning is permitted for the core paper.
