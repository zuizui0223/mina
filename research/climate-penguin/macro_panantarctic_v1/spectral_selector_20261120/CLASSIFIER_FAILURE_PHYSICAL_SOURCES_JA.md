# 固定L7分類器の後年回収低下：物理的解釈の根拠と限界

確認日2026-11-20。USGS/NASA一次資料と固定モデルの係数を確認した。モデル・閾値・既存成績は変更せず、新たな分類成績・生態応答は計算していない。

**後年の回収低下は、固定分類器が後年の原著陽性の分光分布へ十分移植できなかったことを示す。食性変化、大気補正の失敗、混合率変化のどれかを、この結果だけで特定できない。** 以下は説明候補を区別するための根拠であり、失敗原因を確定したものではない。

## LEDAPSと極域のSR

Landsat 4–7 C2 SRはLEDAPS、L8/9はLaSRCで、同じ大気補正処理ではない。USGSの**L4–7専用**C2 guide §2.1は、高緯度、低太陽高度、雪域、小さな陸地を水面が囲む沿岸でSRの不確実性が高まるとする。SR生成の太陽天頂角上限は約76°（高度約14°）。原著の高度15°以上というscene条件を満たしても、極域SRの精度保証にはならない。[USGS C2 SR](https://www.usgs.gov/landsat-missions/landsat-collection-2-surface-reflectance)、[L4–7 C2 guide v4 §2.1, pp.5–6](https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/LSDS-1618_Landsat-4-7_C2-L2-ScienceProductGuide-v4.pdf)

L8/9 LaSRCについて公表されている雪氷上のAOT inversion失敗を、L7で実証された原因として引用してはいけない。また、SRを使った本分類器の学習・評価内では両期間とも同じC2 SR規約を用いており、「原著がTOAだから」という事実だけでは期間差を説明しない。TOA由来の元陽性ラベルとSR特徴量の違いは、ラベル移植の限界として別に残る。[USGS Known Issues](https://www.usgs.gov/landsat-missions/landsat-collection-2-known-issues)

## QA通過が保証しないもの

現抽出はL7 QA_PIXELのfill/dilated cloud/cloud/shadowと、6反射帯域の飽和・dropped pixel・nodataを除外する。雪と水は保持し、4寄与画素が全て通る場合だけ平均する。この規約では、雲bitがOFFでも中・低confidenceの雲や薄雲が完全に排除されたとは言えない。USGSは明るい雪氷、温度差、薄雲による検出限界を記載している。SR_ATMOS_OPACITYも未検証の補助品質情報であり、真の大気誤差の測定値ではない。[L4–7 C2 guide Tables 5-5/5-7, §§5.1.2,5.2.1](https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/LSDS-1618_Landsat-4-7_C2-L2-ScienceProductGuide-v4.pdf)

既知のL4–7水域QA「Clear bit 6」不整合は、bit6単独に依存しない現コードの直接的なバグとはいえない。現コードは推奨されるbits1/3のOFFに加えてshadow等も除く。雪/海/その他という区分はQAに基づく仮区分で、4画素平均の真の被覆率ではない。[USGS QA known issue](https://www.usgs.gov/landsat-missions/landsat-collection-2-known-issues)

## SLC-offの境界

L7のSLCは2003-05-31に故障し、通常scene面積の約22%が楔形に欠ける。学習の1999–2002繁殖季節（暦年2003初頭を含み得る）は故障前、2008–2012評価は故障後である。[USGS SLC-off technical publication](https://www.usgs.gov/publications/landsat-7-scan-line-corrector-gap-filled-product-development)

ただし、**C2 L7 SR生成ではギャップを埋めず、欠けた部分にSRを生成しない**。現処理も4画素の有効性を要求する。したがって「SLCギャップを平均で埋めたためSWIRが変わった」という説明は現手順に合わない。SLC-offは評価に残る位置・撮影日・地表条件の選択を変え得るが、それは有効画素の一律な放射誤差とは別。QAで除外された群と、QA通過後に分類を落とされた陽性を混同しない。[L4–7 C2 guide §2.1 item 5](https://d9-wret.s3.us-west-2.amazonaws.com/assets/palladium/production/s3fs-public/media/files/LSDS-1618_Landsat-4-7_C2-L2-ScienceProductGuide-v4.pdf)

## SWIR1とSWIR2の係数が示す範囲

L7 Band 5（SWIR1）は1.55–1.75 µm、Band 7（SWIR2）は2.09–2.35 µm。B5は水分や雪/雲の識別にも使われ、B7とB5/B7の違いは鉱物・地表組成にも反応する。したがって両帯域の対比は糞・食性に固有の化学指標ではない。L8では帯域幅も異なる。[USGS band definitions](https://www.usgs.gov/faqs/what-are-band-designations-landsat-satellites?qt-news_science_products=0)、[USGS spectral applications](https://www.usgs.gov/faqs/what-are-best-landsat-spectral-bands-use-my-research/?items_per_page=6&page=0)、[USGS NDSI](https://www.usgs.gov/landsat-missions/normalized-difference-snow-index)

固定`matched_center_frozen_model.json`のモデルは `logit(score)=b+Σ βj (SRj−μj)/sj`。他帯域を固定してSRを0.01増加させた場合のlogit変化を係数から計算すると次のとおり。これは**モデルの代数的感度**で、実際に生じた分光変化や確率変化ではない。

|帯域|標準化係数β|0.01 SR増加に対するlogit変化|
|---|---:|---:|
|Blue|−0.427|−0.0183|
|Green|−3.598|−0.1637|
|Red|−2.031|−0.0922|
|NIR|+5.692|+0.2941|
|SWIR1|+15.601|+1.2472|
|SWIR2|−12.105|−1.4997|

SWIR2が相対的に増す、あるいはSWIR1が相対的に減る変化は固定scoreを下げる方向となる。ただし帯域は相関し、係数の大きさ・符号は他帯域を条件とした分類境界を表す。βの絶対値を「その物理原因の重要度」と読まない。全帯域が共に変われば寄与は相殺も増幅もする。scoreは陽性と抽出背景を均衡化した学習に基づくため、校正された現地の糞存在確率ともみなさない。

## 分光寄与分解でできる診断・できない推論

固定モデルなら、同じ比較・同じ重みで `Δlogit=Σ(βj/sj)ΔSRj` と分解できる。どの帯域の**観測された変化がscore低下に寄与したか**は記述できるが、なぜその帯域が変わったかは識別できない。これはlogitの加法分解であり、確率の平均差・閾値通過率の差・medianの差をそのまま足し合わせる式ではない。

30m支持範囲には糞以外の岩・水・雪・陰影が混ざり得る。一定地点でも被覆・水分・照明・観測時期・QA選択が変われば分光分布は変わり得る。線形混合を仮定しても、endmemberスペクトルと独立被覆率がないため「SWIR寄与の何%が糞、何%が岩」という逆推定はできない。広帯域6値と分類ラベルだけでは食性、基質混合、大気残差の効果は同定できない。

既存結果を読む際は、固定モデルの失敗を保ちつつ、同地点・同季節時期の比較、太陽角・QA・有効支持の分布、SWIRの共同変化を**失敗原因の候補を絞る記述診断**として扱う。得られた寄与を使って閾値や帯域を調整すれば新しい方法開発であり、今回の固定検証の成功には書き換えられない。本ノートでは追加診断を実行していない。
