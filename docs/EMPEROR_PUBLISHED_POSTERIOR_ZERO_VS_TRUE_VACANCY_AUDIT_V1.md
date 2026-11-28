# Emperor penguin 'reappearance' is not verified colonization: a 500-site-year published posterior audit

**Date: 2026-10-08.** Source-backed quantitative audit, but **no newly fitted ecological causal effect**, **no newly extracted satellite survey rows**, and **no prospective pre-outcome test**. This file is a distinct retrospective diagnosis within PR #195; PR #189/192/194 remain untouched.

## What was actually analyzed (NOT just proposed)

Public 2009–2018 global emperor-penguin Bayesian model output from LaRue et al. (2024), *Proceedings of the Royal Society B*, doi:10.1098/rspb.2023.2067; author's GitHub `davidiles/EMPE_Global`, pinned commit `13f71112da43c1fd082273677757b41c550457ed`, exact blob SHA `133c900c9dfbf2ce23ca403c9a59edecd9b51ace`:

`analysis/output/model_results/3_Colony_Level/colony_summary.csv`.

This is a complete **50 known colony × 10 breeding year = 500 colony-year posterior-summary** panel. It is *derived Bayesian model output*, not an original complete annual negative-search log or direct surveyed biological vacancy.

### Reproduced published-output diagnostics

| Type of model summary | Audited number |
|---|---:|
| Posterior site-years | **500** |
| Point posterior mean exactly zero | **15** |
| 95% credible lower endpoint = 0 | **114** |
| Positive posterior mean but lower 95% endpoint = 0 | **99** |
| Upper 95% endpoint = 0 | **15** |
| Distinct sites with at least one zero posterior mean | **7** |
| Adjacent annual posterior mean zero→positive | **9** |
| Adjacent annual posterior mean positive→zero | **10** |

These numbers were **computed independently from the author's complete CSV** and recorded in `results/EMPEROR_LARUE_2024_50_BY_10_POSTERIOR_ZERO_AUDIT_V1.json`. Source is **observational historical data already analyzed/published by its authors**; the new contribution here is an eligibility audit for the separate source-option ecological question, not a new penguin population finding.

Examples:
- **Umbeashi (`UMBE`)** has exact posterior means of zero in **2010–2012**, positive means **2013–2017**, zero again **2018**. In a later independently published field-history source Fretwell (2024), Umbeashi—reported non-extant in the 2019 inventory—is **seen again in 2021–2022**. The sequence is incompatible with treating the 2018 model zero as a proven *permanent* abandonment and the later sighting as demonstrated first colonization. Actual breeding status during skipped observation times is unknown.
- **Halley Bay (`HALY`) 2016:** the model output still estimates a **positive annual posterior abundance mean ≈5,997.67** with 95% credible lower endpoint **0** (N estimates in the model are population-level latent/spring-abundance proxies). Yet Fretwell et al. (2025), analyzing spring image *attendance* at Halley, **recorded an observed zero in 2016 and 2017** after early fast-ice loss. Two measurements can disagree without meaning that a permanently extinct colony was biologically refounded: population present during winter versus countable adults attending in a late spring image are different biological quantities.

## Why 9 'recoveries' are NOT 9 recolonizations

The **literal published model code** `analysis/EMPE_model_empirical.jags` makes yearly colony occupancy `z_occ[s,t] ~ dbern(prob_occ)`, independently by year and colony, sharing an overall occupancy probability. It does **not** model movement to new sites, colony-year detection, natal origin, nor any state transition conditional on occupancy in t−1. The growth process is autocorrelated in *latent abundance X* but **not in binary presence z**.

The original authors acknowledge limited colony absences and absence of explicit detectability and previous-year occupancy dependence (LaRue et al. 2024). It is **not** a fault in their intended global *abundance* index; it is a hard limitation if later readers try to infer physical habitat availability, social colonization, re-establishment, or rescued extinction from these posteriors.

**Observation-state mixture** is even sharper in the author's source codebook: their `bpresent=No` includes (1) no birds in a usable scene **OR (2) no breeding fast ice** at the place. Therefore an absent bird count at a known colony has not separated a **vacant but physically available refuge** from **no viable habitat**. Contrasting these as if both were zero-recruitment social exclusion is scientifically invalid.

Fretwell et al. (2025) explicitly documented that their 2016–2018 modeled regional indices were **18.6%, 20.4%, 17.8% below LaRue et al. (2024)** for aligned sites and years. The authors noted Halley zero versus null treatment as *one* reason. They also explicitly stated **88% of the remaining study discrepancy** could be attributed to lower estimates at **Atka Bay, Gould Bay and Smyley Island**, Smyley responsible for **44% of the total discrepancy** in their reported decomposition. Do NOT assume the numerical 18–20% difference is caused only by the Halley zero convention; ecological and observation-model time definitions differ.

Published 2025 source: https://doi.org/10.1038/s43247-025-02345-7, Methods occupancy model and Discussion paragraphs concerning 2016–2018 model comparisons. The 2025 analysis also states its occupancy model could not estimate detectability or previous-state dependence because years with absence were scarce.

