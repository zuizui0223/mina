# South Orkney region independent acoustic krill biomass × Signy penguin fledgling stage v1

> **SOURCE CORRECTION / SUPERSEDED — 2026-10-30:** このv1はIMR 2024報告Table2の年ラベルがSkaret et al. 2023原論文Table3と矛盾するため、**広域オキアミ量×雛生産の科学的結果として使用しない**。2013年の原論文南北統合値は欠測、2014〜2020年の値も元表と不整合。履歴と失敗原因の検査のため旧コード・CSV・CIを残す。訂正された元表と再検証は [v2 source reconciliation](../south_orkney_source_reconciliation_v2/REPORT_JA.md) を参照。旧v1のrやnは訂正済み値ではない。

2026-10-30. **Post-exposure exploratory analysis** in draft PR #206. Original acoustic biomass data are **previously published annual estimates**, transcribed from the Norwegian Institute of Marine Research, [2024 Antarctic krill survey report](https://www.hi.no/hi/nettrapporter/toktrapport-en-2024-14), **Table 2 / Overall stratum**, and are NOT newly measured by mina; raw acoustic data underlying [Skaret et al. 2023](https://doi.org/10.1093/icesjms/fsad076) are available upon reasonable request, not publicly downloaded here. The 10 annual records represent about 60,000 km² around the South Orkney Islands (Subarea 48.2) and not Signy nest-side krill density. Source units: density g/m², biomass million tonnes; survey CV dimensionless, acoustic 38/120 kHz per publisher table.

## Physical timing and reproducibility rule

- The regional acoustic survey is in **January–February calendar year S**, whereas Signy breeding season label **T** starts around October T, with BAS source fledgling stage dates in January–February **T+1**. Primary **preseason** is S=T, making surveyed biomass roughly 8–10 months before the breeding/fledgling event; the response may involve different prey distributions when chick rearing occurs. Secondary **concurrent austral summer** is S=T+1 (January–February during the chick season), and is **not a prior-year forecast**, since exact acoustic sampling days may coincide with or follow reported chick/fledgling-count days.
- Neither biomass versus fledgling correlation nor 2012 anomalous observation is a causal link. Survey area is too broad for local foraging access, and krill biomass is highly heterogeneous within its grid.
- 2013 and 2015 acoustic coverage was substantially restricted by sea ice. Both ALL and FULL-coverage-only results must be reported; 38 vs 120 kHz acoustic frequency, annual survey CV and vessel changes must not be ignored.
- Source-observed species-stage endpoints use the earlier native colony median for Adélie/chinstrap and island aggregate for gentoo. They are not strictly comparable island-wide chick survival. **Three species share one acoustic biomass value in each year, not independent environment replicates.**

## Calculated annual breeding-stage associations

Data-matched **nine** seasons 2011–2019 (9 independent survey-year opportunities, *not 27*); all nine BAS stage dates in early T+1 verified.

| Acoustic-to-breeding alignment | Years | Adélie Pearson r | Chinstrap r | Gentoo r |
|---|---:|---:|---:|---:|
| Preseason survey S=T | 9 | −0.212 | −0.559 | −0.546 |
| Preseason, exclude 2013/2015 incomplete acoustic surveys | 7 | −0.359 | −0.794 | −0.663 |
| Preseason, additionally omit **2012** high-acoustic/low-productivity influential observation | 6 | +0.044 | +0.011 | +0.214 |
| Concurrent Jan/Feb S=T+1 (not a prospective predictor) | 9 | +0.212 | +0.099 | +0.363 |

**The apparent negative association is unstable and highly dependent on 2012.** In full-coverage years, removing the 2012 survey erases all negative linear relationships. 2012 removal is **post hoc influence diagnosis**, not a valid method to favor positive effects. Source rank correlations are much weaker than absolute Pearson coefficients. The concurrent-window signs also differ, but precise survey vs chick-count timing has not been established; do not choose lag by preferred sign or treat concurrent as independent climate-forcing evidence.

### Scientific conclusion

An **external krill-acoustic survey layer is now genuinely connected** to BAS original penguin reproductive stages, but the regional biomass-to-productivity response is **not stable even in this nine-year time-cohort**. The existing 2050/2100 climate→breeding abundance and climate→breeding-space numerical forecast gate therefore remains **NO-GO**. This is a materially stronger falsification of direct food-proxy transfer than relying on stomach diet fractions alone; *not* evidence that food supply is ecologically irrelevant.

The best next independent test is to obtain original **fine-scale survey transect/NASC krill data** and actual penguin foraging/land route fields for each season, and replicate on one or more independent subregions with verified chronological stage outcomes. A single broad South Orkney density index cannot characterize Signy penguin feeding opportunities, salinity/stratification or vegetation feedback. Repeating regression variants in this n=9 dataset will not rescue identifiability.

## Source and reuse

- Original IMR report: https://www.hi.no/hi/nettrapporter/toktrapport-en-2024-14 (Table 2, overall stratum; publisher 2024).
- Annual 2011–2020 values retained with frequency, CV and coverage in \`inputs/imr_south_orkney_krill_2011_2020_2024_table2.csv\` (derived manual transcription of published estimates, NOT acoustic raw counts).
- Repeated original BAS publisher source ZIPs are checked by \`signy_trispecies_stage_source_v1.py\`, including the corrupt \`1998-8895\` Gentoo label quarantine and source sha pins.
- Reproducible overlap in \`work/climate_penguin/south_orkney_krill_fledgling_v1.py\` and \`outputs/imr_south_orkney_krill_v1/...\`; independent numeric receipt checked in source-only CI.
- Frozen Ecology PR #189, Paper2 PR #199, previous 216 environmental association comparisons and earlier time-forward count tests remain unchanged.
