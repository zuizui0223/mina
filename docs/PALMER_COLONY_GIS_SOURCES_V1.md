# Palmer colony GIS crosswalk source registry v1

Date: 2026-09-27

This registry records independent evidence discovered after the frozen
`PALMER_ISLAND_PARTITION_V1` result. It does not assign aliases from demographic
similarity.

## S1. Palmer LTER Adelie Penguin Census metadata

Source:
https://pallter-data.marine.rutgers.edu/erddap/tabledap/AdeliePenguinCensus.html

Relevant metadata:

- `colony_code` is described as a "code identifying an ecosystem colony" and
  the colony number is island-specific.
- `colony_code` is typed as a nominal variable.
- the dataset is an annual synoptic census of five main Palmer-area island
  populations.

Use in crosswalk: establishes semantics of the raw code field but supplies no
coordinates or guarantee that the nominal identifier is a persistent physical
polygon.

## S2. Patterson (2001) MSc thesis

Source:
https://scholarworks.montana.edu/bitstreams/a124761d-6f6e-409a-a7b7-7c60d34b7543/download

Relevant evidence:

- Figure 3 maps spatially separated Adélie breeding patches across Torgersen
  Island on an aerial photograph.
- Appendix A lists numbered Torgersen colonies used in 1993–1995 reproductive
  sampling, with aspect and visitation regime. The listed subset is:
  1, 2, 4, 6, 7, 8, 9, 10, 11, 15, 16, 18, 19, 20, 21, 22.
- The thesis explicitly distinguishes a local "landscape effect" from a larger
  "marine effect" and reports strong island- and colony-scale demographic
  differences associated with habitat.
- The appendix is a reproductive-sampling subset, not a complete 23-colony
  census key; therefore missing numbers must not be treated as absent physical
  colonies.

Use in crosswalk: supports persistent historical numbering and physical
subcolony footprints on Torgersen, but the public thesis figure does not by
itself provide a number printed on each polygon. It is therefore source evidence,
not yet a complete code-to-polygon lookup.

## S3. Patterson, Easter-Pilcher & Fraser (2003)

Source:
https://pallter.marine.rutgers.edu/docs/publications/documents/lterfinalms/240lterc.pdf

Relevant evidence:

- the published chapter describes 23 active Torgersen colonies in 1989;
- the colony perimeters were analyzed using georectified aerial photography and
  a digital terrain/hillshade model;
- colony area and aspect were explicit physical-habitat attributes.

Use in crosswalk: documents that historical "colonies" were spatial units, not
only arbitrary census bins.

## S4. Cimino et al. (2025), Landscape Ecology 40:78

Source:
https://link.springer.com/article/10.1007/s10980-025-02088-y

Relevant evidence:

- 1998/99 Torgersen historic sub-colony perimeters were digitized in ArcGIS Pro
  from the Patterson et al. (2003) map after alignment to a georeferenced image;
- 2020 perimeters were digitized from drone orthomosaics;
- 2022 active sub-colony perimeters were walked with a handheld GPS;
- large historic sub-colonies that fragmented into multiple later patches were
  treated as the same historic footprint for area summaries;
- by 2022, 18 of 23 historic Torgersen sub-colonies were extinct and five
  historic sub-colonies remained active, some fragmented within their historic
  footprint;
- electronic supplementary material is published with the article.

Use in crosswalk: this is the strongest identified bridge from historic
subcolonies to georeferenced physical footprints. The next retrieval target is
the supplementary material or underlying geospatial products sufficient to
recover identifiers/geometry without using demographic outcomes.

## S5. ASMA No. 7 Torgersen mapping

Source:
https://www.era.gs/projects/palmer/index.shtml

The Palmer Basin / SW Anvers Island management mapping includes a dedicated
Torgersen Island zones map. This is useful for georeferencing and management
boundaries but is not yet known to encode individual penguin subcolony IDs.

## Current assessment

A physically grounded Torgersen crosswalk is feasible. The bottleneck is no
longer the existence of spatial information; it is obtaining an explicit,
auditable association between the LTER nominal `colony_code` values and the
historic/georeferenced subcolony footprints.

No crosswalk assignments are frozen in this registry. In particular:

- `TOR 19.0` must not be merged with `TOR 19.1` from count patterns alone;
- decimal suffixes must not be interpreted as split/merge lineage without
  documentation;
- apparent numerical agreement between an LTER code and a Patterson colony
  number is only a candidate correspondence until supported by a source.

## Next retrieval targets

1. Cimino et al. (2025) supplementary material, especially S3/S13 and any
   sub-colony table or geospatial identifier.
2. archived Palmer/EDI geospatial layers or drone products underlying the
   1998/99, 2020 and 2022 Torgersen perimeters.
3. historical field maps or census protocols that print colony numbers directly
   on Torgersen/Humble/Christine/Cormorant/Litchfield maps.
4. only after source-based identity resolution: calculate physical-unit
   centroids/pairwise distances and freeze a distance-conditioned same-island
   boundary model.
