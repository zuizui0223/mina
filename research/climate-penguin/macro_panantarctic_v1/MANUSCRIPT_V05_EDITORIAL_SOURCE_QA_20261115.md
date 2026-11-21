# 2026-11-15 editorial and source gate — compact biology-first Antarctic macro paper v0.5

**Review scope:** claim/content fidelity and four source-backed main figure renders, not journal peer review, causal identification, or a new biological replicate. Draft PR #214 is not merged or submitted. [Canonical compact reading version](MANUSCRIPT_MACRO_V0_5_COMPACT_BIOLOGY_FIRST_WORKING.md). The 135,746-character v0.4 remains untouched as extended source-provenance backup.

## Current main-paper contract

- Working title: **Geographic reallocation of Antarctic penguin nesting does not simply track marine climate change**.
- Main reading file: approximately **4,100 space-separated words** including citations, source provenance and figure plan; abstract tightened to **281 words**. Original site/species/year denominators remain explicit.
- Four figures only, with original-data and inference support pinned in [the fixed figure contract](FIGURE_CONTRACT_V05_BIOLOGY_FIRST_20261115.md).
- **Fig. 1**: original 595 known colony IDs, 588 source marine-eligible sites, 65 sites supporting matched long-term original climate/nest comparisons, 12 strict original source-paired sites and 7 original GLORYS wet-grid unmatched points. These are source-site counts, not modeled species range or full population coverage.
- **Fig. 2**: directly recomputed original 16,464 source site–years marine PCA using NumPy covariance eigendecomposition; **PC1 60.3654233766%**, **PC2 33.3773230639%**, signed original loadings reproduce six archived loadings within 1e−4; the remaining variance PC3 ≈6.26%. 378 distinct original GLORYS wet cells, so not 16,464 independent ocean environments.
- **Fig. 3**: all original 19/26/35 fixed Adélie cohort weighted latitude shifts reproduced **107.310346 / 88.410832 / 99.602627 km south**, with exact three-level region/250-km/source-colony components; nearshore SIC changes are **+0.022 / +0.625 / +0.908 pp** on the full corresponding fixed rosters. A latitude shift is not an individual migration.
- **Fig. 4**: all six genuine original same-citation/same-method Adélie–gentoo site-pair ratio slopes **positive**; original first/last paired two-species observed nesting subtotal **increases at five of six**; local nearshore SIC slopes **negative at four and positive at two**. This is a two-region subpanel, not a continental regression or established competitive displacement.

The four figures are not inferred from generated or fictional coordinates: original source CSV and actual previously checked GitHub Actions ZIPs were bundled with the exact plotting Python script, saved figure-specific numeric receipt, 4 PNG + 4 SVG outputs, and SHA256 manifest. A fresh temporary-directory extraction and successful full script re-run verified same site counts, PCA and nest-weighted shifts. A new GitHub Actions verification for the v0.5 plot bundle has **not** been claimed.

## Editorial decisions applied to avoid misleading novelty

1. **Do not assert that 595 are all contemporary publicly catalogued Antarctic penguin colonies.** MAPPPD is a living database, and its current website advertises 729 sites with counts and 5,487 counts across six penguin species (accessed 2026-11-15). The frozen 595/2,456 is a three-focal-species, original-method selected observational source frame, not that whole live source universe.
2. **Do not claim regional Adélie decline/growth contrast was newly discovered.** It is documented by Lynch & LaRue (2014, The Auk, DOI 10.1642/AUK-14-31.1) and the 2024 Oceanites SOAP. The incremental evidence is the source-matched weighted geographic/accounting decomposition, comparison with marine exposure, and source-denominator and observational-scale limits.
3. **Keep salinity 2019–2020 source discontinuity out of the main causal claim.** GLORYS12V1's ERA-Interim → ERA5 source forcing switch is documented in the 2023 Copernicus QUID. The EN4 genuine 16-month QC run succeeded but found 0/18 regions suitable for strict four-year instrument/month comparisons; it neither independently verified nor falsified the pan-Antarctic freshening anomaly.
4. **Keep static mapped vegetation as context, never an annual greening trend.** Do not infer a causal plant-response pathway or biodiversity shift from a single 2017–2023 composite.
5. **Do not use the nested 19/26/35 Adélie rosters as three independent replicates**, or turn conditional 20,000-count-survey-year bootstrap quantiles into population CIs. Source block, region and site deletions are post-result descriptive checks.
6. **Keep the absence of a predictive climate transfer coefficient explicit.** The 85 site–species matched panel spans only 65 colony sites and six reporting regions, with block intervals crossing zero. No 2050/2100 penguin breeding-nest forecast is supported.

## Research significance and submission boundary

**Supported biology:** a southerly change in relative Adélie nesting weight among fixed, surveyed colony sites and locally repeated gentoo-relative gains that do not imply zero-sum nesting; the marine physical variables are not one interchangeable spatiotemporal axis. **Not supported:** individual southward migration, coastwide colonization/occupancy, a local increase in optimal foraging sea ice, a causal warming effect, the effect of genuine salinity on nests, or a validated warming-driven breeding future.

**Current status: SHARE WITH SCIENTIFIC CAVEATS / NOT SUBMISSION-READY.** A shorter coherent manuscript and reproducible four-figure bundle exist. It still needs author bibliography completeness, target-journal figure design/caption compliance, a full review of method/source limitations and an editorial decision on whether a descriptive two-region biological component provides sufficient macroecological novelty for the selected journal. A request for new independent field or observation support is a scientific limitation, not a reason to keep extracting p-values from the same original panel.

Frozen original Ecology Report, Paper 1, Paper 2, main and the parent climate PR #206 are unchanged.
