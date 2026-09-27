# Critical audit response v2 — serial-structure null correction

## Concern

The earlier synchronized year-block permutation destroyed the temporal
autocorrelation and trend structure of effective colony number. That could make
the coefficient null too narrow and produce anti-conservative evidence for a
positive coefficient. The original mechanical-coupling simulation inherited
the same latent-topology null.

## Circular-shift coefficient null

We froze two structured surrogates before execution.

### Independent island-wise shifts

Each island's complete ordered N_eff sequence was circularly shifted while
response, abundance, island identity and calendar year remained fixed.

This preserves each island's marginal distribution, cyclic temporal ordering,
circular autocovariance and Fourier power spectrum.

With **100,000** shifts:

- observed standardized beta = **+0.1168**;
- surrogate beta >= observed: **0/100,000**;
- Monte Carlo one-sided **p < 1e-5**;
- null 97.5th percentile = **0.0628**.

### Exact covariance-preserving sensitivity

CHR, COR, HUM and TOR received one common lag over their 26-transition series;
LIT received an independent lag over 16 transitions. All **416** combinations
were enumerated.

Only the identity alignment reached the observed coefficient:

**p = 1/416 = 0.00240**.

Thus the coefficient anomaly is not explained by the earlier block null having
destroyed N_eff serial structure or the persistent-island cross-covariance.

## Circular-shift mechanical-coupling null

The original Poisson / Gamma-Poisson CV10% / CV20% error models were rerun
without adding error families or tuning CV values. The only change was that
latent colony composition came from circularly shifted same-island donor years.

Probability that the coupled null beta reached +0.1168:

- Poisson: **p = 0.00030**;
- Gamma-Poisson CV10%: **p = 0.00150**;
- Gamma-Poisson CV20%: **p = 0.00780**.

Median paired bias caused by sharing current-year count error was:

- Poisson: **−1.7%** of observed beta;
- CV10%: **+0.5%**;
- CV20%: **+6.6%**.

These are fixed stylized sensitivities, not calibrated observer-error models.

## Final N_eff interpretation

The structured-null correction changes the confidence in the coefficient but
does **not** reverse the earlier predictive downgrade.

- conditional association: **retained**;
- held-out prediction: **not supported** (gain permutation p = 0.262);
- causality: **not identified**;
- early-warning interpretation: **not justified**.

The defensible wording is:

> Effective colony number is conditionally associated with next-year growth
> beyond island, abundance and time, and the observed coefficient is not readily
> reproduced by the frozen serial-structure-preserving or shared-count-error
> nulls. Its small held-out predictive improvement is nevertheless compatible
> with permutation noise.

## Remaining scientific bottleneck

The highest-value next evidence is independent rather than another null model:

1. a one-to-one LTER `colony_code` ↔ GIS polygon crosswalk for the Torgersen
   reconstruction; or
2. replication in another monitored penguin archipelago.

No additional N_eff null family should be opened for the core paper.
