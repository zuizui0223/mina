# 南極の海洋「2軸」の新たな違い：地理的には海氷・水温が共通、時間的には塩分の地域同期が強い

**2026-11-12 JST｜mina Draft PR #214｜探索的・source-verification済み、因果/温暖化帰属の検証ではない**

## 一文の新結果

南極の既知ペンギン繁殖地588地点・18報告地域に対応する1993–2020年28年間の元海氷衛星データと海洋再解析データで、**海氷・水温が地理的な主要環境勾配（物理PC1）を形成したのに対し、主に塩分を表す別の海洋環境勾配（物理PC2）の年変動は18地域間でより強く同期していた**。場所ごとの気候を1つの「亜南極化」指数に縮約できないだけでなく、**どの物理軸が地理的な違いを作るか**と**どの軸が同じ年に地域を越えて揺らぐか**が異なる。

これはペンギン生態の機構ではなく、実際の繁殖地周辺における**物理環境のマクロ地理・年次変動**。前回の全18地域PCA（物理PC1=60.365%・PC2=33.377%）と、351実測同所同年2種巣数比較の弱い転写可能性に追加する単一論文内の結果である。

## 真正ソースと最小QA

- EUMETSAT OSI SAF OSI-450a1 v3.1, 元1991–2020年8–11月の595地点×120月=71,400元SIC海域100km平均；Copernicus GLORYS12V1 202311, 元1993–2020年8–11月588地点×112月=65,856元塩分/水温。海洋は378固有GLORYS wet-grid海域セル、18報告地域。
- 元588地点×28年=**16,464 source-complete site-year**。この3変数を既存の物理PCAと**全数一致**で再構成（各site×yearのPC1最大数値差 1.78×10⁻¹⁵）。再解析と元海氷の出典を新規選別していない。
- 元の18地域×28年=**504地域年**に対して、既存ソースのPC1・海氷・塩分・水温の年間平均と地点数・海洋セル数を再計算し数値一致。source-yearや地域を勝手に増やしていない。
- サイト等重み地域平均に加えて、**各地域×年の同じGLORYS海洋セルに対応する複数繁殖地は先に平均して、1セル1票に直した平均**を計算。378海洋セルは各原報告地域内に属し、同じセルが**異なる報告地域間で重複する例は0**（出典の元格子で確認）。
- 18地域全体の結果と、元site>=3・固定250kmブロック>=2・GLORYS格子>=2で原観測支持がある**13地域**の結果を同じ実年で比較。
- 最初の地域PC1中期ピーク**13/18、10/13**（2001–2010年平均が1993–2000年/2011–2020年の双方を上回る）を復元。**GLORYS格子セル等重みへ変更しても18地域の中期ピーク判定の変化は0地域**。ただし平均水準の順位の頑健性であって、原因・温暖化の単調な方向の検定ではない。

## 元の空間PCAから、地域間の年次「同期」へ

元PCAは588サイト×28年の3変数の変動に対して、PC1の説明率**60.365%**（SIC −0.70734、水温 +0.70583、塩分 −0.03835）、PC2 **33.377%**（塩分 +0.99772）。この説明率と、下表の「共通年次変動率」は**分母が全く違う**。

地域同士の年次同期の計算では、PC1とPC2それぞれについて、**各地域の28年平均を引いて、その地域の28年SDで標準化**した28年×18地域の年次行列を作った。
- *同方向の共通年次成分率* = 18地域の各年平均の平方和×地域数 / 地域標準化異常値の平方和。地域ごとの年間増減が一緒の方向なら高く、半数の地域が逆なら相殺される。
- *時間的EOF1の説明率* = 28年×地域の年次標準化行列における第1特異成分の平方和比率。これは正負反対に動く地域もまとめうるため、**必ず固有ベクトルの符号も報告**。
- *地域間の相関中央値* = 18地域の原annual standardized anomaliesから地域ペア153個のPearsonを求めた中央値。地域ペア153は独立153実験ではない。

### 空間環境軸とは違い、塩分軸が時間的に強く共通

| source temporal descriptor | PC1 氷–水温 | PC2 塩分 |
|---|---:|---:|
| 全18地域の元region-PC1/PC2年変動の地域ペア相関中央値 | **+0.1514** | **+0.4855** |
| 同方向の地域共通年次成分率 | **19.71%** | **52.14%** |
| 時間EOF1の元標準化変動説明率 | **28.77%** | **53.50%** |
| 第1時間EOFの負荷量符号 | 17正 / 1負 | **18正 / 0負** |
| 13のsource-multiblock地域だけの同方向の共通年次成分 | **17.80%** | **58.74%** |
| 同じGLORYS海洋セルに複数siteの重複を除いた18地域の共通成分 | **19.60%** | **52.29%** |
| 元13 source地域×海洋セル等重みの共通成分 | **17.72%** | **58.97%** |

この統計により、「塩分が各地域で同じ方向へ28年間増加した」とは言えない。**平均的な海洋環境値・長期の物理傾向は異なっても、増減する年の相対的なタイミングが共通する**ことが示される。SIC–塩分が全site yearで相関0.054でも、塩分PC2の地域をまたいだ同年の増減は強く整列する。

元全18地域でのPC1/PC2「地域の共通年次平均」どうしの相関は**−0.187**（海洋セル等重みでは−0.172）。両物理PCの元全site-year内積がPCAにより0になることと、地域年の共通モードが完全に独立することは別問題である。

