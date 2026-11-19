# 南極の島／本土効果：ASI × SCAR 実データ探索の最終判定（2026-11-19）

## 一文の現状

**既存コロニーだけのMAPPPDから、訪問時の非検出を持つASIの196調査地点へ母集団は拡張できた。一方、地理的に比較可能な独立地域は6ブロックで、SCARの「島」ラベルも真の島ではない。島側の繁殖確認率が高い証拠も、島と本土が等しい証拠も得られず、捕食者因果機構は識別できない。**

本書は exploratory outcomes の**後**に作成した出所・感度・推論上限の監査資料である。事前登録済みの検証や独立な追試に置き換えない。**Paper1 / Paper2 / main を変更しない。**

## Source / replay chain

1. **Publisher ASI**: Schrimpf et al., *Polar Biology* (2020) `lynch-lab/Schrimpf_etal_PolarBiology_Occupancy`, original commit `f34545a163ee22eb557ac2cd8c01e219271787aa`, `Raw_ASI_Data.csv` Git blob `b26be882f7a56e77287dbebd897e8762efafe7a3`, `ESM_5.csv` blob `44dfb41e696ed84cba54af356204e39f87561533`. 196 original visited site codes, 1,565 visits, 827 site×season rows, 1995–2017 field seasons. Visit `0`=**not detected**, `1`=present not breeding, `2`=confirmed breeding, NA=not scored; missing is NOT true species absence.
2. **Publisher SCAR ADD coast**: v7.13 high-resolution original BAS shapefile ZIP SHA256 `1e9103e9afaa012b0746eec487c0a473c70834bfc85220f89082e747658aaa66`, EPSG3031. Largest original land-polygon **geographic proxy** used as continental group. All other exact source land features are non-continental polygon proxies, not verified separate islands. Nearest land assignment is disallowed.
3. **Source gate**: Actions [#44511340025](https://github.com/zuizui0223/mina/actions/runs/44511340025) original ASI visit detection panel; [#44512297362](https://github.com/zuizui0223/mina/actions/runs/44512297362) original SCAR 196-site geography; 58 source sites fall off/ambiguous and are **excluded rather than coerced**. 25 mainland source-geometry points, 113 separate land-source points, 58 ambiguous. Six 100km blocks contain both labels.
4. **One explicit post-source exploratory model**: Actions [#44513846995](https://github.com/zuizui0223/mina/actions/runs/44513846995), artifact `14526035124`: `breeding_confirmed ~ separate_source_polygon + C(species) + C(spatial_block_100km) + log2_visits + year_decades`; GLM binomial, site-ID cluster variance; **82 original sites, 1,127 scored site×species×season rows**, six geographic blocks.
5. **Independent fixed-model replay**: repository source-provenance artifact retained, coefficient/OR equal to original workflow values. **No unadjusted row-p should be used for scientific inference.**
6. **Post-result fragility audit, no new model**: `scripts/audit_asi_island_proxy_inference_ceiling.py`, [Actions #44516488503](https://github.com/zuizui0223/mina/actions/runs/44516488503), artifact `14526381026`. Reconstruct fixed 82/1127/6 exactly and report all 6 source block sizes plus observation fractions, without a second ecological effect or new p-value.

## Observed association, limits

- Exploratory site-clustered **OR = 0.7453035**, 95% site-cluster interval **[0.4190, 1.3257]**, descriptive p **0.3171**. Thus **no supported island-side breeding-confirmation advantage**. The interval includes meaningful benefits and harms; **no evidence of equivalence**.
- Across six blocks, raw (unadjusted) noncontinental-minus-continent breeding-confirmation fractions are positive in **2 blocks** and negative in **4 blocks**. The largest block `-25_12` carries **618/1,127 = 54.84%** of source observations. Three blocks each have **1–2 continental site IDs**.
- The single model's leave-one-100km-block-out coefficients remain negative but change from **−0.411 to −0.082**. Omitting `-25_15` brings the coefficient close to 0 (about −0.0816); no stable, generalizable regional magnitude can be claimed.
- Six blocks are too few to treat the 82 sites or the 1,127 site×species×season scores as geographically independent realizations. Site-cluster standard errors do **not** account fully for these correlated regional contrasts. No small-cluster p value or equivalence margin has been preregistered.

## Why this does not test the original predator-refuge causal prediction

- Antarctica is mammal-predator poor relative to many temperate systems, **not predator-free in general** (skuas and other local predators exist). These ASI data do not contain measured predator exposure.
- All South Antarctic sites share the broad lack of native terrestrial mammal predators; there is no within-dataset variation in that treatment. The UK JNCC 1,321 panels are administrative Master-site units, not physical-island matched plots with tested mammal presence/absence. Therefore the difference between two regional observational coefficients would confound taxa, latitude, ocean niche, effort, site history, and mainland geography, not reveal predator causation.
- The ASI source observes detection/non-detection **and** breeding at the visited site, not nest success, fledgling survival, or individual dispersal. A map or a non-detection cannot be made into a source-verified empty nesting patch without a true within-year detection protocol and spatial crosswalk.

## Why this also does not solve postglacial colonization

The original three-geometry crosswalk yielded 25 sites within 1 km of apparent dated GLIMS ice-polygon loss and later-dated SCAR bare-rock polygons on the same SCAR land feature. **Five** of these sites have exact original ASI code and matching coordinates: Jougla Point (78 visits), Py Point (3), Truant Island (1), Sartorius Point (1), Renier Point (6), total 89 visits. The original ASI record window **1995–2017** predates the **2024 rock image year**, so **zero of these visits** is a post-2024 settled/unsettled test. Across the entire ASI, there are **13 observed 0-only→breeding next-season transitions in 11 site codes**, but none among the 25 GIS source candidates. Not a new-rock colonization sample.

**Do not** treat MAPPPD known colony IDs as surveyed vacant options, ASI visit non-detections as true absences, or original GLIMS old−new difference as independently verified newly exposed terrestrial rock.

## New data decision (not a promise of background work)

Public current sources reconfirmed in November 2026:

- [Oceanites MAPPPD v5](https://penguinmap.com/) gives 2025/2026 known penguin **census** records, but not comprehensive repeat *vacant-site surveys*. Adding more positive colony counts cannot repair the missing A/P risk set. Many source families overlap original ASI and MAPPPD.
- [2026 Polar Biology UAV–ground comparison](https://doi.org/10.1007/s00300-026-03484-z) reports 2023/24 observed nests at 12 known colonies, with survey location partly determined by expedition ship itineraries. Useful for count-method comparability, **not** a zero-to-positive survey design of the 25 patches.
- [AADC East Antarctica occupancy](https://data.aad.gov.au/metadata/records/AAS_4518_Seabird_Breeding_Occupancy) has explicit P/A/non-report states but the independent consecutive-season A→P risk-set check previously produced only **one** transition ([prior audit PR #180](https://github.com/zuizui0223/mina/pull/180)). Do not bridge missing years.

### Decision and next meaningful data hinge

**STOP: no causal island-refuge or equivalence result; no postglacial settlement test.** Avoid another p-hunt from the same ASI, JNCC, MAPPPD, or frozen Paper2 source.

Next real-data eligibility check must obtain (1) verified physical landmass identity; (2) temporally dated *ice-covered→bare substrate* patch polygons with before/after source imagery; and (3) repeated **explicitly surveyed vacant patches**, not only registered colonies, with documented surveyed A and P and detection effort. If such data cannot be acquired, freeze this line as descriptive geographical source infrastructure. The existing substantive Paper1 positive within-island concentration remains separate and unchanged.
