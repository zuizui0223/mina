# 繁殖分布の集中を比較する統合マクロ解析

**状態：2026-11-07、Step 1〜5を実データで実施。Step 1 共通表675主解析行・378種ペア、Step 2 観測SSTを1,038／1,053候補行へ結合。Step 3 解析契約を新たなH3/H4関連係数の計算前に凍結（外部登録なし）。Step 4: H3/H4D/H4Wは4仮説Holm補正で支持なし、H2固執率は0/20種で未推定。独立行列実装の係数・CR1検算PASS。Step 5: 対応するCMIP6将来物理曝露は南極MAPPPDの気温3/12・海氷2/12ネットワーク×種のみ完全被覆。Step 6の一本化原稿構成を作成済み。**

## 一つの中心質問

**個体数が変化するなかで、繁殖分布は比例的な増減を超えて少数の場所へ集中するか。その強さは、種の営巣地への固執性と海洋環境の変化に対応するか。**

JNCCの海鳥、MAPPPDのPygoscelis、皇帝ペンギン、Palmer・Signy・Rossを、固定した繁殖単位の二時点比較として一つの台帳に入れる。Q1は共通尺度での集中の記述、Q2は種の特性、Q3は海洋変化、Q4は同じ場所を調査した種間の重なりである。将来計算は、この分布が置かれる物理的曝露を示す。

既存のPalmer/Signy集中、英国の二時点再配置、皇帝の配分指数、Signy食性の肯定結果は、元の推定対象・仕様の結果として保存する。今回の主応答は繁殖分布の集中に統一し、食性・繁殖時期・GPS解析はこの主モデルへ追加しない。既存英語食性稿は保存済みの成果であり、現在の作業目標はこの統合表である。

## 共通表と実際の読出し（2026-11-07）

