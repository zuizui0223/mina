# Paper 2 design: breeding islands as filters of regional demographic forcing

**Date:** 2026-09-29  
**Repository:** `zuizui0223/mina`  
**Paper lane:** Paper 2  
**Status:** design approved in chat; written before demographic count magnitudes are opened

## 1. Scientific pivot

The primary Paper 2 question is no longer:

> Do colonies with more breeding space or habitat options decline less?

That remains a baseline insurance hypothesis, but by itself it is too expected and too close to a generic habitat-quality result.

The primary question becomes:

> **Does breeding-site architecture determine how strongly a local penguin population is coupled to demographic forcing shared across its region?**

The island is therefore treated as a **response filter**, not simply a resource container.

This is especially appropriate for penguins because the main trophic resource field is marine while reproduction is constrained to discrete terrestrial breeding substrates. The ecological role of the breeding island can therefore be separated from food supply more cleanly than in many classical island systems.

## 2. Island-ecology contribution

The intended island-ecology contribution is:

> **For organisms whose trophic resources are acquired outside the island, island architecture can regulate the transmission of external environmental change into local population dynamics rather than merely determining local carrying capacity.**

This extends the usual area/isolation/resource framing toward a **reproductive-island filter**.

The key distinction is:

```text
classical resource-island intuition
island properties -> local resources/carrying capacity -> population size

mina Paper 2
shared marine/regional forcing
        |
        v
breeding-island filter
(space amount, habitat-complex diversity, relief)
        |
        v
local coupling, idiosyncratic variation, long-term fate
```

The paper must not claim that the latent shared demographic signal is itself a uniquely identified environmental mechanism. Environmental attribution is secondary unless supported independently.

## 3. Why this is not already answered

The design connects three existing results that have largely remained separate.

1. Pan-Antarctic Adélie models show strong shared year effects in population growth, indicating large common temporal forcing (Che-Castaldo et al. 2017, Nature Communications, DOI: 10.1038/s41467-017-00890-0).
2. Environmentally dependent Adélie models transfer surprisingly poorly among colonies, with short spatial forecast horizons and colony-specific intrinsic predictability (Şen et al. 2023, Ecological Indicators, DOI: 10.1016/j.ecolind.2023.110239).
3. Island/community theory predicts that environmental heterogeneity is not uniformly beneficial because finite area creates an area–heterogeneity tradeoff (Allouche et al. 2012, PNAS, DOI: 10.1073/pnas.1208652109). Marine subsidies can also modify classical island-area relationships (Obrist et al. 2020, Proceedings B, DOI: 10.1098/rspb.2020.0108).

A targeted literature check conducted before this design found no obvious study directly testing whether **breeding-site architecture explains population-specific loading on shared regional demographic forcing across Antarctic penguin colonies**.

This is a novelty hypothesis, not a claim of exhaustive priority. A full literature review is required before manuscript wording such as "first test".

## 4. Frozen data context

Already frozen before outcome opening:

- 152 Pygoscelis site x species candidate units at Gate 0.
- 122 distinct candidate sites.
- primary time axis: APBP breeding season.
- primary temporal window: 1980–2025.
- 107 bridged site x species units under the common-window rule.
- primary species: Adélie, chinstrap and gentoo.
- observation structure:
  - direct counts are the reference;
  - image-based counts receive one estimable mean offset;
  - raw platform-specific offsets are sensitivity-only;
  - accuracy precision structure is class 1 versus pooled 2–5;
  - missing-vantage exclusion and ground-only analyses are required sensitivities.

Frozen site predictors at 2 km:

1. **breeding-space amount**  
   `A = z(log1p(mapped ice-free area))`
2. **breeding-option heterogeneity**  
   `H = z(Tier 2 Habitat Complex richness)`
3. **terrain heterogeneity**  
   `R = z(log1p(relief p90-p10))`

No new co-primary static site trait is introduced by this design.

## 5. Primary estimand: coupling to shared regional forcing

For site `i`, species `s`, season `t`, let latent breeding abundance be `N_ist`.

The demographic process is written conceptually as:

```text
log N_i,s,t+1 - log N_i,s,t
    = mu_i,s
    + lambda_i,s * F_g,s,t
    + epsilon_i,s,t
```

where:

- `F_g,s,t` is a standardized latent demographic forcing shared by an outcome-blind-defined geographic group `g` for species `s`;
- `lambda_i,s` is the site's **coupling coefficient** to that shared forcing;
- `mu_i,s` is the site's long-run local growth component;
- `epsilon_i,s,t` is local process variation.

Identification:

