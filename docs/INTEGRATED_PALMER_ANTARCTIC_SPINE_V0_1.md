# Integrated manuscript spine v0.1 — local reorganization, limited transferability

## Working title

**Local reorganization without a transferable island-resilience rule in Antarctic penguins**

Alternative:

**From within-island concentration to continental limits: testing island-structured demography in Antarctic penguins**

## Core question

When populations experience broad environmental forcing, does the individuality
of islands create predictable demographic responses across scales?

This manuscript answers that question in two nested stages.

1. **Discovery at Palmer:** determine whether a coherent regional decline is
   expressed simply as proportional thinning or as within-island demographic
   reorganization.
2. **Antarctic-wide test:** ask whether static breeding-island architecture
   predicts how strongly local populations couple to shared forcing.

The first succeeds strongly. The second does not yield a confirmatory,
scale-invariant rule.

The resulting claim is not that islands do not matter. It is:

> **Island individuality is visible in local demographic endpoints and
> within-island reorganization, but it does not automatically yield a static,
> transferable macroecological rule for resilience.**

## Part I — Palmer discovery system

### Data

Five neighbouring Adélie penguin breeding islands near Palmer Station,
1991–2017.

The island populations share a strongly coherent long-term decline:

- PC1 of standardized log abundance: **96.4%**.

But their local demographic endpoints diverge.

### Main phenomenon: concentration during decline

In the three islands with unchanged colony-code rosters, effective colony
number declined:

- Cormorant: **3.54 → 2.86** (−19%);
- Humble: **4.62 → 2.28** (−51%);
- Litchfield: **5.78 → 1.00** before local extinction (−83%).

Under fixed-composition nulls preserving each observed island-total trajectory,
the observed concentration slopes remain unusual:

- Cormorant: p = **0.038** even under the uncalibrated 20% multiplicative-CV
  model;
- Humble: plus-one p = **0.000010**;
- Litchfield: plus-one p = **0.000010**;
- all three simultaneously: p = **0.000010**.

Independent Torgersen mapping records parallel physical contraction from 23
historic active subcolonies to five active footprints and habitat-structured
extinction.

### Part I conclusion

Regional decline is not expressed as proportional thinning alone.

> **As island populations contract, breeders become concentrated into a
> smaller effective set of within-island breeding components.**

This is a local-scale ecological phenomenon.

N_eff next-year-growth associations, sea-ice diagnostics and beta-hierarchy
results are supporting diagnostics, not the central manuscript result.

## Transition: the scaling question

Part I raises a tempting island-ecology hypothesis.

If breeding islands differ in the amount and diversity of terrestrial options
available to penguins, perhaps those static differences explain why populations
respond differently to broader forcing.

This is especially interesting in penguins because their main trophic resource
field is marine while reproduction is tied to terrestrial breeding landscapes.

The Antarctic-wide test therefore asks:

> **Does breeding-island architecture act as a transferable filter on shared
> demographic forcing?**

## Part II — Antarctic-wide test

### Frozen analysis frame

- three Pygoscelis species;
- 152 candidate site × species units at Gate 0;
- 107 temporally bridged units, 1980–2025;
- 2,100 frozen nest-count records;
- final predictor-complete V3 frames:
  - Adélie 41;
  - chinstrap 34;
  - gentoo 29.

One species-wide latent annual forcing is estimated per species. Geography is
retained separately as an adjustment stratum in the loading model:

- Adélie: CCAMLR block;
- chinstrap/gentoo: APBP region.

**Important interpretation boundary:** the species-wide factor is an
identifiability/model-resolution decision, not evidence that biological forcing
is literally synchronized at the full species-range scale. Finer regional
factors were rejected by pre-outcome recovery because they could not be
reliably identified from the frozen temporal layout. The manuscript must not
turn that fallback into an ecological result about the spatial scale of
synchrony.

### Primary island-architecture test

At the frozen 2 km scale:

- A = mapped ice-free breeding-space amount;
- H = Tier 2 Habitat Complex richness;
- primary interaction = A × H effect on site coupling to the shared forcing.

Observed gamma_AH:

- Adélie: **−0.304**;
- chinstrap: **−1.184**;
- gentoo: **−0.318**.

All three are negative.

Chinstrap and gentoo show the full point-estimate option–fragmentation geometry;
Adélie shows attenuation but not a sign-reversing crossover.

### Frozen inference

Paper-level statistic:

