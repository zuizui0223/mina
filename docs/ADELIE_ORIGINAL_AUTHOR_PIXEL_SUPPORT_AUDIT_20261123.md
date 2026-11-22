# Adélie original image-selection gate — source-verified audit (2026-11-23)

**Completed.** The original Youngflesh et al. (2026) pixel selection was reproduced on the published RDS with the actual source author rule from `Scripts/4-diet-est.R`: per-image `n_pix` by (`site_id, season, month, day`), then **site-wide pixel-row-weighted mean** `avg_n_pix >= 2`. Unlike earlier descriptive screening, this is NOT a site-by-year pixel threshold and does NOT require 4 years observed.

## Verified counts

| Stage | Original / reproduced | Distinct sites |
|:--|--:|--:|
| Published raw Landsat RDS | 179,462 pixel rows | 146 |
| Original author-wide quality gate | **179,346** pixel rows | **119** |
| Original-gated source years 2004–2010 | **583 site-years** | **113** |
| Earlier descriptive (unjustified extra) screening | 472 site-years | 88 |
| Actual frozen isotope manuscript (requires archived derived-panel join) | **439 site-years** | **85** |

The source-author script yields **179,346 pixels at 119 sites**, exactly agreeing with the original published `4-diet-est.R` comments. The isolated Actions execution is https://github.com/zuizui0223/mina/actions/runs/45081645133 .

## Full key-based overlap audit for original 583 vs earlier 472

The earlier 472 are **exactly a subset** of the original 583 site-years. All 111 excluded rows were explained **without viewing isotope response values**:
- **64** failed the earlier (incorrect) site×year average ≥2 pixels/image-day rule;
- **47** passed that rule but belonged to a site with fewer than 4 qualifying years under the extra threshold.
The lost 111 comprise **93 records from 25 entirely omitted sites** and **18 records from 15 sites otherwise retained**.
- The original *Queen Mary Land* source site `HASW` has **2007, 2009, 2010**; it is absent from the old 88 and present as a three-record single-colony region in the frozen 439 model, so **the old 88 CANNOT be treated as the manuscript 85-site cohort**.
- The other two non-informative-region checks match the manuscript counts: *Adelie Land* `PGEO` (2006–2010, five source years) and *Palmer Land* `SIMS` (2004–07, 2009–10, six source years).

The machine-readable 583-row lineage table and exact source-vs-preliminary rowwise classifications were computed and separately archived in `adelie_439_85_lineage_audit_20261123.zip`.

**Do not infer** that the 439 final rows are precisely 583 minus 144 named records: the final 439 frozen keys are still not available here for row-by-row matching. Do not claim new ecological validation, conservation effectiveness, or change the current δ15N result.

## Next necessary gate

Re-extract 2004–2010 Jun–Oct DEEP-AA for **all 583** original author-supported site-years using original publication MD5. Record missingness and source-based descriptive variability. Only after a verified frozen derived-panel crosswalk should a manuscript-grade 439/85 protected-area overlay be made.
