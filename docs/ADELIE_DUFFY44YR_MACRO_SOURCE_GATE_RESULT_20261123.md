# Duffy 1979–2022 × MAPPPD v5 Adélie long-term macroecology: verified source gate (2026-11-23)

**Status: SOURCE GATE COMPLETE / NO PUBLICATION-GRADE POSITIVE POPULATION–POLYNYA INFERENCE.** This independent candidate must not be confused with the frozen 439-season Adélie optical isotope manuscript. No model or existing manuscript was modified.

## Authoritative data, not fabricated trends

- Duffy et al. (2024), PNAS: DOI https://doi.org/10.1073/pnas.2321595121; Figshare original https://doi.org/10.6084/m9.figshare.24768654.v1, CC BY 4.0. Original 1979–2022 coastal-polynya polygons for 30% and 50% SIC definitions, physically 25-km grid. Four published files (source ZIP, results ZIP, Rmd and HTML) have passed original size and MD5 checks in [successful source run](https://github.com/zuizui0223/mina/actions/runs/45095395698).
- Current MAPPPD v5 from https://penguinmap.com/mapppd/DownloadAll, as of 2026-10-21: 5,487 all-species census records across 729 sites, 6 species, 4 count fields/types; original columns and SHA in source artifact. **Do not combine chick, adult and nest counts.**
- Source-only processing uses individual Duffy polygon GIS (not six sector means), geodesically intersected with 100-km buffers around the historic MAPPPD colony coordinates. Only Duffy-classified *coastal* polynyas, June–October. Time series average actually observed days, then weight five months equally. Valid zero remains zero; unobserved days do not become zero.
- Physical source: 14,351 total observed satellite days, of which 6,058 fall June–October, 1979–2022. 50%-SIC threshold archive has 250,176 polygons, 84,028 matching winter/coastal; 30% archive has 112,375 polygons, 24,078 winter/coastal.
- The early record is not uniformly daily: 1979 June–October has 77 observed days, 2022 has 153. This changes time-series comparability and must be included in sensitivity design.

## Adélie long-term candidate census support

- 1979–2022 original positive-nest records: **1,221** at 255 source sites.
- Freeze a descriptive long-series eligibility gate: `nests` count type, ≥6 distinct counted breeding years, ≥20 years between first and last. **40 candidate sites**: Ross Sea sector 88.1 n=26, West Peninsula 48.1 n=13, East Antarctic 58.4.1 n=1.
- Original census records at these sites: **822**; unique site×breeding year after preserving duplicate audit and summarizing duplicated same-year numbers by median **743**. **66** unique site-years had multiple source estimates, of which **17** had >20% max/min count discrepancy (8 sites). **23/40** sites changed documented survey `vantage` type; **61** source rows had published `accuracy >2`. Positive nest counts only are not full site occupancy / all-zero monitoring trajectories; no absent census years have been filled with zeros.
- 40 nominal stations form only **seven** haversine-connected geographic groups under a 100-km adjacency threshold: **three Ross Sea, three Peninsula, one East Antarctic**. 250-km grouping has **five** groups. The 40 names cannot supply 40 independent regional-climate replicates.

## Same-source, unadjusted feasibility screen — not an ecological hypothesis test

All actual original 1979–2022 Duffy daily polygons were processed inside the fixed 100-km radius and June–October season for the 40 candidate sites. The 50% source has some nonzero mapped coastal polynya area during the 44 years at all 40 sites; the 30% product never maps nonzero coastal polynyas at **20/40** sites. For trends estimated only during each site's observed nest census span, Theil–Sen `log1p(local seasonal polynya km²)` slopes equal **0 at 23/40 sites under 50%**, and **0 at 34/40 under 30%**. This is an **identifiability/coarse-resolution issue** with zero-rich 25-km polygons, not a test showing no environment effect.

A preliminary, intentionally unadjusted same-site sign diagnostic of the 50%-source polygon slope versus `log1p(nest count)` slope shows **7 matching, 10 opposing, 23 unclassifiable zero physical slopes**. Nominal site-level Spearman `rho=-0.091925`; the seven geographic blocks' descriptive `rho=-0.074125`. Both are **unadjusted descriptive correlations**; **no valid p-value** or causal effect is claimed. There is no matched local total sea-ice concentration control, and census method variation can bias estimated counts. A population-specific positive coastal-polynya effect is not supported by this screen, but neither can an ecological null be inferred.

Importantly, 30%-classified *coastal polynya* area may exceed 50% *coastal polynya* area for a given site-year, because ocean connectivity and coastal classification can change with the SIC threshold; 166/1760 original matched site-year records exhibit this. It is not necessarily a GIS bug or a paradox in raw open-water area.

## Prior work / novelty boundaries

- Iles et al. (2020), https://doi.org/10.1111/gcb.15085: mean sea-ice concentration explained over 85% of among-site variation in long-term mean Adélie population growth, strongly limiting novelty of geography-only correlations.
- Ainley et al. (2024), https://doi.org/10.1017/S0954102024000051: Cape Royds breeding series 1955–2020 already discusses polynya, wind, icebergs, population changes; Ross Island lag search is a case study, not a brand-new ecological mechanism.
- Landrum et al. (2026), https://doi.org/10.5194/tc-20-1815-2026: Antarctic coastal polynya trend sign/significance can change by SIC threshold, observational product and grid. Source article itself supports robust physical-definition tests.
- Duffy et al. (2024) regional changes should not be taken as observed local 100-km geometry at each colony.

## Outcome and future independent data gate

**NO-GO to interpret present 44-year Duffy×MAPPPD 40-site/7-cluster result as a novel, identified, generalizable coastal-polynya effect on Adélie growth.** A future confirmation would need (i) within-site matched Jun–Oct total SIC, (ii) multiple genuinely independent regions/clusters, (iii) comparable nest survey methods and count accuracy, and (iv) local polynya geometry measured robustly at both 30% and 50% SIC. A higher-resolution post-2003 DEEP-AA 6.25-km dataset can be an *independent follow-on source* but it does not restore the 1979–2002 decades or exactly reproduce Duffy's 25-km product.

## Reproducibility

- Frozen exploratory source contract: `contracts/ADELIE_DUFFY44YR_MACRO_SOURCE_GATE_V1.json`
- Official source acquisition: [Actions #45095395698](https://github.com/zuizui0223/mina/actions/runs/45095395698), retains Duffy original official four files and MAPPPD v5 original CSV.
- Data and local reproducible source-processing scripts: ZIP delivered to user in the linked ChatGPT conversation, basename `adelie_duffy44yr_MAPPPD_v5_macro_source_gate_20261123.zip`; includes original-derived 40×44-year 30/50% site exposure panels, source colony-year deduplication, 7 cluster descriptions, audit JSON and two descriptive figures. The ZIP's author-supplied result cannot be substituted for the original published Duffy polygons and MAPPPD release.
- No new Adélie optical isotope model fit; existing Draft PR #214 and #216 unchanged; no claim of independence from existing published image sources where shared physical data are reused.
