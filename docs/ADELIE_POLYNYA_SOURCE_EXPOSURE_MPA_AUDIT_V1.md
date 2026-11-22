> **SUPERSEDED for manuscript cohort mapping (2026-11-23).** The correct frozen 439-colony-season / 85-site data have now been recovered from original Draft PR #214. The 472/88 result documented below is retained ONLY as an independent source-reconstruction and historical methods audit, not as the manuscript cohort or definitive MPA map. See [ADELIE_FROZEN_439_85_MPA_AUDIT_20261123.md](ADELIE_FROZEN_439_85_MPA_AUDIT_20261123.md) and the successful [source-matched workflow](https://github.com/zuizui0223/mina/actions/runs/45082480478). Current designated MPA 100-km overlap is **15/85**, not the provisional **18/88**.
# Source-based Adélie winter-polynya exposure vs current CCAMLR MPA: independent audit (2026-11-22)

**Outcome:** full public-source re-extraction completed, generating a descriptive **472 source-site-years / 88 source sites** map. This is NOT the existing **439-season / 85-site** frozen optical δ15N analysis cohort.

## Original source authenticity

- Youngflesh et al. (2026), Zenodo https://zenodo.org/records/17409948, original `data.zip` 256,425,816 bytes, MD5 `e29a2f68c84e3a515044d554540def2f`; RDS `landsat_reflectance_L457-2025-07-16.rds` read by native R `readRDS()` after third-party Python reader rejected its embedded `sf` type. Source rows 179,462. Filter `bad=0`, `guano_bin=1` yields 625 source site-years at 134 sites during 2004–2010; ≥2 mean quality pixels per image-day gives 522/113; ≥4 observed years gives 472/88. **These thresholds are provisional source rules, not a proven reproduction of exact image-level frozen selection.**
- DEEP-AA Lin et al. (2024), Zenodo https://zenodo.org/records/13358042, `SIC60_6.25km_20d.zip` MD5 `f3f958389cc5e67ac1c4e3a6ee164318`. Official 1,071 daily 6.25-km maps for 7 Jun–Oct winters 2004–2010. Geodesic 100-km sampling around source-derived colony-pixel centroids; positive even `Map` IDs are coastal polynyas. Five months equal weight; ≥80% days/month. ALL 472 source-eligible rows have winter exposure; hence **the 472→439 difference is NOT due to DEEP-AA winter missingness in this period**.
- Source 472 exposure distribution: mean **7.2207%**, SD **6.2800 pp**, range **0–26.7126%**, 28 true measured zeros. Original frozen 439-panel mean **7.03%**, SD **6.32 pp**. Close values do not establish rowwise identity. This re-extraction uses approximate spherical cell-area Jacobian, not exactly the archived native projection correction.
- CCAMLR official mapped MPAs: https://github.com/ccamlr/data/blob/main/geographical_data/mpa/CCAMLR_MPA.json ; polygon CRS EPSG:6932; Ross Sea five zones, South Orkney southern shelf one. **Current** geometry, not historical protection.

## Source-pool geographic summary (not a causal or inferential contrast)

- 88 source-eligible sites with ≥4 complete observed source winters; median within-site SD of annual winter coastal-polynya percent **2.823 pp** (mean 2.574).
- A geodesic circle of 100 km around **18 of 88** source sites intersects a designated CCAMLR MPA polygon; all overlap sites have Ross Sea GPZi overlap; two also touch KRZ. This is **not the percentage of feeding habitat protected**, nor guaranteed ocean-area overlap.
- Median source-site SD **0.794 pp** in 18 overlap sites versus **2.894 pp** in the other 70; this strongly aliases geography (Ross Sea versus other Antarctic regions), observation support and designation dates, hence **no inference that protection causes lower polynya variability**.
- No source site 100-km circles overlap the South Orkney southern-shelf polygon; not evidence for absence of protected penguins or for poor protection effectiveness.

## Residual blocker and manuscript decisions

- Published frozen analysis uses **439 colony-seasons at 85 sites**. Missing source-to-manuscript selection comprises 33 candidate site-years and 3 candidate sites, attributable to **UNDETERMINED** selection and covariate support; winter DEEP-AA seasonal availability no longer explains it. To reproduce final 85-site variability and final 100-km MPA overlays, the original frozen **439-row derived panel** and source centroid crosswalk must be obtained. An older author-review ZIP containing derived inputs exists in the user's ChatGPT Library, but its raw bytes were not available to this runtime.
- Do **not** insert the 88-site source map into the submitted main figure set as the 85-site map; it may be shown as an explicitly marked supplemental reconstruction with provenance.
- Do not call site SD “diet sensitivity”: the manuscript identifies a shared conditional regression, not independent site-specific slopes. This map does not test a biological mechanism.
- Continue original manuscript submission preparation without depending on this descriptive conservation overlay.

## Audit trail
- Native Youngflesh RDS site-years: https://github.com/zuizui0223/mina/actions/runs/45031823417
- Independent DEEP-AA 2004–2010 source re-extraction (official MD5 validated): https://github.com/zuizui0223/mina/actions/runs/45032409092
- Re-extraction code: `scripts/reconstruct_adelie_source_polynya_20261122.py`.
- Result artifact from the run: `adelie-deepaa-descriptive-source-exposure`, including 472 candidate source site-years, monthly exposure and full 80%-monthly coverage report.
- Spatial overlay and provenance kept locally in complete research ZIP supplied with this turn.
