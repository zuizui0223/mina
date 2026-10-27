# Paper 2 V47 — Falklands within-archipelago flightless vs flying sea-breeder source sample VERIFIED

**2026-10-27. First-party Falkland Islands Government original dataset, not a new causal ecological result. Original source evidence is published in results/PAPER2_FALKLAND_FIBD_V47_PENGUIN_FLYING_MAMMAL_SOURCE_RESULT.json and authenticated by a successful GitHub Actions run.**

## The comparison finally exists

The original FIBDv8 20140601 publicly published CC-BY-SA 4.0 workbooks from the Falkland Islands Government — location 534 named places, original bird table 4,958 data rows, invasive entries 1,212 original headerless rows, visits 4,964 rows — were verified against their individual first-party SHA256. Original island names are joined conservatively with Unicode normalization, casefold and whitespace only. No fuzzy aliases, nearest source map points, or inferred biological absence.

With the independently preselected taxonomic group definitions, the bird source includes **249 penguin records (5 literal species labels)** and **1,104 flying seabird records (19 literal species labels)**. Of these, **69 island×calendar-year** comparisons across **66 uniquely named island candidates** and **23 publisher wider-area geographic groups** have **definite breeding evidence for BOTH penguins and volant seabirds** together with at least one same-island-year source visit; **63 island×date** opportunities also contain both guilds with the same-date source visit. Within those 69 island-year comparisons, definite source guild diversity spans **five literal penguin species and 14 flying species**.

This passes the original source-only G1 sample gate (>=20 island-year records, >=10 separate islands, >=2 publisher areas, >=2 guild species). These are NOT island-level observed biological true absences or outcomes of predator pressure. The observation design and field method may differ even if two source bird records have the same date. Observations require external temporal and survey effort controls before population inference.

Original bird-native 'confirmed breeding' evidence was counted only using a frozen literal definite-status whitelist; 'probable breeding', 'possible breeding', non-breeding and unknown records were not counted as confirmed, and other unrecognized source codes were not recoded after results were seen. The dataset records bird 'Presence', 'Breeding status', 'Count' and 'Time surveying' independently; these are not synonymous, nor does missing source record = non-detection.

## What is still wrong with simply fitting the model?

- The same source invasives table includes **78 original Norway rat taxon rows (60 uniquely named islands)** and similarly 34 house-mouse rows and 25 cat rows, but these are **not 78 verified rat present islands**. Only **7 of the 66 originally co-breeding island candidates** have any native Norway-rat TAXON RECORD. The invader status rows have some encoded date/status cells and other source text; one recorded rat species name alone cannot distinguish present, suspected or absent.
- The Falkland Islands Government metadata explicitly says Norway rat "present/absent" source statuses were assigned for surveyed and **unsurveyed** islands, and the unvisited ones were desktop inferred. Therefore FIBD code 0, source row missingness and assumed absence are unfit as monitored negatives. Government original field-visit worksheet is not a repeated mammal-targeted non-detection matrix.
- G2 verified field survey presence/negative mammal contrast **FAILS/NOT IDENTIFIED**. G3 same-day bird monitoring under independently equal detection effort and verified available nesting/habitat cells **FAILS/NOT IDENTIFIED**. **Do not fit** predator×penguin flightlessness interactions with these data as if treatment-control natural experiment.
- V47 bird status counts are sampled from 1997–2013 source original records (even if data registry updated in 2026), which is not the same observational epoch as recent Antarctic original nest GIS 2019–2020 or UK JNCC 2015–2021. Simple between-dataset pooled regression would confound ecology with survey period and geography.
- A physical island boundary/cross-island water-gap is not automatically known from an FIBD 'Location Name' or WGS84 centroid; potential suitable terrestrial nesting habitat and verified shore-to-nest trails are not mapped.

## A precise further independent source rather than reopening negative JNCC analysis

Tabak et al., J Anim Ecol, 2015, DOI 10.1111/1365-2656.12312, monitored passerines on 230 Falkland Islands with published rat states: **85 rat-present, 108 historically free, 37 post-eradication**. Its independently published Dryad doi:10.5061/dryad.dj524 may provide original island identities, field visit years/effort, mammal state evidence. Prior passerine biological effects are **PRIOR ART** and will NOT be analysed as new bird responses. New original data would serve only to validate G2 matching on the already confirmed V47 66 island candidate cohort. Exact public Dryad DOI source metadata audit is separately frozen in contracts/PAPER2_FALKLAND_DRYAD_RAT_FIELD_SOURCE_V48.md and code/scripts/audit_paper2_dryad_rat_original_metadata_v48.py.

**Current ecological conclusion:** The original within-Falklands co-breeding comparison opportunity is real and qualitatively broad (66 islands/23 source areas), but mammal-conditioned refuge and flightlessness interaction are hypotheses, not supported effects. Antarctica remains a mammal-free NATURAL REFERENCE for one threat class, not a predator-free randomized control, and 122,139 BAS nest coordinates are penguin-only samples. The question remains: when is an island physically less reachable by predators but more reachable by flightless ocean-foragers?

## Reproduction
- Frozen source-first V47 methods: contracts/PAPER2_FALKLAND_FIBD_GUILD_BREEDING_SOURCE_V47_FROZEN.md
- Numeric original-data receipt: results/PAPER2_FALKLAND_FIBD_V47_PENGUIN_FLYING_MAMMAL_SOURCE_RESULT.json
- Scripts and synthetic status checks: scripts/audit_paper2_falkland_guild_breeding_source_v47.py and tests/test_paper2_falkland_guild_breeding_source_v47.py
- [Successful 4-source FIG native XLS and index/temporal join run](https://github.com/zuizui0223/mina/actions/runs/40501816259).
