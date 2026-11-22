## 現在の主目標と原稿

**ポリニヤ主軸の同じ一稿をv0.7.1へ更新しました。** 地域情報の偏りを監査した結果、主関連は負を保つ一方、直前冬と翌冬の差は不確かです。Draftを維持し、著者による科学的レビューと申告を待つ段階です。

- [現行原稿への入口](https://github.com/zuizui0223/mina/blob/0dfd8462d38b2a8a022700aa3baf58ae168e6e52/research/climate-penguin/macro_panantarctic_v1/CURRENT_MANUSCRIPT.md)
- [英文要旨・本文・5図の説明](https://github.com/zuizui0223/mina/blob/0dfd8462d38b2a8a022700aa3baf58ae168e6e52/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/MANUSCRIPT_POLYNYA_FOODWEB_WORKING.md)
- [補足方法・結果](https://github.com/zuizui0223/mina/blob/0dfd8462d38b2a8a022700aa3baf58ae168e6e52/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/SUPPLEMENT_POLYNYA_FOODWEB.md)
- [再現手順・検証記録](https://github.com/zuizui0223/mina/blob/0dfd8462d38b2a8a022700aa3baf58ae168e6e52/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/README.md)
- [MEPS準備要件](https://github.com/zuizui0223/mina/blob/0dfd8462d38b2a8a022700aa3baf58ae168e6e52/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/submission_preparation/MEPS_REQUIREMENTS.md) / [著者情報シート](https://github.com/zuizui0223/mina/blob/0dfd8462d38b2a8a022700aa3baf58ae168e6e52/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/submission_preparation/AUTHOR_INFORMATION.md)

Title: **Winter coastal-polynya area is associated with annual variation in Adélie penguin optical isotope proxies**

## 科学的に重要な修正

439観測・85地点・11名目地域の設計を維持しました。固定効果後の推定情報は425観測・82地点・8地域にあり、M_Pの情報量はVictoria Land55.0%、Wilkes Land19.0%に集中します。新しい区間を見る前に選択した単一のCV3地域ジャックナイフ診断を追加し、元の11地域・8地域CR1区間も保存しました。地域情報の集中度を推論の自由度に読み替えていません。

| 比較 | 点推定（‰/10pp） | CV3・t(7)の95%区間 |
|---|---:|---|
| 主関連 M_P | −1.003 | [−1.675, −0.331] |
| 夏の塩分調整後 M_SP | −0.922 | [−1.515, −0.328] |
| 直前冬−翌冬、同じ358観測 | −0.688 | [−1.470, +0.095] |

時間差の区間は0を含み、要旨・本文・図3・結論・カバーレターをこの解釈へ揃えました。元の応答とR1,000応答で対称に検証しています。同じ439観測の塩分係数は+0.646‰/塩分単位、CV3区間[−0.196,+1.488]として追加し、別860観測の+0.834と区別しました。

負の方向は元の正方向仮説に反する探索的所見です。夏の海氷濃度の調整を同冬extent一定の構造検定とは呼ばず、食性転換・因果機構・将来食性を推定しません。前方予測の改善なし、後期の小さい点推定、選択されたクロロフィル標本、Signyの不明確な裏付け、後年の既知陽性回収64.8%による測定ゲート不合格を保持しています。

## 書類と検証

現行MEPS公式要領と関連方針を2026-11-21に取得しました。本文と5図を一つにしたWordは22頁・1,718,740 bytes、要旨222語、総語数4,633（集計定義を要件表へ記録）。補足・図集・Alt text・1頁のカバーレター・著者情報シートを含め、6 Word・39頁を個別に目視確認しました。全図169mm幅、図内文字10pt以上、SVG/PNGと約800dpiのCMYK TIFFを用意しました。

独立QRによる凍結結果58照合、CV3診断34照合が全てPASS。freshディレクトリで4工程を再実行し、5 PNG・5 TIFF・11数値抽出がbyte一致しました。6 Wordは全展開後ZIP entryの内容と名前が一致し、格納日時によるZIP外側の差だけを除外しています。原衛星処理全体や補足S4–S6の全解析を再現したという主張ではありません。GitHub Actionsの新規実行を検証したという主張でもありません。

[再利用台帳](https://github.com/zuizui0223/mina/blob/0dfd8462d38b2a8a022700aa3baf58ae168e6e52/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/submission_preparation/SOURCE_REUSE.md)と[出典・加工の告知](https://github.com/zuizui0223/mina/blob/0dfd8462d38b2a8a022700aa3baf58ae168e6e52/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/submission_preparation/SOURCE_NOTICES.md)を追加し、主要ZenodoデータのCC BY 4.0とCopernicus所定クレジットを確認しました。歴史的NSIDC v4の個別再配布ラベル、独自コードのライセンス、恒久DOIは未確定です。

## 残る著者入力と履歴

著者名・所属・責任著者・貢献、資金・利益相反・倫理／再利用・投稿歴の申告と実際の科学的レビューは未完了です。AI支援は初稿・コード・検算・図作成を含む実態を開示し、英文校正だけと記述していません。出版社方針への適格性や著者承認を自動認定していません。投稿、新規DOI公開、ライセンス付与、mergeは行っていません。

変更は現行原稿フォルダと入口の41ファイル（既存25、新規16）に限定し、他の3,759既存blobは保持しました。旧v0.6と凍結元解析は変更していません。前版のPR説明は[履歴へ保存](https://github.com/zuizui0223/mina/blob/0dfd8462d38b2a8a022700aa3baf58ae168e6e52/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/history/PR214_DESCRIPTION_BEFORE_V071.md)しました。

Latest manuscript commit: 0dfd8462d38b2a8a022700aa3baf58ae168e6e52

