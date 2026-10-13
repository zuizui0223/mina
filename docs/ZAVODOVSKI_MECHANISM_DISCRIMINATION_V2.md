# V2: distinguishing patch inheritance from shared habitat choice (2026-10-11)

## Verified progress
GitHub Actions run 38058717693 completed successfully: synthetic-only job, Shapely geometry tests and no-original-outcome assertion. This verifies **code integrity only**, not real ecological exchange.

## Competing mechanisms and predictions

**H1: site legacy / succession.** After chinstrap disappearance, macaroni gain is disproportionately located on recently vacated chinstrap land **relative to matched, available non-chinstrap land**. A legacy mechanism specifically predicts an effect of *past* chinstrap occupancy after conditioning on current substrate, slope, coast access, terrain exposure, local density and observation effort. This is not sufficient to attribute legacy to guano.

**H2: shared habitat preference.** Both species prefer the same coastal land. Raw overlap is high but the past-chinstrap indicator loses explanatory value after matching on physical terrain and pre-transition availability.

**H3: competitive release.** Former chinstrap occupancy suppresses macaroni establishment until chinstraps disappear. Distinguishing this from H1 requires an independent measure of contemporaneous competitor presence and historical occupancy; annual snapshots may not resolve the order of events.

**H4: spatial segregation.** Macaroni gains occur on other parts of the island, with low or zero transition overlap, even as the island-wide abundance trends diverge.

## Prior-art and observation limitations

Ratcliffe et al. 2026 already established contrasting island-wide species trends and argued nesting-space competition was not the primary explanation. Do not recast those as novel. The BAS archive includes cloud-gap substitutions using images from other years. Unless a per-region **actual observation-year and coverage mask** can be reconstructed independently, the spatial transition endpoint is STOP. Even a high E from original polygons is not a biological transition result if the observation years are synthetic mixtures.

## A stronger null, frozen before geometry opening

Define eligible available land in both years using independently observed cloud-free coverage and actual substrate. Condition on elevation, slope, coast distance, volcanic disturbance and distance to previous macaroni breeding space. Within strata of these variables, compare the frequency of macaroni gain in former chinstrap sites against physically matched never-chinstrap sites. Report risk difference and uncertainty using spatial block resampling rather than treating each pixel as independent. Do not implement an ad-hoc null if eligibility/matching covariates are missing. Separate the *temporal* precedence (chinstrap loss before macaroni gain) from simultaneous between-snapshot change; a 2011→2016 overlay alone cannot establish order.

## Immediate decision tree

1. Download only public archive metadata and layer_descriptions.csv; verify file names, real-year cloud masks, and licensing.
2. If dated masks exist, predefine a 32726 raster grid and matched eligibility support before any colony polygon inspection.
3. If masks absent, label primary endpoint NOT IDENTIFIABLE, do not calculate pseudo-temporal turnover from imputed layers; seek original image provenance or independent repeated field surveys.
4. Do not merge with Ecology PR189. Do not claim competition, facilitation, first settlement, successful breeding, or population replacement without corresponding data.

No real polygon rows or biological response were read or estimated in V2.
