# 凍結：SCAR真正同位体原データのペンギン・地点・採集年の独立支持ゲート

2026-11-21 JST | Draft PR #214 | **測定された同位体Yを回帰・比較する前に固定**。

## 唯一の目的
2026年に公開された SCAR Southern Ocean Diet and Energetics Database (DOI 10.5281/zenodo.20047874) の `scar_isotopes_mv.csv` に、旧Youngflesh 2004–2010の88光学糞地点近傍、または独立な2013–2021の期間について、**原研究が実測したペンギンbulk δ¹⁵N**の独立した地点×採集年がどれだけあるかを照合する。SCAR総安定同位体記録数32,925は全分類群の行数でありペンギンの独立反復ではない。

出典は SCAR 原公開Zenodo 20047874 の `SCAR_Diet_Energetics.zip`、出版社によるZIPサイズ **9,543,574 bytes**、MD5 `5e098c268ce0028704bc4b06300cb0ef`（既存の原資料検証済み workflow と同じ）。ZIP CRC, `scar_sources.csv`, `scar_isotopes_mv.csv`を確認する。SCAR原CSVをGitHubへ再配布せず、集計したmetadataとMD5/SHAのみ保存。

## 固定する集計とソース品質
1. Taxon は source `taxon_name` の `Pygoscelis adeliae`, `P. antarcticus` / `P. antarctica`, `P. papua` のみ。`measurement_name`が厳密にbulkの`delta_15N`を表すものに限る。Pheなど個別AAの値やδ¹³C、体重を混入しない。`measurement_mean_value`が数値でなければ除外。
2. `source_id`は研究出典、`taxon_sample_id`は元サンプルに対応する。長形式の測定行数・独立site×year・研究数・サンプル数を区別。secondary data = Y、quality flag Q は独立検定の候補から除外するが除外数を保存。原`measurement_method`、tissue/material等の列名と値域は原sourceから監査し、羽毛/血液/糞を統合しない。原著のYoungflesh/Michelsonと同じ元sourceは独立研究扱いしない。
3. 元source `west,east,south,north` bboxの測地的な水平対角幅が**25km以下**、南緯55度以南、日付`observation_date_start/end`が同一11月–2月繁殖季にあり期間122日以内のものを位置・時期の最も厳しい候補とする。採集日付≠羽毛形成日、採集地≠採餌域であることを保持する。
4. 凍結した元光学糞88 source-site centroid `spectral_selector_20261120/source_sites.csv` とのWGS84最短距離で**2/10/25km**の地理対応と次点地点を記録。25km以内複数地点候補を勝手に一つの繁殖地へ割り振らない。25km一致は**地理的近接**でありsource colony identityを証明しない。
5. source study×species×source locality×採集年を独立支持の上限単位として計数する。同一source_id・同一年の複数同位体測定と長形式行を独立サイトにしない。元2004–2010、独立2013–2021の結果を別々に報告。観察機会のない場所をゼロ個体扱いしない。

## 独立の機構検定への昇格条件（後から変更しない）
- 20以上の厳密な採集繁殖地×一致する同位体測定期間、少なくとも5 source study/location、3独立region、4独立winter。さらに同位体に対応する**実際の採餌・換羽ウィンドウ**の特定が別途必要。
- 古い光学糞値と同じ観測を「別研究」の独立追試と呼ばない。上の必要条件のどれかがNGなら `NO_GO_SCAR_INDEPENDENT_ISOTOPE_POLYNYA_TEST` として**どのY対ポリニヤ回帰も行わない**。
- 生物量、餌割合、栄養段階、食性変化、海氷適応をbulk δ15Nの大小だけから主張しない。Pheの同位体基線不明を保留する。元主論文・main・凍結Ecology Reportは変更しない。

実装：原アーカイブを GitHub Actions 上でMD5照合し、地理/年/出典の **source-only gate** を先に実施する。新しい正負の生態学的効果を出すための閾値・半径・時期探索はしない。
