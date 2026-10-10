# V18 — Independent 2026 archive does NOT equal an independent biological census

**2026-10-10**. Public original New Zealand Ross Sea 2026 archive ([doi:10.7931/kf06-x745](https://doi.org/10.7931/kf06-x745); CC BY-NC 4.0), publisher original 39-site XLSX MD5 **195a9027a0d18012812b09fb345ac60e**, source-revalidated in [Actions #38038254900](https://github.com/zuizui0223/mina/actions/runs/38038254900). Three biological *original aggregate* published values reappear **exactly** when the 2026 archive's 2012 subcolony counts are summed to their prior 2014 source units:

| Same actual 2012 Ross Island source count | Lyver et al 2014 published Table 1 | NZ original 2026 archive with same census year |
|---|---:|---:|
| Cape Royds | **3,083** | **3,083** |
| Cape Bird (N+M+S) | **75,696** | **50,701 + 4,912 + 20,083 = 75,696** |
| Cape Crozier (E+W) | **272,340** | **30,147 + 242,193 = 272,340** |

The earlier primary paper is [Lyver et al (2014), *Trends in the Breeding Population of Adélie Penguins in the Ross Sea, 1981–2012*](https://doi.org/10.1371/journal.pone.0091188). Exact three-way overlap means **the 2012 original colony count observations are already published**, not three new independent external surveys or a validation on new birds. Do not claim the *entire 1981–2024 dataset* is redundant; years after 2012 and selected other areas extend published coverage, but must be checked for source-independence separately.

The source-only check is clearly exploratory/post-source-exposure and **NOT** a biological outcome or a newly published statistical theorem. All years and subsite aggregations use the publisher's original source and exact MD5, without distributing the copyrighted Excel. The CI tests reject a single-pair mismatch or missing original 2012 source cell rather than silently editing an aggregate.

## V17 adds a short-period off-Ross audit, but remains noncausal

Actual [2001 and 2005 matched-source geographic support CI #38038070701](https://github.com/zuizui0223/mina/actions/runs/38038070701) showed only **nine** source named sites with numeric breeding-pair counts in BOTH seasons:

| Source location group | Number of site rows | 2001 pair counts | 2005 pair counts | Ratio |
|---|---:|---:|---:|---:|
| Ross Island six subcolony sites | 6 | 94,798 | 254,617 | 2.686 |
| Other named physical breeding sites with exact publisher-geography match (Franklin Island East, Inexpressible Island) | **2** | 28,947 | 35,912 | 1.241 |
| Unmatched location source label (Terra Nova Bay) | 1 | 9,478 | 15,693 | 1.656 |

This does **not** provide a causal difference-in-differences. The 2001 census occurred during the B-15/C-16 disturbance, not before it; 1999 pair counts from those same off-Ross sites are missing. The count and date coverage alone cannot separate rapid *rebound from the 2001 low point* from higher underlying population growth, breeding participation or immigration. Six Ross source units are on one island, while exact independent-pair comparison has only two other sites. Sea-ice access and foraging conditions were not measured in the source file.

Most obvious mechanisms have already been identified empirically by marked individuals, not just inferred from the 2026 census:
- [Dugger et al 2010, PNAS](https://doi.org/10.1073/pnas.1000623107) estimated iceberg-associated breeding adult colony dispersal ~3.5% against normal under 1%;
- [LaRue et al 2013, PLOS ONE](https://doi.org/10.1371/journal.pone.0060548) documented increasing Beaufort Island nesting habitat and reduced post-2005 Ross Island visitation by Beaufort-tagged penguins;
- [Lyver et al 2014](https://doi.org/10.1371/journal.pone.0091188) already analyzed 1981–2012 Ross Sea colony trends and iceberg-era heterogeneity.

## Scientific decision

**HOLD_NOVEL_CAUSAL_ISLAND_RECOVERY_MECHANISM.** The real 2026 source adds temporal monitoring beyond 2012 in a restricted Ross Island system (six source components as of 2024) and independent archival provenance, but its historical observations cannot count as independent biological replication. The source is not age-specific tagged prospecting, first-breeding origins, chick success, or independently timed functional colony-sea access data.

The genuinely discriminating future test is still: separate (A) **arrival of identified potential breeders at a recipient colony**, (B) **choice to initiate an egg/nest despite arrival**, and (C) **chick production and later first recruitment** under independently dated access and habitat events, with properly matched receiving islands and known effort. Neither more post-hoc regressions on the same archival pair counts nor treating 39 sparse site names as 39 islands will establish a new mechanism.

**Reproducibility:** `contracts/ROSS_2001_2005_MATCHED_OFFISLAND_SOURCE_SUPPORT_V17.json`; `scripts/audit_ross_2001_2005_matched_offisland_source_v17.py` plus tests/workflow; `contracts/NZ_2026_VS_LYVER_2014_2012_CENSUS_PEDIGREE_V18.json`; `scripts/audit_nz_2026_vs_lyver_2014_census_pedigree_v18.py` plus tests/workflow.

Frozen Ecology PR189, marked source PR142 and emperor source PR195 unchanged.
