# PR #214 description immediately before v0.7.5 Mertz external iceberg test

Captured on 2026-11-22; the previous Draft PR author-review text is retained verbatim below.

## 現行 v0.7.4：地点間の符号反転検証は不支持（2026-11-22）

**結果:** 元の439地点×季節を85地点の年平均に集約し、計算前に判定を固定した地点間 vs 地点内の比較を行いました。元の地点内M_Pは**−1.003‰/10pp（CV3 [−1.675, −0.331]）**。地点間の単純傾き**−0.319**、地域調整**−0.795**、地域・夏の環境・緯度・観測年調整**−1.295‰/10pp（8情報地域CV3 [−4.965,+2.376]）**で、**地点間が正、地点内が負という符号反転は確認できません**。著者1,000回較正平均、3年以上観測した82地点、地域×年標準化でも地点間の点推定は負でした。ただしWilkes Landを除くと係数+0.16に反転し、地点間の結果は不確かです。

これは**同じ衛星proxyの事後補助診断で、Reavesらの雛骨との独立・同一推定対象の比較ではありません**。魚からオキアミへの食性転換、空間的な正の効果、因果的なポリニヤ機構は追加主張しません。主結果・CV3区間・5図は保持しました。負の結果を隠さず本文Results 3.5・Discussion 4.2とSupplement S4へ反映しました。

