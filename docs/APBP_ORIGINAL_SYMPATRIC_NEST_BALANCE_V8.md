# V8 interim biological finding — sympatry ≠ numerical balance in Antarctic penguin nest censuses

2026-10-19. **Positive, entirely observational descriptive original-database result**. Distinct from the previous unsupported V6 island×rock×sea-ice growth model. This is NOT preregistered statistical evidence of interspecific competition, spatial niche causality, or a new island universal law. Full environmental Tier1 Zenodo predictor test is pending a source-derived classifier exclusion correction; **no Tier1 ecological model coefficient or holdout outcome is declared here**.

## Original primary observations

From **SCAR–AntOBIS APBP DwC-A 2023 v2.3**, DOI `10.48361/zftxkr`, source SHA256 `afa947f39d9ad7382266d5be64c70f9fe4e84ffb6e2838c1369e043caae09abf` and authenticated Event/Occurrence/eMoF joined measurement CSV SHA256 `75c98ad9174f6ca8b88ae915adb8bb39de5d279099b45ce1ae7d1b2e25d5ba59`.

**350 original Event-core surveys with ≥2 concurrently recorded Pygoscelis species' actual nest/breeding-pair counts, at 62 distinct original census site IDs.** These generated 472 original within-Event species-pair nest comparisons with strictly positive total reported nests. Consolidating repeat survey years **before** computing ecological summary (median within each `site_id × unordered species pair`) yielded **82 pair-site units at 60 actual source sites**. All absent species are missing, NEVER artificial 0; a source-reported true 0 is retained when the other species' nest count is positive. Same site code denotes the publisher's census site, **not verified contact or competition at one nest/patch**.

Define for any two simultaneously counted species `B = 2 min(n1,n2)/(n1+n2)`. This is 1 for equal nesting counts, 0 for one reported measured count zero, and maps to `fraction of the minority species among the two = B/2`.

### Positive descriptive results

- **Median B = 0.159629** across **82** independent site×species-pair summaries: the minority species typically accounts for **7.98%** of the two-species observed nests. This explicitly conditions on the pair being co-recorded and the publisher census site not having both measured 0.
- Empirical balance quantiles of those site×pair medians: 10th **0.0048**, 25th **0.0236**, 50th **0.1596**, 75th **0.3857**, 90th **0.7022**. Count bins B≤0.1 **31/82** and B≤0.2 **45/82**; the latter means the minority contributes ≤10% of nests in 54.9% of distinct recorded species-pair sites.
- Each of the three species pairs has a similar median balance: **Adélie×Chinstrap 0.156863 (19 site-pairs); Adélie×Gentoo 0.168006 (25); Chinstrap×Gentoo 0.158934 (38)**.
- Source-site cluster percentile bootstrap on the site×pair median, 800 full-site resamples with seed 20261019, **2.5/50/97.5 percentiles ≈ [0.10154, 0.15963, 0.26416]**. This is a descriptive site-resampling *uncertainty illustration*, NOT proof of spatial independence, a one-sided p-value or a population-wide interval under probabilistic colony sampling.

This reveals **highly unequal reported nesting numbers even at confirmed multi-species census sites**, unlike the naive notion that multispecies local occurrence entails balanced breeding abundance. It does NOT imply interspecific exclusion or dominance as a cause of the observed field nest counts. Since the sample consists of *known previously counted rookeries*, zero reporting for an unlisted species is NOT evidence of its absence.

## Physical-area exploratory screen (source-only, NOT a registered result of V8 environmental test)

At the 53 co-recorded source sites with mapped nearby exposed rock and within 7 spatial 250km blocks containing ≥3 sites (71 site×pair units), a separate **exploratory** training-fold standardized ridge `alpha=10` heldout-block comparison showed a demographic/geographical/species-pair baseline MSE **0.09983017** versus baseline + *static* 2025 mapped exposed rock 2km MSE **0.10170849**. Added rock size improved just **3/7** held-out blocks and a full fit coefficient on `log(1 + mapped rock km²)` was **+0.01021**, too weak/unstable to interpret. This convenience screen is **not V8's predeclared Tier1-entropy experiment** and cannot be used as a negative empirical test of habitat quality, future deglaciation, competition or breeding-site availability.

Original geographic source limitations: in the 60 source sites with a positive species-pair denominator, 49 had preliminary island polygon classifications, 6 mainland and 5 unassigned; original source location uncertainty is frequently missing or >1km. Interspecific competitive interactions and microhabitat segregation are NOT directly measured. The resemblance among pairwise medians does not itself establish species-invariant ecology.

## Scientific interpretation / next decision

The pattern suggests a **macro-descriptive direction worth checking**: Antarctic Pygoscelis assemblages can be sympatric at the publisher's site scale yet strongly *numerically asymmetric*; territorial nest microsites, marine prey access, colonial social attraction, chronological colonization history, observer delineation, and local habitat mosaic are competing explanations. We have *not selected a winner*. An independent contemporary habitat layer must be assessed for predictor leakage (the 2025 Antarctic Ecosystem Inventory itself includes a MAPPPD-derived "Penguin colonies" Tier2 that is to be excluded from habitat predictor cells). A positive ecology claim requires geographically transferable conditional association from **uncontaminated Tier1 abiotic predictors**, and preferably independent nest patch microhabitat and source effort data. An external longitudinal test would need more repeated same-event multispecies nest counts; only ~23 exact same-site/year-interval multi-species growth episodes are documented in old APBP at current survey grain.

**Do not fold these results into the frozen *Ecology* PR189 without reopening its science freeze.**
