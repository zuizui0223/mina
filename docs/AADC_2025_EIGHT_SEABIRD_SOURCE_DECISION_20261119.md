# 2025 AADC：8種海鳥の調査済み候補地と島嶼効果のデータ適格性

## 主目標と現在地（2026-11-19）

**主目標:** 氷に覆われない候補地全体のうち「どこが実際に調査されたか」を公開原データから区別する。単に既知コロニー分布を真の占有・非占有とみなさない。新たな島／大陸の効果係数は本段階で推定しない。

2025年公開の観察記録を提供する AADC EDS 5959（DOI [10.26179/5n29-r073](https://doi.org/10.26179/5n29-r073)）と、2016年潜在生息地一覧 EDS 4344（DOI [10.26179/53yk-8z83](https://doi.org/10.26179/53yk-8z83)）を公式APIで元ファイル単位に特定、SHA-256と表構造を検証した。新しい取得APIの発見ではなく、既存の [PR#180](https://github.com/zuizui0223/mina/pull/180) が使っていたアデリー11,089件の**同一データ家系**の全種・確実度表への拡張。

## 実際に検証した原本

| 公式ファイル | データ行 | 内容 |
|---|---:|---|
| `occupancy_seabird.xls` | 22,018 | 飛翔性海鳥7種の `2_search events`、18列 |
| `occupancy_penguin.xlsx` | 11,089 | アデリーペンギン `2_search events`、18列 |
| `geog_sites_all.xlsx` | 7,785 | `geog_site_id`・`geog_site_feature`・座標・area・基地距離、10列 |
| `occupancy_certainty.xlsx` | 216 | 種×P/A/NR×観察法×地物面積区分の確実度表、9列 |
| 2016年 `Spatial reference systemn coastal East Antarctica.xlsx` | 4,884 | 旧版の全候補地一覧、37列（うち余剰空欄ヘッダ28列） |

- 公式 API マニフェスト [CI #44523051952](https://github.com/zuizui0223/mina/actions/runs/44523051952)。元 XLS/XLSX 構造と SHA [CI #44524557961](https://github.com/zuizui0223/mina/actions/runs/44524557961) 成功。全原ファイルの取得・チェックサム・スキーマは `scripts/audit_aadc_2025_seabird_riskset_original_schema.py` に再現可能な形で固定。
- 出版された Southwell et al. (2025, *Diversity and Distributions*, DOI [10.1111/ddi.70066](https://doi.org/10.1111/ddi.70066)) の記載は合計 **33,297** search event。一方、AADC現在の配布元2ファイルの明示的なデータ行数は **22,018 + 11,089 = 33,107**、**差190行**。追加対象、版差、除外理由が特定できるまで **33,297件と33,107件を同じNとして統合・主張しない**。
- source `P` は報告された繁殖存在、`A` は報告された繁殖不在、`NR` は繁殖状態未報告。**NR≠A**。同じ地点×種×繁殖季節にA/Pが同居する場合は矛盾として保持する。連続する明示的A→Pも「観測された状態変化」であり、真の新規定着とは限らない。著者提供の `occurrence_cert_cat` と3種のexpert-validation欄があるが、カテゴリに対応する検出確率が既知とは扱わない。

## 新規性と設計上の停止

既存の Southwell et al. (2025) は繁殖確認・不在・未調査の空間図、確実度（高・中・低）、種別の調査被覆、基地からの距離と観測確率の関係、年代別の再訪問率を既に公刊した。**この原表で同じ地図や単純な島/大陸出現率を再計算することは新しい知見でない。**

大陸側の調査努力は7種の飛翔性海鳥でも論文推定で多くが **≤0.2%**。飛べないアデリーは内陸大陸露岩を営巣機会に含まない。原地物 `geog_site_feature` の `island` と `continent` を比較する場合も、利用可能な地域・海岸近接性・観察法・確実度の交絡を除く新しい検出設計が先に必要。

2016年4,884地点と2025年7,785地点は違う版の地理参照系であり、数の差は**温暖化による新しい露岩の増加数ではない**。調査範囲も東南極30°E–150°Eであり、前に検証した西南極半島25地点（およそ60–65°W）とは直接重複しない。2025公開台帳の観察年は1910–2020、先のSCAR露岩画素の撮影年2024より古い。

### 再現できる次段階と判定条件

- `scripts/audit_aadc_2025_eight_species_original_riskset.py` は配布元5ファイルの元SHAを強制し、原地点IDでP/A/NRと確実度lookup、島/大陸地物区分を照合し、源泉支持のみ集計する。稼働 CI: [AADC original eight-seabird source gate](https://github.com/zuizui0223/mina/actions/workflows/aadc-2025-eight-species-riskset-actual-source.yml)。
- 同じ地点×種×季節の**明示的A/P**を1単位とし、未訪問・NR・矛盾・不明IDを数えて別に提示する。年次A→Pのソース対応は参考支持数に過ぎず、直前 [PR180](https://github.com/zuizui0223/mina/pull/180) のアデリー1件STOPを撤回しない。
- 先に固定した `contracts/AADC_2025_EIGHT_SEABIRD_SOURCE_SUPPORT_V1.json` の地理的支持条件を確認し、十分な**実際に調査された大陸側候補地**と複数の独立地域が成立しなければ、島/大陸の生態学的検定を行わない。
- 実現したとしても現在の台帳には**新規露岩が生じた暦年**や**現地哺乳類捕食者の曝露**はない。温暖化の新定着・捕食者因果効果・将来の巣数予測には使えない。

**凍結済み Paper1 / Paper2、旧V41、PR180 は不変更。main未マージ。**