- each retained shared forcing is centered at 0 and scaled to SD 1;
- mean site loading within a forcing group is constrained to +1, fixing factor sign and scale;
- individual site loadings may be above 1, between 0 and 1, zero, or negative.

Interpretation:

- `lambda > 1`: amplified regional forcing;
- `0 < lambda < 1`: buffered regional forcing;
- `lambda ~ 0`: demographic decoupling;
- `lambda < 0`: local dynamics oppose the shared regional signal.

The primary ecological target is not simply whether `mu` is less negative.

## 6. Primary island-filter model

Within each species, site coupling is modeled as:

```text
lambda_i
  = 1
  + gamma_A * A_i
  + gamma_H * H_i
  + gamma_R * R_i
  + gamma_AH * A_i * H_i
  + u_region
  + u_site
```

The three frozen predictors remain the only co-primary site variables.

The `A x H` interaction uses only already-frozen predictors and is frozen **before** count magnitudes are opened.

### H1 — breeding-space buffering

More ice-free breeding space reduces the magnitude of coupling to adverse shared regional forcing.

Operational prediction:

- `gamma_A < 0` for coupling magnitude under the primary factor orientation.

This is the simple insurance prediction and is not the main novelty.

### H2 — option–fragmentation crossover

Breeding-option heterogeneity is not assumed to be uniformly beneficial.

At low breeding-space amount, increasing Habitat Complex richness may subdivide finite breeding space into smaller effective patches and **increase or fail to reduce coupling**.

At high breeding-space amount, the same heterogeneity may provide genuine alternative breeding conditions and **reduce coupling**.

Primary directional prediction:

```text
d lambda / d H at A = -1 SD >= 0
d lambda / d H at A = +1 SD < 0
```

Equivalent interaction expectation: `gamma_AH < 0`, with the two marginal effects reported directly.

This is a population-dynamic extension of the area–heterogeneity tradeoff logic, not a claim that Antarctic Habitat Complexes are identical to the niche categories in community-level AHTO theory.

### H3 — terrain as a decoupler, not automatically a stabilizer

Relief can create microtopographic alternatives but also snow/melt traps and spatially uneven breeding conditions.

Therefore relief is not given a one-direction "more is better" prediction for mean trend.

Primary question:

- does relief reduce coupling to shared regional forcing?

Secondary variance question:

- if relief lowers coupling, does it simultaneously increase local process variance?

This separates **decoupling** from **stability**.

A site can be weakly synchronized with its region yet locally unstable.

## 7. Secondary estimands

### 7.1 Long-run local growth

The existing direct site-trait question remains as a secondary baseline:

```text
mu_i = alpha + theta_A A_i + theta_H H_i + theta_R R_i + ...
```

This answers whether architecture predicts average local trajectory after shared forcing is accounted for.

It must not replace the coupling analysis as the headline test.

### 7.2 Local process variance

If the state-space model is identifiable, test whether local residual process variance changes with the frozen site traits.

This is secondary because variance regression is more weakly identified than the coupling coefficients.

The key interpretation is:

- lower regional coupling + lower local variance = genuine buffering;
- lower regional coupling + higher local variance = decoupling without stability;
- unchanged coupling + changed mean growth = ordinary habitat-quality effect.

## 8. Gate 2C: outcome-blind forcing-support audit

Before any count magnitude is summarized or modeled, use only:

- species identity;
- site identity;
- APBP region / CCAMLR geography;
- breeding season;
- record presence/absence.

Purpose: determine whether region x species groupings contain enough overlapping time support to estimate a shared forcing and site-specific loadings.

Candidate grouping hierarchy, fixed in this order:

1. APBP region x species;
2. if insufficient, CCAMLR unit x species;
3. if still insufficient, species-wide forcing with region intercepts.

A region x species forcing group is independently estimable only if it meets all of:

- at least 5 bridged site x species units;
- at least 15 seasons with observations from >=3 distinct units;
- at least 10 seasons in which >=50% of its retained units have either an observation or a state-space bridge between observed seasons;
- at least 3 units spanning both the first and last thirds of 1980–2025.

The audit chooses the finest grouping level that satisfies the rule without inspecting counts.

If APBP and CCAMLR groupings both fail for a species, use a species-wide shared year factor and do not invent a new geography after outcomes are opened.

## 9. Observation model

The observation layer must inherit the frozen Gate 2B result.

Conceptually:

```text
observed count_j
    <- latent N_i,s,t
    + image-based mean offset
    + accuracy-dependent observation error
```

Frozen decisions:

