# V4: Source chronology and identifiability gate (2026-10-11)

Verified directly against BAS official metadata https://data.bas.ac.uk/full-record.php?id=GB/NERC/BAS/PDC/02256.

The official lineage says satellite colony boundaries were digitised from Vantor/Airbus images **taken between December and March in 2010, 2011, 2016, 2020, 2022, and 2025**, and that **cloud gaps were filled with colony polygons from the closest-in-time clearly visible image**. Image details are reported in layer_descriptions.csv. The 2023 drone survey is 14 December 2023 during incubation; some southwestern plateau and Stench Point chinstrap habitat was not covered. Satellite imagery is proprietary; original scenes are not included as a freely licensed reanalysis input. The archived derived polygons are openly available.

**Correction to simplified V1 framing:** the 2011/2016/2020/2022/2025 layer labels do NOT imply uniform observation-year support across every polygon. The 2010 satellite year also appears in the official methods. The comparison-year pairs are provisional until source documentation verifies a common within-interval actual-acquisition chronology. Seasonal December–March acquisitions may straddle calendar years and breeding seasons; map dates to breeding seasons explicitly before declaring transitions.

**Hard gate:** no pairwise occupancy transfer, extinction/colonization, temporal order, habitat legacy or competition claim until (a) species-specific polygon provenance and acquisition dates are verified; (b) source-replaced/cloud-filled polygons are isolated spatially and excluded; (c) both species share a same-area valid observed support in both periods; (d) projected geometry registration and measurement error are quantified. If the dictionary documents dates only per *layer* but not per *feature/region*, a layer-level date cannot establish pixel-level genuine-year coverage. STOP and ask custodians for georeferenced cloud/replacement masks.

**Additional biological limit:** satellite boundary change is an occupied-area change, not individual movement, reproductive success, density, or direct competition. Even with robust occupancy transitions, the historical-site effect needs matched available habitat and independent landscape covariates.

**Verified in this step:** published lineage and access metadata. **Not verified:** archive CSV contents, cloud provenance masks, original polygon coordinates, any new biological effect. No source polygon row opened. Ecology PR189 remains frozen.
