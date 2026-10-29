# Palmer abandonment–greening: authentic observation gate and spectral check (2026-10-29)

**Status: executed original-source measurements. The biological event-study remains UNIDENTIFIED.** These runs are all post-exploration feasibility/diagnostic analyses. They are **not** replicated Antarctic greening results, soil-nutrient results, or evidence of a southward penguin migration mechanism. Frozen Paper 1 (#189), Paper 2 (#199) and seabird tests (#201) have not been changed.

## 1. Why this P0 check exists

Litchfield Island has positive breeding-pair counts through season 2006 (four pairs in that year), followed by eleven monitored zeros from 2007–2017. February–March imagery in calendar year 2007 represents the end of season 2006/07; calendar year 2008 represents season 2007/08. The 2017–2023 Plantarctica map is a **single composite** and cannot establish vegetation increased after the 2007 zero.

The geographic unit cannot be a 2 km radius, which overlaps Humble and Torgersen. The coordinates in the following calculations are fixed EPSG:3031 **25-point grids in a ±80 m neighborhood of each MAPPPD site coordinate, spaced at 40 m**. They are not historical penguin colony boundaries or an independent non-colony control.

## 2. Fixed February–March original-image support, all available 1986–2026 years

**Source-original completed GitHub run:** [Actions #40860032303](https://github.com/zuizui0223/mina/actions/runs/40860032303), artifact **#12890938282**, ZIP SHA256 \`08d5759e9577548aea0214e9df617e2f90929a92ec2a8b85e4fa92a3ad55769f\`.

- 406 original Landsat Collection 2 Level 2 QA_PIXEL scenes from the prespecified regional catalog, **1,218 site×scene reads** (three sites), **123 site×calendar-year rows**, **0 source asset read errors**.
- The audit examines each year's full scene list. Missing years remain missing; an observed no-clear source year is not absence of vegetation.
- For each of 25 *fixed geographic positions*, a summer counts as observed only when at least one scene's QA excludes fill, dilated cloud, cirrus (conservative), cloud, shadow, snow and water. Three scenes in one summer are **one** observed summer, not three independent years.
- Pre = calendar 1986–2007; post = 2008–2026. This alignment describes **Litchfield's** first monitored absence, not a common abandonment event in Humble/Torgersen.

| Registered island grid | Pre summers with ≥1 QA-clear fixed point | Post summers with ≥1 QA-clear fixed point | Fixed positions with ≥3 pre summers AND ≥3 post summers |
|---|---:|---:|---:|
| Litchfield | **7** (1989, 1991, 2001, 2003, 2004, 2006, 2007) | **16** (2009, 2011–2016, 2018–2026) | **25 / 25** |
| Humble | **8** | **14** | **25 / 25** |
| Torgersen | **5** | **15** | **13 / 25** |

Independent container-side recomputation of every per-position pre/post year count from the complete artifact agreed with the saved source JSON at all three grids. This clears a **fixed-point repeated-imagery observational support criterion**, NOT the required **verified historical-colony-plot** or terrestrial vegetation measurement criteria. The 2008 **February–March** first-post-zero year still has **zero** locally QA-clear fixed points in the catalog's only image. The early post 2009 and 2011 scenes are later than immediate abandonment; a lagged response remains possible but cannot be inferred from scene availability.

Original code: \`work/abandonment/palmer_annual_qa_support.py\`; deterministic tests: \`tests/test_palmer_annual_qa_support.py\`; run output: \`local_qa_scenes.csv\`, \`local_qa_years.csv\`, \`checks.json\`.

## 3. Separately labeled post-hoc January 2007/2008 same-position source gate

The earlier 2008 February–March cloud failure motivated a **post-hoc January QA search**, explicitly *without looking at vegetation or NDVI outcomes*. The single January 2007/2008 pair selected by maximizing shared QA-clear *same EPSG:3031 ground-point positions* (then minimizing calendar-day mismatch) was:

- 2007-01-05 \`LE07_L2SR_218106_20070105_02_T2\`;
- 2008-01-15 \`LE07_L2SR_219105_20080115_02_T2\`.

**Original source run:** [Actions #40860491682](https://github.com/zuizui0223/mina/actions/runs/40860491682), artifact **#12891152497**, ZIP SHA256 \`bb386e7ca78d735b7395f5c99a617c7d3462da02258b70792b77156a8f791c62\`. The 27 source scene×site reads and 675 fixed-ground-point QA records contained no read failures. A separate check reconstructed selected intersecting sets from the raw per-point CSV, agreeing with the JSON:
- Litchfield: **7/25** shared clear-ground positions, index \`9,11,15,16,20,22,23\`;
- Torgersen: **3/25**, \`9,12,13\`;
- Humble: **0/25** in January 2007/08.

This demonstrates that the **entire 2007/08 breeding season** must not be called unobservable merely because the isolated **March 2008** source was cloudy. Nevertheless, this is a post-result observational window revision, not independent confirmation; all future years must use a comparably defined season window.

## 4. First preselected Landsat 7 red/NIR *spectral* pilot — completed but NOT vegetation

**Original source run:** [Actions #40861183313](https://github.com/zuizui0223/mina/actions/runs/40861183313), artifact **#12891691538**, ZIP SHA256 \`e0fda5f9a38d882dbef1efbd84c69dd79f555157a888b20a4816db8a1db9cdc4\`. Source \`checks.json\` SHA256 \`5168aa038b28d7f796da456a6bfcde6ce23d05c4e9e615d03a29c5ad0388abb1\`; per-point CSV SHA256 \`3581df249c81a8394b46ab5548f2961b2c7ef7709ccb9ea09de769a5504ec0c8\`.

**Crucial separation:** January scenes and shared 7/3 point sets were frozen by the independent QA-only run *before* red/NIR source values were retrieved; their selection used no NDVI. This is still an exploratory post-hoc feasibility pilot.

- Sensor: same Landsat 7 ETM+, 2007-01-05 and 2008-01-15 (10-day calendar-day mismatch).
- Genuine USGS Landsat C2 L2 surface reflectance: \`SR = DN×0.0000275 − 0.2\`, retain DN in 7273–43636; QA_PIXEL and band-specific QA_RADSAT filters.
- Both pre/post red and NIR are radiometrically usable at **7/7 Litchfield** and **3/3 Torgersen** preselected same-coordinate positions. Zero saturation flags for these points.
- **Litchfield: exploratory median ΔNDVI (2008 − 2007) = −0.1436955 (range −0.1979302 to −0.0514676), 7/7 point values negative**.
- **Torgersen: median ΔNDVI = −0.0319485 (range −0.0586420 to +0.0702734), two negative and one positive**.

All per-point NDVI values were independently recomputed from the **original downloaded red/NIR integer DN columns** using the same USGS scaling rule and matched to the archived CSV to within numerical tolerance. **No plant-cover change, moss expansion/contraction, guano legacy, Antarctic greening slope, before/after causal effect, or statistically independent n=7 result may be claimed from these figures.** NDVI is sensitive to spectral rock/guano/soil conditions, moisture, atmospheric residuals, native 30m pixel misregistration and local melt state. The source grid is not the location of known historical nesting cores. One spectral pair lacks controls and pre-event trend; a drop in this pilot neither confirms nor falsifies eventual delayed colonization by vegetation.

Original code \`work/abandonment/palmer_january_spectral_probe.py\`; tests \`tests/test_palmer_january_spectral_probe.py\`; artifact rows \`original_paired_spectra.csv\`. USGS product scaling source: https://www.usgs.gov/faqs/how-do-i-use-a-scale-factor-landsat-level-2-science-products .

## 5. What remains before the ecological hypothesis is identifiable

1. **Reconstruct and verify nesting footprints, first.** Cimino et al. (2025, DOI:10.1007/s10980-025-02088-y) digitized 1998/99 Torgersen subcolony perimeters from the Patterson map and tracked five of 23 subcolonies active in 2022. Those authenticated polygons and matched census-code crosswalk are not present in the repository. Their historic extinct extents of about 212–3433 m² are frequently at or below a few 30m Landsat pixels. Litchfield's registered island point is likewise **not an independently digitized historical nest polygon**.
2. **Co-measure true counterfactual land.** Within the same island or microclimatic neighborhood, select never-occupied and maintained-colony areas *before opening their vegetation outcomes*; evaluate slope, aspect, elevation, snow-free duration, distance to shoreline, seal and other bird use, and sensor observation support.
3. **Validate terrestrial vegetation itself.** Multi-date red/NIR/other bands must be validated against independent high-resolution original imagery, field ecology or published vegetation polygons; bare dark rock, residual guano, lichen, moss and snow algae must not be collapsed into 'greening'.
4. **Only then fit event-time effects.** Need at least three interpretable plotted summers before and after independently dated **patch** abandonment and nondivergent pretrends. Islands or distinct, historically verified plots are clustering units, not 25 sensor points. Warming and sea-ice history enter as time- and geography-controlled co-exposures; temperatures and ice changes are not independent random treatments.
5. **Check nutrient mechanism last.** A plant signal on formerly occupied soil does not itself establish fertilization; source-specific soil nitrogen/phosphorus or isotope evidence and absence of ongoing trampling are separate requirements.

**Scientific decision:** source discovery PASS, repeated fixed-location *QA availability* PASS, January single-pair spectral measurement COMPLETE (negative in Litchfield point grid, noncausal), **historical footprint × validated vegetation response × adequate controls still HOLD**. Preserve this hypothesis without claiming an Antarctic Peninsula 'green in the penguins' wake' front.
