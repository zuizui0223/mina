# Manuscript spine v1.0 — Unified breeding-site redistribution across colonial seabirds

**Status: evidence-constrained draft; not submission-ready; 2026-11-07.** Frozen source counts and Step 4 hypotheses are not altered. Previous UK and penguin positive findings are retained as source-provenance results, not new independent confirmations. These data are predominantly UK–Irish administrative breeding-site networks, not a global island experiment.

## Proposed working title

**Beyond proportional thinning: uneven breeding-site concentration across seabirds**

A more explicit title if needed: **Breeding-site concentration is widespread in UK seabirds but not explained by a uniform sea-surface temperature association**

## Candidate abstract (English; exploratory, not confirmatory)

Population declines do not necessarily produce proportional thinning across discrete breeding sites: relative spatial composition can change even when the total number of recorded breeders is held fixed. The geographical breadth and environmental correlates of such reallocation remain poorly characterized. We harmonized two-epoch censuses into 675 network-by-species comparisons across 20 seabird taxa, including 663 British–Irish seabird records and 12 Antarctic penguin records. A ten-year-scaled change in inverse-Simpson concentration was contrasted with a fixed-share, finite-count multinomial benchmark conditional on both observed census totals. Among British–Irish records, excess concentration was positive in 436 of 663 comparisons (65.8%), and the network-averaged response was positive in 15 of 17 species. In declining networks, 324 of 479 (67.6%) showed positive excess concentration. The Antarctic regional comparison was less uniform (5 of 12 positive), and British–Irish coverage was geographically unbalanced, particularly toward Scotland. Species-conditioned analyses retaining networks as dependence blocks found no four-test-Holm-supported association of excess concentration with historical spring sea-surface temperature change (662 records; adjusted p = 0.94). Nor did average demographic decline or temperature change support predicted increases in between-species site-use overlap (376 pairs; adjusted p = 1.00 for each). Annual adult breeding-site fidelity was not estimable under the common definition. We conclude that reallocation beyond the count-only benchmark is frequent in the British–Irish surveillance data, but its regional and climatic drivers are not captured by a single uniform thermal or decline association. Inferences concern monitored components, not verified breeding polygons, causal warming responses, or future colony abundance.

## Core claims and corresponding evidence

| Claim | Original harmonized evidence | Strength / limit |
|---|---|---|
| Spatial composition can change beyond count-only proportional allocation | 436/663 UK–Irish main rows with positive Y_excess; 15/17 species with positive network mean; 324/479 declining rows positive | Descriptive evidence, NOT a detection-error-calibrated null or an independently registered test |
| The result is geographically structured | 497/663 eligible JNCC rows were Scottish in the original Step1 readout; Ireland separately showed opposite average tendency | No universal island or across-country rule established |
| Antarctic regional networks do not automatically reproduce the UK direction | 5/12 MAPPPD main regional rows positive (3 species, 7 regions) | Too few independent Antarctic region/network units for a pooled hemispheric generalization |
| More SST warming does not consistently predict stronger excess concentration | H3: beta +0.033163; CR1 95% CI [−0.021376,+0.087702]; wild p=0.235; Holm4=0.940; 662 rows/387 networks/20 species | No support for predeclared positive direction; not proof of zero physical effect |
| Stronger average decline does not consistently increase two-species spatial overlap | H4D: beta +0.006161; CR1 95% CI [−0.031821,+0.044143]; p=0.7576; Holm4=1.0; 376 pairs/90 networks | No support; pair rows are dependent within source network |
| SST warming does not consistently increase overlap | H4W: beta −0.015216; CR1 95% CI [−0.049814,+0.019383]; p=0.4212; Holm4=1.0 | Main effect not supported; direction in Scotland-excluded descriptive sensitivity is more negative (−0.091891, CI [−0.147714,−0.036068]) |
| Adult breeding-site fidelity moderates concentration | H2 not estimable: 0/20 species with strict comparable annual same-breeding-site estimate | Do not substitute adult return rate, survival or qualitative philopatry |
| Future warming predicts population or concentration shifts | Not established. Existing CMIP6 site atlas matches only 3/12 Antarctic regional species-networks completely for air temperature and 2/12 for stringent marine forcing; 0/663 UK network inputs | Future physical exposure belongs in supplement as source-coverage illustration, never a biological forecast |

## Paper argument and division of evidence

### Introduction
Colonial breeding populations occupy discrete site networks. Changes in total abundance are often used to infer demographic vulnerability, while the allocation of breeders among sites is separately measurable. Under constant site shares, finite counts alone can increase apparent concentration as totals decline; a source- and count-matched null is needed to distinguish this arithmetic expectation from additional redistribution. Both species-specific site attachment and ocean forcing could modify redistribution, but need independent measurements and sufficient geographic repetition. A multi-system synthesis must also separate geographically defined networks from physical islands.

**Main question:** Is excess breeding-component concentration widespread among monitored colonial birds, and does it covary predictably with adult site fidelity, contemporaneous SST change, population decline, or sympatric species' spatial overlap?

