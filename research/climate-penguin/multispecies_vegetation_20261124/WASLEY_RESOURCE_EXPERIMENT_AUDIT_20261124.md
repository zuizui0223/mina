# Published water × nutrient experiment: evidence-grain and novelty audit

Executed 2026-11-24. This is a published-summary recalculation, **not a raw-data reanalysis** or a meta-analysis. Sources: Wasley (2004), *The Effect of Climate Change on Antarctic Terrestrial Flora*, PhD thesis, Chapter 4 §§4.2.1–4.2.4 and Tables 4.3–4.4 (printed pp. 95,100); official parent https://data.aad.gov.au/metadata/records/ASAC_1087. Related article Wasley et al. (2006), https://doi.org/10.1111/j.1365-2486.2006.01209.x. Thesis indexed text inspected; PDF screenshot failed (expired/cache-miss source). Figures not digitized. Child record ASAC_1087_WaterNutrientExpt not retrieved; original treatment-cell measurements unavailable. No restricted uploads used.

## Design and measurement grain
At ASPA Meltlake, four communities, 32 randomized 25×25cm quadrats per community, four treatments (control, water, mixed fertilizer, both), across two summers. Fertilizer contains N/P/K and other nutrients; not isolated N or penguin guano. Thesis §4.2.2 explicitly describes six ETR measurements within one randomly selected quadrat per community-treatment combination. The nominal 96 ETR measurements therefore do not demonstrate independent plot replication (16 sampled quadrats, one per cell). Do not use published ETR treatment×community p=0.0003 as independent replicated interaction evidence without clarification. §4.2.3 describes seven replicate quadrats per cell for chemical/pigment/water measures (some missing values).

## Recalculate partial eta squared and p from printed F statistics
Formula partial eta² = F*df1 / (F*df1+df2); p=F survival function. The treatment factor has 3 numerator df and treatment×community has 9. Selected eight plot-replicated endpoints from Tables 4.3 and 4.4, excluding ETR. Separate descriptive Holm checks across eight endpoints within each term; not prespecified original family, not a complete multiplicity audit of all thesis outcomes. No variance partition across terms. Source rounded F values used.
| Outcome | Error df | Treatment F | Treatment partial eta² | Treatment×community F | Interaction partial eta² | Interaction raw p |
|---|---:|---:|---:|---:|---:|---:|
| ETR (subsamples only) |80|16.6085|0.3838|4.0602|0.3136|0.000257|
| Total chlorophyll |96|10.4628|0.2464|0.8329|0.0724|0.587594|
| Chlorophyll a/b |96|1.2177|0.0367|0.8314|0.0723|0.588934|
| Turf water |96|0.9719|0.0295|0.5295|0.0473|0.849850|
| N % |81|12.9166|0.3236|2.1529|0.1930|0.034013|
| P % |82|1.1904|0.0417|1.102|0.1079|0.370757|
| C % |82|1.3214|0.0461|1.091|0.1069|0.378528|
| δ15N |82|0.6365|0.0228|0.5974|0.0615|0.795668|
| δ13C |82|0.9378|0.0332|0.7446|0.0756|0.667094|

Eight-endpoint Holm checks: total chlorophyll treatment 3.574e-5, N% treatment 4.491e-6; all other selected treatment tests >=0.05. No treatment×community test passes selected eight-outcome Holm (smallest adjusted p 0.272105 for N%). Does not establish equal community responses. These are ANOVA effects on original reported transformed scales. The four-level treatment term does not identify water × nutrient synergy; treatment×community is not water × nutrient. No cell means, variance, signed factorial contrast or marine-origin N effect recovered. Do not pool different endpoints or thesis and article as independent studies.

## Decision
Existing manipulation provides a mechanistic precedent for resource limitation, not novelty for the proposed animal-subsidy/water story. It also confirms why independent treatment-plot support matters. Original child file or directly accessible equivalent source needed for signed water×nutrient interaction on a replicated endpoint; model y ~ community*water*nutrient (+ collection block if verified), report contrasts and dependence. Avoid another round of regression variants on the same small soil survey. A more distinct macroecological target remains temporal change in marine subsidies / breeding history and land response under climate, with direct source-matched observations. Keep earlier public findings and local AADC embargo/consultation holds intact. No merge or submission.
