# Signy vegetation–seal linkage: executed source decision (2026-11-24)

Status: BLOCKED_SOURCE_AND_GEOGRAPHIC_SUPPORT. No joint plant/seal observations constructed, no plant numerical outcomes opened in an original-data model, no ecological coefficient fitted. This does not negate the existing six-zone seal result, the Palmer vegetation association, or Cannone's published findings.

## Actual source acquisition

- Actions run 45389826056, head 6d0c07240e8c8051c43cbbad03126a170c22c7f4, artifact 14918157360. Downloaded ZIP SHA256 c1943147afaf61c4f02a8332e510acfd498072c6975f0faab1fcd508ed9096c6 matches Actions; ZIP CRC verified. Both receipt and rendered source page inspected.
- Cannone et al. (2022) Current Biology DOI 10.1016/j.cub.2022.01.074 explicitly lists Figshare DOI 10.6084/m9.figshare.18282695, but the Figshare API /v2/articles/18282695 and DataCite DOI API both return HTTP 404 in Actions. No original plant data files or coordinate schema obtained. This establishes unavailable through the tested public endpoints, not deletion or nonexistence. Do not guess a substitute ID.
- Dunn et al. (2025), 10.1111/gcb.70290, original NERC PDF SHA256 f62dfdb9f116ed2c64c6c1ab03c23994116e3e46777f1a5e432492c2bb8bb0cd; Figure 2, page 4, rendered and visually inspected from the verified artifact. Six purple bounded regions encompass coastal areas/nearshore water and some land, with gaps across inland ice and terrain. A graticule and scale bar are present. These are not a complete partition of land area; no nearest-zone assignment beyond the depicted boundaries, no digitized coordinates or validated transform claimed. Web PDF screenshot unavailable; rendered artifact supplied the visual audit.
- BAS 2020 land-cover reference DOI 10.5285/af80c82c-b6a0-4978-92e0-efe063c390af: source ZIP SHA256 3d4a7a9d8173cc16ca1f9f1819fdfa1efda1e470dccf33d56e6d420258cf6e74. Original land-cover shapefile: 640 polygons, SHA256 8e7058c8e171e7c55af018a055a53255ca1d88e42bc618461f483c68576f1c30. Original streams: 79 line features. CRS WGS84 / UTM zone 23S. Source inventory includes both GPKG and shapefiles. Not vegetation cover and not an independently verified 2009/2018 ice-free survey footprint. No zone geometry reconstructed.

## Timing/measurement support (structure-only recheck of prior source receipt)

Reviewed prior verified panel_receipt.json and schema_review.json from Actions run 45356876730 / artifact 14901864718. The illustrative, not yet frozen, pre-2018 exposure windows in VEGETATION_LINKAGE_GATE.md face further support limits:

- 2004–2008: 2005, 2006, 2007 have otherwise complete six-zone row structure; all month labels blank but source protocol documents February census. 2004 has two missing adult fur seal counts in zone 6 (area 101 and 102). 2008 mixes labelled subarea records in zones 2,3,4 with one unlabelled area row in each of zones 1,5,6; these may be whole-zone counts but cannot be certified from the available record structure alone. Three clearly usable candidate years before checking numerical subarea overlaps; fourth year not established.
- 2013–2017: 2013, 2014, 2016, 2017 structurally complete; 2015 absent in publisher source year inventory. Four candidate years, subject to composite-label overlap and comment audits.
- Do not claim four valid years in both windows or automatically choose a different interval. Need source confirmation of mixed aggregation in 2008 or a new pre-outcome design if inputs permit. The earlier 2016–2024 exposure includes years after 2018 plant endpoint and is not admissible. 1960 plant records precede the seal time series.
- Annual seal counts include adjacent sea ice, not just terrestrial animal-days. Population presence on a survey day is a proxy for pressure rather than direct trampling or nutrient input. Exposure is at most six zones in one island; plant points are not independent exposure replicates.

## Prior art / scope

Cannone et al. (2016), DOI 10.1007/s10584-015-1551-7, already interpreted negative seal disturbance below 20 m and possible nutrient-associated expansion at 20–60 m, with physical constraints above 60 m. Cannone et al. (2022) already hypothesized release from fur seal disturbance with warming and described east/west redistribution. The new question is whether the magnitude and direction of observed plant change align with spatially differentiated prior seal abundance change, within genuinely comparable survey footprints. Even with data, this is a descriptive comparison and cannot establish a new causal mechanism or a general Antarctic rule.

## Restart requirements

1. Publisher/author-original 1960, 2009, 2018 spatial point records, population-size classes, disturbance code, survey footprints or repeat-visit/absence evidence, coordinate system and year identity. Obtain original GIS before inferring colonization or extinction. 
2. BAS official seal zone GIS or source-approved geographic map and verified 2008 aggregation meaning; use boundaries only where survey extent is established.
3. Review source identity, licenses, coordinate uncertainty, overlap/coverage and pre-endpoint counts before estimating relationships. Record at most six zone-level summaries, with explicit unassigned sites and no fabricated boundaries. No further retries of the same unavailable Figshare URL and no post-2018 exposure substitution.

## Draft request to vegetation data lead (not sent)

Dear Dr Cannone,

I am interested in the spatial relationship between marine vertebrate use and plant distribution change on Signy Island. I read your 2022 Current Biology paper (doi:10.1016/j.cub.2022.01.074) and the earlier Climatic Change study. The Figshare DOI listed in the paper currently returns a not-found response through the public metadata APIs.

Could you advise whether the deposited datasets are available at a different link? If available for research reuse, I would be grateful for the original spatial records for Deschampsia antarctica and Colobanthus quitensis in 1960, 2009 and 2018, including coordinate reference system, site identities, population size classes, recorded marine vertebrate disturbance, and survey footprints or repeat-visit records. My proposed comparison would use prior seal census counts within the six stable BAS survey zones, while recognizing the limits of a single island and distinguishing spatial association from causation.

I would welcome advice on data-use terms, appropriate attribution and possible collaboration. Thank you for your consideration.

Best regards,

Lead contact as listed in the paper: nicoletta.cannone@uninsubria.it. This is a repository draft only. No email or form submitted. 
