# 南極ペンギンの種間繁殖巣数比は、海氷・水温軸と塩分軸のどちらに対応するか

**2026-11-11｜自前原本から実計算・実現したsource panelの上限｜単一の南極マクロ論文 Draft PR #214**

## 最終判断

**南極の海洋物理は二軸であるが、既知コロニーの2種間繁殖巣数変化を一貫して説明する「南極共通の2軸応答」は確認できない。**

ただし、ヒゲペンギン/ジェンツーの**同じコロニーで本当に同じ繁殖季に両種とも巣数を計測した記録**に限り、塩分主体のMarine PC2の高い年ほどジェンツー対ヒゲの log1p 巣数比が相対的に低い方向の**非常に弱い探索的な関連**が残った。個別の地域/ブロック欠落や年次調整を含む数値監査が必要であり、因果的に塩分がジェンツーの繁殖や競争を抑えることを意味しない。

**全18地域への一般化を阻む決定的感度：Central-west Antarctic Peninsulaを丸ごと除くと、暦年調整後の塩分PC2係数は−0.176→+0.072に符号反転**。また最初のsource群集モデルでの見かけの説明率はわずか2.09%、年次固定効果後の残差の説明率は**0.48%**。後者は異なる基準残差のin-sample R²であり、互いの精度や予測改善率ではない。

## Source and exact population

- 595原MAPPPD known breeding sites / 18原source reporting regions / 2,456 fixed most-frequent-method actual site×species×season nest records (unobserved never zero).
- Publisher-verified monthly OSI SAF v3.1 SIC 595 sites × 1991–2020 × Aug–Nov; original GLORYS12V1 202311 sea-surface salinity/thetao 588 sites / 18 reporting regions / 1993–2020 / 65,856 actual site-months across 378 original native marine reanalysis cells.
- Site×year balanced **588×28 = 16,464** environmental rows. Standardized source-only PC1 **60.3654%** and source-only PC2 **33.3773%**; original source site×year PC1 scores matched individually to **max absolute 1.78×10⁻¹⁵** when reconstructed without reading breeding outcomes. Fixed PC1 loadings (SIC−0.70734, salinity−0.03835, thetao+0.70583). Fixed salinity-positive PC2 (SIC+0.01216, salinity**+0.99772**, thetao+0.06640). Positive PC2 = higher original salinity-like reanalysis axis; positive PC1 = warmer/low-SIC orientation. Each PC score then divided by **its original entire 16,464-source-score standard deviation** so coefficients have comparable score units; no outcome-dependent axis refit.
- True 2-species same-colony same-breeding-year original counts were **351 records** across 3 fixed species pairs (ADPE/GEPE 98; CHPE/GEPE 165; ADPE/CHPE 88). Of those, dual species same counting method **97/98, 165/165, 88/88**. "Same year" does NOT establish same day, source citekey, effort, or demographic sampling area.
- Biological contrast = log1p(originally OBSERVED nests for second species) minus log1p(originally OBSERVED nests for first species). Recorded count 0 retained, species/site/season without an actual observation never treated as zero. First count a true source observation not verified *local ecological absence*.
- Source-trained physical PCs are not species niche thresholds or greenhouse forcing instruments; GLORYS reanalysis includes assimilated data and marine processes.

### The actual source biology, three species-pair comparisons

| Species numerator / denominator | Original actual same-year records | Primary both-method-matched records | Source repeated sites / independent source 250km blocks | Raw r(PC1, nest log ratio) | Within-site r PC1 | Within-site r PC2 |
|---|---:|---:|---|---:|---:|---:|
| Gentoo / Adélie | 98 | 97 | **11 / 3** | −0.145 | −0.008 | −0.033 |
| **Gentoo / Chinstrap** | **165** | **165** | **20 / 5** | −0.036 | +0.061 | **−0.102** |
| Chinstrap / Adélie | 88 | 88 | **9 / 3** | −0.131 | −0.042 | +0.008 |

n repeat sites excludes single-year source locations. The 351 line items are **not 351 independent ecological populations**: 98/165/88 observations share colony codes, source years, GLORYS cells and 250km geographic blocks. The sign of the raw vs within-site association can differ, as already found in the initial 34-colony panel. No p-values or false spatial IID confidence intervals.

### Same-site, same-survey-year response to BOTH physical marine axes at once

