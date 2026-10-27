# V35 — Source-only JNCC × RSPB predator-island PROXIMITY support audit

**Proposed and frozen before a V35 JNCC→RSPB geographic/label join, 2026-10-27.** The prior JNCC 17-species concentration V30 effects and all predator V33–V34 original island profiles have already been observed. This is NOT a pre-registered mechanistic effect test. NO JNCC numerical breeding counts, decline states, shares or E may be read.

## Exact source objects and identity

- JNCC original V29/V30 14,112 original species × site matched metadata and **1,483 structurally eligible species × Country × Master site × count-unit parent panels**. The parent-overlap guard and metadata source SHA/years/stages remain frozen.
- RSPB UK Islands 2014 ArcGIS original point centroids with 9,688 unique original integer `lowid` IDs, independently joined (9,688/9,688) to Stanbury et al. (2017) ESM5 mammal categories.
- Original JNCC `Start.Lat`/`Start.Long` coordinate is site metadata, not guaranteed exact historical breeding patch GPS. RSPB point location is island feature reference centroid, not a physical polygon. Geometric proximity DOES NOT prove the JNCC site is located *on* that landmass or year-to-year island occupancy.
- Use the original JNCC source row parser and **only `v30.extract_structural`** before numerical count parsing. Do not call `v30.model` or process original adjusted nest counts.

## Fixed geographic proximity algorithm

1. Transform original JNCC WGS84 source points and RSPB original centroid points into ETRS89-LAEA (EPSG:3035) for distances, record each RSPB lowid and exact source data provenance.
2. For each unique original JNCC point find nearest and second nearest RSPB island point centroids using a spatial KD-tree. An exploratory PROXIMAL_UNIQUE candidate exists only if **d1<=250 m AND d2>750 m**. A site within 250 m of two different RSPB centroids is AMBIGUOUS; other cases are UNMATCHED. There is no name-based alias, local-buffer tuning, census outcome conditioning or invented polygon membership.
3. Record source-geographic sample support: original 1,483 parents and original source child sites, number of uniquely near points, candidate original landmass IDs, panels where **all children** are uniquely near **distinct two or more RSPB island references**, and across-child source predator status variation among candidate physically distinct islands. Code 0 remains an **assumed OR verified absent mixture**, never surveyed predator absence.
4. A parent showing mixed *nearby centroid IDs* is NOT a verified mixed physical-landmass parent; **therefore V35 cannot pass V32 H2 strict physical-island/within-parent causal gate**. Independently sourced GSHHG/OSMR map geometry and historical JNCC patch footprints would still be needed.
5. If fewer than 20 candidate mixed parents, fewer than 5 source species, fewer than 5 candidate distinct islands, or source date/status remains unresolved, then no signed H2 comparative predator effect even on a provisional basis. Report denominators and STOP transparently rather than rescuing with larger radii or JNCC count magnitude filters.
6. UK RSPB excludes the large Britain and Northern Ireland landmasses and tidal islands by original mapping definition, so **no RSPB match is NOT evidence of predator absence or of a mainland nest**. Irish sites outside RSPB inventory do not count as zero. Report per-source region/country without invented source absences.

## Next causal identifiability stage

A future bird–predator ecological response fit additionally requires physical landmass polygon identity with georeference QA, contemporaneous predator occupancy/detection/eradication history near both JNCC census epochs, independent nest susceptibility and surveyed effort. Do NOT reopen these source gates because V30 concentration is known, and do not modify PR #189 or Antarctic Penguin paper.
