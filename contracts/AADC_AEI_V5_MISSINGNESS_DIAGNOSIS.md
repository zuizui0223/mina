# V5 source missingness diagnosis after independent AEI model non-improvement

**Status 2026-10-26: post-V4 diagnostic. V1/V2 source-density and V4 AEI biological observations already viewed. This is NOT a new effect search. No ecological models or tuned geography are allowed.**

V3 original AADC×AEI atlas mapped independent non-animal habitat at 6,863 of 7,785 sites. V4 only fit originally eligible P/A rows at sites with independent AEI pixels; 1,355/10,723 original eligible survey rows were omitted. V4 candidate-density signal was weak on this restricted cohort, and AEI habitat variables worsened spatial CV for both Adélie and seven flying seabird species. To interpret this **sample restriction**, separate why and where records are missing.

**Frozen source categories from original V3 derived site CSV**
1. INDEPENDENT_NONANIMAL_HABITAT: >=1 classified mapped AEI cell with no penguin/bird/ornithogenic source class label.
2. ONLY_ANIMAL_DERIVED_CLASSIFIED_AEI_CELLS: >=1 classified AEI cell in disk, but zero independent non-animal cells. Such cells can be linked by source authors to observed penguin colonies; dropping them may be outcome-dependent.
3. NO_AEI_MAPPED_CELLS: no classified ice-free AEI pixels at radius 2 km. This is mapping noncoverage, NOT absence of suitable nesting habitat.

Original respondent cohort is fixed to V1/V4 original AADC sources: 10,723 unique eligible P/A rows after unambiguous area/location/survey certainty/duplicate gate. Use exact source site IDs, source programme ADP versus seven flying codes, observed P versus explicitly reported A, source island/continent site class, historic AADC 2021-frame membership and frozen 250-km blocks. NR never becomes absence. Do not pool repeated site-years as independent population units; report row counts and distinct site counts by P/A, sample restriction and block separately.

Compute AEI coverage proportion among original P versus A observations for each programme, and location/class/era stratified missingness. Report source-weighted difference by original sites as a separate diagnostic if feasible, not a formal ecological test. **Do not reinterpret a systematic missingness difference as a causal animal effect**; it shows nonignorable sample selection and map-class leakage risk, not observed change in animal breeding habitat.

Original V4 biological model scores and frozen outcomes remain unchanged. No new radius, missingness imputation, source-class reinterpretation or habitat variable is allowed as rescue. If the cover-only denominator is biased by observed P/A, V4 is no longer suitable for physical-habitat inference even at its already cautious descriptive level.
