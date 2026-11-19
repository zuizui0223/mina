# V14 — AADC nesting guild × island area: reproduced result and decision

**Current status: 2026-10-20.** The original AADC data are accessible, the
site/survey join is complete, and the frozen V14 model has been run and
independently reproduced. This route is no longer waiting for source access.
**The prespecified predictive-support conditions failed. The island-specific
three-way interpretation also fails the prespecified physical-overlap rule.**
This is not an estimate of a zero ecological effect, nor evidence that nesting
substrate is biologically unimportant. No positive macroecological mechanism
has been established by V14.

The review and reporting completion below retain the original cohort, guilds,
models, regularization, folds, weighting, and decision thresholds. The
original 2026-10-19 execution is preserved separately. All 115 numerical
fields in that original receipt reproduce exactly; the included-row CSV has
the same SHA-256. Ecology PR #189 remains separate and unchanged.

## 1. Question and actual analysis population

The frozen question was whether coarse nesting mode modifies the association
of static mapped site area and island/continental-outcrop classification with
reported breeding presence, after species identity, geographic location,
season, research-station distance and survey attributes.

The source database covers eight Antarctic land-breeding seabird taxa. V14's
fitted comparison uses **seven flying species**, with multiple species in each
of the OPEN, LEDGE and CREVICE categories. It is not a seven-species penguin
analysis and does not estimate an Adélie-versus-flying-species effect.

| Data stage | Verified count | Meaning |
|---|---:|---|
| 2021 geographic reference | 4,884 sites | Earlier coastal spatial reference |
| 2025 geographic reference | 7,785 sites | Updated island/continental ice-free feature frame |
| Original eight-species search records | 33,107 | 11,089 Adélie + 22,018 flying-seabird records |
| Flying-species records in valid 1980–2020 seasons | 13,723 | Before duplicate/status/geographic filters |
| Unique direct P/A records after duplicate exclusion | 7,069 | Complete duplicate groups excluded before status selection |
| After certainty linkage and geographic validity | 6,991 | Seven certainty mismatches and 71 invalid geography rows excluded |
| Final V14 responses | **6,956** | Unique site × species × breeding-season records |
| Final geographic sites | **368** | **295 islands + 73 continental outcrops** |
| Final site × species histories | **1,581** | Each history has total weight one, despite repeat seasons |
| Held-out spatial blocks | **8** | 250 km EPSG:3031 grid cells; ≥5 sites each |

The final sample contains **1,988 reported presences and 4,968 directly
reported absences**. NR is not recoded as zero. Twenty-six duplicate
site/species/season groups (57 rows), including four with inconsistent source
status categories, were excluded in full. Years denote the start of the
source breeding season, 1980/81 through 2020/21.

The 2025 source publication reports 33,297 search events; that published total
is not substituted for the **33,107 rows in the actual pinned workbooks**.
Version/content discrepancies are retained explicitly. The original authors
already investigated occupancy knowledge, ignorance, richness and survey
bias. Neither their dataset size nor those patterns are new V14 discoveries.

## 2. Frozen results

Lower Brier scores are better. The primary score averages the eight held-out
blocks equally, using site × species history weights inside each block.

| Model | Primary mean block Brier | Global history-weighted Brier | Ordinary original-row Brier |
|---|---:|---:|---:|
| B0: species, survey and geography | 0.3103778025 | 0.2628639058 | 0.2873831369 |
| B1: B0 + area, island, area × island | 0.3562448217 | 0.2776883148 | 0.2599356574 |
| B2: B1 + six nesting-guild interaction terms | 0.3590335529 | 0.2783739124 | 0.2633711844 |

B1−B2 = **−0.0027887312** on the primary score: adding the guild bundle
worsens regional prediction. Only **3/8** blocks improve, below the frozen
requirement of **6/8**. B0−B1 = **−0.0458670192**, so the physical-area bundle
also worsens the primary score.

### Why the denominator matters

