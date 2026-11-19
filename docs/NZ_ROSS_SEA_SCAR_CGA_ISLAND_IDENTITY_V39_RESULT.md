# V39 — Four original Ross Sea landmass names are SCAR-recognized islands, but nest GPS is still imprecise

**2026-10-24 executed source-only ontology validation** after V36 and unsuccessful V37/V38 exact-nest-location tests. Four source-named physical landmass groups in the original New Zealand Adélie 2026 aerial census (Ross, Beaufort, Coulman, Inexpressible) were compared against original SCAR Composite Gazetteer of Antarctica (CGA) source entries hosted by the Australian Antarctic Data Centre. The original source received independent publisher HTML SHA256 receipts; [GitHub Actions V39 #40077782430](https://github.com/zuizui0223/mina/actions/runs/40077782430) passed all invented-fixture tests and verified four live authoritative records.

## Distinguish two scientific questions

1. **Categorical landmass identity:** The original NZ colony-location workbook assigns colony names to named features (e.g. Ross Island, Coulman Island). The SCAR CGA independently confirms each is a recognized **Island (5)** with a distinct official feature record. These names are not invented by replacing a coordinate outside a polygon; the actual islands exist and are different landmasses.
2. **Accuracy of mapped nesting-site coordinate:** The same NZ workbook reports original nesting localities at only full arcminutes. V37 original 17,269-landpolygon high-res SCAR source found only one island surviving ±1 arcminute position-envelope containment, with no shared two-island comparison windows. New MAPPPD v5 published site centers in V38 also FAILED exact-source location-precision support. Official gazetteer *island centroids* themselves show **Unknown precision** and are never nest colony GPS. Thus this second question remains UNRESOLVED.

## Exact publisher-recognized island IDs

| Original source-named landmass | SCAR CGA hosted national record | Authoritative feature type | Original same-colony annual comparison windows from unchanged V35 |
|---|---|---|---:|
| **Ross Island** | US Gazetteer 130958 | Island (5) | 35 |
| **Beaufort Island** | New Zealand Gazetteer 112759 | Island (5) | 11 |
| **Coulman Island** | New Zealand Gazetteer 113061 | Island (5) | 5 |
| **Inexpressible Island** | New Zealand Gazetteer 113617 | Island (5) | 5 |

Four separate canonical SCAR feature types/IDs were retrieved verbatim over HTTPS and source SHA checks retained. The unchanged original V35 sample has **13 concurrent annual start windows** (1983–92, 2001, 2004, 2005) under source locality-name groupings. Six other NZ original colony labels have no exact match to the author location file, and are not silently included. Cape Bird N/M/S and Cape Royds are four monitored colonies on **one Ross Island**, not four islands.

### What the original ecological evidence can and cannot say

V36 genuinely computed the **source-named four-island** nested Adélie log1p breeding-pair index changes under the original case-by-case author locality grouping. On 13 years, **61.54% year-weighted directional agreement** (19 of 30 overlapping island pair/year comparisons) is a descriptive signal of nonuniform yearly breeding changes. Ross–Beaufort r=+0.468 (11 overlapping windows), Ross–Coulman r=−0.501 (5), Ross–Inexpressible r=−0.422 (5). The 2,000 diagnostic shuffled sign median was 51.3%, with original 5–95 percentile 33.3–69.2%; observed 61.5% is within that range.

**V39 validates the categorical name and physical-feature type only**. It does not promote these original V36 coefficients into independent causal, pre-registered, point-precision-robust physical-island results. Different actual authors, counting methods, stages, original event duplication, and original colony coordinate uncertainty are unresolved. Nested colonies and annual windows remain dependent observations; the original source is one Ross Sea geographic sector. Neither biotic interactions nor marine/wind/sea-ice forcing has been identified.

The key new distinction is *not* simply "four islands versus one": SCAR recognizes four physically separate landmasses, even though nest GPS locations cannot be independently verified at sub-kilometer accuracy. For a paper about **island identity**, authoritative CGA names/feature types and original survey-site landmass labels are meaningful. For a paper about **distance to coast, island area, accessible rock, precision-matched substrate or a physical water barrier's causal action**, source GPS and historical rock accessibility remain essential.

## Original sources and reproducibility

- SCAR Composite Gazetteer [Ross Island](https://data.aad.gov.au/aadc/gaz/display_name.cfm?gaz_id=130958), [Beaufort Island](https://data.aad.gov.au/aadc/gaz/display_name.cfm?gaz_id=112759), [Coulman Island](https://data.aad.gov.au/aadc/gaz/display_name.cfm?gaz_id=113061), [Inexpressible Island](https://data.aad.gov.au/aadc/gaz/display_name.cfm?gaz_id=113617).
- [V39 original authoritative name record SHA receipts](../results/NZ_ROSS_SEA_SCAR_CGA_FOUR_ISLAND_IDENTITIES_V39.json).
- [Exact original new geolocation site V38 limitation](NZ_ROSS_SEA_MAPPPD_V5_GEO_SOURCE_V38_RESULT.md).
- [Original V36 4-island ecological result](NZ_ROSS_SEA_GIS_ISLAND_GROWTH_V36_RESULT.md).
- Frozen source/CI: original New Zealand 2026 aerial census DOI https://doi.org/10.7931/kf06-x745; SCAR composite gazetteer official Australian Antarctic Data Centre.