Within each fixed source site, center original two-PC scores and the log1p nest ratio. Fit site-equal (site total weight 1, not n-year-weighted) 2-PC OLS; coefficients below are descriptive log1p nest-ratio units per 1 global full-588-site-year PC SD. Site effects do NOT control shared calendar-year conditions.

| Species ratio | Thermal-ice PC1 coef | Salinity PC2 coef | Within-site observed source records | In-sample site-centered R² (not forecast) |
|---|---:|---:|---:|---:|
| Gentoo / Adélie | **−0.113** | +0.068 | 84 / 11 repeat sites | **0.54%** |
| Gentoo / Chinstrap | +0.070 | **−0.187** | 152 / 20 repeat sites | **2.09%** |
| Chinstrap / Adélie | +0.054 | +0.055 | 73 / 9 repeat sites | **0.65%** |

In the Gentoo/Chinstrap pair, exact original count-zero sensitivity excluding actual recorded 0 nests at either species (165→135 source rows, repeated sites20→18, no fake true absences) changed PC1 +0.070→+0.006, PC2 **−0.187→−0.137**. This is the origin of a weak salt-axis hypothesis candidate; it did not emerge as a general 3-pair response law.

The standard same-site model is not a species niche selection model, demographic survival model or validated time-wise forecast. The sample is source-selected geographically and by shared monitoring.

## Critical independent SOURCE calendar-year diagnostic: common time effects

Because ocean salinity/sea ice and penguin counts can both vary across calendar years, the same observed co-census subset was refitted using **weighted site+calendar-year fixed effects**, via exact weighted Frisch–Waugh–Lovell residualization. Only repeat source sites were used and **actual common year records not filled**. A calendar-year FE also discards genuine shared climatic responses; it is a conservative post-result diagnosis and not uniquely correct biology.

| Species ratio | Site-only salinity PC2 coef | Site + year PC2 coef | Site + year PC2 with source 0 nests excluded | Site + year residual in-sample R² |
|---|---:|---:|---:|---:|
| Gentoo / Adélie | +0.068 | **−0.475** | −0.418 | 8.01% |
| **Gentoo / Chinstrap** | **−0.187** | **−0.176** | **−0.083** | **0.48%** |
| Chinstrap / Adélie | +0.055 | −0.159 | **+0.301** | 6.38% |

The source Gentoo/Chinstrap shared-year co-count has **20 actual repeat sites, 3 source regions, 5 polar blocks, 152 source records and 27 distinct observed calendar years**, with 26 years having ≥2 source sites. Source-year FE design leaves unclustered algebraic residual DF104 (not independent ecological trials) and a source full-rank two-PC regression. With original recorded zeros removed, 18 repeat sites / 122 source records and 77 algebraic DF remain. The poor 0.48% source residual R² indicates no compelling biological prediction from these two climate PCs.

By contrast the ADPE/GEPE and ADPE/CHPE results change sign under year adjustment/zero exclusion, confirming that their original limited pairwise associations are sensitive to observational time structure. The year-FE site model must not be selected because it gives a bigger R² (its response variance has already been conditioned on calendar year).

### True geography changes the conclusion

When the source year+site fixed effect Gentoo/Chinstrap salt-PC2 model was re-estimated after removing every original source region/block **ONE AT A TIME**:

- Drop any **one polar250km block**: PC2 coef **−0.2539 to −0.0069**, negative in all source block omissions, but sometimes nearly zero.
- Drop any **one original source region**: PC2 coef **−0.1834 to +0.0724**, **sign changes**.
- The reversal is specifically caused by omitting **Central-west Antarctic Peninsula**: salt-PC2 −0.17596 (all)→**+0.07241**, with only **2 source regions and 3 original blocks** contributing repeated same-site/year biological information afterward. Omitting South Shetlands still yields −0.18335, with 2 regions / 3 source blocks.
- Two other species-pair PC2 source year-FE coefficients also fail region and spatial-block sign stability (ADPE/GEPE region delete −1.434→+7.472, ADPE/CHPE some region deletion is unidentifiable after residualization).
- **Never label this observation a general Southern Ocean salinity-controlled species turnover.** The source original site count and year support are real, but their ecological transfer scope is limited by regional gradients, species survey program, biological source synchronization and GLORYS cell geography.

This is a failure to reproduce a common association geographically, not a causal statistical test that salinity does not matter biologically.

## Actual longitudinal ORIGINAL co-census site slopes

