# 追加の原補遺・旧画素座標と連結陽性領域の位置支持

2026-11-20。新たに一次資料4ファイルを取得した。反射率や生態応答のモデルは実行せず、原文書・scene一覧・座標対応のみを調べた。取得物は`public_grid_evidence/`、URL・HTTP status・bytes・SHA256は同ディレクトリの`source_receipts.json`に保存。

## 今回取得できたもの

1. **Youngflesh et al. 2026の最終補遺**。[mmc1.pdf](https://ars.els-cdn.com/content/image/1-s2.0-S0960982226007414-mmc1.pdf)は2,002,214 bytes、SHA256 `3ca85684c505d263f1925c71c6f02af9cd4ee57825785bdf247573892b2a02bb`。Figure S1–S4とTable S1を含む。格子原点・cell生成・切出し補間仕様は記載されない。
2. **最終Table S2のCSV**。[mmc2.csv](https://ars.els-cdn.com/content/image/1-s2.0-S0960982226007414-mmc2.csv)をHTTP 200で取得。420,947 bytes、SHA256 `0663f54b9ae3bbd4a77ca276f1f7d4c7e05f1270c095d747f734417e3c9164a2`。3,938行・119 Site ID・1,721固有L1製品。列はSite ID/name、緯度経度、Landsat Product Identifier、Date、Satellite。**画素のrow/colや格子のextentではない。** 既存RDS由来のL7陽性一覧2,652 site×product組のうち2,643組が一致し、9組は一致しなかった。全てHOPEの361行、学習期間7撮影・後年2撮影である。`source_rds_pairs_not_in_final_tableS2.csv`に列挙した。これは「元公開RDS」と「最終論文採用scene一覧」が完全一致しないという監査結果であり、除外理由や誤りは未確定。今回既存分析から削除していない。
3. **Lynch & Schwaller 2014のTable S2添付**。[s003 DOCX](https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0113301.s003)は20,242 bytes、SHA256 `1a69a082a3afd6e83bb110a2f6474c2e3fd414329f1351b1501e4db179d1984d`。実体の冒頭はSupporting Information S1 / Landsat Retrieval Methods。TOA六帯域の角度変換、6×6遷移行列、変換空間の距離dが0–1の分類則を収録する。これは分類式の具体的復元資料になるが、実行プログラム、raster-to-colonyの格子や補間手順は含まない。式はWord数式の分数・累乗を含むため、単純テキスト抽出をそのままコード化しない。旧KMZのNASA FTP URLも記載されるが、今回KMZ本体を取得したとは扱わない。
4. **Schwaller et al. 2013の原画素テーブル**。[PANGAEA 804588](https://doi.pangaea.de/10.1594/PANGAEA.804588)、[実TSV](https://doi.pangaea.de/10.1594/PANGAEA.804588?format=textfile)をHTTP 200で全取得。1,162,231 bytes、SHA256 `05ea627065a4e9d5b905e49a98c88a6197c965892825f0512d8ba7cd14c707c4`。9,143行・187 colony IDs・47陽性source files、実撮影1999–2003。本文の195 scenesは探索母集団であり、陽性表の47 filesと混同しない。文献説明には187/189の表記揺れがあり、ここでは実テーブルの187を報告する。

## 旧画素データは中心の意味を明記している

PANGAEAの提供者メタデータはrow/columnを**元Landsatファイルで0起算**、northing/eastingを**RAMP極平射影のpixel center**、緯度経度をWGS84のpixel centerとして説明する。全9,143行でeastingとnorthingの30 m剰余はともに15 mである。テーブルの汎用列名は`UTM north/east`だが、提供者の説明はRAMPであり、この列名だけでUTMとして再投影しない。rotationはtrue northに対する説明であって、EPSG平面上でその値だけ画素を追加回転する根拠にはしない。[原メタデータ](https://doi.pangaea.de/10.1594/PANGAEA.804588)

現RDS由来の`source_positive_records.csv`と旧テーブルを、path/row/実撮影日＋easting/northing完全一致で照合した。共通撮影は36件、そのうち座標完全一致は**2,434行・47地点**。旧source file×座標の重複は0。詳細集計は`source_geometry_crosscheck.json`に保存した。この一致は、同撮影・同座標のsubsetについて**旧資料では中心と定義された位置との整合性**を新たに示す。

ただし、旧source IDは現Collection 2の処理日付き製品IDではない。一致だけでは2025年RDSの全格子の中心定義、非整数セル間隔の生成法、現在配布画像への補間、値の同一性までは証明できない。旧9143行もアルゴリズム陽性であり、独立の真値ではない。今回公開の実行可能な上流抽出コードは追加取得できなかった。

## 3×3・5×5の陽性近傍から言えること

以下は**幾何学的な提案・推論**であり、一次論文が保証した糞純度ではない。同じ地点・同じL1撮影の復元格子で、周辺を含む3×3または5×5の全セルに元陽性記録がある場合、内部セルを選ぶことは位置ずれに対してラベル支持を保つ方法として合理的である。異なる日・年の陽性を合算して穴を埋めない。

- 位置の不確実集合をU、候補画素の実支持範囲をF、同日陽性セルの仮定した和集合をPとすると、全ての許容位置で`F + U`がPに含まれることを検査する。これはPをFとUで侵食した内部を使う操作に相当する。中心か角かの候補・登録誤差・補間kernelの支持幅もU/Fの定義に明示する。3×3という個数だけから許容誤差を自動的に決めない。
- 全陽性3×3の中央は、単に「8近傍のどこかへ接続している」より強い支持になる。細い鎖状の連結成分や穴のある領域は全近傍条件を満たさない。row/colの列端をまたぐcell番号連続を隣接と数えない。
- 得られるのは**指定した位置誤差モデル下での、歴史的な元分類ラベルへの支持**であり、糞の面積率・純度ではない。未知の画像補間が広い範囲を混合する場合や、誤差の上限が未実証の場合には、感度分析としての位置づけに留まる。
- 同じ分類器の近接陽性には誤分類の空間相関があり、9個/25個を独立の真値反復として扱えない。2014年の一次論文は土壌誤分類、他のペンギン種、飛翔性海鳥を挙げ、s003はLovill Bluff、Mount Biscoe、Scullin/Murrayを飛翔性海鳥の混入疑いで除外している。大きな連結陽性領域でもAdélieの純糞とは限らない。[2014本文](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0113301)、上記s003
- ラベルがない周辺セルは負例にせず不明とする。後年の同一位置への転用は持続性という追加仮定であり、L8の新年独立真値にはならない。3×3・5×5条件と位置誤差範囲は分光値や生態応答を見る前に固定し、残る地点・地域・年の偏りを報告する。

今回の新資料は「剰余15 mの座標を中心とする旧公開画素」の存在と、一部現RDS座標との一致を示した。現行native画素を一律半画素移動すれば原著を再現できる、という結論にはならない。
