# PR #214 description before the v0.7.3 scientific effect-scale clarification

Captured 2026-11-22 from the existing Draft PR before editing its title/body.

## 現在の原稿

**同じポリニヤ主軸原稿をv0.7.2へ更新しました。** 引用・出典と図の読み上げ用説明を整えた改訂です。v0.7.1の解析結果と図の数値は保持しています。Draftのまま、著者による科学的レビューと事実情報の確定を待つ段階です。

- [現行原稿への入口](https://github.com/zuizui0223/mina/blob/7235604eb26ea242883403cd8b225855b19b3d6b/research/climate-penguin/macro_panantarctic_v1/CURRENT_MANUSCRIPT.md)
- [英文要旨・本文・5図の説明](https://github.com/zuizui0223/mina/blob/7235604eb26ea242883403cd8b225855b19b3d6b/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/MANUSCRIPT_POLYNYA_FOODWEB_WORKING.md)
- [補足方法・結果](https://github.com/zuizui0223/mina/blob/7235604eb26ea242883403cd8b225855b19b3d6b/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/SUPPLEMENT_POLYNYA_FOODWEB.md)
- [再現手順と検証記録](https://github.com/zuizui0223/mina/blob/7235604eb26ea242883403cd8b225855b19b3d6b/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/README.md)
- [MEPS準備要件](https://github.com/zuizui0223/mina/blob/7235604eb26ea242883403cd8b225855b19b3d6b/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/submission_preparation/MEPS_REQUIREMENTS.md) / [著者情報シート](https://github.com/zuizui0223/mina/blob/7235604eb26ea242883403cd8b225855b19b3d6b/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/submission_preparation/AUTHOR_INFORMATION.md)

Title: **Winter coastal-polynya area is associated with annual variation in Adélie penguin optical isotope proxies**

## v0.7.2で変更したこと

1. 文献8件の題名・著者・年・DOIと、本文が依拠する内容を一次資料で照合しました。Reavesは出版社の書誌・抄録・補足と登録情報の確認であり、有料本文の通読とはしていません。Meierのデータ引用には正式DOIとメタデータ確認日を記載しました。
2. 図5点の代替テキストを、配置・単位・区間と解釈の限界が分かる英文へ改訂しました。数字を読み上げ向けに綴り、本文Wordと図集の埋め込み説明を同じ内容へ揃えました。別添説明は図ごとに同じページへ収めました。
3. NOAAの日次・月次v4配布記録にあるアクセス・利用の制約なしという記載を記録しました。原NSIDCリリースとのDOI不一致は未解決のままで、原版のライセンス確定やCC0付与とはしていません。本文の補足節参照をS4–S5へ訂正しました。

[文献照合記録](https://github.com/zuizui0223/mina/blob/7235604eb26ea242883403cd8b225855b19b3d6b/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/submission_preparation/evidence/bibliography_audit_20261122.json) / [v4配布条件の確認範囲](https://github.com/zuizui0223/mina/blob/7235604eb26ea242883403cd8b225855b19b3d6b/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/submission_preparation/NSIDC_V4_DISTRIBUTION_TERMS.md)

## 科学的な結果と限界

439観測・85地点・11名目地域の設計を保持しています。固定効果後の推定情報は425観測・82地点・8地域にあり、地域情報の偏りを踏まえたv0.7.1のCV3診断と旧CR1区間を残しました。

| 比較 | 点推定（‰/10pp） | CV3・t(7)の95%区間 |
|---|---:|---|
| 主関連 M_P | −1.003 | [−1.675, −0.331] |
| 夏の塩分調整後 M_SP | −0.922 | [−1.515, −0.328] |
| 直前冬−翌冬、同じ358観測 | −0.688 | [−1.470, +0.095] |

主関連は負を保ちますが、冬同士の差は不確かです。同じ439観測の塩分係数は+0.646、CV3区間[−0.196,+1.488]として、別860観測の+0.834と区別しています。

負の方向は元の正方向仮説に反する探索的所見です。夏の海氷濃度調整を同冬extent一定の構造検定とは扱わず、食性転換や因果機構を確立したとはしません。予測改善なし、後期の小さい点推定、選択されたクロロフィル標本、独立した食性裏付けの不成立、後年の測定ゲート不合格を明示しています。

## 書類と今回の検証

本文と5図を一つにしたWordは22頁・1,718,937 bytes、要旨222語、総語数4,654です。全6 Word・39頁のうち、変更した5頁を新たに目視確認しました。再レンダリングでPNGハッシュが一致した24頁と、Word全体のbyteが一致する10頁は前版の確認を引き継ぎました。変更した3 Wordの機械的なアクセシビリティ確認では検出事項はありません。これは包括的な規格適合認証ではありません。

凍結入力・図・解析スクリプト等56ファイルのbyte一致を確認しました。v0.7.1の数値58照合・CV3診断34照合とオフライン再現記録は保存しており、今回それらを再実行したとはしていません。

[今回の編集検証](https://github.com/zuizui0223/mina/blob/7235604eb26ea242883403cd8b225855b19b3d6b/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/editorial_verification_20261122.json) / [39頁の確認根拠](https://github.com/zuizui0223/mina/blob/7235604eb26ea242883403cd8b225855b19b3d6b/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/document_visual_qa.json) / [ファイル要件の実測](https://github.com/zuizui0223/mina/blob/7235604eb26ea242883403cd8b225855b19b3d6b/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/submission_preparation/evidence/preflight_v072.json)

## 残る著者入力と履歴

必要な入力は既存の著者情報シートへ集約しています。実際の科学的レビュー、著者名・所属・責任著者・貢献、資金・利益相反・倫理／再利用・投稿歴などの事実と、公開範囲の決定は未完了です。AI支援は初稿・コード・検算・作図を含む実態を開示しています。著者承認や出版社方針への適格性を自動認定していません。

今回のソース変更は19ファイル（既存13、新規6）で、他の3,787既存blobを保持しました。v0.6と凍結元解析は変更していません。前版のPR説明は[履歴](https://github.com/zuizui0223/mina/blob/7235604eb26ea242883403cd8b225855b19b3d6b/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/history/PR214_DESCRIPTION_BEFORE_V072.md)に保存しました。投稿、新規DOI公開、ライセンス付与、mergeは行っていません。

Latest manuscript commit: 7235604eb26ea242883403cd8b225855b19b3d6b

