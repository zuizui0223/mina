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

Within each species, the frozen modeling order is deliberately staged rather than placing every term in one primary model.

1. Fit each frozen site predictor separately against coupling, with the selected forcing-group structure:
   - `group + A`
   - `group + H`
   - `group + R`
2. Test the single predeclared ecological interaction in a dedicated crossover model:
   - `group + A + H + A:H`
3. Fit `group + A + H + R + A:H` only as a **secondary combined synthesis** if diagnostics remain acceptable.

The three frozen predictors remain the only co-primary site variables. The `A x H` interaction uses only already-frozen predictors and was frozen **before** count magnitudes were opened. This ordering preserves the earlier predictor-set contract: main effects are not allowed to disappear inside a more complex combined model before their standalone relationships are reported.

### H1 — breeding-space buffering

More ice-free breeding space reduces the signed site loading on the shared regional forcing under the fixed positive factor orientation.

Operational prediction:

- `gamma_A < 0` for the signed coupling coefficient under the primary factor orientation.

Because individual `lambda` values are allowed to cross zero, absolute coupling magnitude (`|lambda|`) is reported descriptively rather than substituted for the predeclared signed-loading test.

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
- at least 10 seasons in which >=50% of its retained units are temporally covered, where a unit is covered in a season only when that season lies between its first and last observed season in the frozen window;
- at least 3 units spanning both the first and last thirds of 1980–2025.

The strict Gate 2C diagnostic first evaluated complete coverage: a level counted as complete only when every frozen bridged unit belonged to a qualifying group. That diagnostic is retained as an audit result, but it exposed an outcome-blind design problem: one or two isolated series can force an otherwise well-supported multi-region species onto a species-wide factor.

Before demographic count magnitudes were opened, the modeling-eligibility rule was therefore refined and separately frozen:

- choose the finest APBP or CCAMLR level for which qualifying groups jointly contain at least **95%** of that species' frozen bridged units;
- require at least **two qualifying groups** at that regional level;
- units outside those estimable groups remain available for secondary long-run growth/trend analyses but are excluded from the shared-forcing `lambda` estimand;
- if neither APBP nor CCAMLR satisfies the rule, use species-wide forcing only if its support gate qualifies;
- the 95% threshold reuses the atlas program's pre-existing completeness tolerance and cannot be changed after abundance outcomes are opened.

The outcome-blind Gate 2C support audit selected:

- **Adélie:** CCAMLR, 42/44 units (95.5%), groups 48.1 and 88.1; `PGEO` and `WPEC` excluded from coupling only.
- **Chinstrap:** APBP region, 33/34 units (97.1%), Central-west Antarctic Peninsula and South Shetland Islands; `STNK` excluded from coupling only.
- **Gentoo:** APBP region, 28/29 units (96.6%), Central-west Antarctic Peninsula and South Shetland Islands; `STNK` excluded from coupling only.

The primary shared-forcing coupling cohort is therefore **103/107 units (96.3%)**. No count magnitude, trend direction, or site-trait association was used to choose these scales.

Contract: `contracts/PAPER2_FORCING_MODEL_ELIGIBILITY_V1.json`.

### Gate 2D — predictor identifiability — PASSED

Before demographic outcomes were opened, the selected coupling cohort was joined
to the frozen 2 km site predictors and audited as a design matrix only.

The corrected breeding-option missingness rule leaves **101 complete predictor
units** for the primary regional coupling analysis:

- Adélie: **40**
- chinstrap: **33**
- gentoo: **28**

The predeclared crossover matrix `group + A + H + A:H` is full rank in all
three species. Interaction VIF is **2.26 / 1.25 / 1.19** and condition number is
**3.72 / 4.03 / 4.32** for Adélie / chinstrap / gentoo. Every species has at
least four units in each A/H sign quadrant, and each selected forcing group
retains at least three distinct Habitat Complex richness values.

Therefore the option–fragmentation crossover remains a structurally estimable
primary interaction. This gate says only that the interaction can be estimated;
it does not say that the ecological effect exists.

Receipt:
`results/PAPER2_PREDICTOR_IDENTIFIABILITY_AUDIT_RESULT_V1.json`.

### Forcing-scale sensitivity — FROZEN

The 95% regional-eligibility rule is not treated as invisible analyst
flexibility. An outcome-blind threshold audit shows that the regional choices
are unchanged at 90% and 95% coverage, whereas a 97.5% or 100% completeness
requirement sends all three species to a species-wide forcing factor.

The primary analysis therefore retains the frozen regional forcing definitions,
but a **species-wide shared-forcing fit is mandatory** using all 107 bridged
units, with **104 complete predictor cases** (Adélie 41, chinstrap 34, gentoo
29). The observation model, priors, site predictors, transforms and time window
must remain identical.

A response-filter conclusion is called scale-robust only when the regional and
species-wide fits agree qualitatively on the focal site-trait effect and do not
reverse the A × H crossover. If they disagree materially, the result is reported
as **forcing-scale dependent** rather than choosing the more favorable scale.

Contract:
`contracts/PAPER2_FORCING_SCALE_SENSITIVITY_V1.json`.

### Gate 2E-A — latent-factor schedule recovery — PASSED WITH ONE FALLBACK

The Gate 2C temporal-support criterion was not treated as sufficient evidence
that the corresponding latent forcing can actually be recovered from the
irregular census schedule. Before any real abundance magnitude was opened,
the frozen 1980–2025 observation seasons were therefore used in a synthetic
latent-state recovery experiment.

Each species/scale was tested over 100 null and 100 crossover simulations with:

- shared-forcing SD = 0.08;
- site-loading residual SD = 0.15;
- process SD = 0.04;
- site-drift mean = -0.01 and SD = 0.01;
- crossover truth `gamma_AH = -0.35`;
- null truth `gamma_AH = 0`;
- eight fixed alternating-least-squares iterations.