## Primary observation protocol cross-check — dates and zeros can generate incompatible "reappearances"

The **actual source script**, not an inferred criticism, `davidiles/EMPE_Global` pinned commit `13f71112da43c1fd082273677757b41c550457ed`, `analysis/script1_PrepareData.R`, defines satellite survey window September–November and then removes late-season apparent absences with the filter:

`!(yday >= nov1_yday & area_m2 == 0)`

That is: **at/after November 1, a satellite image classified as having zero penguin area is excluded**. This is an author-chosen safeguard against late-season departures after breeding, not necessarily a mistake for estimating population abundance. But it changes which observations can substantiate **actual colony-site disappearance**. Another study counting those spring-time zero images as immediate observed absences has a *different observation estimand*. Fretwell et al. (2025) explicitly discuss this difference at Halley Bay; do not infer a latent population die-off from the contrast.

Combining the original codebook with the public posterior table:
- **15/500** posterior point means are exactly zero;
- **9** zero→positive next-year point transitions (and 10 positive→zero);
- **0/9** satisfy the PR #195 independently documented **stable-ice + repeated negative whole-site survey + confirmed new breeding** gate. This says **zero verifiable events in this *source***, NOT zero real Antarctic founding events.

A third prior-art limit: Bielinis et al. (2026), *Remote Sensing in Ecology and Conservation*, DOI `10.1002/rse2.70064`, detected historical guano evidence **predating the earliest published colony record at 18/66 known emperor colony sites**, using Keyhole/Landsat/Sentinel-2 imagery since the 1960s. Thus the general problem **first discovered in an inventory ≠ first colonized in nature** was itself already demonstrated at continental scale; the four-site 2024 reappearance audit is a reproduction and eligibility check, not novel ecological history.

The genuinely untested functional alternative—existing occupied receiver versus verified vacant and *physically available* nesting refuge—still requires independent negative image histories, contemporary fast-ice access and breeding, which the LaRue posterior output does not provide.

Primary sources: [LaRue data processing script](https://github.com/davidiles/EMPE_Global/blob/13f71112da43c1fd082273677757b41c550457ed/analysis/script1_PrepareData.R), [model code](https://github.com/davidiles/EMPE_Global/blob/13f71112da43c1fd082273677757b41c550457ed/analysis/EMPE_model_empirical.jags), [Fretwell 2025](https://doi.org/10.1038/s43247-025-02345-7), [Bielinis 2026](https://doi.org/10.1002/rse2.70064).

## What would qualify as genuine ecological 'recolonization of an available option'?

**Minimal observational sequence for site i**:
1. Before shock, *the candidate physical ice platform is usable* (`A_i,t=1`) using an independently measured same-season ice/access footprint, not inferred from the presence of birds.
2. The candidate is adequately searched at relevant breeding stages in repeated baseline seasons, showing **surveyed absence**, not missing images.
3. After independent shock at source j, **confirmed reproduction** starts at i (egg/chick/fledging stage evidence or appropriate substitute) with site polygon continuity.
4. Ideally, documented *founding individuals / origin*, to link j to i; absence of origin identification reduces inference to new occupancy *without source attribution*.
5. Follow-up checks whether breeding-site occupancy persists and is not simply a temporary subgroup/colony movement at the same physical site.

The **published posterior summaries, even with 500 annual points, meet none of the required independent prior physical-availability / surveyed-empty / breeding-founder criteria**. Prior published 'newly discovered' sites also mostly have positive earlier satellite records, but no verified repeated earlier negatives.

**Verdict:** the simple rescue/colonization claim for PR #195 is **not identifiable** from `bpresent` or published model-`N_mean` alone. The mechanism is not biologically falsified; the *specific public-data-based route* is insufficient. The strongest empirically demonstrated source result in this audit is a descriptive posterior-state sensitivity, not a newly established social attraction or island-biogeography causal law.

## Reproduce / pinned provenance

```
python scripts/audit_larue_2024_global_posterior_occupancy_v1.py --out /tmp/larue50posterior.json
python -m pytest -q tests/test_emperor_larue_global_posterior_occupancy.py
```

The script checks **the exact Git blob SHA** of the author's public CSV. If the source changes or cannot be obtained, this source check fails and the frozen receipt remains a historical record; it does not silently fit a new replacement dataset.

References:
- LaRue et al. (2024), original article: https://pmc.ncbi.nlm.nih.gov/articles/PMC10932703/
- LaRue original model code: https://github.com/davidiles/EMPE_Global/blob/13f71112da43c1fd082273677757b41c550457ed/analysis/EMPE_model_empirical.jags
- LaRue published result data: https://github.com/davidiles/EMPE_Global/blob/13f71112da43c1fd082273677757b41c550457ed/analysis/output/model_results/3_Colony_Level/colony_summary.csv
- Fretwell et al. (2025), model comparison: https://doi.org/10.1038/s43247-025-02345-7
- Fretwell (2024), Umbeashi returning: https://doi.org/10.1017/S0954102023000329
