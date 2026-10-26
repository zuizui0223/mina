# V17 BAS Hart original SSI_count_results — multi-island original census source

2026-10-26, follow-up to source-only V16 directory walk. This is an
**independent original 2019–2020 multi-locality UAV biological observation
table**, not a meta-analysis of published effect sizes. The publisher
[Hart et al. 2022 DOI 10.5285/28222725-c53d-40f4-9350-49c368899f0b]
reports original on-image counted nests, model-estimated nests in distorted
imagery, and manual/unknown/mixed-species categories. The producer's reported
published file-count summary (31 CSV, 127 TIFF) differs from the LIVE archive
listing (32 CSV, 132 TIFF). Original file IDs and SHA provenance take
precedence over the summary's outdated counts; this is a source edition
disagreement and must be disclosed.

## Stage: original source entire small summary census table

The sole official publisher root \`SSI_count_results.csv\` is a first-party
survey tally of site categories. Read and SHA the actual publisher original
CSV, bounded at 5 MB. List literal column names, source site names, original
species labels, count/report categories, missingness and original row total.
Do not assume the row labels identify different physical islands. A named
survey locality is not a named island; the physical island graph is an
independent spatial join using original nest coordinates/coastlines.

Count cell classifications must distinguish:
- *observed nest counts*: literal original species and direct UAV annotated nests;
- *estimated nests*: uncountable/distorted-area extrapolation, explicitly
  kept separate;
- unknown/mixed species nests: **never imputed to species**;
- 2022 re-observation of Zavodovski chinstrap: **not** an independent 2020
  contemporaneous species point pattern or breeding-season replicate;
- source blanks, negative markers, commentary and non-numeric cells: do not
  silently convert to zero direct nest counts.

An original species count is a count **within the source observed survey
footprint**. Without site-specific surveyed-area and true negative patches,
species absence at a survey locality cannot be inferred merely from an empty
or unreported count. It is not an island-wide census unless documented.

## Macrobiogeographic design after source structure

Comparative estimand: observed local species assemblage composition and local
nest clustering *conditional on independently surveyed UAV footprint and
physical island identity*, not a rescaling of Hart et al.'s published SSI
island-wide abundance estimate. Preserve every original surveyed locality,
intra-island pseudoreplication and source method.

Propose 2 complementary outcomes only after the original schema is read:
(1) site survey reported direct nest shares (not island population proportions);
(2) coordinate-level species co-occurrence in common survey footprints where
exact CSV nest locations and same-season species IDs are independently
supported. Demand at least 3 true separate islands, multiple direct-count
taxa and same-year coverage, or STOP on transferable macro conclusions.

Original dataset includes locations north of 60°S. Interpret as **South
Sandwich sub-Antarctic archipelago analogue**, not a second Antarctic
continental independent geographical region. This distinction is fixed before
opening count values.

No first-person claim that the original dataset's published assembly is novel;
the new possible contribution is an independently modelled, externally
mapped island-vs-habitat partition given calibrated observation effort.
