# V14 — critical historical 2011 code mismatch and mixed-colony censoring

On original 2011 historic shapefile access, the V13 code **correctly stopped before any geometry was opened**. Original DBF values contain `CHPE`, `MCPE`, and `MIXED`, rather than the data dictionary's `CPE` and `MPE` examples. GitHub Actions #38366301810 is a **data-provenance hold, not an ecological null result or a test failure**. It cannot be fixed by relabeling `MIXED` as one species.

This is ecologically important. Macaronis can occur within or near chinstrap colonies in original 2011 imagery; independently documented same-image mixed areas complicate forced discrete patch replacement. Published prior art on species differentiation and co-occurrence: Lynch et al. 2012, *Polar Biology* doi:10.1007/s00300-011-1138-3. Historical 2011 mapping is not independent satellite time series.

Next pre-geometry stage: inspect unique category counts in the original `species` DBF attribute **without loading shapes**. Only `CHPE`, `MCPE`, `MIXED` categories are permitted; no assumptions about the share of a mixed polygon and no CPE/MPE autoconversion. Distinct `CHPE` and `MCPE` attribution can be explored only with a published code crosswalk or direct custodian clarification. If mixed areas are material, exclude them from any alternative-map species-specific exchange analysis and report the exclusion domain rather than a misleading whole-island effect.

Frozen Ecology PR189 and original V10 descriptive receipt remain unchanged.
