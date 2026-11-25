# BAS Hart 2019–2020 multi-locality penguin nests: independent original-source macro-ecological evidence V16–V21

**Date 2026-10-26 | User direction: original database-based island ecology, not other papers' reported slopes. | Draft PR #199.** This is a separate sub-Antarctic biological test case, not a continental Antarctic-wide island mechanism or a new field sampling programme.

## Original source archives and observational grain

Official BAS/UK Polar Data Centre, Hart et al. 2022, DOI `10.5285/28222725-c53d-40f4-9350-49c368899f0b`. Verified **22** real nested publisher archive directory manifests, listing **32 original CSV and 132 original TIFF** source items across seven author survey locality folders and the root count CSV. The publisher's older count of 31 CSV/127 TIFF differs; preserve the full publisher file IDs and receipts instead of inventing missing files. [V16 complete original publisher manifest CI](https://github.com/zuizui0223/mina/actions/runs/40261490725).

Seven named *survey localities* correspond by source gazetteer context to five **provisional** physical islands:
Zavodovski, Candlemas, Saunders (Ashen Hills), Bellingshausen, and Thule (Beach/Hewison/Herd), but original specimen island-parent shoreline GIS and full orthomosaic survey masks were NOT independently verified.

The exact original publisher 431-byte `SSI_count_results.csv` reports four literal species count categories (Adelie, Chinstrap, Gentoo, Macaroni), mixed/unknown classes, spatial-extrapolation categories (e.g., Chinstrap_estimate), and a total. Source SHA256 `3206e74af11b3424bc59cb1c451f1eaeb490de6677d0b7b91b85e3a9fa68cede`. **Two source total-additivity discrepancies**: Ashen Hills `Total − listed component sum = +1000`; Hewison Point `= −2711`. The original Zavodovski table's reported 537,848.4766 includes **323,363.4766 estimated-nest equivalents**, plus 41,430 originally mixed/unknown nests, leaving 173,055 nests in species-labeled count cells. No species absence inferred from blanks. The **2022** Zavodovski Chinstrap coordinates are not a contemporaneous 2020 Macau interspecific nest study. [V18 source ledger CI](https://github.com/zuizui0223/mina/actions/runs/40262648235).

## New independently measured individual nesting coordinates

