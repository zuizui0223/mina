# 将来の海氷曝露と公式CCAMLR保護区を重ねるための真正空間ソース確認（2026-11-16）

**判定：公式の採択済みMPAポリゴンは取得・出典固定できた。海域アクセスの保護率は未計算。** 個体の採餌GPSを持たないため、将来計算できるとしても「海上潜在アクセス域と管理海域との幾何的重なり」であり、真に保護された採餌・繁殖巣数や将来個体群維持確率ではない。

## 出典と確定した地理データ

CCAMLR公式 [Public Data Repository / Marine Protected Areas](https://github.com/ccamlr/data/tree/main/geographical_data/mpa) の **version v0.9, 2022-08-04**。CC0公開。元 `CCAMLR_MPA.json` のGit Blob SHA1 `17fdf0d2ef6388c02d1b1a45d7e7c7d4e9a6cd0a`、保存元repostory commit `8f17ec7e1e37d139ead6ea277821d5983beabd6a` を事前固定。

元GeoJSONには計 **6個のMPA polygon**：Ross Seaの **GPZi / GPZii / GPZiii / KRZ / SRZ** の5 zone と、South Orkney Islands southern shelf の **SOSS**。前者の`GAR_Reference` はConservation Measure **91-05 (2016)**、後者は**91-03 (2009)**。出典内の`GAR_Start_Date`は採択作業の日付であり、実際の法的効力開始日を意味するとは限らない。公式の[2025/26 conservation measures schedule](https://cm.ccamlr.org/)では、CM 91-03 とCM 91-05が現行の保護区域の項目に含まれる。

**CRSの重要ゲート：公式source GeoJSONは `urn:ogc:def:crs:EPSG::6932`（投影座標）で、経度緯度ではない。** そのままEPSG:4326の地理データとして投影して保護率を計算すると、偽のポリゴン照合になる。source CRSを原本で検証し、利用前に海岸線mask・各zoneの採餌/漁業管理ルールと整合させる必要がある。既存の[保護区の空間評価コード](ccamlr_mpa_source_gate.py)は、MPAと海域マスクを**別々の宣言CRS**からEPSG3031へ投影するよう修正済み。

**[GitHub Actions公式source QC #43874200577 SUCCESS](https://github.com/zuizui0223/mina/actions/runs/43874200577)**。公共の`ccamlr/data`を上記commitでcheckoutし、6個のsource feature、出典名・法的CM参照・2022版、ファイルblob SHA1、原EPSG6932を検証。結果は[元official source metadata validator](verify_official_CCAMLR_MPA_zone_source.py)と出力artifact `penguin-ccamlr-six-official-mpa-source-readiness-no-overlap`で保存した。

## まだ計算しない保護効果

- CCAMLRのzone規制は同一ではない。Ross Sea General Protection Zone、Krill Research Zone、Special Research Zone等を一律に「完全漁業禁止」の一つのポリゴンにまとめない。公式2025/26 CM91-05・91-03の各zoneの操業許可条件と適用年が検証できるまでは、単なる名称から制限内容を決めない。
- 同じ南極の陸側MAPPPD site点の所属だけでは「海上採餌域が保護される」ことにならない。生物種別の観測採餌域がなければ、50/100/200km海上潜在アクセス円と**信頼できる海洋・陸域マスク**の共通分母が必要。それでも未観測GPS行動を補完した仮想バッファとの重なりであって真の保護率ではない。
- 2011–2020年の実計数は元595siteのうち271 siteだけ、巣数重みは異年の種別中央値の和。元の新265系列も出典未照合。未実測324siteの繁殖巣数・年変化をMPAで埋めない。
- 海氷10pp以上の未来曝露閾値と、MPA内の漁業の具体的な規制区域は別である。**「海氷減少が小さい場所＝保護されている場所」ではない。** GIS polygonなしでRoss Sea保護区内に全Victoria Landが入る等の地理割合を創作しない。

## 次の必要なソース

公式CCAMLR GISまたはSCAR ADDの**海陸マスクと正しいCRS・発行版・ライセンス**、2025/26のzoneごとの合法な漁業管理規則を固定してから、最初に保護区の海域空間そのものを面積で照合する。次に元271 source site×SIC曝露ごとの潜在海上50/100/200km海域割合を算出する。その時点で保護対象の漁業採餌率とは呼ばず、単に potential marine access という限定結果として示す。

**現在のソースゲート：`OFFICIAL_CCAMLR_2022_V0_9_GEOMETRY_VERIFIED_BUT_NO_MARINE_ACCESS_OVERLAP`。人口保護率は `NO_GO_PROTECTION_COVERAGE`。** 凍結Ecology Report・main・PR #206と既存原稿v0.5の主図4枚は不変。