A separate, more stringent temporal unit is each source colony site with both species genuinely counted in **at least 3 source seasons spanning at least 10 years**. Count and physical PC1/PC2 slopes are fit to identical real observed co-count years per site, not asynchronous 10-year climate bins.

| Species ratio | Qualifying original time-series sites | Source regions | Polar250km blocks | Site-equal across-site corr, observed count logratio change vs salinity-PC2 change |
|---|---:|---:|---:|---:|
| Gentoo / Adélie | 7 | 2 | 2 | +0.154 |
| **Gentoo / Chinstrap** | **15** | **2** | **4** | **−0.196** |
| Chinstrap / Adélie | 6 | 2 | 2 | +0.020 |

Within-source-region centering of those qualifying site slopes for Gentoo/Chinstrap yields r≈−0.158. These are **longitudinal real colony units, not site×year pseudoreplication**, yet only 2 geographic source regions each have 3+ observations per site over ≥10 years. No 18-region independent temporal transfer.

## Supported ecological synthesis and next evidence

1. **Supported physically across 18 regions:** Antarctic coastal sea-ice concentration and water temperature share one strong spatial marine gradient; ocean salinity is a second largely orthogonal dimension; the time trajectories differ by region and decade. The old 34-site salinity-as-PC1 interpretation does not transfer to the new source geography.
2. **Observed biology:** Real 2-species original nest counts can be compared in 351 source site-years, but the two physical axes do not universally covary with within-site shifts. Three pairwise source relationships are numerically weak.
3. **Exploratory mechanism candidate:** Gentoo-vs-chinstrap source count ratio and salinity-oriented axis show negative direction after original site/calendar-year and source recorded-zero diagnostics. This is NOT validated out of sample. It is geographically concentrated and flips after excluding the Central-west Antarctic Peninsula, so a universal salinity-niche-switch narrative is NOT supported.
4. **Not established:** future temperature effects on breeding, salinity acting causally, long-term penguin range migration, winter habitat tracking, independent Peninsula vs Ross Sea ecological time response, historical colonial occupancy / verified absences, greening co-evolution. Static 2017–2023 Plantarctica maps contain neither true 1993–2020 plant productivity changes nor a future greening trajectory.
5. **Next high-value external validation:** Source independent *in situ* or hydrographic transects in distinct Southern Ocean regions, paired with genuinely repeated same-method penguin simultaneous nest counts or prey/foraging observations, would be needed to assess the mechanism. Repeating correlations with threshold/lag tuning on the present two-region biology is not useful.

## Reproducibility and changes

- **Physical full 18-region source run [#42961084667](https://github.com/zuizui0223/mina/actions/runs/42961084667), artifact 13829236358**; before that original 588-site hydro fields [#42958013800](https://github.com/zuizui0223/mina/actions/runs/42958013800).
- **Source-only species-matched 2-PC exploratory run [#42969734584](https://github.com/zuizui0223/mina/actions/runs/42969734584)**, artifact **13832576882**. Includes all 351 original site×species×year co-count records, fixed physical PC1/PC2 scores, source 3plus co-count site slopes, leave-one-region/block source coefficients, exact all-PC provenance. Original 6 unit tests passed after fixing an earlier synthetic test that incorrectly used a 5-observation helper despite the frozen 3-observation site-slope rule.
- **Source calendar-year FE/recorded-zero geographic sensitivity [#42970845705](https://github.com/zuizui0223/mina/actions/runs/42970845705)**, artifact **13832319364**. Includes 3 fixed species pairs, site and year FE source support, year-FWL residual model rows, source region and original polar block omission sensitivity, original 5 arithmetic unit tests.
- Frozen source-driven plan: DUAL_MARINE_AXIS_PENGUIN_COCENSUS_EXPLORATORY_CONTRACT_20261111.md. Post-result sensitivity: DUAL_MARINE_AXIS_COMMON_YEAR_DIAGNOSTIC_20261111.md.
- Code: test_dual_marine_axis_paired_penguin_response.py, audit_dual_marine_axis_calendar_year.py, six and five source-free arithmetic tests and source pinned GitHub Actions workflows in the same PR. Output/source attachments stay in GitHub Actions rather than inflating fixed manuscript files.
- No changes or automatic merges of main, frozen Paper 1/2, prior climate PR #206, or separate penguin bright/dark PR #215. All are kept in the single Antarctic warming and niche manuscript research trajectory within Draft PR #214.