## post-result sensitivity：同じ28年の傾向そのものを除いても残る？

**最初の結果を見た後**、「全地域が同じ塩分長期増加傾向だから年次同期が高いだけでは？」という疑問の診断を追加した。従って以下は後出しの感度解析であり、前述の元同期値を置き換えたり、仮説の事前登録と偽ったりしない。各地域×各物理軸で28年線形OLS傾きを除き、その残差を地域内SDで再標準化した**元region time anomaly**を同じ方法で比較した。

| geographic cohort / year signal | PC1 (thermal ice) | PC2 (salinity) |
|---|---:|---:|
| 18 source regions, mean centered only | 19.71% | 52.14% |
| **18 regions, each region OLS linear trend removed** | **19.84%** | **50.61%** |
| 13 source multi-site/multi-block regions, OLS linear trend removed | 17.64% | **55.85%** |
| 18 regions, each original wet GLORYS cell one vote, OLS trend removed | 19.74% | **50.72%** |
| 13 source regions with wet cell one vote, OLS trend removed | 17.59% | **55.99%** |

同期の高低差は、**地域をまたいだ一様な直線的な塩分トレンドを差し引いても**維持。18全域のトレンド除去後の元地域ペア相関中央値はPC1 +0.154、PC2 **+0.456**、13 source region条件ではPC1 +0.120、PC2 **+0.501**。

同じデータで、28年の各地域を1～27年ランダムな位相だけ循環シフトして1,000回のsource参照分布を生成（固定種20261112）。元18地域トレンド除去後の共通年成分率はPC1 **0.1984**（参照2.5–97.5%は約0.0294–0.0923）、PC2 **0.5061**（参照約0.0265–0.0976）。**この1000回で同じ値以上は0回**だったが、これは*正式なp値ではない*。各海域の実際の年次自己相関・気候テレコネクション・GLORYS同化に由来する空間共有誤差を独立に表す検定ではないため、「気候因子を証明した」とは扱わない。

**核心的な不確実性：** 2011年前後のGLORYS再解析同化の変更、衛星・観測系列の製品切り替え、広域的なモデルsalinityバイアス変動でも同時年変動は強まる。今回のsource再計算はOSISAFの原本とGLORYSオリジナル数値の再現を保証するが、元塩分の複数地域での*現場独立測定*の一致を証明しない。次に必要なのは「同期塩分年変動」を南極全域の独立したArgo / CTD現場観測と比較すること。

## 論文にどう統合するか

**採用できる中核**：沿岸の元繁殖地に対応する海洋環境には異なる空間的な次元があり、**それらが時間的に共有する共変動の強さは逆転する**。海氷/水温PC1は場所の差をよく表すが、塩分PC2は地域をまたいだ同時年次変動をより大きく共有する。この物理的時間構造と繁殖カウントから種の比率への生物学的転写は別に検証しなければならない。

**同じ論文内の生物的境界**：本研究で本当に同じsource-site/yearに計数されたペンギン3種ペアは351記録だが、反復可能な地域支持は狭く、元海洋物理PC1/PC2との地点内比率は一般化しない。ヒゲ/ジェンツーの探索的な塩分PC2係数は暦年＋site FEでも−0.176、sourceゼロ除去で−0.083だが、Central-west Peninsula除外で+0.072へ反転し、source年FE後R²は0.48%だけ。**物理的な塩分年次の共通性は、「塩分がペンギン群集を共通に動かす」証拠とは正反対に区別すべき**。

**統合しない**：元2017–2023陸植生/地衣類/藻類の静的ポリゴン面積を28年にコピーして植生変化や緑化の同期を創作すること、CMIP6からペンギン繁殖数を外挿すること、元の595既知繁殖地を全海岸の占有/未占有に変換すること。旧34-site GLORYSだけでは地理的な限定軸が見えたが、本18地域結果をもって機構としての「亜南極化」を一般化することも避ける。

## Source files / numerical execution

- **[Original full-run 18-region physical synchrony and 1000 offset references — GitHub Actions SUCCESS #43049546362](https://github.com/zuizui0223/mina/actions/runs/43049546362)**, artifact **13869360730**, source-verified 504 site-equal vs unique-wet-cell region-year PC1/PC2 records, original 18 region fixed 3-era peak classification audit, all original/source-supported region phase analyses and post-result detrending.
- Code: analyze_original_18region_marine_time_synchrony.py, independent six physical/regional arithmetic synthetic source tests: unit_test_18region_marine_time_synchrony.py, workflow .github/workflows/penguin-original-18region-marine-synchrony-phase.yml.
- Contract: REGIONAL_MARINE_SYNCHRONY_CONTRACT_20261112.md (post-result OLS-detrending section explicitly appended after initial synchronized salinity source result).
- Earlier full 588-site source: [#42961084667](https://github.com/zuizui0223/mina/actions/runs/42961084667) artifact 13829236358. This source itself comes from verified 595 colony OSISAF v3.1 satellite month data [#42612067836](https://github.com/zuizui0223/mina/actions/runs/42612067836) and original GLORYS12V1 monthly 1993–2020 ocean data [#42958013800](https://github.com/zuizui0223/mina/actions/runs/42958013800).
- No new penguin count or salinity field/threshold selected in this result. All changes confined to Draft PR #214; main, frozen Paper1/Paper2, warming v0.6, original climate PR #206 and exploratory bright/dark PR #215 are unchanged.
