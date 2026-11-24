# Cape Shirreff: annual chick production and juvenile mass on the same observed seasons

Executed 2026-11-25 JST. New source: Sydeman & Thompson (2025), BCO-DMO DOI 10.26008/1912/bco-dmo.985565.1, v1 dated 2025-09-30, CC BY 4.0, [publisher metadata](https://www.bco-dmo.org/dataset/985565). Original recovery workflow [45425855761](https://github.com/zuizui0223/mina/actions/runs/45425855761), artifact 14935924098 SHA256 fbeeffce21a8323f8f9afa75986b6d3cc05d7d66053ee872a43a39d7251b0e06. Exact CSV 819408 bytes, publisher-listed MD5 53686f4df00bb61e184fafc30b432ecc, SHA256 1f1f7c0b6aeb4d9f4ae5288edea9b668666fcbc25bfa93c607229ec9d317c6e3. All verified. 6602 rows, 87 sites, 77 literal common-name labels versus metadata description 73 species; do not assume 77 valid taxa. Metadata copies disagree on revision/validation status; confirm stable version and consult contributors before publication. PDF text parameter definitions verified, screenshot unavailable. Original biological source Hinke et al. 2020 DOI 10.5061/dryad.2v6wwpzkh, inner ZIP SHA256 84e8a4ddd736dfcbb8050b38a4391714b7a283f3b00d42afef1f84f4d0b49df8 reopened, 14198 weights. BCO reports year = austral season START, Dryad YEAR = END, joined on YEAR=year+1. Same-number-year diagnostic strongly attenuates mass-productivity association, never a replacement alignment. No invented data or original source redistribution. These sources may share the NOAA monitoring programme; no independence claim. 

## Executed same-source precursor

19 chinstrap years with observed total chick counts and annual mass, not per-female productivity. Trend-adjusted log mass vs log total chicks +.041365 (omit-year +.034177..+.124577); 13 P100-complete years +.033732 after P100 and year adjustment; 14 adjacent year changes +.049221. Incident-year deletion (exclude both adjacent intervals touching deleted year) +.042627..+.149612. No causal density or individual brood-size inference.

## Direct matched productivity and weight

Cape Shirreff 47 BCO rows, CHPE 24 (1997–2020 start years), GEPE 23 (1998–2020); all finite positive. Exact 22 CHPE and 20 GEPE mass matches, common 20 seasons (1998/99–2018/19 excluding 2008/09), 4200 CHPE and 3225 GEPE weights aggregated once per species-year. Equal-year OLS, log(mean weight) ~ centered year + log(offspring per female). Both species evaluated on identical 20 seasons. Different measurement stages (GEPE age-standardized weight versus CHPE departure weight) and productivity monitoring vs weighed birds; no individual-level linkage.

| Outcome | Annual mass-productivity slope | Omit-year range | Adjacent-year slope | Incident-year deletion range |
|---|---:|---:|---:|---:|
| CHPE | +.034809 | +.031258..+.124141 | +.048336 | +.042251..+.132342 |
| GEPE | +.225840 | +.198925..+.248449 | +.130468 | +.094435..+.214911 |
| GEPE minus CHPE log contrast | +.032349 | +.017727..+.100298 | +.021654 | -.110466..+.052042 |

Median-mass slopes +.036478/+.190525 for CHPE/GEPE. Positive direction in both on 12 P100 complete common years after time+P100 adjustment (+.021390/+ .241247, all omissions positive). This does not establish individual quantity-quality tradeoff absence or a statistically tested difference in slopes.

## Does relative productivity explain the prior negative polynya–relative mass association?

12 common P seasons; log(GEPE/CHPE mean mass) P100 slope with year -.028867, after adding log(GEPE/CHPE productivity) -.029452 (omit-year -.036829..-.014307). P25 conditional -.032430 (all omissions negative). Thus the negative association is not removed by adjusting for measured relative productivity. NOT a causal mediation result. P100 coefficient of relative productivity +.015476 (partial R2 .006504, omission [-.001523,.028007]); absolute difference +.016150 (partial R2 .032106, omission [.004943,.029639]); full-adjusted log contrast +.193818 at P100 but P25 +.031557 (omission crosses zero). Do not claim stable P-driven reproduction or life-stage tradeoff. Same annual sample, no multiple-comparison inference or new p-values.

## Reproduction and next step

Executed code and tables local archive cas_quantity_quality_results_20261125.zip SHA256 4b9d2d18b3b237aa095495ff2f7ec246d9a9f084533b07c8518e3c181acec26d. analyze.py SHA256 79f921d6ddcd2b02e7bda63e2a6c1cf2727cc627645c4dc729d5a2ae03d3eda3; paired_productivity.py 4d15bf95401f88896372f38a6e81c64c2b8a8da1a9e60748bf5d3468ffd3e015; verify.py f38e113ae127a9d7958cf68e8ba8a1d785e98f165817b7abbaa8bb3d2f642e1e. Independent standard-library covariance slope check max 4.372e-16. Adjacent-change deletion CSV distinguishes ordinary endpoint omission vs true incident-year removal. Existing P and hydro derived matched-mass source reused with exact mean checks. The new CSV has 15 Pygoscelis site-species series at 11 named sites; next gate is true native P geographic support, especially Admiralty Bay, Palmer, Pointe Geologie, Signy and Cape Shirreff. Signy may repeat existing BAS source; subantarctic sites outside native Antarctic winter product must not be treated as zero exposure. No main merge or manuscript change.