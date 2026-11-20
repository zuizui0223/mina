# 実測沿岸ポリニヤはδ¹⁵N光学proxyと正ではなく負に関連：事前の正方向仮説は不支持、時間外予測改善なし

**2026-11-20追加探索：[直前冬対翌冬の時間特異性とクロロフィル経路](../polynya_temporal_20261120/RESULT_JA.md)。** 同じ原データの共通358地点季節で直前冬の負関連が翌冬より強く、8情報地域による感度区間でも差は−0.6877‰/10ポイント [−1.3461, −0.0293]。一方、海色が全4か月揃う112行は海氷の少ない条件に偏り、クロロフィルを加える前から元の負関連を再現せず、生産系経路は未確立。これは本稿の元の正方向仮説の不支持や時間外予測改善なしという判定を変更しない。

**2026-11-19 JST | Draft PR #214 only | 同一439観測で元GitHub成果物をローカル独立計算。GitHub Actions #44547277067 **SUCCESS**、同じ元ソースで独立ローカル計算と係数・予測RMSE・CIが数値一致。結果artifact **14539734362**、digest **sha256:e413eab31b101c4a9a11c6dc7656d58906527a2146e6ccef442bb677ede6b233**。main・凍結原稿は未変更。**

## 元データが本当に重なった（Yを開く前の段階）

