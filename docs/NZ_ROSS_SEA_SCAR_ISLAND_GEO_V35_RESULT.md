# V35 — Ross Sea original colony sites independently linked to SCAR Antarctic land polygons

**2026-10-22 executed new independent GIS source check.** New Zealand DOI https://doi.org/10.7931/kf06-x745 1981–2024 original 39-colony aerial Adélie breeding-pair census and source colonylocations.xlsx were re-downloaded with exact SHA256s, and joined to original SCAR Antarctic Digital Database/ADD medium-resolution 2026 source coastline DOI https://doi.org/10.5285/c9c6d671-ad19-4a78-96b2-7d47e9bac46a, publisher original ZIP SHA256 b0172d698436f871f49339cea5c7155e3d98648360521cc4bbc44a026c0edc38. Real source run [GitHub Actions #39724187361](https://github.com/zuizui0223/mina/actions/runs/39724187361) and all original-source synthetic polygon tests completed successfully.

## Geography: truly separate original land polygon groups, not 39 independent islands

The source already showed 33 exactly matching census-colony/geography names. With independent 1786 current SCAR land polygons, 33 site localities yielded 8 **exact containing-land** links, 17 unique-nearby within a fixed 2 km coarse-point buffer, 6 unmatched farther than 2 km, and 2 near multiple polygons. Such near-only matches are provisional because original site coordinates are reported only to full arcminutes, often ~1 km geographical uncertainty.

Source named island groups supported by a UNIQUE separate SCAR land polygon were:
- **Ross Island** original land polygon 59: Cape Bird Middle, Cape Bird North, Cape Bird South, Cape Royds; **35** same-colony year-to-year group windows under the ≤2016 survey-method restriction. Original Cape Crozier East/West source points were not within the frozen 2 km source land match and were not rescued by names.
- **Coulman Island** original land polygon 37: Cape Anne, Coulman Island North/Middle/South; **5** group windows.
- **Beaufort Island** polygon 50: 1 colony; **11** windows.
- **Inexpressible Island** polygon 43: 1 colony; **5** windows.
- **Possession Island** polygon 29: 1 colony but **0** suitable strict annual windows.

Chinstrap Island and Sabrina Island both matched the same ADD polygon 4 while given different original source island names; **both are excluded as conflicting**, not counted twice. Other locations described as capes/continental coastline are not relabeled oceanic islands. Original Ross Island is one physical landmass despite six source colony labels.

## Temporal source support, no ecological effects opened

Use strict same-original-colony observed in years y and y+1, pre-2018 source-method period. **Four GIS-supported island groups** have ≥5 adjacent annual windows. **13 common annual starts** contain at least two distinct verified-source named island land polygons: **1983–1992, 2001, 2004, 2005**. Seven starts contain ≥3 island groups (1985–1988, 1991, 2001, 2005). These are independent landmass *source support opportunities*, NOT yet sign or growth statistics. The source-only gate of three islands and eight co-island years PASSED.

Original survey count magnitudes, colony loss and recovery, population synchrony, environmental forcing and species competition **were not computed**. This supports a *separately frozen V36 descriptive* analysis using these exact original island identities and year roster, but it does not itself validate matched observations at different islands nor demonstrate sea-ice, wind, island area or migration mechanisms. Modern land polygons do not provide historical available nesting space.

[Full machine-readable geographic site and annual source roster](../results/NZ_ROSS_SEA_SCAR_ISLAND_GEO_V35.json).

Decision: PROCEED_SEPARATELY_FROZEN_DESCRIPTIVE_ISLAND_GROWTH_ONLY.
