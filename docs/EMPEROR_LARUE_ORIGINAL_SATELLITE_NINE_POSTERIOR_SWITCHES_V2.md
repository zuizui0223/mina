# Nine inferred emperor colony "returns" versus the original satellite records: observed state or model interpolation?

**2026-10-08 | Retrospective source-backed audit; PR #195.** Not a new ecological colonization result, no post-2018 biological outcomes and no new model fit. The source original workbook was inspected directly by exact GitHub blob SHA `a964360e2cc9bc6303199e0971a4e7d40f793752`; result receipt is `results/EMPEROR_LARUE_RAW_SATELLITE_TRANSITION_SUPPORT_V1.json`.

## What the source actually contains

Authors' original [satellite observation workbook](https://github.com/davidiles/EMPE_Global/blob/13f71112da43c1fd082273677757b41c550457ed/data/empe_satellite_2023-05-25.xlsx), LaRue et al. (2024), has **669 observation rows overall**, and **599 rows dated 2009–2018** in its `site_id`, `img_year`, `bpresent` fields.

Across the 599 period-specific rows:

| Literal original `bpresent` | Number of observation records |
|---|---:|
| `yes` | **502** |
| `no` | **20** |
| `NA` | **77** |

These are **image-observation records**, not 599 distinct colony-years or count-confirmed breeding attempts. `no` mixes no penguins with **no breeding fast ice** according to the original author codebook. `NA` can reflect no usable image.

**Prior-art check on the ecological phenomenon:** LaRue et al. (2024) explicitly listed temporary colony "vanish and reappear" episodes as one of the population processes their model sought to accommodate (Dryad README, "Model overview", point 2). Thus documenting apparent annual disappearances is **not a new biological phenomenon**. Our audit instead narrows exactly which of those *model transitions* were observed by original imagery and which can be used for a **different** physically-available-yet-unoccupied refuge hypothesis. No social-fidelity or competition mechanism is inferred.

## Match each of the nine already-opened posterior mean 0→positive switches