- 生態応答：Youngflesh 2026原Landsat反射率から自前再構成したδ¹⁵N光学proxy（**測定された魚食割合ではない**）。GitHub Actions artifact **14328755565**、ZIP SHA256 `dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205`。
- 物理曝露：Lin et al. 2024 DEEP-AA v1.1.0-2023 出版社推奨元ZIP `SIC60_6.25km_20d.zip`、元MD5 `f3f958389cc5e67ac1c4e3a6ee164318`、元SHA256 `b05a36aa4e775d69c06e2ffa897a8de8a20318b65f6478298167f73cc9f7c3f9`、4,077日分の元6.25km NetCDF、`LonLat.nc`真の地点地理参照。元site重心とMAPPPD照合≤2km、EPSG:3412の投影面積歪みを修正、コロニー中心100km測地圏内、6–10月の元正の偶数coastal-polynya IDのみを面積比に変換。冬の5か月すべてで月80%以上のnative実観測がある場合だけ採用。
- source-only geotemporal gate [Actions #44545732891 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44545732891)、artifact **14539723210**、digest `sha256:702ab3eeff9ed953c19a9e696492ba9bf5cddce204d40a9c7d9b1234d98f9f96`。元860 site×seasonのうち**439 source support rows、85 site、11 region、2004–2010の7 winters**。予告した3地域のサイト数 Victoria Land=**20**, Wilkes Land=**16**, Southwest Antarctic Peninsula=**8**。すべてpre-fixed physical gates PASS。405/439行は正のポリニヤ曝露（残りは真に観測したゼロ）。
- 暴露の平均0.07030、標準偏差0.06319、範囲0–0.26676。予告した直接曝露はサマー塩分ではない。観測はsea ice衛星derivedなので統計的に独立な無作為操作ではない。

## 単一の事前固定解析（local independent calculation）

**先に凍結** [DIRECT_POLYNYA_OPTICAL_ISOTOPE_MODEL_FROZEN_20261119_JA.md](DIRECT_POLYNYA_OPTICAL_ISOTOPE_MODEL_FROZEN_20261119_JA.md) (commit `ee423e0b0ecb7b92b0d25aab16dcc26203dd8b6b`) への完全一致を確認。元の同source DOY, DOY², Nov–Feb 海氷割合, GLORYS θo水温, original site固定効果, source region×season固定効果。元δ¹⁵N proxy Yは全モデル同じ439行。ランダム抽出や新しいウィンドウ・半径の選択なし。

| 439同一観測のモデル | M0からの追加残差R² | 100km真のポリニヤ割合が10 percentage points増える場合のδ¹⁵N proxy係数（‰） |
|---|---:|---:|
| M0 = 海氷＋水温など調整のみ | 0% | — |
| M_S = M0＋Nov–Feb表層塩分 | **2.1429%** | — |
| M_P = M0＋DEEP-AA 100kmポリニヤ | **3.7939%** | **−1.0031**、11 source-region cluster t(10) CI **[−1.4668, −0.5395]** |
| M_SP = M0＋表層塩分＋DEEP-AA | **5.2928%** | **−0.9216**、11 source-region cluster t(10) CI **[−1.3493, −0.4939]** |

M_SP の追加残差割合：**M_Sに対して3.2188%**。region×season・site FEを除去したPとSの相関は **−0.08043**。11個の元地域を1つずつ除外しても、β_Pの符号は両モデルとも**全て負**：M_P の係数/ポリニヤ割合単位 −11.664〜−7.621、M_SP −10.910〜−7.546。

**この現象は「ポリニヤが活発な年にδ¹⁵Nが高くなる」という固定した正方向仮説とは逆**。事前宣言に従い正方向機構の支持 `NO_GO_DIRECT_POLYNYA_ASSOCIATION`。このラベルは「無関連」を意味しない。得られた負の同一標本内の関連は探索的記述として保持し、正方向への再探索はしない。

## 凍結した2004–2006学習→2007–2010時間外評価

2004–2006年 train **132 rows /79 sites /10 regions**、2007–2010年 test **291 rows /79既観測sites /10 regions**、訓練に未出のsiteに由来する16rowsは新しいsite切片を捏造できず除外。未知のregion×season固定効果を予測に流用せず、学習元siteだけのinterceptを利用。

| 同じ291未使用seasonのsite-equal RMSE (‰、小さいほど良) | 値 |
|---|---:|
| M0 | **1.83954** |
| M_S | **1.80090** |
| M_P | **1.84893** |
| M_SP | **1.81221** |

真のポリニヤを足すと、**塩分なしではM0より悪く（M_P 1.849 vs M0 1.840）、塩分ありでもM_Sより悪い（M_SP 1.812 vs M_S 1.801）**。region-block 2,000 bootstrap paired MSE difference: M_P−M0 **+0.03466‰² [−0.13760,+0.22534]**、M_SP−M_S **+0.04084‰² [−0.17040,+0.29469]**。95%区間は0を跨ぐため、予測的に明確な害とも主張できないが、**予測改善は認められない**。

## 科学上の最終Disposition

1. **直接ポリニヤを測った意味はあった**：少なくとも塩分の正の相関を説明する正方向の中間機構を示すものではなく、ポリニヤ曝露は**逆向きの条件付き関連**があり、地域除外にも耐える。
2. **実測食性シフトの証拠ではない**：光学δ¹⁵N proxyの地理的/時間的な基準同位体変化、採餌範囲、夏の本当の栄養段階、海域一次生産等を区別する独立実測がなく、δ¹⁵Nを魚の摂食割合に直結できない。多くの同源検定探索の後であり、全探索経路でのfamily-wise発見として扱わない。
3. **機構探索停止**：A/B/C・実測ポリニヤも、最初の「夏表層塩分→δ¹⁵N proxy 正方向」を独立に説明し、かつ未来の島嶼・南極域へ時間転用できる機構を発見したとは言えない。主原稿に「機構未確定の弱い条件付き塩分相関」として極小の位置づけ。温暖化・海氷・繁殖時期・繁殖空間の既存肯定結果を主線に戻す。
4. **再現確認条件**：元source ZIP digest と原source site-season count、FWL 2-way FE、region t10 intervals、known site holdoutをGitHub Actions #44547277067と照合。再現差があれば原因を記録し、作為的な追加仮説/窓を探索しない。

## 実装/再現入口

- source-only [`extract_original_DEEPAA_100km_25km_source_20261119.py`](extract_original_DEEPAA_100km_25km_source_20261119.py)、source [Actions #44545732891](https://github.com/zuizui0223/mina/actions/runs/44545732891)
- frozen test [`fit_one_frozen_DEEPAA_100km_optical_d15N_20261119.py`](fit_one_frozen_DEEPAA_100km_optical_d15N_20261119.py), [Actions #44547277067](https://github.com/zuizui0223/mina/actions/runs/44547277067)（**SUCCESS**、同一439行と符号・region CI・2004–06→2007–10時間外RMSEでローカル計算と一致。）。
- すべてDraft PR #214枝であり、main・凍結Paper2・Ecology Report等を変更・mergeしない。
