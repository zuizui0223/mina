# 3種の将来海氷曝露差は地域間の繁殖分布でどの程度説明されるか

2026-11-17 JST｜mina Draft PR #214｜原CMIP6×原実巣数の追加マクロ物理解析。生物学的巣数予測ではない。

## 分母と推論境界

元のsource-method固定595 known colony site / 2,456真正巣数行から、2011–2020年の**実巣数がある271 site（16原source region）／331 site×species中央値**を使用した。species site数はAdélie 108、Chinstrap 138、Gentoo 85。種別の巣数中央値weightは2,211,900 / 534,727.5 / 101,702。種別・年で非同時に計数されたproxyであり、2020年の全個体群推定でも現在の真のペア数でもない。未調査324 known siteを0巣にしない。

原27 Zarr store・元3 model（ACCESS-CM2、BCC-CSM2-MR、CESM2）・同一3モデル等重み、1995–2014 historical対 SSP5-8.5 2081–2100（8–11月）のsite SIC delta ppを使用。将来の営巣数に換算しない。

地域間・地域内の**算術恒等分解**を次のように定義：同じ271 source siteでregionごとの地点等重み将来ΔSICを m_r とする。各種sの地域の観測巣数proxy比 p_sr を使って、地域間項 B_s = Σ_r p_sr m_r、地域内項 W_s = E_s − B_s、E_s は種別巣数proxyで重みつけたΔSIC。種の差 (E_G−E_A)=(B_G−B_A)+(W_G−W_A) が必ず一致する。m_r は観測がある全source siteの地域平均であって、種の生息適性ではない。「95%は地域間」はこの固定参照方式での**会計寄与**であり、95%の因果・進化的差を地域が生んだという意味ではない。

## 実計数271siteでの結果

| Species | 観測species sites | 種別巣数重みSIC delta（pp） | 地域間構成参照（pp） | 地域内地点差（pp） |
|---|---:|---:|---:|---:|
| Adélie | 108 | −11.256 | −11.300 | +0.044 |
| Chinstrap | 138 | −17.534 | −15.985 | −1.548 |
| Gentoo | 85 | −34.839 | −33.678 | −1.161 |
| Chinstrap − Adélie | — | **−6.278** | −4.686 | −1.592 |
| Gentoo − Adélie | — | **−23.583** | −22.379 | −1.205 |

Gentoo−Adélie差の94.89% (=22.37872/23.58348) は地域別の現在の観測巣数の分布に由来する、という同一source条件下の恒等分解。GentooはAdélieより「海氷の減る地点に計数巣が多く位置する」が、Adélieより低い温暖化適応・繁殖成功という意味ではない。

## 海洋格子距離とモデルによる感度

元3モデルの海洋格子中心まで各site≤50kmという厳格条件で残るのは**158/271サイト**。species site数はADPE63、CHPE93、GEPE37。特にGentooの巣数proxyサポートは **52,176/101,702 = 51.30%** に減る。モデルの50kmは採餌半径ではなく格子と原site点の距離品質である。

| Species | 271全計数site（pp） | 158海洋格子対応site（pp） |
|---|---:|---:|
| Adélie | −11.256 | −10.652 |
| Chinstrap | −17.534 | −15.872 |
| Gentoo | −34.839 | −18.779 |
| Gentoo − Adélie | **−23.583** | **−8.127** |

158でのGentoo−Adélie gapは −8.127 pp = 地域間 −9.096 pp、地域内 +0.969 pp。支援地点を絞ると種別物理曝露差そのものが大きく縮む。

**各3モデルを別々に計算したGentoo−Adélie gap（pp）：**

| 原CMIP6 model | 271site | 海洋格子50km条件 |
|---|---:|---:|
| ACCESS-CM2 | −16.664 | **−0.563** |
| BCC-CSM2-MR | −7.948 | **−0.045** |
| CESM2 | −46.139 | **−23.773** |

271では3モデルとも負、158でも符号はすべて負だが、**158では2モデルの差はほぼゼロであり、モデル平均の−8.13pp差は大きくCESM2に依存する**。これは3モデルの例示的物理差の比較で、CI、将来発生確率、保全リスクの検定ではない。

## 結論／論文での扱い

- **肯定的な計測結果**：種間の将来海氷の平均物理曝露差の大きな部分は、種の現在の計数巣数がどの地域に分布するかを通じて生じる（同じ原本・同じ3モデル・同じ地域参照で再現）。
- **重要な感度**：海洋格子の支持距離を揃えるとGentoo−Adélie差は−23.58→−8.13ppに縮み、3モデル間の一致は弱くなる。
- **不可**：海氷ニッチへの生理的適応、環境が引き起こした増減、future colony nests、保全による救済率、漁業影響・種間競争をこの数字から推測しない。CMIP6近岸cellは実際のGPS採餌領域ではない。
- **主論文**：単一v0.5 biology-firstの主張や4 main figuresを変更せず、supplementの「physical-only source exposure / geographic accounting」に留める。元265長期気候βを使うリスク換算もNO-GO維持。

## Original-source replay

- Python: derive_species_geographic_exposure_decomposition.py。元2456/595 siteを元SHA固定のbuild.pyで再構築し、元CMIP6 full595 artifactsをsite ID×source model×scenarioで接続する。
- GitHub Actions： https://github.com/zuizui0223/mina/actions/runs/43898099948 **SUCCESS**。新しいspecies model/region CSV＋machine JSONと、元の36/4/64 source accounting checksを保存。元source 21,420 CMIP6 model delta rows、3モデルを保持し、原巣数のゼロはゼロとして残す。巣数proxyが地域内すべてゼロの場合はその種の**local nest-weighted meanは未定義**として欠測にし、ゼロ巣を失敗した観測や生物学的な欠測と混同しない。