Published model summaries, [50 sites × 2009–2018](https://github.com/davidiles/EMPE_Global/blob/13f71112da43c1fd082273677757b41c550457ed/analysis/output/model_results/3_Colony_Level/colony_summary.csv), include exactly nine transitions `N_mean(t)=0; N_mean(t+1)>0`. Directly matching their original image records:

| Model site | Model transition | Raw preceding year | Raw next year | Critical interpretation |
|---|---|---|---|---|
| Amundsen Bay (`AMUN`) | 2010→2011 | `no` (Oct 8) | `yes` (Sep 27) | Observed detection changes, but prior ice availability unknown |
| Amundsen Bay | 2012→2013 | `no` (Sep 10) | **`NA`** (no usable image date) | Modeled positive despite next year **unobserved** |
| Lazarev (`LAZA`) | 2011→2012 | **`yes`**, measured guano area 0 (Sep 20, quality 1) | `yes` (Sep 26) | Model zero despite **birds already recorded in prior raw image** |
| Ledda Bay (`LEDD`) | 2009→2010 | `no` (Oct 27) | `yes` (Oct 8) | Direct detection change, biological availability not checked |
| Ledda Bay | 2012→2013 | `no` (Oct 22) | `yes` (Nov 30) | Direct detection change, no confirmed independent physical refuge |
| Ledda Bay | 2014→2015 | `no` (Oct 13) | **`no`** (Nov 13) | Model positive but next image still `no`; November zero **excluded by author's analysis rule** |
| Mertz (`MERT`) | 2010→2011 | `no` (Oct 2) | `yes` (Oct 11) | Direct detection change, not proof of new breeding |
| Rupert Coast (`RUPE`) | 2016→2017 | `no` (Sep 13) | `yes` (**Dec 11**, image quality missing) | Positive raw image **outside author September–November fitting window** |
| Umbeashi (`UMBE`) | 2012→2013 | `no` (Sep 27) | `yes` (Oct 12) | Direct detection change; true habitat availability and breeding unresolved |

**Audit counts (9 model 0→positive cases):**
- preceding raw status = **8 `no` / 1 `yes`**;
- following raw status = **7 `yes` / 1 `no` / 1 `NA`**;
- literal raw `no→yes` transitions = **6**;
- only **5** of those six have positive-year images inside the author-defined September–November window with nonmissing penguin area, **before checking additional removal flags**;
- **3/9** modeled transitions are visibly discordant with a simple `no→yes` reading (Lazarev 2011, Ledda 2015, Amundsen 2013);
- **0/9** have independently verified *physically available ice plus repeated whole-site surveyed absence* and newly confirmed breeding from this publication alone.

The [original author processing code](https://github.com/davidiles/EMPE_Global/blob/13f71112da43c1fd082273677757b41c550457ed/analysis/script1_PrepareData.R) explicitly excludes apparent zero satellite areas **at/after November 1**, and its survey window ends November 30. Accordingly, Ledda's **Nov 13 2015 `no`** was not an eligible fitted zero; Rupert's **Dec 11 2017 `yes`** fell outside the fitted window. The **2013 Amundsen `NA`** source row was not usable evidence for that year's positive latent abundance. All nine retain possible contribution from other aerial records or the Bayesian temporal abundance process; this is **not a fault in the original abundance inference**, but a strict limitation on ecology of new site founding.

## Ecological conclusion: why this is stronger than a methodological caveat

The proposed novel mechanism was *physically available but socially unoccupied habitat* versus *movement into an already occupied colony*.

These are three biological states, not two:
1. **Ice unavailable** — the platform does not exist or cannot support breeding (a physical constraint).
2. **Ice available, bird absent** — a genuine vacant option (requires independent ice and a high-quality negative survey).
3. **Ice available, birds nesting** — actual breeding expression, which requires stage-matched reproductive evidence, not simply guano pixels.

The original `bpresent=no` **collapses states 1 and 2**, while apparent model `N_mean=0→positive` can occur even when the raw observation is `yes→yes`, `no→no` or `no→NA`. Therefore the nine model returns **cannot serve as nine confirmed colonizations**, and none adjudicates social attraction over physical-access failure. The strongest biological takeaway is **that observed colony attendance, ice-platform availability and reproductive establishment are genuinely different variables**; their conflation would produce a false apparent source-retention/rescue mechanism.

The original JAGS model's `z_occ[s,t] ~ dbern(prob_occ)` has no occupancy state dependence or explicit detection model. So its year-to-year zero switches are **statistical summaries**, not individual settlement transitions. A genuine ecological contrast needs multiple independent surveyed negative images **while ice is independently present**, followed by positive breeding evidence and persistence.

**Decision:** stop trying to infer novel occupied-versus-vacant founding from this source's nine posterior changes. A public archive with joint physical ice observations and repeated stage-resolved occupancy at the *same patch* is needed before any new cause can be tested. Treat the 2009–18 study and 2024 redetections as already-published descriptive controls; do not retrofit them into a prospective 2022–24 natural experiment.

## Reproduction and assurance

- Raw audit script: `scripts/audit_larue_original_satellite_image_support_v1.py`, pinned to exact author XLSX Git blob.
- Reproducibility test: `tests/test_larue_original_satellite_image_support_v1.py` includes synthetic XLSX parsing and source integrity/interpretation guards.
- GitHub Actions `.github/workflows/emperor-colony-evidence-v1.yml` downloads the original XLSX, checks all tallies against `results/EMPEROR_LARUE_RAW_SATELLITE_TRANSITION_SUPPORT_V1.json`, and uploads only an aggregate audit receipt.
- Source-year totals are **raw observation records**, not inferred population sizes or detection-corrected occupancy.

**Scientific boundaries:** This retrospective audit does not change the frozen Ecology paper PR #189, the Beaufort source-island route PR #192 or the separately locked external archive PR #194.
