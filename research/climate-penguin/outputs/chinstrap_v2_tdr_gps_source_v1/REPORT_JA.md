# Chinstrap BAS Version2 GPS×TDR source audit: same-deployment potential

**2026-10-31 — original-data source gate, no dive outcome read.** Main goal is to replace crude modelled krill accessibility on all GPS tracks (which includes transit and near-land fixes) by a source-verified subset of GPS positions linked in time to observed diving pressure records. This is relevant to the same-species matched-year comparison of Signy/Laurie/Powell/Monroe already implemented.

Original BAS PDC first-party:
- GPS v2 DOI https://doi.org/10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92
- TDR v2 DOI https://doi.org/10.5285/da13e049-be2b-4345-bbdd-ab960cb24731

BAS explicitly warns that Version1 contained mismatched GPS/TDR files, fixed in v2, and that TDR v2 contains original pressure and temperature time series, **not interpreted dive summaries**. TDR nominal cadence is 1 s, instrument pressure in dbar, not necessarily zero-corrected depth (temperature/drift offset); valid dive detection needs a scientifically defensible baseline algorithm, per-deployment QA, and GPS–TDR clock alignment. The original paper describes pressure zero-offset correction as necessary and all land points excluded. These are measurement gates, not assumptions to hand-wave.

The audit script reads only the ZIP central directory, original TDR and GPS member names, tiny CSV header prefixes, first timestamp formatting and publisher deployment IDs, preserving island codes SI/LI/PI/MI (Powell PI### rather than PIC### in some publisher filenames). It outputs the precise GPS/TDR overlap and every TDR member's header, original byte count and CRC. NO raw pressure values are used to choose thresholds or favorable models. Do not infer GPS-only deployments as animals that did not dive.

Next only if actual header/time/coverage gate passes: (1) detect dives with an explicit per-tag surface-offset adjustment and predefined 2/5/10 dbar thresholds plus ≥10-second duration; (2) map peak-dive timestamps to nearest **original** GPS fixes within ±5/10/20 minutes, preserving clock and temporal uncertainty, no invented locations across large gaps; (3) intersect modelled krill surface cell at the matched dive-GPS position, conserving individual deployments as units; (4) compare all GPS visited cells vs dive-matched locations and same-species matched-year islands, with unit-specific missingness. The source Freer GAM itself fits 2011–2020 IMR observations, ice and salinity, so any pattern remains a **within-model geographic index, not an independent climate or krill observation**, even if dive events line up. A dive alone is not confirmed krill consumption.

Original GPS and TDR ZIP contents are downloaded only in dedicated GitHub Actions and full native pressure data are NOT committed to the repository. No frozen mina paper or 216 comparison updated. Full transfer to 2050/2100 penguin abundance, N_eff or vegetation remains NOT validated.