[凍結した事前判定](https://github.com/zuizui0223/mina/blob/d82e0b0f8d30d5a82618a158231fd67a7a62f728/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/FROZEN_SCALE_BETWEEN_WITHIN_COLONY_TEST_20261122_JA.md) / [NO-GO結果と解釈](https://github.com/zuizui0223/mina/blob/d82e0b0f8d30d5a82618a158231fd67a7a62f728/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/RESULT_BETWEEN_WITHIN_POLYNYA_NO_GO_20261122_JA.md) / [計算コード](https://github.com/zuizui0223/mina/blob/d82e0b0f8d30d5a82618a158231fd67a7a62f728/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/test_between_within_source439_20261122.py) / [GitHub Actions再計算SUCCESS](https://github.com/zuizui0223/mina/actions/runs/45011139260)。

**v0.7.4の著者レビューWord:** 本文23頁 / 1.72 MB、補足10頁、元の5図（変更なし）、要旨222語。初回投稿用Wordの5 MB基準内。著者の科学的承認・著者情報・申告・公開とライセンス方針は未完了。投稿・merge・DOI発行は行っていません。

---
### 以前のv0.7.3の記録（履歴）

## Current single manuscript: v0.7.3 (author-review Draft)

**Winter coastal-polynya area is associated with annual variation in Adélie penguin optical isotope proxies**

The same 439 colony-seasons, 85 sites and 11 nominal reporting regions are retained; after colony and region-season effects, 425 records / 82 sites / eight unevenly informative regions identify the principal coefficient. This reanalysis of Youngflesh et al. (2026) optical isotope proxy observations is **exploratory and not independent diet confirmation**. The negative direction contradicted the earlier positive hypothesis.

### Numerical results, unchanged from v0.7.1

| Original comparison | Estimate (‰ per 10 percentage points) | Eight-informative-region CV3+t(7) 95% interval |
|---|---:|---|
| Prior winter polynya, M_P | **−1.003** | **[−1.675, −0.331]** |
| With summer salinity, M_SP | **−0.922** | **[−1.515, −0.328]** |
| Preceding winter minus following winter (same 358) | −0.688 | **[−1.470, +0.095]** |

The temporal difference is uncertain, not statistically resolved. Forward prediction did not improve, and 2013–2021 measurement recovery failed its prior acceptance gate. Salinity in the same 439 rows was +0.646‰ per salinity unit (CV3 [−0.196,+1.488]); the 860-record result is a separate panel. No causal diet switching, same-winter ice-extent-controlled geometry mechanism, or future penguin diet projection is claimed.

### New v0.7.3 reviewer issue resolved: the true scale of identifying exposure

The originally reported **−1.003‰ per 10pp** remains mathematically correct, but the winter-polynya exposure SD after all M0 covariates and fixed effects is **1.601pp**, not its raw 6.311pp SD. The original slope therefore corresponds to only **−0.161‰ per one conditional exposure SD**; M_SP corresponds to **−0.146‰ per its 1.588pp residual SD**. A 10pp increment is about 6.25 conditional SDs and should not be depicted as a routine within-colony annual change or intervention. This is an algebraic scale description of the *same already-selected observational coefficient*, not a new hypothesis test, new p value, or replication.

- [Main manuscript and 222-word abstract](https://github.com/zuizui0223/mina/blob/analysis/penguin-decade-redistribution-v1-20261110/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/MANUSCRIPT_POLYNYA_FOODWEB_WORKING.md)
- [Supplement S2 and unchanged CV3 tables](https://github.com/zuizui0223/mina/blob/analysis/penguin-decade-redistribution-v1-20261110/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/SUPPLEMENT_POLYNYA_FOODWEB.md)
- [Source-locked scale audit script](https://github.com/zuizui0223/mina/blob/analysis/penguin-decade-redistribution-v1-20261110/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/audit_polynya_estimand_scale_20261122.py) · [numeric receipt](https://github.com/zuizui0223/mina/blob/analysis/penguin-decade-redistribution-v1-20261110/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/source_inputs/polynya_estimand_scale_audit_20261122.json) · [GitHub Actions success](https://github.com/zuizui0223/mina/actions/runs/45009422843)
- [Reviewer-facing scientific risk note](https://github.com/zuizui0223/mina/blob/analysis/penguin-decade-redistribution-v1-20261110/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/SCIENTIFIC_REVIEW_ESTIMAND_SCALE_V073_JA.md)
- [Reproduction scope and commands](https://github.com/zuizui0223/mina/blob/analysis/penguin-decade-redistribution-v1-20261110/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/README.md) · [MEPS author requirements](https://github.com/zuizui0223/mina/blob/analysis/penguin-decade-redistribution-v1-20261110/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/submission_preparation/MEPS_REQUIREMENTS.md) · [author input](https://github.com/zuizui0223/mina/blob/analysis/penguin-decade-redistribution-v1-20261110/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/submission_preparation/AUTHOR_INFORMATION.md)

### Manuscript deliverables and execution boundary

The v0.7.3 combined main Word is **22 pages / 1,719,285 bytes / 4,803 visible words**, with five original figures and a 222-word abstract. The supplemental Word is **8 pages / 48,972 bytes**, enlarged by one scale-and-support table. Other 4 review Word documents cover five figure, two alt-text, one cover-letter and two author-information pages (40 pages overall). [Build receipt](https://github.com/zuizui0223/mina/blob/analysis/penguin-decade-redistribution-v1-20261110/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/document_build_receipt.json) and [scope-limited visual QA](https://github.com/zuizui0223/mina/blob/analysis/penguin-decade-redistribution-v1-20261110/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/document_visual_qa_v073.json) document the revised files. The fresh extracted reproducibility package also passed the prior frozen-result 58 checks and the new descriptive source-scale check; no changed ecological model is claimed.

**STOP CONDITIONS:** This PR remains Draft and unmerged. Human scientific review, author names/order/affiliations and contribution statements, funding/conflicts/ethics, accurate generative-assistance declaration, permission and terms for a final public archive, project code licence and DOI remain author decisions. No publication, archive DOI, blanket licence or submission has occurred.

Previous v0.7.2 PR description: [preserved history](https://github.com/zuizui0223/mina/blob/analysis/penguin-decade-redistribution-v1-20261110/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/history/PR214_DESCRIPTION_BEFORE_V073.md). Earlier v0.6 remains historical, with nest-weighted exposure only as supplementary context.

