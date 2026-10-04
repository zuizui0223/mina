# MAPPPD regional breeding-site concentration synthesis v1

**Status:** bounded existing-data extension. This analysis does not reopen the frozen Ecology Report and does not use SMP data.

## Question

Does the breeding-space contraction pattern discovered within penguin breeding systems also appear one spatial level higher, among repeatedly monitored breeding sites inside published APBP regions?

The parent unit is **species × APBP region** and the components are fixed monitored site_id values. These are geographic monitoring networks, not assumed closed demographic populations.

## Frozen implementation

The analysis reuses the pinned MAPPPD snapshot at commit 88c73a507e0921b2541c218c71eaf16721bc6502 and the already frozen Paper 2 observation cohort/calibration. Repeated same-season counts are corrected for the previously estimated image-vs-direct offset and precision-collapsed using the frozen accuracy model.

Eligibility is based on coverage only: at least three retained sites, five complete seasons, and a ten-year calendar span. A deterministic pruning rule removes the sparsest site until the first qualifying fixed roster is reached. Count magnitude does not enter roster selection.

For each eligible network, E = 1/sum(p_j^2), and log(E_t) = alpha + kappa_obs log(N_t).

The fixed-composition null preserves the observed total trajectory while drawing site counts from time-invariant pooled shares. A second null adds the frozen observation-error structure on the log1p scale. The focal effect is delta-kappa = kappa_obs - median(kappa_null).

## Structural support

Thirteen species × region groups were present in the frozen cohort. Seven passed the fixed-roster support gate, spanning all three Pygoscelis species and three APBP regions:

- Adelie: Central-west Antarctic Peninsula, South Shetland Islands, Victoria Land
- chinstrap: Central-west Antarctic Peninsula, South Shetland Islands
- gentoo: Central-west Antarctic Peninsula, South Shetland Islands

Four of the seven eligible networks were declining over their retained complete seasons.

## Declining networks

| Species | Region | Sites | Seasons | raw kappa | observation-error calibrated delta kappa | p | Robust panel support |
|---|---|---:|---:|---:|---:|---:|---|
| Adelie | Central-west Antarctic Peninsula | 3 | 5 | 0.080 | +0.073 | 0.108 | no |
| Adelie | South Shetland Islands | 4 | 7 | 0.088 | +0.115 | 0.0148 | yes |
| Chinstrap | Central-west Antarctic Peninsula | 3 | 10 | 0.022 | +0.017 | 0.432 | no |
| Chinstrap | South Shetland Islands | 6 | 8 | 0.445 | +0.434 | 0.0152 | yes |

All four declining networks have positive null-calibrated kappa. The median observation-error-calibrated effect is **+0.094**. The exact sign count is 4/4 (nominal one-sided sign p = 0.0625), but species × region panels inside the same region are not independent geographic replicates, so that p-value is descriptive rather than a macroecological generality test.

The important split is geographic: both South Shetland panels survive the observation-error null, while both Central-west Antarctic Peninsula panels point in the same direction but do not.

## Increasing networks: descriptive context only

Three eligible networks increased in abundance: Adelie in Victoria Land and gentoo in Central-west Antarctic Peninsula and South Shetland Islands. Their observation-error-calibrated delta-kappa values were **-0.355, -0.228, and +0.020**, respectively.

Notably, effective breeding-site number was lower at the final than the first retained season in all three increasing networks. This is qualitatively consistent with the pre-existing slow-state / weak-recovery hypothesis from the five-population contraction analysis, but the regional contract did not freeze a formal ratchet test for these panels. It is therefore descriptive corroboration, not new confirmatory evidence for hysteresis.

## What the existing data now support

The result strengthens the claim from a purely within-island phenomenon to a **cross-scale Antarctic Pygoscelis pattern**.

At the local scale, the existing Palmer and Signy analyses show concentration beyond proportional thinning in five populations across two species and two monitoring systems. At the regional scale, every estimable declining MAPPPD network shifts in the same concentration direction after panel-specific null calibration, and two species in the South Shetland network remain individually supported after the frozen observation-error sensitivity.

The strongest defensible synthesis is:

> **Population loss in Antarctic Pygoscelis is repeatedly accompanied by redistribution of breeding effort toward fewer effective breeding components beyond proportional thinning, and the same direction can persist from within-island breeding structure to networks of breeding sites. The strength of that regional-scale response is geographically heterogeneous.**

## Boundary

This is not a general seabird macroecological law. Taxonomic breadth remains Pygoscelis, only two species contribute declining regional networks, and the two robust regional results come from the same geographic region. MAPPPD sampling is sparse and geographically uneven, and the retained fixed-site networks describe repeatedly monitored components rather than complete regional occupancy.

The correct upgrade is therefore **cross-scale generality within Antarctic Pygoscelis**, not universal colonial-breeder generality.

## Stop rule

No alternate regional definitions, distance radii, hand-built clusters, completeness thresholds, lags, collapse hinges, or trait searches are opened in response to these results.
