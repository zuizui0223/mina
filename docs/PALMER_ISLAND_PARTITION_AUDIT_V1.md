# Palmer island-partition v1: invalid-gate audit

Date: 2026-09-27

## Status

**V1 is closed as INVALID, not as a negative biological result.**

The design and decision rules were frozen before the primary result was opened.
The predeclared complete-unit validity gate required every island to retain at
least two eligible colony units and at least 75% of all unique reported
`colony_code` values. Christine Island retained 11/15 = 0.7333 and therefore
failed the gate. The threshold will not be lowered after outcome access.

Frozen provenance:

- branch: `analysis/island-partition-v1`
- workflow run: `36317485881`
- head SHA: `eb2bc5ca10d69094a3a54c23ad94cd0550f10c8a`
- artifact id: `10930934109`
- artifact digest: `sha256:00c18ad25d43179ebc1ddfd4a74a06498e9b68c6a39f8359d6c58a9aff04b6fd`
- Palmer LTER census SHA256:
  `b4ef04e2275ea779fc8fe54fa13528dc2052d37dd88a60c811d54c7601f67b16`

## Why the validity gate failed

The complete-case design exposed a problem with treating `colony_code` as a
time-invariant physical subcolony identifier.

| Island | Code | Presence pattern | Diagnostic implication |
| --- | --- | --- | --- |
| CHR | 11.0 | 2007–2017 only; recorded abundance always zero | late code appearance is not an active-colony trajectory |
| CHR | 3.1 | 1991–2006; positive in 10 years | a biologically used unit disappears from later code records |
| CHR | 4.2 | 1991–2006; positive in 8 years | same problem |
| CHR | 7.0 | 26/27 years; missing only 2006; positive whenever present | complete-case filtering discards a major active unit because of one missing code-year |
| TOR | 19.0 | 26/27 years; missing only 2014; positive whenever present | possible coding discontinuity/lineage issue |
| TOR | 19.1 | appears only in 2014 with one pair | cannot be treated as an independent 27-year physical unit without external evidence |
| TOR | 6.0 | 1991–2006; positive through 2001 | historical unit disappears from later code records |

Zeros are explicitly recorded for many inactive colony codes in the census, so
absence of a code cannot automatically be recoded as zero.

The Palmer LTER metadata describes `colony_code` as an island-specific nominal
code. Historical Torgersen material also uses numbered colony identities, while
later spatial work documents fragmentation and persistence within historical
footprints. Therefore the raw code field is not yet sufficient evidence that a
code is a persistent physical subcolony unit across the full time series.

## Outcome diagnostics retained for provenance only

Because the validity gate failed, the following values are **not confirmatory
support**. They are retained to prevent selective re-analysis and to motivate
the independent identifier-resolution gate.

Observed complete-unit diagnostics:

- within-island Fisher-mean annual-growth correlation = **0.1991**
- between-island Fisher-mean annual-growth correlation = **0.0937**
- observed within-minus-between contrast = **+0.1054**
- abundance-matched pseudo-island two-sided permutation p = **0.0030**
- mean within-island annual-growth synchrony phi = **0.2553**
- synchrony among island-total annual growth = **0.4405**
- hierarchy gap = **+0.1853**

The spatial-insurance prediction points in the opposite direction from the
original working hypothesis. Mean within-island growth synchrony is higher, not
lower, than in abundance-matched pseudo-islands; its lower-tail permutation
p is 0.9988. The observed hierarchy gap is also smaller than pseudo-island
expectation (upper-tail p = 0.9793).

The raw-abundance Wang–Loreau synchrony values are high on every island
(phi = 0.876–0.953), implying little abundance-level portfolio insurance among
the retained colony units.

## Revised ecological hypothesis

The result does **not** justify reopening H2 ("loss of spatial insurance
precedes collapse"). Instead it motivates a different, sharper hypothesis:

> Geographic islands may act as local demographic covariance domains nested
> within a broader regionally forced metapopulation.

Under this hypothesis, subcolonies on the same island share local land/snow/
geomorphic forcing and therefore co-fluctuate more strongly than equally
sized pseudo-groups, while broader marine forcing synchronizes island totals at
a larger scale.

This is only a working hypothesis until persistent physical subcolony identities
and distances are independently resolved.

## Mandatory next gate

Do not change the 75% threshold, completeness rule, synchrony metric, growth
transform, number of abundance strata, or permutation scheme to obtain a valid
v1 result.

The next scientific step is an independent `colony_code` ↔ physical
subcolony/GIS crosswalk using published maps, tables, supplements, LTER
documentation, or georeferenced spatial products. Count-trajectory similarity
must not be used to infer aliases.

Only after that crosswalk is frozen should a distance-conditioned island-boundary
test be specified.
