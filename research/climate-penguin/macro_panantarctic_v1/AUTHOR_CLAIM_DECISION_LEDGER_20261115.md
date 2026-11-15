# Antarctic penguin macroecology: author claim ledger (2026-11-15)

Canonical single working manuscript: [v0.4](MANUSCRIPT_MACRO_V0_4_SOURCE_GATED_WORKING.md). Draft PR #214, not submitted. The v0.3 draft is preserved as provenance.

## Source-supported results

| Claim | Estimate and support | Status and use |
|---|---|---|
| Coastal physical axes are distinct | Original 588 known colonies, 18 reporting regions, 378 unique GLORYS cells, 1993–2020 PC1 thermal–ice 60.37%, PC2 salinity 33.38%; 1993–2018 PC1 60.15%, PC2 33.49% | Retain as a descriptive physical result; Figure 2 |
| Geographic biological support is much narrower | Marine physical 588 sites/18 regions → 85 matched site-species series at 65 sites/6 regions → 18 paired series at 12 sites/2 regions; 0 of the 12 strict sites in coldest PC1 climate quartile | Restrict biological transfer; Figure 1 |
| Gentoo relative nesting gains are locally reproducible | 6/6 source-matched gentoo/Adélie ratio slopes increase; two-species observed subtotal rises 5/6 | Figure 4: descriptive local reassembly, not competition or pan-Antarctic law |
| Relative composition and subtotal are different observations | 34 actual three-species site-years at three colonies: gentoo share rises at all three while three-species observed subtotal rises in two and falls in one | Supplement; do not equate nesting shares with population growth |

## Independent salinity source-gate progress (2019–2020)

- Same-source negative controls on 378 distinct GLORYS wet cells, using each cell's own 1993–2018 reference: salinity anomalies below −2 SD at **239/378 cells (2019)** and **310/378 cells (2020)**, versus seawater temperature **7/378 and 11/378** and original nearshore OSI SAF SIC **0/378 and 8/378**, respectively. [Cell-wise actual-source table](source_audit_20261115/GLORYS_378cell_2019_2020_three_variable_anomalies.csv), [methods / caveats](GLORYS_2019_2020_CROSSVARIABLE_DIAGNOSTIC_JA_20261115.md). This is an additional **same-source diagnostic only**, not independent field validation nor climate attribution.
- **EN4 2017–2020 raw-source original field-data gate completed — confirmed NO-GO due to observation support.** [Publisher-source QC SUCCESS #43681294518](https://github.com/zuizui0223/mina/actions/runs/43681294518), artifact **14149243392**: 16 original NetCDF months, 714,756 globally archived profiles, 2,414 Antarctic near-colony profiles passing depth 0–10m and 100-km QC, allocated 316/364/887/847 across 2017–2020. 2018 has 0 region-month cells with ≥3 identifiable platforms; **0/18 regions qualify** for ≥2 common Aug–Nov months with ≥3 platforms in every source year. Relaxed 250km/20m yields only Victoria Land Oct–Nov, platform-equal **+0.08914** (2019–2020 minus 2017–2018), not equivalent to the pan-Antarctic GLORYS 26-year anomaly. This **does not falsify** GLORYS or independently validate broad freshening. [Complete original-source report](EN4_2017_2020_RAW_SALINITY_OBSERVATION_RESULT_JA_20261115.md), [machine summary](EN4_2017_2020_RAW_SALINITY_QC_SOURCE_SUMMARY.json), [frozen prior source design](EN4_2017_2020_INDEPENDENT_TIME_GATE_PROTOCOL_20261115.md).

## New 27-interval source-year step audit

The original source-verified 588 colony×28y climate data were aggregated once per **378 true GLORYS wet cells** and tested across **every year-to-year change from 1994 to 2020**. The **2018→2019** change in the median original-cell salinity was **−0.42344**, the most negative of 27 intervals; **346/378 cells** declined and **188/378** had a change more than two historical 1994–2018 within-cell annual-difference SD below expectation. In 2020, the corresponding figures were −0.20505, 298/378 and 54/378. A regional sign alone is not unique to 2019: 2010 also showed **18/18 reporting regions** with a negative median cell step, but only 28/378 cells below −2SD and median step −0.20486. Thus the identifying property is the **exceptional magnitude of the 2019 source step**, not a novel common negative direction. [Full 27-step QA and independent recomputation](GLORYS_2019_YEAR_ON_YEAR_STEP_GATE_JA_20261115.md). This is *source-only temporal evidence*, not validated in-situ freshening or a proven ERA5 forcing artifact.

## Held claims and required evidence

| Gate | Source result | Prohibited extrapolation / necessary validation |
|---|---|---|
| GLORYS salinity temporal coherence: SOURCE HOLD | 18-region PC2 common-year fraction 52.14% (1993–2020) vs 29.29% (1993–2018); 2019 and 2020 below pre-2019 in all 18 reporting regions and 368/378 and 363/378 ocean cells | Do not claim an independently verified pan-Antarctic salinity event. Copernicus forcing switches from ERA-Interim to ERA5 in Jan 2019, a possible source confound, not proven cause. Independent same-period hydrography or controlled source product is needed |
| Universal penguin climate response: NOT ESTABLISHED | Six region matched 85 site-species panel; each region-adjusted joint two-PC block interval spans zero | No 2050/2100 calibrated nest forecast or species-level universal climate coefficient |
| Warming–terrestrial vegetation mediation: NOT TESTED | Land polygon observations cover one static 2017–2023 composite | Do not infer annual greening or a dynamic vegetation-mediated climate pathway |
| Spatial tracking / displacement: NOT ESTABLISHED | Fixed-roster observed Adélie weighted nesting latitude moves 88.41 km south at 26 sites | Not individual dispersal, true species range movement, or climate-niche tracking |

## Author-facing decision

The supported unifying claim is that Antarctic coastal marine data span at least two distinguishable statistical physical dimensions, but the geography and time support of repeated breeding censuses are too narrow to establish a transferable climate response across Antarctic penguin communities. Local species-composition changes and monitored nesting totals are not zero-sum equivalents. The exceptional full-period salinity synchrony stays explicitly qualified by 2019–2020 reanalysis source-year sensitivity.

Keep one manuscript and four main figures. No new post-hoc p-value search, biological future forecast or climate forcing causal claim. Original main, Ecology Report and frozen Paper1/Paper2 are not changed.

Sources: [2019–2020 salinity QA](GLORYS_2019_2020_SOURCE_GATE_JA_20261115.md); [biological support](CLIMATE_VS_BREEDING_SUPPORT_SCOPE_JA_20261115.md); [same-source nesting subtotal](strict_pair_20261115/REPLACEMENT_VS_COMMUNITY_TOTAL_JA_20261115.md).
