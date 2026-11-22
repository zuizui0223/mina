# Emperor penguin × DEEP-AA persistent coastal polynya: frozen primary screening (2026-11-22)

**Status: completed / prespecified positive prediction not supported.** The independent empirical run passed official DEEP-AA MD5 and LaRue raw Git blob SHA and produced 500 outcome×year joined rows; 450 eligible after the 2012 seasonal data gap. This file records the frozen primary result. Do not rewrite it in response to later exploratory tests.

Official empirical run: https://github.com/zuizui0223/mina/actions/runs/45018808042

## Frozen main test

- Outcome: LaRue et al. 2024 **modeled** spring attendance/abundance index `N_mean` from 50 emperor colonies, 2009–2018.
- Exposure: 100 km mean April–August area, DEEP-AA `SIC60_6.25km_20d.zip`; only **positive even ID** coastal-polynya pixels. Index/LatLon were verified.
- Model: colony and calendar-year fixed effects; 8 sea-ice-regions as the cluster units.
- Eligible site-years: **450** (2009, 2010, 2011, 2013–2018). 2013 had 149/153 days (97.39%) and was eligible under the frozen ≥95% coverage rule.
- Standardized within-FE beta: **+0.01827168** on log1p index per within-FE SD log1p polynya area.
- Region-cluster SE **0.04531691**, t-based 95% CI **[−0.08888578, +0.12542914]**, t p **0.69883**.
- Exact 8-region signflip count 256, p **0.6640625**; locked primary decision **frozen_hypothesis_not_supported**.
- Region×year FE: beta **+0.02248224**, 95% CI **[−0.08908189, +0.13404637]**, cluster p **0.64822**, signflip p **0.578125**.
- One-region-out: effect changed sign when the West Indian Ocean region was excluded (**−0.01042334** per log-unit area). Therefore the predeclared all-positive LORO gate also failed.

## Spatial sensitivity — independent local statsmodels replication (same observations and region t correction)

| Radius | Colony+year beta per within SD | region-cluster t p | Colony+region×year beta |
|:--|--:|--:|--:|
| 50 km | +0.0876 | 0.1534 | +0.0871 |
| **100 km (frozen main)** | **+0.0183** | **0.6988** | **+0.0225** |
| 200 km | −0.0074 | 0.8508 | −0.0088 |

- Omitting 2013: primary radius β +0.0217, p 0.6761 (400 colony-years).
- Removing N_mean=0 rows: β +0.0037, p 0.8649 (438 observations).
- Mean LaRue posterior uncertainty is material: median `N_se/(N_mean+1)` = 0.3085; 90th percentile = 0.5786. Full posterior draws should be propagated before paper-grade uncertainty claims.

## Interpretation limits — no biological absence inference

Lin et al. (2024) DEEP-AA algorithm excludes open-water sequences shorter than **20 days** and those with maximum area **<100 km²** from the identified-polynya category. It still records other open water as `Map==-1` and open ocean as `Map==-2`. Consequently, this screen tests persistent relatively large coastal polynyas, **not short-lived leads/cracks or actual measured accessibility**; see https://pmc.ncbi.nlm.nih.gov/articles/PMC11408600/ .

Labrousse et al. (2019) tagged emperor penguins using small ephemeral openings near the fast-ice edge rather than the centers of large recurrent polynyas: https://doi.org/10.1029/2019GL084347 . The null for persistent-polynya area does **not** falsify ephemeral-water use.

Further test of `Map==-1` 50km is explicitly post-hoc and separately frozen under `contracts/EMPEROR_EPHEMERAL_ACCESS_EXPLORATORY_V1.json`. Neither result is a species-wide causal inference or a direct cross-species replication of the Adélie isotope finding.
