# Moss vs bare soil water: organic-carbon overlap audit (2026-11-24)

Executed locally on Ball (2025), USAP-DC DOI 10.15784/602015 (CC BY 4.0), workbook MD5 75cc48e8ca21d8b408098a14692e6d3e and SHA256 eabd7171cb700351ee8b6d0df82a5f8bb92ccb8a4076cd55387a9cca8f5fcfbf. No restricted AADC inputs. Continuation of CARBON_CONDITIONING_DIAGNOSTIC_20261124.md. No tissue hydration or marine-N-origin measurement.

## Design
Select Bare and five moss genera (Polytrichastrum, Sanionia, Bryum, Syntrichia, Bartramia). Exclude missing water/carbon. Within each of nine site-stage strata, match distinct bare and moss samples without replacement, maximizing count of matches with carbon ratio <=1.5 and then minimizing total absolute log-carbon distance (Hungarian algorithm). Alternate ratios 1.25 and 2.0. Matching does not imply physically paired plots. Equal stratum weights after mean paired log-water differences, exponentiated. Independently verify optimal match cardinality and cost by exhaustive enumeration of assignments (at most three bare samples per stratum). Strict observed carbon-range overlap only 5/9 strata, so even caliper matches may span disjoint observed ranges. No inferential p-value (3 sites; selected cover classes).

| Carbon ratio tolerance | Sites | Strata | Pairs | Positive strata | Matched water ratio | Matched carbon ratio | Unmatched water ratio on same strata | Site-deletion water ratio |
|---|---:|---:|---:|---:|---:|---:|---:|---|
|1.25|2|5|6|2|1.340712|0.979540|1.581274|0.758089–1.960706|
|1.5 primary|3|6|8|3|1.318949|1.046522|1.550639|0.887069–1.739730|
|2.0|3|9|15|6|1.466042|1.393904|1.901887|1.265659–1.932370|

Primary equal-site ratio 1.217728. Site-specific ratios Collins 1.214596, Fourcade 0.758089, Nelson 1.961095. Omitting Nelson L (post-result leverage diagnostic) yields 0.977606. Restricting to Polytrichastrum and Sanionia gives 6 pairs/4 strata with ratio 1.429606 (site deletion 0.863068–1.895553) at primary caliper. Broad caliper allows substantial remaining carbon imbalance. Do not interpret attenuation as causal mediation. The original positive cover contrast (1.901887) remains descriptive; an independent moss water-retention effect is not established. More sample support or experimental manipulation is needed.

Local reproducibility archive moss_carbon_overlap_analysis_20261124.zip, SHA256 189dd9abaa37ca4f9fb4a96ada629a6fc0aabb362067a18d9c52491006ab8ae2. Executed script SHA256 e7b82358a592ef8f1e782b86dab62b85f1b98f13dc977e337a6dadbaa3e9f235. Contains exact code, support/match/stratum/summary CSVs, README and receipt. Original workbook not republished.

USAP 602038 (Plant Thermal Traits) and 602039 (Plant Nitrogen) catalogues rechecked, original files not acquired. No alternative verified public table found. Clements et al. 2026 DOI 10.1007/s00300-026-03502-0 already reports moss nitrogen-gradient and hydration/thermal trait relationships; no claim that repeating them is novel. Next gate remains original sample identities/metadata and matching support, distinguishing tissue water from soil water. No main merge or submission.
