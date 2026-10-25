# Antarctic Functional Archipelago v1 — independent geography-first macroecology

**Status 2026-10-25: outcome-blind spatial-architecture implementation.**
This is an independent *mina* research lane, branched from PR #197. Do not alter
the frozen Ecology Article PR #189, do not reopen the failed V41 land-pair gate,
and do not reinterpret previous positive penguin contrasts as validation here.

## Central ecological question

Are Antarctic breeding populations structured by the nominal physical landmass
("geographic insularity") or by networks of exposed reproductive substrates
("functional breeding-habitat insularity"), and does the distinction depend on
life history and access to marine subsidies?

Antarctica contains rock/outcrop patches on the continuous mainland as well as
on offshore islands. For primarily land-nesting penguins, food is mainly marine
while breeding depends on available terrestrial surfaces. Emperor penguins
are a separately sourced and separately modelled fast-ice-breeding contrast;
they must not be folded into a rock-area model as if they were land breeders.
Flying seabirds supply possible within-East-Antarctica life-history contrasts,
not an automatic claim about competition or movement.

The new object is a *candidate habitat landscape* constructed independently of
penguin colony locations, not a literature-derived summary of colony effects.

## Distinct observational grains

1. Land polygon: an ADD v7.12 mapped "surface=land" feature. Its polygon identity
   is **not** necessarily an official named island, stable historical shoreline,
   independent population or proof of an intervening ocean barrier.
2. Exposed-rock polygon: an independent ADD v7.11 mapped rock outcrop, with
   distinct source feature identity. It is a candidate habitat patch, **not**
   confirmed usable nesting area or annually observed ice-free surface.
3. Survey site: an authoritative original field-programme site with a source ID,
   positional uncertainty/lineage, year, searched species and explicit effort.
   Do not project survey observations onto a patch without a validated crosswalk.
4. Biological observation: a P/A/NR species × geographic-site × season record;
   **NR is neither zero nor absence**. Population count, presence, breeding stage
   and survey programme are separate data types.

## Stage A — geography only (implemented by new script)

Primary radius: **2,000 metres** of mapped EPSG:3031 planar boundary-to-boundary
rock-patch gap. This local-scale descriptor is not a dispersal distance or a
geodesic swimming-path estimate. Inputs are the original frozen SCAR/BAS land
shapefile v7.12 and rock-outcrop shapefile v7.11, not APBP/MAPPPD outcomes.

A rock feature receives an unambiguous land ID **only if its entire geometry
is covered by one valid original source land polygon**. Ambiguous, overlapping,
uncovered and mixed-resolution rock features remain HOLD; no nearest-land
rescue or snapping. Record source-specific status for every exposed-rock feature.

For each exactly classified rock polygon compute:
- its source identity, parent mapped-land identity and approximate EPSG:3031
  projected polygon area; boundary-distance is deferred because a single
  extremely complex continental coastline would require an independent
  optimized coastline-segment index, and would not change the nested-gap test;
- nearest eligible mapped-rock *edge gap* within the **same** parent land
  feature, censored if no such polygon occurs within the frozen 2 km radius;
- nearest eligible mapped-rock edge gap on a **different** parent land feature,
  censored by the same rule;
- when both are observed, whether a different-land rock patch is closer than
  the nearest rock patch on the same continuous land feature.

This is an independently derived spatial *topology-disagreement* diagnostic.
Stage A uses source geometry PREPARED containment and radius-expanded bounding-box
candidate searches followed by exact GEOS rock-edge distances; it does NOT
run repeated expensive distance-to-entire-continental-coastline calculations.
A different mapped land feature is **not automatically a sea-water gap**. The
separating medium (marine water / glacier / shelf / uncertain) must be resolved
from independent original surface/topology data before claiming a water-barrier
effect. Never infer ice thickness, terrain passability, nesting capacity or
animal movement from these gaps alone.

Output two build artifacts: "summary.json" and "rock_patch_features.csv", with
pinned SHA256 receipts and explicit nulls for right-censored neighbor distances.
No animal abundance, occupancy, colony coordinate or other biological outcome
is accessed. The derived CSV is not a list of independent penguin colonies.

## Stage B — original survey-source eligibility (not yet implemented)

