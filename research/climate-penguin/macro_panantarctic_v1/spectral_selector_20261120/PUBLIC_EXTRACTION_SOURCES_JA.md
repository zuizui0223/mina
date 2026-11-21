# 公開原資料から確認できる抽出・格子情報

確認日: 2026-11-20。対象は元画素の位置・反射率処理と独立ラベルの取得可能性のみ。生態応答の解析は行っていない。

## 結論

**原著はTOA反射率を使用する。しかし、公開された記述から原RDSを生成した格子原点・extent・再標本化法・cell番号の定義は特定できなかった。** 座標の30 m剰余が15 mであることだけでは、native画素中心への±15 m移動を正当化できない。元データが再投影・再標本化後の値なら、移動した点にnativeバンド値を付与しても原観測の再現にはならない。

## 原著と公開コード

- 最終論文の正式題名は *Space-based monitoring of penguin diet links sea ice, food webs, and population change*。著者公開PDFのSTAR Methods e1は、Landsat 4/5/7、30 m、1984–2013、11–2月の**top-of-atmosphere reflectance**を明記する。e2ではSchwaller et al. (2013)の糞検出法を引用し、WRS row 90–130、Tier 1/2、image quality ≥5、sun elevation ≥15°、M2M取得を記載。L8/9は帯域差のため除外と明記される。したがって新しいL8 surface reflectanceに原係数・閾値をそのまま適用することは原著と同一手順ではない。[著者公開の最終論文PDF、e1–e2](https://www.youngfleshlab.com/assets/papers/Youngflesh-et-al-2026-Current-Bio.pdf)
- ZenodoのAPIを今回再取得してHTTP 200を確認。公開説明は`cell`をcell number、geometryをEPSG:3031とするが、nrow/ncol、extent、原点、cellの0/1起算、再投影順序・補間法を説明しない。`guano_bin`は陽性のみを含むと明記する。Landsat入力は抽出済み`landsat_reflectance_L457-2025-07-16.rds`。[Zenodo 17409948](https://zenodo.org/records/17409948)、[直接API](https://zenodo.org/api/records/17409948)
- GitHubの今回確認したmain SHAは`4ab7c992fc2232b7905af0d1aa949d88dc9561ea`。公開treeには元画像からの糞検出・RDS作成プログラムがなく、`3-predict-diet.R`はこのRDSを読み、既存geometryからeasting/northingを取り出す。sfを利用していることは確認できるが、**上流抽出がsf/terraで行われた証明ではない**。[固定版コード](https://github.com/caseyyoungflesh/penguin_diet_from_space/blob/4ab7c992fc2232b7905af0d1aa949d88dc9561ea/Scripts/3-predict-diet.R)、[公開tree](https://api.github.com/repos/caseyyoungflesh/penguin_diet_from_space/git/trees/4ab7c992fc2232b7905af0d1aa949d88dc9561ea?recursive=1)
- Schwaller et al. (2013)は原著の文献4、DOI `10.1016/j.rse.2013.08.009`。その全文は今回取得できず、2026年処理のsoftware/versionを断定しない。関連するLynch & Schwaller (2014)はLandsat CDRの**TOA**を使用し、半島用に岩・土壌等の学習例を追加した6バンドの楕円体分類を記載する。遷移行列・判定則はTable S2にあると明記される。これはアルゴリズム復元の資料であり、2025年RDSの格子仕様の証拠ではない。[一次論文Methods](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0113301)

最終論文はscene一覧をTable S2とするが、今回独立した補遺ファイルの内容は取得確認できていない。最終論文のe1–e5と公開コードを確認した範囲での「未確認」であり、世界の全公開資料に存在しないとの断定ではない。必要な証拠は抽出直前ラスタのtransform/shape、sceneとcellの対応、再投影・切出し・再標本化コード、TOA変換規約である。

## 実際に公開取得できる新年ラベル

**ArdleyのZenodo 14503437は匿名取得可能。** 今回API 200に加え、公開ZIPの先頭64 bytesをRange取得し、HTTP 206、`Content-Range: bytes 0-63/4109917595`、ZIP signature `PK`を確認した。4.11 GB全体の再ダウンロードはしていない。[公開記録](https://zenodo.org/records/14503437)、[実ファイル](https://zenodo.org/api/records/14503437/files/Dataset%20distinguish%20breeding%20penguins%20drone%20imagery.zip/content)

提供者の記録全体は2013–2018、Ardley・King George・Nelson・Deception各島の一部、画像とvectorを含む。ただし、これを全地点の糞マスクがあるという意味に広げない。既に取得済みのZIP member indexを今回読み直したところ、`Guano/<season>/Ardley_<date>_<adelie|gentoo>.shp`はArdleyの44ファイル、22日×2種、2013/14・2014/15・2016/17・2017/18の4季節である。例えば2013-12-20と2018-01-14を含む。`.prj/.dbf/.shx`も既存抽出手順の対象。これは撮影日に対応する独立糞ポリゴンの具体的候補であり、L8と日差・位置合わせ・30 m被覆率を検証できる。ただし1島の部分的annotationであり、外側全部を非糞とみなせず、大陸全体・全季節のラベルを代替しない。

ローカル照合元: `work/ardley_zip_index/penguin-Ardley-Zenodo14503437-4GB-ZIP64-native-GIS-index-no-new-Y/ARDLEY_4GB_ORIGINAL_ZIP_MEMBER_INDEX.json`、既存`diet_salinity_source_20261117/extract_ardley_original_true_guano_44_shapefiles_source_only_20261120.py`。これらを変更していない。

既存の原SHP検証記録では、44/44がPolygon、EPSG:32721、Adélie 227・Gentoo 914オブジェクト、属性には`green`, `green_red`, `darkred`, `guanorings`等を含む。したがってnest countの点ではなく実際の糞関連被覆のvectorである。ただし今回geometry全体を再取得したわけではなく、この詳細は既存[原幾何検証記録](../diet_salinity_source_20261117/ARDLEY_44_GUANO_GEO_MASKS_30M_SOURCE_PURITY_AND_INDEPENDENT_REPLICATION_VERDICT_20261120_JA.md)に基づく。同記録のAdélie注釈総面積は各日247.9–566.8 m²で、名目900 m²画素の80%純度に不足する。小さな部分annotationを高純度30 m真値に読み替えない。

## 取得済みラベルとして数えない候補

- Le et al. (2019)は31手動ラベル画像と弱ラベル群を説明するが、今回確認した指定GitHubのdevel treeにはshp/zipマスクがなく、READMEのダウンロードリンクは**学習済みモデル**。対応日・地理参照付き真値の実取得とは扱わない。[論文](https://openaccess.thecvf.com/content_CVPRW_2019/papers/cv4gc/Le_Weakly_Labeling_the_Antarctic_The_Penguin_Colony_Case_CVPRW_2019_paper.pdf)、[提供README](https://github.com/lynch-lab/CVPR19-CV4GC-WeaklyLabeling/blob/devel/README.md)
- Danger Islandsの2015 UAV・nest shapefileは論文に**著者へのrequestで提供**と明記される。論文図の糞領域を原マスク取得と数えない。[一次論文Data availability](https://pmc.ncbi.nlm.nih.gov/articles/PMC5834637/)
- Cape HallettのKOPRIは既存`l8_negative_replication_20261120/LABEL_ACCESS_AND_HISTORICAL_PERSISTENCE_JA.md`に記録された申請制のまま、本調査では申請・メールを行っていない。

今回、Ardley以外に「対応日・地理参照・糞annotationが揃い、直ちに取得済み」と追加できる新しい資料は確認できなかった。
