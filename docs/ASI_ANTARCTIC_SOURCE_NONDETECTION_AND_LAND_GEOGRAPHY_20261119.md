# 2026-11-19 — Antarctic ASI field non-detections resolve GIS risk-set bottleneck only at the source level

## Current decision

**Do not fit or claim a glacier-retreat → new penguin colony effect using original MAPPPD + GLIMS + SCAR.** We obtained an independent type of biological observation (repeated ASI field visits with *not detected / present / breeding detected*) but the actual historic observations do not join a source-dated newly exposed nesting-patch risk set. Source data are publicly reproducible and the join has been run.

The ASI source creates a different, **exploratory** opportunity: within the Antarctic Peninsula, is a site on a separate mapped terrestrial land feature more or less likely to yield a penguin breeding observation than a site on the largest continental land polygon, conditional on local spatial blocks, species and survey effort? This compares a **land-polygon proxy**, not verified island versus mainland and not predator treatment. Do not label it a confirmed island-biogeographic law.

## Source acquisition

Schrimpf, Che-Castaldo & Lynch (2020), *Polar Biology*, https://doi.org/10.1007/s00300-019-02613-1, published 1995/96–2016/17 raw Antarctic Site Inventory field visits through https://github.com/lynch-lab/Schrimpf_etal_PolarBiology_Occupancy.

Original immutable commit: `f34545a163ee22eb557ac2cd8c01e219271787aa`. `Raw_ASI_Data.csv` Git blob `b26be882f7a56e77287dbebd897e8762efafe7a3`; `ESM_5.csv` blob `44dfb41e696ed84cba54af356204e39f87561533`. The authors' source defines 0=not detected, 1=present, 2=breeding detected, NA=missing; it does NOT claim per-visit 0 is true ecological absence. Original raw rows are 1,565 visits, 196 exact sites, 22 seasons; 827 unique site × season units.

The frozen MAPPPD/GLIMS/SCAR three-source shortlist is still 25 GIS-near-rock sites and not 25 newly occupied patches. The ASI source codes plus WGS84 coordinates match **exactly five** of those original MAPPPD sites (0 m coordinate difference): `JOUG` (Jougla Point; 78 visits, 22 seasons), `PYPT` (Py Point; 3 visits/3 seasons), `TRUA` (Truant Island; 1/1), `SART` (Sartorius Point; 1/1), `RENI` (Renier Point; 6/5). Total five-site 89 original visits / 32 site-seasons.

## Measured visit-state support

Across all 196 original ASI sites, species-by-visit **0=not detected**: Adélie 1,058, chinstrap 891, gentoo 505. For species-by-site-season, observed same-season **0 and 1/2 mixed** records occur for Adélie 82, chinstrap 78, gentoo 75. This makes the point that 0 is a recorded non-detection, not verified absence, empirically visible. Original 0-only consecutive season followed by breeding detected in next season: **3 Adélie, 3 chinstrap, 7 gentoo = 13 observed transitions** among **11 original site codes**, with **435/438/442** evaluated consecutive species-specific site-season pairs. These are not 13 establishment events.

In the **five** original sites matched exactly to our 25-site rock shortlist, there are **zero** such consecutive-season 0-only→breeding observations across all three species. Across all 13 observed 0-only→breeding state changes, **zero fall in the 25 independent three-source rock-proximity GIS candidate site IDs**. One event (`BAIL`, Baily Head) lies in the broader **133** MAPPPD site pilot-rectangle sample but has **no source-supported nearby ice-loss/rock geometry**. No climate or settlement effect fit is justified on these joins.

Source-script: `scripts/audit_asi_glims_rock_candidate_source.py`; original successful GitHub Actions #44511340025, artifact 14524376093. Machine-readable `results/ASI_ORIGINAL_ND_BREEDING_GIS_SOURCE_GATE_20261119.json`. Important: MAPPPD and ASI may partly reuse original field census sources, so they are not guaranteed independent biological samples.

## New, different support cohort: Antarctic Peninsula same-source site geography

With **all 196 ASI visited sites**, the original verified SCAR ADD v7.13 high-resolution land polygons (SHA256 `1e9103e9afaa012b0746eec487c0a473c70834bfc85220f89082e747658aaa66`, EPSG:3031) give:

| Source geometry class | ASI sites | Actual visits | Site-seasons |
|---|---:|---:|---:|
| Exact inside *largest* original terrestrial land polygon (continental proxy) | 25 | 185 | 102 |
| Exact inside another separate original land polygon | 113 | 904 | 480 |
| No unique exact original land-polygon assignment | 58 | 476 | 245 |

This is **NOT** 113 independent oceanic islands. A coastline vector land polygon source row is not an independently validated biological landmass and ice-isolated rock outcrops may be included; no nearest-land imputation rescues the 58 ambiguous sites.

At the independent, outcome-blind **100 km** source geographic grid, **six blocks contain both classes**. Those six shared blocks have **82 source site IDs** (24 continental proxy and 58 separate-land proxy), **758 original ASI visits**, and **384 site-seasons**. The fixed source support gate (≥8 sites/group, ≥5 repeated sites/group, ≥20 site-seasons/group, ≥3 distinct 100km blocks/group) passes both geographic classes. All three Pygoscelis species have scored state observations in both classes. This is enough *for an exploratory observation contrast*; not geographic randomization, causal identification, or physical-island identity proof.

