# V22 — Independent 2023 identified nests on 2011-consensus historical patches (frozen before 2023 nest-point rows)

Date 2026-10-14. Specific follow-up to V18 and source-limited V21, **exploratory after V18 outcome** but frozen **before opening 2023 original nest-point geometries**. Frozen Ross/Palmer Ecology PR189 unaffected.

## Scientific separation of 2020 and 2023 data

V21 original Hart et al. 2019/20 UAV `ZAVO_2020_Macaroni_coordinates.csv` holds only **730 maca-labeled nests inside a ~105 × 69 m source footprint**. Its 2020 maca nest points had **0 points in the original V18 T**, but 550 were in established 2011/2016 maca polygons. V21's separate `Mixed_species` category had 19,812 points, also 0 within T, and cannot be assigned to maca or chinstrap. **No true 2020 absence** can be claimed outside surveyed footprint, especially at T. This result is a source coverage limitation, not a rejection of 2011→2016 site reuse.

An independent, broader dated aerial survey exists: Ratcliffe, Dickens & Clucas 2026, BAS GIS DOI 10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308. The dataset contains `drone-derived_data/mac aroni_nest_points_2023` [without space, `macaroni_nest_points_2023`], `chinstrap_nest_points_2023`, 2023 species colony-boundary polygons, and `area_outwith_drone_survey_2023` polygon. Images acquired **14 Dec 2023** during incubation, orthomosaic ~1.9–2.7 cm pixels. 2023 nests were semi-automatically classified against manual validation, not independently ground-tagged breeders. Southwest plateau/Stench Point chinstrap nesting areas were not fully surveyed. The separate `chinstrap_outwith_drone_area_2025` MUST NOT be presented as a 2023 observation.

## Preconditions — fail closed

1. Retrieve only officially listed original 2023 files `macaroni_nest_points_2023`, `chinstrap_nest_points_2023`, `macaroni_colony_boundaries_2023`, `chinstrap_colony_boundaries_2023`, `area_outwith_drone_survey_2023`, `zavodovski_coastline_2023`; all original .shp/.shx/.dbf/.prj/.cpg sidecars. Verify publisher host/source file path, bytes, SHA256, original EPSG:32726 and per-shape nonempty validity. Do not download 26.9GB commercial 2023 mosaics.
2. Exact 2023 drone survey mask: map area outside `area_outwith_drone_survey_2023` **within the 2023 coastline polygon**; use as surveyed land ONLY under publisher's definition. Clip V18 original 2011→2016 T cores to that measured survey area, and never treat outside it as an observed zero.
3. Independent same-date species identity QA: at least **90%** of 2023 classed Mac nest-point shapes within `macaroni_colony_boundaries_2023.buffer(5m)` and similarly for chinstrap. Both must have at least 1 valid point. If this fails, STOP (no post-outcome widening). At least 90% of each species within the 2023 land geometry or its 50m buffer. Record duplicate coordinates, point distribution and counts without thinning.
4. Original 2011/2016 T and its 0/1/2/5m interior margin geometries must exactly reproduce V18 pinned areas (T0 ≈ 9,938.357 m², T1 ≈ 7,003.755, T2 ≈ 4,753.571, T5 ≈ 1,216.517) before opening **2023** point outcomes. Same historical 2011 CHPE/MCPE/MIXED source fingerprint must pass; no reassigning MIXED.
5. A 2023 nest is a **single-year detected nesting location**, not tracked survival, lifetime first breeding, chick success, or one statistically independent replicate of settlement. No species substitution causal claim.

## Frozen positive-only endpoints

A. Within (T_{\delta}\cap\mathrm{droneSurveyed2023}\cap\mathrm{land2023}), for margins δ=0,1,2,5m, compute **Macaroni nest-point count, Chinstrap nest-point count, species share of counted labeled nests, per-hectare point density descriptive**, and unique 5m/10m cells. Report surveyed T area and **fraction of original T surviving 2023 coverage exclusion**, separately for each δ.
B. Positive controls, also 2023 surveyed area: (i) `Q=M2011∩M2016` established maca, (ii) `P=C2011∩CHPE∩C2016` minus 2011 historical `MCPE∪MIXED`, baseline established pure chinstrap. Both clipped to the same 2011/2016 cloud-free support, 2023 land and survey mask. Count 2023 Mac/C nest points and report mapped measured area.
C. Island-wide source sanity: 2023 maca and chinstrap nest point totals; fraction within correct 2023 colony polygon ±5 m and within 2023 coastline ±50 m; surveyed-area row accounting. No negative evidence if 2023 survey incomplete.
D. Interpret if T maca positive as **independent dated 2023 nest-location corroboration** for a region jointly labelled pure chinstrap on the same 2011 satellite scene and mapped as maca in Jan 2016. Even if Mac dominates 2023, this does not prove individual movement, competitor displacement, or a causal priority effect. If no Mac observed, report 2023 point-source support and do not infer absence without high independent detection certainty.
E. Report source QA and exact dates. No hypothesis-testing p-values or ecological null without independent habitat access and time-resolved 2011/2016 observations.

This route tests biological site-level presence more directly than overlap of two boundaries, but **still cannot identify the causal mechanism**. The archived V21 zero must not be sold as negative support because 2020 coverage is narrow.
