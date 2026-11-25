# BAS South Sandwich V18: first-party counted versus estimated nest ledger (exploratory)

The original BAS Hart et al. 2022 \`SSI_count_results.csv\` publisher file is **actual first-party nesting tally data**, not paper effect-size estimates; source SHA256
\`3206e74af11b3424bc59cb1c451f1eaeb490de6677d0b7b91b85e3a9fa68cede\`
(431 bytes). 2026-10-26 V17 source schema has an intentionally unnamed
first column of count category, seven **survey localities**, and the ten literal
count-category rows: \`Chinstrap\`, \`Chinstrap_estimate\`, \`Mixed\`,
\`Mixed_estimate\`, \`Adelie\`, \`Gentoo\`, \`Macaroni\`, \`Unknown\`,
\`Unknown_estimate\`, \`Total\`.

**Frozen post-schema, before V18 numerical summary calculations.** V17 did inspect the first 6 rows of counts; V18 is **exploratory source data descriptive**, not a prospectively independent validation of Hart et al.'s conclusions.

## Analytical grain

- Seven original survey localities: \`Zavodovski\`, \`Candlemas\`,
  \`Ashen_Hills\`, \`Bellingshausen_Island\`, \`Beach_Point\`,
  \`Hewison_Point\`, \`Herd_Point\`. Never call them seven separate
  physical islands or seven complete breeding census populations.
- Geographical grouping from external gazetteer/field locality references:
  Zavodovski→Zavodovski Island; Candlemas→Candlemas Island;
  Ashen Hills→Saunders Island; Bellingshausen→Bellingshausen Island;
  Beach/Hewison/Herd→Thule Island. Thus **7 locality columns across five
  named physical islands**, independent only as site-location groups,
  not statistical random independent demographic populations.
  Confirm geographical grouping later against original nest GPS and
  shoreline; do not manufacture a new island-level abundance count.
- One austral season 2019–20 **except** the publisher used a 2022
  Zavodovski chinstrap resurvey for some 2020 reconstruction.
  All Zavodovski 2020 chinstrap nests are marked **MIXED_TEMPORAL_LINEAGE**:
  do not use them in strictly contemporaneous 2020 species-pair tests
  without independent per-point observation-year provenance.

## Frozen original response partition

- \`Adelie, Chinstrap, Gentoo, Macaroni\` = **taxonomically assigned
  reported nest counts**, integer-valued original CSV. Original
  \`Chinstrap\` on ZAVO may have mixed acquisition years.
- \`Mixed, Unknown\` = **reported original count categories whose nest
  species is not resolved**; strictly excluded from each species numerator.
- \`Chinstrap_estimate, Mixed_estimate, Unknown_estimate\` =
  **spatial extrapolation/estimated categories**, never considered
  individually annotated nests or extra surveyed sites.
- \`Total\` = **publisher-reported locality aggregate**; do not assume
  it is exactly the sum of cells without explicit numerical integrity
  check (tolerance 1e-6 relative or 1 nest absolute for publisher
  rounding). If discrepancy, report, but do not force totals to match,
  impute missing blanks as structural zeros, or substitute a manually
  selected total.
- Blank data cells = unreported/missing, NOT observed zero and NOT
  documented species absence. Candlemas orthotiffs support counting
  Adélie only; nonreported species are not absent.

Per survey locality report: original reported sum of four species-labelled
count cells, taxonomically ambiguous counted cells, explicitly estimated
cells, original Total, additive consistency, and **identifiability
fraction conditional on source's own reported Total only when additive
consistency holds**. No confidence interval or original island-wide
nest-count interpretation without surveyed polygon footprint and imputation
source model.

## Ecological next hypothesis (NOT asserted)

Separate absolute local abundance from multi-species nesting configuration:
for sites with >=2 coordinate-labelled species in a common 2019–20
UAV observation footprint, compare interspecific nearest nest distances,
species-specific observed 10m cell sharing and a geography-conditioned
null preserving count/patch clusters. Must retain mixed/unknown unassigned,
2019–20 versus Zavodovski 2022 temporal identity, true mapped island and
original local extent. A single-season cross-sectional pattern is **not
competition, displacement, priority effects or direct dispersal**.

Source original data policy: BAS open under OGL v3; do not assert new
independent observations for the existing PR #196 2020 ZAVO nest point data.
