# Litchfield historical nest location, vegetation and fur seal confounding: original-source decision

Status 2026-10-29: **important new source audit, not a positive ecological effect**. This memo adds a competitor mechanism to Palmer post-abandonment greening and checks novelty independently of any greenness outcome. Original frozen Paper 1, Paper 2 and JNCC remain untouched.

## First-party 2014 ASPA 113 management plan

Official original PDF: https://www.env.go.jp/nature/nankyoku/kankyohogo/database/jyouyaku/aspa/aspa_pdf_en/113.pdf (ATCM Measure 1, 2014).
- **Map 2, final PDF page** marks the *former Adélie penguin colony* **on the eastern part of Litchfield Island**, sourced from the **1998 USGS orthophoto**. Its legend is a *symbol*, NOT a verified digital colony polygon. It also depicts approximate principal vegetation areas based on the **February 2009 orthophoto**. Do not convert those symbols into an authenticated subcolony or a 30m Landsat mask by eye.
- The 1999 USGS LIT1 survey monument at 64°46′13.97″S / 64°05′38.85″W anchors the historical site map, but is not the colony center. The MAPPPD registration coordinate LITC (-64.7708, -64.0919) is a point coordinate, not a historic nest polygon. The existing 25 QA probes around this registration coordinate have **not** been validated as sampling the former colony. The official east-side colony location makes that mismatch particularly consequential.
- The *same island already had extensive living moss before the Adélie collapse*: large moss carpets were described in 1964 and deep peat banks in 1982. Therefore a positive 2017–2023 vegetation-composite map cannot imply post-2007 primary colonization.
- The management plan documents that fur-seal trampling and nutrient enrichment **damaged or destroyed vegetation on accessible lower slopes by 2001**, and that by 2014 **some previously damaged vegetation appeared to recover alongside a local decline in fur-seal numbers**. Elephant-seal wallows and avian occupancy are additional processes. An increase after the 2007 penguin loss could therefore reflect **seal-pressure release** or climate-driven snow availability; neither could be uniquely ascribed to the penguin event.
- Official 2006 breeding count four pairs; original zeros from 2007 onwards are source-verified separately in the PR. Historical observation dates and spatial colony boundaries are unresolved.

## Original overlapping science (priority novelty audit)

The US Antarctic Program-funded 2021–2024 project **"Common Environmental Drivers Determine the Occupation Chronology of Adélie Penguins and Moss Peatbanks on the Western Antarctic Peninsula"**, led by Cimino, Groff and Johnston, *already explicitly targets* Litchfield's 2007 collapse, moss/peatbanks, microclimate, high-resolution remote sensing and potential guano nutrients:
https://www.usap-dc.org/view/project/p0010354 .
Thus **Litchfield-only penguin–moss associations and guano-source questions are not an untouched research gap**, even if a particular causal test is unpublished. The 2025 Torgersen snow/topography study separately already shows colony-size and aspect/snow-associated extinctions: https://doi.org/10.1007/s10980-025-02088-y .

The 2025 continent-wide 28-moss-species analysis **"Proximity to seabird colonies and water availability shape moss distributions in Antarctica"** already tests distance to bird colonies and thermal/wetness predictors: https://doi.org/10.1002/ecog.08166 ; data https://doi.org/10.5061/dryad.wstqjq2zf . A static moss–seabird-colony correlation is therefore not a new macroecological mechanism.

## Fur seal source: direct Litchfield survey NOT available (2020)

**Source audit (executed; 2026-10-29):** The published Larsen et al. 2025 drone survey (https://pmc.ncbi.nlm.nih.gov/articles/PMC11967255/) explicitly lists **Litchfield Island among locations modeled but NOT surveyed** (the paper's Table 1 list). Humble and Torgersen are in the actual survey system. For Litchfield, Table A4 gives a **2020 modeled estimate 304 fur seals (95% CI 198–468)**, **not observed seal counts or spatial positions**. The same paper quotes a **1994 observed count 874**, but states cross-year comparison assumes interannual stability of seal distribution that its single season cannot verify. Do not subtract 304 from 874 as a measured population change or use 2020 predicted suitability as 2007 observed exposure.

**Source acquisition executed twice from GitHub Actions:** [source audit #40865572551](https://github.com/zuizui0223/mina/actions/runs/40865572551) and [HTTP-diagnostic #40865734013](https://github.com/zuizui0223/mina/actions/runs/40865734013). The original Dryad catalogue identifies three public CSV file ids 3801883, 3801884, 3801885, but all three **file API download URLs gave HTTP 401 (Unauthorized)** and all three ordinary download URLs gave **HTTP 403 (Forbidden)** in that environment. All four offline parser/metadata unit tests passed. The attempted source CSV download failed; **no row-level 2020 seal coordinates have been acquired or joined in mina**. No claim that a public file is permanently inaccessible; this is an observed access block from these runs. Stop repeated attempts to the same endpoints until access state/source route changes. The workflow fails explicitly and preserves source failure receipts, rather than fabricating zeros.

This result **tightens the causal limitation**: the 2020 fur-seal study does not supply Litchfield's true seal occupation or trampling history in 2001–2014. Fur-seal decline remains a first-party historical description, but it is not a quantified independently adjusted exposure during the penguin abandonment. Current existing registered-point NDVI also lacks original colony polygons. These are distinct **failure gates**.

## Existing original seal data candidate (not yet usable in Litchfield event regression)

Larsen et al. 2025, original public Dryad: https://doi.org/10.5061/dryad.qv9s4mwp0 (fur seal coordinate and survey tables, austral January–March 2020, UTM zone 20S; includes all survey rows and DEM/modeled suitability). Associated paper https://doi.org/10.1002/ece3.70833 . Read-only executable API audit: `work/abandonment/audit_furseal_2020_source.py`, CI workflow `climate-penguin-p1-furseal-source.yml`. Source CSV file IDs on original dataset: 3801883, 3801884, 3801885. This is a published **single-year, partially surveyed and partially modeled** spatial data source; Litchfield is in the modeled-only set. It cannot adjust a 2001–2014 abandonment event-study.

## Corrected research decision

1. Litchfield as **positive-source geospatial calibration case only**. Do not treat the previous registered-point NDVI 2007/2008 result (median -0.1437) as a response by *historic nesting ground*.
2. Obtain authentic historic nest polygon/census-code crosswalk first (original 1998 orthophoto / Patterson maps), independent seal and never-penguin plot histories; test local land/snow/NDVI observation support without selecting by effect sign.
3. Main distinctive question must require **multiple independent, spatio-temporal colony transitions** in other islands/regions and test whether historic occupation changes warming-related terrestrial vegetation *after controlling snow, seals and geographic trends*. In a failure of replication/ground truth, state **NOT IDENTIFIED**, keep Antarctic greening and colony decline separate descriptive findings.
4. Under no circumstances claim guano-derived nutrient causation without isotopic or soil source-specific evidence, or a directional migration front without individually calibrated movement data.
