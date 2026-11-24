# Penguin breeding-site deletion and geographic-support audit (2026-11-24)

Executed local sensitivity on hash-pinned original-derived seal/vegetation point and tile analyses and original Dryad survey geometry. No contemporaneous penguin occupancy density, verified absence, nest-footprint overlap, vegetation change or causal coefficient was estimated.

## Breeding evidence
- Humb/Torg: breeding confirmed in 2019 ASMA plan and January 2020 drone colony study https://doi.org/10.1007/s10980-025-02088-y.
- Dream: 2019 ASMA plan confirms Adélie and chinstrap breeding, not a new 2020 count.
- Pt8: October 2020 Palmer science report confirms gentoo nesting AFTER the Jan–Mar seal survey; conservative additional deletion only.
- Other sites have not established penguin absence. Other marine animals remain potential co-users.
- https://documents.ats.aq/recatt/att658_e.pdf
- https://pallter.marine.rutgers.edu/docs/publications/sitreps/2020b/2020-10%20Palmer%20Science%20Report.pdf

## Actual reaggregation (percentage points; equal site weights)
| Deletion | Point sites | Observed−expected mapped vegetation+lichen | 20m tile sites | High−low vegetation-only | High−low lichen |
|---|---:|---:|---:|---:|---:|
| None | 10 | +3.581561 | 9 | +3.040452 | −0.629120 |
| Humb/Torg | 8 | +2.817012 | 7 | +3.181189 | −0.554736 |
| +Dream | 7 | +3.237043 | 6 | +3.711387 | −0.647193 |
| +Pt8 | 6 | +2.853493 | 5 | +4.290798 | −0.776631 |
| +ShortE high leverage | 5 | +3.098347 | 4 | +1.537109 | −0.970789 |

Five remaining tile sites: four positive, one tied for vegetation-only. All-four deletion does not demonstrate independence from penguin influence, because unrecorded breeding and other seabirds remain unresolved; historical and spatial support differs.

## Original survey polygons, geographic grouping
Minimum polygon distance, not centroid distance, EPSG:32720. Six remaining survey sites form two connected groups at 500m: AmslE/ER and BonPt/KCove/ShortE/ShortW. Point group means −0.898546 and +4.729513 pp; vegetation-only tile group means +2.470800 and +4.745798 pp (ER lacks matched tile support). Equal group means +1.915484 and +3.608299 pp respectively. All six connected at 1km. Local descriptive association only; no independent geographic replication or new p-value.

## Reproduction
Executed script and tables packaged as palmer_penguin_seal_overlap_20261124.zip, SHA256 c3d1c3b7715f178173ee12ed7b03775be3f7194bde431b00db67341ac769be2c, delivered in conversation. Three input archive SHA256 values:
- Point package: 590fa4a032f4e3e21a6e7ecde4a29f7ca0634b3ea1e0acfbfd2550d71640b42d
- Density package: 6ed568c9ae50acc84a675156dfdf565d9eb7dbdfac0ba61f8cd769d6eba38ffb
- Original Dryad: 7a5f991864d9a433cb9667626d27cc6f05cd43368097a8b57fd02340a9bc17af

Next source gate: georeferenced contemporary penguin occupancy/nest polygons, not island centroids. Direct retrieval of ASMA map PDF did not succeed locally; historical maps do not represent 2020 footprints. Need independently validated matched plant imagery for temporal response. PR217 branch only; no main, Paper1/2 or isotope manuscript changes.