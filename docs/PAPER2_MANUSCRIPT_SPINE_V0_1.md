# Paper 2 manuscript spine v0.1 — limits of breeding-island buffering

## Working title

**Breeding-island architecture does not provide a scale-invariant demographic filter of shared Antarctic forcing**

Alternative:

**From local reorganization to macroecological limits: testing reproductive-island buffering across Antarctic penguins**

## One-sentence result

Across 104 predictor-complete Pygoscelis site × species units spanning 1980–2025, all three species showed a negative 2 km area × habitat-complex interaction in demographic coupling to a shared species-wide latent forcing, but the preregistered cross-species permutation test was non-confirmatory (median gamma_AH = -0.318, p = 0.0947), simple breeding-space buffering was also unsupported, and the interaction changed strongly with spatial radius.

## Why this paper exists

Many island-biogeographic arguments implicitly treat island structure as a local
container of resources, habitats or demographic insurance. Penguins offer a
different system. Their trophic resources are largely marine, whereas
reproduction is constrained to discrete terrestrial breeding landscapes.

This makes breeding islands a useful test of a different hypothesis:

> island architecture may act as a response filter that changes how external
> forcing is translated into local population dynamics.

Paper 1 showed that a shared regional decline can be expressed as
non-proportional reorganization within breeding islands. Paper 2 asks whether
that local architectural logic scales up: can static breeding-space amount,
habitat-option heterogeneity and terrain explain why colonies differ in their
coupling to shared forcing?

The answer is not a clean yes.

## Data scale

Frozen analysis frame:

- MAPPPD pinned at commit `88c73a507e0921b2541c218c71eaf16721bc6502`;
- 152 candidate site × species units at Gate 0;
- 107 temporally bridged units in the common 1980–2025 breeding-season window;
- 2,100 nest-count records in the frozen cohort;
- primary species: Adélie, chinstrap and gentoo penguins;
- final species-wide V3 predictor-complete frames:
  - Adélie: 41;
  - chinstrap: 34;
  - gentoo: 29.

Primary site traits at 2 km:

1. breeding-space amount: `z(log1p(mapped ice-free area))`;
2. breeding-option heterogeneity: `z(Tier 2 Habitat Complex richness)`;
3. terrain relief: frozen but not inferentially opened for the core result.

## Model logic

The final estimator was fixed only after multiple pre-outcome recovery gates.

The final process model uses one latent species-wide annual forcing per species.
Static geography is retained separately as a loading-adjustment stratum:

- Adélie: CCAMLR block;
- chinstrap/gentoo: APBP region.

Within those blocks, A, H and A × H are centered. Site coupling is represented
conceptually as:

```text
lambda_i
  = 1
  + alpha_spatial_block[i]
  + gamma_A * A_i
  + gamma_H * H_i
  + gamma_AH * A_i * H_i
  + b_i
```

The key primary parameter is `gamma_AH`.

The predeclared ecological prediction was an option–fragmentation crossover:

- at low breeding-space amount, greater heterogeneity may subdivide scarce
  effective breeding space;
- at high breeding-space amount, heterogeneity may provide usable alternative
  breeding conditions.

The frozen full-crossover classification requires:

```text
gamma_AH < 0
low-area H slope  = gamma_H - gamma_AH >= 0
high-area H slope = gamma_H + gamma_AH < 0
```

## Why the estimator is defensible

The development history is a strength of the paper and belongs in Methods/SI,
not as a heroic success story.

### Outcome-blind gates

Before real count magnitudes were opened:

- observation-method overlap was audited;
- direct versus image offset was shown estimable;
- accuracy precision was collapsed to 1 versus 2–5;
- predictor missingness was corrected so unsupported AEI sites were NA, not
  ecological zeroes;
- A × H design-matrix identifiability was confirmed;
- latent-factor recovery was tested on the real temporal schedule;
- regional forcing was rejected for gentoo and later, under the integrated
  count model, for Adélie/chinstrap;
