# 南極アデリーの海氷・塩分と食性proxy：同一季節の原本マクロ解析と地域異質性

**2026-11-17 JST | mina Draft PR #214 | original-source derived exploratory analysis; NOT a confirmatory species-wide causal/diet study, NOT revised Paper1/Paper2, NOT a future abundance forecast.**

## 生態学的結論候補（範囲を明示）

> 南極アデリーペンギンの原著衛星画像から再構成したδ¹⁵N（食物網・環境の影響をともに受ける同位体proxy）は、海氷・水温・観測日・既知繁殖地・地域×年を調整しても、表層塩分の同季節変動と**全体では正に関連**した。ただし同じモデルを海域別に当てると南西南極半島では**負**、北東南極半島はほぼ**ゼロ**、Victoria Land/Wilkes Landは**正**。13地域単位の保守的クラスタ推定では全体係数の95%区間は**ゼロを含む**。

この結果は元論文Youngflesh et al. 2026の「sea-ice vs diet」の再発見ではないが、**真の魚食率やkrill消費量、海氷・塩分の因果効果、あるいは大陸一般則を実証したものでもない**。意義の候補は、見かけの「環境一軸→食性一方向」が海域ごとに異なる可能性を、同一season・同一colony source ID・元衛星画素・実海洋解析を使って明示したこと。

## 元データと実際の原本照合

