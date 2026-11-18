# 南極595既知繁殖地の将来海氷減少×海洋低塩分化：実計数巣数と実δ¹⁵N観測地点を同じ地図で比較

**2026-11-18 JST | mina Draft PR #214 原本固定の新規マクロ物理解析。** 既存main、投稿/凍結済みEcology Report/Paper2、v0.5生物学本文/4図は未変更。主対象は「気候の**物理的な多次元曝露**」であり、巣数・魚/オキアミ比・δ¹⁵Nの未来予測**ではない**。

## 1. 中心結論：温暖化の海洋変化は海氷減少だけではない

元sourceの3 CMIP6モデル（ACCESS-CM2 / BCC-CSM2-MR / CESM2；各1member）のhistorical **1995–2014** に対する、SSP2-4.5/SSP5-8.5 × 2041–2060/2081–2100、**8〜11月**の変化を、全595既知MAPPPD地点の原モデル格子で直接計算。原27 Zarrストアを2026-11-16にsource固定で取得した結果から `siconc`（海氷濃度pp）、`sos`（CMIP6海面塩分、native単位 **0.001**）、`tas`（**大気気温℃**、海水温ではない）を再結合した。

SSP5-8.5／2081–2100：

| 指標 | 595 site等重み | 2011–2020年に本当に巣数計測がある271 site、source nest median weight |
|---|---:|---:|
| 海氷濃度 `siconc` change | **−21.441952 pp** | **−13.276241 pp** |
| 海面塩分 `sos` change | **−0.251640 (model native 0.001)** | **−0.257250** |
| 2m付近大気温 `tas` change | +3.8106 ℃ | +3.7409 ℃ |

595地点では**3モデル平均**のsos未来差が**595/595 siteで負**。しかし3モデル各々が負なのは **464/595 (78.0%)**。海氷減少も3モデルで一致する条件と同時に要求すると **384/595 (64.5%)** へ減る。**モデル平均でのすべての塩分低下と、個々のモデルでの符号一致を混同しない。**

元source真正2011–2020年の調査巣数がある271site／331 site×species中央値／合計**2,848,329.5 source median nests proxy**（単一年度個体群総数ではない）では、
- 3モデル全てが塩分低下 **179/271 sites (66.1%)**、そのsiteがsource巣数proxy総和の**93.5425%**を担う。
- 同じ3モデル全てが**海氷減少も塩分低下も**支持するのは**152/271 sites (56.1%)**、source巣数proxy重みの**59.0808%**。
- 源海洋モデル格子の`siconc`と`sos`を3モデル全部**50km以内**に制限すると158 site／source巣数重みの80.2099%。その中では3モデル塩分低下一致 **127/158、巣数proxy重み94.0509%**、二変数同時減少一致 **106/158、巣数proxy重み53.4517%**。

これは生物種の実際の危険度や発生確率ではなく、**同一シナリオ下で選択した3モデルが共通に予測する気候物理方向と、現在実計数がある巣数の地理的重なり**。『巣数の59.1%が将来減少する』との読みは誤り。

## 2. シナリオ・時期で3モデルの一致は大幅に異なる

下表は271 siteの実計数種別中央値固定重みを分母とし、どのsiteで3モデルとも負かという**方向の一致**を重みで再集計した。

| source-model future vs historical | nest-weight mean ΔSIC pp | nest-weight mean Δsos native | 塩分低下が3モデル全一致するsiteの固定巣数proxy重み | 海氷減少・塩分低下の両方一致するsiteの固定巣数proxy重み |
|---|---:|---:|---:|---:|
| SSP2-4.5／2041–2060 | −6.5602 | −0.0353 | 29.93% | 19.64% |
| SSP2-4.5／2081–2100 | −7.5969 | −0.1540 | 53.10% | 17.52% |
| SSP5-8.5／2041–2060 | −7.3346 | −0.0603 | 54.74% | 17.92% |
| **SSP5-8.5／2081–2100** | **−13.2762** | **−0.2572** | **93.54%** | **59.08%** |

特にSSP2-4.5世紀末の3-model-mean `sos` は全595で負でも、BCC-CSM2-MRでは271のうち227siteで塩分増加を示し、ACCESS-CM2とCESM2の低下がmeanを負にする。同じSSP5-8.5世紀末の271巣数proxy重み平均sosは、ACCESS **−0.31607**、BCC **−0.02942**、CESM2 **−0.42627**（すべてモデル物理量）。選択した3モデルだけでも海面塩分変化の絶対値と局所符号の不確実性は大きい。

全271siteのsos／siconc未来変化は3モデル分、2シナリオ・2年代の**同じ原site ID**で一対一に対応。元モデル海洋格子を同じサイトに複数割当てたからといって595の独立気候実験があるわけではない。

## 3. 地域・種の地理と物理曝露が重なる割合

SSP5-8.5世紀末、3モデルで「両方負」と合意するsiteが元調査巣数proxyのどこに多いか：

| original source region | 真正計数site | 271全巣数proxy中の固定重み | その地域内の両方負3model一致の巣数proxy重み |
|---|---:|---:|---:|
| Victoria Land | 32 | 49.46% | **35.1%** |
| Northeast Antarctic Peninsula | 27 | 20.60% | **100.0%** |
| South Shetland Islands | 59 | 14.23% | **68.5%** |
| Central-west Antarctic Peninsula | 73 | 2.22% | 16.1% |

