# V12 — actual independent physical landmass support among V10 repeated East Antarctic Adélie GIS sites

**2026-10-26 source-only audit.** V10 and post-result V11 polygon metrics were observed; this audit does not create new independent animal data or fit spatial ecology. No radius/matching threshold may be tuned based on previous mapped shrinkage/Jaccard results.

## Question
V9 publisher file inventory contains 13 repeated source-defined colony reference site IDs in just two AADC survey groups HBE/HBW. **How many different actual mapped physical land features does that constitute?** Two survey groups and 13 original site IDs are NOT necessarily two physical islands or 13 independent island-level replicates.

## Source receipts
- `results/ANTARCTIC_SOURCE_BOUNDARY_MANIFEST_V9.json`: original publisher IDs and time.
- `results/AADC_REPEATED_ADELIE_COLONY_GIS_V10.json`: exact 28 original source polygon file receipts and source survey records; retrieve actual original *site-year metrics* CSV, source SHA and bounds for a location-only QA. Do not download colony polygons again or read additional biology.
- Original AADC 2025 geographic reference 7,785 unique sites, exact original publisher XLSX SHA `ed5f59d11a0e2ca7491ecf32dc8b04de524e83edf7acd268702963c3b7561294`.
- SCAR/BAS original high-resolution ADD coastline v7.12 `surface=land`, original zipped source SHA256 `66d82fa69f86eb8dbe8b04f01505cb2129feafec608455459ee4ed19d1dc38d4`, EPSG:3031. Parent polygons are *land features*, NOT official named islands.

## Fixed original-geography audits
1. For each of the **13 original repeated survey site IDs**, locate exactly one original AADC published geographic site reference (or retain MISSING). Preserve author geographic class 'island' versus 'continent'.
2. Project its WGS84 coordinates EPSG:3031; match point to **exactly one** original high-resolution SCAR land polygon if unambiguous. No nearest-polygon rescue, buffer tolerance or source class overwrite. Exact largest mapped land feature is continent proxy, not a named island. Sites unmatched or crossing boundaries remain HOLD.
3. From the original V10 **bounds-only** source QA, compare original AADC site reference point to bbox of original colony geometry per repeated season. This is a coarse *minimum distance to bbox* only, not distance to actual polygon. A site reference outside bbox illustrates incompatible source coordinate grains, not true species movement.
4. Report original source survey groups, original site IDs, distinct matched parent land polygon IDs, original author label distribution, and repeated site-year coverage. Even if two survey groups exist, do not call them two independent physical landmasses unless supported by actual original mapped land IDs.
5. No link to MAPPPD counts or existing AADC P/A source. No ecological slope, site-reshuffling inference or island-level dispersal mechanism.

## Gate
If most repeated site IDs share one physical mapped land feature, this is a valuable **within-one-landmass morphology/census-boundary data case**, but insufficient independent physical-island contrast. If multiple land features occur, report exact count with source position uncertainty; still cannot infer mobility between islands or transferable Antarctic-wide slope because source regions are two adjacent groups.
