# V7: preceding marine-ice change and separate observed growth of Chinstrap/Gentoo

2026-10-30. Continue PR206 from 44dcccaf; do not change V1–V6, Paper1/PR189,
Paper2/PR199 or the existing 216-test family. Entire study is post-exploration.

Goal: connect the previously fixed V6 CHPE/GEPE observed intervals to the same
OSI-450-a1 v3.1 prior Aug–Nov, 100km marine-cell product and separate the two
species' absolute count changes from their relative change. No date/abundance
imputation, alternate product or horizon search.

Eligibility inspected before opening the new environmental association:
79 V6 intervals, of which 78 across 19 original sites and 3 source regions fit
1979–2020 preceding seasonal windows; one endpoint outside product remains
excluded. Require all four original census date lower bounds to follow the
corresponding prior November 30. Source years are publisher bounds, not field-
validated dates. Exact source IDs, counts, citation and vantage must agree.
35 years × 4 months = 140 original monthly files. Reuse V4 source files only at
identical original URL and checked SHA; fetch the remainder from original MET
Norway. Same fixed100km geodesic mask, provider primary ice_conc, >=80% spatial
support, stable ocean-cell support. Exclude nothing based on response.

Model, fixed before environmental output:
 yA=log(NA_end/NA_start)/gap; yB=log(NB_end/NB_start)/gap;
 yDifference=yB-yA; x=(prior SIC_end-prior SIC_start)/(10*gap).
 Weighted regression with w=gap, site intercepts: equivalent to total log count
 change = site drift*gap + beta*(SIC_end-SIC_start)/10, weighted by 1/gap.
 This is an endpoint state-change association, not a cumulative exposure model
 or interpolated yearly count series. The gap weighting is a working process-
 variance assumption, not empirically known count precision.
 Secondary model includes region-specific ENDPOINT-YEAR differences / gap;
 unlike end-year-only dummies this respects unequal observation intervals.
 Guard rank and residual degrees of freedom; no p values or inferential CIs.
 Exactly same X/weights for A, B and difference, check betaDifference=betaB-betaA.
 Analyze the source-exact noncontinental land subset with equal-land/equal-site
 duration weights. Report singleton sites' zero within-site information and
 source pixel overlaps; do not call site IDs independent islands/climates.
 Delete one source site/region and one exact-land unit as descriptive dependence
 checks only. Never tune a subset to obtain the desired sign.

Tasks:
[ ] Write failing synthetic tests for support, chronology, interval scaling,
    endpoint-year controls, coefficient decomposition, rank and land weights.
[ ] Implement dedicated V7 code and contract, leaving originals unchanged.
[ ] Run local tests, then full normal repository suite and real-source GHA.
[ ] Download actual result and original files. Recalculate extraction with h5py
    and spherical/geodesic mask support, models with direct dummy WLS, and
    invariants against the frozen V6 source. Report failures explicitly.
[ ] Save code, source receipts, CSVs, result/decision, verification and one plot.

Known limitations: positive persistent endpoints only, irregular survey effort,
shared count endpoints, current—not historic—land geometry, overlapping marine
pixels, 48h original sampling before July1987, ERA5 ancillary input, no measured
snow/shore access/prey/competition or anthropogenic attribution.