The fit did **not** receive the simulated forcing. It estimated annual shared
forcing and site loadings jointly from inter-observation changes, with
mean-zero forcing and mean-one loading identification within forcing group.
The true forcing was used only after fitting to score recovery.

The frozen recovery gate required every forcing group to have median
true-versus-estimated forcing correlation >=0.70 and 5th-percentile correlation
>=0.30, while the crossover estimate had to recover `-0.35` with absolute
median bias <=0.10 and >=90% negative estimates. The null estimate had to
remain centered within +/-0.05 with its 5th–95th percentile interval spanning
zero.

Results:

- **Adélie:** CCAMLR forcing retained. Group median correlations were **0.948**
  (48.1) and **0.964** (88.1), with 5th percentiles **0.893** and **0.895**.
  Median recovered `gamma_AH = -0.358`; 100% of crossover replicates were
  negative.
- **Chinstrap:** APBP-region forcing retained. Median correlations were
  **0.768** (Central-west Antarctic Peninsula) and **0.936** (South Shetland
  Islands), with 5th percentiles **0.490** and **0.883**. Median recovered
  `gamma_AH = -0.334`; 99% were negative.
- **Gentoo:** the Gate 2C APBP-region scale **failed** latent-factor recovery.
  The Central-west Antarctic Peninsula factor had median correlation only
  **0.349** and 5th percentile **-0.029**, even though the synthetic crossover
  coefficient itself remained recoverable. The predeclared fallback therefore
  applies: **gentoo uses one species-wide shared forcing**. Under that scale,
  forcing correlation was **0.975** (5th percentile **0.958**) and median
  recovered `gamma_AH = -0.343`, with 100% negative recovery.

The primary forcing definition is therefore now:

- Adélie: **CCAMLR**;
- chinstrap: **APBP region**;
- gentoo: **species-wide**.

This is an important design correction: temporal overlap sufficient to define
a candidate forcing group does not guarantee that the factor is recoverable
from the actual sampling schedule.

Receipt:
`results/PAPER2_LATENT_FACTOR_RECOVERY_RESULT_V1.json`.

This gate validates only the latent demographic process under the real
observation-season schedule. It does **not** validate the count observation
likelihood, direct-versus-image offset, accuracy-class error structure, or any
real ecological effect.

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
- one image-based mean offset shared across species;
- unknown vantage retained without its own identified mean offset;
- observation precision grouped as accuracy 1 versus pooled 2–5;
- raw-vantage offsets sensitivity-only;
- missing-vantage exclusion sensitivity required;
- ground-only sensitivity required.

Accuracy flags correspond approximately to increasing count uncertainty (historically about ±5%, ±10%, ±25%, ±50%, ±90% for classes 1–5), but the primary model uses the already-frozen 1 versus 2–5 split rather than five freely estimated scales.

### Gate 2E-B — synthetic observation recovery — PASSED

The exact frozen **2,100-record** metadata layout was reconstructed without
opening any real count magnitude:

- direct records: **1,889**;
- image-based records: **149**;
- unknown vantage: **62**;
- mixed direct/image site × species × season groups: **41**
  (Adélie 9, chinstrap 10, gentoo 22).

Using 200 synthetic replicates with a moderate shared image effect
`delta_image = log(1.15) = 0.1398`, the median recovered offset was
**0.1387** (bias **−0.0011**; 5th–95th percentile **0.105–0.170**) and the
correct sign was recovered in **100%** of replicates. Under the offset-null
simulation, the median was **−0.0011** and the 5th–95th percentile interval
(**−0.0356, 0.0303**) contained zero.

The collapsed accuracy scales were also recoverable from within-season
replication after method correction:

- accuracy 1: 196 repeat groups, residual df 296; truth log-SD 0.04879,
  median recovery **0.04902** (relative bias **+0.5%**);
- pooled accuracy 2–5: 9 repeat groups, residual df 9; truth log-SD 0.22314,
  median recovery **0.21846** (relative bias **−2.1%**).

All frozen recovery checks passed. Species-specific image-offset estimates are
reported only as diagnostics; the primary observation parameter remains one
shared image offset.

Receipt:
`results/PAPER2_OBSERVATION_RECOVERY_RESULT_V1.json`.

This gate validates the observation nuisance layer **in isolation**. It does
not yet demonstrate that shared forcing, site loadings, crossover effects and
observation nuisance parameters are jointly recoverable in one integrated
model.

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

Gate 2E-A validates the latent shared-forcing process on the real season
schedule, with retained scales **Adélie = CCAMLR, chinstrap = APBP region,
gentoo = species-wide**. Gate 2E-B separately validates the frozen shared
image offset and accuracy-1 versus pooled-2–5 observation-error structure on
the real 2,100-record metadata layout.

The next and final pre-outcome gate is **Gate 2E-C: integrated synthetic
process-plus-observation recovery**.

Do **not** open real demographic count magnitudes until one integrated
estimator can recover, from synthetic observations generated on the real
record layout:

- the retained shared forcing at each species' Gate 2E-A scale;
- normalized site loadings `lambda`;
- the null and negative `A x H` scenarios;
- a shared direct-versus-image observation offset;
- the frozen two-level accuracy observation scales or their explicitly frozen
  treatment;
- local process variance sufficiently well to distinguish buffering from
  decoupling-with-instability;
- mandatory species-wide forcing, missing-vantage-exclusion and ground-only
  sensitivities.

The integrated model must be **zero-safe by construction** before outcomes
are opened; the likelihood or transformation cannot be chosen after seeing
whether the real series contain zero nest counts.

Only after Gate 2E-C passes may the frozen real count magnitudes be opened.
