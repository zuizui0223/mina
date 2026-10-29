# Source-observed intervals across penguin species: V6

Goal: extend the independent geographic support beyond annual-only paired records, not retune the fixed44 climate result.

Architecture: use the SHA-fixed MAPPPD v5 source from run40868828790. Keep the old annual sample exactly; add only consecutive jointly observed seasonal endpoints, retain all longer gaps explicitly, block intervening explicit absence/zero, duplicate counts, invalid counts, and citation/vantage changes. No interpolated annual counts. Exact current SCAR containment diagnoses repeated mapped-land units; not historical nest polygons or certified ecological independence.

Outcome: (log(N_b,end/N_b,start)-log(N_a,end/N_a,start))/season_gap. Main site summary=sum log-ratio changes/sum observed seasonal gaps, then equal site weights; within land equally weight site summaries and then lands. Secondary equal-interval rates show whether duration weighting matters. Summarize annual-only, all observed intervals, nonannual-only and newly added source sites without picking a favorable direction. Three taxon contrasts separate; no pooling correlated differences.

No model of climate, no p-values, no change to V1–V5 thresholds, no claim of prospectively confirmed effects. Input count magnitudes were previously exposed in project; structure-only preview found no new ADPE–GEPE site, five extra CHPE–GEPE source sites, one ADPE–CHPE source site. These are newly used records, not newly collected or biologically independent measurements.

Task 1: implement and test exact source eligibility, chronology barriers, non-overlapping consecutive endpoints, numeric zero/absence distinct from missing, elapsed-season rate and weights. Watch synthetic tests RED and GREEN, then source execution with annual51/56/28 comparison.
Task 2: map unchanged source centroids with original SCAR helper; no snapping, no mainland promotion, no island interpretation for failed geometry. Pure aggregation tests first; live geometry in dedicated Actions. Save original land ZIP with source run artifact for independent local checking.
Task 3: verify the full repository pytest suite on GitHub in core dependency environment, run actual source code, download and independently recalculate all rates/summaries, preserve test/provenance receipts and archive. If full clone inaccessible locally, record that and do not claim a full local suite.

Implementation uses standard-library Python plus optional GIS dependencies at run-time only. Existing code and frozen Paper1/2 remain unchanged. Branch update must preserve latest head; no force push.

## Source version and execution

MAPPPD source: v5.0 / 2026-10-21, 5,487 original observations and 729 site registry rows. Original published source SHA pins are inherited exactly from matched species run40868828790; existing annual records are reproduced before geographic expansion. Full endpoint source IDs, elapsed seasons, counts and method/citation provenance remain inspectable. Count values and source records are not edited. The exact current land helper and Antarctica mainland feature exclusion (17692) are unchanged from the earlier mapped-land diagnostic. More source sites are NOT automatically more independent islands or climatic exposures.

This extension is a separate monitored-period estimand, not relaxation of a failed confirmatory threshold. Its multi-year intervals can share endpoints; three contrasts share species records. No new sea-ice correlation, p-value or independent-validation claim. Causal attribution and expanded environmental exposure remain untested. Frozen Ecology Paper1 and physical-island Paper2 are unchanged.

Output: observed_species_intervals_v6.csv and observed_species_intervals_v6_result.json; original land archive preserved in artifact. Full repository suite runs in the standard core environment; dedicated source execution adds GIS libraries after those tests. Previously failed third-party Dryad acquisition is not repaired or relabeled here.
