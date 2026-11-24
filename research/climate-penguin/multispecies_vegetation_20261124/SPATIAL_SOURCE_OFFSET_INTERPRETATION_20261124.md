# Spatial offset of observed breeding-nest changes, 2026-11-24

Executed fixed-roster diagnostic; not migration, animal-to-land nutrient flux, or a climate effect estimate. Source original census-derived Git blobs and exact checks are in spatial_source_offset.mjs. Early 1991–2000 and late 2011–2020 site-species medians, >=2 recorded years in each window. The 43-row three-decade panel is a verified nested subset of the 50-row strict endpoint panel. Coordinates validated against the archived unambiguous census table; different census dates/methods are not guaranteed comparable; unobserved sites/species are excluded, not zero-filled.

## Same-species offset

Max-flow between losses and gains under great-circle distance constraints, gain capacity used at most once. Absolute lost-nest denominator. At radius 100 km, strict endpoints ADPE 26 sites: 3.943% (loss 12,325.5; gain 392,264), CHPE 12: 2.933% (loss 7,893; gain 231.5), GEPE 12: 100% (loss 1,085; gain 15,197). ADPE 19-site nested panel: 5.988%; site-deletion 0–12.942%, region-deletion 0–17.851%; strict panel region deletion 0–23.028%. GEPE strict panel site-deletion 90.876–100%. CHPE and GEPE panels unchanged between nested cohorts, not independent replication. GEPE/ADPE sampled geographic supports differ. In shared two source regions ADPE six sites all non-increasing (five declining, one zero at both endpoints); gain zero. No evidence of biological species differences independent of sampling geography. Relative redistribution diagnostic also computed, distinct from absolute count offsets; see JSON.

## Cross-species scenarios in common two regions

Fixed 30 site-species rows, 21 unique site IDs, South Shetland Islands and Central-west Antarctic Peninsula. Same site means exact shared site ID; all rows not simultaneously counted, and no complete species census is implied. Region-constrained max-flow for hypothetical common count units. Relative GEPE weight 0.5, 1, 2; ADPE and CHPE weights fixed at 1. Weights deliberately illustrative, not measured guano rates. No double use of gains. Same-species-only matching is a nested constraint and cannot exceed any-species matching.

| radius | Same species only (equal weights) | Any species (equal weights) |
|---|---:|---:|
| Same site | 0 | 25.901% |
| 1 km | 0.089% | 25.990% |
| 10 km | 0.118% | 31.791% |
| 25 km | 3.266% | 38.417% |
| 100 km | 6.324% | 44.724% |
| unlimited within region | 6.324% | 44.724% |
| unlimited without region constraint | not reported | 74.113% |

At equal weights, gross losses 20,817.5, gross gains 15,428.5, net -5,389 counted nests. South Shetland loss 18,188.5/gain 6,681.5 (net -11,507), 100-km any-species offset 36.735%; peninsula loss 2,629/gain 8,747 (net +6,118), offset 100%. In full two-region panel, 100-km offset ranges 27.797% (GEPE weight 0.5) to 76.064% (weight 2). The net count-weighted change even switches sign at weight 2 (+8,723). Site-deletion at equal weights 30.851–64.120%; block deletion 36.942–57.015%; two-region deletion 36.735–100%. Even unlimited within-region matching cannot exceed 44.724% at equal weights, because gains are geographically imbalanced. At 100 km allowing cross-region edges produces the same equal-weight result. This does not establish redistribution of actual nutrients: 100 km is a spatial diagnostic, not a validated delivery distance, and same colony codes do not define the same land patch. Species-specific N/P delivery, seasonal use, seal inputs, terrain and unobserved colonies remain unknown.

## Reproduction and decision

- spatial_source_offset.mjs (8b2f145772d045002fb3eccaac936b63f729c940)
- SPATIAL_SOURCE_OFFSET_RESULT_20261124.json (86a285d007ab9eadd25599d4af38c88e0b0be051)
- cross_species_source_offset.mjs (d1c6768fc28a3c55933e824f877a80d20a48bd1d)
- CROSS_SPECIES_SOURCE_OFFSET_RESULT_20261124.json (e688d80218bccbcb255c885544afe93a28c8b215)

Max-flow/min-cut equality checked for each run; endpoint identity and monotonic radius checks, nested-roster comparisons, nested-species constraint checks and complete-network capacity checks passed. No new inferential p-values. These are complementary to previous geographic centroid and concentration analyses, not a new independent biological replication. Next useful test is a matched co-survey census panel and small, empirically supported terrestrial exposure footprints with source-specific subsidy rates, rather than interpreting large radii as nutrient transport. Main and frozen manuscripts unchanged.