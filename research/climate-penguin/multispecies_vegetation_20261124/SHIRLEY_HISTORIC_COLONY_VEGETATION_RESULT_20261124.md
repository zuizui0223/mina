# Shirley Island original historic breeding polygons × mapped contemporary vegetation

Executed locally using the user's original AADC EDS 1539 archive and previously verified Plantarctica original source. Source DOI 10.4225/15/5549ADA38E017 (Woehler & Bricher 2015); colony ZIP SHA256 e9386997fe3f743aaca47c996baf734198dae7a19cb626b0b43957ea043109c3. Plantarctica DOI 10.6084/m9.figshare.24745956; ZIP SHA256 7e304e7a610d03287577e91faff05c009cf82039ae5f227763c37730a548a236. Source 110 polygons: 58 extant, 22 relic, 30 historical maximum; 47 invalid geometries repaired, absolute summed area changes <1e-5 m². All source status labels refer to 2005/06 or historical maximum, not modern occupancy. Exact unions and differences in original UTM49S. Modern optical composite 2017–2023, not a time series.

| Polygon union definition | Area m² | Mapped vegetation overlap m² | Mapped cover % |
|---|---:|---:|---:|
| Extant | 14372.244704 | 0 | 0 |
| Relic minus extant | 7249.682198 | 230.378011 | 3.177767 |
| Maximum minus extant | 2557.172594 | 0 | 0 |
| Maximum minus extant and relic | 2527.979859 | 0 | 0 |

Lichen and snow algae have zero mapped overlap in all definitions. Relic positives: Area_ID 3, 4, 84; three original polygons intersect four mapped vegetation features, but all three form a single 50m-connected spatial group. Removing each positive polygon in turn leaves relic cover 0.682124–6.803375%; this is not independent spatial replication. Fixed 8 directions translation of vegetation geometry by 2m yields relic cover 2.854066–3.512723%, 10m yields 1.640559–4.098763%, extant remains zero at both; 10m is sensitivity scale not calibrated map error. Nearest mapped vegetation to extant ~18.9877m. 25 common Colony_ID extant/maximum pairs; no mapped vegetation in either extant or maximum-minus-extant. Do not conclude every historical maximum polygon is proven former occupation. Current reoccupation, historical plant status, terrain/drainage and plant classification ground truth unmeasured. No p-value, recovery, guano flux, or comparison of causal effects between animal species is supported. Positive contrast is local, spatially clustered.

Reproducible package delivered in conversation shirley_colony_vegetation_20261124.zip SHA256 5a3844739d0e2268bfc3040159ba79848c7a5d65e06fbbe7f55dc9944a4a4780. Includes executed script, summary JSON, per-polygon, leave-one-polygon-out, translation and shared-ID outputs and map. Original inputs not republished. Next gate: Anders (2007) original 2m DEM and reliability layer, official https://data.aad.gov.au/metadata/records/shirley_dem; source workflow commit efada1494d5d09683b81522bf1976cd715c6f1ac. Main and manuscript unchanged.
