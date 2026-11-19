# V38 — Original APBP published colony georeferences do not solve Ross Sea coordinate precision

**2026-10-24.** Original SCAR/AntOBIS Antarctic Penguin Biogeography Project (APBP v2.3), DOI [10.48361/zftxkr](https://doi.org/10.48361/zftxkr), 4,055 original Event records and 719 unique source locationIDs, fetched from the source-pinned original DwC-A ZIP SHA256 `afa947f39d9ad7382266d5be64c70f9fe4e84ffb6e2838c1369e043caae09abf`. Matched only exact original publisher locality strings to the 33 original NZ aerial Adélie author colony/location-ID pairs DOI [10.7931/kf06-x745](https://doi.org/10.7931/kf06-x745), whose census and locality original source SHA256 were independently checked. [Successful original-source CI #40076576836](https://github.com/zuizui0223/mina/actions/runs/40076576836).

## Original named colony match and uncertainty numbers

- **21/33** NZ source colony names match EXACT one APBP original locationID and one consistent Event locality label; the remaining 12 have no exact matching original APBP locality ID.
- **14** exact-name sites: APBP author-published original coordinateUncertaintyInMeters exceeds the frozen 250 m threshold. Source reported uncertainties range into kilometres (e.g. Beaufort Island reported 1248 m, Cape Bird North 1732 m, Coulman Cape Anne 4291 m, Inexpressible Island 5300 m).
- **7** additional exact-name sites: original APBP point is **more than 3 km** from the original NZ source minute-rounded colony coordinate. Examples include Beaufort Island 5481.5 m, Cape Royds 3978 m, Franklin East 6223 m, West 5493 m and SE Promontory ~29 km. Such points may reflect source nesting footprint centers, measurement definitions or erroneous georeferencing. The original source alone cannot choose a better location after the V36 outcomes are known.
- **ZERO** original APBP locationIDs passed all frozen requirements (name uniqueness, ≤250 m published uncertainty, ≤250 m within-original locationID coordinate drift, ≤3 km NZ source location consistency, not just a copied rounded coordinate).
- Thus no Ross Sea original V35 4-island source panel could gain an independently precise georeference from APBP: **0 islands with ≥5 source-paired annual windows**, **0 shared year windows**, and no potential V39 ecological effect is authorized.

All APBP original fields inspected were **Event location identity and original coordinate uncertainty**, NOT penguin nest counts. Some Event records may republish the identical NZ original colony-year observations; treating them as independent populations or new field samples would be incorrect.

## Scientific outcome

**HOLD_NO_INDEPENDENT_APBP_PRECISE_GEOLOCATION_SOURCE_SUPPORT.** A high-resolution 2026 coastline by itself does not resolve a rounded 1-arcminute colony location (V37), nor does borrowing APBP geographic coordinates with kilometre-scale source uncertainty. The V36 13-year source-named island growth result remains observational, real, and NOT promoted to a source-geographically stable physical-island causal law.

Next independent geography evidence can separate *official named island identity* from *precision of the colony point*. If an authoritative Antarctic place-name gazetteer corroborates Ross/Beaufort/Coulman/Inexpressible island *names*, this can support the **named landmass category**, but it cannot retrospectively improve the original colony-point GPS precision or annual breeding-site attributes. No manual coordinate replacement, fuzzy alias, GIS threshold relaxation, observational p-values or mechanism fitting is justified from APBP.

- [V38 source-locked outcome-blind contract](../contracts/ROSS_APBP_EXACT_GEOREFERENCE_SOURCE_V38.md)
- [Exact all-33-site APBP source match, uncertainty, spatial disagreement result](../results/NZ_ROSS_APBP_EXACT_GEOREF_QA_V38.json)
- [V37 official high-res coastline position uncertainty](NZ_ROSS_SEA_HIGHRES_PRECISION_V37_RESULT.md)

## 2026-10-24 methodological correction — APBP polygon extent is not a GPS error estimate

The prior V38 language treated APBP Darwin Core coordinateUncertaintyInMeters as an original field-GPS POSITIONAL ACCURACY or measured localization error. This was **incorrect**. The APBP v2.3 original dataset description explicitly defines the Adélie measure as the **average distance from the vertices of a polygon known to contain the colony to the colony site's reported centre coordinates**, rather than a GPS error distribution. Source: https://pmc.ncbi.nlm.nih.gov/articles/PMC10848690/ (the data dictionary for coordinateUncertaintyInMeters); original DOI 10.48361/zftxkr.

Therefore the earlier 14 names with values above the frozen 250 m cutoff **cannot be counted as 14 GPS-imprecise coordinates on that basis**. They are 14 original source COLONY-FOOTPRINT size/uncertainty metrics above an ad hoc 250 m sampling threshold, and that threshold cannot certify or reject independent field-position accuracy. The other seven exact-name original APBP source centres disagree with the coarse NZ source centre by more than 3 km; these are genuine SOURCE CENTRE discrepancies, but may reflect different colony geometries, not necessarily erroneous nest GPS.

V38 original numeric receipt, source hash, 21 exact original names, source-site annual roster and original hard source gate remain **unchanged for reproducibility**. The V38 result is reinterpreted narrowly as **NO INDEPENDENTLY VALIDATED HIGH-PRECISION GPS SOURCE** (not evidence of 14 inaccurate field GPS sites). This repair was made without looking at any original NZ/MAPPPD nesting count effects, choosing different original site IDs, or refitting V36. V39 independently validates four named landmasses, not colony georeference accuracy.
