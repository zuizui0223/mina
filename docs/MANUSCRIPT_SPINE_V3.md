# Manuscript spine v3 — post N_eff uncertainty diagnostic

## Working title

**Common decline, divergent endpoints: multiscale demography across Antarctic penguin breeding islands**

## What is no longer the novelty

- PC1 = 96.4% is not presented as surprising.
- Lower annual than long-term synchrony is placed in Moran-effect and
  timescale-dependent synchrony theory.
- N_eff is not presented as a supported held-out predictor.
- The Palmer Penguins audit is not used as the Introduction motivation.

## Central ecological contribution

The Palmer system is an externally subsidized island system: trophic resources
are primarily marine, while reproduction is constrained to discrete terrestrial
patches.

Within a shared regional decline, nearby breeding sites reach different local
states:

- persistence at very low abundance;
- local extinction/vacancy;
- species replacement at the Biscoe Point benchmark;
- habitat-structured subcolony attrition on Torgersen.

The paper therefore asks how **regional demographic direction maps onto local
ecological fate**, not whether synchrony exists.

## Evidence hierarchy

### R1. Regional demographic background

Five complete island series, 1991–2017:

- PC1 = 96.4%;
- median annual-growth correlation = 0.373;
- unique year fraction = 53.5%;
- unique island fraction = 33.0%.

Interpretation: useful scale decomposition, expected to be timescale dependent.

### R2. Local endpoints diverge

Litchfield reaches extinction; other true islands persist at low abundance.
Biscoe Point, explicitly a non-island benchmark, undergoes strong
Adelie-to-gentoo replacement. Dream provides a possible Adelie/chinstrap
alternative but lacks synchronized composition coverage for a confirmatory
community trajectory.

### R3. Simple environmental formulations do not identify the mechanism

Finite prospective tests fail for:

- positive annual sea-ice duration;
- fixed 3/5/7-year duration windows;
- October snowfall x static snow-prone habitat.

These are formulation failures, not evidence that marine climate or terrestrial
habitat are unimportant.

### R4. N_eff association survives one diagnostic but not prediction uncertainty

Original standardized beta: **+0.1168**.

Original held-out MSE gain: **+0.00102884**.

Synchronized 20,000-block permutation:

- gain p = **0.26224**;
- observed gain percentile = **73.78%**;
- beta permutation p ≈ **0.00010**.

Therefore: **association retained; predictive claim withdrawn**.

### R5. Shared census-count error does not readily generate beta +0.1168

Fixed coupled topology-null simulations:

- Poisson p = 0.00080;
- Gamma-Poisson CV10% p = 0.00060;
- Gamma-Poisson CV20% p = 0.00640.

Maximum fixed median paired coupling bias is 8.8% of the observed beta.

Boundary: these are stylized sensitivity models, not calibrated observer-error
estimates.

### R6. Independent Torgersen mapping shows real spatial attrition

23 historic active footprints -> five active by 2022, with non-random terrain
associations.

Boundary: phenomenon-level triangulation only; no public one-to-one
`colony_code` ↔ GIS polygon crosswalk.

## Discussion order

1. Timescale-dependent synchrony is expected; do not oversell PC1.
2. Shared regional direction does not determine local ecological endpoint.
3. Externally subsidized breeding islands make local reproductive-patch state
   ecologically distinct from the marine food environment.
4. The environmental mechanisms tested here are finite falsifications, not
   exhaustive causal analysis.
5. Colony organization is associated with demographic state, but out-of-year
   predictive evidence is weak.
6. Independent spatial evidence supports real breeding-patch attrition while the
   exact census-to-habitat link remains unresolved.

## Journal position

**Ecosphere first shot. Ecology and Evolution fallback.**

JAE is paused unless genuinely independent evidence materially strengthens the
positive ecological result.
