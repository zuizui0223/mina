# Antarctic co-censused 3-species breeding-niche response: fixed descriptive comparison

**2026-11-10 | PR #206 | post-result observational macro subpanel**. The full primary Antarctic observation base remains 595 original penguin-colony sites and 1991–2020 original OSI SAF ice at all 595. This **subpanel** asks a genuinely biological species-composition question that the already-completed 173-site environment–environment spatial comparison could not test.

## Why and exactly what is being tested

**Question:** At original sites where two penguin species were *both actually counted in the same breeding season*, how does their within-colony **relative observed nest abundance** vary with original same-season (Aug–Nov) coastal SIC? Does the signal reflect a between-colony geographic association or repeat-observation changes at the same colony?

This is **conditional community composition of co-censused species**, not occupancy, detection-adjusted local abundance, physiological ice preference, migration/colonization rate or causal warming effect.

### Frozen inputs / source grain

1. `macro_panantarctic_v1/outputs/observed_multi_species_same_year_303.csv` from original Git-blob-pinned MAPPPD data `fc134e364cf38699fa7611d7dee5fbbbcb370c0a`. Exactly 303 co-census site-years over original all-years records. Only original **1991–2020** seasons join to the existing source [full 595×120-month OSI SAF NetCDF artifact #42612067836](https://github.com/zuizui0223/mina/actions/runs/42612067836) using exact site/year.
2. Do NOT introduce a missing species as zero. If one of the pair was not counted in a given site-year, that pair is **not included**. Real original nest count zero is permitted with `log1p` response. Original selected within-site species method (most frequently recorded) does not change.
3. Exactly the 3 fixed unordered pairs: **ADPE–GEPE, ADPE–CHPE, CHPE–GEPE**, in this written order; no extra species, post-hoc lag, regional exclusion, k, beta, climate threshold or vegetation covariate.
4. Response for ordered pair `A–B`: `log(1+observed_nests_A)−log(1+observed_nests_B)`. Predictor: the same colony×year's original 25km ocean-source mean 8–11 month SIC averaged equally over all four supported months. Note that this mean uses austral calendar Aug–Nov, not each penguin's precise breeding dates. A zero observed nest is allowed; `log1p` is a fixed transform, not a movement probability.
5. **Preidentified source support (without opening ratio outcomes)**: 1991–2020 ADPE–GEPE **100** co-censused site-years at **25** sites; ADPE–CHPE **89** at **24** sites; CHPE–GEPE **168** at **33** sites. All source site-years must have complete original 4-month SIC; if incomplete, count/record rather than silently drop the whole source year.

### Fixed scales / outputs (no additional p-value search)

- **Site-year pooled descriptor:** Pearson r of log-nest ratio vs same-site-year SIC, with clear pseudo-replication warning (repeated years/sites), no independent site-year p-value.
- **Site-equal geographic descriptor:** For each site×pair, average log-nest ratio and environmental SIC over its actually co-censused years, then compute site-equal across-site Pearson r and broad-region-demeaned r. If sample variance or original region size is insufficient, record undefined.
- **Within-site temporal descriptor:** Only if original pair has **≥3 distinct co-censused years spanning ≥5 calendar years**, fit that site's OLS `log_ratio ~ SIC/10pp` (no lag). Never select a site by response sign or original ice variation; an exactly flat SIC site yields undefined slope and remains reported with an `UNIDENTIFIABLE_SIC` status. Report site slope distribution, median, number positive/negative and original source-region/250km-grid cover; do not pool repeated site-years into independent p-values.
- **Sensitivity of site-equal regional correlation:** Fixed-seed (20261110) 2000 **250km polar block bootstrap resamples** of **sites** (not site-years). If fewer than five distinct source blocks or <1500 valid reps, mark `REGIONAL_BIOLOGICAL_INFERENCE_UNDERPOWERED`. Spatial block CI is a descriptive dependence check, NOT 5% confirmed ecological causal effect or project-wide corrected p. Report all three pairs regardless of signs; don't pick the most positive slope as a new hypothesis.
- Also report the **count of unique sites, years, sampled 250km blocks, source regions and sites with 2/3/5 years**, and whether species-pair co-census is confined to WAP/Shetlands/Orkneys rather than the 18-region biological inventory.

## Causal/generalization boundary

Co-census is nonrandom, penguin counting effort and methods differ by colony and time, and only original sites with both species counted contribute. Even a spatial-block CI excluding zero would be an **association conditional on observed colony pairs**, not a temperature effect, ocean→plant mediation, true abundance ratio across unobserved sites, or a future nesting scenario.

The **173 positive terrestrial-map sites** provide a separate cross-sectional land niche component, not annual greening and not every co-censused species pair's source-year variable. Do not fake a joint 3-axis time-series analysis. Final status explicitly separates the 595-site Antarctic environment/macro atlas, 100 long biological trend series, 173 static terrestrial sites and this distinct co-census marine community-niche subpanel.

Outputs: source-joined pair site-years, one row per actual surveyed site and pair, one row per identified within-site temporal slope, a 3-pair original-source diagnostic summary, full region/block support audit, Japanese bounded interpretation. Leave PRs #211–#213, main and frozen Paper1/2 unchanged.