- the final retained forcing scale became species-wide for all three species;
- the first two-stage integrated estimator failed and was frozen as a failure;
- hierarchical V2 recovered the frozen synthetic scenarios;
- spatially adjusted V3 then restored within-region trait comparison;
- nonzero H-main recovery was separately validated because crossover
  classification uses H marginal slopes;
- cross-species generality and paper-level observation-source robustness were
  tested before real outcomes were opened.

No failed gate was rescued by relaxing its frozen recovery threshold.

## Primary result

Observed V3 interaction estimates:

| Species | gamma_AH | Frozen species p | Holm p | full point-estimate crossover? |
| --- | ---: | ---: | ---: | --- |
| Adélie | -0.304 | 0.2162 | 0.2162 | No |
| Chinstrap | -1.184 | 0.0661 | 0.1689 | Yes |
| Gentoo | -0.318 | 0.0563 | 0.1689 | Yes |

All three interactions were negative.

The preregistered paper-level statistic was the median interaction across the
three species:

```text
median gamma_AH = -0.318
9999 block-preserving permutations
one-sided p = 0.0947
```

The permutation null was centered near zero
(median = 0.0027; 5–95% range = -0.424 to 0.366).

Therefore the primary hypothesis is **not confirmed**.

The correct wording is:

> The three species showed concordant negative point estimates at the frozen
> 2 km richness scale, but the preregistered cross-species permutation test did
> not provide confirmatory evidence for a general area-dependent
> heterogeneity effect.

Do not write “marginally significant”, “approached significance”, or substitute
a species subset.

## What the point estimates still show

Adélie:

```text
gamma_A  = -0.399
gamma_H  = +0.348
gamma_AH = -0.304
low-area H slope  = +0.652
high-area H slope = +0.045
```

The interaction is negative, but the high-area H slope remains slightly
positive. Adélie therefore shows attenuation of the apparent fragmentation
effect with area, not a full sign-reversing crossover.

Chinstrap:

```text
gamma_A  = -0.705
gamma_H  = +0.717
gamma_AH = -1.184
low-area H slope  = +1.901
high-area H slope = -0.467
```

Gentoo:

```text
gamma_A  = -0.255
gamma_H  = +0.109
gamma_AH = -0.318
low-area H slope  = +0.427
high-area H slope = -0.209
```

Chinstrap and gentoo therefore show the complete point-estimate
option–fragmentation geometry at 2 km, but neither species-specific interaction
survives the frozen Holm correction.

## Prespecified H1: simple breeding-space buffering

The simpler prediction was:

> more breeding space should reduce local coupling to shared forcing.

A-only estimates were negative in all three species:

```text
Adélie    gamma_A = -0.280
Chinstrap gamma_A = -0.200
Gentoo    gamma_A = -0.071
```

But none was inferentially supported:

| Species | raw p | Holm p |
| --- | ---: | ---: |
| Adélie | 0.1426 | 0.4278 |
| Chinstrap | 0.4225 | 0.6134 |
| Gentoo | 0.3067 | 0.6134 |

Thus even the intuitive “larger breeding landscape = stronger demographic
buffer” version of the hypothesis is unsupported.

H-only point estimates are descriptive only:

```text
Adélie    gamma_H = +0.294
Chinstrap gamma_H = +0.518
Gentoo    gamma_H = -0.006
```

There is no consistent simple heterogeneity-buffering signal.

## Robustness: observation calibration

The primary shared image/direct multiplicative offset was approximately 1.040.

Timing-matched sensitivity estimates were:

```text
exact-date pairs: 23
image/direct factor = 1.069
cross-species median gamma_AH = -0.326

<=14-day pairs: 53
image/direct factor = 1.058
cross-species median gamma_AH = -0.323
```

Under both timing calibrations:

- all three gamma_AH estimates remained negative;
- chinstrap and gentoo retained the full crossover classification;
- Adélie remained negative-interaction but not full crossover.

The directional pattern is therefore not an artifact of the broad same-season
method calibration.

## Robustness: spatial scale and habitat metric

This is the strongest limitation.

### 1 km

```text
median gamma_AH = -0.058
negative species = 2/3
full crossover = gentoo only
```

