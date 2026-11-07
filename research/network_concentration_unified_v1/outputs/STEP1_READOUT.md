# Step 1 — fixed-endpoint macroecology readout (new derived calculation)

Source and endpoint lock: SHA256 `439bd6a0403d7698209e8e5c79676e44b3182618f35ef2dfacebe4a10b7c0783`.
B = 20,000 two-endpoint independent pooled-share multinomial draws per eligible count row.
This is an arithmetic fixed-share benchmark, NOT an observation-error-calibrated ecological null.
No Step 2–4 trait, SST, species-overlap regression or corrected p-values have been fitted.

Main network×species candidate records: **1529**; computed count-null: **680**; among macro-primary: **675**.
Shared physical-site species-pair candidates: **732**; computed count-null: **378**.

## Count-null outcome support by source

| Source | candidate rows | count-null computed | model/index/pending/nonestimable |
|---|---:|---:|---:|
| BAS_Signy | 2 | 2 | 0 |
| EMPE_Global | 8 | 0 | 8 |
| JNCC | 1483 | 663 | 820 |
| MAPPPD | 32 | 12 | 20 |
| Palmer_LTER | 3 | 2 | 1 |
| Ross_MAPPPD | 1 | 1 | 0 |

## Null noncomputation reasons

- asynchronous_epochs: 721
- computed: 680
- insufficient_components: 19
- model_joint_uncertainty_unavailable: 8
- nonpositive_total: 72
- total_below_two: 29

## Pair noncomputation reasons

- computed: 378
- insufficient_components: 279
- nonpositive_total: 55
- total_below_two: 20

## Source integrity

- `emperor_author_index`: `c887b9e1176b153345073281ebcaf6752ffb361023269afb5bdcfa371ec381ec`
- `jncc_revised_20240708`: `9edf05b8af0a44c3ca770f390120c4b99bcaae3ae35fd844a82982d6ad8116d4`
- `mapppd_pygoscelis`: `fcb622814d9aec674fb34ff5f8acd357f5508cf4bc1c63945e62d0c558fbc3c1`
- `palmer_within_island`: `b4ef04e2275ea779fc8fe54fa13528dc2052d37dd88a60c811d54c7601f67b16`
- `signy_within_island_ADPE`: `585f87928ed64d8982ef5bd86d8a785c38df65c39223d88ec17425854c786d62`
- `signy_within_island_CHPE`: `e50e98719ba5eedc6f5e617e0c7aa404ebfba15bc22a51e93e78cd4443bf787b`

## Interpretation and checks

- Matched site IDs are not interchangeable with physical islands. The UK JNCC network is a Country×Master-site administrative structure.
- Original parent/child count records are not added as independent study replicates.
- Local-resolution Palmer, Signy and Ross are not added to MAPPPD macro-primary as independent rows.
- Emperor model-mean allocation is descriptive; without joint posterior draws the multinomial count null is not applied.
- A terminal observed zero is retained, but Y is missing; zero totals are never replaced by last-positive census.
- Null quantiles describe simulated counts, not 95% confidence intervals of the observed Y.
- Surveys-per-epoch denominators and coordinate-derived island habitats are unknown unless the actual full original survey roster supports them; never equate the matched cohort with complete abundance coverage.
- Census adjusted counts, source-site boundary shifts, time-span differences and observational effort can still influence results.
- Sources whose originals cannot be byte-verified are retained as explicitly unresolved.
- All results are post-prior-evidence exploratory, not externally preregistered.
