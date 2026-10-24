# V34 — Original 2026 Ross Sea 39-colony census mapped to named source islands

Date 2026-10-22. Original publisher-source matched geographic metadata and source observation-year records ONLY, no Adélie nests/pairs growth, spatial concordance or climate fit. [Executed source GitHub Actions #39723278365](https://github.com/zuizui0223/mina/actions/runs/39723278365). Original census XLSX SHA256 23a95d9e693dd095e085534f2c215b79880a72fe9cfb5a59337501192dae03e6 and location XLSX SHA256 d744e7493f85564f1b634f390a5e4a976b2d5359a6f93cdd9ef345639661b6a6. Publisher DOI https://doi.org/10.7931/kf06-x745.

## Source nomenclature and geography
- **39** original census colony rows, 40 source location-name rows. **33 exact** casefold+whitespace colony–location key matches.
- Source original census labels WITHOUT an exact location-ID match: Aviation Islands, Beaufort Island New, Foyn Island, Terra Nova Bay, Thala Island, Wood Bay. Location file separately lists Beaufort Island North and Svwend Foyn Island; **no plausible-sounding fuzzy alias has been made**.
- Exactly **8 singular named island candidate groups** recoverable from source text: Beaufort Island, Chinstrap Island, Coulman Island, Inexpressible Island, Nella Island, Possession Island, Ross Island, Sabrina Island. In particular Ross Island contains **6** nested colony sites (Cape Bird North/Middle/South, Cape Crozier East/West, Cape Royds), Coulman Island **4** (Cape Anne plus Coulman North/Middle/South). Counting these 10 nested colony names as 10 separate islands is invalid.
- Some colony records on peninsulas or continental capes do not have explicit source "Island" grouping and are NOT pooled as island landmasses. A name is a candidate physical-landmass group until independent GIS coastline polygons are joined; coarse source coordinates are not independently surveyed borders.

## Exact observation-availability support
- Four source-named island groups have at least five same-colony original consecutive-year observation windows: Ross **40**, Beaufort **11**, Coulman **6**, Inexpressible **6**. Source named-landmass panel condition PASSES.
- **14** different original adjacent-year start seasons have at least two distinct named island groups with a paired colony observation: 1983–1992, 2001, 2004, 2005, 2017. The later 2017→2018 pair is NOT documented by the old methods PDF through 2017, so a new V35 can freeze a strictly documented pre-2018 cohort rather than silently assume matching survey practices.
- Only **4** original year windows meet the stricter condition of at least two island groups EACH with >=2 same-colony transitions, below frozen six-year requirement. This stricter WITHIN-versus-BETWEEN COLONY synchrony analysis is CLOSED as insufficient; do not lower its gate.
- The original source is CC-BY-NC 4.0, and overlapping historic Ross Island bird counts may be republished in APBP/MAPPPD. A new record vendor does not automatically imply independent animal data for already shared colonies/years.

**Decision: HOLD_GIS_ISLAND_POLYGONS_AND_COUNT_STAGE_BEFORE_BIOLOGY.** The original metadata source passes a more limited descriptive named-island group annual co-observation gate, but does not yet demonstrate a generalized water-barrier/area causal effect. A new separate V35 may examine site-stage-matched bird fluctuations at the SOURCE NAMED ISLAND level over documented source seasons and with explicit nonindependence limits, without applying the failed stricter colony-level comparison.

- [Frozen V34 geographic source contract](../contracts/NZ_ROSS_SEA_COLONY_ISLAND_CROSSWALK_V34.md)
- [Machine-readable full exact source geographic crosswalk](../results/NZ_ROSS_SEA_2026_ISLAND_CROSSWALK_V34.json)
