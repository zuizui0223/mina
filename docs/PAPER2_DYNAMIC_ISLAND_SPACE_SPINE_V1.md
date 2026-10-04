# Paper 2 spine v1 — when habitat expands but breeding space contracts

**Status:** prospective island-ecology extension. Measurement support is being audited without demographic outcomes.

## Core question

> **Can an Antarctic breeding landscape become physically more available while the penguin population uses progressively less of it?**

Paper 1 established a bounded spatial form of decline: breeding effort can become disproportionately concentrated among fewer effective monitored components. Paper 2 asks what kind of island process can generate or constrain that spatial contraction.

The Antarctic advantage is that terrestrial breeding opportunity is not fixed. Deglaciation can create new ice-free ground, while the marine environment supplying food changes independently. This separates three quantities that are often conflated in island population studies:

1. **physical opportunity** — how much accessible terrestrial breeding space exists;
2. **realized occupation** — how much of that space is actively used for breeding;
3. **population abundance** — how many breeders occupy the realized space.

## Primary state variables

### Available breeding opportunity

\[
A_{available,t}
\]

Accessible ice-free terrestrial area around a frozen breeding-site anchor, derived from harmonized optical imagery and an outcome-blind accessibility mask.

This is not total island area. Raw newly exposed rock is not automatically usable nesting habitat.

### Realized breeding footprint

\[
A_{occupied,t}
\]

Active Adélie breeding/guano footprint retrieved from the same primary Landsat sensor family and processing logic across epochs.

This is a direct spatial state and is therefore preferred to substituting abundance for breeding space.

### Abundance

\[
N_t
\]

MAPPPD breeding-pair abundance is reserved for a later, separately frozen validation/interpretation stage. It cannot determine site eligibility, imagery selection, classifier tuning or change thresholds.

## Competing hypotheses

### H1 — opportunity tracking

New accessible land is occupied as terrestrial opportunity expands.

Prediction:

\[
\Delta A_{available} > 0
\Rightarrow
\Delta A_{occupied} \ge 0
\]

after allowing for frozen measurement error.

This is compatible with the Beaufort Island precedent, where deglaciation increased available nesting habitat and Adélie population use expanded.

### H2 — land–population spatial decoupling

Physical breeding opportunity expands, but realized breeding space contracts.

Critical pattern:

\[
\Delta A_{available} > 0
\quad \text{and} \quad
\Delta A_{occupied} < 0.
\]

This is the most distinctive Antarctic island-ecology outcome. It would show that physical island opportunity can increase while biological use of the island shrinks.

It would **not** by itself identify marine limitation. Marine forcing, social fidelity, demography, snow, microtopography and other processes remain candidate explanations.

### H3 — coupled land–sea constraint

Expansion of realized breeding space depends on both terrestrial opportunity and the surrounding marine matrix.

After the two spatial quantities are measured independently, a separately frozen second-stage analysis may test whether marine conditions explain residual variation in \(\Delta A_{occupied}\) conditional on \(\Delta A_{available}\).

The marine predictor set must be small and biologically prespecified. No broad environmental screen is permitted.

## Primary taxon

The first implementation is Adélie penguin only.

This restriction is measurement-based, not outcome-based:

- continental Landsat retrieval of Adélie guano/colony extent has published validation;
- guano-area–abundance relationships have been independently evaluated;
- equivalent measurement error is not assumed for chinstrap or gentoo;
- cross-species expansion requires a separate measurement-recovery gate.

## Evidence sequence

### Gate A — temporal imagery support

For the frozen long-term site roster, establish whether early and recent Landsat support exists under predeclared epochs and scene/year minima.

No habitat change is calculated.

### Gate B — independent footprint-reference overlap

Determine which frozen long-term Adélie sites overlap the published Schwaller et al. Landsat-7 guano-pixel reference.

No new classifier is tuned and no demographic result is read.

### Gate C — pixel-level image quality

At sites passing metadata support, use QA bits and local windows to determine whether enough clear, non-shadowed pixels exist in each epoch.

Scene-level cloud cover alone is insufficient.

### Gate D — measurement recovery

Before estimating temporal change, demonstrate that a frozen guano classifier can recover independent published colony footprints to a predeclared accuracy and that the ice-free opportunity classifier recovers known exposed ground.

This gate must also establish a minimum detectable change.

### Gate E — frozen longitudinal measurement

Only after A–D pass, compute:

- \(\Delta A_{available}\);
- \(\Delta A_{occupied}\);
- their measurement uncertainty.

### Gate F — ecological outcome test

Freeze the sign/uncertainty rule for opportunity tracking versus decoupling, then open the spatial-change results.

MAPPPD abundance and marine covariates remain locked until this spatial test is closed.

## What would be genuinely new?

The novelty is **not** that glaciers retreat, that penguin colonies change, or that guano can be seen from satellites. All are established.

The stronger contribution would be demonstrating a mismatch between two moving spatial envelopes:

> **the physical envelope of possible breeding space and the biological envelope of realized breeding space can move in opposite directions.**

This reframes island area as a dynamic opportunity surface rather than a fixed predictor.

## Relationship to classical island ecology

A static formulation asks whether population state depends on island area and isolation:

\[
P = f(A, I).
\]

The Antarctic formulation makes both the habitat and matrix dynamic:

\[
A_{occupied,t}
=
f(A_{available,t}, M_t, C_t, S_t),
\]

where:

- \(M_t\): marine resource/access state;
- \(C_t\): functional connectivity among breeding sites;
- \(S_t\): spatial/social memory such as site fidelity and established colony structure.

The program therefore asks not merely whether large islands hold larger populations, but **whether changes in physical island opportunity are translated into changes in realized biological space**.

## Claim boundaries

- Do not call all Antarctic sites literal islands.
- Do not equate \(A_{occupied}\) with Paper 1 effective component number \(E\).
- Do not infer marine causation from land–occupation decoupling alone.
- Do not tune remote-sensing thresholds using population trend.
- Do not pool chinstrap or gentoo until their footprint measurement error is independently validated.
- Do not interpret 30 m boundary changes below the frozen detectable-change threshold.

## Stop rule

If a sufficiently broad long-term Adélie sample cannot recover both available-area and occupied-footprint change above frozen measurement error, Paper 2 stops as a longitudinal footprint paper. It is not rescued by replacing occupied area with abundance after seeing demographic outcomes.
