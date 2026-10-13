# V15 — test whether apparent new macaroni space had ALREADY been labelled mixed (pre-geometry contract)

**V14 observed DBF codes (attributes, no geometry):** CHPE 442, MCPE 18, MIXED 46, all 506 records. Attribute area sums: CHPE 704779.45972, MCPE 76236.34528, MIXED 219515.73525 **units not validated**. Original data dictionary described CPE/MPE nomenclature instead of these literal CHPE/MCPE/MIXED values. It is **NOT permitted** to assign MIXED entirely to either species. No 2011 historical polygon geometries have yet been opened.

This new exploratory analysis is explicitly downstream of V10 E≈0.67 (already exposed). It tests an alternate *measurement explanation*, not a confirmed social mechanism. It does not rewrite Ecology PR189.

- Use original 2011 historic `mac_and_chinstrap_colony_boundaries_2011` to retain CHPE, MCPE and MIXED as **three separate labels**, without assigning MIXED.
- Compare to V10 **newly mapped macaroni area**, defined exactly from updated 2011 vs 2016 `macaroni_colony_boundaries` with both original date-specific cloud regions removed. Compare on the SAME support and dates as V10.
- Primary diagnostic: percentage and m² of this apparent gain intersecting 2011 MIXED polygons. Secondary diagnostic: the fraction of V10 gain∩chinstrap-loss co-location intersecting 2011 MIXED polygons, conditional on a nonzero denominator.
- Partition remainder into CHPE, MCPE and outside-original-2011 footprints, but first report category geometry overlap; do not force a partition if categories overlap spatially.
- Compare independently projected geometric areas with historical DBF `area` attributes as a source-quality audit, without changing units after opening outcomes.
- If much of V10 'new' macaroni area lies inside areas formerly classified MIXED, apparent colonization is **not identifiable as genuine new macaroni occupancy** in those polygons. A MIXED polygon indicates co-occurrence at the subcolony-patch scale, not every square meter; do not assert that all apparent gain existed in 2011.
- No p-values, no recruitment or individual bird movement, no competition or marine driver inference.

Source: Ratcliffe et al. 2026 DOI 10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308; historical Lynch et al. 2016. This contract was frozen before opening original 2011 historic polygon geometry.
