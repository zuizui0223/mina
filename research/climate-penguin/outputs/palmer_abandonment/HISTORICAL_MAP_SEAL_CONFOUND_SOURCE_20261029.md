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

## New directly usable independent confounder source

Larsen et al. 2025, original public Dryad: https://doi.org/10.5061/dryad.qv9s4mwp0 (fur seal coordinate and survey tables, austral January–March 2020, UTM zone 20S; includes all survey rows and DEM/modeled suitability). Associated paper https://doi.org/10.1002/ece3.70833 . Read-only executable API audit: `work/abandonment/audit_furseal_2020_source.py`, CI workflow `climate-penguin-p1-furseal-source.yml`. Source CSV file IDs on original dataset: 3801883, 3801884, 3801885. This is **one year of seal spatial occupancy**, not a 2001–2014 longitudinal seal-pressure history, and thus **cannot by itself adjust an abandonment event-study**.

## Corrected research decision

1. Litchfield as **positive-source geospatial calibration case only**. Do not treat the previous registered-point NDVI 2007/2008 result (median -0.1437) as a response by *historic nesting ground*.
2. Obtain authentic historic nest polygon/census-code crosswalk first (original 1998 orthophoto / Patterson maps), independent seal and never-penguin plot histories; test local land/snow/NDVI observation support without selecting by effect sign.
3. Main distinctive question must require **multiple independent, spatio-temporal colony transitions** in other islands/regions and test whether historic occupation changes warming-related terrestrial vegetation *after controlling snow, seals and geographic trends*. In a failure of replication/ground truth, state **NOT IDENTIFIED**, keep Antarctic greening and colony decline separate descriptive findings.
4. Under no circumstances claim guano-derived nutrient causation without isotopic or soil source-specific evidence, or a directional migration front without individually calibrated movement data.