Use AADC DOI **10.26179/5n29-r073** (Adelie and seven flying seabird species:
P/A/NR + original search effort) and accompanying original feature reference
DOI **10.26179/53yk-8z83**. Prepare an *outcome-blind* field-site × mapped rock
site crosswalk with explicit original coordinate accuracy and boundary stability.
The published AADC data are prior art as an occupancy archive, not a claimed new
finding. An AADC geographical ice-free *site* is not the same observational grain
as an ADD polygon or a biological breeding patch.

Do not use MAPPPD presence-only coordinates as surveyed non-occupancy controls.
MAPPPD v5 (2026-10-21) can become a separate repeated-census secondary outcome
only after original site identity, source/citation genealogy, biological stage
and geography pass a pre-outcome test. Specifically, the **316** original NZ/Ross
census overlaps in PR #197 V40 are the *same original observations* and must not
be counted as independent replication.

## Stage C — prospective biological prediction (NOT YET TESTED)

**Primary falsifiable contrast:** controlling for source programme, geographic
region, repeated-site identity, spatial blocks, observation effort and species,
does independently mapped *rock-patch configuration* contribute genuine held-out
information about explicitly surveyed breeding occupancy beyond nominal land
area and land-feature identity? A difference between land-nesting Adélie and
flying seabirds is a proposed *candidate interaction*, not a finding.

Freeze the following model sequence after Stage B's spatial *support* gate and
before observing any new independent P/A outcomes:
- M0: effort, time/period, species, region and geographic/spatial random structure;
- M1: M0 + physical land polygon area and land-geometry class (only if validated);
- M2: M1 + amount, adjacency and fragmentation of *independently* mapped rock;
- M3: M2 + biologically justified species × functional geometry interaction.

Use balanced spatially held-out predictive log loss/Brier and predeclared
confidence intervals, not in-sample coefficients or pseudo-replication by
repeated original census; require support from **multiple independent original
survey regions**. Freeze minimum region/site/species support and exact outcome
processing with a new signed contract *before* running M0–M3. Without that gate,
stop rather than tuning radii, coast tolerances, guilds, original field aliases
or habitat classifications after outcomes are inspected.

Emperor-specific fast-ice metrics and additional penguin species need
independent spatially/temporally appropriate data and their own pre-outcome
cohort; do not interpret the land-rock Stage A as validating them.

## Novelty boundary

Prior art is explicit: Lee et al. 2022, *Islands in the ice* (DOI
10.1111/gcb.16331) already describes Antarctic ice-free habitat islands;
Obrist et al. 2020 (PMCID PMC7126081) already tests marine-subsidized island
biogeography; existing island-area and Antarctic ecosystem mapping are not
new concepts; Southwell et al. 2025 (DOI 10.1111/ddi.70066) already publishes
East Antarctic seabird survey occupancy; and the 2023 *Science Advances* emperor
fast-ice habitat study (DOI 10.1126/sciadv.adg8340) is not our discovery. The candidate original
contribution is the independently measured mismatch between *nested Antarctic
habitat isolation* and *mapped land continuity*, and its cross-guild effect
under actual sampling controls. Stage A creates a spatial data product but does
not yet establish a penguin ecological effect. Moreover, the earlier V14
analysis in PR #197 **already inspected** AADC flying-seabird P/A outcomes for
island-area × nesting guild and FAILED spatial held-out predictive support.
Consequently a later AADC re-fit with novel rock topology is **exploratory**;
it cannot be sold as untouched preregistered external validation. A genuinely
confirmatory claim requires independent newly eligible field programmes/regions
or prospectively acquired data, frozen before outcome analysis.

## Original data sources

- SCAR ADD land v7.12 (2026), DOI 10.5285/13c4d2f1-8903-4d7f-8977-592121975554,
  original ZIP SHA256 66d82fa69f86eb8dbe8b04f01505cb2129feafec608455459ee4ed19d1dc38d4.
- SCAR ADD rock v7.11, DOI 10.5285/3f0c400f-04b9-4819-98cb-f6b53716aca5
  (original ZIP SHA to record at source-only fetch before any bird outcomes).
- AADC East Antarctic breeding seabird site surveys, DOI 10.26179/5n29-r073,
  with eight species and explicit P/A/NR distinction.
- Oceanites MAPPPD v5.0, https://www.penguinmap.com/mapppd/ .
- Antarctic Ecosystem Inventory 100 m, DOI 10.1038/s41597-025-04424-y.