- median gamma_AH = **−0.318**;
- 9,999 block-preserving permutations;
- one-sided p = **0.0947**.

Species-specific Holm-adjusted tests also do not reject.

Therefore:

> the Antarctic-wide test does **not** provide confirmatory evidence that
> breeding-island area and habitat heterogeneity jointly create a general
> demographic filter.

### Simple breeding-space hypothesis

A-only estimates are negative in all three species:

- Adélie −0.280;
- chinstrap −0.200;
- gentoo −0.071.

But none survives the preregistered species-specific permutation tests after
Holm correction.

The intuitive rule

> “more breeding space = stronger demographic buffering”

is therefore also unsupported.

## Observation robustness

The focal 2 km interaction is stable to how the image/direct calibration is
timed.

Primary same-season image/direct factor: approximately **1.040**.

Exact-date and <=14-day calibrations yield cross-species median gamma_AH values
of approximately **−0.326** and **−0.323**, respectively, retaining:

- negative interactions in all three species;
- full point-estimate crossover in chinstrap and gentoo.

Thus the negative point-estimate pattern is not explained by the broad
same-season image calibration.

## Spatial support

Raw sensitivity:

- 1 km: median gamma_AH = **−0.058**;
- 2 km richness, primary: **−0.318**;
- 5 km: **+0.107**.

Tier 2 Shannon at 2 km gives median gamma_AH = **−0.163** and retains the
chinstrap/gentoo crossover classification but not Adélie.

### Radius sign-switch null

The raw 1/2/5 km estimates change substantially, but this pattern is **not**
evidence for a biological scale effect.

A joint block-preserving multi-radius permutation keeps each site's complete
1/2/5 km trait tuple together, preserving cross-radius covariance, and asks how
often the null generates both:

1. a negative 2 km median and positive 5 km median; and
2. a 5 km minus 2 km contrast at least as large as the observed **0.425**.

Across the full frozen **9,999** joint permutations:

- the simple 2 km negative → 5 km positive sign switch occurred with
  plus-one probability **0.2478**;
- a 5 km − 2 km contrast at least as large as the observed **0.425** occurred
  with probability **0.0971**;
- the prespecified **joint sign-switch + contrast** event occurred 809 times,
  giving plus-one probability **0.0810**;
- a 1/2/5 km range at least as large as observed occurred with probability
  **0.2645**;
- the exact observed ordering `2 km < 1 km < 5 km` together with an
  observed-size range occurred with probability **0.0765**.

Therefore the prespecified ecological scale-dependence criterion
(joint probability <= 0.05) is not met.

The correct interpretation is:

> the island-architecture estimate is sensitive to how the breeding landscape
> is spatially supported, but the observed sign reversal is compatible with
> finite-sample/block-permutation fluctuation and should not itself be treated
> as a biological scale-dependence discovery.

## Information content of the null primary result

The observed paper-level effect is −0.318 and the frozen 5% permutation
boundary is approximately −0.424.

A post-inference operating-characteristic analysis reused the unchanged V3
simulation/model on the real frozen observation layout and compared synthetic
common effects with the exact frozen 9,999-permutation rejection rule.

Detection fractions were:

| true common gamma_AH | detection fraction |
| ---: | ---: |
| −0.20 | 0.000 |
| −0.25 | 0.0367 |
| −0.30 | 0.0467 |
| −0.35 | 0.1167 |
| −0.40 | 0.3800 |
| −0.45 | 0.5967 |
| −0.50 | 0.8100 |
| −0.55 | 0.9267 |
| −0.60 | 0.9667 |

The resulting retrospective detectable-effect thresholds are:

- **MDE80 = |gamma_AH| 0.498**;
- **MDE90 = |gamma_AH| 0.539**.

The observed absolute effect, 0.318, is only about 64% of MDE80.

Therefore the primary null is **not** strong evidence that an interaction of
the observed/moderate magnitude is absent. The design had little power for a
common interaction around −0.30 to −0.35. It was, however, highly sensitive to
very large common interactions around −0.55 or stronger.

This analysis is a sensitivity diagnostic, not an equivalence test and not an
upper confidence bound. Do not write that effects larger than 0.50 are ruled
out. The defensible wording is:

> the study was well positioned to detect a very large common interaction, but
> not a moderate interaction of the magnitude actually observed.

## Integrated ecological result

The combined evidence separates three propositions.

### 1. Local demographic reorganization exists

