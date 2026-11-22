# PR214 description before v0.7.1

Captured 21 November 2026 from the open Draft PR at head 7867969c640e9e1fce627ed0e172e549fb6b4f0f.

## 現在の主目標と原稿

**現行候補はポリニヤ主軸のv0.7一稿です。** v0.6の巣数重みづけ中心の構成は履歴に残し、その結果は補足S6へ移しました。Draftを維持しています。

- [現行原稿への入口](https://github.com/zuizui0223/mina/blob/7867969c640e9e1fce627ed0e172e549fb6b4f0f/research/climate-penguin/macro_panantarctic_v1/CURRENT_MANUSCRIPT.md)
- [英文要旨・本文・5図の説明](https://github.com/zuizui0223/mina/blob/7867969c640e9e1fce627ed0e172e549fb6b4f0f/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/MANUSCRIPT_POLYNYA_FOODWEB_WORKING.md)
- [補足方法・結果](https://github.com/zuizui0223/mina/blob/7867969c640e9e1fce627ed0e172e549fb6b4f0f/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/SUPPLEMENT_POLYNYA_FOODWEB.md)
- [再現手順・入力・検証記録](https://github.com/zuizui0223/mina/blob/7867969c640e9e1fce627ed0e172e549fb6b4f0f/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/README.md)
- [文献確認と投稿前の未確定事項](https://github.com/zuizui0223/mina/blob/7867969c640e9e1fce627ed0e172e549fb6b4f0f/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/REVIEW_NOTES_JA.md)

Title: **Winter coastal-polynya area is associated with annual variation in Adélie penguin optical isotope proxies**

## 主な変更と推論の範囲

冬6–10月・100km内の沿岸ポリニヤ面積率と、翌夏の光学δ¹⁵Nの地点内年変動を中心に再構成しました。439観測・85地点・11名目地域。固定効果後に情報を持つのは425観測・82地点・8地域で、主表示の区間は新しく明示した8地域t(7)支持感度です。

- M_P: −1.003‰/10pp、95%区間[−1.505,−0.501]。夏の塩分調整後M_SP: −0.922[−1.384,−0.459]。
- 直前冬−翌冬の同一358観測での差: −0.688‰/10pp。347情報観測・8地域での区間[−1.346,−0.029]。
- 元11地域の区間を保存し、係数・SSEが不変であることを検算。負の方向は元の正方向仮説に反し、事後の探索的所見であることを要旨に明記。
- 対照は夏の海氷**濃度**であり、extentを一定にした「量より構造」の検定とはしない。Maccapan2023、Reaves2025、Polito2019、Youngflesh2026との関係を具体化。
- 前方予測の改善なし、2007–2010の小さい点推定、偏ったクロロフィル支持、Signyでの不明確な裏付け、64.8%の既知陽性回収により後年延長を止めた事実を保持。食性転換・因果機構・将来食性は推定しない。

## 検証

独立QR実装の数値・出典照合58項目PASS。添付の凍結派生成果物だけからオフラインで検証・描画・Word作成を再実行し、5 PNG、5 TIFF、9数値抽出がbyte一致しました。本文17頁・補足6頁・図版5頁を目視確認。5図は170mm幅、SVG/PNGと約800dpi TIFFを生成可能です。新しいCI実行済みという主張はしていません。

著者情報・各種申告、現行投稿規程の最終確認、再配布条件と恒久DOIは未確定です。投稿・DOI公開・mergeは行っていません。

## 旧経緯

この更新前の長いPR説明は[全文を履歴ファイルへ保存](https://github.com/zuizui0223/mina/blob/7867969c640e9e1fce627ed0e172e549fb6b4f0f/research/climate-penguin/macro_panantarctic_v1/v07_polynya_20261121/history/PR214_DESCRIPTION_BEFORE_V07.md)しました。既存の凍結解析と旧稿の内容は変更していません。

Latest manuscript commit: 7867969c640e9e1fce627ed0e172e549fb6b4f0f

