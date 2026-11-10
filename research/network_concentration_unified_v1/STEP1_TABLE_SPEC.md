# Step 1　統合表の定義案 v0.1

**2026-11-06／設計草案。既存の生態学的結果を再計算・上書きした表ではない。**

## 1. 行と空間単位

主表 `network_species` の1行は、**出典 × ネットワーク × 種 × 計数単位 × 固定構成単位集合 × 二時点**。同じ対象の旧解析窓や解像度違いを主解析の別反復にしない。`row_id`はこのキーから決定し、`cohort_id`は構成単位IDのソート済み集合のハッシュとする。

「ネットワーク」は、出典が定義した繁殖地点の集合である。JNCCのMaster site、MAPPPDのregion、皇帝のice_reg、島内監視区画は、同じ地理分類・閉鎖個体群を意味しない。`scale_class`、`component_type`、`parent_network_id`、`lineage_group`を残す。

| 入力 | ネットワーク | 構成単位・時点の採用案 | 保存根拠 |
|---|---|---|---|
| JNCC | Country × Master site | 元Site.ID。Seabird 2000とSeabirds Countの原調査年。全子Siteの早期年・後期年がそれぞれ一致するV39規則を主候補とする | [既存V39仕様](https://github.com/zuizui0223/mina/blob/0f913ecfd4fd03e328dc1a6c78c77e451a99fe9e/contracts/JNCC_MATCHED_EPOCH_COHORT_V39_FROZEN.md) |
| MAPPPD | 原region | 同じ巣計数地点、同じ原方法で対応する二つの繁殖開始年。観測0を残す | [既存地点年表](../climate-penguin/outputs/comparison_audit/mapppd_unambiguous_site_seasons.csv) |
| 皇帝 | 原ice_reg | 50固定コロニー、2009年と2018年。N_meanを配分の点推定に使用 | [著者公開表](../climate-penguin/outputs/emperor_ice_land_substrate_v1/author_colony_summary.csv) |
| Palmer | Cormorant、Humble、Litchfieldの各島 | 既存の固定7、9、9 colony codes。1991年と2017年。Litchfieldの最終0を残す | [既存結果・原本識別子](../../results/PALMER_BREEDING_PATCH_CONCENTRATION_RESULT_V1.json) |
| Signy | Signy島 | 1996年と2019年。Adélieは5 canonical units、chinstrapは9 units | [Adélie仕様](../../contracts/SIGNY_BREEDING_PATCH_CONCENTRATION_V1.json)、[chinstrap仕様](../../contracts/SIGNY_CHINSTRAP_BREEDING_PATCH_CONCENTRATION_V1.json) |
| Ross | Ross島 | BRDM/BRDN/BRDS/CRZE/CRZW/ROYDの6原セクター、1985年と2024年。3地区集約は解像度照合のみ | [既存仕様](../climate-penguin/outputs/ross_island_spatial_scale_v1/README.md) |

`network_id`は種を含まない地理IDとし、種は`species_id`、種別の監視集合は`cohort_id`で識別する。PalmerのChristine/Torgersenは監視コード数が変わるため、島合計を固定区画の代わりに入れない。既存情報で区画対応が確定しない場合は台帳に理由を残す。Signyの別の1998–2009年・8 literal units版は同じ対象の追加反復にしない。

## 2. 二時点の決め方

### 主仕様：同期した最初・最後のセンサス

平均値を整数個体へ丸めないため、**本解析は最初・最後の同期したセンサス1回ずつ**とする。長期系列を年ごとの回帰係数へ変換してからJNCCの二時点差と混ぜない。年度は繁殖季節の開始年に統一し、元年表記を構成単位表に保持する。

1. JNCC・Palmer・Signy・Ross・皇帝は上表の既存期間と単位を使用。JNCCは原調査年がネットワーク内で一致することを確認する。V30の非同期行も台帳に残すが、別年の計数を同時点の分布とみなさない。
2. MAPPPDは、固定した入力表のregion×speciesごとに、**共通の比較可能な地点が3以上ある年対**を観測有無・ID・方法だけで列挙する。その中で開始年が最も早い年対を選び、同じ開始年なら終了年が最も遅いものを選ぶ。集中、減少方向、気候値は年対選択に用いない。原方法が不明、または複数方法が一行へ集約されている場合は比較可能性未確定として保持し、方法一致とみなさない。
3. その二時点で調査記録のある共通地点集合を固定する。これは地域全地点の完全調査ではなく、**対応する監視地点の部分集合**である。各時点の元調査地点数と共通集合の割合を記録する。
4. 選んだ最終年の総数が0でも、最後に正だった年へ戻さない。計数の妥当性で行が不適格になっても、別の有利な年対へ差し替えない。
5. 元の親集計と子区画を同じベクトルへ重ねない。既知のRoss階層などは原単位対応を記録し、上位・下位の結果を独立反復にしない。曖昧な親子対応は理由付きで保持する。

採用年対・構成単位・除外理由を `endpoint_registry` に保存し、そのハッシュを共通効果量計算前に固定する。K≥3は既存JNCCのネットワーク定義に合わせる構造上の規則であり、種数・行数・p値に応じて変えない。K<3、二時点なしなどの候補も、消去せず非推定行として残す。

### 複数年平均の位置づけ

主解析完了後に期間を選び直さない。事前指定する補助値は、主端点の年を含む**最初の3暦年／最後の3暦年**の年平均とし、同じ構成単位の全3年が実測され、両窓が重ならない場合に限定する。10年換算の分母には**両窓の平均観測年の差**を使う。帰無の共通シェアは6年の元整数計数をプールして定め、各年の元総数で独立に生成してから、観測と同じ年平均・集中計算を行う。3年分の合計を端点個体数として扱わない。3年がそろわない、または窓が重なる場合は補助値をNAとし、窓を広げない。JNCCの非同期調査をこの平均感度で同期扱いへ救済しない。

## 3. 共通効果量

構成単位j、端点tの記録値をn_jt、総数をN_tとする。**各端点のN_tが正なら、その端点の指標**を計算する。

\[
p_{jt}=n_{jt}/N_t,\qquad H_t=\sum_jp_{jt}^2,\qquad D_{2,t}=1/H_t.
\]

D2は実効繁殖単位数である。物理的な繁殖面積や島数ではない。両端のNが正のとき、集中の生の変化は、

\[
Y_{raw}=\frac{10}{\Delta t}\{\log H_1-\log H_0\}
=-\frac{10}{\Delta t}\log(D_{2,1}/D_{2,0}).
\]

**正は集中、負は分散**。10年当たりは比較用の対数変化率であり、10年間を実際に観測したという意味でも将来予測でもない。

### 計数データの共通帰無

帰無仮説は、**総数が変わっても構成単位間の潜在的なシェアは不変**。両端の対応する計数だけから、

\[
\bar p_j=\frac{n_{j0}+n_{j1}}{N_0+N_1},\qquad
\mathbf n_t^{*(b)}\sim\mathrm{Multinomial}(N_t,\bar{\mathbf p})
\]

を二時点それぞれで生成し、同じYの計算を行う。主応答は

\[
Y_{excess}=Y_{raw}-\operatorname{mean}_b(Y^{*(b)}).
\]

固定シェアと有限計数で予想される集中変化からの、同じ対数単位の偏差である。B=20,000、seed基準20261106、行別seedはrow_idと基準seedのSHA-256から決める。帰無平均・SD・2.5/97.5%点・平均のMonte Carlo SEを別列にする。**帰無SDや分位点を観測効果のSE／CI、逆分散重みとして使わない。** 主応答にz-scoreや旧p値を使わない。

適用対象は、原単位が両端で同じ、非負整数相当の記録計数、N0・N1≥2、K≥3の同期行。1.0のような表現を整数として読むことは許容するが、調整値1.2やモデル事後平均を丸めない。JNCCのadjusted countsにも、原調整・調査誤差を較正したモデルでないという条件を付ける。

旧Palmer/Signyは全期間のシェアとPoisson/Gamma–Poisson、旧JNCC V30は初期シェアからの後期配分基準であり、新仕様と異なる。旧補正値・年傾き・p値を転記せず、この二時点仕様から再計算する。[旧ローカル帰無コード](../../src/mina/hierarchy_count_error.py)、[旧JNCC仕様](https://github.com/zuizui0223/mina/blob/0f913ecfd4fd03e328dc1a6c78c77e451a99fe9e/contracts/JNCC_COMPONENT_CONCENTRATION_V30.md)。

### 皇帝とモデル推定値

皇帝ではD2とY_rawを著者N_meanの配分指標として計算する。これはD2の事後平均ではない。全地点が同比例に変わればY=0という算術基準は共有できるが、**0を差し引いて有限計数補正済みと呼ばない**。共同事後サンプルがないためY_excessとその観測不確実性はNA、`null_status=model_joint_uncertainty_unavailable`。周辺区間を独立に乱数化して合計やD2の区間を作らない。原N_meanの配分変化は同じ主表・同じ論文の記述パネルに保持する。

### 個体数・記録総数の変化

\[
G=\frac{10}{\Delta t}\log(N_1/N_0),\qquad
\%\Delta_{dec}=100\{\exp(G)-1\}.
\]

正は増加、負は減少。N0>0なら全期間の変化率100(N1/N0−1)も保存する。N1=0なら全期間−100%を残し、初期D2は保持、後期D2・対数変化・集中の二時点変化・帰無補正はNA。N0=0の場合も起点ゼロとして記録し、正の後期D2があれば保持する。疑似計数を加えず、記録0から永久絶滅を断定しない。集中変化をGで割ったκはG≈0で不安定なので主指標にしない。

## 4. 主表の項目

完全な型・欠測条件は[SCHEMA.json](SCHEMA.json)に対応する。表示用の短い表はネットワーク、種、K、t0/t1、N0/N1、Y_excess、G、幅、役割を中心とする。

| 項目群 | 列 | 定義 |
|---|---|---|
| 識別 | row_id, dataset_id, network_id, species_id, cohort_id | 出典・原種ラベル・固定単位集合を識別。JNCCのRazorbil等の原綴りを保持し標準表示名との対応を別記 |
| 階層 | scale_class, component_type, parent_network_id, lineage_group | ネットワークの尺度、子単位の種類、上位集合、同じ元計数の系統 |
| 時点 | year0, year1, dt_years, epoch_sync_status | 二時点の実観測年と経過年数。非同期値を中央値の年に押し込まない |
| 支持 | K, occupied0, occupied1, surveyed_components0, surveyed_components1 | Kは両端で観測された固定集合。occupiedは正値の構成単位数 |
| 調査範囲 | coverage0, coverage1 | K／当該端点の元の比較可能な調査単位数。地域全個体数を何割調査したかではない |
| 総数 | N0, N1, count_unit, estimate_type | 原単位の総数。AON/AOS/AOT/AOB/IND、nest、pair、adult_indexを混同しない |
| 集中 | neff0, neff1, concentration_raw_decade | D2二時点とY_raw |
| 帰無補正 | concentration_excess_decade, null_mean_decade, null_sd_decade, null_q025_decade, null_q975_decade, null_mcse_decade, null_status | Y_excessと帰無の記述。観測CIではない |
| 総数変化 | abundance_log_change_decade, abundance_pct_change_decade, abundance_pct_change_interval | Gと変換した変化率。全期間率は最終0でも保持 |
| 空間幅 | extent_km, coordinate_status | 固定集合の原座標間の最大WGS84測地距離。占有正値の単位だけで計算しない |
| 状態 | endpoint_status, analysis_role, exclusion_reason, prior_view_status, source_id | ゼロ総数、非推定理由、主解析／解像度照合／モデル指数、既知結果、出典台帳とのリンク |

幅はあくまで観測地点間の直径であり、面積、利用可能 habitat、採餌範囲ではない。全構成単位の比較可能な座標がないときはNA。JNCCのStart.Lat/Longは原開始点で、コロニー重心と断言しない。Palmerの島代表点を島内区画の座標として代用しない。幅が0のときも小さい正値を足して対数化しない。

## 5. 同じ原計数を一度だけ使う

`analysis_role`は次のいずれかとする。

- `macro_primary`：重複しないネットワーク間の、共通計数帰無が適用できる行。JNCCとMAPPPDの比較候補。
- `local_resolution`：Palmer/Signy/Rossの島内行。共通効果量は計算するが、上位MAPPPDの集計と一緒に独立反復として主モデルへ足さない。島内だけの結果を同じ論文で並べる。
- `model_index_reference`：皇帝など、記録計数と同じ誤差モデルを使えない配分指数。
- `descriptive_only`：非同期、構成変更、非整数調整値、小標本、0総数など。理由を保存する。
- `input_recovery_pending`：使用済みの長期原本を回収できていない候補。短い現存表や島合計に差し替えない。

Rossの6コードはMAPPPDと同じ原行なので重複が確定している。PalmerのCHIS/CORM/HUMB/LITC/TORGも原出典を照合する。`source random effect`を入れるだけでは二重使用を解消しない。主モデルでは同じ系統の重複を除き、補助図では階層関係を表示する。

## 6. Q4のために保持する二つの付表

### unit_endpoints

`row_id × component_id × species_id × endpoint`。row_idは主表の行または種ペア表の行を指し、`analysis_unit`で区別する。元計数、計数単位、実調査年、原方法、調査済みか、観測0か、座標、原行の出典を保持する。主表と種ペア表の構成比をそれぞれ再現できる最小単位である。

### network_species_pairs

`network_id × species_pair × pair_cohort_id × 二時点`。両種で同じ地理的構成単位が同じ二時点に調査されているときだけ推定する。種ごとの主表で集合や期間が違う場合、**ペア専用の共通集合・共通二時点で両種のN・G・構成比を元計数から再計算**する。別集合の主表総数をそのまま結合しない。

MAPPPDのペアでは、両種・両端で観測と計数方法が比較可能な同一物理単位が3以上ある年対を列挙し、開始年が最も早く、その開始年で終了年が最も遅いものを採用する。JNCCは両種・共通単位の原調査年が早期・後期それぞれ一致する集合に限り、複数の年対があれば同じ早期優先・後期最遅規則を使う。固定期間の島内系列は上表の期間を維持する。ペア用の時点・構成単位も`endpoint_registry`で先に固定し、種単独の端点と同じになることを条件にしない。

重なり自体は両種×両端の4総数がすべて正のとき定義できる。共通帰無補正はさらに、4総数がすべて2以上、K_pair≥3、各種の原単位が両端で同じ、非負整数相当の計数という条件を満たす場合だけ行う。いずれかの総数が0なら候補は残し、重なり変化とペアの対数減少指標をNAにする。

\[
O_t=\sum_j\min(p_{ajt},p_{bjt})=1-\frac12\sum_j|p_{ajt}-p_{bjt}|.
\]

0は配分の分離、1は同じ相対配分。種ごとに端点pooled sharesと両端総数を固定した独立multinomial基準から、\(Z=10(O_1-O_0)/\Delta t-E_0[10(O_1^*-O_0^*)/\Delta t]\)を得る。この独立配分基準は、同じ潜在分布が維持される場合の有限計数効果を表し、種間競争のモデルではない。

未記録種を0にしない。SignyのAラベルとCラベルは別々の区画なのでunion＋0埋めで重なり0を作らない。Palmer/RossのAdélie単種系列と皇帝だけのセクターではQ4は該当なし。共通単位がないという理由を、重なりがないという生態学的結果へ変換しない。

## 7. この段階の完了条件

全対象を台帳へ載せ、出典・単位・二時点・固定集合・階層・非推定理由を保存する。原表の合計と主表のNが一致し、観測0と欠測が区別され、増加・不変・起点0・終点0も残っていればStep 1の基本構造は完成する。形質値・気候値を見て行、期間、指標を選び直さない。関連モデルはStep 2とStep 3を固定した後に実行する。
