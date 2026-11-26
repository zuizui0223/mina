# V17 results and integration decision — 26 November 2026
**Status: executed descriptive accounting and exact identification sensitivity; not a measured ecological function.** No merge, submission, new causal claim, or change to the protected Antarctic integrated v0.6 manuscript.

## Count reorganization hidden by aggregation
For the fixed six ADPE–GEPE site series all endpoints have ADPE decline and GEPE growth. The fraction of gross absolute species-specific count change cancelled in the aggregate is median 0.47910, site-equal mean 0.45428. Across 45 adjacent-calendar-year comparisons, 25 have mixed signs, median cancellation 0.06283, site-equal mean 0.22173. These different temporal supports are descriptive, not a formal timescale effect. Other endpoint families: ADPE–CHPE median 0, CHPE–GEPE 0.02016; three-species complete observations (three sites, overlapping two-species panels) median 0.48743. All source rows were previously outcome-exposed; these are new arithmetic summaries, not independent ecological replications. The 183 pair site-years span just two regions and four 250-km blocks, and the 34 three-species site-years are not additional independent observations. Shared citation/method within a year does not prove identical survey effort or method across years.

## Species-weighted nest-index identifiability
For a hypothetical positive, additive, time-invariant per-nest contribution w_s, constrained to relative weights [1,R], the exact change interval is [G-RL, RG-L]. This is an algebraic sensitivity analysis, not a measured flux. The unknown weights have not been estimated and the soil concentration contrasts in V16a must never be used as per-nest rates.

| Site | ADPE change | GEPE change | net | GEPE/ADPE contribution ratio for zero weighted change |
|---|---:|---:|---:|---:|
| ARDL | -866 | +2750 | +1884 | 0.31491 |
| BISC | -1279 | +3152 | +1873 | 0.40577 |
| LION | -3640 | +1147 | -2493 | 3.17350 |
| LLAN | -2366 | +4625 | +2259 | 0.51157 |
| PCHA | -14 | +356 | +342 | 0.03933 |
| PETE | -379 | +1353 | +974 | 0.28012 |

When GEPE/ADPE contribution is below a row's break-even ratio, its weighted change is negative; above, positive. At maximum hypothetical between-species weight ratios R=1.25/1.5/2/3/5/10, strict reversal of the observed total sign is possible in 0/0/1/2/5/5 of the six endpoint series. The R=5 set contains four of five growing sites and the declining LION site; there is no claim of simultaneous reversal under one common weight vector. The annual values are 3/3/6/10/11/18 of 45; site-balanced frequencies 0.0331/0.0331/0.0985/0.2328/0.2745/0.3770. Three-species endpoint reversal is possible in 0/0/0/0/2/2 of 3; the 23 consecutive-year comparisons are separately recorded. A modest factor 1.5 cannot reverse any endpoint sign in the six ADPE–GEPE sites; do not claim pervasive functional collapse or even pervasive sensitivity to small weight differences.

## QA
Pinned original-source-derived inputs: ref c67e55c9f4f657ef308c02a85c6ff366dce8e1f4; pair blob 7e86b2eb5f5a4e012f128101ebec02d51cbfe41c and triple blob 9ca2819016318d177a8d447a89ef03d7c8b78f7a. Code checked all 102 triple/pair agreements and 4,344 corner-weight evaluations. Separately reread source rows and committed result blob cb73e98eac4c3a765938448bb550e7e9fe0056c4, recomputed all 21 endpoint and 134 adjacent-year comparisons using cancellation=1-|net|/gross and independently enumerated weighted endpoint differences; all 930 scenario classifications matched; maximum cancellation discrepancy 1.11e-16. Execute `node species_weight_sensitivity.mjs pair.csv triple.csv` to reconstruct arithmetic payload; archived JSON adds input reference, blob SHAs and interpretation status. No new Actions run or raw census download; actual calculation executed in the connected analysis session.

## Proposed text for v0.6 discussion, subject to author review
"Across the six source-matched Adélie–gentoo site series, opposite species-specific count changes cancelled a median 47.9% of the gross absolute change in the two-species count sum. Thus aggregate count changes are not a sufficient description of assemblage reorganization. For a hypothetical additive, positive and time-invariant species-weighted index, the direction of change was not identified from total count change alone at all sufficiently broad weight bounds. The observed soil-context contrasts motivate direct measurement of species-specific terrestrial contributions, but do not supply such weights. No nutrient flux or plant response is estimated here."

Retain this as a supporting result/supplement for the spatial allocation and composition paper, not a standalone paper or new mechanism. Next actual biological bridge requires paired colony-specific measured nutrient input/guano deposition and repeated vegetation response, with densities and occupied area, or a properly calibrated taxon-specific contribution measure. Do not reopen the already failed temporal plant join or assign invented weights. The existing habitat exposure decomposition and polynya associations remain the marine main results.
