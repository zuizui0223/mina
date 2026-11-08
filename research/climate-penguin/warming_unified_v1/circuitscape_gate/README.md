# Circuitscape applicability gate — Antarctic breeding-colony marine connectivity

**2026-11-08, separate exploration on top of climate PR #206.** This gate tests whether Circuitscape can be *applied meaningfully* to the currently available physical and biological observations. It does not claim an effective-resistance estimate, penguin movement, or a validation of the warming manuscript's demographic response.

## Biological question

> Does a changing marine resistance network make island/colony movement opportunities more or less accessible, and are those opportunities ever demonstrably associated with actual redistribution of **breeding individuals** rather than just local counts?

Two distinct outputs, not interchangeable:

1. **Physical/opportunity model:** Pairwise Circuitscape effective resistance and current-flow density on ocean grids, conditional on explicit sea-ice-dependent resistance scenarios, climate period and coastline mask.
2. **Biological validation:** Observed between-breeding-site transitions of marked individuals, independently calibrated occurrence/colonization events, or a separate individual GPS route use test (foraging only). Neither static colony counts nor a resistance map establishes breeding dispersal.

### Already available, and its actual scientific meaning

- Exactly 40 original MAPPPD climate-anchor source coordinates: `outputs/sic_spatial_coherence_macro40_v1/macro40_site_coordinates.csv`, pinned Git blob `5a211a0eaa63b6a5d3516353dd9431428618dbd3`.
- Six strict same-year Adélie/Gentoo co-breeding sites: ARDL, BISC, LION, LLAN, PCHA, PETE. These occupy only two geographic regions. Original measured nesting species counts and their different site-year windows were already audited; a point may be a dataset monitoring label rather than a geolocated nesting polygon.
- Original EUMETSAT OSI SAF **OSI-450-a1 v3.1**, 25-km Southern Hemisphere EASE2 sea-ice raster, 1979–2020. The prior long-lag data gate verified 1979–2020 SIC continuity and original monthly/daily match in 120 site-months, but those are nearshore **spatial averages, not spatial resistance rasters**. The present source-node gate fetches original NetCDF spatial pixels, keeps unknown ocean pixels separate from land and zero-SIC.
- Previous original Chinstrap GPS×sea-ice binary 4-/8-neighbor graph analysis: 45 matched satellite/GPS days, 4,320 island-day settings and no *disconnected low-SIC marine component* under the explored 15/30/50% thresholds. Source: `outputs/chinstrap_ice_graph_connectivity_v1/REPORT_JA.md` and [successful original data run #41193469710](https://github.com/zuizui0223/mina/actions/runs/41193469710). This does not rule out **relative continuous resistance differences**; it does rule out presenting the same coarse pixel thresholds as newly discovered hard barriers.
- Palmer resighting audit: `results/PALMER_MARK_RESIGHT_DATA_AUDIT_RESULT_V1.json`. Banding and repeated searches exist, but the needed **public individual ID → later breeding colony/status** crosswalk was not found. Hence no *direct empirical breeding dispersal* validation can be performed from those inspected tables. BAS Chinstrap GPS/TDR data are **foraging movements**, not between-year breeding settlement.

## The first blocked-or-go gate (no ecological outcomes examined)

1. Reconstruct exactly six original source site coordinates and their all 15 WGS84 pairwise geographical distances. Flag pairs closer than 25 and 50 km. Close points are **not proven to occupy the same ocean grid cell** just because their geographic distance is less than a raster cell width.
2. In a **fixed original 1993-09 and 2018-09 OSI monthly sample**, locate the nearest source-valid ocean pixel (finite SIC and OSI `status_flag` marine bit coding) within 60 km for each of the six sites. Preserve source URL, SHA256 and original grid indices. Do not substitute arbitrary high-SIC or land pixels, invent subpixel corridors, or call the nearest cell a real coastal access point. A site without a valid near-ocean cell is a SOURCE_HOLD case.
3. Report coordinate-to-ocean-pixel offset and whether multiple source sites collapse into the **same raster cell** at either sampled date. If endpoints collapse, **do not** report pairwise effective resistance between them on that raster, because the chosen nodes are identical. Do not jitter points to rescue independence.
4. Distinguish the **ocean base conductance** (all valid water same positive cost, distance/geometry null) from explicit **model-only** SIC scenarios. Never set `R=∞` based on 15/30/50% as if experimentally validated passability; do not claim a species-neutral SIC response.
5. Any future Circuit result must compare a null *constant marine cost* with fixed alternatives such as `R=exp(β×SIC/100)` across a **predefined** range of β, reporting the full range and never fitting β against the same test tracks/counts after looking at performance. Negative/positive β are rival biological assumptions depending on species and season. A circuit provides **geographic opportunity**, not immigration probabilities or abundance forecasts.

## Next analysis only if node support passes

- **Preferred empirical test**: With exact original BAS Chinstrap GPS visits, pre-specify a coastal source/observed destination and compare current-flow hotspots against *withheld* within-season real GPS used marine pixels and equal-availability background pixels, with held-out island-years. This tests **foraging accessibility**, not breeding dispersal. Data currently comprise only three across-island-year comparison pairs; acknowledge sample dependence.
- **Secondary mapping**: Use broad regional marine circuits across candidate breeding colonies as an **exploratory opportunity atlas**, with distinct year/season and source-mask provenance, and compare open-ocean equal-cost/null to ice-related hypotheses. Do not use six selected co-breeding site counts to calibrate resistance and then claim climate causes their change.
- If the goal is specifically to test **'penguins can swim, but the breeding population does not move'**, wait for actual band-resight, juvenile recruitment, or newly occupied breeding-site observations with year/site identities. Circuitscape cannot create that response variable.
- For 25-km Antarctic sea ice, nodes within tens of km will often be poorly resolved: if the result depends on them, obtain independent fine-resolution shoreline/ocean movement information or analyze larger separated nodes. Regridding to 1-km pixels **does not create 1-km SIC observations**.

**Decision:** Circuitscape is technically appropriate for the *environmental opportunity* layer. It is **not yet a supported mechanism test of Antarctic breeding-colony movement**, and remains a separate source-gated exploration rather than becoming a new primary result in warming manuscript v0.6.

## Software contract

Actual `Circuitscape.jl` accepts either **raster** or **network** data with resistance or conductance values. Pairwise mode produces effective resistances and optionally current/voltage maps; using network mode with ad-hoc coast-to-coast edges is **not evidence for marine routes**. For future native execution, use the [official Circuitscape documentation](https://docs.circuitscape.org/Circuitscape.jl/latest/usage/) and explicitly record package version, Julia version, raster projection/extent, connected graph size, and four/eight-neighbor rule. Pilot execution is not implied by this feasibility report.

## Output

Audit script: `audit_nodes.py`. CI stores `circuitscape_node_support.json`, original all-pairs distances and fixed-date coastal source-pixel assignments. No `effective_resistance` column is fabricated or filled before an actual Circuitscape solve.