- Original biological source: Youngflesh et al. (2026), *Current Biology*, DOI:10.1016/j.cub.2026.06.028; Zenodo DOI:10.5281/zenodo.17409948 / original 256,425,816-byte ZIP **MD5 e29a2f68c84e3a515044d554540def2f**.
- Original isotope spectra: **103 original calibration specimens**, per sensor original published 350–2500nm RSR, 6 synthetic Landsat bands; reconstruction **five-component PLSR**, with 100-times stratified random calibration CV median RMSE L4=1.722, L5=1.741, L7=1.742 δ¹⁵N‰. **Not identical** to original authors' R \`pls::plsr(method=oscorespls)\`, missing original 1000-ensemble source coefficients and Stan posterior.
- Original 179,462 Landsat pixel rows / 146 sites / 1,410 site×season / 4,038 days. Replicated author filter mean pixel count≥2: **119 sites / 179,346 pixel rows / 3,938 days** exact original author comments. Geography crosswalk strict within 2km, identical source site ID and no ambiguity vs MAPPPD; original source GI 892 site×seasons; after pixel filter **860 source site×seasons, 88 sites, 82 unique GLORYS native wet cells, 13 reporting regions, 15 start seasons 1996 and 1999–2012**.
- Marine source actual 11–following February from GLORYS12V1 202311 original near-colony wet-grid point salinity and sea temperature, all four months per source season. **Original NOAA/NSIDC G02202 Version 4** native 25km monthly SIC, source location 150km projected buffer, seasonal 4 months. Actual NetCDF dimensions expose bare 0..315 and 0..331 indices; explicit projected **pixel centers** are x=-3,937,500..3,937,500; y=4,337,500..-3,937,500, 25km steps, EPSG:3412. Native geographic support=60 true months×99 image sites =5940 site-month, **892/892 complete site-seasons**, minimum 36 valid original ocean cells per site×season's least-covered month.
- **Essential corrective source geometry note**: official GeoTransform upper-left **grid outer boundary** is x=-3,950,000, y=4,350,000 (NOT pixel center), see [NSIDC projection guide](https://nsidc.org/data/user-resources/help-center/guide-nsidcs-polar-stereographic-projection) and [official ERDDAP original source metadata](https://coastwatch.pfeg.noaa.gov/erddap/pt/griddap/nsidcG02202v4sh1day.html). A separate wrongly centered +12.5km horizontal/vertical QA run produced β=+0.82580; true 25km pixel centers produce β=+0.83415. **The former is strictly a grid-position sensitivity, not a second result or the canonical value.**
- Original paper used R \`terra::extract\` with an EPSG:3412 150km circular buffer; our Python uses native 25km **cell-center inclusion** of its circles and valid ocean cell mean. Thus it is **not** numerical identity to the author's unarchived \`colony_sic.csv\`. All source values are independently original and the buffer is approximately equivalent geometrically, but this distinction remains a QA gate.

## 凍結した観測単位・推定対象と結果

One real matched \`site_id × season\` per row, 860 rows. Response \`Y\` is the **day-equal average original-pixel-derived PLSR δ¹⁵N proxy** (not actual guano isotope measurement for all 860, not original hierarchical DI posterior). Minimum original image filter avg pixels≥2 applied at entire site, no fabricated zero/non-sampled year. Fixed 11–Feb marine salinity, temperature and NSIDC sea ice all aligned to source season.

\`M0: Y ~ original image DOY + DOY² + temperature + SIC + site fixed effects + (original region×season) fixed effects\`; \`M1: M0 + salinity\`. Same 860 original source rows in both; FWL projection; no change of radius or variable window based on p-value.

| 全860 site-season | 係数・数値 |
| --- | ---: |
| **Salinity β, δ¹⁵N‰ per GLORYS salinity unit** | **+0.8341458** |
| Cluster by **82 distinct GLORYS wet cells**, nominal 95% CI | **[+0.38863,+1.27967]** |
| Cluster by **13 original reporting regions**, small cluster t(12) 95% interval | **[−0.01594,+1.68424]** |
| Conditional SSE reduction / residual partial R² from M0→M1 | **+0.02880 (2.88%)** |
| Actual residual salinity variation after site and region×season FE (SD) | **0.2230** |
| Leave-one-reporting-region-out β range (13 checks) | **+0.5893 to +1.3833** |
| Leave-one-start-season-out β range (15 checks) | **+0.5877 to +0.9859** |

Note: conservative region t-groups CI is **not** an independent ecological p or proof of population effect; with only 13 and highly unequal contributing regions it includes zero. 100 repeated lab CV folds do **not** create 100 independent ecosystem replicates.

### Geographic support and sign variation: 8 regions with at least 3 sites/3 wet cells and 25 site-seasons

| Original source reporting region | Observed site-seasons | Sites / distinct wet cells | β salt within that region (site + season FE) | 82-cell-type cluster-robust interval *within region* |
| --- | ---: | ---: | ---: | --- |
| **Victoria Land** | 197 | 20 / 18 | **+1.616** | **[+0.925,+2.308]** |
| **Wilkes Land** | 146 | 17 / 15 | **+1.025** | **[+0.281,+1.769]** |
| **Southwest Antarctic Peninsula** | 78 | 8 / 8 | **−0.903** | **[−1.768,−0.039]** |
| **Northeast Antarctic Peninsula** | 147 | 13 / 12 | **+0.042** | **[−0.504,+0.588]** |
| Enderby Land | 44 | 5 / 4 | +0.077 | [−3.023,+3.177] |
| Mac. Robertson Land | 73 | 7 / 7 | +3.757 | [−0.346,+7.859] |
| Marie Byrd Land | 66 | 7 / 7 | +1.674 | [−1.138,+4.486] |
| Princess Elizabeth Land | 80 | 6 / 6 | +2.159 | [−0.172,+4.490] |

Remaining **5 named source regions** lack support (only one source site). 8 estimated local slopes are **post-result descriptive** tests; no correction for their multiplicity or out-of-region transfer tests has been completed. Especially SW Peninsula opposite slope needs independent source confirmation and cannot be called an established reversal mechanism.

Of the available site + original region×season-adjusted salinity sum-of-squares, **87.90%** comes from Victoria Land (35.20%), Northeast Antarctic Peninsula (32.20%) and Wilkes Land (20.50%). Thus the full-panel slope is geographically concentrated, and 13 nominal regions ≠ 13 equally informative physical contrasts.

### Transparent post-result robustness, without selecting a model based on outcome

- Reweight each site-season by **equal original pixel rather than equal date**: β=**+0.8473**, cell CI [0.3778,1.3168].
- Retain only original site-seasons with **at least 2 distinct dated image acquisitions** (n=603): β=**+1.1183**, 82-wetcell-type interval [0.5606,1.6761].
- Add original source image **log pixel count and log count of dated acquisitions** to M1: β=**+0.7186**.
- Remove site-specific linear temporal trends in addition to site and region×season FE: β=**+0.9117**.
- Include both image-support controls + site-specific trends: β=**+0.8199**.
- Reinterpret 12.5km shifted grid calculation **β=0.82580** as physical support sensitivity, not a replacement source or data replicate.

These improve neither original DI posterior validation nor causal identifiability. They are after-result diagnostics, so report ranges and uncertainty, not newly discovered independent p values.

## Why this is not yet a confirmed dietary ecology mechanism

1. **Isotope baseline vs prey guild**: δ¹⁵N also reflects regional particulate nitrogen and food-web isotope baseline, guano biochemical/optical properties, not solely krill/fish diet. Raw spectrum→δ¹⁵N calibration RMSE ≈1.7‰ for individual lab samples; inferred coefficient × one within-site/regyear salinity SD ≈0.186‰, much smaller. The paper's hierarchical uncertainty estimates missing; more accurate residual modeling and independent isotopic baseline controls required.
2. **Different marine spatial supports**: GLORYS salinity/temperature at the nearest original coastal wet point, SIC mean across 150km disk. Same season ≠ measured penguin foraging footprints; local access, freshening and krill fields not identifiable.
3. **Uneven temporal and geography**: 860 image site×seasons are repetitive historical records; 82 reanalysis wet-cell IDs and 13 *unequal* regions, not 860 independent evolutionary/ecological experiments.
4. **New hypothesis, old literature**: Youngflesh et al. 2026 already demonstrated sea-ice/diet and diet/long-term population associations. A conditional salinity slope on the same original satellite source may add secondary data insight, not an independent biological replication or a new ecology general law.
5. **No attribution**: water mass, glacial melt, primary producers, observer image spectral shift, temperature covariates, and genuine foraging choice remain competing explanations. No causal arrows, no SSP→isotope or SSP→penguin nest predictions should be drawn.

## Source and reproducibility (all same GitHub draft branch, not main)

- Original publisher ZIP and exact 119-site filter: [Actions #44078492773](https://github.com/zuizui0223/mina/actions/runs/44078492773), original proxy artifact **14326122826**.
- Original 892 Nov-Feb GLORYS: [Actions #44079373480](https://github.com/zuizui0223/mina/actions/runs/44079373480), artifact **14326721399**.
- Official real NSIDC V4 pixel-center calculation: [Actions #44081227652](https://github.com/zuizui0223/mina/actions/runs/44081227652), artifact **14327796404**. Earlier [#44080328594](https://github.com/zuizui0223/mina/actions/runs/44080328594) used 0..N-1 array indexes as geographic coordinates, produced all SIC missing, and is **invalid**. Wrong pixel-boundary-as-center [#44081369403](https://github.com/zuizui0223/mina/actions/runs/44081369403) is retained as **sensitivity only**.
- Corrected, source-guarded code: [\`rebuild_author_sic150_novfeb.py\`](rebuild_author_sic150_novfeb.py); model [\`fit_source_isotope_salinity_conditional.py\`](fit_source_isotope_salinity_conditional.py); verified raw isotope proxy [\`reconstruct_isotope_proxy.py\`](reconstruct_isotope_proxy.py).
- Full fixed-source GitHub Actions end-to-end [\`penguin-20261117-source-isotope-salinity-conditional.yml\`](../../../.github/workflows/penguin-20261117-source-isotope-salinity-conditional.yml). Locally independent consistency checks and ZIP freeze include output site×season and omit-year/region audits. Github Actions artifact retention is temporary, not DOI archival.
- **Freeze:** no overwrite or merge into main, no changes to v0.5 source data/figures or protected Ecology Report. This is a Draft PR #214 research lane, not a paper accepted or submitted.


## 最終再現監査（同日）

- Source-matched **full CI** [Actions #44083346932](https://github.com/zuizui0223/mina/actions/runs/44083346932) **SUCCESS**。オリジナルZenodo ZIP MD5、PLSR派生原103個校正標本、119サイト／179,346ピクセル／3,938元撮影日、元892厳格地理source、海氷150kmとGLORYS 4か月、860サイト×季／88地点／82wet格子／13地域を別ステップで再監査した。
- `fit_source_isotope_salinity_conditional.py` の **CIからの完全再計算β=+0.8341458422, residual partial R²=0.02880176895** は会話ローカルの独立同一source実装と小数点以下で一致。8地域の推定可能性と5地域のsource不足判定も一致。保存された派生source tables artifact **14328755565**。
- 画像サポートの事後感度では、同じ元入力で `log(1+pixel数)`・`log(1+撮影日数)` を加えるとβ=+0.7186、島・siteごとの線形時系列トレンドを加えるとβ=+0.9117。両方を追加してもβ=+0.8199。画像数・撮影季節の交絡を完全には排除しない。
- **適切な推定区間**：82 wet格子の区間[+0.3886,+1.2797]に対し、13元報告地域のsmall-group t(12) intervalは[−0.0159,+1.6842]。後者を欠いた「南極全域で有意」とする表現は禁止。
- 結論と原稿の境界：source-audited探索的δ¹⁵N optical proxy関連、海域別符号異質性の候補。元著者のStan DI posterior、餌種比率、個体数、独立海域への予測転写、真の因果/融水機構は未完了。Publication frozen main/figure変更無し。

**Final level:** exploratory positive isotope-proxy–salinity association, with substantial geographic heterogeneity and source-validity constraints. Before claiming genuinely new macroecological mechanism, obtain/independently reproduce published hierarchical \`DI\` posterior and isotope baseline or independently observed diet, and repeat fixed tests in independent marine provinces.
