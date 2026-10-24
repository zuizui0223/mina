# V38 — Alternative publisher site coordinates do not resolve the Ross Sea island-precision limitation

**Executed 2026-10-24.** We interrogated Oceanites/MAPPPD newly released **version 5.0 (October 21, 2026)** official read-only public SITE API, source version validated, then matched ten prespecified original 2026 New Zealand Ross Sea Adélie colony names to independently published WGS84 MAPPPD coordinates and SCAR ADD high-resolution land polygons. **No MAPPPD observations, penguin count magnitudes, ecological r, or V36 colony-effect refitting.**

**Source provenance:** MAPPPD official source: https://www.penguinmap.com/api/v1/sites/?region=Victoria%20Land&format=json (original metadata SHA256 **70e2cea2355330591fba3d9e68c720335a882b5793c25a7f36b626929494f513**), https://www.penguinmap.com/api/v1/release/ (release **5.0, 2026-10-21**); MAPPPD license CC BY 4.0. The original SCAR ADD v7.12 highres SHP source ZIP SHA256 **66d82fa69f86eb8dbe8b04f01505cb2129feafec608455459ee4ed19d1dc38d4** yielded 17,269 land polygons. The old NZ 2026 census/location source SHAs and V35's 13 survey-year windows were frozen and reproduced. [Actual original-data V38 CI](https://github.com/zuizui0223/mina/actions/runs/40077244401) succeeded.

## Exact names and geography, not outcomes

The ten fixed site IDs contain **seven identical original NZ–MAPPPD names** and three pre-fixed *abbreviated*, but not independently identical, Coulman Island names. All ten official v5 site IDs and expected names were found. Full highres polygon center containment gave: Beaufort Island site **NOT inside land** (uniquely within 2 km; high-res feature 728), Cape Anne **inside** Coulman feature 713 (center + a hypothetical 250 m buffer), Coulman Middle/North/South **near within 2 km** feature 713 but not inside, all four Ross component sites Cape Bird N/M/S and Cape Royds **inside** feature 742, Inexpressible site **inside** feature 720. The v5 published coordinate digits do **NOT prove GPS error accuracy**; full 250m/1000m buffer coverage is merely a hypothetical diagnostic.

Under V35's *unchanged* original colony/year source presence and coastline polygons:

| Comparison fixed before GIS classification | Islands with >=5 original matched-colony annual windows | Shared distinct-island annual windows | Gate |
|---|---:|---:|---|
| **Identical-name, exact land-polygon center only** | **2** | **5** | Fail (<3, <8) |
| Add the three Coulman original-name abbreviations (do not assume same survey identities) | 2 | 5 | Fail |
| Identical-name plus hypothetical 250m disk fully inside polygon | 0 | 0 | Fail |
| Identical-name plus hypothetical 1000m disk fully inside polygon | 0 | 0 | Fail |

The center-only source-windows represent Ross Island and Inexpressible Island; Cape Anne itself lacks a consecutive shared colony survey window despite confirmed Coulman land polygon center. Beaufort's point is offshore of the high-resolution mapped land polygon. The categorical source-named island label and its source-site WGS84 coordinate accuracy are DISTINCT evidentiary claims.

**Scientific decision: HOLD_SITE_IDENTITY_OR_PRECISE_GEOREFERENCE_SUPPORT.** Neither the new MAPPPD v5 API nor high-resolution shoreline precision independently certifies the V36 four-island source-based nesting synchrony as a GIS-location-robust island mechanism. V36's descriptive 61.5% direction concordance, Ross–Beaufort +0.468, Ross–Coulman −0.501, Ross–Inexpressible −0.422 are unchanged, as are the V37 original minute-coordinate envelope failures. Published source sites may not have independent field GPS coordinates; the MAPPPD records may descend from the SAME airborne breeding-colony data or derived site map.

**Next discriminating data type:** an independent authoritative *geographic island name-to-landmass gazetteer*, and original field GPS/uncertainty if available. A gazetteer can validate categorical named island identities even when an approximate nesting-point lies offshore; it cannot establish high-resolution observed penguin nest-point accuracy. A new biological generality test would still need separate unshared original census populations across several sectors, comparable protocol and event source genealogy.

- [Frozen V38 geographic source contract](../contracts/NZ_ROSS_SEA_MAPPPD_V5_GEOSOURCE_V38.md)
- [Machine-readable original site/geographic and year QA](../results/NZ_ROSS_SEA_MAPPPD_V5_GEO_SOURCE_QA_V38.json)
- [V37 original highresolution precision result](NZ_ROSS_SEA_HIGHRES_PRECISION_V37_RESULT.md)
