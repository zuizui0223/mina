# When a breeding platform exists but no emperor penguins are visible: Ledda Bay and a 20-image audit

**2026-10-08 — direct retrospective author-source analysis, PR #195.** This is new explicit source classification and within-site evidence synthesis, **not** a new causal mechanism, confirmed de novo breeding, demographic rescue, or independent ice-satellite validation. PR #189's frozen Ecology manuscript and PR #192/#194's scientific/data gates are untouched.

## 1. Actual original images, not inferred model posterior switches

We opened the original **LaRue et al. (2024) publicly archived XLSX**, pinned GitHub blob SHA `a964360e2cc9bc6303199e0971a4e7d40f793752`. Among **599 original 2009–2018 image observation records** (`yes=502`, `no=20`, `NA=77`), inspected the literal author `comments` field for **all 20 `no`**.

| What original image interpreter wrote about the physical platform | Number of `no` image records |
|---|---:|
| Explicit **no fast ice** or fast ice already broken away | **4** |
| Explicit **fast ice available**, yet `bpresent=no` | **3** |
| Fast ice status **not clearly classified** by original note | **13** |
| Total | **20** |

This is **not** 4 truly ice-free *colony-years* and 3 repeated full-season biological absences without error. These are **dated individual image records**. The image is evaluated by the same annotator who judged bird presence. Fast ice could be ephemeral, inaccessible or already broken later, and a negative image might miss cryptic birds.

Fifteen of the 20 literal `no` records pass the original paper's **basic** date/area/removal conditions; that does not by itself mean all 15 were finally included in every fitting stage. Specifically, `LEDD` 2015-11-13 `no` has `area_m2=0` and was excluded under the authors' no-late-November-zeros rule. `LEDD` 2016-08-25 `no` lies before the Sept–Nov fitting window. The original sheet also contains **one `no` with `area_m2=93`** (`SANA` 2012) and **three `yes` with `area_m2=0`** (`AMUN` 2016, `FOLD` 2018 and `LAZA` 2011); one of these `yes` annotations explicitly states **guano and shadows but no live penguins**. The original Bayesian abundance model uses pixel-area/quality/date observations, not a strict biological three-state occupancy classifier.

## 2. Ledda Bay: physical absence versus no birds with apparently available ice in one 10-year record

The **same author-labeled Ledda Bay colony** on the Amundsen Sea coast is unusually informative because the original notes explicitly report both opposite physical situations.

| Original image date | Bird detection code | Author's physical ice note | Passes basic original fitting screen? |
|---|---|---|---|
| **2009-10-27** | `no` | **no fast ice** | Yes |
| **2010-10-08** | `yes` | historically observed group; measured pixel area 2300.82 m² | Yes |
| **2011-09-23** | `no` | **fast ice available** | Yes |
| **2012-10-22** | `no` | **no fast ice** | Yes |
| **2013-11-30** | `yes` | small group, hand-drawn polygons; 312 m² | Yes |
| **2014-10-13** | `no` | **fast ice available, no birds** | Yes |
| **2015-11-13** | `no` | **fast ice available, no birds** | **No** — late-season zero excluded |
| **2016-08-25** | `no` | **no fast ice** | **No** — August |
| **2017-11-01** | `yes` | lots of fast ice, colony might have held on; area unavailable | **No** — area missing |
| **2018-10-06** | `NA` | possible birds on pack ice, later disappearance of ice | No |

**This record alone disproves the deterministic statement 'every single image without visible birds denotes unavailable nesting fast ice'**, because 2011 and 2014 were original high-quality September/October observations of ice noted as physically present while birds were not detected. Even 2015 records a similar snapshot, though its zero was legitimately excluded from the author's abundance fit.

At the raw-image **annual snapshot** level, all **three** explicit no-fast-ice records were followed by a `yes` image in the next observation year (2009→2010, 2012→2013, 2016→2017), versus **zero** of the three `no` observations annotated as ice present (2011→2012, 2014→2015, 2015→2016). However, one of those three former event pairs **fails** the original fitting date/area screen; **only two pairs pass**. The 2016 August→2017 missing-area pair fails. 2016 August→2017 missing-area does not. These events involve **one site, nonindependent repeated observations, different dates, potentially mobile ice and prior exposure**. There is **no valid general contingency-table p-value, no source of immigrants, and no inferable ice-caused settlement effect**.

