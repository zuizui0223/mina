# V22 — Positive local Gentoo synchrony across a South Georgia physical island boundary

**Actual original-source biological analysis 2026-10-20**, source SHA verified. [Successful original-data GitHub Actions #39415804780](https://github.com/zuizui0223/mina/actions/runs/39415804780).

Bird Island BAS historical v1 gentoo source (252 colony rows, original SHA256 b1abc3c3adacee3f277d481217aabe4206c7b592a81f1f0eb1a0ec20a64450d3, DOI 10.5285/c8d5a7a4-e19b-497f-b7ae-56f9a2b15a56) and Maiviken on the much larger *main island of South Georgia* (12 source-season rows, SHA256 8eef8ba06b0f1e666041be38415cfcc70d16cdb07e72ca6db805d8b70631dc85, DOI 10.5285/1fd5bc8a-96b5-4f53-aa15-33e5330e7705).

## Original input diagnosis
Initial strict run matched zero years due to an **unsupported DD-Mon-YY date format** in both original source files (e.g. 20-Oct-19, 11-Nov-08). Without opening any animal Count magnitudes, original date labels exposed this source schema issue. We added only this literal date format; no study years, site identities, 30-day stage-matching threshold or biological prediction was changed. Subsequent original-source run and invented fixture tests PASSED.

## Numerical analysis
- **11** matched seasons 2009–2019, **10** strictly consecutive yearly change windows, original nesting dates within the frozen 30-day seasonal stage window.
- **7** persistent Bird Island colony census components (Johnson, Landing Beach, Lower Mountain Cwm, Lower Natural Arch, Square Pond, Upper Mountain Cwm, Upper Natural Arch); an equally weighted mean of seven colony-specific annual log(1+original nests) changes, NOT an assumed island-wide total.
- Maiviken annual log(1+incubating nests) change on the same original seasons.
- **Pearson r = +0.5621534427494942** for annual nest-count growth across the small offshore island versus the South Georgia main island. Leave-one-year-window-out r **+0.46096277397736507 to +0.7574255492713723**.
- Both original monitoring systems rise/fall in the same direction in **7/10** adjacent-year windows.
- Within Bird Island, **21** pairs of nested colony-specific annual growth series yield median r **+0.6106618550720883**. They are nonindependent sub-sites, not 21 new islands.

**Ecological interpretation:** Across this one physical boundary, local annual breeding counts show positive interannual association, consistent with a possible shared regional process even when colony locations are separated by water. The observations do NOT distinguish marine shared forcing, meteorological state, life-history timing, researcher/survey protocols, competition, predator impacts or genuine rescue/immigration. One South Georgia comparison is **not** a pan-Antarctic macrobiogeographic law.

V20's separate NOAA South Shetlands local Gentoo growth r=+0.635 had a different year support and census stage. The two local systems are context, not independently preregistered evidence (V22 was selected following positive V20 exploration). To discriminate institutional effects from geographical separation within BAS, independently compare nearby Bird–Maiviken to longer-distance Signy using **the same** 2009–2018 annual windows before causal claims.

## Artifacts
- [Exact frozen V22 contract](../contracts/BAS_BIRD_MAIVIKEN_NEST_GROWTH_V22.md)
- [Original-result JSON](../results/BAS_BIRD_MAIVIKEN_GENTOO_NEST_GROWTH_V22.json)
- [V21 source discovery and two publisher SHA hashes](BAS_BIRD_MAIVIKEN_V21_SOURCE_RESULT.md)

Current scientific decision: DESCRIPTIVE_SINGLE_ISLAND_BOUNDARY_ASSOCIATION_CAUSAL_HOLD. Do not claim island barrier **caused** synchrony nor relabel the large South Georgia island as continental mainland Antarctica.
