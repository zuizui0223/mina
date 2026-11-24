# Original Dryad seal detections × Plantarctica vegetation, 2026-11-24

**Executed locally on both original ZIP files; exploratory spatial association only, not a vegetation-change effect.** The previous Dryad HTTP 401 was resolved by the user's original download. Plantarctica was recovered from [original-source Actions artifact](https://github.com/zuizui0223/mina/actions/runs/45327603485/artifacts/14890995110).

- Dryad DOI 10.5061/dryad.qv9s4mwp0, supplied ZIP SHA256 `7a5f991864d9a433cb9667626d27cc6f05cd43368097a8b57fd02340a9bc17af`.
- Plantarctica DOI 10.6084/m9.figshare.24745956, original ZIP SHA256 `7e304e7a610d03287577e91faff05c009cf82039ae5f227763c37730a548a236`.
- UTM 20S (EPSG:32720); 102 unique survey site-date records, 98 in the 12 available survey masks, 4,131 detection records all matched to survey metadata, 3,716 inside their named survey mask, 3,684 with valid terrain/access raster values. 10 positive-detection sites, 69 positive site-days. Repeated observations are not unique seals. Two Jbn sites lack a released survey mask; 415 detections outside/missing matching masks and 32 lacking eligible raster support excluded. Humble/Torgersen surveyed-mask centroids are 14.25 m/44.25 m from archive MAPPPD points.

## Fixed exploratory comparison
Native 2 m DEM and mapped vegetation+lichen (exclude snow algae), same-site available cells in elevation (5,10,20 m), slope (5,15,30 degrees), exposed-land-edge distance (10,30,60 m) strata, minimum 10 native cells per stratum. Equal date weight within sites and equal site weight across 10 sites. Exact point-vector/raster map agreement 3653/3684. Plantarctica is a multiyear optical composite, not a 2020 botanical truth or annual response.

| Site | eligible observations | actual overlap % | terrain-matched expectation % |
|---|---:|---:|---:|
| AmslE | 477 | 1.402 | 2.627 |
| KCove | 565 | 17.392 | 5.181 |
| BonPt | 447 | 9.513 | 5.918 |
| Pt8 | 121 | 10.998 | 5.460 |
| ShortW | 238 | 14.796 | 13.312 |
| ShortE | 102 | 4.709 | 3.080 |
| Torg | 366 | 11.849 | 2.798 |
| Humb | 459 | 38.590 | 34.361 |
| ER | 71 | 0 | 0.572 |
| Dream | 838 | 0 | 0.123 |

- Equal-site/day actual overlap **10.924876%**, expected **7.343315%**; difference **+3.581561 pp**, 7/10 positive sites; leave-one-site-out mean difference +2.622770 to +4.115653 pp. No inferential p-value; all sites are clustered locally.
- First point per fixed 10 m cell within each site-day: +3.413493 pp, 7/10 positive; max observed count date per site (ties earliest): +2.307671 pp, 6/10 positive.
- Separate class exact point vs raster area: mapped Vegetation +3.136176 pp (8 positive/2 negative), Lichen +0.713751 pp (2 positive, 4 negative, 4 zero). These are descriptive sensitivity checks, not an additive decomposition of the union raster contrast.
- Median used slope below median available in 9/10 sites; elevation 6/10. Exploratory resistance cost from any exposed-land polygon boundary (2 m 8-neighbor grid, penalty 1+(slope/15)^2) yields site/date mean percentile 0.492729; conditional rank 0.492693 (6/10 below 0.5; LOO range 0.465162–0.512117). No consistent incremental terrain-cost association. Boundaries are not verified landing routes. Do not optimize resistance parameters to manufacture support.

## Interpretation
Fur seal detection locations overlap mapped vegetation/lichen more often than expected under this coarse terrain-matched availability definition, opposite a simple spatial avoidance hypothesis. Does NOT show seals increase vegetation, damage vegetation, or select plants directly. Temporal overlap of the 2017–2023 optical composite with the 2020 seal observations, map classification error, co-occurring penguin/other animal activity and microhabitat differences remain. No observed seal positions at Litchfield in the released data; never substitute the MaxEnt prediction as observed counts. No sea-ice-to-seal or penguin-to-greening mechanism inferred.

The full executed local point/cell tables, per-site/day outputs, source-pinned reproducer and summary JSON were packaged as `palmer_seal_vegetation_analysis_20261124.zip` in the associated conversation. Raw publisher archives are not republished here. The original PR214 isotope manuscript, main and Paper1/2 are unchanged.
