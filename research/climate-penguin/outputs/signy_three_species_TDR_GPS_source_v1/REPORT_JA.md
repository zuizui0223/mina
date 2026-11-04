# Signyの3種：BAS原GPS×TDRを同じdeployment IDで照合

2026-11-05｜mina Draft PR #206。元6アーカイブを再取得してファイル形式・タグID・TDRヘッダを照合し、元3種GPSの正規source content SHAを再確認。[再現CI SUCCESS #41921358734](https://github.com/zuizui0223/mina/actions/runs/41921358734)、源manifest artifact 13368285415。

## 真に同じ原タグIDで両機器の記録が存在する個体

| 種 | 元GPSメンバー | 元TDRメンバー | 非空かつ同じIDで結合可能 |
|---|---:|---:|---:|
| Adélie | 41 | 48 | **38** |
| Chinstrap | 121 | 124 | **108** |
| Gentoo | 11 | 11 | **11** |

GPSメンバー数と独立個体数は必ずしも一致しない。Chinstrapの元GPSには同内容のファイル名重複が1件、空・非有効追跡も存在。元TDRの無圧力・短いファイルは個体の潜水なしとしない。TDR圧力ヘッダは3種とも DateTime, Pressure [dBars] を持ち、水温列を含む。Chinstrapの108メンバーはDEP_IDも含む。原TDRのZIP内部未圧縮量はAdélie 497,408,595 byte、Chinstrap 1,633,584,490 byte、Gentoo 198,836,277 byte。

Adélie TDR DOI 10.5285/bf62d713-93e5-487f-acba-1ec2da35c7e1、Chinstrap修正Version2 DOI 10.5285/da13e049-be2b-4345-bbdd-ab960cb24731、Gentoo DOI 10.5285/ff0cbcb7-bdad-4d03-bdf2-a54c54d67d9f。GPS DOIは順に 10.5285/55b4d36f-c5e1-4d64-bb14-0b832dcd4b88、10.5285/8f8ccba5-01af-4b00-8a3b-c3c85b24bf92、10.5285/9cb04ca6-f88f-4368-b715-45ff73ff81eb。Chinstrap旧Version1の誤ペアは使用しない。

**この数字はGPSとTDRの観測が同じタグに存在するという観測機会であって、実際に時刻が重なり、深度・採餌・獲物摂取が確認されたタグ数ではない。** GPS全168非空追跡、174,127位置の内容SHA e65a884341346a95ebb4a25de492d350716fde5f5cb77a669d66846811f6800a は従前の監査と一致。元TDR ZIP内ファイルはパス・未圧縮長・CRC・小さなヘッダを読んだsource gateであり、TDR全ファイルの内容SHAまで計算したという誤表現を避ける。

## エラーと修正の実施履歴

初回3ジョブが source audit で停止：元GPSのファイル名に年や追加トークンを含む場合を厳密なID_GPS.csvで読めず、Adélieの原41ファイルを誤って0とカウントしていた。元GPSの既存のSource-verified parserと同じ判定（先頭のタグID＋_GPSを含む末尾CSV）へ修正し、**同内容のGPS重複1メンバー**を検証可能な形で処理。次のCIで元6ZIPの完全取得、タグ3種の数値検算がSUCCESS、潜水候補の限定48タグパイロットも実行完了。データソースそのものは失われていなかった。

再現：research/climate-penguin/work/signy_three_species_TDR_GPS_source_v1/audit.py、元6ZIPをActionsで再取得。派生 source_inventory.json に各元タグID・メンバーCRC・ヘッダ・個別時間開始・欠測候補とソース観測粒度を保存。捕食行動を結果へ昇格させるには、別の[潜水候補のセンサ・GPS時刻QA](../signy_three_tdr_gps_pilot_v1/REPORT_JA.md)を参照。元main・凍結Paper1/2不変。
