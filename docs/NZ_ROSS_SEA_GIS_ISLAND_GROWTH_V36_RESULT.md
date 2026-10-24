# V36 — True Ross Sea island breeding changes are geographically heterogeneous, not universally synchronized

**Executed October 24, 2026.** The independent 2026 New Zealand Adélie aerial nesting-pair source, author site list, and previously verified SCAR Antarctic Digital Database land polygons were linked WITHOUT changing source colony IDs or island/year sample after numerical outcomes. [Original-source CI and synthetic tests](https://github.com/zuizui0223/mina/actions/runs/40073531736) PASS. This is a prospectively frozen *within-exploratory-workflow* directional comparison, not independent external preregistration of a universal island result.

## Fixed data and genuine sample unit

- Original New Zealand 2026 DOI [10.7931/kf06-x745](https://doi.org/10.7931/kf06-x745), author census XLSX SHA256 `23a95d9e693dd095e085534f2c215b79880a72fe9cfb5a59337501192dae03e6`, 39 Adélie census colonies, 1981–2024.
- Original source colony-location SHA256 `d744e7493f85564f1b634f390a5e4a976b2d5359a6f93cdd9ef345639661b6a6`, checked against original SCAR 2026 ADD medium coastline SHA256 `b0172d698436f871f49339cea5c7155e3d98648360521cc4bbc44a026c0edc38`. V35 independently established 4 geographically different publisher-named island landpolygon IDs: **Ross (59), Beaufort (50), Coulman (37), Inexpressible (43)**. Source points marked "unique within 2 km" remain **provisional** due full-arcminute geolocation precision.
- Distinct island sample units: 4 maximum, not 39 colonies. Ross has 4 GIS-qualified original colony components (Cape Bird North/Middle/South and Cape Royds), Coulman 4 (Cape Anne and three Coulman sites), Beaufort 1 and Inexpressible 1. Between-year island response is equally weighted mean of changes in exactly the **same observed original colonies in both years**, not observed island-wide total growth.
- Method-document restriction: only original pair start years through 2016; source states **no 2020 survey** (never an observed zero). Exact V35 co-island start-year roster **1983–1992, 2001, 2004, 2005**, n=**13**. 10/13 windows are clustered in 1983–92. Unlike annual single-colony long series, these are not 13 independent multi-island experimental replicates.

## Primary measured ecological result

Original within-colony annual log(1+reported occupied nest count) changes were computed only after exact source genealogy/point/colony/year compatibility checks.

| Frozen metric | Original observational result |
|---|---:|
| 4 candidate separate physical island landmass groups | 4 |
| All fixed exact concurrent annual starts | 13 |
| Independent ISLAND-pair × annual-window sign comparisons | 30 |
| Pair-year comparisons with same direction | **19/30 = 63.3%** |
| **Equal-year-weighted across-island sign coherence (primary)** | **61.5%** |
| Remove each year one at a time, primary coherence | **58.3% to 66.7%** |
| Frozen 2,000 within-island independent sign shuffles, median | **51.3%** |
| Sign-shuffle reference 5th–95th percentile | **33.3%–69.2%** |

The observed 61.5% is within the descriptive shuffled reference range. The shuffling preserves island-specific sign prevalence and original observed-year availability, but **not temporal autocorrelation**, so it does not provide a defensible population-level ecological p-value. **Do not claim a statistically unusual shared island synchrony law.**

The signed observational response is *mixed*: seven calendar starts (1985, 1987, 1988, 1989, 1990, 2004, 2005) have unanimous same-direction among available islands, whereas 1983, 1984 and 1992 have opposite paired directions. Other years have partial agreement. That is descriptive temporal heterogeneity, not identified climate regime changes.

## All six fixed original island pair comparisons

Pairwise r is reported ONLY if at least 5 common original annual transitions exist:

| Original island pair | Same-year changes | Pearson r | One-window-out r |
|---|---:|---:|---|
| **Ross – Beaufort** | **11** | **+0.46837** | +0.26662 to +0.55624 |
| **Ross – Coulman** | **5** | **−0.50118** | not estimated: n=4 after deletion below frozen minimum |
| **Ross – Inexpressible** | **5** | **−0.42236** | not estimated: n=4 after deletion below frozen minimum |
| Beaufort – Coulman | 4 | not fitted | insufficient observations |
| Beaufort – Inexpressible | 3 | not fitted | insufficient observations |
| Coulman – Inexpressible | 2 | not fitted | insufficient observations |

**Biological interpretation:** Distinct Ross Sea island units do not have uniformly positive or uniformly negative annual breeding-index changes. A positive nearby-island association can coexist with opposite-sign or negatively associated other island pairs. This challenges an overly simple "every island within a sector follows one regional trajectory" interpretation, but **does not identify foraging connectivity, colony competition, sea ice, dispersal, island area, or any causal boundary effect**. In the n=5 comparisons Pearson r is particularly fragile, and shared years overlap across pair estimates.

## Two critical predeclared sensitivity limits

1. **Exact original SCAR polygon containment only:** If source localities assigned provisionally to their unique nearest land polygon (within 2 km) are withheld, only **two** islands have >=5 year windows and only **five** concurrent island-year windows survive. The predefined independent 3-island/8-year geographic-precision robustness threshold FAILS. Therefore V36 is **not a geometry-robust confirmation** of an island-level mechanism, even though GIS supplied candidate landmass separation.
2. **Leave out Ross Island:** Only **seven** multi-island shared year windows remain, below the frozen eight. Thus a claim that the same pattern occurs independently of the extensively monitored Ross Island complex is not identified; Ross Island anchors much of the dataset.

The original source methods PDF describes surveys through 2017 while a newer XLSX adds 2018–24; the V36 2016 upper start year protects against silently assuming later method continuity. The original colony count precision and aerial survey effort may differ among original years. Some NZ records likely also occur in historic APBP/MAPPPD; no double-counting as an independent field replication is justified.

## Scientific disposition and next actual information gain

**DESCRIPTIVE_ROSS_SEA_ISLAND_CONCORDANCE_WITH_GEO_AND_EFFORT_LIMITS.** The answer to the **narrow original-data question** is that local Adélie nesting-index changes among independently named GIS landmasses are *heterogeneous*, and the source data do not show an unexpectedly strong, geographically robust universal synchronized sign. This is a positive observed-variation description, not a biological null of all island interactions.

Do NOT manufacture a favorable source geography by changing the original 2-km threshold after viewing the r coefficients. Before a manuscript can credibly argue "island boundaries control spatial synchrony", collect or validate **high-quality colony GPS/coastline landpolygon assignments for multiple landmasses, matched year-wise census effort/stages, and independent marine exposure/individual resight data**; prospectively test these across additional island sectors. The already closed original APBP V27 multi-region consistent-synchrony gate remains unsupported, and Paper1 Ecology PR189 remains frozen.

- [Exact frozen V36 scientific design](../contracts/NZ_ROSS_SEA_GIS_ISLAND_GROWTH_V36.md)
- [Source-authenticated full V36 numerical and precision receipt](../results/NZ_ROSS_SEA_GIS_PHYSICAL_ISLAND_GROWTH_V36.json)
- [V35 independently verified original land polygon and annual observation eligibility](NZ_ROSS_SEA_SCAR_ISLAND_GEO_V35_RESULT.md)
- [The original New Zealand Adélie census publication](https://doi.org/10.7931/kf06-x745), publisher CC-BY-NC 4.0; acknowledge Manaaki Whenua Landcare Research and original contributors Dean Anderson, Michael Meredyth-Young and Esme Robinson.