Ordinary observation-row averaging gives an apparent B0→B1 improvement
(0.2874→0.2599), whereas both history weighting and equal-block weighting
give deterioration. This is a descriptive diagnostic of this fitted sample,
not a new ecological discovery. Block `6_-8` contributes **5,313/6,956 =
76.38%** of original records but only 59 sites and 404 site/species histories.
Those repeats must not be presented as thousands of independent islands.

The ordinary-row score was required by the contract but was missing from the
old numerical receipt. It is now exported under `original_row_Brier`.
The existing `weighted_observation_Brier` is retained for compatibility and
explicitly defined as the global **history-weighted** score. No primary metric
was changed or selected after inspecting results.

All three primary Brier values exceed 0.25, the error of an uninformative
constant probability of 0.5 for any binary observation. That arithmetic
reference was not a prespecified model-selection gate; it is included to
prevent an overstrong interpretation of the negative result. These models
do not provide reliable generalization to the held-out regions, so their
failure cannot establish biological irrelevance of island area.

## 3. Physical comparability and sensitivities

The contract requires at least eight distinct sites per land class and
strictly positive overlap of the island and continental area IQRs for every
guild. All guilds satisfy the count requirement, but CREVICE fails area
comparability:

| Guild | Island sites | Continental sites | Island log10-area IQR | Continental log10-area IQR | IQR overlap |
|---|---:|---:|---|---|---:|
| OPEN | 222 | 57 | 3.1937–5.1722 | 4.1612–5.7982 | +1.0110 |
| LEDGE | 220 | 57 | 3.1515–5.0714 | 4.1612–5.7465 | +0.9102 |
| CREVICE | 177 | 37 | 4.2944–5.4005 | 5.6451–6.6258 | **−0.2447** |

Areas retain the source's raw GIS units; no unverified unit conversion or
claim of measured suitable nesting capacity is introduced. Guild site counts
overlap because several guilds can be reported at the same geographic site.

The CREVICE three-way coefficient is positive in the primary full fit and
after omitting the implemented largest block (+0.00284 and +0.14881).
This single passed condition does not override the failed score,
block-consistency and overlap conditions.

- **Ground vantage only:** primary Brier B0 0.3332863, B1 0.3765075,
  B2 0.3794483; B1−B2 −0.0029408; only 3/8 blocks improve. The three-way
  coefficient changes sign after largest-block omission (−0.00611→+0.15453).
- **Expert-validated only:** 6,322 records, 237 sites, but only **7** eligible
  blocks. The frozen eight-block requirement fails; no sensitivity model was
  fitted by lowering the gate.

## 4. Interpretation and review findings

The scientific disposition has two separate parts:

1. **Predictive support failed:** the fixed guild-feature bundle did not
   improve transfer to held-out geographic blocks.
2. **The island-specific three-way interpretation is not identifiable under
   the frozen overlap criterion:** the island and continental samples for
   CREVICE occupy materially different central area ranges.

The machine-readable original decision remains
`NOT_SUPPORTED_OR_UNIDENTIFIABLE`; neither component is a proof that the
biological effect is zero. The source is a nonrandom collection of recorded
searches. Reported absence is not perfect detection, and static feature area
is not contemporaneously measured nest substrate. B2 adds six terms jointly,
so even a positive comparison would not isolate the three-way coefficient or
demonstrate a mechanism.

Read-only independent review found no train/test outcome leakage or
duplicate/status filtering error that reverses the result. All 368 site IDs
stay within one held-out block, and imputation/scaling use training rows
only. The review identified reporting details now made explicit:

- `largest_heldout_block` means **largest by unique sites**, with raw rows as
  a tie-breaker, as the original code implements. The contract's
  “largest-data block” wording was ambiguous. The implemented block is
  `8_2` (132 sites, 712 rows, 603 histories), not the raw-row-largest `6_-8`.
  The definition has not been changed after outcomes.
- All B0/B1/B2 absolute block scores and their denominators are now exported.
- Final site totals are 295+73; the older 297+84 QA counts describe the
  sample **before** the minimum-sites-per-block filter.
- Spatial grid holdout does not guarantee independent observers or source
  groups. For example, source subgroup `CON_SG_01` spans three grid cells.
