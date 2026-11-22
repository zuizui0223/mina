# Adelie RAATD × winter-polynya temporal support: independent source gate (2026-11-22)

**Outcome:** Winter-synchronous track overlay is **not possible** with the official filtered RAATD Adélie CSV and DEEP-AA 2003–2022 support. No behavioral model fitted; do not replace winter tracks with summer tracks.

Official source: https://zenodo.org/records/3722948 (filtered-noTMB ZIP, MD5 `168e5b9b5c4ed20bb84dd00145acb0a5`). Source-run: https://github.com/zuizui0223/mina/actions/runs/45029523241 . The zipped archive passed MD5 and CRC. Exact species table `ADPE_ssm_by_id_predicted.csv` contains **90,202 filtered position estimates** from published **520** Adélie individuals, 1991-11-25 through 2013-01-20.

## Decisive month and year census
- 6–10 June–October fixes across **all** available years: **4,010**.
- Winter fix years: 1993 (765), 1996 (12), 1997 (581), 1998 (2,652).
- **Zero June–October fixes 2003 or later**. Consequently **zero winter tracks overlap DEEP-AA, available from 2003 onward**, and zero fixes overlap the original Adélie 439-season 2004–2010 winter covariates.
- For *following* Nov–Feb breeding seasons whose November start year is 2004–2010: **22,093 filtered fixes** from **171 unique individual_id strings** across **6 breeding seasons**. This counts filtered locations and individual identifiers, not spatially independent units, foraging trips, or verified breeding-stage samples.
- Filtered location uncertainties are included in the source columns (`longitude_se`, `latitude_se`). Neither colony ID nor original tracking deployment coordinates are in the species position CSV. The separate deployment metadata are still needed to establish independent site-years.

## Go / no-go
- **NO-GO:** winter position × simultaneous winter coastal-polynya mask, any season in common with DEEP-AA.
- **POTENTIAL:** preceding Jun–Oct polynya exposure × following summer maximum foraging distance/duration, after matching real track deployments to winter site-year data and stages.
- **NOT YET FROZEN:** the lagged summer outcome hypothesis. Stop if deployment metadata reveal fewer than five independent colony-years across at least three colonies, or if deployment stages cannot be standardized. Avoid sampling specifications conditioned on a favorable isotope direction.

This is a **feasibility result only** and does not confirm diet change, a predator–polynya mechanism, or breeding responses. The existing 439-season isotopic manuscript remains unchanged.
