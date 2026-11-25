# V35 — contiguous, stage-matched original Antarctic census changes (source evidence gate)

**Frozen after source QA V33 (562 high-quality original ASI N-stage records across 93 multi-year Site_ID×species histories) and independent physical land-source QA V34 (278 records on 38 exact SCAR land features), BEFORE original count growth ratios were calculated.** This is a new source-derived real-data longitudinal ecological *description*, not a meta-analysis of authors' fitted paper coefficients. The exact 2013 source census is already incorporated in some later MAPPPD time series; do not count same field data as independent external validation.

## Unambiguous original inputs

1. First-party original 2013 Antarctic Site Inventory 1,124-row CSV, exact publisher MD5 00871bd47b6ec30cda68d1506120bfb3 and SHA256 e01ee9bfbd8337bcaca7c71aea0b00162f9015cf4954d3ad76eed536cad37634, `Counted_object` N/C, Accuracy rank, `Source` ASI or original outside literature.
2. Original 113 ASI Site_ID → original SCAR ADD v7.12 land polygon 1:1 strict-site-point crosswalk, derived CSV SHA256 **279c85ea8976493fe780c4996183f87ac362945933d5cb80d0435a20d3fbcb26**, from successful V34 original GitHub Actions `40341465452`.
3. Locked selection **original ASI primary, Counted_object=N, accuracy rank 1/2, original numeric positive reported Count, valid original Season, original unambiguous four-character Site_ID × source taxon × Season, exact original valid lat/lon**, reproducing V33 562 rows before spatial matching; source land strict assignment leaves V34 278 original rows across 54 site IDs / 38 original land features.

## Primary temporal comparability gate

- **Never turn missing site-year into 0 or no breeding**; do not interpret never-observed colony as a vacancy or a transition.
- For each original Site_ID×Species, sort unique actually observed `Season` original breeding-season-start years. A genuine adjacent observed pair requires **year gap exactly one**; a 2–15 year gap is NOT one-year growth and must remain separately tabulated as source interrupted sampling.
- Original `Date` often has `xx` for missing day/month. Only fully valid source `mm/dd/yyyy`, with calendar year either Season or Season+1, defines a seasonal offset: days since Nov 1 of the original austral season year. No invented median dates.
- Primary future population growth comparison requires **both source dates complete** and within **±30 days of austral seasonal offset**; observational count `N` type and accuracy 1/2 already frozen. The ±30 days comparison tolerance is fixed before reading pairwise changes. Other adjacent counts are diagnostic only.
- For each accepted pair, report `log(N_{t+1}/N_t)`; original birth/death/migration, extinction probability and source unobserved zero are not identified by a change in nest counts alone.
- Report source adjacent-year pairs and phenology-aligned pairs per original seven region codes, seven taxa, exact parent mapped land feature ID; all responses weighted one per site×species×paired season but repeated pairs are correlated within site and land.
- **Support gate before a causal island/habitat ecological fit**: ≥3 geographical source regions each with ≥3 distinct strictly mapped physical land features, and ≥5 independent site×species adjacent-year comparable pairs in each; ≥3 source multi-season series per region. If failed, *stop physical-island ecological effect fitting*. This source support gate is not a biological null and does not assert absent habitat.
- If passed, any future original environment measurement must be explicitly independent of original response, methodologically predeclared, and robust to the high observed cross-map source rock disagreement. Large original continent land polygon and separate ice-free nunatak are not interchangeable.
- No arbitrary output "niche threshold", no post-result trimming of dramatic declines or growth, no mass regression with 278 pseudo-independent rows. Descriptive source growth median/p10/p90 per series is permitted but not a pan-Antarctic causal law.