- The historical key `raw_eight_flying_species_search_rows` is misnamed:
  its 22,018 entries describe the **seven** fitted flying species. The
  historical field is preserved rather than silently rewriting the original.

## 5. Execution, provenance and current next state

Five workbooks were retrieved again from the official public AADC object
API, following its advertised redirect to `transfer.data.aad.gov.au`.
All sizes and V12/V13-pinned SHA-256s matched. Rebuilding V13 with the
unchanged source parser produced exact input CSV hashes:

```text
Geographic sites: 48c716c38c41a054eefc20c03de3c21d75047049e6e277d471d9b9135aab7da5
Search records:   dba39d79f6309f90e23e896415177ea75086aaf2ecb5523256e48895e95dfc5c
V14 included rows:9343c9c7a491178a9ceda489f77a389d2c2fb907c15782eac3ba52ff799df4b5
```

The original run and reporting-complete replay agree exactly on every
previously exported numerical field and scientific decision. **27 focused
tests passed** across V11–V14. A new unequal-history test first reproduced the
missing reporting fields, then verified that raw-row, history-weighted and
equal-block summaries retain distinct, reconcilable denominators.

Reproduction commands, using the existing source and model programs:

```bash
python scripts/join_aadc_original_site_occupancy_v13.py \
  --out-json data/aadc/V13_QA.json \
  --out-sites data/aadc/AADC_ORIGINAL_7785_GEOGRAPHIC_SITES_V13.csv \
  --out-surveys data/aadc/AADC_ORIGINAL_33107_BREEDING_SEARCHES_V13.csv

python scripts/fit_aadc_nesting_guild_island_area_v14.py \
  --sites data/aadc/AADC_ORIGINAL_7785_GEOGRAPHIC_SITES_V13.csv \
  --surveys data/aadc/AADC_ORIGINAL_33107_BREEDING_SEARCHES_V13.csv \
  --json data/aadc/V14_RESULT.json \
  --csv data/aadc/V14_ELIGIBLE.csv
```

**Completed:** original data access, exact V13 reconstruction, V14 primary
and frozen sensitivity evaluation, independent code review, numerical result
recovery, and correction of stale repository/PR status.

**Closed:** V6, V8 and V14 proposed environmental mechanisms are not supported
by their respective frozen tests. Do not re-run V14 with different guilds,
spatial radii, overlap thresholds or data weights to manufacture support.

**Unresolved scientific requirement:** no tested macro route currently
identifies the proposed Antarctic island-breeding mechanism. A further
mechanistic comparison needs directly measured nesting substrate and a
comparison design with comparable land-area ranges and survey ascertainment.
Repeated source verification or an extra fit on the same frozen cohort is
not an independent biological advance. No new positive effect, paper-ready
macroecological law, or automated follow-on model is claimed here.

## Sources and durable outputs

- [Original V14 run, 39271034255](https://github.com/zuizui0223/mina/actions/runs/39271034255),
  commit `31616bc8b9d1b678d0444660bc815feb4b002625`.
- [Original V13 source-join run, 39268125503](https://github.com/zuizui0223/mina/actions/runs/39268125503).
- [Southwell et al. 2021 geographic reference](https://doi.org/10.26179/53yk-8z83).
- [Southwell & Emmerson 2025 original survey database](https://doi.org/10.26179/5n29-r073).
- [Southwell et al. 2025 source study](https://doi.org/10.1111/ddi.70066):
  prior art for knowledge/ignorance, occupancy mapping and survey bias.
- [Frozen V14 contract](../contracts/AADC_EAST_ANTARCTIC_NESTING_GUILD_AREA_V14.md).
- [Reporting-complete numerical result](../results/AADC_GUILD_ISLAND_AREA_SPATIAL_CV_V14.json).
- [Unchanged historical result](../results/AADC_GUILD_ISLAND_AREA_ORIGINAL_RUN_20261019.json).
- [Exact-reproduction receipt](../results/AADC_V14_REPRODUCTION_20261020.json).
- [Block-level comparison table](../results/AADC_V14_BLOCK_SUMMARY_20261020.csv).
