# V22 — Timing mismatch: late visiting nonbreeders cannot be counted as conventional pre-egg breeding candidates

Date: 2026-10-10. This is a **source timing and null-model QA**, NOT an empirical penguin result. No AADC tagged individual observations were read and no new biological model was fitted.

## A discovery in the published *method*, not a new species response

[Emmerson, Walsh & Southwell 2019 (*Ecology and Evolution*), doi:10.1002/ece3.5067](https://doi.org/10.1002/ece3.5067) already linked SAME TAG individual weighbridge mass records and breeder/nonbreeder nest scans from Béchervaise Island. The original paper reports **most gate detections of nonbreeders occurred after the chicks had hatched**; relatively few nonbreeders passed the gate before egg laying, with early peaks related to breeder foraging changes. The analysis is of published five-day season-specific mass trajectories, not direct prospective **first lifetime egg** transitions in following breeding seasons.

This exposes a denominator error in V20–21's general phrasing of `P(egg | visits island this year)`. A mixture of late posthatch visits and early prelaying visits does **not** represent a homogeneous current-season first-laying risk set. Furthermore, a late visit may indicate information-gathering for subsequent colony choice; it must not automatically count as either a failed current-season breeding attempt or a prospecting event that causes later reproduction.

More direct novelty prior art: [Acker et al 2022 (*Journal of Animal Ecology*), doi:10.1111/1365-2656.13676](https://doi.org/10.1111/1365-2656.13676) already modeled the **attraction to and competition for high-quality colonial seabird nesting patches as determinants of first-breeder/skipper/immigrant breeding participation** (in kittiwakes). Thus the abstract concept 'visitors arrive but competition prevents nesting' is not a new ecological mechanism. A cross-Antarctic penguin study would need independently shown stage-specific arrivals, opportunity, egg initiation, and later first recruitment beyond this theory.

### Exact risk-set separation required when original data become available

- **Pre-first observed colony egg**: tagged individual first seen crossing inward before a colony/season's first detected egg date; this is a *conservative reference* and not the total population of possible later nest initiators.
- **After first colony egg but before hatch**: still potentially able to breed under site-specific phenology, but NOT the strictly earliest first-egg cohort.
- **After first colony hatch**: late attendance/prospecting; never quietly add to pre-egg first laying risk denominator. A rare late egg is theoretically possible and does not prove a causal first arrival, but must remain separate.
- **Same observation calendar date as first egg/hatch**: **ambiguous temporal ordering** if original egg and hatch were logged as dates rather than exact event instants. An RFID gate timestamp later than midnight does not imply the egg was actually laid at midnight.
- **Unknown source scan opportunity**: 'no tag at monitored nest' is not certified never bred or died. The reported >98% nest-tag detection referred to incubating birds physically present under a handheld reader, not all gateway visitors.
- **Repeat entries from same tag**: use a `tag × austral season` unique risk unit, preserve actual event numbers for effort, and do not turn daily feeding trips into many independent newcomers.
- **Same-tag egg confirmation**: an observed direct egg at an independently identified nest after the first detected gate entry may provide *temporal data*; it does not itself prove the first-ever egg without marked chick age and earlier season effort.
- **Next-season first breeding**: only after status at t (prebreeder vs previously breeding skipper vs early failed) and t+1 verified first egg are known on the same source ID. Do not assume all tagged nonbreeders are first-year breeding candidates.

## Exact synthetic demonstration only

[Original-data-free GitHub Actions V22](https://github.com/zuizui0223/mina/actions) executes `scripts/audit_bechervaise_season_phase_selected_entrants_v22.py` on five fabricated tag-season identities and six incoming crossings:

- 2 first seen **before first colony egg** (one has independently documented egg later, one never observed with egg), thus the *documented positive fraction among that restricted risk set* is **1/2** with a logical unknown-outcome upper bound **2/2**.
- 1 first seen between first egg and first hatch (this bird's egg was documented *before* its first detected incoming gateway pass).
- 2 first seen **after first hatch**, one with a fabricated exceptional later egg to explicitly reject claims that late first laying is mathematically impossible. Their presence cannot be merged into the prespecified pre-first-egg at-risk denominator.
- A naive all-phase documented postgate egg fraction would be **2/5**, a different number generated simply by mixing qualitatively distinct attendance events and outcome-detection patterns.

These fractions are **deliberate synthetic arithmetic**, not observed penguin breeding probabilities or a causal demonstration that earlier site attendance causes eggs. The study was constructed specifically to catch denominator contamination. Its source-data interpretation stops at observation timing and missingness.

## What new source/authorization would actually unblock the ecology

[AADC AAS_4086](https://doi.org/10.26179/1205-2s58) raw 2006–2018 gate events still lack a validated original download/processed codebook in this workflow. [AADC AAS_4518](https://doi.org/10.26179/s2qa-s344) site tag scanning and dates (1991–2019) are available through publisher's interactive email-mediated download, but no original bytes were acquired. The original custodians' methods and code must distinguish a gate detection from a true arrival and an observed nest tag from verified egg. Publisher asks users to discuss proposed new analyses with Louise Emmerson. The code and report in PR193 must not be taken as an authorized or completed independent penguin research analysis.

**Current scientific decision:** HOLD breeding propensity conditional on prospecting, HOLD confirmed first recruitment, HOLD novel island colonization cause. Study-team consultation and original event-time/tag code documentation are prerequisites.

Files: `contracts/BECHERVAISE_ARRIVAL_PHASE_VS_FIRST_EGG_RISKSET_V22.json`, `scripts/audit_bechervaise_season_phase_selected_entrants_v22.py`, synthetic tests and `.github/workflows/bechervaise-nonbreeder-stage-riskset-v22.yml`. Frozen Ecology PR189 and original USAP bird-ID PR142 unmodified; emperor PR195 unchanged.
