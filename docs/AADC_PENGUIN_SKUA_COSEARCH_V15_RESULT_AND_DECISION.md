# V15 — Real original Antarctic penguin × flying-bird co-search support: STOP

2026-10-20. Focal original-data structure test, outcome-blind for two-species P/A associations, based on the preregistered [V15 gate](../contracts/AADC_PENGUIN_SKUA_COSEARCH_V15.md). The source-only test and six synthetic controls passed in [GitHub Actions #39383947582](https://github.com/zuizui0223/mina/actions/runs/39383947582); independent pull-request event also passed. **No biological association model or two-species presence/absence contingency was fitted or opened.**

## Source and exact observational grain

- Official AADC 2025 geographic frame: 7,785 original geographic IDs, of which **4,476** are independently valid island geography with positive mapped area and finite location after the predeclared island-only gate. The full AADC source has 33,107 eight-species search records, hashed independently in V13.
- Match original **Adélie (ADP)** with **south polar skua (SK)**, and separately with **snow petrel (SP)**, only at precisely equal publisher geographic-site IDs and original six-digit breeding-season IDs.
- Only single original source records with directly author-reported presence or explicit absence and consistent original certainty are eligible. Whole ambiguous duplicate site/species/season groups, nonreporting (NR), different seasons and continent-coded sites never become positive pairings or pseudozeros.
- Unit for spatial replication is a publisher-defined coastal island geographic site; repeated annual reports are not distinct islands. A region is a 250-km EPSG:3031 grid, not automatically an ecologically independent source community.
- **No biological direction estimated:** status P versus A was used only for source eligibility and was not cross-tabulated.

## Original structure-only findings

| Metric | Adélie × south polar skua | Adélie × snow petrel (fixed comparator) |
|---|---:|---:|
| Matched geographic site × breeding-season records | **1,061** | **701** |
| Distinct original island geographic sites | **96** | **89** |
| 250-km blocks with ≥5 paired sites | **5** | **5** |
| Explicit same-calendar-day paired records | **8** | **1** |
| Distinct co-dated sites | **8** | **1** |
| Distinct blocks containing co-dated sites | **1** | **1** |
| Same source vantage text | **1,056** | **697** |
| Matching source obs_number text | **1,061** | **701** |

The strongest site-season pairing is geographically uneven: the 250-km block 6_-8 alone holds 51 of the 96 matched ADP–SK island sites; the other seven blocks each hold 1–14. The primary fixed data gate requires ≥30 co-dated site-season records from ≥20 islands across ≥4 blocks. It **fails** (8, 8, 1), despite passing the ≥60-site and ≥5-supported-block totals. The SP fixed comparator passes its site/block support gate. This does not rescue the missing primary common-observation denominator.

An apparently exciting but invalid inference would be “identical obs_number = independent joint co-survey.” It matches in **all 1,762** paired rows, yet the original AADC publications do not establish that this column is a globally unique observer/visit identifier across the separately compiled Adélie and flying-bird workbooks. Same-vantage labels are also nearly universal; neither equals independently observed simultaneous field effort. Moreover, the source paper explicitly describes a **constructed m species × n sites × p seasons search-event expansion from heterogeneous source material** and combines flying-bird references with an independently compiled Adélie database. Merely pairing those rows cannot reconstruct a joint field visit or a detection-corrected co-occurrence risk set.

The published paper already mapped detection/ignorance/richness biases, and the basic penguin–skua predation relationship is established prior art. Testing naïve ADP–SK spatial co-occurrence on these records would risk reporting source-construction and survey-focus correlations as ecological interaction or a new island-specific mechanism.

## Scientific disposition

**STOP_INSUFFICIENT_OR_UNMATCHED_INDEPENDENT_COSURVEY_SUPPORT.** The result concerns the availability and granularity of joint observation evidence; it is **not** evidence of zero ecological association, zero predation or lack of biological connectivity. This archive cannot identify a new pan-Antarctic prey-subsidy/predator nesting effect under the frozen independent co-survey gate. Do not rescue V15 by matching neighbouring islands, adjusting source seasons, classifying NR as absence, changing the focal species or relaxing the original gates after observing this result.

The genuinely missing input is independently recorded same-visit survey identity/effort for multiple breeding seabird taxa on the same Antarctic islands, plus independent contemporaneous nesting substrate. An independently sampled multi-taxon programme is needed, not a second regression on expanded historical search references. No AADC source data, V14 fit or frozen Ecology PR189 science was modified.

Machine-readable original source receipt: [V15 result](../results/AADC_PENGUIN_SKUA_COSEARCH_SUPPORT_V15.json).

### Primary sources
- Southwell & Emmerson 2025 original AADC DOI: https://doi.org/10.26179/5n29-r073
- Southwell et al. 2025 *Diversity and Distributions*: https://doi.org/10.1111/ddi.70066 (149 heterogeneous source references; construction of m×n×p source-event records)
- Australian Antarctic Program, south polar skua species ecology: https://www.antarctica.gov.au/about-antarctica/animals/flying-birds/south-polar-skua/
