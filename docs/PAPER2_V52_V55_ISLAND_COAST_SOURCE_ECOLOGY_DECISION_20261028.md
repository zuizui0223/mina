# Paper 2 source-based ecological result — coastal geography beyond local elevation and slope (V52–V55)

2026-10-28 | **original-data exploratory result** | 2019–20 BAS/Hart South Sandwich penguin nests + independent BAS/SCAR 2020 official coast

## Main study: asymmetric access to breeding islands

**Integrated hypothesis:** islands simultaneously protect seabird breeders from some terrestrial mammalian predators and create shore-to-nest access limitations for flightless marine breeders. The hypothesis is about a **predator access × breeder access mismatch**, not the mere existence of island isolation or a generic negative abundance–habitat correlation.

**What is measured TODAY:** only a component: the relation between independent coastal MAP geometry and the distribution of geolocated breeding nests of two *flightless* penguin species. No flying-bird nests or terrestrial mammalian status in this BAS sample. No shore-to-nest actual walk/landing trajectory, available empty nesting habitats or continuous annual field surveys. It cannot identify the integrated predation/flight effect.

## What the actual original new source proves

Original BAS/Hart first-party 2019–20 nest coordinate and CopDEM sample NPZ SHA `1566f4fef4ac5370f40f6482e9f76f7b252e32ade8915a190cf0d2fc946883ec`, 122,139 geolocated original nest points in four locations nested in three actual separately polygon-mapped islands. Original independent BAS/SCAR 2020 sub-Antarctic coast DOI 10.5285/c1d83502-8799-4e3c-bdca-21db6a4405d4 ZIP SHA `27b4cd2085b9c845abf7928c336cf82f0d37492bbe2c21522ac4c670750f6cff` yields three independently identified source original physical polygons:
- Saunders 37.93 km² (source polygon index 458);
- Bellingshausen 1.56 km² (451);
- Thule 16.74 km² (450).

**Source limitation:** original coordinate strict inclusion on the 2020 coast: Ashen 96.87%, Bellingshausen 95.47%, Beach 100%, Hewison only 85.64%. Source gate V51/V52 stipulated >=95% in EVERY location; therefore `shoreline-as-actual-walkable-land` **stays STOP**. All 3221 Hewison off-polygon original nest coordinates are within 39.3m of official coast, 98.5% within 30m, median 8.0m (V53). This suggests bounded georeference/cartographic mismatch but does not validate the original real nesting-land or path assumption.

## New species-location predictive information

Fixed original species comparison of original Adélie vs chinstrap NEST centres; real-island-out cross-validation leaves all localities of the held-out island outside training, including both Thule localities; compare fixed logistic B1 original independent source DEM elevation+slope with B2 adding `log1p(unsigned original 2020 coast map distance)`; C=0.3; train-island-only median/IQR standardization; held-out class-balanced site Brier with island/equal-site averaging.

| Held out real island | B1 original nest source | B2 + original coast proximity | Improvement |
| --- | ---: | ---: | ---: |
| Saunders | 0.277671 | 0.235903 | +0.041768 |
| Bellingshausen | 0.212095 | 0.187285 | +0.024810 |
| Thule (2 original sites equally weighted) | 0.397991 | 0.309730 | +0.088262 |
| **3-source-island equal mean gain** | — | — | **+0.051613** |

This meets the pre-fixed V54 **2/3 islands improving and mean gain>=0.005**. Original V54 is POST prior V27 exploratory; source positive accuracy is not a preregistered independent ecological demonstration.

### Direct source artifact falsification V55

The original coast excludes 26.4% of Hewison chinstrap points but only 0.22% of Hewison Adélie points: an exceptionally strong possible map × species ascertainment bias. V55 therefore refits B1 AND B2 on identical strictly INSIDE-2020-coast source bird nest samples in every source training/test fold. Original positive island gains **PERSIST**:

| Original island | V55 strictly inside source land, B1−B2 |
| --- | ---: |
| Saunders | +0.043160 |
| Bellingshausen | +0.030365 |
| Thule | +0.080066 |
| **Equal-island mean** | **+0.051197** |

**Important:** A distinct pre-fixed 30m occupied source cell-equal weighting falsification **could not be fitted**. Bellingshausen's chinstrap nests occupy only **16** distinct 30m cells and Thule Beach Point's chinstrap nests only **12**, below predeclared minimum **20 each taxon×source locality**. Original other site classes: Ashen A256/C177, Bell A32/C16, Beach A33/C12, Hewison A66/C110. **Do not relax 20**, do not claim V54 robust to cell-level pseudoreplication, and do not use any purported spatial-bootstrap population p-value from raw 122k nests.

V55 source original strict-land *location-level association* survives, but taxon source nests cluster far more tightly than 122k independent geo samples imply.

## Why this is relevant, and why it does NOT answer the whole paper

**Supported at original source-nest association level:** independently mapped coastline geometry contains **reproducible location-classification information across three held-out true islands** beyond local DEM slope and elevation, and the signed incremental gain survives exclusion of original source offshore-map points. This is a real nontrivial conditional predictive outcome.

**Not supported:** measured penguin travel effort, actual passable routes, true selection over all suitable available land, breeding success, flightless-v-flying causal difference, terrestrial mammal refuges or predator-breeder crossover. Within Thule the gain is heterogeneous: on original Beach Point site B2 worsens; most Thule heldout benefit comes from Hewison. Standard original nest counts give stronger apparent precision than independent patch-level sample support. Three original islands remain three ecological island replicates.

**Paper2 next true mechanism target remains:** independent physical island colonization/available rock and shore-entry paths; same-survey flying seabird nesting source across more than one island; *field-verified* mammalian occupied and genuinely surveyed non-occupied islands (Falkland original V47 co-breeding 69 source island-year opportunities but G2 predator status unavailable). Avoid further re-analysis selected coast buffers/grid thresholds of this same BAS nest output after V55.

## Exact live receipts

- [V52 three source polygons and source land gate](../results/PAPER2_V52_BAS_SUBANTARCTIC_EXACT_THREE_ISLAND_COAST_SOURCE_RESULT.json)
- [V53 original nest mismatch distance from official coast](../results/PAPER2_V53_BAS_ORIGINAL_SHORELINE_NEST_DISAGREEMENT_SOURCE_RESULT.json)
- [V54 full source nest map-coast positive result](../results/PAPER2_V54_ORIGINAL_COAST_MAP_PROXIMITY_THREE_ISLAND_RESULT.json)
- [V55 strict-land positive but 30m cell gate STOP](../results/PAPER2_V55_BAS_COAST_MAP_STRICT_LAND_AND_30M_CELL_SOURCE_RESULT.json)
- [V54 actual Github original source test execution](https://github.com/zuizui0223/mina/actions/runs/40630832563)
- [V55 actual source and pre-declared false-positive test](https://github.com/zuizui0223/mina/actions/runs/40631659488)

**No modifications to frozen Ecology Paper 1 PR189 or paused Zavodovski PR196. This is one Paper2 exploratory step, not a second new paper.**
