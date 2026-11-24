# Shirley Island historical breeding footprints, vegetation and terrain reliability

Executed local original-source analysis (2026-11-24). Source Anders (2007), Australian Antarctic Data Centre, https://data.aad.gov.au/metadata/records/shirley_dem (CC BY 4.0). 2m native E00 grid, 740 x 470 cells, UTM49S, 127271 finite values. Historical 2001 aerial photography; 2005/06 GPS control. Source metadata state unresolved +3m elevation adjustment and unreliability over snow/ice/guano. 232 snow/ice polygons, 1050 derived contours. North-first raster orientation checked against contours (RMSE 6.969m vs reversed 23.765m; median absolute 0.634m); contours are derived, not independent accuracy validation.

## Exact vector partition
| 2005/06 status | Historical snow/ice mask | Area m2 | Modern mapped vegetation m2 | Cover % |
|---|---|---:|---:|---:|
| extant | outside | 14372.244704 | 0 | 0 |
| relic minus extant | inside | 1740.831838 | 174.822404 | 10.042464 |
| relic minus extant | outside | 5508.850359 | 55.555607 | 1.008479 |

75.885% of the 230.378011 m2 of mapped vegetation in historic relic polygons lies within the historical snow/ice reliability mask, which covers 24.01% of relic polygon area. Extant has zero intersection with that mask. This is a cross-source spatial overlap, not observed snow retreat or demonstrated vegetation colonization. Old snow/ice and modern botanical map errors, changing occupancy and substrate remain alternative explanations.

## Terrain matching
Native 2m cell exact intersection areas reproduce prior polygon-area and vegetation-area sums. Conservative primary mask excludes cells and 5x5 local plane-fitting neighbourhoods touching historical snow/ice polygons or missing elevations. Extant 14096.061177 m2, zero vegetation; relic 4683.092374 m2, mapped vegetation 36.727641 m2 (0.784260%). Mean source elevation on this support: extant 24.265323m, relic 13.820074m (absolute datum uncertain). Match on 5m elevation, 10 degree slope, aspect quadrant (flat <=5 degrees), >=20m2 of both categories per stratum, weight min area. 14 strata, common weight area 1837.451203 m2; observed standardized mapped cover extant 0%, relic 0.334864%. 4488.294493 m2 of eligible relic and 7425.967844 m2 of eligible extant in supported strata. Alternative strata or gradient scale +0.326923 to +0.563557 pp; including unreliable ice area +4.104789 pp. Adding local 100m or 200m spatial blocks leaves 2 or 4 strata with common weight 146.248556 or 290.635374 m2; both have ZERO mapped vegetation in each status, so local positive contrast is not identifiable on vegetated support. No inference of equal plant cover or causal absence. No p-value, independent region replication, current breeding occupancy, annual vegetation change or comparative species effect.

## Reproduction
Local package shirley_terrain_vegetation_20261124.zip (SHA256 9cbe0a3322869c71d705b80d0bf2081c5a8e63598086aa9e4c840a95a4b2934d), delivered in associated conversation; includes executed Python script (SHA256 593f6a7ba8451cb9bb33dba3e36df72e8cbbcf3085b9b62c348c7f3584b20d28), cell areas, matched strata, all sensitivities, map, summary and independently reaggregated validation. Input SHA256:
- Original colony GIS: e9386997fe3f743aaca47c996baf734198dae7a19cb626b0b43957ea043109c3
- Plantarctica: 7e304e7a610d03287577e91faff05c009cf82039ae5f227763c37730a548a236
- shirley_dem.zip: 08715cdb697bba4e1dcbeb8902eac3da5086b7e2565fce92c77e9204e785f543
- shirley_contours_reliability.zip: f7de02f05f3f724aabc43f2a82c8f4ffbc4dafb19d4e7cd69ecc3021f1baf39c

Interpretation: original unadjusted relic-vegetation spatial association is largely located in historic snow/ice terrain, motivating a separately measured snow persistence/retreat and breeding history comparison. Do not claim abandonment drives greening; the current source support cannot separate mechanisms. PR217 research branch only; main and frozen papers unchanged.
