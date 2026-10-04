# Paper 2D spine v1 — dynamic breeding opportunity and regional reallocation

**Status:** prospective design note. This document does not open demographic magnitudes or habitat-change outcomes.

## Why a new dynamic lane is needed

The earlier Antarctic breeding-island macroecology lane tested **static place**: whether fixed breeding-space amount, heterogeneity and terrain predict demographic response. That lane did not yield a confirmatory transferable static-place rule.

The next question is deliberately different:

> **When the amount of usable breeding land changes through time, do penguin populations redistribute breeding effort toward the sites that gain terrestrial opportunity?**

This is a change-to-change question. It must not be interpreted as a rescue of the static-area hypothesis.

## Island-ecology object

The ecological unit is a breeding-site node embedded in a regional network.

For each site (i):

- (A_{i,early}): accessible ice-free breeding opportunity in an early optical epoch;
- (A_{i,late}): accessible ice-free breeding opportunity in a late optical epoch;
- (Delta A_i): change in accessible breeding opportunity;
- (D_i): demographic change **relative to the shared regional/species temporal state**, not raw site change alone.

The key quantity is therefore whether sites with larger positive (Delta A_i) gain relative demographic weight within their regional network.

This distinguishes three processes:

1. **capacity tracking** — new terrestrial opportunity attracts/retains breeding effort;
2. **capacity decoupling** — breeding opportunity expands but relative breeding use does not;
3. **capacity loss** — terrestrial opportunity contracts and breeding effort also retreats.

## Primary hypothesis: terrestrial opportunity tracking

### H1
Sites gaining more accessible ice-free breeding opportunity should show more positive demographic change relative to contemporaneous conspecific sites exposed to the same broad regional temporal state.

The primary contrast is **relative reallocation**, not “larger sites have more penguins.”

A positive H1 result would mean that changing physical island capacity helps determine which nodes carry breeding effort as a regional population changes.

A null H1 result would mean that terrestrial opportunity can change without corresponding demographic redistribution; it would not show that land is irrelevant to nesting at local scales.

## Antarctic-specific alternative: land–sea decoupling

Penguin breeding sites differ from ordinary terrestrial islands because the matrix is simultaneously:

- a movement medium / source of isolation cost;
- the foraging habitat that supplies energy to the breeding colony.

This motivates a second-stage modifier rather than a large environmental search.

### H2
The effect of terrestrial opportunity change depends on marine accessibility during breeding.

Conceptually:

[
D_i = eta_A Delta A_i + eta_M Delta M_i
      + eta_{AM}(Delta A_i 	imes Delta M_i) + ldots
]

where (Delta M_i) is a predeclared marine-access change metric.

Interpretation:

- (eta_A>0): terrestrial opportunity tracking;
- (eta_{AM}>0): newly available land is used preferentially where the marine matrix also remains/becomes accessible;
- (Delta A_i>0) with negative (D_i): direct evidence of physical-habitat expansion without biological expansion.

H2 is opened only if the marine metric passes its own outcome-blind support and identifiability gate.

## Primary demographic estimand

The all-site analysis must remove shared temporal change before asking whether sites gain relative weight.

Preferred model family after support is frozen:

[
log(1+n_{ist}) =
alpha_i + lambda_{g(i),t}
+ eta_{A,s},h_i,	au_t
+ epsilon_{ist},
]

where:

- (n_{ist}) is the observation-calibrated nest-count state;
- (alpha_i) is a site intercept;
- (lambda_{g(i),t}) is the previously support-selected species × regional forcing state;
- (h_i) is the rate of accessible-land change between the frozen optical epochs;
- (	au_t) is centered/scaled time;
- (eta_{A,s}) measures whether sites with greater habitat expansion gain relative to their regional conspecific background.

This parameterization uses unsynchronized records without pretending that every site was counted in every year.

The exact likelihood, observation-error propagation and inferential calibration remain locked until the optical/pixel support roster is known; those choices must be frozen in the later Stage-C outcome contract before count magnitudes are rejoined.

## Compositional cross-check

Where a species × region has a fixed site roster and enough complete seasons, run a secondary direct compositional test using regional site shares:

[
p_{it} = n_{it}/sum_j n_{jt}.
]

Ask whether sites with larger (Delta A_i) gain share from early to late complete seasons.

This is a robustness bridge to Paper 1 / MAPPPD effective-site concentration, not the primary estimator, because complete-season requirements sharply reduce the usable network set.

## Habitat metric

The primary terrestrial exposure is **accessible ice-free breeding opportunity change**, not raw rock exposure.

The pixel pipeline must separate:

1. optical ice/snow versus exposed substrate change;
2. permanent topographic constraints from REMA;
3. coastal/site accessibility QA.

No slope cutoff is chosen from demographic outcomes.

Before a categorical “nestable / not nestable” slope threshold is introduced, it must either:

- come from an independent published biological criterion; or
- remain a sensitivity range, while the primary metric uses exposed substrate without a hand-tuned demographic cutoff.

## External validation

### Positive control
Beaufort Island is a method-validation site because published work independently documented substantial increase in available nesting habitat during glacier retreat.

The image pipeline must recover the **positive direction** of terrestrial opportunity change over the closest supported historical-to-2010 comparison before multi-site habitat-change estimates are treated as trustworthy.

The published Beaufort demographic increase is not used to tune the habitat classifier and is not counted as a new demographic confirmation.

### Secondary geographic QA
Where available, independently mapped Antarctic Peninsula glacier-front retreat can validate the direction of local ice-loss change without using penguin counts.

## Sample gate

The ecological model is opened only after pixel-level terrestrial support is frozen.

Minimum continuation requirements, evaluated without demographic magnitudes:

- at least 30 eligible site × species units;
- at least 20 distinct physical breeding sites;
- at least two Pygoscelis species;
- at least two independent regional groups containing >=5 eligible sites each;
- Beaufort positive-control direction recovered if its imagery passes the optical support gate.

If these conditions fail, no thresholds are relaxed after inspecting counts. The dynamic terrestrial Paper 2D stops and the program moves to the mobile-substrate emperor route.

## What would be genuinely informative?

### Strong island-opportunity tracking
(Delta A>0) predicts positive relative demographic reallocation across regions/species.

### Strong land–sea decoupling
Many sites show (Delta A>0) but negative relative demographic change, and marine accessibility explains the discrepancy better than land opportunity alone.

### Species contingency
Adélie, chinstrap and gentoo differ in (eta_A), showing that identical physical expansion is translated differently by ecological strategy.

### No dynamic terrestrial signal
Even measured change in accessible land fails to explain relative reallocation. This would sharply separate physical breeding capacity from the process driving the Antarctic population redistribution seen in Paper 1.

## Claim boundary

Do not claim that a site with more exposed rock necessarily has more occupied nesting area.

Do not infer individual dispersal from site-share changes.

Do not treat APBP regions as closed demographic populations.

Do not use the same-data static island-trait nulls as evidence for or against the new dynamic opportunity hypothesis.

Do not call a land-only association a test of the full land–sea island model; that requires the separately frozen marine modifier.
