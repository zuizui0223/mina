# Antarctic exceptional insularity — independent macroecology contract, v2

**Programme scope 2026-10-26:** new question with source-defined exposure and independently acquired animal outcomes. NOT a literature effect-size meta-analysis, nor a rescue of frozen penguin Ecology PR #189, AADC P/A V14–V5 or MAPPPD V41 failed source gates. This is the next *mina* scientific mainline after the source-only Antarctic Functional Archipelago PR #199.

## Focus on a causally distinct ecological claim

**Central test:** In a marine-subsidised breeding assemblage, is the functional network of annually usable reproductive substrates a better determinant of local breeding occupancy, population restructuring and recolonisation than static continental/island coastline isolation? **Does the separating medium (sea vs glacier/grounded snow vs fast ice) modify that relationship after habitat amount, regional marine forcing, observation effort and documented species-specific substrate use are accounted for?**

This distinguishes three **observational** spatial boundaries, not three interchangeable ways of naming an island:

1. `P`: physical landmass continuity and shoreline gap. The corrected global physical-island analogue from **zuizui0223/island** uses GSHHG v2.3.7; this is the source-harmonised reference frame for the ordinary global 8,264 island units (operational area >=5 km2), not automatically a penguin nesting surface. [Current baseline](https://github.com/zuizui0223/island/blob/main/config/chapter1_submission_current.json).
2. `F`: functional exposed breeding-habitat geometry, minimum verified rock/ice-free patch gap, area, network connected components and reoccupation candidates; **not** whatever polygon happens to contain one source reference point. Off-continent ice-free nunataks can be effective terrestrial habitat islands within a physically connected landmass.
3. `T`: seasonal breeding-substrate architecture. For emperor/fast-ice breeders, formation, persistence and break-up of **anchored fast ice** can change available breeding topology; static summer rock or offshore coarse sea-ice concentration is not a substitute.

**Hypothesis H_F**: physical landmass area/isolation will be a poor sufficient summary of breeding-patch risk **when** usable-substrate availability and connectivity vary independently of coastlines, *even among sites on the same mapped landmass*. But it must be evaluated prospectively with multiple independent original land features/islands and verified breeding effort, not by comparing GSHHG plant-island trait slopes to Antarctic count slopes.

## Hard evidence from original independent geography — why the new biological gate is necessary

- Old SCAR manually compiled rock v7.11: 31,480 source polygons; Landsat v7.3 auto+manual fallback: 366,106 polygons (359,880 automated origin, 6,226 manual fallback). Both map the **same fixed 7,785 AADC 2025 potential-site centre coordinates**, not individual penguin nest GPS.
- New deterministic Shapely make-valid source QA recovered 541 point-inside-rock matches lost due invalid source polygons. Native valid 2,159; native+repaired 2,700. Old manual v7.11 source point hits 2,523.
- Crucial independent source overlap: **721** points lie in rock according to *both* source rock maps; old-only 1,802, Landsat-only 1,979; Jaccard exact **0.16015**. At exact-or-within-250m diagnostic threshold, old 3,035 and new 5,769, intersection 2,094, Jaccard **0.31207**. Details: `results/SCAR_ROCK_TWO_SOURCE_SITE_OVERLAP_V8.json`, pinned source `results/SCAR_LANDSAT_V7_SOURCE_TOPOLOGY.json`.
- Therefore **source polygon overlap at a single historical reference coordinate is not a validated biological breeding-site classification**. Map method/vintage/rock segmentation differences are confounded with true historic substrate; choosing whichever source yields more significant colony associations is prohibited. The Jaccard figure describes a fixed original AADC *source-site-centre* population only, not true continental rock map overlap.
- Strict AADC×SCAR biological support previously STOPPED (6 Adelie/11 flying sites; zero comparable holdout regions). AADC AEI current physical habitats are response-selectively incomplete and all prior P/A outcomes are already opened. Do **not** refit this cohort to claim an insularity mechanism.

## Measurement and scale separation

- Set biological unit to a **field-verified nest-bearing or explicitly searched breeding patch × species × breeding season**, unique permanent identifiers with coordinates, year, count stage, survey effort, and original publisher/citation family. Distinguish records that are nonvisit/unknown from actual surveyed absent.
- Independently identify parent **physical island vs continental exposed outcrop** from a frozen trustworthy land source/GSHHG crosswalk plus verified map boundary uncertainty. For landscape options, use a *disk/window of independently mapped raster cells or independently digitised field nest-suitable substrates*, not a single source centroid-class hit. Source-vintage disagreement must be propagated to predictor uncertainty.
- Do not pool different stages (nests/chicks/adults), unknown count methods, georeference proxies, or the known 316 duplicated original NZ Ross/MAPPPD censuses as independent observations.
- Fit climate/marine forcing and year effects after source lineage and habitat metrics frozen. Colony movement vs breeding propensity vs nest success are different mechanisms; counts alone do not identify individual dispersal.
- Compare two spatial resolutions (island and within-island patch) as a *nested model*, while maintaining physical landmass IDs; stratify/exclude unstable georeferences before outcomes, never tune distances to restore support.

## Cross-system comparative role of existing repositories

- **zuizui0223/island**: external 'ordinary' physical-island geometry and known ecological responses under GSHHG 2.3.7, currently **8,264 operational units** with >=5 km2; supplies a physical-coastline reference and method for strict sibling-landmass IDs, NOT a pooled animal effect or direct plant-vs-penguin response estimate.
- **zuizui0223/mina**: own Antarctic mapped ice/rock landscape, local penguin discovery, and new georeferenced breeding-network biological tests; frozen PR #189 remains separate manuscript.
- Flightless Pygoscelis versus flying Antarctic seabirds: post-V5 same-programme/period spatially paired observations required; different AADC source-season/effort families are not matched.
- Emperor penguins: explicitly different ice-breeding substrate domain, requiring original dated fast-ice extent, stage-consistent colony occupation and melt/break-up timing; do not infer from static land maps.

## Actual next data lane (ranked by unique contribution; not a new study if inaccessible)

1. **Open original spatially digitised multi-season source** with verified per-patch positional accuracy and census unit consistency at multiple separate landmasses/regions. Candidate original UK BAS Zavodovski 2010–2025 vector boundaries (one island, two penguins, independent bird/fur-seal taxa) is a *calibration site*, not continental macro replication; previously scoped in paused PR #196. Do not reopen pre-submission frozen PR #189.
2. **Additional spatially precise independent sites**: USAP-DC 2019–2021 Ross orthomosaics across three named colonies, ~96.9 GB, officially 'contact us' for large file transfer; KOPRI Cape Hallett UAV 2018–2025 ~66.39 GB request-only. Existence is verified; access approval and downloads are **not** claimed.
3. **Landscape-wide independent ice time-series for emperor substrate** must distinguish landfast sea ice from moving pack ice. Published 2026 Dryad emperor source environment is a candidate for *independent topology derivation*, not a new confirmation of its already published climate-habitat associations. Test a prospectively stated island-network topology estimand rather than re-running authors' modelling.

## Tests that could overturn the hypothesis

- Once parent-island identities and habitat windows are independently validated, compare heldout ecology with block/time and observation controls. If functional patch topology does not improve independent-region predictions *or* changes sign under external habitat maps (like existing Jaccard=0.160), report failure/measurement unidentifiability.
- Evaluate the same habitat patch graph under true surveyed unoccupied patches: post-hoc rejection of inaccessible false absences is forbidden.
- For confirmed fast-ice annual colonies, test whether time-varying substrate continuity explains recruitment/occupancy beyond stage-compatible counts and sea-ice exposure; coarse general sea-ice extent is not a substitute.

**Current claim ceiling:** new original Antarctic macro **geographical** data and a quantified cross-map measurement boundary are completed. A novel universal Antarctic insular *biological mechanism* remains a future test, not a demonstrated result.
