# V16 original BAS Hart multi-island archive manifest — source-only correction

**Stage 1 independent data-source inventory, 2026-10-26.** Previous V9 incorrectly interpreted only the \`url\` column of the RAMADDA \`output=default.csv\` archive listing. The real original publisher CSV uses \`id\`, \`type=group\`, and \`entry_url\` for nested directories while the direct file \`url\` is only populated for \`type=file\`.

V15 verified the literal eight root entries: seven original locality folders \`Ashen_Hills\`, \`Beach_Point\`, \`Bellingshausen\`, \`Candlemas_Island\`, \`Herd_Point\`, \`Hewison_Point\`, \`Zavodovski\`, plus one root \`SSI_count_results.csv\`. V15 also confirmed the original ZAVO nested \`coordinates\` subfolder contains actual separate \`2020_Macaroni\`, \`2020_Mixed\`, \`2020_Unknown\`, \`2022_Chinstrap\` and outline files. **2022 chinstrap is not a 2020 nest observation.**

## Fix

- Recursively traverse \`type=group\` entries using the exact original \`id\` string from the trusted publisher manifest; convert to canonical official HTTPS entry/show URL; never guess site names or access unrelated archive IDs.
- Preserve parent locality folder, nested path, original publisher row name, original \`id\`, \`type\`, and original file URL, plus source manifest SHA256 receipts. Only \`type=file\` counts as independent file. Files and folder metadata are not counts of biological records.
- Inventory by file type and source island/locality. Source folder label \`Herd_Point\` or \`Hewison_Point\` is a **survey locality**, not necessarily one independent physical island. Later physical island identity must be resolved from original coordinates/geography.
- Expect full 31 original CSV and 127 TIFF according to BAS Hart (2022) published metadata, but **STOP/HOLD** on missing or extra original file count unless original manifests explain the discrepancy. Do not invent file paths to hit the expectation.
- No orthotiff large image downloads. No penguin/animal nest records, no original count rows in this stage.
- Do not merge these south-of-60°S? South Sandwich sites are largely **north of 60°S**; classify them as a distinct sub-Antarctic analogue, not Antarctic Treaty-area independent replication.
- After successful original file inventory, freeze a source-controlled **count_results** file row schema audit, actual original field nest CSV schema, and same-season/2022-imputed status before comparing species/islands or geographical source geometry.

## Scientific scope

This is first-party original data acquisition for independent comparative population/ecological data, **not** a re-analysis of a paper's effect sizes. The original site totals and imputed subcolonies belong to the same Hart 2022 biological survey; a later original BAS Zavodovski 2023 publication (archived PR196) must not be counted as independent replications of the 2020 nest point file if original source observations overlap. Do not use original nesting counts to fit ecological island biogeography without source effort, physical island IDs, land area and habitat availability controls.
