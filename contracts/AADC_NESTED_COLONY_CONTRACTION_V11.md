# V11 — nested contraction versus spatial relocation in original AADC East Antarctic colony polygons

**Status: post-V10 spatial outcome descriptive diagnostic, 2026-10-26.**
The V10 results (15 source original repeated-site transitions; Jaccard median
0.40336 and later/earlier colony mapped area median 0.45152) are **already
known**. This derived V11 estimator is not preregistered and no independent
confirmation, causal movement or hypothesis-significance claims are permitted.

## One exact site-year polygon-derived metric, independent of colony area arithmetic

Let first and later **mapped colony footprint areas** be A and B and the
intersection be I, at an identical original source `IS_<id>` as selected
outcome-blind in V10. Jaccard `J=I/(A+B-I)` will fall automatically when B shrinks,
even for *perfectly nested* mapped shrinkage. This is not evidence of relocation
or a distinct ecological displacement process by itself.

The maximal possible geometric overlap when one footprint nests in the other
is `min(A,B)`; the strongest achievable Jaccard conditional on the observed
areas is `min(A,B)/max(A,B)`. Report two area-adjusted descriptive quantities:

1. **Smaller-footprint inclusion** = `I/min(A,B)` in [0,1]. One means the
   smaller year footprint lies entirely within the larger (mapped contraction
   or mapped expansion without off-core displacement).
2. **Residual spatial mismatch** = `1-I/min(A,B)` in [0,1]. One means no
   overlap; zero means fully nested. Report complementary
   `J/J_max` as a bounded geometry-only check.

Crucially, even an observed small mismatch **cannot be called social site
fidelity or individual nest persistence**: the two polygons are mapped colony
boundaries, may incorporate a standard 2m buffer around subcolonies, and
published photography/gaps/positional registrations may differ by year.

## Frozen computational contract

- Read only **successful V10 original site-pair CSV**, SHA256 pinned in
  `results/AADC_REPEATED_ADELIE_COLONY_GIS_V10.json` and the original
  GitHub Actions artifact `40257955794`. If original 15 rows or 13 unique
  site IDs, HBE/HBW two groups, source seasons or SHA drift: STOP.
- Compute geometric metrics above for all 15 pairs. Preserve individual
  source-site and source-season IDs, raw area ratio and original Jaccard.
- Summarize both `n=15` independent **site-pair descriptions** and
  `n=13` **site-ID means** (so the one four-year site does not count
  as three independent island-level replicates). Report HBE and HBW
  distributions separately.
- Count the original pairs with area ratio < 1, = 1, >1; zero
  geometry-identical pairs are already known.
- Do not add arbitrary thresholds such as J>0.5 or p-values chosen from
  the result; no random relocation spatial null without a validated
  searched nesting area polygon.
- Document whether residual mapped mismatch could simply arise from
  original photo coverage, subcolony boundary buffer and georegistration
  errors; the new metric removes arithmetic area constraints but not
  observational biases.

This is a new raw-GIS derived ecological **description**, NOT new
causal island biogeography. To support the latter, independent age-matched
real colony counts, site-area, rock/ice substrate and per-season
survey footprints are still required.
