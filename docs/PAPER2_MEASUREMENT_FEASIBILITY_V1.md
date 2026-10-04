# Paper 2 measurement feasibility v1

## Current decision

The direct occupied-breeding-footprint route remains viable and is now preferable to substituting abundance for space.

### Frozen long-term demographic support

The existing outcome-blind bridge contains:

- 107 site × species units;
- 88 distinct breeding sites;
- 44 Adélie, 34 chinstrap and 29 gentoo site × species units.

The new footprint paper begins with Adélie because a validated Landsat guano/colony-extent method exists for that species.

## Independent guano-reference overlap

The frozen 44-site Adélie roster was matched, without demographic magnitudes, to the published Schwaller et al. Landsat-7 classified-pixel dataset (PANGAEA 804588).

At the predeclared 5 km match radius:

- **22 / 44** long-term Adélie sites match a published reference colony;
- the feasibility gate of at least 10 sites and at least two regions passes;
- 22 sites also match at 2 km;
- 24 sites match at 10 km.

### Geographic limitation

The 22 primary matches are not geographically balanced:

- Victoria Land: **21**
- Adélie Land: **1**

Therefore this reference is suitable for **measurement recovery**, not for claiming continent-wide measurement validation.

The correct design is:

1. freeze and evaluate the Landsat guano classifier against the 22 matched published reference sites;
2. quantify the minimum detectable footprint change under that recovery test;
3. keep all demographic outcomes locked;
4. apply the frozen classifier to other supported sites without retuning;
5. report geographic transfer explicitly rather than blending recovery and application sites.

## West Antarctic sanity check

The Schwaller reference contributes little direct validation on the western Antarctic Peninsula.

An independent published Torgersen reconstruction provides a geographically separate check on the biological quantity of interest: historical subcolony perimeters were reconstructed for 1998/99, active subcolonies were delineated from 2020 drone imagery, and 2022 active subcolonies were walked by GPS. This is a useful western-Antarctic **sanity check**, but one site cannot replace broad classifier validation.

The new Landsat method should therefore be required to reproduce the direction and approximate scale of the known Torgersen footprint loss without parameter retuning once the classifier is frozen.

## What this changes scientifically

The intended Paper 2 comparison is now:

\[
A_{available,t} \quad \text{versus} \quad A_{occupied,t}
\]

rather than:

\[
A_{available,t} \quad \text{versus} \quad N_t.
\]

This keeps the paper genuinely spatial.

The high-value outcome remains:

\[
\Delta A_{available}>0,\qquad
\Delta A_{occupied}<0.
\]

If observed beyond frozen measurement uncertainty, this would demonstrate that the physical envelope of terrestrial breeding opportunity and the biological envelope of realized breeding space can move in opposite directions.

It would not, by itself, identify the mechanism causing that decoupling.

## Optical archive support result

The first outcome-blind STAC audit closed successfully.

Across the 88 distinct long-term sites:

- **88/88** pass the primary historical-versus-recent Landsat metadata support rule;
- **84/88** pass the stronger Landsat support rule;
- **88/88** have sufficient recent Sentinel-2 metadata support.

Within the 44-site Adélie subset:

- **44/44** pass the primary rule;
- **42/44** pass the strong rule;
- **44/44** pass the Sentinel validation rule.

Thus archive availability is not the limiting step for the direct-space route.

### Why v1 is not the final measurement roster

The v1 audit was deliberately broad (1984–1993 versus 2016–2025) and queried Landsat Level-2 metadata. Method recovery subsequently established that the published Adélie guano classifiers were developed on Landsat-7 ETM+ **top-of-atmosphere reflectance**, with the Antarctic Peninsula implementation using imagery from 1999–2003.

Therefore v1 is retained as successful archive-availability evidence, not as the final occupied-footprint design.

The final support lane must use:

- Adélie only;
- Landsat Collection 2 Level-1;
- an ETM+ reference epoch aligned with the published 1999–2003 classifier;
- a recent OLI/OLI-2 epoch;
- an explicit ETM+ ↔ OLI sensor-harmonization gate before longitudinal footprint change is calculated.

## Next gates

1. recover the published Antarctic Peninsula classifier coefficients and decision rule;
2. audit the 44 Adélie sites at the correct Level-1 ETM+/OLI sensor epochs;
3. freeze and validate the ETM+ ↔ OLI radiometric bridge;
4. run local pixel-level QA;
5. build classifier-recovery benchmarks on the published reference sites;
6. freeze a minimum detectable footprint-change and censoring threshold;
7. use Torgersen as an independent western-Antarctic sanity check;
8. only then measure longitudinal available and occupied area.

No population trend or Paper 1 concentration endpoint is authorized for classifier tuning or site selection.
