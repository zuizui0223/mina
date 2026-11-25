# V27 — cross-island, source-aware penguin species terrain filtering (exploratory)

**Frozen 2026-10-26 after V26 original Copernicus source elevation/slope
at 122,139 located nest records succeeded, but BEFORE reading any
per-species elevation or slope summaries.** V20/V21 species positions and
V22 patch responses were already observed, so V27 is exploratory and
not a preregistered independent biological study.

## Falsifiable comparison and expected new ecological information

Are original Adélie versus Chinstrap nest centres preferentially located in
different **relative terrain elevations and slopes** at the local breeding
landscape scale, and does any two-variable rule generalize to a different
physical-island candidate that was not used to fit it?

If model transfer fails, the major V21 conspecific nearest-neighbour excess
may be a spatial-colony mosaic, locally conditioned or historical settlement
pattern rather than a generalizable simple terrestrial slope/elevation filter.
Even success does not prove active habitat choice: available and unoccupied
substrates were not independently surveyed/registered.

## Frozen sample / provenance

Source: original BAS Hart 2022 DOI 10.5285/28222725-c53d-40f4-9350-49c368899f0b,
10 original first-party individual-nest CSVs; 122,139 original located points
across Ashen Hills, Bellingshausen, Beach Point, Hewison Point.
Independent environment: public Copernicus DEM GLO-30 original source
two 2021 COGs and SHA256 pinned by V26. V26 recorded 100% DSM valid
3x3 slopes at every original located point (real DEM sampling only).
Only two original species codes for **primary** comparison:
ADELIE and CHINSTRAP. Ashen Hills' GENTOO and MACARONI (also original
observations) get source-only descriptive environmental profiles, not
an opportunistically fit multi-species classifier chosen post result.
Mixed/unknown original nests and 2022 Zavodovski chinstrap are excluded,
never imputed.

Exactly duplicated UTM nest points within each original source locality
are removed from the primary paired-source modelling as frozen in V21,
without choosing which species should win the tie. Preserve percent
removed (Beach Point original source ~7.7%), original source coordinate
number vs count and georeference QA. No missing environment is imputed,
and report source missing fraction before any model.

## Fixed site and island observable replicates

Original source site labels:
- Ashen Hills → *provisional* Saunders Island, first-party TIFF filename
  05JAN2019;
- Bellingshausen → *provisional* Bellingshausen Island, TIFF filename
  09JAN2020;
- Beach Point and Hewison Point → *same provisional* Thule Island,
  TIFF filename 09JAN2020.

This is **four surveyed localities but at most three parent-island clusters**,
not 122k independent island replicates. Original date filenames alone do
not prove that every source nest CSV was counted from the same exact
area/date as the other species. Original full orthoimagery survey footprints
remain unverified; V25 HTTP byte-range requests were denied.

## Primary source-level descriptive estimands

Within each locality, report nest-weighted original labelled species
median DSM elevation (metres) and slope (degrees), plus
\`Delta_elev = median_Chinstrap - median_Adelie\` and
\`Delta_slope = median_Chinstrap - median_Adelie\`.
Do not convert these medians to species preference for available
nesting habitat. Report one per-locality sample, and one equal-locality
aggregation within Thule (never treat Beach and Hewison as independent
islands). Contrast directions by island; n=3 candidate island groups.

## Fixed cross-island out-of-source generality falsification

Binary original species ADELIE (0), CHINSTRAP (1).
For each of the THREE source-defined candidate parent islands, leave
**all its localities and all nests out** and fit on the remaining
two parent-island groups; do not randomly split individual nests or
leave Beach out while training on Hewison.

- B0: fixed 0.5 class-balanced species predictor, Brier 0.25 by design
  (a rigorous source-frame class-balanced no-terrain control).
- B1: ridge logistic, fixed C=0.3, predictors two only:
  within-locality terrain elevation centred by the **combined A/C
  observed nest-position** median divided by its combined IQR, and
  within-locality 3x3 DEM slope similarly normalised. No interaction,
  degree-n on lat/lon, polynomial, species-specific island intercept
  or tuned spatial radius is allowed.
- No original label leakage in normalizing covariates; per-locality
  terrain location/dispersion uses all source A/C nest positions only,
  without their original species labels.
- Per training locality, weight every original source species to
  **equal 0.5 within the locality**, with physical-island groups also
  equal total weight despite Thule having two surveyed localities.
  Held-out prediction Brier/log loss is weighted equally per
  taxon within each original heldout locality, then averaged
  equally across localities within held-out parent-island group.
- Each species in the held-out island must have ≥100 distinct
  source nest coordinates; all three candidate island groups must
  qualify for complete three-fold test. Otherwise STOP with original
  sample gates, not a source-region cherry-pick.

Primary result: **mean across three parent-island held-out Brier gain**
\`Brier(B0)-Brier(B1)\` and number of distinct source island groups
with positive Brier gain. Positive mean and ≥2/3 improved groups
is at most **exploratory source-supported terrain transfer**; otherwise
source-island-general terrain predictor unsupported. Preserve ALL island
fold values, no nested bootstrap treating individual nests as islands.

This is deliberately a stringent transfer test, not a territorial
competition mechanism. Any result is limited to 3 provisional
South Sandwich physical island groups with only one survey campaign
(2019–2020), uncertain imaging footprints, 30m DSM resolution and
no independently surveyed unoccupied rocky breeding habitat.
No cross-taxon or polar-continental universality or seabird dispersal
law may be inferred.

## Next independent test if transfer succeeds

Only after primary 3-source-island transfer result is frozen, report
locally source-environment matched A/C patches (e.g. both-species
100m cells) without reselecting DEM windows, and seek a truly
independent Antarctica-continent/GLO30 habitat available-patch survey.
If it fails, preserve failure rather than fitting one model per island
or reverse-selecting the sign to tell a favorable story.
