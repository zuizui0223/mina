# Antarctic penguin abandonment → terrestrial greening: identifiable event study (v1)

**Research status:** 2026-10-29 post-exploration *design and feasibility contract*. The ecological effect has **not** been estimated. Adds a single focused test to draft PR #206; does not alter frozen Paper 1 (#189), Paper 2 (#199), or seabird branch (#201). This design was developed after viewing colony counts and spatial associations: it is **not** a preregistered independent confirmation.

## Central question and competing processes

> Does historical penguin occupation change the terrestrial greening response to warming, and is vegetation recovery faster *after* breeding abandonment than at matched never-occupied ground?

Do **not** assume a universal, south-moving, three-element “front.” Warming may act on both vegetation and ice-dependent birds; sea-ice changes can alter prey/access rather than physically drive individual birds south. Colony loss does not prove emigration. Penguin guano supplies marine-derived nutrients but living colonies can inhibit plants through trampling and excessive nutrients. The hypothesized post-abandonment release therefore concerns a **conditional response** on previously occupied, independently located ground, not all warming sites.

Three distinguishable explanations:
- **Common climate only (C0):** within island and matched terrain, never-occupied and abandoned plots change together with melt duration / temperature / precipitation and observation support.
- **Legacy + trampling release (H1):** after independently verified local breeding abandonment, historically occupied plots show greater *validated terrestrial plant-cover* change than comparable never-occupied plots; event-study leads are approximately flat before abandonment. Soil/plant marine-derived nitrogen evidence is needed for a guano-specific mechanism.
- **Species or substrate replacement (H2):** Gentoo/other birds reoccupy nearby suitable substrates or other disturbance/snow regimes change, explaining local vegetation differences independently of Adélie abandonment. Do not classify a plot as abandoned merely because ADPE falls if another species nests there.

## Verified existing source support (do not upscale units)

Source: fixed `research/climate-penguin/outputs/comparison_audit/palmer_five_island_counts.csv`, `palmer_site_coordinates.csv`, `mapppd_zero_episodes.csv`, `vegetation_2km_mapped_area.csv`, and `outputs/climate_penguin/satellite_multiscene_common_support.csv`.

| Palmer monitoring island | 1991 counted pairs | 2007 | 2017 | 2017 observed zero? |
|---|---:|---:|---:|---|
| Litchfield (LITC / LIT) | 497 | 0 | 0 | yes |
| Humble (HUMB / HUM) | 1,085 | 178 | 68 | no |
| Torgersen (TORG / TOR) | 3,016 | 246 | 22 | no |
| Christine (CHIS / CHR) | 1,410 | 329 | 27 | no |
| Cormorant (CORM / COR) | 681 | 94 | 23 | no |

**Independent candidate-screen check:** `mapppd_zero_episodes.csv` has **8 ADPE site-level observed-zero episodes** (CBAR, CORN, FITC, HANN, LAUF, LITC, SEPR, STEN), not eight verified local extinctions. Two (CORN, SEPR) have a recorded later reappearance; several have only a single zero survey after a multi-year gap. Of the eight, **only LITC** passes the existing fixed ≥5-season, ≥10-year long-term candidate rule. None of the other seven can simply be promoted to an independent confirmed-abandonment time-series replicate. This does not rule out finding more subcolony-level events with separately verified original surveys and polygon histories.\n\nLitchfield: 2006 = 4 monitored breeding pairs; 2007–2017 = **11 successive observed zeros**, rather than treating all future unobserved years as zero. The MAPPPD state table only independently has zero records in 2007/2008; do not count it as an independent second dataset. “Zero” applies to monitored census units; island-wide physical absence outside the census footprint remains unverified.

Distances from Litchfield recorded coordinate: Humble **0.710 km**, Torgersen **0.882 km**, Christine **4.180 km**, Cormorant **6.464 km**. A 2 km radius necessarily overlaps other islands and is **not** a unit-specific colony-area estimand. The mapped 2017–2023 composite Vegetation+Lichen detection within Litchfield's 2 km circle is about **227,620 m²**, *not measured growth, percent cover, Litchfield's own plants, or a historical pretreatment value*. Zero mapped pixels elsewhere cannot be called true plant absence.

Sentinel-2 *January* 2019/2024 existing local multiscene comparison: Litchfield `loc024` has `common_land_once_pixels=0` (0/1,976 fixed-circle pixels), and 2019 has no clear-land pixels in the audited product; 2024 has some. Its two-date NDVI **cannot be estimated under current common-support gate**. Expand a **fixed February–March seasonal window** and then test Landsat history separately; do not select dates by the sign of resulting NDVI. The 7-site 2019/2024 NDVI pilot does not include Litchfield.

Published 2025 Palmer spatial audit (in `outputs/spatial_feasibility/palmer_audit.md`) documents **23 historic Torgersen subcolony polygons, 18 classified extinct, five active** in published Fig. 5, but no census-code-to-polygon crosswalk nor verified re-use of raw georeferenced imagery in this repository. They are potential within-island spatial contrasts, **not 23 independent islands or established vegetation histories**.

## Frozen analysis sequence and gates

