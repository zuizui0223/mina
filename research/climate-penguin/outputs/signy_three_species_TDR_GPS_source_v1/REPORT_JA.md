# Signy島3種の元GPS×TDR：個体単位の潜水位置が比較できるか

2026-11-05｜mina Draft PR #206。2026-11-04に到達した「AdélieとChinstrapの同じ1時間GPS位置（2011/13/15）」を、元の同一deployment IDのTDR圧力へ接続するためのsource-first工程。**source audit CIとpilotがSUCCESSになる前に、同時潜水や空間分離の数値を結論として書かない。**

## 公開原本が存在することを公式BASで再検証

| 種 | TDR元DOI | GPS元DOI | 科学上の注意 |
|---|---|---|---|
| Adélie | 10.5285/bf62d713-93e5-487f-acba-1ec2da35c7e1 | 10.5285/55b4d36f-c5e1-4d64-bb14-0b832dcd4b88 | 元TDRは2011–2016の圧力・水温と元deployment番号、直接の魚捕獲記録ではない |
| Chinstrap | 10.5285/da13e049-be2b-4345-bbdd-ab960cb24731 | 10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92 | GPS/TDRの不整合が過去Version1にあったため必ずVersion2同士 |
| Gentoo | 10.5285/ff0cbcb7-bdad-4d03-bdf2-a54c54d67d9f | 10.5285/9cb04ca6-f88f-4368-b715-45ff73ff81eb | 2015年は元GPS追跡が１羽だけで、種全体の安定比較はできない |

BAS公式の説明では、GPSとTDRのファイル名は同じ鳥に装着したdeployment IDを共有。元TDRは約1秒間隔で圧力（dbar）を測定するが、**圧力ゼロ点の基準が不確か**なのでdbarを厳密な深度・捕食イベントに直結させない。

## 同一生物学的粒度への整合

既存GPSの全168非空deployment、元位置174,127点、原member内容SHA e65a884341346a95ebb4a25de492d350716fde5f5cb77a669d66846811f6800a を再監査する。TDRアーカイブはZIP central directory、元ファイル名・非圧力の最初8KB・CSVヘッダ・CRCを取得し、**圧力を開封する前**に原deployment IDでGPSと厳密に照合する。ヘッダだけで「潜水した／潜水していない」と結論しない。

出力：research/climate-penguin/work/signy_three_species_TDR_GPS_source_v1/audit.py、出典別source_inventory.json。元6ZIPの取得と原スキーマ検査にはGitHub Actions workflow penguin-signy-three-species-TDR-GPS-original-source-v1を使用。原CSV/TDR時系列はGitHubに再配布せず、集計監査のみ保全する。

## 生態学的な判断上限

この工程から分かるのは、島・繁殖季×同一個体のGPS／TDRソースが存在するか、データ形式が一致するか。**同時刻の海域分割**の推定は潜水候補とのGPS時刻結合とセンサQA後の工程へ進める。前回の元BAS同時刻GPS観測65日・1,121時間枠は維持するが、そのGPS点全部が実際の捕食地点だとは仮定しない。凍結main・Paper1・Paper2には変更を加えない。
