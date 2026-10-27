# Original UK island invasive mammal probability SDM — V40/V41 scientific result

**Date 2026-10-27 | \`mina\` PR #201 | Independent first-party original-data predator spatial macroecology, separate from closed JNCC seabird island-refuge H2 test and the frozen Ecology submission.**

## What was actually built

- First-party 2014 RSPB \`UK Islands\` ArcGIS POINT dataset, exactly **9,688 original island \`lowid\`** records, SHA-backed metadata and source provenance; 2017 Stanbury et al. original island-by-mammal spreadsheet ESM5 SHA256 \`3d876a92e68122f8594b320e0794a54c5e8c7306c5a0e6252cbc24776ce1d1c5\`; original lowid matches 9,688/9,688. None of these source island POINTS is itself the exact physical coastline polygon or surveyed animal burrow.
- Source-period conservative size cohort: **506 original UK islands with low-tide area >10 ha**, excluding **9,182** much smaller original entries from SDM fitting (their numerous seemingly confirmed large-mammal labels and weakly known survey denominator require independent source adjudication).
- Four independent source-record labels: American mink, brown rat, house mouse, feral/free-roaming domestic cat. Literal statuses \`1 confirmed\`, \`2 probable\`, \`3 possible/incidental\`, \`0 assumed OR known absent\`. The target combines \`1/2\` versus \`0\`, excludes \`3\` from training and labels that class as unresolved on the map. The reported model probabilities **do not quantify actual island occupancy**.
- Per-species logistic \`StandardScaler + LogisticRegression(C=1)\`, fixed predictors \`log1p(original low-tide island area)\`, latitude, longitude, \`log1p(2014 human residents)\`, and binary **source-listed** ferry access. All source predictors are independent of the JNCC seabird population response; however Stanbury assessments themselves may have used area/access and geographic assumptions.
- Probabilities for each of 506 source island points × four species (**2,024 rows**) with geographic (199-block-bootstrap) model-instability p05/p95, 506-island GeoJSON, four static species maps, exact source and model QA JSON.
- Spatial generalization validated first across **heldout 1-degree geographic cells** (V40), then across **26 original RSPB archipelago/location groups** (V41). Both use five-fold independent group blocking and same fixed GH logistic specification, no post-hoc tuning to rescue a species.

## Real source-label-model predictive evidence

Improvement is the reduction in heldout Brier score **versus training-source prevalence-only baseline**. It measures prediction of the ORIGINAL published 2017 record category, **not** actual ecological occupancy or seabird predation.

| Species | Confirmed/probable source label among 506 | V40 heldout 1° block Brier gain | V41 original archipelago heldout gain | Scientific interpretation |
| --- | --- | ---: | ---: | --- |
| American mink | 113 (source code 3: 3) | **−0.01582** | **−0.01655** (fold group support also fails) | Published labels not reliably transferred even to other source groups. No physically portable mink occupancy map claim. |
| Brown rat | 106 (code 3: 6) | **+0.06904** | **+0.05846** | Source record label predictability transfers better than source prevalence; original status 0 still not field-surveyed negative. |
| House mouse | 96 (code 3: 13) | **+0.11295** | **+0.11429** | Published labels are spatially predictable in both holdouts. |
| Feral cat | 84 (code 3: 13) | **+0.11435** | **+0.11783** | Published labels are spatially predictable in both holdouts. |

5%-median-95% quantiles of **full-original-sample fitted source-label probability across the 506 island points**, not field occupancy:
- Mink: **0.071 / 0.228 / 0.397** (nonportable).
- Brown rat: **0.027 / 0.085 / 0.909**.
- House mouse: **0.011 / 0.033 / 0.991**.
- Feral cat: **0.0035 / 0.0072 / 0.997**.

Source-only bootstrap intervals are **model parameter geographic-block resampling** with 199 runs, not Bayesian probabilities of actual mammal presence. A 95th quantile near 1 may be driven by original documented human-population-linked source labels. A high fitted value cannot prove an island has an invasive predator; a low fitted value cannot certify an island is predator-free.

## Interpretation and novel ecological questions

**Supported here:** a verified public *spatial model of published mammal assessment labels*, with substantially different generalizability by taxon. In the original records, rodents/mice/cat labels have reproducible geographic and human-access signals, whereas mink labels are not transportable between island groups using these fixed predictors. These results can inform hypotheses about human introductions versus swimming/fragmented predator histories, but **cannot distinguish those mechanisms** because original published source statuses may encode presumed island accessibility or reporting effort.

**Not yet supported:** true biological island occupancy probabilities \`Pr(z_i=1)\`, climatic fundamental niche, invasion hazard, dynamic colonization/extinction rates, true prey vulnerability, seabird demographic predation effect, source predator-free island refuge causal contrast, or current-2026 predator distributions. The source inventory is not contemporary and no two-census JNCC predator/colony causal fit was made.

## Why reporting probability cannot automatically be converted to actual mammal presence

Let \`z_i\` be latent true predator occupancy and \`Y_i\` the record-positive label. Even a simplified binary non-detection model would have:

\`Pr(Y_i=1)=Pr(z_i=1)Pr(Y_i=1|z_i=1)+Pr(z_i=0)Pr(Y_i=1|z_i=0)\`.

With only one heterogeneous original label whose \`0\` mixes assumed and known absence, actual occupancy prevalence, island-specific survey sensitivity and false-positive rates are not separately identified. Worse, documented status \`2 probable\` is itself inferred rather than a direct repeated detection. Model calibration against Y is **not** calibration against actual z. Therefore no arbitrary linear conversion from source probability to \`Pr(z=1)\` is defensible.

## Next **independent animal-observation source** to estimate real ecological occupancy

- UK Marine Strategy invasive mammals assessment at island SPAs has **42 SPA groups**, 13 with confirmed or suspected invasive mammals and 29 without (as of source assessment). This is potentially informative for actual field/biosecurity status but **group-level summary is not independently verified island×species×visit data**. It cannot be joined to source lowid as 42 perfectly surveyed single islands without original island identity/effort records.
- Mammal Mapper (The Mammal Society / NBN via GBIF DOI 10.15468/mjw32e, latest publisher refresh 2026-09-07) contains independently verified UK mammal sightings; survey effort GPS tracks are reportedly **stored separately**. The occurrence archive alone cannot serve as repeated non-detection histories.
- A true dynamic ecological island occupancy SDM requires original survey trap/raft/camera deployments with island IDs, effort and repeated detections/non-detections (including verified zeros), true positional accuracy, survey year (1998–2021 if joining JNCC), and independently mapped original habitat and coast/water-gap access. Then separately estimate latent \`z_{i,p,t}\`, survey detection \`p_{i,p,t,v}\`, and covariate effects with a region/archipelago-blocked validation rather than training on assumed absences.
- Original site source 2014/2017 labels are now used **only** to generate prior/screening source-label *propensity* maps; avoid incorporating those predictions as verified predator-free status in frozen JNCC V36 or attributing the seabird V37–V39 size-turnover results to predation.

## Reproduction and artifacts

- Contract: \`contracts/JNCC_UK_PREDATOR_SOURCE_PROBABILITY_SDM_V40.md\`
- Script: \`scripts/map_jncc_uk_island_predator_sdm_v40.py\`
- Synthetic tests: \`tests/test_jncc_uk_predator_source_sdm_v40.py\`
- Original-data run: https://github.com/zuizui0223/mina/actions/runs/40461670193
- Four-species 2,024-probability CSV, 506-island GeoJSON, calibration numeric JSON, four PNGs (GIS points, no fake ocean interpolation): https://github.com/zuizui0223/mina/actions/runs/40461670193/artifacts/12714872313
- Compact pinned V40 result: \`results/JNCC_UK_ISLAND_PREDATOR_SOURCE_LABEL_SDM_V40_RESULT.json\`
- Additional independent archipelago-heldout robustness: https://github.com/zuizui0223/mina/actions/runs/40462552039
- Compact pinned V41 result: \`results/JNCC_UK_PREDATOR_SDM_ARCHIPELAGO_TRANSFER_V41_RESULT.json\`
- Both branches remain research/DRAFT; frozen Ecology Paper1 #189, South Antarctic original macro #197/#199 and JNCC V30 #198 are unchanged.
