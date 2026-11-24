# Temporal persistence beyond observed use density (2026-11-24)

Executed locally on source-pinned prior point and native-grid tile archives (Dryad 10.5061/dryad.qv9s4mwp0 and Plantarctica 10.6084/m9.figshare.24745956). Primary 20m, >=5 detections/date, >=3 dates/site, >=2 detections/tile. Conditional null holds total detections in each tile and site date counts fixed. Expected number of detected dates is sum_d (1-P_hypergeom(X=0; N,N_d,n_tile)). Outcome (observed minus expected dates)/eligible dates. Pooled site-fixed-effects weighted least squares, equal site weights, mapped vegetation and lichen fractions, log detection count, mean elevation, slope, distance from exposed-land edge. Support >=20 repeated-detection tiles with >=5 vegetation-positive and >=5 vegetation-unmapped per site.

| Scale | Sites | Tiles | Coefficient pp per 10pp mapped vegetation | LOO range |
|---|---:|---:|---:|---:|
| 10m | 4 | 322 | +0.089523 | +0.036888,+0.126152 |
| 20m | 5 | 252 | -0.153975 | -0.397031,+0.307707 |
| 40m | 4 | 117 | -0.655407 | -1.317988,+0.833238 |

20m terrain-unadjusted coefficient +0.001319; site-specific fits 1 positive, 2 negative, 2 rank-deficient. >=20 detections/date gives -0.181013 at 20m. No consistent positive relationship between time-persistence and vegetation beyond total use, no evidence of a negative temporal response either. No p-value, no true absence, no individual persistence, guano flux, or plant-cover change claim. Different spatial support between scales. Bounds and residual identity independently checked.

Local package palmer_seal_persistence_vegetation_20261124.zip, SHA256 51571c06c7508143b4497b8c9e4a2d2995f99b498bd7ff7c6c751935ef4a24cf, contains executed script and all output tables. Point archive SHA256 590fa4a032f4e3e21a6e7ecde4a29f7ca0634b3ea1e0acfbfd2550d71640b42d; tile archive SHA256 6ed568c9ae50acc84a675156dfdf565d9eb7dbdfac0ba61f8cd769d6eba38ffb.

## Independent penguin data route
Official catalogues confirmed Shirley Island 2006 extant/relic/maximum boundaries (10.4225/15/5549ADA38E017; EDS 1539), and East Antarctic colony boundary dataset 1981-2017 (10.4225/15/58f59b52edfef; EDS 4399, 32 linked child records). Relic status is specifically unoccupied in 2005/06, not confirmed abandoned through 2017-2023. [Source inventory run](https://github.com/zuizui0223/mina/actions/runs/45344865291) retrieved original metadata but download endpoints returned frontend HTML, not ZIPs. A separate bounded public object-catalogue workflow was committed as c3e83d859587fc50b1a55bf33f4eac90023cdd55. No new penguin geometries or comparative ecological model yet. Future comparison: verify original polygons, separate overlapping maximum/relic/extant polygons and subsequent reoccupation where supported, match within-island terrain and local plant detection support, do not infer vegetation change from static map. No change to main, isotope or frozen papers.
