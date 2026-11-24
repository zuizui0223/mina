# Daily spatial concentration of Palmer fur-seal detections (2026-11-24)

Executed descriptive extension on original-source-derived point archive, SHA256 590fa4a032f4e3e21a6e7ecde4a29f7ca0634b3ea1e0acfbfd2550d71640b42d (3,684 eligible detections; Dryad 10.5061/dryad.qv9s4mwp0). Fixed UTM 20S cells. Primary 20m grid, >=5 eligible detections/day, >=3 eligible days/site. Site/day equal weights. Within-day collision probability = sum over cells n_c(n_c-1)/[n(n-1)] then average across days. Between-day collision probability = dot product of daily relative counts averaged over distinct day pairs. No ecological p-value or claim of independent regional replication.

| grid m | sites | within-day % | between-day % | positive sites |
|---:|---:|---:|---:|---:|
| 10 | 10 | 3.9699 | 2.1454 | 10 |
| 20 | 10 | 7.111631 | 4.411916 | 10 |
| 40 | 10 | 12.8460 | 9.5376 | 10 |
| 80 | 10 | 25.8334 | 22.9509 | 10 |

Primary 10 sites, 58 site-days, 3,663 detections. Within-minus-between +2.699715 pp; leave-one-site-out +1.383930 to +2.976667 pp. Site/day-equal 85.740489% of detections in cells recorded on at least two eligible days; mean pairwise daily detected-cell Jaccard 0.280351. For minimum 20 eligible detections per day, all seven eligible sites retain positive within-minus-between contrasts at every tested scale. Concentrations shift among observations while use areas overlap, conditional on survey coverage and recorded days. Individual resighting IDs and exact per-date polygons absent; no individual movement, true occupancy, guano flux, vegetation-change effect or difference between taxa established.

Local reproducibility archive `palmer_seal_temporal_20261124.zip`, SHA256 c9ba1b5b244fc08a3ff78385a43ed2ba0235c6775ab5717a819c5d865ab46c19, contains script, site and day-pair tables, sensitivity summary, provenance. No raw source redistribution.

## Contemporary penguin source audit
- Cimino et al. 2025 (https://doi.org/10.1007/s10980-025-02088-y): 14/15 January 2020 Torgersen/Humble drone-derived breeding perimeters; publisher points to Duke DOI 10.7924/r4sf2xs2w.
- [Catalogue run 45342591761](https://github.com/zuizui0223/mina/actions/runs/45342591761): authoritative DataCite record HTTP 200, Duke dataset/orthomosaic/site-guide endpoints HTTP 202 empty bodies; actual imagery or georeferenced colony polygons NOT retrieved.
- [USAP GPS header run 45342738730](https://github.com/zuizui0223/mina/actions/runs/45342738730): USAP official catalogue and exact 2019-20 file links confirmed, but both CSV requests returned HTML, not CSV. Header checksum failed. No GPS data accepted and land use cannot be inferred from catalogue. Foraging GPS cannot substitute for full colony footprints.
- Next: obtain original georeferenced 2020 Torgersen/Humble drone orthomosaics or author-derived breeding perimeters; validate CRS/date, align to seal survey footprint and compare matched cells. Do not digitize non-georeferenced figures or infer colony boundaries from site centroids.

No change to main, frozen manuscripts, polynya results or previous research claims.