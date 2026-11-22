# GLORYSの冬塩分(A)・成層(B)：元860×seasonと完全に一致した新しい物理的結果

**2026-11-19 JST | mina Draft PR #214 | 生物応答モデル未実施 | mainと凍結原稿を変更せず**。

## 実計算の成否

- 固定契約 [MECHANISM_ABC_PREFLIGHT_FROZEN_CONTRACT_20261119_JA.md](MECHANISM_ABC_PREFLIGHT_FROZEN_CONTRACT_20261119_JA.md) commit `7c78f03390b852a164093916935d18a83757cc6a` に従う。
- GitHub Actions **[44539876656 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/44539876656)**、artifact **14537926313**（30日保存）、結果は4 files: `source_82_cells_15seasons_winter_salinity_summer_density.csv`, `source_860_site_seasons_A_B_physics_only_NO_OUTCOME.csv`, `source_13regions_A_B_physical_support.csv`, `source_AB_physical_exposure_receipt.json`。
- Original original isotope source artifact 14328755565 ZIP SHA256 `dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205`を照合、**860元site×season、88 site、82 original GLORYS wetcell、13地域、15 start seasons（1996、1999–2012）**を変更せず元wetcells索引で抽出。
- 実GLORYS12V1 202311 Zarrから**135 distinct calendar months**（各15 seasonの6–10月の5か月と11–翌2月の4か月）を取得。82格子×15季節=**1,230物理格子×season**。各月 `so` practical salinity と `thetao` potential temperature を0.494m／47.374mで抽出、GSW / TEOS-10で `sigma0_50m - sigma0_0m` を導出。
- 元860 source の11〜翌2月表層塩分との最大絶対差 **7.105427357601002×10^-15**。元のソース一致の独立QAに成功。
- 初回[44539624787](https://github.com/zuizui0223/mina/actions/runs/44539624787)は全元データ取得、値照合後のJSON最終出力に NumPy `int64` を直接渡して失敗。**データ変数・季節・判定基準は変更せず**、単なるJSON型変換（commit `9f773bd8ace20f910bba348326fb0f325898b8b8`）を修正して[44539876656](https://github.com/zuizui0223/mina/actions/runs/44539876656)にて成功。

## 観測サポート（元site×seasonが分母、独立実験のnではない）

| 物理候補 | 有効元site×season | 元sourceの解像度と解釈 |
|---|---:|---|
| **A**：直前の冬6〜10月の表層塩分 | **860/860** | 82/82元wetcellで全月有効。冬塩分≠実際のポリニヤ出現率 |
| 元M1と同じ11月〜翌2月の表層塩分 | **860/860** | 元sourceと最大差7.1e−15 |
| **B**：11月〜翌2月 47.37m−0.49m 密度差（TEOS-10, sigma0） | **693/860**（**68/82 distinct wetcells**） | 必須4か月、同一沿岸格子かつ0m/50mが有効な場合のみ。熱成層と淡水成層は未分離 |
| **C**：200m塩分と水温 | **39/82**元wetcells（2005年12月物理ゲート） | 南西半島2/8など、事前支持条件未達。元860でA/B/C三者同条件比較はNO-GO |

Bの地域ごとの元site×season支持：Victoria Land **155/197**、Wilkes Land **106/146**、Southwest Antarctic Peninsula **49/78**、Northeast Antarctic Peninsula **121/147**。深度欠測に基づく除外はランダムではない。全860を用いるAと693を用いるBの回帰適合を**別母集団のまま比較してはならない**。

## 生態学的推論の凍結

- **今の作業は物理ソースだけ**。結果はAやBのどちらが光学δ15N proxyを説明するか、冬のポリニヤがペンギン食性を変えるか、食物網基準値変動が原因か、を一切検証していない。
- AとBを統計比較するなら、**同じB有効693元site×season**上で、元M0基準／現地Nov–Feb表層塩分M1／A冬塩分／B成層の完全一致行集合と同じ固定効果を使用。手元データでモデルの当てはまりを競うなら探索的と表記し、事前の時間外検証に合格しない限り未来予測にしない。
- ポリニヤAの厳密検証には別の直接ポリニヤ観測が必要（DEEP-AA期間2003–2022には2011–2012年欠測）。海水塩分や冬SIC単独ではブライン排出を特定できない。
- δ15NはYoungflesh 2026のLandsat画像からの**光学再構成proxy**。魚・オキアミ割合ではない。POM窒素同位体同年100km内20/860という観測支持の不足は未解消。
- mainの肯定結果のβ=+0.834、partial R²2.88%、保守13 region CI [-0.016,+1.684] はそのまま維持する。今の作業では新しい有意な機構は宣言しない。

## 再現リンク

- [実行スクリプト](extract_original_82_cell_winter_and_50m_density_20261119.py)。
- [GitHub Actions YAML](../../../.github/workflows/penguin-20261119-original-82-wetcell-winter-salinity-density-AB.yml)。
- [先行GLORYS実深度ゲート](MECHANISM_ABC_DEPTH_SOURCE_VERDICT_20261119_JA.md)。