Supported strongly at Palmer.

Island population contraction is accompanied by concentration among
within-island breeding components.

### 2. Static island architecture may covary with local demographic coupling

Suggested by the 2 km point estimates, especially in chinstrap and gentoo.

But this association is not confirmatory at the paper level.

### 3. Static island architecture provides a transferable Antarctic resilience rule

Not supported.

This is the main cross-scale conclusion.

> **Local demographic reorganization is clear, but the Antarctic-wide data do
> not establish a transferable static-island rule for its demographic
> consequences. Moderate common effects remain unresolved, while very large
> common effects were readily detectable.**

## Relation to ODSP

The conceptual bridge to ODSP is information hierarchy.

An apparent “island signal” can contain information from different levels:

- species identity;
- regional forcing;
- island-level structure;
- within-island spatial organization.

The analytical failure mode is to treat information carried by one level as if
it were transferable information about another.

In this manuscript:

- Palmer demonstrates real within-island organization;
- the Antarctic test asks whether static island structure transfers that
  information across populations;
- the non-confirmatory result shows that the transfer is limited.

ODSP is therefore an intellectual origin, not terminology that needs to appear
in the manuscript.

## Phenotype result

The phenotype lane is not required for the main manuscript.

Current interpretation:

- much of the apparent island-level phenotype difference is carried by species
  composition;
- Adélie island differences are weak/unstable.

Default placement: Supplement or a short Discussion paragraph.

Promotion to a main-text ecological result requires the separately defined
sign-reversal null.

## Figure architecture

### Figure 1 — Two scales of the problem

Panel A: Palmer five-island trajectories.

Panel B: within-island concentration / effective colony number.

Panel C: Antarctic-wide map of the three species and final analysis units.

The visual question becomes:

> local island individuality exists — does it transfer?

### Figure 2 — Palmer concentration phenomenon

Observed concentration slopes against fixed-composition/count-error nulls,
plus independent mapped contraction.

### Figure 3 — Antarctic-wide island-filter test

Species gamma_AH estimates plus cross-species median and frozen permutation
null.

The visual must emphasize that all point estimates are negative while the
paper-level test is non-confirmatory.

### Figure 4 — generality/scale diagnosis

Panel A: low-area and high-area H slopes by species.

Panel B: 1/2/5 km interaction estimates.

Panel C: radius-null diagnostic once completed.

Optional inset: retrospective detectable-effect curve.

## Discussion order

### 1. Start with the contrast

Decline has a clear within-island spatial architecture at Palmer, but that
architecture does not translate into a confirmed static Antarctic-wide
predictor of demographic coupling.

### 2. Why local mechanism need not be transferable

Potential, explicitly nonidentified reasons:

- behavioral relocation;
- historical occupancy;
- density dependence;
- snow/melt and fine-scale substrate;
- marine foraging environment;
- mismatch between mapped potential habitat and occupied nest substrate.

### 3. Externally subsidized islands

For marine-foraging breeders, terrestrial islands constrain reproduction
without containing the dominant trophic resource field.

Classical area/heterogeneity expectations may therefore be weaker or more
context-dependent than in systems whose key resources are island-contained.

### 4. Hierarchy of island information

Island identity can be informative at one hierarchical level without providing
a transportable predictor at another.

This is the manuscript's strongest general ecological idea.

### 5. A bounded negative result, not evidence of absence

Do not write that “islands do not matter” or that the macroecological effect is
zero.

The operating-characteristic analysis shows low sensitivity to a common
interaction around the observed magnitude (about 0.32), but high sensitivity
to very large common interactions (MDE80 about 0.50; MDE90 about 0.54).

Write that:

> **the ecological organization visible within islands did not yield a
> confirmed, transferable static-island rule at Antarctic scale; the analysis
> was capable of detecting very large common effects but leaves moderate common
> effects unresolved.**

## Terminal rules

Do not:

- rescue the Antarctic interaction with a species subset;
- call p=0.0947 marginal/near significant;
- introduce new radii or climate windows;
- promote 5 km or Shannon to primary;
- interpret process SD ecologically;
- use phenotype results as rescue evidence;
- present the latent species-wide factor as a specific climate mechanism.
- interpret the retained species-wide factor as evidence for species-wide biological synchrony.

The pending MDE and radius-null diagnostics may refine the strength of the
negative/scale interpretation, but they cannot change the frozen primary
hypothesis test.
