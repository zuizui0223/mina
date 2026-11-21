# USAP-DC 602094 真正アデリー羽毛：bulk δ¹⁵NにはPheと栄養段階の両方が対応。ただしどちらが優位か未確定

**2026-11-21 JST | Draft PR #214 | 原著の108胸羽・45列を正式MD5で検証し、凍結した別問いをローカルPythonと別のstatsmodels計算で再現。** これは **独立なポリニヤ同位体回帰ではない**。凍結設計 [`FROZEN_AA_BULK_PHE_VS_TP_DIAGNOSTIC_20261121_JA.md`](FROZEN_AA_BULK_PHE_VS_TP_DIAGNOSTIC_20261121_JA.md) をcommit `32f17ad` に作成後、元の同位体値を測定系の比較に使用した。

## 主結論と保留判定

**一次判定：`NO_CLEAR_LOSO_BASELINE_VS_TP_PREDICTIVE_DOMINANCE`（Phe単独とTP単独の優位性は支持されない）。** 実測羽毛のbulk δ¹⁵Nは、源AAのphenylalanine δ¹⁵Nと著者のGlu-Phe派生trophic positionの双方を含むと予測しやすい。しかし両者の違いを「基線が主原因」／「食性が主原因」という排他的因果分解にはできない。

原データ [USAP-DC DOI 10.15784/602094](https://doi.org/10.15784/602094)（Michelson et al., 2026）。出版原CSV MD5 `f9a91c9d9bf3dba9607bf0767df8c206`、元CSV SHA256 `d9b24f994896130c6afed1c8359c9a8835f70b3cfb8bea40b54b3529f23b5cb9`、ユーザーアップロード元ZIP SHA256 `185dca693aa9cef96019e379308fa999d6985e010f9ddd9358e706c69ff9b1ce`。同じ標本で bulk d15N / Phe_d15N / Glu_d15N / Trophic_position が全部実測・算出可能な元個体 **65件**。同じ`Site×Year_collected`の10超過個体を平均して**55 Site-label×collection year、35原Siteラベル**を主単位とした。羽毛形成年は不明、Source `Site`の一部は島や海域の広域ラベル（厳密な35繁殖コロニーではない）、外部座標も標本ラベル・MAPPPD・Wikipedia等から由来し現地の採餌地点ではない。

## 固定した35 Site丸ごと除外予測

同一55 Site×採集年を4層（Antarctic Peninsula/Ross Sea × historical<=1995/modern>=2000）へ分け、層切片はどの予測モデルでも同じ。元`Site`の全採集年をLOSO一度に除外し、残りSiteで学習→除外Siteを予測。35SiteのMSEを各1票で平均してRMSE換算。**元のSiteを予測学習に流用せず、個体も独立55以上として水増ししていない。**

| 55 Site×年の同条件モデル | 35Site等重みLOSO RMSE（bulk δ15N, ‰） |
|---|---:|
| 4元地域×時代層の切片のみ | 0.88386 |
| + 源AA `Phe_d15N` のみ | 0.86945 |
| + 著者推定 `Trophic_position` のみ | 0.81621 |
| + 両指標同時 | **0.70357** |

一次凍結対比 `MSE(Phe alone) − MSE(TP alone)` は **+0.08974‰²**。原Site単位の**4,999回bootstrap**（seed 20261121）で、分位95%区間 **[−0.13145, +0.29753]‰²**。0を跨ぐため、Phe独自優位もTP独自優位も宣言しない。このbootstrapは「元35Siteで得たCV差を再標本化」したもので、新しい別採集時代や全南極の予測精度の保証ではない。Phe-onlyがTP-onlyより低誤差だったのは35Siteの**16 Site（45.7%）**。

両指標モデルがさらに低誤差なのは、同一個体に2種類の同位体に関連した情報があることと整合する。ただし`Trophic_position`は元々PheとGluの差から導出され、**Pheと独立した直接の餌割合や採餌行動測定ではない**。両指標が良いのは言い換えると`Phe`と`Glu`の両方の観測を使えるという測定モデルの性質を反映し得る。真の餌供給機構の二重の独立証拠として数えない。

## 二次：4層に共通のモデルと同じ採集Site内の感度

55地点年の4地域×時代グループ効果を差し引いた残差を基準とするモデル内説明率は、Pheのみ **9.45%**、TPのみ **15.97%**、**両指標 38.29%**。TPを既に入れたモデルへPheを加えた残差の減少率 **26.56%**、PheにTPを追加して **31.84%**。実測Pheと派生TPの群補正後の相関は**−0.342**で、独立な二つの因果説明変数ではない。

さらに事前固定した「同じSource Siteに2年以上の観測がある」集合は、**12 Sites・32 Site×採集年**。Site固定効果を完全に除いた同地点の年変化だけでは、Phe-only **2.50%**、TP-only **0.16%**、両指標 **6.29%**の残差内説明率に留まった。どれもrankは識別可能だが、小標本かつ非連続採集年・羽毛形成期不明。従って元55の38.29%から「同じ地点で基線と栄養段階の年変化がbulkを因果的に決める」と外挿できない。この弱さは**独立ポリニヤ年変動を検証できない**既存判定と整合する。

## 元サンプル構成の重大な制約

| 原広域×時代 | 4指標完全Site×年 | Source Site数 | bulk δ15N mean (‰) | Phe δ15N mean (‰) | TP mean |
|---|---:|---:|---:|---:|---:|
| Antarctic Peninsula, historical (1843–1995) | 23 | 17 | 9.959 | 4.509 | 2.805 |
| Antarctic Peninsula, modern (2006–2015) | 6 | 4 | 9.300 | 4.100 | 2.638 |
| Ross Sea, historical (1841–1975) | 21 | 14 | 10.334 | 3.944 | 2.886 |
| Ross Sea, modern (2000–2013) | 5 | 2 | 10.160 | 4.480 | 2.856 |

現代の完全な試料はわずか**11 Site×年・6元Site**しかない。大部分のhistorical試料が剥製標本、modernが捕獲/脱落羽根であり、**現代と歴史期にまたがる4指標完全SiteはCape CrozierとRoss Islandの2か所のみ**。採集年代と地域の共通支持は広くない。表の時代平均差は異なる採集地点・標本構成を含み、温暖化による栄養段階変化、歴史的オキアミ供給差、南極全体の傾向と**同義ではない**。

## 元のマクロ生態学上の問題へ何を追加できたか

1. **測定上は、bulk δ15NをそのままTP/魚食割合に読めないという一般的制約を別実測データで確認した。** これは元研究 [Michelson et al. 2026 *Trophic stability of Adélie penguins through major historical changes in krill abundance*, DOI 10.3354/meps15233](https://doi.org/10.3354/meps15233) の既存の問いにも含まれる。原著の結果を新規研究発見と主張しない。
2. **元のポリニヤ負の関連はまだ食性の証拠ではない。** Youngfleshの旧439 site×seasonにおけるwinter100km polynya +10pp→光学δ15N −0.94‰という事後的な負の関連と、直前冬対翌冬の差は、原著R1000較正・同一歴史画素に安定していた。しかしそれは同じ古い糞画像から算出した光学Yであり、**羽毛のbulk/Phe/TPを同じ年・同じ採餌域で結合できていない**。
3. **独立生態学的再現としてはNo-Go維持。** 元USAP602094の2004–10/2013–16で4指標完全なsite×**collection** yearは9、5 site/2 regions、真のfeather-molt yearなし。凍結した独立site×本当の羽毛形成年>=20、3地域以上等の支持ゲートに届かない。原データを入手したからといって、元のポリニヤ仮説のconfirmatory evidenceへ昇格させていない。
4. **結果の論文配置**：もし引用するなら「食性と基線を混同しないための別測定に基づく根拠」として付録や議論へ。主要図や因果モデルを拡張しない。元の南極ペンギンの温暖化・海氷・繁殖空間という論文主線は維持。

## 実行・再現性

- 原ソース：[USAP-DC USAP602094](https://www.usap-dc.org/view/dataset/602094)、**CC BY 4.0**。正式元CSVのMD5・SHA・ZIP CRC照合。
- [GitHub凍結仕様](FROZEN_AA_BULK_PHE_VS_TP_DIAGNOSTIC_20261121_JA.md)、[Python固定解析コード](fit_frozen_bulk_d15N_vs_source_Phe_vs_derived_TP_LOSO_sites_20261121.py)。原生の108標本CSVはリポに再配布しない。ユーザーの元ZIPを指定して実行する。
- ユーザーが提供した原ZIPを **2026-11-21 JSTにローカルPythonで解析**し、55 source site-yearのnull/Phe/TP/bothモデルのSite単位の再現MSE CSV、グループ平均CSV、主要係数JSONを保存。別の`statsmodels.formula.api.ols`による同じ固定効果・SSEの独立実装で原SSEを再計算し、全値が一致。**現時点でこの追加測定診断をGitHub Actionsで実行したとは主張しない**（原8kBユーザーアップロードZIPはGitHubリポに公開/再配布していない）。
- 原元DATAのMD5チェックは本レポートとローカル成果物のsource checksumへ記載。全てDraft PR #214追加のみ、`main`/v0.5/v0.6/Ecology Report/Paper2に変更なし。
