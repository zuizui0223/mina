# Step 2 — SST source and trait-definitions freeze candidate (2026-11-07)

## SST input (model fitting NOT yet authorized)
Source: NOAA/NCEI OISST v2.1; DOI 10.25921/RE9P-PT57. Original NOAA PSL monthly 0.25° dataset. UK JNCC March–May each original year; no endpoint reselection. Site original Start.Lat/Long -> nearest one wet cell within 50 km with all 6 months; that cell must stay unchanged across endpoints. All fixed matched Site.ID components must match; use equal sites (not abundance) weights to define two network-level temperatures. W is 10*(SST1-SST0)/(year1-year0), in °C per decade. Raw original site counts/locations remain ephemeral in Actions. NCSS response URLs and byte hashes recorded; errors block the entire join rather than creating invented SST.

SST under sea ice is an interpolated physical value, not penguin prey availability. JNCC survey start coordinates do not prove fixed colony polygons, and spring SST need not precede every seabird count. South Atlantic/Antarctic Step1 rows are not resampled with UK seasonality.

## H2 trait-data audit
Coulson (2016), Waterbirds 39:229–240, doi:10.1675/063.039.0302 explicitly distinguishes natal philopatry from interannual adult nesting-area fidelity. Table 2 provides heterogeneous estimates including approximate values, thresholds such as ">95%", and qualitative labels "high"; do not encode these as comparable exact annual same-breeding-site probabilities.

An independent source, UKCEH *Isle of May long-term study annual return rate 1988–2021*, doi:10.5285/1624fe45-0deb-4bcd-9f13-75578693aaae, covers five relevant species (Atlantic puffin, common guillemot, razorbill, European shag, black-legged kittiwake), but the proportions observed in consecutive seasons are not corrected for individuals missed by observers and are **not** conditional probabilities of reuse of the same physical nesting site. BTO's RAS separates annual survival from re-encounter. They must not be substituted for the Step2 H2 numerical F.

Status: keep strict F missing until original definition, denominator, study period, observation process and spatial reuse unit are checked; do not claim an H2 test or modify Holm family to seek positive significance.