- direct = reference;
- one image-based mean offset;
- unknown vantage retained without its own identified mean offset;
- observation precision grouped as accuracy 1 versus pooled 2–5;
- raw-vantage offsets sensitivity-only;
- missing-vantage exclusion sensitivity required;
- ground-only sensitivity required.

Accuracy flags correspond approximately to increasing count uncertainty (historically about ±5%, ±10%, ±25%, ±50%, ±90% for classes 1–5), but the primary model uses the already-frozen 1 versus 2–5 split rather than five freely estimated scales.

The exact likelihood and priors are to be fixed in the demographic-response contract before counts are opened.

## 10. Species and geography

Primary inference remains species-specific.

Reason:

- Adélie spans 9 APBP regions in the candidate sample;
- chinstrap and gentoo are concentrated mainly in the central-west Antarctic Peninsula and South Shetland Islands;
- species identity and geography are partially confounded.

Therefore:

1. fit each species independently;
2. compare standardized coupling-trait effects across species;
3. pooled hierarchical synthesis is secondary and must include region structure.

No unqualified pooled species x architecture test is primary.

## 11. Relation to Paper 1

Paper 1 establishes a local phenomenon:

> shared regional decline can coexist with non-proportional internal reorganization within breeding islands.

Paper 2 asks the broader question:

> does breeding-site architecture systematically determine how strongly local populations track shared regional demographic forcing?

The papers therefore operate at different scales:

```text
Paper 1:
regional decline -> within-island redistribution/concentration

Paper 2:
shared regional forcing -> site-specific coupling -> local population trajectory
                         ^
                         |
                breeding-site architecture
```

Paper 2 must not claim that the exact within-island concentration mechanism is measured across Antarctica. MAPPPD does not provide equivalent within-site subcolony structure.

## 12. Falsifiable result space

The design is valuable even if the intuitive insurance prediction fails.

### Result A — simple buffering

`A`, `H` or `R` lowers `lambda` and/or improves `mu`.

Interpretation: breeding architecture buffers shared demographic forcing.

### Result B — option–fragmentation crossover

Heterogeneity amplifies or fails to buffer coupling on small-space sites but buffers coupling on large-space sites.

Interpretation: the ecological value of habitat heterogeneity depends on the amount of breeding space available.

This is the most distinctive island-ecology result.

### Result C — decoupling without stability

Heterogeneous/relief-rich sites have lower regional loading but larger local process variance.

Interpretation: architectural complexity reduces synchrony without necessarily increasing demographic stability.

### Result D — architecture affects mean growth but not coupling

Interpretation: ordinary local habitat-quality effect; the response-filter hypothesis is not supported.

### Result E — no site-trait effects

Interpretation: breeding-site architecture does not explain the observed spatial heterogeneity in shared-forcing response at this scale; marine/regional processes or unmeasured local factors dominate.

This null result must remain publishable and must not trigger new trait fishing.

## 13. Anti-p-hacking rules added by this design

Before demographic count magnitudes are opened:

- freeze the forcing-support audit and grouping fallback;
- freeze the `A x H` interaction as the only co-primary interaction;
- do not add quadratic terms after seeing outcomes;
- do not search alternative buffer radii;
- do not replace Habitat Complex richness with Shannon except the already-declared sensitivity;
- do not select a subset of years because coupling is stronger there;
- do not choose an environmental covariate because it correlates with the fitted latent forcing;
- do not reinterpret low coupling as resilience without checking local process variance;
- do not call the latent factor a specific climate mechanism without independent evidence.

## 14. Figures if the design survives

1. Antarctic map of the frozen 107 demographic units and site architecture.
2. Conceptual response-filter diagram plus examples of high- and low-coupling colony trajectories.
3. Species-specific distributions of site loadings `lambda` and architecture effects.
4. Area x heterogeneity response surface for `lambda`.
5. Mean growth versus coupling versus local process variance, separating buffering from decoupling.

## 15. Success criterion

Paper 2 succeeds scientifically if it can distinguish these three propositions:

1. **habitat quality:** some breeding sites simply have better average growth;
2. **response filtering:** site architecture changes sensitivity to shared regional forcing;
3. **decoupling:** site architecture changes synchrony but not necessarily stability.

The headline island-ecology claim is justified only by proposition 2, especially if the option–fragmentation crossover is supported.

## 16. Immediate next implementation step

Run Gate 2C using timestamps and geography only.

Do **not** open demographic count magnitudes until Gate 2C freezes:

- forcing group definitions;
- fallback hierarchy actually selected for each species;
- exact state-space demographic likelihood;
- priors and observation-error treatment;
- reporting rules for `lambda`, `mu`, the `A x H` interaction and local process variance.
