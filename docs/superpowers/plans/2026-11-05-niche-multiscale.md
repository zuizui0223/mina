# Signy multiscale diet analysis implementation plan

Goal: Test whether low sea ice is associated with convergence at fish/crustacean, krill carapace size, and maturity levels, preserving the stomach/year hierarchy and sample-date support. Deliver reproducible outputs and synchronize PR206.

Architecture: one source-pinned Python analysis, separate independent verification, aggregate outputs and Japanese report. Python pandas/numpy/scipy/statsmodels/matplotlib. Existing main/Paper1/Paper2 unchanged. No raw stomach republication.

Spec: outer workspace outputs/niche_reframing_v1/DIRECTION_JA.md; user authorizes actual analysis, timing/sample-size sensitivity and PR sync.

- [x] Retrieve original BAS 3 ZIPs; compare hashes with prior audit; validate units, stage codes, season mapping and stomach identifiers. Save source manifest and exclusion/support tables.
- [x] Freeze continuous Aug–Nov nearshore GOPT SIC predictor and 2001–2009 common seasons; September is sensitivity. Base fish distance is mean of absolute Gentoo–Adelie and Gentoo–Chinstrap mean fish-share differences. Preserve prior signed gap separately. Fine distances: Wasserstein-1 of stomach-equally-weighted carapace distributions and total variation of stomach-equally-weighted stage composition. Both restricted to sampled krill, not prey availability.
- [x] Analyze full per-trait cohorts plus common-stomach sensitivity. Keep raw-stage unknowns separately and report missingness; no negative/missing to zero. For each metric require >=3 valid stomachs per species/year. Compute per-pair and composite outputs without treating pair rows as independent climate replication.
- [x] Estimate year-level correlations/slopes with HC3 intervals, exact 9! permutations and max-|r| adjustment over the three main metrics. Year-detrending, first differences, leave-year-out and circular phase diagnostics are sensitivities, not broad correction of historical exploration.
- [x] Equalize stomach numbers within each year/species and across years (minimum supported count), conditional stomach bootstraps, and pairwise mutual nearest-date support within 7/14 days. Date-matched pairs require >=3 stomachs on both sides; insufficient common years remain insufficient, no fabricated match.
- [x] Independently verify joins, mass fractions, distance calculations, weighted CDF normalization, permutation counts and output claims. Inspect plot. Document prior-art overlap and causal/forecast limits.
- [ ] Commit scoped code, aggregate results, report, source provenance; push existing progress branch and verify remote SHA. Do not claim global CI passes unless final-head checks verify it.

The metrics/windows above are fixed before running new effect estimates, but study is exploratory because prior diet effects were already inspected. Unknown sampling effort, temporal autocorrelation, incomplete stage coding and isotope/GPS period incompatibility remain explicit limits. No automatic future biological forecast.

Source-gate amendment before new effect estimation: Gentoo carapace units cannot be verified against the Adelie/Chinstrap `_mm` column; BAS metadata mentions eyepiece units. Three-species W1 is therefore a common-numeric-scale ASSUMPTION diagnostic, not an established physical-size convergence result. Adelie–Chinstrap `_mm` contrast is retained separately. Maturity primary is recorded label composition (excluding U/Unknown/missing), with a source-catalog-only sensitivity J, FS, FAS, MS, MAS; do not silently interpret undocumented FA/MA/FASG as adult stages.
