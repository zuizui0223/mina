# East Antarctic replication support and Windmill colony identity (2026-11-24)

**Result: source-support extension only; no independent colony-history × plant-cover effect fitted.**

The verified original AADC parent record (DOI 10.4225/15/58f59b52edfef, original source run 45344865291 artifact 14896599187) lists 32 linked child surveys. The current [initial catalogue run](https://github.com/zuizui0223/mina/actions/runs/45356922134) returned an empty application-shell catalogue and cannot count as zero records. [Corrected run](https://github.com/zuizui0223/mina/actions/runs/45357084850) froze all 32 original IDs from that prior parent artifact, rejected non-metadata responses, and obtained 0/32 usable new metadata bodies, no new object inventories, no original polygons. Workflow success means diagnostic completed, not source gate passed. Stop retrying the same route.

## Prioritize exact repeated footprints
- Whitney Point, February 2006: extant/relic/maximum GPS shapefile, same status definition as Shirley 2006. Published catalogue mirror https://data.wu.ac.at/schema/data_gov_au/NmIzNDA0NjUtZDcxOS00YTkxLWExYTMtMTgzNGRjYWE3YWIx confirms title and schema, no original file acquired. This is a second locality within Windmill region, not independent Antarctic regional replication.
- AADC Windmill 2012–13 https://data.aad.gov.au/metadata/records/AAS_4088_Adelie_occupancy_Windmill_2012-2013 (exact child ID from official parent): seven ground-GPS sites surveyed 10 Dec 2012–9 Jan 2013 including Shirley and Whitney; original shapefiles needed to establish overlap/possible reoccupation. First input priority.
- Robinson 2006 https://doi.org/10.4225/15/590036ce1f0a3, https://data.aad.gov.au/eds/4427/download, 27 mapped islands; Robinson 2013 https://data.aad.gov.au/metadata/records/AAS_4088_Adelie_occupancy_Robinson_2013 nine remapped sites. Independent geographic follow-up, once both survey polygons and actual common survey extents are verified. Omitted polygons do not imply abandonment (e.g. Bechervaise 2013 metadata specifically records unmapped but occupied subcolonies).

## MAPPPD source grain
Rechecked exact archived derived census source blob fc134e364cf38699fa7611d7dee5fbbbcb370c0a. The seven named GPS localities correspond by published names to only five archive site codes: SHLY Shirley/Beall, WHTY Blakeney/Whitney, BERK Berkley/Cameron, HOLL Holl/O'Connor, ODBE Odbert. Four are grouped labels; no one-to-one spatial crosswalk verified. Do not copy their counts to seven individual islands, or infer full polygons from their centroids.

## Executed local botanical map support (not a biological effect)
Original Plantarctica ZIP SHA256 7e304e7a610d03287577e91faff05c009cf82039ae5f227763c37730a548a236. Independent official historic survey reference coordinates from https://data.aad.gov.au/metadata/records/SOE_seabird_candidate_sp_AP, not nesting coordinates. Fixed 1 and 2km circles in UTM49S, exact map intersections. No land-area denominator, no current occupancy, no comparison of cover, no effect estimate. Reference points 3767.790 m apart.

| Site | Reference lat/lon | MAPPPD grouped-coordinate distance m | Radius m | Vegetation mapped m2 | Lichen mapped m2 | Snow algae mapped m2 |
|---|---|---:|---:|---:|---:|---:|
| Shirley | -66.28219444,110.48830556 | 532.729 | 1000 | 2809.173 | 0 | 121.122 |
| Shirley | same | 532.729 | 2000 | 3390.380 | 484.337 | 484.320 |
| Whitney | -66.25238889,110.52780556 | 1521.488 | 1000 | 2614.827 | 8812.943 | 727.662 |
| Whitney | same | 1521.488 | 2000 | 2808.532 | 9297.165 | 727.662 |

Map vegetation detected in both pre-fixed circles at both reference sites, so Whitney is not an all-zero-map candidate. Circles are NOT colony footprints, or island-specific plant area. 2km circles can overlap; no inference that Whitney differs ecologically from Shirley. No snow-history map verified for Whitney; replication of relic vs extant can precede a snow-specific contrast. Need actual 2012/13 Windmill GIS and 2006 Whitney polygons; later Robinson independent region. Prior source-pinned results remain unchanged.