V19 verified **20 first-party original species/mixed nest-coordinate CSV headers** all with `nest_number,lat,lon`, separate from eleven polygon-outline-vertex CSVs and one root count CSV. [V19 original publisher schema run](https://github.com/zuizui0223/mina/actions/runs/40263269258).

Before opening their coordinate rows, V20–V21 froze exactly **10 species-labelled source nest CSVs** across:
1. Ashen Hills (Saunders candidate): Adelie, Chinstrap, Gentoo, Macaroni;
2. Bellingshausen: Adelie, Chinstrap;
3. Beach Point (Thule candidate): Adelie, Chinstrap;
4. Hewison Point (Thule candidate): Adelie, Chinstrap.

**Source-incomplete coordinate QA disclosed as post-source amendment**: 31 of 122,170 original nest-numbered source rows (0.0254%) lack one or both lat/lon fields. The unlocated nest source IDs are retained as counts but excluded from spatial point analysis, never imputed as locations. Thus **122,139 original georeferenced nest points** were source-audited, transformed from WGS84 to local EPSG:32726. Original source CSV SHA256 and site/labeled-taxon provenance preserved. The sample excludes unknown/mixed individuals and all ZAVO noncontemporaneous/imputed taxon labels. [V20 source QA and point artifact](https://github.com/zuizui0223/mina/actions/runs/40274662115), `results/BAS_HART_10_ORIGINAL_MULTIISLAND_NEST_GPS_V20.json`.

**Independent count discrepancy diagnosis:** Ashen Hills original Adélie coordinate file has **53,572 uniquely labelled source nest-number records** (53,565 valid positions, seven missing positions), while the *separate original count table* displays **52,572 Adélie**. The independent +1,000 difference coincides *exactly* with the source table's +1,000 nonadditive total discrepancy at the same locality. This points strongly to a count-transcription or bookkeeping mismatch, **not** a verified publisher error correction and not proof of ecological abundance growth; no values are silently changed. The remaining taxa generally reconcile; original Beach Point Adélie point file has one fewer source nest row than the root table.

## V21 original spatial source pattern: strong 10-m conspecific clustering

Across the exact 4 localities, after separately tracking and excluding **3,366** geographically duplicated point records, **118,769** original nest points have an unambiguous nearest nest within the fixed **10-m** radius (only 4 unique points are further away). For each locality the frozen null is **199 random species-label permutations keeping all original point locations and each local original taxon count constant**.

| Source locality | Valid eligible 10m NN point centres | Observed nearest nest heterospecific (%) | Local-label-shuffled null median heterospecific (%) | Conspecific enrichment difference (percentage points) |
|---|---:|---:|---:|---:|
| Ashen Hills, 4 taxa | 75,253 | 0.1674 | 44.0248 | +43.8574 |
| Bellingshausen, 2 taxa | 14,003 | 0.04285 | 44.2834 | +44.2405 |
| Beach Point, 2 taxa | 7,089 | 0.0000 | 46.6074 | +46.6074 |
| Hewison Point, 2 taxa | 22,424 | 0.05797 | 49.6834 | +49.6254 |

The observed heterospecific rate is below **all 199 source-label randomizations at all four sites**, but this is a baseline descriptive point-pattern departure, **NOT** a biological causal p-value. The source nearest-neighbour median spacing by site is **0.73, 0.50, 0.68, and 0.75 m**, consistent with dense nesting within local colony patches. All four sites contain >1 source-identified taxon yet immediate nest neighbors are overwhelmingly conspecific.

**What is empirically supported:** distinct original penguin species are very strongly spatially assorted at the individual nest scale **within the mapped, counted colony point clouds** at these four surveyed localities. The inference is original, reproducible point-level pattern estimation from first-party data, not pooled published site-level effect estimates.

**What is NOT established:** This finding alone is expected if original digitized nests occupy **distinct conspecific breeding patches**, and the whole-locality null erases those patch identities. It does *not* prove interspecific competition, a niche exclusion mechanism, island-directed dispersal or a general Antarctic law. The four localities nest within only **three provisional physical islands** in one survey campaign, and the original imaging footprints may differ between species even within the same nominal locality. Since source filenames lack exact calendar dates, precise contemporaneity of all species at each locality is also not independently proven.

[V21 original reproducible 10m point analysis](https://github.com/zuizui0223/mina/actions/runs/40274846668) · `results/BAS_HART_4_LOCALITY_ORIGINAL_NEST_SPATIAL_V21.json`.

## V22 post-result falsification, not yet a pre-outcome ecological effect

V22 is designed **after inspecting V21**, to see how much original species assortment is due to selection of different **25m/100m/500m** nest patches. It keeps spatial cell-specific species abundance fixed and shuffles only labels within mixed-taxon cells. The primary 100m test must have ≥5% of source nearest-neighbour point centres in mixed-species cells; otherwise conclude testability HOLD, not local exclusion. The 100m grid is shifted to four fixed phases to assess arbitrary-grid sensitivity. The result is explicitly exploratory even if the per-cell species-label null is positive.

No island-ecology generalization or new competition mechanism is authorized until independent actual nest-available habitat, spatial survey imagery masks, island coastline identities, comparable seasons and true visited-empty nesting patches can be incorporated. In particular, **neither BAS site counts nor the 122k point-level pseudoreplication can supply independent tens-of-islands evidence**.

## Main programme alignment

The island-specific causal question remains: do physical land continuity `P`, functionally reachable reproductive rock `F`, and time-dependent ice substrate `T` have different associations with colonisation/persistence and spatial redistribution? For this source study, measured nest points resolve the *spatial response* well but lack the *independent causal environmental exposure* and multi-year individual histories. The global physical-island geographic baseline in `zuizui0223/island` is methodology context, **not** an unrelated taxonomic slope to regress directly against penguin counts. Original Antarctic MAPPPD, SCAR and AEI database source QA remains separate; PR #189 frozen Ecology manuscript untouched.


## Executed V22: how much species nesting separation is explainable by local patch composition?

[Source-frozen 100m spatial-patch control CI](https://github.com/zuizui0223/mina/actions/runs/40275598206) succeeded after an import-path regression fix. Post-V21 exploratory result: 99 source-label permutations were performed **within** fixed 100m×100m UTM cells (not over the full locality), preserving *the original geographic counts of all taxa within each cell*.

| Source locality | V21 all-site label-shuffle excess conspecific NN (pp) | V22 fixed 100m-grid excess conspecific NN (pp) | Source NN points in mixed-species 100m cells |
|:--|--:|--:|--:|
| Ashen Hills | +43.86 | +4.98 | 18.8% |
| Bellingshausen | +44.24 | +8.40 | 19.9% |
| Beach Point | +46.61 | +15.97 | 39.5% |
| Hewison Point | +49.63 | +7.30 | 20.6% |

Thus **a substantial part of the dramatic V21 site-wide randomization departure is explained by each species' concentration within different 100m-scale spatial cells**. But the fixed 100m mixed-cell controls still yielded fewer heterospecific original nearest-neighbor nests than within-cell exchangeable labels at all four locations. This is a *spatial structure hierarchy* finding, not direct territorial interaction.

**Important scale-and-origin sensitivity:** The 25m cell test failed its >=5% mixed-species-cell eligibility support gate for Ashen (4.33% eligible), Bellingshausen (4.63%), and Beach (3.06%); only Hewison (5.24%) narrowly cleared. The 100m null excess at Beach varied sharply from +1.37 to +15.97 percentage points across its four frozen grid phases; Bellingshausen varied +2.63 to +8.40. Consequently the exact residual magnitude is **not robust to arbitrary grid alignment** at some sites; do not turn this into a fixed taxon-vs-habitat niche breadth parameter.

Source spatial V22 JSON: `results/BAS_HART_FOUR_LOCALITY_SPATIAL_PATCH_V22.json`. Its rules were defined *after* V21, so neither these repeated spatial label controls nor their differences are prospective confirmatory evidence.

## Next source/method gate rather than further result-mining

The 4×species original nest point clouds do **not** include independent uniformly surveyed nesting-substrate masks. Two species may have different registered original source images within a nominal same locality. The separate V23 original TIFF file-list test explicitly asks whether the original source orthomosaics and their acquisition dates/footprints overlap; this must be source-verified before any mechanism is attributed to nesting substrate preference, true microhabitat niche partition or interspecific competition.

**Scientific decision now:** This South Sandwich original source provides a quantitatively demonstrated, reproducible *observed multiscale conspecific clustering phenomenon* at four localities nested in only three provisional island groups. It does not yet establish whether the cause is coastal terrestrial geomorphology, substrate accessibility, inherited colony-site preference, social recruitment, direct species interactions, source digitization extent, or an Antarctic-wide physical-island law.
