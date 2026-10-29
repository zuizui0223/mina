# Palmer spatial feasibility audit — 2026-10-29

## Verified resources and limits

- Downloaded and visually inspected Cimino et al. (2025) Fig.5 and supplementary Fig.S2, and read the supplementary DOCX. Torgersen historic subcolony perimeters (1998/99), January 14 2020 drone survey, and 2022 GPS perimeters exist in this published analysis. Humble was surveyed January 15 2020. Fig.S2 explicitly compares January 11 2019 satellite imagery with January 2020 drone imagery. Figure labels referring to 2019 can mean the 2019/20 season; do not shift these to calendar January 2019.
- Fig.5 depicts 23 historic Torgersen subcolonies (18 extinct, five active). The downloaded figure does not label polygons with the numeric colony codes in the census. This audit has NOT completed a code-to-polygon crosswalk or georeferenced/digitized these polygons.
- Supplement S2 reports approximately 1.5 cm and 3 cm ground sample distance and survey-grade ground control. These are image sampling resolutions, NOT confirmed positional errors for every derived perimeter.
- Supplement S3 describes a longer census than the frozen local ERDDAP table: extinct subcolonies mainly 1991–2019 and active subcolonies 2020–2022, combining EDI, publications and digitized historical graphs. The cited EDI v8 title says 1991–2021. Treat these as different observation frames pending raw download; do not silently replace the local 1991–2017 series or assume every colony has annual observations through 2022.
- The EDI DOI resolves to knb-lter-pal.87.8. The portal returned a human verification page in this audit; direct metadata access returned HTTP403. Raw extended census not obtained.
- The Duke drone dataset DOI resolves to record/263. HTTP access returned empty202 and the web reader403; the raw georeferenced orthomosaics were not obtained. Public deposit existence is documented, actual reuse not verified here.
- Downloaded and rendered the official ASMA7 Arthur Harbor map dated December 11 2008. It distinguishes penguin-colony symbols from SMALL BOAT LANDING SITE symbols. Boat symbols are not evidence of penguin landings. This overview is not a census-code map.
- Patterson (2001) MSc thesis text and map caption are available through the web reader. Local PDF retrieval failed; Fig.3 was not visually inspected here and is not treated as a completed crosswalk. The thesis is MSc, despite the later supplement citing it as PhD.

## Scope decision

Primary Palmer candidates: Torgersen and Humble, January 2020 imagery. Torgersen adds historic/2022 perimeter comparison; these do NOT constitute annual vegetation maps. Christine and Cormorant remain island-scale census sites, without a verified component boundary match in this audit. Litchfield is useful as a historical abandonment case but disappearance in 2007 precedes the 2017–2023 vegetation composite; vegetation after abandonment cannot explain preceding extinction without reverse-causation bias.

The local frozen census has 1991–2017 coverage, so its only nominal overlap with the vegetation composite is 2017, not a matched annual image comparison. A 2020 census-plus-imagery comparison is a stronger candidate, conditional on acquiring and checking the cited extended census and original imagery.

## Hypothesis test ceiling

A map of shore accessibility is not a map of actual penguin landings. Do not use shortest distance to any shoreline or human boat landings as the measured route. This audit verified no dated, independently identified penguin landing point or complete used route on either Palmer island. Fig.S2 shows snow, coast and nesting stains, but publication resolution cannot validate a narrow route or vegetation composition.

The observed snow/topography explanation is already tested by Cimino et al.2025. To add a distinct access hypothesis, one needs independently identified landing/route geometry, matched available nesting terrain and snow/elevation controls, and a temporal outcome independent of mapping. No causal effect of mammalian-predator absence is estimable within a sample where all sites share that absence. No flight ability effect is identifiable from Adelie-only Palmer comparisons. Avian predators and fur seals remain relevant.

## Primary sources

- https://doi.org/10.1007/s10980-025-02088-y (article, Fig.5 and supplemental S2/S3)
- https://media.springernature.com/original/springer-static/esm/art%3A10.1007%2Fs10980-025-02088-y/MediaObjects/10980_2025_2088_MOESM1_ESM.docx
- https://doi.org/10.7924/r4sf2xs2w (drone deposit; raw download not achieved)
- https://doi.org/10.6073/pasta/805f6b97593c60cfdfd02266db9ab4b6 (EDI v8; raw download not achieved)
- https://documents.ats.aq/ATCM32/att/Atcm32_att021_e.pdf (official boat access/colony overview)
- https://scholarworks.montana.edu/bitstreams/a124761d-6f6e-409a-a7b7-7c60d34b7543/download (Patterson2001 thesis)
- https://www.usap-dc.org/view/project/p0010354 (existing penguin–moss shared environmental driver project; related research already underway)
- https://doi.org/10.5061/dryad.qv9s4mwp0 (fur-seal distribution resource; potential covariate, not measured here)

Downloaded third-party figures are retained as research scratch, not republished as new deliverables. This is a feasibility audit, not a fitted hypothesis test.
