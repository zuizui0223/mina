# SCAR外部食性：41,010元行から独立再現の支持範囲を確定

2026-11-02 / mina Draft PR #206。今回の判断は **別島でSignyの海氷×食性差が再現した、ではなく、元資料でどこまで同定可能か**。既存のSigny・MAPPPDの肯定結果を否定しない。

## 原資料・データの粒度

SCAR Southern Ocean Diet and Energetics Databaseの2023固定版（Zenodo DOI 10.5281/zenodo.7796465）。公開GloBIミラー commit 1856664248be16b9dcee9ba56d2b23d87f3d9cd1、原25.6MB表Git blob 418c4495ad27fe2f62e96305525019fd2fee905f をCIに固定。元 **41,010餌項目行**からPygoscelis3種の**1,180行、31原出典**をsource-firstで抽出。2026現在のSCARデータ全体と2023固定版がbyte-identicalとは主張しない。

元SCARの日付は observation_date_start/end。年齢・採取月を見ず年だけで結合しない。**−999 はtrace（微量で非定量）でありゼロではない**。Fish/Crustaceaの集約行とその下位分類群は入れ子なので両方足さない。原行は餌項目または研究集約単位であり、個別の胃1件と同一視できない。

## 検証可能な元出典

| source_id | 島・出典 | 元餌項目行 | 元種×採取年 | 繁殖季 | 魚・甲殻類が数値的に揃った群 |
|---|---|---:|---:|---|---:|
| 22 | Cape Shirreff／Polito et al. 2011 | 35 | 4 | 2007/08、2008/09 | 3/4 |
| 189 | Gourlay Peninsula（Signy）／Lynnes et al. 2004 | 60 | 10 | 1996/97〜2000/01 | 1/10 |
| 398 | Stranger Point／Juáres et al. 2018 | 24 | 12 | 12繁殖季 | 12/12 |

Cape Shirreff 2007/08 の原著集計湿重量は **Gentoo魚0.163、Chinstrap魚0.004**、差0.159。2008/09はGentoo魚0.308、甲殻類0.682だが**Chinstrap魚がtrace**で、種間の魚割合差を数値にできない。両種の魚＋甲殻類が定量できる共通繁殖季は**1季節のみ**。Signy source189は既存のSigny研究の再録で、別島追試に含めない。Stranger Point source398は**Adélie単独12季節**なので、種間差の独立再現は不可能。

## 結論と再現

SCAR2023固定版のこの抽出では **Signy以外で少なくとも２種×同じ島×定量できる魚・甲殻類×複数の繁殖季** という最小の再現ゲートを通過しなかった。湿重量の測定法、個別胃と集約値、採取日・季節とSICの対応がさらに揃わない限り、単一の普遍的な温暖化応答へ変換しない。

再現コード：research/climate-penguin/work/scar_external_diet_v1/audit.py、work/scar_external_diet_grain_v2/inspect.py。検証CI：[原全数監査](https://github.com/zuizui0223/mina/actions/runs/41411233867)、[trace＋prey hierarchy監査](https://github.com/zuizui0223/mina/actions/runs/41412033089)。Strangerの単独食性・海氷比較は [別レポート](../scar_stranger_point_ice_v1/REPORT_JA.md)。main、Paper1、Paper2を変更しない。