### 2 km richness — primary

```text
median gamma_AH = -0.318
negative species = 3/3
full crossover = chinstrap + gentoo
```

### 5 km

```text
median gamma_AH = +0.107
negative species = 0/3
full crossover = none
```

### 2 km Shannon instead of richness

```text
median gamma_AH = -0.163
negative species = 2/3
full crossover = chinstrap + gentoo
```

Therefore the interaction is not scale invariant.

The manuscript should not present “island heterogeneity changes from
fragmentation to insurance” as a general law. The defensible ecological point
is instead:

> demographic coupling can show local area-dependent associations with
> breeding-landscape heterogeneity, but those associations are sensitive to the
> spatial support used to define the breeding landscape.

## Island-ecology interpretation

The strongest island-ecology conclusion is a limitation on transferability.

Classical intuition suggests that more island area and more habitat options
should provide demographic insurance. The reproductive-island framing makes a
more specific prediction: when food is obtained outside the island, terrestrial
architecture should act as a filter on how external forcing reaches local
population dynamics.

The Antarctic comparison does not provide confirmatory support for a simple,
scale-invariant filter.

That matters because it separates three levels that are easy to conflate:

1. **local reorganization exists** — supported by Paper 1;
2. **some colony-specific architecture associations exist** — suggested by
   the 2 km point estimates, especially in chinstrap and gentoo;
3. **static island architecture yields a transferable macroecological
   resilience rule** — not supported.

This suggests a broader island-ecology lesson:

> the existence of within-island demographic buffering or redistribution does
> not imply that static island structure can predict resilience across islands.

For externally subsidized breeders, marine/regional forcing, behavioral
plasticity, colony history and fine-scale occupied substrate may dominate or
interact with static landscape structure in ways that prevent a single
area/heterogeneity rule from transferring across scales.

## Relation to Paper 1

The two papers now fit together more cleanly than under the original positive
Paper 2 hypothesis.

### Paper 1

Shared decline can resolve into heterogeneous within-island endpoints and
subcolony reorganization.

### Paper 2

A macroecological attempt to predict that heterogeneity from static
breeding-island architecture does not yield a confirmed, scale-invariant rule.

Together:

> local demographic reorganization is real, but its macroecological
> predictability from simple island architecture is limited.

This is a substantive ecological conclusion, not merely a failed replication.

## Results order

### Result 1 — analysis frame and recovery-qualified estimator

Briefly establish:

- 107 bridged units;
- 2,100 observations;
- final 41/34/29 predictor-complete frames;
- species-wide forcing;
- spatial loading-adjustment blocks;
- successful V3/V4 pre-outcome recovery.

Do not let the methods-development history dominate the ecological Results.

### Result 2 — primary area × heterogeneity interaction

Show:

- all three observed gamma_AH values;
- paper-level median;
- frozen permutation p = 0.0947;
- species-specific raw/Holm p-values.

Main figure should make clear that the point-estimate concordance and the
inferential uncertainty coexist.

### Result 3 — marginal-slope geometry

Show low-area versus high-area H slopes.

Important distinction:

- chinstrap/gentoo: point-estimate full crossover;
- Adélie: attenuation, not sign reversal.

### Result 4 — simple breeding-space H1

Show all three negative A-only point estimates and non-significant permutation
tests.

This rules out the easy fallback story that total breeding space alone is the
robust signal.

### Result 5 — robustness and scale dependence

Show:

- timing-offset stability;
- 1/2/5 km comparison;
- Shannon comparison.

The 5 km reversal belongs in the main Results or a prominent robustness panel,
not buried in the supplement.

## Figure spine

### Figure 1 — System and inferential architecture

A compact schematic:

```text
shared species-wide demographic forcing
                 |
                 v
       breeding-island loading
        /        |        \
     area   heterogeneity  A x H
                 |
                 v
        local population trajectory
```

Alongside an Antarctic site map and sample-size summary.

### Figure 2 — Primary interaction effects

Forest/interval-like panel with:

- observed gamma_AH for each species;
- cross-species median;
- permutation-null distributions or reference quantiles;
- p-values.

Avoid visual language that makes p=.0947 look like a positive finding.

### Figure 3 — Ecological geometry

For each species, plot fitted coupling against H at A = -1 SD and +1 SD.

This makes the difference between:

- Adélie attenuation;
- chinstrap/gentoo crossover;

immediately visible.

### Figure 4 — Scale dependence

Plot gamma_AH by spatial support:

```text
1 km | 2 km richness | 5 km
```

with Shannon-2 km as a separate marker.

This may become the most memorable ecological figure because it shows why a
single island-architecture rule does not transfer across scales.

## Abstract skeleton

Island structure is often expected to buffer population responses by providing
more space or habitat options, but this assumption is difficult to separate
from local resource supply. Antarctic penguins obtain food primarily at sea
while reproducing on discrete terrestrial breeding landscapes, allowing a test
of whether breeding-island architecture filters shared demographic forcing. We
combined long-term nest-count records for three Pygoscelis penguins with
outcome-blind breeding-space and habitat-complex metrics and a recovery-tested
hierarchical model of species-wide demographic forcing. At the prespecified
2 km scale, area × habitat-heterogeneity interactions were negative in all
three species, with full point-estimate crossover geometry in chinstrap and
gentoo penguins. However, the preregistered cross-species block-permutation test
was non-confirmatory (median gamma_AH = -0.318, p = 0.0947), and a simpler
breeding-space buffering hypothesis was also unsupported. The interaction was
stable to observation-timing calibration but strongly dependent on spatial
support, weakening at 1 km and reversing at 5 km. These results do not support
a scale-invariant demographic buffering rule based on breeding-island
architecture. Instead, they show that local island structure can be associated
with demographic coupling at particular spatial scales without yielding a
transferable macroecological resilience rule.

## Discussion architecture

### 1. Start with the falsification

The intuitive buffering hypothesis did not survive the frozen confirmatory
test.

This should be the opening sentence of the Discussion, not hidden after the
negative p-value.

### 2. Explain why the negative result is informative

The design had enough synthetic recovery power to detect the predeclared
effects under the real temporal/observation structure. Therefore the result is
not simply “the model could not work”.

The observed pattern is real enough to produce concordant point estimates but
not stable enough across spatial support to justify a general rule.

### 3. Scale is part of the biology

A breeding landscape defined at 1, 2 and 5 km represents different ecological
objects.

The sensitivity reversal implies that “habitat heterogeneity” is not a
scale-free property of a breeding island.

Possible mechanisms belong in Discussion only:

- immediate nest-site microenvironment;
- within-colony relocation;
- access routes and snow/melt redistribution;
- historical occupancy and density dependence;
- mismatch between mapped potential habitat and actually occupied substrate.

Do not promote any of these to inferred mechanisms.

### 4. External subsidies weaken classical island intuitions

When trophic resources come from outside the island, terrestrial island
structure may constrain reproduction without controlling the dominant resource
field.

This can weaken the direct translation from island area/heterogeneity to
population stability.

### 5. Local mechanism does not imply macroecological predictability

Use Paper 1 as the motivating contrast, not as pooled evidence.

Within-island reorganization can occur without producing a transferable
cross-island rule.

## What not to do next

Do not:

- search alternative radii between 1 and 5 km;
- open climate months or sea-ice windows to rescue the interaction;
- redefine the species subset around chinstrap + gentoo;
- replace richness with Shannon as the primary metric;
- switch to a two-sided or different permutation test;
- introduce a new island-size variable post-outcome;
- interpret process SD ecologically;
- call p = 0.0947 a trend or near-significance.

Any environmental attribution of the latent species-wide forcing is a separate,
pre-specified extension or a separate paper.

## Current paper-level conclusion

The most defensible conclusion is:

> **Breeding-island architecture does not provide a simple, scale-invariant
> demographic filter of shared Antarctic forcing.**

The more interesting conceptual implication is:

> **Local demographic reorganization can be real without being predictable
> from static island architecture at macroecological scales.**
