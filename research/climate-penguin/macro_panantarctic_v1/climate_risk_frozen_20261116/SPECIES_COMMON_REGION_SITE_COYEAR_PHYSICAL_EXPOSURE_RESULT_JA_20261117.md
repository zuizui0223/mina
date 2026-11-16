# 同一地域・同一繁殖地で比較すると種別CMIP6海氷曝露差は残るか

2026-11-17 JST｜mina PR #214、元source matched-geometry supplementのみ。今回の「同じサイト」は同じMAPPPD原site IDであって、同じ調査日・同じ巣区画・個体の移動や将来生息適性ではない。

## 判定

**種別の大きい将来海氷曝露差を、そのまま種ごとの気候応答・生理耐性・未来巣数変化とは読めない。** ADPE–GEPEの元全計数site差−23.583 ppは同じ6報告地域を均等重みで比較すると+0.656 pp、同じ23 original site IDの比較では+0.312 pp（すべてGEPE−ADPE）。同じ年・同じknown source methodが2種ともある20 site IDだけでは−1.341 pp。これは元の地域地理／巣数の配分の違いに依存した**物理曝露集計**だという強い感度証拠。

ただし**すべての種差が同じサイトで消えるわけではない**。CHPE–GEPEの比較では共通29 siteでもGEPE−CHPE =−14.759 ppである。その同じ共通siteの中でも二種の巣数proxyがどこに集中するかが違うため、同じsite集合へ限定するだけでは別々のspecies nest-weighted meanは必ずしも同じ値にならない。このペアは50kmのモデル海洋格子支持域に制限すると差が−0.735 ppに変わるため、普遍的な種差とは扱えない。

## 先に固定された本来の分母

- 2011–2020の真正source：595既知site / 2,456 original source-count rows、現期間に観測がある271 site、331 site×species中央値。元方法固定の種別site数ADPE108、CHPE138、GEPE85。元source用量反応265系列とは異なる。
- 将来物理：元3 model（ACCESS-CM2, BCC-CSM2-MR, CESM2）＋3モデル等重み平均、2 SSP×2未来期間、過去1995–2014との差、8–11月のsiconc pp。各siteの物理Δは種ラベルと無関係で同一。
- 新規検証：3組の種ペア×4物理シナリオ×4モデル別/mean×2距離支持域×4地理集合 = **384 descriptive summary rows**。384件の独立な生物学的検定ではなく、固定元データと同じ海氷モデルの繰返し集計。
- 共通地域：各種がともに正の観測巣数proxyを持つ原報告regionだけ、各地域内は種の実数中央値で重み付け、その地域別値を**両種に同じ均等地域重み**で平均する。地域内では異なるsiteに重みを置けるので、完全な同所比較ではない。
- 同じ繁殖site：元2011–2020に両種記録のあるsite IDへ限定し、元各種別巣数中央値で物理Δを加重。種内の観測年は一致しないことがある。
- 真正同年同方法：元sourceで同一site×繁殖seasonに2種の巣数がともに記録されoriginal_survey_methodも同じ記録だけ残し、site別にそれらの年だけの種別中央値を作る。この条件は調査日・観測範囲・source引用の一致を保証しない。

## 主シナリオでの元3モデル等重み（SSP5-8.5, 2081–2100）

列は **B species−A species の2011–2020元巣数proxyで加重した未来海氷変化差**。単位 percentage points。符号は繁殖率ではない。

| ペア（B−A） | 各種別全計数site | 共通地域・地域均等重み | 共通site ID | 元同年同方法site |
|---|---:|---:|---:|---:|
| CHPE−ADPE | **−6.278** | **+0.610**（7 region） | **+5.785**（18 site） | **+6.563**（17 site / 28 site-year） |
| GEPE−ADPE | **−23.583** | **+0.656**（6 region） | **+0.312**（23 site） | **−1.341**（20 site / 36 site-year） |
| GEPE−CHPE | **−17.306** | **−1.462**（6 region） | **−14.759**（29 site） | **−17.391**（27 site / 74 site-year） |

同じsiteに同じ物理SICモデルを与えた場合、そのsiteのsite-equal物理曝露は2種で**定義上等しい**。共通site集合で残る巣数加重差は、2種の**その集合内の巣数proxy配分**の違い。種の適応・競争・移住の独立した物理的効果ではない。

## 現在の海洋モデル格子50kmの制約を追加

3モデルのsiconc+sosのwet-grid-center距離すべて≤50kmの元siteだけにすると、271→158計数siteになる。同じ主シナリオ：

| ペア（B−A） | 各種全対象site | 共通region均等 | 共通site | 同年同方法site |
|---|---:|---:|---:|---:|
| CHPE−ADPE | −5.220 | −0.302（6 region） | +10.570（10 site） | +11.481（9 site / 16 site-year） |
| GEPE−ADPE | −8.127 | +1.642（5 region） | +7.445（15 site） | +7.213（14 site / 23 site-year） |
| GEPE−CHPE | −2.907 | +0.622（5 region） | −0.735（16 site） | −1.129（15 site / 42 site-year） |

この50kmはモデル格子位置の支持域を揃える判定であって、ペンギンの採餌距離ではない。common-site/同年のrestricted supportは種ごとの真の巣数母集団を代表するとは限らない。具体的にfull23 ADPE/GEPE shared siteは元全species median proxyのADPE**12.365%**、GEPE**43.054%**。sameyear20 siteではそれぞれ**7.114% / 42.359%**。50km common15 siteへ狭めると**6.534% / 29.465%**。この重み喪失を隠して新しい生物学的有意差を主張しない。

## 生態学的意味と発表ゲート

1. 「ジェンツーの方が将来海氷の減少にさらされやすい」という全域平均は**種ごとの現在の巣数地理分布の記述**であり、生理・遺伝・実個体群動態の種差とは区別する。
2. ADPE/GEPEは比較する地域/siteを揃えると物理差がほぼ消失。CHPE/GEPEは同じsiteでも巣数分布の重み差が残るが、モデル格子の支持域によって大きく変わる。
3. これらは**地域・site・site-yearという観測階層の違い**から生じる。空間的な曝露分布と気候に対する時間的な繁殖応答を直接結ぶ係数は依然として無い。従来の未再現265 seriesのβ−0.55をSSPに掛けない。
4. 主論文の4図と生物学の主線（観測繁殖配置の南向き再加重、同出典の種別比、海洋物理の二軸）は維持。この解析は図の追加や新たな種別脆弱性見出しにせず、**補助資料／本文の短い境界説明**に限る。

## 再現

- Python source: source_match_species_shared_site_exposure.py
- 元の凍結MAPPPD原実数再構成: build.py
- 元のfull595 CMIP6 artifact: Actions #43845907301
- 再現CI： https://github.com/zuizui0223/mina/actions/runs/43901632512 SUCCESS、全384行と元site×season/method auditを原入力から再計算。距離条件後の同年同方法の**実際のsite-year分母**は元28→16（ADPE/CHPE）、36→23（ADPE/GEPE）、74→42（CHPE/GEPE）で、同じ原site×yearだけで重みを再計算した。訂正後の [Actions #43902145453](https://github.com/zuizui0223/mina/actions/runs/43902145453) も **SUCCESS**。
- Derived downloadable artifact: penguin-271-recorded-species-common-region-common-site-physical-sic、保持期限30日。恒久DOIなし。
