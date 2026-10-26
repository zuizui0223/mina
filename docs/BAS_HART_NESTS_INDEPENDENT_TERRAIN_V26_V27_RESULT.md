# South Sandwich penguin nesting terrain — V26–V27 original-data result

**2026-10-26. Exploratory ecological cross-island comparison, not a proven
island-mediated causal mechanism.** This is a new analysis of first-party
nest coordinates and independent topography, not a meta-analysis of published
paper coefficients.

## Original primary and environmental data

Original UK Polar Data Centre Hart 2019–20 penguin nest coordinate archive,
DOI 10.5285/28222725-c53d-40f4-9350-49c368899f0b: 10 species-labelled
source CSVs, 4 survey localities, at most 3 *candidate* parent physical islands.
Of 122,170 original numbered nest records, 31 had no coordinates;
**122,139** located original nest centres were mapped to EPSG:32726.
Source species labels do NOT count unknown, mixed, unvisited or 2022 Zavodovski
chinstrap as a 2019–20 observed nest.

Independent 2021 Copernicus DEM GLO-30 Public surface DSM,
DOI 10.5270/ESA-c5d3d65, primary original two tiles:
S58 W027 SHA256 8e235dd28bab594ed33f080d777bb48eec3be41954414eda6eef4caf78f4716c;
S60 W028 SHA256 a232586ae96f00661ea89d1ce110aec9ac9a027c9c447d6a5aeed1f66b50ef30.
Original AWS tile list SHA256
10604e3052c98a09e9216f1a8f0a555a04148419757575f783d4937fd44316dc.

Real first-party source acquisition and metric sampling at **all 122,139**
georeferenced nest centres succeeded. Locality-wide original DSM elevation
medians: Ashen Hills 35.58m, Bellingshausen 27.49m, Beach Point 15.16m,
Hewison Point 17.19m. Local 3x3 DEM slope medians: 14.81°, 18.75°,
5.51°, 4.54°, respectively.

Source original V26 QA receipt:
results/BAS_HART_INDEPENDENT_COPDEM_TERRAIN_V26.json.
Execution: https://github.com/zuizui0223/mina/actions/runs/40279185790 .

## Source-independent geography × original species result

Exact source duplicate nest coordinates excluded before the V27 comparison,
using the original V21 rule (10% source duplicate ceiling). The primary
binary two-taxon cohort was Adélie versus Chinstrap at the **four
pre-selected surveyed localities**. Additional Gentoo and Macaroni in
Ashen Hills are kept as descriptive third/fourth species, not
selectively included in a fitted effect model.

| Original site | Candidate island | Adélie median DEM elevation | Chinstrap median | Chinstrap minus Adélie | Median slope difference |
|---|---|---:|---:|---:|---:|
| Ashen Hills | Saunders | 32.04 m | 45.70 m | +13.66 m | +0.50° |
| Bellingshausen | Bellingshausen | 21.89 m | 61.19 m | +39.30 m | -0.32° |
| Beach Point | Thule | 15.61 m | 14.18 m | -1.43 m | +0.73° |
| Hewison Point | Thule | 18.93 m | 16.08 m | -2.85 m | +2.48° |

At Ashen Hills, Gentoo nesting-point DEM median was 1.49m (n=712
after duplicate removal), and Macaroni slope median was 25.32°
(n=1,411). The near-zero Gentoo elevations may reflect coastal DEM
pixel ambiguity and are not automatically true ground nest altitudes.

These within-survey-site differences are observable independent
DEM associations; the negative 1–3m Thule differences are small
relative to potential DEM/regional georegistration uncertainty, and
should not be presented as proof of ecological niche reversal.

## Transfer test: whole candidate physical islands held out

V27 method fixed before inspecting per-species terrain values, but
earlier V21/V22 species nesting-point patterns were known (EXPLORATORY).
Ridge logistic C=0.3 with two predictors only: per-site combined A/C
observed-point median/IQR-normalized elevation and DEM slope.
Equal source locality and species weighting, physical-island groups
strictly held out together. Baseline B0 predicts p=0.5 for both
original species and has class-balanced Brier=0.25.

| Held-out original island group | B0 Brier | B1 elevation+slope Brier | Gain B0 minus B1 |
|---|---:|---:|---:|
| Saunders | .2500 | .245848 | +.004152 |
| Bellingshausen | .2500 | .252082 | -.002082 |
| Thule (Beach and Hewison both held out) | .2500 | .373720 | -.123720 |

**Only 1 of 3 candidate island groups improves**. The original
three-island-equal-weight Brier gain is **-0.04055**.
Therefore a simple, transportable elevation+slope rule for Adélie versus
Chinstrap nesting identity is **NOT supported**.

V27 original source QA/real model result:
results/BAS_HART_ORIGINAL_COPDEM_TERRAIN_TRANSFER_V27.json.
Reproduction: https://github.com/zuizui0223/mina/actions/runs/40280146558 .

## Integrated ecology: what survives and what does not

V21 independent nest coordinates display strong local source species
neighbour assortativity at <=10m. V22 source geography-constrained
100m/25m/500m label controls show that the broad source colony-patch
mosaic accounts for much of the site-wide free-label effect, and
100m residuals are partly sensitive to chosen spatial grid phases.
V27 establishes that **independently measured terrain predictors
cannot transfer between the three parent island groups**.

Thus the current best *exploratory working hypothesis* is that
penguin nest species assemblages are strongly spatially organised
in local source patches, with island/context-dependent correspondence
to coarse mapped terrain, rather than a universal slope/elevation niche.
These source datasets cannot distinguish environmental filtering,
persistent colonial settlement, interspecific competition, photo/search
mask design or natal site fidelity.

Causal inference is explicitly prohibited: only one 2019/20 source
campaign; at most three parent physical islands (gazetteer-provisional);
122k nest points are NOT 122k ecological or island replicates;
source full surveyed-empty nesting-substrate and common UAV footprint
not independently verified. The DEM is static 2021 surface elevation
at ~30m scale while observed nest-neighbour distance is ~0.5–0.75m.

**Terminal decision for this exact source terrain test:** do not rescue
failed three-island heldout prediction by retuning terrain variables,
projections, signed taxon contrast, source grid, model degree or sample.
To test a genuinely Antarctic archipelago-wide island/ice mechanism,
add field-verified independently observed *multiple* years and regions
with true physical island identity, visited empty patches, landscape
ice/rock history and per-survey nest abundance/effort. The related
Zavodovski PR #196 is a distinct paused exploratory original source
and cannot be represented as a new independent 2019/20 survey.
