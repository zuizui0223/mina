# Antarctic Adélie SIC: threshold-independent future climate novelty vs historical 10/15/20-year SIC windows

**Task**: Reinterpret existing physical CMIP6 projection without borrowing the unvalidated 60–80% *biological* threshold.

At each of the original 39 Adélie census site codes, reconstruct 30 original annual 1991–2020 Aug–Nov satellite SIC values. Compute site-specific envelopes of all 11 overlapping 20-year means, plus all 16 overlapping 15-year means and 21 10-year means. For each original model×SSP×future-period site, add the CMIP6 1995–2014-relative SIC anomaly to the observed 1995–2014 mean, clipping [0,100%]. Label **physical** novelty if the conditional future 20-year mean is below the smallest of the site's historically observed 20-year means.

The 11 overlapping historical windows are not 11 independent replicates and do not define a statistical prediction interval. Future climatology is from a coarse-resolution model (not a site forecast). Require additional sensitivity margin (2 and 5 percentage points), different historical window lengths, an annual-single-year-minimum diagnostic (different timescale!), model agreement, and observation baseline 1991–2020 (time misalignment sensitivity).

Use both equal-site and historical latest original MAPPPD recorded count weights. Count sources are different years (2001–2025) and different methods/targets, so weighted fractions are *scenario-index mass*, not future breeding-pair loss.

**Strict NO-GO**: no causal response, extirpation, colonization or projected nesting abundance; no claim of "safe climate refuge" solely based on crossing no 60% threshold. Source pinned and CI-reexecuted results must be observed before making quantitative claims.

Do not edit frozen Paper 1 / Paper 2 / main. Keep Draft PR #206 as progress branch.
