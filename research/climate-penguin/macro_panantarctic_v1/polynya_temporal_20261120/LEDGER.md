# Execution ledger

- Binding specification: ../diet_salinity_source_20261117/POLYNYA_TEMPORAL_CHL_SPEC_20261120_JA.md, committed before this analysis at 4f3ab035.
- Starting checkout: PR214, 4f3ab035; remote head verified. Existing unrelated caches left untouched.
- Task 1: retrieve original image-day provenance and audit dates; reconstruct P0 and P1 from verified DEEP-AA maps independently of next-year isotope availability.
- Task 2: save support before outcome analysis; run frozen models and full contrast covariance; validate fixed-effects algebra and region omission diagnostics.
- Task 3: proceed to the frozen chlorophyll stage only if the exact time-specificity gate passes; otherwise record the stopping decision.
- Task 4: independent review, report, figure, PR sync and verify remote head.
- Ruling: this is a source-day provenance audit using the original reconstruction artifact, not a new validation of guano classification or optical isotope calibration.
- Task 1 passed: 358 rows / 85 sites / 11 regions / 6 seasons; all source image days precede P1 by >=93 days; reconstructed P0 agrees within 3.6e-14.
- Task 2 passed exact gate: joint P0 negative and P0−P1 upper 95% limit −0.0792 per 10 pp; all 11 omitted-region signs negative. Explicit fixed effects and independent cluster sandwich reproduce results.
- Source correction before Task 3 model: independent reviewer identified changing validity in the proposed one-day DEEP-AA mask. Discard that pilot denominator; use static NOAA ETOPO1 ice-surface elevation <0 at native OC centres. Keep 100 km and monthly/daily eligibility thresholds unchanged. No C–Y model was run before this correction.
- Retrieval optimization: common region/month native rectangles, query-keyed cache, sequential necessary-condition screening. This permits a support failure decision from an upper bound, without pretending unqueried months were observed.
- Inferential disclosure: three labeled regions have zero FE-residual information. Preserve the frozen 11-region interval, but add/foreground the 8-informative-region t(7) interval; the coefficient contrast remains negative with upper bound −0.0293. This was a design-based audit, not selection by region effect size.
- Before C–Y fitting: interpret the frozen attenuation criterion conservatively as a negative pre-C P0 coefficient moving toward zero without a positive sign reversal. A sign reversal will not be counted as pathway consistency.
- Bootstrap optimization: because all absorbed FE are nested in regions, precomputed within-region cross-products are exactly equivalent to resampling whole regions and assigning new FE IDs to each copy. Six synthetic draws were checked against explicit copied-data fits. All 4,999 fixed-seed draws and failures will be archived.
- Task 3 complete: 112/358 rows, 55 sites, 10 labeled regions pass four-month OC-CCI support; only four regions carry FE-residual information. Pathway consistency not established. The restricted cohort P0 is already positive before C; no attenuation/mediation claim. All source retrievals succeeded. First-failed-month screening excludes 246 rows without imputing unqueried later months.
- Independent review verified temporal coefficients/contrast, native ETOPO indexing, monthly screening logic, explicit least-squares pathway estimates, cluster-bootstrap quantiles and a*b = -delta_beta identity. Superseded pilot outputs moved outside PR to work/polynya_temporal_review/superseded_pilot.
