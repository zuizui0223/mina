# V11: post-outcome technical robustness, NOT a new preregistered biological endpoint

The original 2011→2016 and 2016→2025 GIS overlay outputs were exposed in CI #38364797404 BEFORE creating this robustness extension. E was 0.669617 and 0.678212 respectively; the corresponding fraction of *chinstrap lost area* that was reoccupied as mapped macaroni gain was only 0.079741 and 0.057344. We MUST present both denominators, not portray approximately two-thirds of chinstrap disappearance as a species replacement.

We now specify **exploratory sensitivity** checks without modifying the frozen V10 file or original Ecology PR189.

- Spatial offset: move **only the mapped chinstrap loss polygon** in 8 compass directions by each of 2, 5, 10, 20 metres relative to the apparent macaroni gain polygon, keeping the pair-specific cloud-free support and observed macaroni gain fixed. Report min/median/max of the eight shifted overlay ratios (not confidence intervals or a registration-error probability distribution). Changes at 2m indicate severe positional fragility; persistence at 10m supports a geographic patch association but still not a social or causal mechanism.
- Patch-core overlap: independently erode both gained-macaroni and lost-chinstrap polygons by 1, 2, 5, 10 metres before computing the intersection. Normalize by the eroded gained-macaroni area, returning undefined when it vanishes. This filters thin digitization fringes but biases toward broad patches; it is *not* a corrected biological estimator.
- Same-year interspecies overlap: within each observed 2011, 2016 and 2025 clear-sky cloud mask, calculate C∩M area and its fraction of M area, to audit possibly ambiguous or jointly labelled patches.
- Do not use 2020–22 date-mixed polygons or under-cloud replacement layers. Do not fit a p-value, infer actual first settlers, competition or guano legacy, or interpret the eight offsets as biological replicates.
- Main limitation remains unknown **independent co-registration error** and habitat-matched available-space null. Treat nonzero robustness as mapping robustness only.

All inputs are original BAS public GIS assets (doi:10.5285/7220dc6b-2f52-4160-a6c0-e57c50963308). This analysis is a diagnostic requested after inspecting the first descriptive findings.
