# SCAR原bulk δ¹⁵Nによる独立ポリニヤ追試：出典・採集年・地理が合わずNo-Go

**2026-11-21 JST | PR #214 (Draft) | GitHub Actions [#44890386911](https://github.com/zuizui0223/mina/actions/runs/44890386911) SUCCESS | source-only; 生態系係数の再fitは行っていない。**

## 固定ゲートと原データの検証

事前に [FROZEN_SCAR_REAL_ISOTOPE_SOURCE_SUPPORT_GATE_JA.md](FROZEN_SCAR_REAL_ISOTOPE_SOURCE_SUPPORT_GATE_JA.md) をコミット（`693190e`）してから、一度だけ元Sourceのペンギン同位体データを読み、修正はログの追加と原ソース既存列 `isotopes_body_part_used` の読み出しのみで実施（モデル、期間、閾値、半径、除外条件の変更なし）。

- 本物の公開SCAR Southern Ocean Diet and Energetics Database, Zenodo record [20047874](https://zenodo.org/records/20047874)、元ZIP `SCAR_Diet_Energetics.zip` **9,543,574 bytes**。Zenodo API上の原サイズ・MD5 `5e098c268ce0028704bc4b06300cb0ef` と完全一致。ZIP CRC通過。
- 元 `scar_isotopes_mv.csv` は全分類群32,925 measurement rows。元のPygoscelis 3種（Adélie/Chinstrap/Gentoo）計**1,244 measurement rows**、`measurement_name=delta_15N` **408 rows**。原 `scar_sources.csv` で `source_id` を研究出典に照合した。
- 原`quality_flag`、`is_secondary_data`、同一採集季・日時の正確さ（11–2月、122日以内）、原 bbox対角**25km以下**、南緯55度以南、2004–2010または2013–2021、固定の旧88地点WGS84 centroidから最短**25km以内かつ唯一**で一段ずつ絞り込んだ。重要：広域ソース地名のbbox表記が点（0.0km）でも実GPSの測位精度を証明しない。

## 実証されたボトルネック

| 元データの段階 | 実際の数 |
|---|---:|
| SCARの全分類群同位体測定行 | **32,925** |
| Pygoscelis 3種の測定行（δ¹³CやC:N含む） | **1,244** |
| 3種のbulk δ¹⁵N測定行 | **408** |
| 厳密な日時＋源位置精度＋時期窓を通過した出典×産地×種×繁殖季のグループ（2004–2010） | **4** |
| 同（2013–2021） | **6** |
| 上記と旧光学糞88元地点で25km以内に1地点だけ一致 | **0 / 4; 0 / 6** |

**ゼロの直接原因は地理的対応の欠如。** 元4+6グループはたくさんの独立地点ではなく、**2007・2008年のCape Shirreff（Polito et al. 2011; ヒゲ、ジェンツーの羽毛）**と**2013・2015年のPowell Island, South Orkney Islands（Tarroux et al. 2018; アデリー、ヒゲ、ジェンツーの羽毛/血液等）**という**2原ソース・2産地・4繁殖季**のみだった。

- Cape Shirreffの元SCAR産地中心から旧光学糞88元地点最近接 `TSIS` へ **154.14km**。
- Powell Islandから旧88最近接 `HERO` へ **550.17km**。
- 分母の研究出典・産地がどれほど限られるかを示すため、同じ場所・年の多数の個体試料・測定行は決して独立な“地点”として加算しない。
- さらに `isotopes_body_part_used` は `feathers`、`feather`、`down`、`whole blood`、`plasma`、`red blood cells` と異なり、組織の同位体統合期間も異なる。どの標本でも厳密な冬の採餌位置や羽毛形成冬の対応を立証していない。

主解析を通るはずの **20独立採集地×同時期、3地域以上**の条件は満たされないため、事前の決定規則どおり `NO_GO_SCAR_INDEPENDENT_ISOTOPE_POLYNYA_TEST`。これは**ポリニヤの効果がないという検定ではない**。SCARを使って元439の探索的負係数を新しい独立生態学的関連へ昇格させることはできない。

## 必要な解釈の境界

1. 同じ2004–2010元光学糞439地点×季節に、原著の1000組のPLSR較正を適用しても100km冬ポリニヤの負係数は残った（光学proxy −1.023‰/10pp, region 95%区間 −1.498〜−0.548）。原著感度を越える**新時代・独立Yの再現ではない**。
2. SCARの今回の原ZIPは同位体の個体値を実際に収録しているが、地点・時期・組織対応が成立しないので**ポリニヤとYの回帰自体を行わなかった**。
3. 原Michelson USAP-DC 602094の真のアミノ酸AA 55 source site-yearはbulkの基線と栄養段階の測定解釈には有用。しかしこちらも旧88地点に同一地理で対応せず、同じ帰結。
4. 海氷・温暖化・繁殖空間の生態学的結果を持つ南極マクロ論文の主線を変更しない。ポリニヤ負関連はsupplement/探索の位置から昇格させない。新しい独立画像・実測食性・羽毛形成年/海域が対応する公開資料が確保されるまでポリニヤ→オキアミという機構の有意性探索を止める。

## 再現性・状態

- 事前凍結仕様：[source-only gate](FROZEN_SCAR_REAL_ISOTOPE_SOURCE_SUPPORT_GATE_JA.md)
- 正式スクリプト：[audit_original_scar_pygoscelis_isotopes_source_only.py](audit_original_scar_pygoscelis_isotopes_source_only.py)
- GitHub Actions [#44890386911](https://github.com/zuizui0223/mina/actions/runs/44890386911) **SUCCESS**、原ZIP MD5/SHA/CRC/source schema、原88地点数、測定行→産地×年の縮約、source-only候補10グループのログ実証。公開Artifact **14701831675**、ZIP SHA256 `3c38187a3973814f829dcf0fff1c3913486adcc22b03b21b0426a638e6de1a79`。**Artifactは派生元地点metadataと集計JSONのみで元個体同位体測定Yを配布しない。**
- PR #214だけにcommit。 `main`・凍結Ecology Report・v0.5/v0.6/Paper2は未変更。投稿・マージなし。
