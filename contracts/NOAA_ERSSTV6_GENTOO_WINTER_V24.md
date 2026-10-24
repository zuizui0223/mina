# V24 — Independent NOAA ERSSTv6 prebreeding marine-temperature exposure, exploratory

Frozen 2026-10-21 AFTER the three-BAS V23 bird-growth gradient was inspected. An environmental plausibility check, explicitly NOT independent preregistration or causal discovery. Closed V14–V17 and Ecology PR189 unchanged. Do not tune variables, months, lags, source grid/radius or species to seek a positive sign.

## Biological prediction, alternatives
V23 source-authenticated same-provider Gentoo nest-growth changes were more aligned within South Georgia (+0.514 Bird Island–Maiviken) than with distant Signy (−0.334, −0.668), at 8 common annual windows 2011–2018. A candidate *regional marine forcing* account predicts (1) **regional prebreeding SST changes themselves** are more concordant Bird–Maiviken than either Signy distance contrast, and (2) winter-to-winter SST shifts may associate with nest-count growth within the three monitored series. Neither an SST correlation nor aligned signs is a demonstration of temperature causing breeding changes or of krill, winter foraging or island boundary effects. Alternatives include air temperature, wind, precipitation/snow, productivity, fisheries, nest-stage/observer differences and breeding dispersal.

## Independent NOAA environmental original
NOAA Extended Reconstructed Sea Surface Temperature **ERSSTv6** (current V6, NOAA PSL THREDDS official gridded monthly dataset), not the no-longer-updated v5. Official source dataset:
https://psl.noaa.gov/thredds/catalog/Datasets/noaa.ersst.v6/catalog.html
Original full sst.mnmean.nc (not downloaded wholesale): https://psl.noaa.gov/thredds/ncss/grid/Datasets/noaa.ersst.v6/sst.mnmean.nc
Use **only** a NetCDF Subset Service source request with sst, 2009-01-01 to 2019-12-31, region latitude −62 to −52 and longitude 312 to 326 **degrees east** (0–360 original). Require official psl.noaa.gov HTTPS, bounded size <=12 MiB, actual NetCDF magic, CF axes/units, monthly time stamps, source SHA256 and no source changes between 2 steps. The NOAA original 2-degree field is regionally averaged reconstructed SST, not a contemporaneous fine-scale coastal foraging or near-nest observation.

Original site reference coordinates fixed prior to environmental values:
- BAS Bird Island station −54.000, −38.050 longitude west → 321.950 E. Official BAS https://www.bas.ac.uk/polar-operations/sites-and-facilities/facility/bird-island/
- BAS Maiviken Gentoo source −54.246, −36.510 → 323.490 E. UK Polar Data Centre / BAS https://data.bas.ac.uk/full-record.php?id=GB/NERC/BAS/PDC/01487
- BAS Signy station −60.7167, −45.600 → 314.400 E. BAS history https://legacy.bas.ac.uk/about_bas/our_history/stations_and_refuges/signy.php

Use closest **published original ERSST grid-cell centers** in the fixed spatial subset for each site (within 1.1 degrees per axis); no interpolation or cell repositioning after seeing SST values, no choosing a warmer alternative for Bird or Signy. Report original actual grid centers, axis spacing and any source land/missing mask.

## Exact predeclared exposure and comparison
- Prebreeding winter SST(y): arithmetic average of the three original **July, August and September** monthly SST observations at the chosen fixed grid cell for austral breeding start year y. No other month/lag/exposure adjustment, no mixing sea-ice values with SST. Every month must be valid, unmasked and in physically plausible original-source range −3 to 35 Celsius.
- For the original V23 growth start years y=2011,...,2018, assign change ΔSST(y) = winter_SST(y+1) − winter_SST(y). This matches the year-over-year breeding census response difference and avoids level conflation. Retain all 8 windows or STOP without environmental association. Source must include exactly 9 winters (2011–2019) for all 3 sites, with all 27×3 monthly cells.
- Re-download exact original Bird/Maiviken/Signy BAS sources and SHA-check as before; independently reproduce preserved V23 near-minus-mean-far Δr=+1.0154800142899 and its exact 8 start years before fitting V24.
- Primary SOURCE PHYSICS result: three winter-ΔSST pairwise Pearson r on the **same 8 windows**, and fixed near-minus-average-far r. Next, independently report three within-location Pearson r between ΔSST(y) and Gentoo nest/pair annual log changes on those exact windows. No p values, and no regression feature selection or partial correlation with just eight time windows.
- No claim that temperature or regional marine environment caused the avian result, even if both environmental and bird-distance gradients are positive. Need external prey, meteorology, real nesting patch availability, seasonally matched observation effort and replicated island/mainland pairs to identify an island mechanism.
- Preserve machine-readable original source metadata, SHA, selected 2-degree grid centers, winter SST and source-only derived deltas, and r values. Do not store/reprint biological original absolute nest/pair counts.

If original server not accessible or axes/data fail, a SOURCE STOP is scientifically appropriate; do not silently switch environmental data providers, SST versions, geographic cells or seasons after seeing the result.

## Post-source-access missing-month diagnostic (before any SST-breeding effect)
The original V24 source NetCDF subset verified the three geographic cells but returned an incomplete Signy winter (September 2011 unavailable). Under the frozen complete-eight-window rule no environmental correlation was estimated. To distinguish a genuine publisher NetCDF _FillValue/mask from nonfinite or physically out-of-range values, the code now exports a bounded reason-by-cell diagnostic WITHOUT accepting any new data, changing source/grid, reducing required months or fitting the biological outcome. A missing Signy September value remains an unavailable exposure, never a measured 0°C or inferred sea ice concentration.