Source-only script: `scripts/audit_asi_ant_island_mainland_source_support.py`; successful original source CI #44512297362 artifact 14524101863. The GIS source audit is based on the unmodified official 7.13 source ZIP and 2020 original authors' raw CSV.

## Single explicit observational model (post-source discovery)

A fixed exploratory GLM was created, **after group and biological ASI state counts had been examined**; therefore no preregistered/holdout or new confirmatory claim is allowed. Unit: independently scored original site × species × season. Response: at least one field visit **observed breeding** (2), otherwise 0 or 1 on recorded visits; NA excluded, 0 is not true absence. Formula:

```text
breeding_confirmed ~ separate_source_polygon + C(species)
                   + C(100km spatial block) + log2(number of visits)
                   + (season_start - 2006)/10
```

Site-clustered sandwich uncertainty (not region-cluster independent); one descriptive leave-one-100km-block-out sensitivity. No other year cutoff, geography subset, covariate, species subset or source threshold will be selected from resulting p-values. This deliberately DOES NOT fit latent detectability or measure rock availability, marine access, predator exposure, or individual dispersal. It is an exploratory geography proxy screen, not an island ecology mechanism result.

Original-source workflow: `.github/workflows/asi-antarctic-polygon-proxy-exploratory.yml`; script `scripts/fit_asi_antarctic_polygon_proxy_exploratory.py`. Do not add a numerical claim to this document until the GitHub Actions artifact has been inspected.

## Why novelty is constrained

- Schrimpf et al. (2020) originally fitted multispecies Antarctic Peninsula detection-corrected occupancy against sea ice. Same raw ASI data reused here.
- Schrimpf & Lynch (2021), *Ibis*, https://doi.org/10.1111/ibi.12910, already found contrasting wind-fetch breeding occupancy associations among chinstrap, gentoo and Antarctic shags.
- Southwell et al. (2020), *Ecology and Evolution*, https://doi.org/10.1002/ece3.6037, already contrasted East Antarctic island-archipelago and continental nunatak habitats: breeding habitat amount/terrain, avian composition and colony density differ.
- True new post-glacial settlement at Point 8, Anvers was published by Cimino et al. (2026), https://doi.org/10.5038/2074-1235.54.2.1707. One prior-art positive case does not validate an Antarctic-wide mechanism.

**Scientific stopping rule:** even if the exploratory area-group effect becomes small or imprecise, that does not demonstrate that islands stop being special when land mammals are absent. Neither true geographic island identity nor independently observed mammalian predation treatment is present; nonconfirmation is not equivalence. To identify the specific 2017 land-exposure→surveyed A/P process, independent original pre/post nest-patch rock imagery and explicitly surveyed vacant patches are still required. No new ecological model is fit for the glacier-retreat question, and main/frozen Paper1/2 remain unchanged.

## 2026-11-19 continuation: one frozen-in-code exploratory contrast (observed source assay)

The previously described one-off binary observational GLM was independently recomputed from the two source-audited GitHub Actions CSV artifacts in the local container (pandas 2.2.3, statsmodels 0.14.6), using the identical model formula as `scripts/fit_asi_antarctic_polygon_proxy_exploratory.py`. This is NOT held-out confirmation or a new author-validated ASI occupancy estimate.

- **Original source frame:** 82 ASI visited sites in 6 both-class 100-km spatial blocks, yielding **1,127** scored site×species×season rows across Adélie, chinstrap and gentoo. Unknown state rows excluded, not coded zero.
- **Observed outcome:** detection of breeding during at least one visit in a site/species/year, not true latent breeding occupancy. `0` from the original ASI is not a detected absence.
- **Single exploratory group coefficient:** log-odds `beta = −0.293963759729`, odds ratio **0.7453035**, site-code cluster-robust descriptive 95% OR interval **[0.4190, 1.3257]**, site-code cluster-robust **p=0.3171**. This is non-confirmatory and cannot establish even the *sign* of an island/source polygon association.
- **Six leave-one-spatial-block-out coefficient values:** `−0.3303, −0.3489, −0.4113, −0.2920, −0.0816, −0.3438`. All are negative but effect magnitude changes; no 6-block inferential p-value or positive ecological explanation can be claimed.
- Source provenance: GitHub Actions **44511340025** ASI site-year CSV SHA256 `44f746cd66727afed648a372eac970669ce8c59570df52c15b41db2d4678acaa`; GitHub Actions **44512297362** SCAR geography CSV SHA256 `62141712b88c4ffa9ce46f0f4d30634147aa44ac0a71cf9145584951f94885e1`. Independent local numerical receipt `results/ASI_SCAR_POLYGON_PROXY_LOCAL_REPLAY_20261119.json`.
- **Important status distinction:** isolated GitHub Actions model validation run **44513846995** is still in GitHub's queue at the time this section was written; do not represent the locally replayed model as a successful final GitHub CI until a completed artifact is verified. Its predecessor run **44513290167** failed due a constant synthetic visit-effort predictor causing singular design covariance; the synthetic test was repaired, not the actual source model.

**Final scientific classification:** source-verified crosswalk and exploratory association, no verified predator effect, oceanic island advantage, land-mammal counterfactual, lack-of-effect equivalence, postglacial settlement or future demographic prediction. Even a much smaller p-value in this site-clustered binary GLM would not fix unverified physical island identity or imperfect detection. A new result with true mechanism requires new independently validated physical landmass and mammalian predator field detection/absence records, or an actual dated ice→rock **candidate survey risk set**, not another radius or species subset of this observational series.
