# Original Adélie 28-site exclusion mechanism, independently reproduced (23 November 2026)

**State: PASS. No isotope response was opened; no ecological model was refitted.**

Frozen original source gates come from the original `analysis/penguin-decade-redistribution-v1-20261110` branch, notably `research/climate-penguin/macro_panantarctic_v1/diet_salinity_source_20261117/extract_matched_novfeb_glorys.py`. The exact original author pixel rule (from Youngflesh et al. 2026, `Scripts/4-diet-est.R`) is documented separately at `docs/ADELIE_ORIGINAL_AUTHOR_PIXEL_SUPPORT_AUDIT_20261123.md`.

## Reproduced upstream sequence

1. Youngflesh original source has **146** projected colony centroids.
2. The strict source↔MAPPPD geographic crosswalk (595 atlas sites) accepts **102/146**: nearest MAPPPD site ID matches the Landsat site ID and is within **2,000 metres**; second-nearest site must be more than **2,000 metres** away.
3. Of 102, **100** have a site in the 1997 marine-source site roster (588 original sites). Of those, **99** have real observed Landsat seasons in the author's 1993–2013 source window, giving **892 actual source site×seasons**. These reproduce original published-pipeline gates.
4. Restrict original author-qualified pixel records to 2004–2010: **583 site×seasons / 113 sites**. The matched optical+marine data contain **439 site×seasons / 85 sites**. These retain **all seasons** for every included site; **28 entire sites / 144 site×seasons** fail crosswalking.

## Table: first failed source-matching rule for 28 excluded sites

| Sequential first failed gate | Sites | Site×seasons |
|---|---:|---:|
| Another MAPPPD site within 2 km, so matching ID not spatially unique | **12** | **58** |
| Nearest MAPPPD site ID differs from original Landsat ID | **8** | **42** |
| Nearest matching-ID MAPPPD site more than 2 km away | **6** | **33** |
| Absent from frozen 1997 original-marine source site roster | **2** | **11** |
| **Total** | **28** | **144** |

A "first failed" classification respects the source-pipeline ordering; two or more rules might be violated by the same site. An absent source-site marine row does **not** mean the ocean was absent or fully iced over.

The original source pixel inclusion alone contains **179,346 source pixels at 119 sites** across all years. The modern MPA analysis cohort was recovered without retuning any filter and is **439/85** with 34 truly measured zero-exposure site×seasons.

## Regional sample representation (2004–2010 source support)

| Reporting region | Excluded site×seasons | Original observed source site×seasons |
|---|---:|---:|
| Victoria Land | 38 | 136 |
| Mac. Robertson Land | 36 | 73 |
| Princess Elizabeth Land | 28 | 70 |
| Northeast Antarctic Peninsula | 17 | 91 |
| Marie Byrd Land | 10 | 44 |
| Central-west Antarctic Peninsula | 8 | 8 |
| Wilkes Land | 5 | 81 |
| Southwest Antarctic Peninsula | 2 | 43 |
| Remaining four original-source reporting regions | 0 | 38 |

These totals are descriptive, not independent environmental replicates. The complete omission of both Central-west Antarctic Peninsula source sites explains why the 2004–2010 source pool reports 12 regions but the final 439 sites occupy 11. Observations are selected geographically, including against dense-colony networks (12 sites fail the second-nearest gate). This limits generalization from the frozen 439 observations to the full original Antarctic source geography. It neither reverses nor independently confirms the exploratory original isotope association.

## Exact provenance and execution

- Original 146-site centroids (GitHub Actions artifact **14324288144**), original MAPPPD 595 atlas (**13669533413**), original 1997 marine-source roster from 588-site annual marine atlas (**13828472111**), original author-qualified 583 site×year panel (**14777168517**), pinned 113→85 source catalogue (**14777234122**), and original 892-source seasonal marine match (**14326721399**).
- Independent source-code implementation: `scripts/verify_adelie_28_site_source_geographic_gate.py`.
- Verified successful Actions run [#45093939224](https://github.com/zuizui0223/mina/actions/runs/45093939224). The artifact contains the full 113-site audit, per-region counts and a machine-readable exact-gate receipt.
- The 85-site MPA map is at [#45082480478](https://github.com/zuizui0223/mina/actions/runs/45082480478).
- Author review of **S8 and Table S6**, with no modification to the original v0.7.5 main manuscript, is isolated in [Draft PR #216](https://github.com/zuizui0223/mina/pull/216).

## Cautions

The *matching gates* and 28-site first-failed categories are now known. The field reason underlying the mismatched source coordinates/IDs is not independently verified. There is no measured penguin diet, demographic failure or conservation effect associated with exclusion. All evidence is the same published site-inventory sources; this audit only reduces reproducibility uncertainty.
