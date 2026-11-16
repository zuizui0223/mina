# Candidate v0.6 abstract — climate-linked responses and the spatial grain of penguin breeding

**2026-11-17 | mina PR #214 | candidate hypothesis-led abstract, NOT a replacement of source-pinned v0.5 and NOT a journal submission.**

## Proposed title

**Climate-linked trophic variation and spatially structured breeding change in Antarctic penguins**

## Abstract (candidate, evidence-bounded)

Antarctic penguins may respond to marine environmental change through resource use, population size, and redistribution among breeding colonies. These responses need not follow the same environmental gradient, yet are often conflated when evaluating climate vulnerability. We combined source-audited nest counts for three *Pygoscelis* species (2,456 original records across 595 catalogued breeding sites), 1991–2020 satellite sea ice, coastal ocean reanalysis at 588 sites, and published individual-level diet archives to contrast environmental and biological changes across observational scales. The marine environment varied along a temperature–sea-ice axis (60.4% of principal-component variance) and a separate, largely salinity-associated axis (33.4%). In repeatedly counted Adélie colony rosters, nest-count-weighted latitude shifted 88–107 km south between the 1990s and 2010s, whereas corresponding nest-weighted nearshore sea-ice concentration differed by only 0.02–0.63 percentage points. Gentoo-to-Adélie nest ratios increased at all six strictly source-matched colonies in two regions, while their observed two-species nesting subtotal increased at five of six, distinguishing relative composition change from absolute loss. At Signy Island, gentoo fish use covaried with preceding sea ice over nine breeding seasons; a four-season sequential retrospective holdout improved local prediction over a mean baseline, but the same relationship transferred poorly to Palmer. Under a three-model late-century CMIP6 scenario, fixed historical nest-weighted sea-ice exposure differed strongly from site-equal exposure, while species contrasts were sensitive to shared geography and offshore grid support. Together, these observations indicate that local resource use, relative species composition, and colony nesting allocation carry information at different spatial and temporal scales. They do not identify a universal climate-driven demographic response, individual breeding dispersal, or a forecast of future colony persistence.

## 日本語の中心命題

南極ペンギンでは、海氷に関連する食性の季節変動、同所的な種構成の変化、既知繁殖地間での巣数配分の再編が観測される。ただし、これらは同じ時間・空間スケールの応答ではない。地域・元の繁殖地配置・観測支持域を揃えない限り、見かけの温暖化傾向を種別の人口減少・繁殖地の移動率・将来の局所絶滅へ変換できない。

## Claim/evidence gates — pre-publication

| Proposed statement | Evidence / denominator | Gate |
|---|---|---|
| Regional climate universally drives colony growth (reported ADPE β=−0.80, 265 source series) | 265 source roster with ADPE102/CHPE116/GEPE47 not recovered; old frozen method series 159, current 268 publisher reproducible; latter β intervals cross zero | **Do not include** |
| Different species show opposite quantitative breeding-phenology slopes (+0.40/−0.42) | Not verified in this PR's original long-term date/effort matched census; Signy arrival proxy correlates strongly with first survey day | **Hypothesis/local contextual observation only; no numeric slope in Abstract** |
| Diet covaries with preceding ice in Signy | Gentoo fish-share vs SIC r≈+0.788 over 9 seasons; internal 4-year historical holdout improvement 46% vs mean for Gentoo, 43.2% for 3-species separation; transfer to Palmer substantially worse than Palmer-local mean | **Positive local association, not transferable forecast** |
| Adélie count-weighted latitude shifts south | +107.31 km/19 three-decade matched colonies; +88.41 km/26 two-endpoint strict colonies; nearshore SIC +0.022/+0.625pp | **Observed fixed-roster reweighting, NOT bird movement or proof locations cannot change** |
| Six reciprocal gentoo/Adélie pairs | 6/6 nest ratio increases, 5/6 two-species subtotal increases at same-source/same-method colonies | **Relative community composition, not region-wide species extinction/replacement/competition** |
| CMIP6 physical losses under SSP5-8.5/2081–2100 | 595 equal sites −21.44pp, counted 271 equal sites −28.63pp, same 271 nest proxy weighted −13.28pp; 3 models | **Physical fixed-weight scenario, not future nest forecast** |
| Climate vs configuration decisive model | Existing 2010/2015 first-held-out nest-count SSM: log1p MAE persistence 0.337/0.241, marine-SIC-SSM 0.386/0.342, but last-observed-nest persistence is NOT a measured within-colony patch-configuration predictor | **Do not claim a spatial-configuration model won** |
| Positive selection into better-colony sites, Bird Island p=0.0001 | Original individual-level movement/first-breeding event ID and prospective protocol not verified in current PR #214 | **Mechanistic hypothesis only, excluded from Abstract** |
| Concentration replicated across Palmer, Signy and other groups | Multiple positive within-network examples, but colony/patch, island and species all have different grain; broad leave-one-region and source/measurement qualification remains | **Interpret as supporting spatial-configuration context, NOT a pooled universal causal coefficient** |

**Do not silently replace the four existing main v0.5 figures or overwrite the v0.5 paper.** This is a writing candidate for author review. The 2026-11-16 older −2.2 pp limited CMIP6 mean does not replace the source-audited 595/271-site latest physical exposure means.

## Original source pointers

- \`macro_panantarctic_v1/MANUSCRIPT_MACRO_V0_5_COMPACT_BIOLOGY_FIRST_WORKING.md\`
- \`macro_panantarctic_v1/RESULT_ORIGINAL_588_18REGION_MARINE_AXES_JA_20261111.md\`
- \`macro_panantarctic_v1/DECADAL_REWEIGHTING_RESULT_JA_20261110.md\`
- \`macro_panantarctic_v1/climate_risk_frozen_20261116/CMIP6_595_COUNT_WEIGHTED_PHYSICAL_EXPOSURE_RESULT_JA_20261116.md\`
- \`macro_panantarctic_v1/climate_risk_frozen_20261116/SPECIES_COMMON_REGION_SITE_COYEAR_PHYSICAL_EXPOSURE_RESULT_JA_20261117.md\`
- \`research/climate-penguin/outputs/signy_species_trophic_forward_v1/REPORT_JA.md\`
- \`research/climate-penguin/outputs/regional_diet_paper/MANUSCRIPT_JA.md\`
- \`macro_panantarctic_v1/population_dynamics_20261116/POPULATION_DYNAMICS_SSM_BACKTEST_RESULT_JA_20261116.md\`
