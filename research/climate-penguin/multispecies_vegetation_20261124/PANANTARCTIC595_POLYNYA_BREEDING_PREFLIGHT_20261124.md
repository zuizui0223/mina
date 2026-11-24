# Pan-Antarctic native polynya expansion and observed breeding-interval preflight

2026-11-24. Source-only native extraction launched at [commit 959f7b3](https://github.com/zuizui0223/mina/commit/959f7b3b40ac5267b4a2d91b0343ca8360d36783), [run 45404870371](https://github.com/zuizui0223/mina/actions/runs/45404870371). No new outcome fit or physical period result at preflight checkpoint.

## Exact inputs

- Original source atlas 595 locations, 18 regions, archive 13669533413, run 42610664607, SHA256 add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a. Atlas member SHA256 543056ded5e2b896ba5f447db690f6537ff07cecb78d89d66b4868728e53de24; 2456 actual count rows member SHA256 ab131e5828674b88623d372ce8a1758a6bb1fc63972301f9676534ebf870d28c. 707 fixed site-species series each has one known survey method; unique site/species/season.
- Exact 588 locations x 28 calendar years (1993–2020) Aug-Nov marine source from artifact 13829236358, SHA256 64a8e9832e254171139d78bb22351d6c9a3acf490356931b2635ed5b108d94b5. Original member SHA256 3a1d45f88249fcaf6fc5bca4e2ce10afdf79736a063bbfccbc4bde5d10390969. Every coordinate, region and site ID matches atlas (1e-7 degrees tolerance). All four original months complete.
- Native DEEP-AA publisher ZIP MD5 f3f958389cc5e67ac1c4e3a6ee164318, SHA256 b05a36aa4e775d69c06e2ffa897a8de8a20318b65f6478298167f73cc9f7c3f9, native WGS84 geodesic membership, EPSG:3412 corrected area. 100km primary and 25km secondary. June-Oct each month >=80% valid native days; valid 15 calendar winters 2004–10 and 2013–20. Missing 2003 and 2011–12 stay missing. Sparse matrix extraction must reproduce previously verified 23 sites (828 requested winter rows, 3450 complete calendar-month rows) to tolerance 1e-12.

## Preflight actually executed before opening new polynya outcome associations

Require consecutive observed counts within the same fixed known-method series, two positive observed endpoints, and all years between start+1 and end in the 15 available native calendar windows. No interpolation and no jumping across a recorded zero. 460 candidate intervals (1–5 years) on 588 physical sites, before repeat support (>=2 intervals/site/species). Primary annual interval, secondary 1–5 year intervals. Ground-only sensitivity, not a search for a method-dependent positive result.

| mode | species | records | sites | regions | 250km blocks |
|---|---|---:|---:|---:|---:|
| annual fixed known method | ADPE |45|11|4|6|
| annual fixed known method | CHPE |87|19|3|5|
| annual fixed known method | GEPE |128|30|3|5|
| 1–5 years fixed known method | ADPE |89|27|5|9|
| 1–5 years fixed known method | CHPE |131|25|3|5|
| 1–5 years fixed known method | GEPE |199|39|4|6|
| annual ground only | ADPE |27|7|2|3|
| annual ground only | CHPE |87|19|3|5|
| annual ground only | GEPE |126|29|3|5|
| 1–5 years ground only | ADPE |46|12|3|4|
| 1–5 years ground only | CHPE |131|25|3|5|
| 1–5 years ground only | GEPE |192|37|4|6|

The counts are potential source support conditional on native calendar-year availability, not verified local polynya completeness yet. Multi-year intervals add geographic support, particularly for Adélie. Many Antarctic sites still lack repeated observations. Method definitions differ from the earlier 23-site raw ground-only archive: not an isolated test of expanding geography.

## Locked analysis

Response ln(N_end/N_start)/(end-start). For primary annual models, current calendar-year physical values; for multi-year, mean of all native observed years start+1...end (annualized response, not annual census reconstruction). Separate species, site equal weights; site and endpoint-year FE. Primary predictors winter polynya fraction in pp, Aug-Nov sea ice /10pp, salinity /0.1, temperature /C. Common complete rows for base and full; >=3 sites, >=2 intervals/site, full slope rank, >=5 residual degrees of freedom. Weighted dummy QR/FWL numerical check against direct weighted dummy regression. Prespecified 25km and ground-only diagnostics, omit sites/blocks/regions, forward 2004–10 vs 2013–20 known-site predictions, not future forecast. No pooling site counts as independent regions or climate-to-land causal chain. Calendar labels may differ from actual breeding seasons. No inferential p-values proposed given sparse regions. Do not tune windows, radii, or filters for significance. Local analysis script preflight executed, SHA256 f8c80ea8b98e1b2d0cf95eab2ce35c1a100c66fedd904a6113bcc42d52567da8. Full mode remains unexecuted until native physical artifact validated. Main/frozen manuscripts unchanged.