### Methods
- Pin original JNCC two-census XLSX, MAPPPD Pygoscelis nest-site series, Palmer/Signy colony codes, emperor marginal model estimates, Ross sectors. Preselect synchronous initial/terminal epochs and K>=3 source sites using only metadata and methods; preserve zeros and missingness.
- Core Y = 10/dt * log(H1/H0) − E_null[10/dt * log(H1*/H0*)]. Null draws use the pooled site share and fixed empirical N0,N1, B=20,000. This is not an observational detection or breeding-success model.
- Q4 uses 1−0.5*L1 distance between two species' relative site allocations, exactly matched original sites/epochs, and a similar pair-specific source count-only null.
- Link NOAA OISST v2.1 March–May (UK) or Sep–Nov (Antarctic) to unchanged source Site.ID coordinates with one common six-month valid marine cell within 50 km. W is a per-decade difference in original survey years; the original label and coastline error remain.
- Step3 frozen exploratory regression uses species fixed effects; cluster-block CR1 and 9,999 null-restricted Rademacher draws with network clusters preserving shared original pair counts; predeclared directions, two-sided p, Holm across original H2/H3/H4D/H4W slots. Explain deviation from initial LMM draft before the new fits.
- For physical exposure only, use a separate frozen atlas of 40 source-matched Antarctic sites under three CMIP6 models × 2 SSP × 2 time periods; require all original monitored sites per network to match before computing a network mean. Do not forecast biological state.

### Results
**R1 distributional reconfiguration.** Present overall raw concentration, null-centering, sex/demographic-count unit differences, 17 taxon effects and country support. Retain nondeclining networks and terminal zero as nonestimable Y, not missing at random.

**R2 geographic variation and Antarctic scope.** UK–Irish dominance and regional unevenness; Antarctica is a contrasting sparse regional source, not independent universal replication; local-resolved Palmer and Signy positives use different nulls and occupy the supplemental hierarchical scale panel.

**R3 fixed correlates.** H2 unestimable, H3/H4D/H4W no corrected support, report positive and negative coefficients with exact uncertainty. Scotland-exclusion only as predeclared descriptive geographic sensitivity. Do not overinterpret unsupported association as proof climate irrelevant.

**R4 prospective physical context.** Climate atlas covers only 13/61 original MAPPPD cohort-site memberships; strict complete marine 2/12 network×species. This is physical context, NOT evidence of climate-driven reallocation or a validated penguin future forecast.

### Discussion
The primary supported observational insight is a recurring mismatch between census decline and breeding-site proportional allocation, especially among the monitored British–Irish taxa. It is not a newly proven island mechanism. A single regional SST trend, demographic mean change or generalized adult philopatry proxy does not resolve which sites gain or lose shares; candidate local processes (nest-site memory, changing habitat, predators, social attractors, survey practices) require independently measured variables. The strongest counterargument is that count-only nulls do not model adjusted census error, colony-border changes, or spatial coverage; this caveat must appear in abstract, Methods and Discussion. Future exposures should only be interpreted for coverage-verified source sites. No causal competition or 2050/2100 breeding abundance conclusion is warranted.

## Main display plan (no additional unapproved endpoints)
1. Figure 1: geographic sampling and hierarchical unit diagram. Clarify Country×Master-site versus MAPPPD region versus island within-colony codes. No pseudoreplication.
2. Figure 2: species-equal distribution of excess concentration and geographic uncertainty; UK/Irish 17 species separated from Antarctic 3.
3. Figure 3: three coefficients with network CR1 95% intervals and family Holm decision, H2 explicitly NA; Scotland-excluded sensitivity in supplementary figure.
4. Supplement: site-level leader changes from old JNCC V46, clearly labeled as same original dataset and **different null**; previous Palmer/Signy local analyses; OISST source/hash QA; complete/partial CMIP6 match and coverage.

## Unresolved before submission
Quantify observation/survey-effort consistency beyond count-only null. Confirm physical-site geometry where possible. Resolve H2 annual same-site fidelity or formally retain non-estimable. Add continent- or site-specific environmental drivers only as a separately declared new stage, not as a post-H3 rescue. The manuscript is **not** a demonstrated universal climate mechanism or rigorous island-effect analysis at present.

## Canonical source receipts
- Step1: outputs/STEP1_DESCRIPTIVE_PROFILE_JA.md; data/network_species.csv; data/network_species_pairs.csv
- Step2: outputs/STEP2_SOURCE_READINESS.json; outputs/STEP2_OISST_UK_JOIN.json; outputs/STEP2_OISST_SOUTH_JOIN.json
- Step3: contracts/ANALYSIS_PLAN_FROZEN.md
- Step4: outputs/STEP4_FIXED_ASSOCIATIONS.json; outputs/STEP4_MODEL_READOUT_JA.md; outputs/STEP4_INDEPENDENT_ARITHMETIC_QA.json
- Step5: outputs/STEP5_PHYSICAL_EXPOSURE_JA.md; outputs/STEP5_PHYSICAL_EXPOSURE_QA.json
