# Terrestrial extension synchronization checkpoint — 2026-11-24

Scope: exploratory Antarctic marine-animal/terrestrial vegetation analysis. The user requested GitHub synchronization before further analysis. This public branch is a draft research record, not a submitted or merged manuscript. Earlier Palmer and Shirley records remain unchanged. Do not combine unmatched studies into a causal path or describe geographic support as regional replication.

## Public-source results from local executed archives

### Soil properties in penguin colonies
Iannuzzi, González, Acuña, González, Almendras & Orlando (2025), *Physicochemical parameters of Antarctic soils impacted by Pygoscelis penguins*, DOI [10.5281/zenodo.17742676](https://doi.org/10.5281/zenodo.17742676). [Source acquisition](https://github.com/zuizui0223/mina/actions/runs/45371398914), artifact 14908753735. Publisher MD5: metadata b58d6e6b476c98afeb9f4e75f8f520fe; chemistry fa57915e1d1253a6eeac36e70579ccf9; methods 0a2430c1943387e5369159ea950774f2. Local reproducibility archive antarctic_soil_nutrient_moisture_analysis_20261124.zip SHA256 a700bbfa74523b63a243704806d7e4c05a6ec72fea99fda8675f74f9793fb845.
87 unique paired samples in 29 triplicate groups and 23 named sites, 2019/20/22/23; 184 blank lines in each of the 271 parsed rows removed. Catalogue says 84; retain all 87 matched observations pending author clarification. Species groups 12 ADPE, 11 GEPE, 6 CHPE. No nitrate/phosphate values for 33 samples in 2022/23 (n.d. unknown, not zero). Water dry-mass basis; values above 100% allowed.

| Response | Between-group log-water slope, species/year adjusted | site-bootstrap 95% percentile interval | Within-group slope | site-bootstrap 95% interval |
|---|---:|---|---:|---|
| log organic carbon | 0.700447 | [0.464138,0.933093] | 0.538369 | [0.230762,0.716054] |
| log ammonium | 0.108945 | [-0.384059,0.575568] | 0.114174 | [-0.098262,0.786875] |
| log nitrate | -0.015290 | [-0.325975,0.358838] | -0.012205 | [-0.220902,0.326605] |
| log phosphorus | -0.225293 | [-1.954360,0.407645] | 0.549602 | [0.004070,1.341423] |
| pH | -0.195048 | [-0.473873,0.165988] | -0.306902 | [-0.448425,-0.166321] |

All exploratory. No multiplicity correction; bootstrap 2000 replicates, sampled named sites, no region-level inference. Between-group mean logs, group-centered within slopes. Organic carbon between LOO 0.583668–0.773088, within 0.428220–0.639060. Nine selected point estimates independently reproduced from original data (max absolute difference <2e-15). All samples from colony soil; no control or marine-source isotope, historical exposure, vegetation outcome, or causal climate effect.

### Independent soil–cover survey
Ball (2025), *Exploring the Functional Role of Antarctic Plants during Terrestrial Succession: Fine-Scale Survey*, USAP-DC [10.15784/602015](https://doi.org/10.15784/602015), CC BY 4.0. Workbook MD5 75cc48e8ca21d8b408098a14692e6d3e; SHA256 eabd7171cb700351ee8b6d0df82a5f8bb92ccb8a4076cd55387a9cca8f5fcfbf. Recipient archive usapdc_602015_download_20261124_102759.zip SHA256 1cd33aa0f7342174f9b08da689b91bc870c48413fcf02849c46671e54ee69e3b. Local result archive king_george_soil_vegetation_analysis_20261124.zip SHA256 bc073d0a2230e222800b2368bab8476e5120c5d46b4384303ac1519dedc433b1. 132 unique Site×Stage×Cover×Rep rows, 44 triplicate groups, 9 strata (Collins/Fourcade/Nelson × E/M/L). One row missing most chemistry. 3 sites, selected cover categories not random occupancy or vegetation cover proportion; nonbare includes cyanobacteria and lichens. Supplemental README missing; no unit conversion or exact age inference. No penguin exposure, isotope, sample coordinates or repeated time observations.

| Soil response | nonbare/bare geometric mean ratio | positive strata/9 | moss-only/bare ratio |
|---|---:|---:|---:|
| Swc | 1.825176 | 8 | 1.901887 |
| OrgC | 4.814572 | 9 | 5.292938 |
| TotalN | 3.670318 | 9 | 3.860106 |
| Ammon | 3.712994 | 8 | |
| Nitr | 1.184371 | 7 | |
| Phos | 1.176695 | 7 | |

All three moss-only contrasts positive in 9/9 strata. Average log measurements within cover, equal nonbare cover-type weights within site-stage, equal weights across 9 strata. Moss labels Polytrichastrum, Sanionia, Bryum, Syntrichia, Bartramia. Between-group OrgC log-water slope adjusting site×stage and cover 0.891757 (44 groups; site deletion 0.779075–1.301843); within group 0.857772 (131 observations, equal group weight; site deletion 0.850496–0.886118). TotalN between 0.712667, within 0.802306. Separate within-group OrgC slopes bare 0.557, moss 1.094; descriptive not a tested difference. Secondary nematode water×total N interaction 0.0825; site deletion -0.021 to +0.548, not supported robustly. Independent contrast and within-group centering checks passed. No formal cross-study meta-analysis or causal plant effect. Source title and aims already encompass plant–soil links; reanalysis is supporting evidence, not a new mechanism.

### Published radiocarbon spatial-support diagnostic
Emslie (2026), DOI 10.1017/S0954102026100807; Emslie & Woehler (2005), DOI 10.1017/S0954102005002427. Original Plantarctica DOI 10.6084/m9.figshare.24745956; SHA256 7e304e7a610d03287577e91faff05c009cf82039ae5f227763c37730a548a236. Ross 43 georeferenced age records/24 locations, Windmill 40 ages/13 dated locations. Manual table transcription, 2005 PDF screenshot validation failed: check tables before publication. Mapped plant detection at 50m: 0/24 and 0/13; at 100m 0/24 and 1/13; at 250m 0/24 and 3/13; at 1km 16/24 and 12/13. Large buffers share features. Dated material is not date of abandonment; no age effect fitted, no inference of plant absence. Known Robinson Ridge ground monitoring map extent (AADC Map 14451, 10371 m² projected rectangle) had no overlapping mapped plant features, not a sensitivity estimate. Local ross_windmill_dated_colony_audit_20261124.zip SHA256 404cae0e9218cf46dfacb7917a689cef8395f28e9be62ba62d81a65d6734591f; no transcribed source tables republished.

## Held from public synchronization
The following packages exist locally, with original-derived data/results kept out of the public branch until release terms and custodian consultation are clarified. Repository is public. AADC 2012/13 seabird archive has CC BY 4.0 but an attached SCT policy requests prior communication and restricts external redistribution; archive citation says Unreleased data. AADC fixed quadrat archive also says Unreleased data despite CC BY notice. No files, restricted-source values, coordinates or polygons uploaded from these packages. Hash-only inventory (local artifacts, not GitHub download paths):
- windmill_colony_vegetation_comparison_20261124.zip SHA256 2ceb62aa158299b731d59dc7288ae78121d1929bfb7c7e91ab147dc24fff365b
- windmill_vegetation_validation_20261124.zip SHA256 e900ec0caf9ed687c84d61925aafb6fbb65431215086f0d6e03d2089a7b6683b
- windmill_ground_moisture_analysis_20261124.zip SHA256 409ce707392997381f4a27c72baa592c511884ed45e89abd2b382975fc552495

## Next prespecified gate
Organic carbon–water co-variation appears in two separate sampling designs. It is not evidence for marine animal → organic carbon → water → plant mediation. Next test whether organic carbon accounts for soil N–water associations conditional on site-stage and cover, then independently test matched moss N/relative water traits only if source unit and join key support exists. USAP 602039 plant nitrogen and 602038 thermal traits are separately described samples, not assumed paired. Clements et al. (2026), DOI 10.1007/s00300-026-03502-0, already studies moss N gradients and hydration; do not present that association itself as novel.