Importantly, Ledda was already known to have harbored a small emperor colony in **1999**, and Fretwell et al. (2012) previously observed that early fast-ice break-up prevented high-resolution coincident counts in subsequent years. **Neither early break-up dynamics nor colony persistence at Ledda is newly discovered here.** The new empirical source finding is more limited: **the image-level 'bird absence' class mixes at least two distinct recorded physical situations at the same historically occupied colony**.

## 3. The biological question after this comparison

An observed suitable-looking platform that appears *unused* is not automatically a colony colonization opportunity. Relevant unmeasured explanations for the 2011 and 2014 snapshots include:
- insufficient fast-ice **duration** or poor route between sea, food and nest site despite local visible ice;
- regional penguins being at another part of the breeding site or absent for the imaged day/stage;
- skipping reproduction, seasonal breeding phenology, or observational error;
- natal or social attraction to existing breeding groups, **not directly tested**;
- prey, predation and other site-specific conditions.

This supports a **stronger hypothesis separation** but not preference for any one mechanism. Merely running an occupancy GLMM on `bpresent` against `fast ice available` as coded by the **same satellite annotator** would be circular/biased and lacks independent colonies with matching exposure.

### Next real test, if physically independent rasters can be obtained

The independently published **Fraser & Massom (2020) MODIS version 2.2 fast-ice archive** contains **432 maps at approximately 1 km/15-day resolution** from 2000 to February 2018 (DOI:10.26179/5d267d1ceb60c). Author-maintained [Chad Greene's dataset loader](https://github.com/chadagreene/fast-ice/blob/main/fastice_data_download.m) establishes exact annual file names `FastIce_70_{year}.nc`, with each annual file about **500 MB**. Data grids classify fast-ice pixels separately from continent, island, ice shelf and open ocean. **These annual rasters have NOT been downloaded or independently sampled here**; the full archive is ~7.7 GB, and original Ledda colony coordinates are a rounded centroid rather than the changing breeding footprint. Also note 2014 and 2016 files had documented corrections in version 2.2. 

A predeclared future comparison must extract **local 1–5km neighbourhood ice state and persistence in the 15-day window BEFORE each exact source image**, and inspect 2011/2014 high-quality original negative images versus 2009/2012 ice-loss events while controlling for stage and detection. It must not select the fast-ice pixel location after observing colony guano at the new site. If the physical platform is independently validated but no birds are visible, only then is a genuinely **available-but-unused in that observation** classification strengthened; verifying whole-season emptiness, true first breeding or social choice requires additional data.

## 4. Verdict and provenance

**Supported:** historical Ledda Bay satellite annotators documented **two different mechanisms for a no-birds-looking image**—no physical fast ice in three years, and fast ice apparently present with undetected birds in three other years. Of the latter, **two were high-quality original-fit-window observations**. Other original `no` images do not resolve physical ice state in 13 cases. This distinction is biologically meaningful when formulating breeding-option hypotheses.

**NOT supported:** a statistically generalizable ice-platform-choice law; differential bird preference conditional on externally measured true suitability; a social Allee effect; local colonization after extinction; immigration rescue; post-2022 persistence at formerly vacant sites.

Files:
- `results/EMPEROR_LARUE_AUTHOR_NO_IMAGE_ICE_BIRD_ANNOTATIONS_V1.json` (all 20 source rows, 10 Ledda years and explicit stop codes);
- `scripts/audit_larue_2024_annotation_ice_bird_state_v1.py` (source-pinned reprocessing);
- `tests/test_emperor_author_fastice_birds_annotations_v1.py` and CI reproduction.

Sources: [LaRue et al. 2024 original XLSX](https://github.com/davidiles/EMPE_Global/blob/13f71112da43c1fd082273677757b41c550457ed/data/empe_satellite_2023-05-25.xlsx); [author's original filtering code](https://github.com/davidiles/EMPE_Global/blob/13f71112da43c1fd082273677757b41c550457ed/analysis/script1_PrepareData.R); [Fretwell et al. 2012](https://doi.org/10.1371/journal.pone.0033751); [Fraser 2020 fast-ice data](https://doi.org/10.26179/5d267d1ceb60c).
