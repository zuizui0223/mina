# アデリー塩分3機構の検証：A冬塩分/B成層は大陸横断のδ15N光学proxyを追加説明・時間外予測しない

**2026-11-19 JST | Mina Draft PR #214 exploratory source-gated result | main 5肯定結果と凍結原稿は未変更。**

## 判定

**`NO_GO_AB_MECHANISM_WINNER`**。冬の表層塩分（A、ポリニヤ・ブライン仮説の代理）と夏の50m-表層密度差（B、融解水/成層仮説の代理）を**元693の完全一致観測行に揃えて検証**した。どちらも、海氷＋水温＋同じsite＋季節日M0や、夏の表層塩分を加えたM_Sを**2005–2012の時間外予測**では改善しなかった。Cの200m深層水は有効39/82海洋格子で事前の地理支持ゲートに達せず、A/B/C全比較・生態学的機構勝者の判定対象にしない。

実行証拠：[GitHub Actions #44541379015 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44541379015)、source-derived artifact **14538722146**、SHA256 **553f724a32d6b1589654ba841295cc2003636077b9d7fc9258df379b3898692e**。事前契約 [MECHANISM_AB_EXPLORATORY_MODEL_FROZEN_20261119_JA.md](MECHANISM_AB_EXPLORATORY_MODEL_FROZEN_20261119_JA.md) は **commit a9ba0f45fda92af9733ccac08e5def3ce7609b5b** として初回のoutcome当てはめ前に保存した。実行コード [fit_original_AB_693_optical_isotope_exploratory_20261119.py](fit_original_AB_693_optical_isotope_exploratory_20261119.py) はsource input SHA256検証、同一固定効果、真の時間分割、地域復元で発見基準を実装。

## 1. 元観測分母・解析の新規範囲

- 元アデリーYoungflesh et al. 2026から再構成したδ15N光学proxy: 860 site×season, 88 site, 13 original source regions, 82 GLORYS wetcells.
- 夏表層塩分と冬塩分: 860/860物理データあり。BのTEOS10 0m–47.37m成層: **693/860**、**72 original sites / 68 real wetcells / 12 original source regions**。Palmer Landは50m鉛直層が欠けるためBの共通コホートから脱落。抜けた167行をゼロ・データ補間扱いしない。
- 元860表層塩分と新GLORYS再抽出の絶対差最大3.55e−15、元海洋格子ID・site×season完全一致。
- **同じ693元site×seasonの説明解析のみ**比較。M0=DOY + DOY² + Nov–Feb海氷 + 同海水温 + original site FE + original reporting region×season FE。M_S=M0+夏表層塩分、M_A=M0+6–10月表層塩分、M_B=M0+Nov–Feb密度差。M_SA/M_SB/M_AB/M_SABは探索的な足し算。同一original wetcell・regionが擬似反復を作らない。
- 時間検証は**train:1996と1999–2004、243元観測、67 site、11 regions**；**heldout 2005–2012：学習済み66 site／435 site×season、10 regions**。初出siteの15行はsite固定効果を予測できず除外。heldout側のregion×season FEやtarget Yを未来入力として使わない。

## 2. 同じ693元観測・同じFEにおける探索的な追加残差説明率

| 候補モデル | M0に対する条件付き残差R²増分 | 読み方 |
|---|---:|---|
| M0：海氷＋水温＋site・region×seasonなど | 0% | 同一source baseline |
| M_S：従来の**夏の表層塩分** | **1.5907%** | 元860での2.88%とは異なる、B取得可能693だけの推定対象 |
| M_A：**直前の冬表層塩分** | **0.0052%** | Aの予測「冬塩分がより強い」はこの代理変数では未支持 |
| M_B：**夏の鉛直密度差** | **1.3012%** | 同sourceでは夏の表層塩分より説明率が小さい |
| M_SA：夏塩分＋冬塩分 | 1.6005% | 夏塩分に対する冬塩分の追加 ≈0.0097 percentage points of M0 residual SSE |
| M_SB：夏塩分＋成層 | 1.6101% | 夏塩分に対する成層追加 ≈0.0194 percentage points of M0 residual SSE |
| M_AB：冬塩分＋成層 | 1.3338% | M_B単独と大差なし |
| M_SAB：夏・冬塩分＋成層 | 1.6149% | M_Sからの追加は約0.0242 percentage points |

同じ行集合での記述的比較であり、係数に因果解釈はない。特に同位体の基準値、海流、水塊移流、分光PLSR誤差は未同定。

## 3. 確定済み2004年固定→2005–2012年時間外テスト

**66 original known sites、435 original site×season、10元地域**に対して学習固定。site-equal RMSE（δ15N proxy ‰、小さいほどよい）。

| モデル | 時間外 RMSE ‰ |
|---|---:|
| **M0：海氷＋水温＋DOY＋site** | **1.38307** |
| M_S：M0＋夏表層塩分 | 1.38889 |
| M_B：M0＋成層 | 1.39506 |
| M_A：M0＋冬塩分 | 1.47409 |
| M_AB：M0＋冬塩分＋成層 | 1.47722 |
| M_SAB：M0＋夏塩分＋冬塩分＋成層 | 1.47613 |

冬塩分・成層のいずれも**M0より悪い**。保守的10地域×2,000 bootstrap、paired site-equal squared-error difference（candidate−M0、負がcandidate有利）は：
- M_A: **+0.26007‰²**、地域復元95%範囲 **[−0.01329,+0.61769]**。
- M_B: **+0.03331‰²**、同95% **[−0.02527,+0.11602]**。
- 対M_S: M_A **+0.24392** [−0.02888,+0.58472]、M_B **+0.01716** [−0.01144,+0.05308]。
- A vs Bの差も地域bootstrapでゼロ横断。**AもBも安定して悪化させると断定はできないが、事前規準「A/BがM0とM_Sの両方に勝つ」は成立しない。**

## 4. 科学的結論と取り下げる解釈

1. **元860の正の塩分相関は維持**。元sourceで海氷・水温・site・region×season調整した海面塩分β=+0.8341458‰/塩分単位、partial R²=2.88%、13元地域cluster t 95%区間 **[−0.01594,+1.68424]**。本結果は**Bが有効な693**との物理変数比較なので、元860の効果を「消失した」と言わない。
2. **Aは今回の冬塩分代理に関して未支持**。冬塩分≠海氷生産・沿岸ポリニヤ発生頻度、ポリニヤそのものを反証していない。日別実ポリニヤマスクを利用する研究は元15 source seasonでの別時間ゲートが必要。
3. **Bは今回の水柱密度差代理に関して未支持**。密度差は温暖化・淡水・成層の合成であり氷河融解量を直接測っていない。海域別の塩分δ15N符号逆転機構を立証しない。
4. **Cは当該沿岸元格子では識別不能**。元82の深層200m有効39、南西半島2/8では元860の公平比較に満たない。別の海底谷・採餌海域に基づく構造化されたsourceが必要。
5. **根本の応答は光学再構成δ15N proxy**。同位体の地理的POM baseline変動、実餌種/魚割合、追跡とisotopeの元時空間重複は独立に検証不可能なまま。観測0.186‰/塩分残差SDに対し原PLSR試料校正RMSE約1.7‰である点に注意。これは多数観測平均係数の直截の不確実性CIではなく、解釈上の測定尺度差。
6. 2026年11月19日の3仮説比較から**追加の有意な生態学的機構勝者なし**。元mainに既に統合済みの5肯定結果／凍結原稿・主図に**このA/B mechanistic storyを加えない**。将来δ15Nや2100年のペンギン巣数へ外挿しない。

## 5. CIエラーの正確な修正履歴

初回 [44541125715](https://github.com/zuizui0223/mina/actions/runs/44541125715) はモデル本体を最後まで計算・保存し、**最終のsample-region QAだけ** original 13 regionsをB完全同支持の12 regionsと誤って同一視する行で失敗。観測、コード・モデル、事前判定を変更せず、**QA assertのregion期待値だけ13→12**修正 (commit `6dc8e833bc3f05590a81213792412a3cb683abba`)。その後 [44541379015](https://github.com/zuizui0223/mina/actions/runs/44541379015) はfull SHA、当てはめ・source split・支持域・全5結果ファイルuploadを**SUCCESS**。探索的結果が未確認な新独立サンプルで得られたことを意味しない。

## 次工程の判断

**停止条件に到達**。新規の海洋説明変数・地理窓・深度を選び直してp値を探す継続はしない。次に機構を研究として強くするには、少なくとも真のポリニヤ観測と採餌到達域、夏の実測同位体基準値、地域3以上で同じ年の直接餌構成という**データ設計の変更**が必要。今は負の結果を正しく凍結し、元マクロ論文の独立に成立している肯定結果を保全する。
