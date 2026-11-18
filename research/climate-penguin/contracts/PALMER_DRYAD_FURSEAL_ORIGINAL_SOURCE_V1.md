# Original Dryad 2020 Palmer Antarctic fur seals — noncausal source gate

Study: Larsen et al., original 2020 Palmer Antarctic fur seal drone surveys. Published Jan 21 2025 on Dryad, DOI **10.5061/dryad.qv9s4mwp0**, original dataset and field survey descriptions at https://datadryad.org/dataset/doi:10.5061/dryad.qv9s4mwp0. Survey dates, seals, surveyed footprints and exposed-land masks are publicly listed. This first stage is a **source retrieval/schema integrity check only** before opening colony-specific seal locations or site-sampled presence/absence.

Predeclare exact original requested filenames:
- `README.md`
- `drone_survey_dates_times.csv`
- `fur_seal_locations_all_surveys.csv`
- `surveyed_regions_land_mask.zip`
- `exposed_land_mask.zip`.

First-party Dryad REST dataset metadata, version and file listing must be available; verify file IDs, exact SHA256, original byte sizes, ZIP CRC, original shapefile members, and CSV schema/count. Do not fabricate source data or missing records if public REST/stream downloads fail (mark HOLD). Source artifacts may contain original public wildlife coordinates; do not embed exact animal georeferences in a tracked repo result or infer nest locations.

**Next stage only after source success**: independently validate original mask geometry CRS, survey footprints and survey dates, crosswalk onto previously verified five 2026 SCAR physical land polygons at fixed Palmer site coordinates (LITC, HUMB, TORG, CHIS, CORM). Determine *surveyed* island areas and exposure/effort BEFORE opening the wildlife location response; classify unsurveyed islands as unknown, never zero seals. Point locations of seals are survey detections (not persistent occupancy/absence), and 2020 data cannot resolve 2007 penguin disappearance nor explain the 2024 static vegetation footprint by itself. Regional seal attendance may be confounded by island terrain, season and detection. It is at best an independent time-specific competing habitat-pressure hypothesis.

This source-gate result cannot establish `penguin abandonment -> greening`, `climate warming -> colony zero`, or seal-driven vegetation change. All frozen PR189 scientific results and independent Paper2 PR199 source gates remain untouched.
