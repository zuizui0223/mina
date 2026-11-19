# Antarctic penguin island macro V6 — first source-reproduced model result (2026-10-19)

**Actual status:** observed V6 results recomputed from four independently verified public-source derivatives in [GitHub Actions run #39207033264](https://github.com/zuizui0223/mina/actions/runs/39207033264) (SUCCESS). Machine-readable frozen receipt: `results/APBP_LAND_SEA_ISLAND_CV_RESULT_V6.json`. This is a deliberately **exploratory observational prediction analysis** with specified candidate comparisons and geographic CV, **not a causal discovery or a preregistered confirmation**.

## Main finding: original island-buffering H1 NOT SUPPORTED

| Model | Predictors | 12-block equal-block MSE | All 406 pairs weighted MSE |
| --- | --- | ---: | ---: |
| B0, baseline | Species, previous nests, observation precision, year and geography | **0.200104166** | **0.172317767** |
| B1, sea ice | B0 + near/far annual offshore summer SIC changes and species interactions | **0.227392335** | **0.180675144** |
| B2, island exposed rock | B1 + island, log mapped rock availability and the proposed sea ice × island × rock interaction | **0.259979114** | **0.189579382** |

- Marine-only addition B0→B1 **worsened** heldout macro MSE by 0.02728817.
- Island/rock addition B1→B2 **worsened** macro MSE by 0.03258678. Only **1 of 12 geographical blocks** improved.
- Crucial largest source block (217 of 406 site-year growth pairs) also worsened: B1 MSE **0.075061269** vs B2 **0.079409522**.
- Proposed `SIC_near × island × logrock` coefficient: fitted all original pairs **−0.291253595**, refitted without largest block **+0.089362272**. Sign not stable.
- All prespecified substantive support gates **FAIL**; source-supported decision `NOT_SUPPORTED_BY_THIS_DATA`; `novel_island_mechanism_demonstrated=false`.

## Original support limitations (quantified, NOT amended after seeing effect)

- 3,370 three-species original nest records; 2,246 exact Dec–Jan–Feb breeding-season records before duplicate removal.
- 214 ambiguous site×species×season duplicate-survey groups containing 520 source rows excluded **entirely**, with no results-based choice of a preferred observation.
- 1,726 unique dated eligible seasonal records before geographic matching; 1,372 after original high-res island/mapped-rock/offshore-SIC support.
- **406 actual consecutive season pairs** from **61 locationIDs** and **31 high-res land-polygon features**, distributed across **12 spatial blocks**. **217/406 (53.4%)** belong to the most sampled block.
- By species: Adélie 280 pairs, Chinstrap 46, Gentoo 80. By provisional land class: **350 island** and **56 mainland** pairs. Many blocks contain only **1–5 pairs**, so equal-block MSE is noisy and not a universal-scale environmental effect estimate.
- High-res 2026 mapped islands classify 498/719 locations provisionally as islands, 74 as mainland and 147 unresolved, but 428/719 published points lack a location uncertainty estimate and measured uncertainty median is 1,043 m where available.
- Mapped rock is **modern presence around source point**, **not objectively available 1980s colony nesting capacity**. Offshore 25 km SIC cannot measure landfast ice, guano substrate, breeding access, krill availability, adult dispersal or species-specific foraging range.
- Site-year growth in observed nests could arise from detection, breeding skipping, breeding phenology and survey changes; cannot be identified as net adult population growth.
- Ice concentrations from 719 site locations during 1979–2022 yielded 31,636 *predictor* rows; only the above 406 rows are usable **paired biological response** samples after prespecified QC.

## Biological decision

**Do NOT claim** an Antarctic island nesting-substrate climate buffering law, marine habitat competition mediator, penguin colony site memory mechanism, abundance gain due to sea-ice retreat, or universal island-specific response. On existing recorded nest histories, the more complex sea/land/island predictor did not generalize between geographic regions; its interaction sign depended on the sampling-dominant region. **This is absence of support in the existing data, not evidence for the biological null of no ecological effect.**

A negative cross-region predictive result is worth preserving to constrain research choices: stop re-tuning coastline buffer, annual sea-ice lag, count-quality threshold, spatial-block size, coefficients, or source years to find a favorable sign. They were fixed prior to the main effect.

## What would materially change capability, NOT just number of source gates

A **separate independently timestamped updated whole-census database** with more site-level comparable nesting pair series and better representation of mainland and low-latitude remote islands, plus an independently measured or high-resolution historical **time-variable terrestrial nesting opportunity** covariate, would address the actual limiting dimensions. Current [MAPPPD v4.4 public portal](https://penguinmap.com/mapppd/) advertises bulk "Download all counts" through the 2024/25 breeding season, but its relationship to pinned 2023 APBP records and source-quality fields must be verified **before** interpreting it as independent new data (many will overlap). A genuine later holdout cannot reuse overlapping 2019–22 records as independent evidence.

Keep current `Ecology` Ross/Palmer manuscript PR189 separate and unchanged; this standalone macro experiment in PR197 is not evidence that the previous island-biogeography causal gap has been solved.
