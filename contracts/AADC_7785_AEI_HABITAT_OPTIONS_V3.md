# V3 independently mapped Antarctic breeding-habitat options at original AADC sites

**Status 2026-10-26: new geography-only source-derived atlas; NO new AADC animal outcome loaded.** Defined after the candidate-site-density V1 and V2 biological analysis. Later correlations with these same AADC animal outcomes are by definition EXPLORATORY; do not relabel or tune predictors after inspecting outcomes.

## Primary question
A raw count of publisher-defined candidate-site centroids predicts surveyed seabird P/A in exploratory V1, but its interpretation could be biased by survey-site mapping density. Replace the ambiguous candidate-point proxy, not its biological result, with an independently mapped environmental measure: Antarctic Ecosystem Inventory v1.0 mapped ice-free physical habitat **within a fixed 2 km disk** at every original 2025 AADC potential-site reference coordinate (7,785 sites).

This treats each potential site as an observational sampling anchor rather than assuming that it lies within a polygon or that its coordinate is an individual nest GPS point. It avoids relabeling the failed strict SCAR rock-site-match gate, where Adélie had 6 sites and flying seabirds 11.

## Original spatial sources
- AADC geographic potential sites: 2021 edition 4,884 original IDs SHA 2236269e754962f9af082a0853993fc65a4afd20c7489a65fae81bdd1899ffaa; 2025 edition 7,785 original IDs SHA ed5f59d11a0e2ca7491ecf32dc8b04de524e83edf7acd268702963c3b7561294. Biological XLS/XLSX not downloaded here.
- Antarctic Ecosystem Inventory original 100 m raster, DOI 10.5281/zenodo.11629115, file AntarcticaEcosystemInventory_IceFreeLands_v1_int.tif, source MD5 cde880d73f7f18b44aecf5690aa2dc92.
- Author original VAT .dbf, source MD5 fa5363b1c0d882b4343e239d03dc2ba4, all 269 expected Tier-3 class IDs, 9 Tier-1, 33 Tier-2.
- Same previous PAPER2 spatial metric conventions: WGS84→EPSG:3031, fixed 2000 m circular pixel-centre inclusion; do NOT substitute a chosen radius or missingness imputation after seeing biology.

## Mapped terrestrial option descriptors
At every original AADC source-defined geographic site report:
1. Mapped ice-free pixel count and projected ice-free area (ha) and fraction of pixels covered in fixed radius. A cell is not annual accessible breeder capacity; 0 mapped area does NOT prove true absence of ice-free habitat.
2. Original VAT Tier-2 Habitat Complex diversity after conservatively excluding classes with animal-outcome-derived labels. Freeze case-insensitive substrings: "penguin", "seabird", "bird", "colony", "rookery", "guano", "ornithogenic". These are not used as penguin/seabird outcome predictors even if their raster pixels exist. Retain a source receipt reporting exactly which author original classes were excluded. Do not classify biologically derived pixel types as independent breeding-habitat predictors.
3. The non-animal-derived mapped ice-free area, Tier-2 richness and Shannon entropy separately. No valid mapped non-animal cell means predictor MISSING, not a confirmed ecological zero.
4. Source class island/continent and 2021-frame membership for descriptive coverage ONLY; source class is not an independent mapped island polygon.

Export 7,785-row site-ID feature CSV and summary JSON with input hashes, coverage, source class and geographic source-edition strata, and predeclared 2-km descriptive medians/p10/p90. Never read P/A/NR or census counts in this stage.

## Required biological next-stage gate (not authorized by this atlas)
Before any new ecological association from the same AADC data, freeze and report missingness by original species/programme and >=5 sites/250km spatial block. Do not relabel the existing AADC V14 negative model, or the V1/V2 candidate-site density result as independent confirmation. Any association of these habitat traits with already-opened AADC P/A data is exploratory; a confirmatory island-biogeography claim requires new field source/period and independent validation of true physical island vs ice-gap topology, not just source site classes or raster cell proportions.

## Scientific inference ceilings
The raster partly uses known animal-biogeographic class definitions: excluding animal-linked classes helps prevent direct leakage but does not erase all mapping/survey biases. Site centroids are authored *potential sites*, not census of every accessible rock patch. Geo pixel area in EPSG:3031 is projected, not equal-area. No causal mechanism of penguin site choice, breeding success, sea-ice access, or competition is identified solely by these static atlas data.