種別で元2011–2020年site×species巣数中央値を使用したとき、ADPE 108siteはsos −0.2826、海氷−11.256pp、両方3モデル一致するsiteの巣数proxy55.3%。CHPE 138siteはsos −0.1515、海氷−17.534pp、両方74.8%。GEPE 85siteはsos −0.2618、海氷−34.839pp、両方59.1%。**これら種別の違いは巣数proxyが現時点でどの地点・地域に重いかを反映し、生理的な塩分耐性や、将来の個体数増減ではない。**

## 4. 「塩分×δ¹⁵Nの肯定結果」へ、物理的な将来シナリオを直接対応

Youngflesh 2026 original Zenodoの真のLandsat画像から再構成したδ¹⁵N proxyは、**860 site×season／88 site／13 source regions**で、元11〜翌2月のNSIDC V4 SIC/GLORYS近岸thetao/塩分、site/region×season/画像日調整後、塩分係数**+0.8341458422‰ per salinity unit**、partial residual R²=**2.88018%**。これは明確な**探索的な正の条件付き関係**であり、因果機構が確定しなかったことを理由に取り下げない。

その実際の88site IDを595 model siteに結合すると、**88/88が4物理シナリオの原site支持を持つ**。SSP5-8.5世紀末では、
- 元88siteのmodelmean海面塩分の未来差 **−0.327722**、海氷Δ **−14.064pp**、3モデル平均塩分低下 **88/88**。
- **3モデル塩分低下一致80/88**、海氷減少との**両方一致43/88**。
- 原モデル海洋格子3モデルで50km以内を全て通るのは**46/88**、その中で塩分低下40/46、両方17/46。

**解釈の境界は厳格:** 元のδ¹⁵N現地sourceは11〜翌2月 (1996–2012年) のGLORYS近岸格子・150km NSIDC。未来CMIP6は8–11月 (2041–2100) の**別の粗い物理モデル格子と海面塩分**で、温度もGLORYS海水温`thetao`に対しCMIP6では**大気`tas`**。元のδ¹⁵N係数+0.834を将来Δsos−0.328に掛けて「将来δ¹⁵Nが−0.274‰」と予測するのは、時期・変数・測定・空間支持も因果/地域転写も合致せず**禁止**。既存の温度/海氷/塩分3成分の観測PCAを`tas`で未来外挿することも禁止。

## 5. 先行研究との差：『南極は初めて低塩分化する』という発見ではない

南大洋の塩分変化と海氷の連動、将来温暖化での低塩分化と混合・成層への影響は既知。Silvano et al. (2025) *PNAS* DOI [10.1073/pnas.2500440122](https://doi.org/10.1073/pnas.2500440122) は**2015年以降に南大洋表層塩分がむしろ上昇した衛星観測**を報告している。これは今回の将来長期3-model mean低塩分化と時間尺度・地理・観測対象が違い、直接矛盾・逆転年を推定したわけではない。海洋淡水のペンギン生態への異なる可能な影響は2026年の総説（DOI [10.1016/j.avrs.2026.100386](https://doi.org/10.1016/j.avrs.2026.100386)）ですでに論じられている。

**今回のオリジナルな実施結果**：595既知siteの完全再抽出済みCMIP6 **sos＋siconc＋tas** を、同じ271真正実巣数重み／species／元地域／海洋格子50km品質と結合し、**モデル平均と3モデル全一致を区別して**多変数の現実的な物理曝露を示したこと。さらに塩分との観測関連が実際に検出された88 original isotope sitesへ新たに対応し、**生物因果外挿をせず物理的な支持域を測定**したこと。

## 6. 再現・現状

- 原CMIP6 27 Zarr storeの全595変数×モデル×未来の元ソース： [Actions #43845907301 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/43845907301)、artifact **14214704362**（20年×各期間、3 models、siconc/sos/tas、元store/catalog/model/member固定）。
- Original MAPPPD実巣数2456/595 source: [Actions #42610664607](https://github.com/zuizui0223/mina/actions/runs/42610664607)、artifact **13669533413**。
- **新しいjoint source script：** [audit_CMIP6_joint_ice_freshening_595.py](audit_CMIP6_joint_ice_freshening_595.py)。[新CI #44238218203 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44238218203)、artifact **14398755921**。CMIP6元ZIP SHA256 `c91e3a1126bdb9af2345fe08bcb201b3c21e802cbd2fcfe21db99faa2163c4d0`、元2456 ZIP SHA256 `add9f2a4c9a82279a70b4e9edb4156f5dc9d21fbe55122276e5199a02487f38a`、元21,420のsite×model change と7,140 ensemble site meanを独立再構成、モデル符号の一致を数えた。元595×4scenario CSV、271×3model×4scenario、16region×4scenario、3 species×4scenario、JSON source receiptを保存。
- **δ¹⁵Nを観測した88 source地点の追加物理対応：** [audit_CMIP6_88_isotope_source_exposure.py](audit_CMIP6_88_isotope_source_exposure.py)、[CI #44238693569 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44238693569)、artifact **14397982914**。元 isotope860 original source artifact **14328755565**、元delta595 joint artifact **14398755921** から同一site IDを正確に対応。88site×4scenario出力、13region source-support表と機械可読No Biological Extrapolation receiptを保持。
- 本件は**主論文v0.6 candidateのphysical-climate extensionとして補助Results／図案に組み込み候補**。元v0.5・図4枚・既存mainを変更しない。3モデルの不確実性、GCM格子の疎さ、調査済みsite選択、空間構造を全て記載し、強い未来生物予測・種の保護区適性等は不主張。

**一文の結論：海氷後退だけでなく沿岸海面塩分の低下も3-model futureで広範囲に予測されるが、両方が同時に一致する既知繁殖地と現在の巣数proxyの範囲は局所地理とモデル選択に依存し、海洋物理曝露から食性や将来巣数へ飛躍できない。**