- [実測集計表：network_species.csv](data/network_species.csv)（1,529候補、うち計数帰無680行）
- [同期した種ペア：network_species_pairs.csv](data/network_species_pairs.csv)（732候補、うち計数帰無378行）
- [端点選択台帳：endpoint_registry.json](data/endpoint_registry.json)（2,261候補を計数の符号と独立に固定）
- [再計算コード：build_step1.py](build_step1.py)、[GitHub Actions実行](https://github.com/zuizui0223/mina/actions/runs/42324472225)
- [回収・品質監査](outputs/STEP1_READOUT.md)、[集計QA](outputs/STEP1_QA.json)、[種・国別の記述的結果](outputs/STEP1_DESCRIPTIVE_PROFILE_JA.md)

JNCC・Palmer・Signyの既存固定原本はActions内でSHA照合して回収した。原Excelと元の地点別数表はGitに再配布していない。単位端点表はActionsで計19,218行を一時生成して検証し、集計表のみGitへ記録した。帰無は計数に関する理想化比較であり、独立した観測誤差・検出モデルではない。

## これまでの設計成果物

1. [STEP1_TABLE_SPEC.md](STEP1_TABLE_SPEC.md)：行の単位、二時点化、列定義、集中・個体数変化・帰無・空間幅・欠測の扱い。
2. [PREREGISTRATION_DRAFT.md](PREREGISTRATION_DRAFT.md)：Q2–Q4の方向、主モデル、判定、既知結果の開示、説明変数を凍結する条件。
3. [SCHEMA.json](SCHEMA.json)：主表、構成単位表、種ペア表、時点台帳の機械可読な列定義。
4. [SOURCE_CATALOG.json](SOURCE_CATALOG.json)：現存ファイル、別ブランチの固定参照、同じ原本の回収対象、用途と制約。
5. [PLAN.md](PLAN.md)：ユーザー指定の6工程を維持した実行順序と現在地。

## 同じ表に入れる対象と役割

| 対象 | ネットワーク／構成単位 | 論文内の役割 |
|---|---|---|
| JNCC 17原種ラベル | Country × Master site／Site.ID | 年がそろう二時点のネットワーク間比較。原単位と国を保持する |
| MAPPPD Pygoscelis 3種 | 原地域／同じ巣計数地点 | 同じ二時点で調査された固定地点集合の地域比較 |
| 皇帝ペンギン | ice_reg 8区分／50コロニー | 同じ配分指標によるモデル推定値の比較。共同事後サンプルがないため計数帰無の補正値・p値を作らない |
| Palmer、Signy、Ross | 島／固定監視区画・セクター | 細かい空間解像度での照合。同じ原計数を含む上位MAPPPD行へ独立反復として加算しない |

共通の時点数と数式だけで空間スケールが同じになったとは扱わない。主検定は重複しないネットワーク間の計数行を使い、島内行は同一論文の解像度別パネルに置く。全対象を同じ表に保持し、`analysis_role`で検定への使い方を明示する。

## 現在の入力状態

- JNCC原Excel・Palmer LTER元区画計数・Signy両種原CSVを、元URLから再取得し原SHAを確認できた。現ブランチのMAPPPDと皇帝の派生原本も一致。
- JNCCの調査年非同期721行、終点0、少数地点、皇帝の共同事後標本欠如は理由付きNAとし、元の結果を推定値で埋めない。
- 主解析675行は JNCC663・MAPPPD12（17+3種）。スコットランドの比重が大きいため英国種の方向を南極全域の一般則と同一視しない。
- 同一NOAA OISST v2.1（月次0.25°）を英国（3–5月）と南極（9–11月）の元調査年へ結合し、**1,038/1,053行**で出典・年月・地点集合を確認。未結合15行は1981年以前の8行と海域50km条件を満たさない7行。繁殖地固執率の同一定義数値はまだ **0/20種**。温暖化と集中の関連を支持したとはまだ書かない。

## 追加の実測成果：Step 2 SSTとStep 3のモデル適格性

- [Step 2 実測SST台帳](data/network_climate_intake.csv)、[英国取得監査](outputs/STEP2_OISST_UK_JOIN.json)、[南極取得監査](outputs/STEP2_OISST_SOUTH_JOIN.json)。英国 [Actions 成功](https://github.com/zuizui0223/mina/actions/runs/42329225964) と南極 [Actions 成功](https://github.com/zuizui0223/mina/actions/runs/42330003605) の元配列URLとSHAを保存。原Site.ID座標・計数は一時処理し、結果はネットワーク別の数値だけ保存。
- [Step 2 1,053行の欠測・結合可否](data/step2_join_readiness.csv) と [国・出典を分けた実測SST記述](outputs/STEP2_SOURCE_READINESS_JA.md)。H3 662/675、H4D/H4W 376/378 がデータ入力条件を満たす。H2は0/675。
- [Step 3 事前の説明変数行列監査](outputs/STEP3_PREFIT_SOURCE_DESIGN_JA.md)、[機械可読QA](outputs/STEP3_PREFIT_SOURCE_DESIGN_QA.json)、[Actions 成功](https://github.com/zuizui0223/mina/actions/runs/42330488896)。集中Y・重複Zを参照せず、H3・H4とも固定効果はランク6/6。種ペアの共有種・共有計数による相関を無視できない。

## Step 3–6 の実行結果と論文への統合

- [Step3固定解析契約](contracts/ANALYSIS_PLAN_FROZEN.md)（旧草案の混合モデルから種固定効果＋ネットワークブロック検定へ、係数閲覧前に変更理由を記録）。外部事前登録済みではない。
- [Step4固定H3/H4実測結果](outputs/STEP4_MODEL_READOUT_JA.md)・[全係数/不確実性/ハッシュ](outputs/STEP4_FIXED_ASSOCIATIONS.json)：H3 β=+0.03316、Holm p=0.940、H4D β=+0.00616、Holm p=1.000、H4W β=−0.01522、Holm p=1.000。H2は未推定。[GitHub Actions成功](https://github.com/zuizui0223/mina/actions/runs/42331279597)。[独立行列実装のQA](outputs/STEP4_INDEPENDENT_ARITHMETIC_QA.json) PASS。
- [Step5将来物理曝露](outputs/STEP5_PHYSICAL_EXPOSURE_JA.md)・[被覆率の完全監査](outputs/STEP5_PHYSICAL_EXPOSURE_QA.json)：南極12ネットワーク×種（61元構成単位）のうち元座標一致は13地点、完全対応は気温3行・厳格海域2行。英国663行には同じCMIP6 source-site mapがない。**生物学的な繁殖未来予測は実施していない。**
- [Step6 一つのマクロ論文スパイン](MANUSCRIPT_SPINE_V1.md)：本論文の肯定的な観察パターンは英国海鳥17種中15種のネットワーク平均で過剰集中が正、436/663行で正。気候・減少・種間重なりの事前方向仮説は主検定で支持されず、北海道〜南極の普遍的機構、島嶼因果、温暖化による将来個体数予測を主張しない。

## 現在の次の一手

**Step6の投稿可能性を査読目線で監査する。** 最優先は原調査境界・観測努力・非同期、JNCCの行政ネットワークを物理島と見なせない問題、およびスコットランド偏重を本文で明確に扱うこと。H2の定義を揃えた数値が確認できなければ未推定のままにする。ネガティブな主検定を事後選択で別モデルへ置き換えない。凍結済みPaper1/Paper2/mainは変更していない。
