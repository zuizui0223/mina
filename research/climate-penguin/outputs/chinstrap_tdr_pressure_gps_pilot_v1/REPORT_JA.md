# Chinstrap TDR pressure + GPS clock overlap four-island pilot (not foraging conclusions)

Date 2026-10-31. Source-only gate succeeds for original [BAS v2 TDR](https://doi.org/10.5285/da13e049-be2b-4345-bbdd-ab960cb24731) and [GPS v2](https://doi.org/10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92), with **300 exact source-justified original deployments containing both**, across Signy108, Laurie60, Powell68, Monroe64. 317 original TDR files include 3 empty/header-only SIC members; remaining **314 contain dated raw pressure, all in dbar**. Source TDR has six actual header schemas (pressure and DateTime common, order/temperature differs). Raw TDR is **4.176 GB uncompressed** and 317 files, thus we begin with a small, fixed original-deployment pilot instead of treating all raw pressure as valid diving.

Original four pilot ids fixed by the first nonempty GPS+TDR common published member in each island, before opening any pressure outcomes:
- Laurie LIC001, Powell PI001 source TDR filename PIC001, Monroe MIC001, Signy SIC004.
- Publisher ID difference at Powell is explicitly \`PIC001_TDR.csv\` versus \`PI001_GPS.csv\`; map only this numeric-suffix identity, retain actual native source name. Do not match unrelated tags.
- Read all original TDR pressure/timestamp values for each of those *four* fixed files, no outcome-based subset.
- Provisional pressure zero-offset: 1st percentile within fixed 60-min windows with ≥300 finite measurements, piecewise-linear interpolated across hours. Record zero-offset range and sample gaps. This is *not* validated surface detection; alternative ZOC and pressure sensor baseline must be checked before ecological interpretation.
- Potential dives: 5 dbar (secondary 2/10 dbar), ≥10 seconds above cutoff, maximum between-sample time gap 3 sec. Peak TDR pressure time recorded.
- GPS pairing only if bracketed by *actual* previous and next source fix in same original tag within 600 seconds and candidate dive peak within 300 seconds of an original fix; no shifting clocks to fit desired biology or interpolation through long GPS gaps.
- Record count of TDR finite points inside original GPS time coverage, number of candidate pressure dives, pressure drift, and fraction with strict GPS time brackets. No raw GPS coordinate or TDR pressure series published in the derived artifact.

Foraging is **not** directly observed by raw pressure events; no prey capture, no sea-ice/salinity causal effect, no source years' modelled krill extraction, no island effect on reproduction. The pilot decides whether 4-island TDR event-location analysis is technically and scientifically feasible before reopening all 4GB raw series. Published diveMove ZOC and BAS original sensor metadata still require validation, with the long-gap/tag-attrition risk documented in \`chinstrap_v2_gps_bracketability_v1\`.

Run via GitHub Actions \`climate-penguin-chinstrap-tdr-dives-4-island-source-pilot-v1\`, output pilot decision and fixed numeric sensitivity on the 4 exact source tags. Original PR189 and PR199, existing 216 tests and 2050/2100 future numerical forecast NO-GO remain unchanged.