1. **Define geographic units before any vegetation outcome.** Acquire historic and recent georeferenced colony/subcolony polygons for Litchfield and Torgersen, geolocate census extents with uncertainties, map coast/ice-free land per date. A MAPPPD point or an overlapping 2 km buffer never substitutes for a colony footprint. Separate historical colony core, 0–50 m peripheral marine-nutrient zone, matched never-colony terrain, and maintained neighboring colony. Candidate distances are design parameters only, not an empirical ammonia plume scale.
2. **Confirm biological transition.** Use dated counts, distinct observation methods, actual on-ground extirpation of that patch, and whether Gentoo, chinstrap, seals or other birds occupy the same footprint. Report last positive season and first independently surveyed zero, left/right censoring, and actual survey coverage. Litchfield's monitored zero starts in 2007; for subcolonies, exact individual abandonment years must be established or treated as interval-censored. Decline without absence is a separate exposure.
3. **Audit imagery support without looking at trend signs.** Use harmonized Landsat (1986 onward, 30 m) **only where the plot is resolvable** and Sentinel-2 (2015 onward, 10/20 m). Match fixed austral late-summer windows across years, sensor, view, snow/ice, shadow, tide/water and solar angle. Establish a constant terrestrial pixel support mask and record per-site-year clear observations; report unequal observation opportunity and coverage. Minimum temporal comparison: at least 3 interpretable austral summers *before* and 3 *after* a documented patch-level event, plus plot pixels independent of boundary uncertainty. If historic plots are smaller than resolvable pixels, report **NOT ESTIMABLE**, not an island-level proxy.
4. **Calibrate vegetation rather than threshold NDVI alone.** Independent high-resolution imagery / field ground truth must discriminate moss, vascular plant, lichen, terrestrial algae, snow algae, guano, bare soil, rock and snow. Use plant class area or fractional cover among observable ice-free ground as the **primary outcome**, raw harmonized NDVI and TCG as diagnostics. `SCL4/5` is a clear-land mask, not moss validation. A 2017–2023 composite is a single-period *reference*, not pre/post change.
5. **Compare events within matched geography, preserving clustering.** For each dated abandoned footprint, match never-occupied control plots within the same island / local climatic zone on elevation, slope, aspect, melt exposure, distance to coast, baseline plant cover and satellite completeness; add maintained historic colony patches to separate direct disturbance from persistent guano legacy. Estimate an event-time plot-level contrast `Y_{plot,t} = plot FE + island×year FE + Σ event-bin×historic-occupied + snow/observation controls + error`. The event bins and reference years must be fixed before outcome inspection. Test **pre-event leads** and never-treated placebo dates. An isolated Litchfield event is a case study, not population-level independent replication; Torgersen patches cluster within island and cannot supply independent island-level degrees of freedom.
6. **Mechanism and external validation.** Only after a reliable post-abandonment plant response is observed, test soil N/P, plant δ15N or other source-specific nutrient evidence and residual colony trampling/occupation. Examine same-place time lag, local sea-ice timing, and climate/ice covariation separately. A guano-specific conclusion needs nutrient measurements, not vegetation-color change alone. Multiple externally replicated island/colony events are required to generalize the hypothesized moving front.

## A priori result interpretation for the NEXT (new) imagery analysis

- **H1 supported provisionally:** post-event terrestrial vegetation-cover increase in historic colony plots exceeds *within-island matched controls*, after comparable pre-event trajectories and held observation quality; biological source of nitrogen then remains to be established.
- **C0 favored:** no differential post-event response on supported comparable plots, even if both green as warming progresses. An imprecise null is inconclusive, not proof of no effect.
- **Reverse temporal order:** reliable greening precedes first confirmed abandonment / trend already differs before the event: reject the proposed local abandonment-triggered sequence, investigate shared climate and potential reverse causation.
- **Unidentifiable:** no same-place pretreatment imagery, unverifiable colony polygons, too few usable years, or confounding by replacement breeders. Do not compute selective site-level significance from NDVI, and do not claim a penguin-caused continental front.

## Next operational work

**P0:** original historical footprint georeferencing for Litchfield and Torgersen; test seasonal Landsat pre/post image support and 2018–2025 Sentinel support with an *outcome-blind* availability table. This precedes any new “greening” effect calculation.

**P1:** once gates pass, extend candidate discovery to multiple genuinely independent abandoned colonies, keep the single Litchfield case separately, and examine Gentoo replacement as a secondary, species-aware alternative rather than treating its +0.61 exploratory correlation as confirmation.

## External scientific anchors (not new findings from mina)

- Roland et al. (2024), Antarctic Peninsula Landsat greenness 1986–2021, https://doi.org/10.1038/s41561-024-01564-5
- Bokhorst et al. (2026), biological realism/coverage criticism, https://doi.org/10.1038/s41561-026-02076-0
- Roland et al. (2026), response, https://doi.org/10.1038/s41561-026-02080-4
- Robinson et al. (2023), ancient abandoned Adélie guano and moss nutrient legacy review, https://doi.org/10.1007/s11120-023-01040-y
- Walshaw et al. (2024), Antarctic composite vegetation baseline, https://doi.org/10.1038/s41561-024-01492-4

**No plant-cover time series, post-abandonment treatment effect, sea-ice-caused emigration, or nitrogen source has been measured by this contract.**
