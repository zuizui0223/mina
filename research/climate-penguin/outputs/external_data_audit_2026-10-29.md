# Public island-comparison datasets: verified audit, 2026-10-29

This is an access/schema audit, not an ecological reanalysis. Downloaded scratch files are in work/external-audit/. No repository code or frozen mina analyses changed.

## 1. Wright et al. 2016: most direct predator–morphology benchmark

- Primary article: https://pmc.ncbi.nlm.nih.gov/articles/PMC4855539/
- Frozen archive: https://doi.org/10.6084/m9.figshare.3123148.v1 ; Figshare API confirms CC BY 4.0, species_averages_flight_muscles.xlsx and skeletal_data.xlsx.
- Author repository: https://github.com/coereba/islands ; actual skeletal CSV: https://raw.githubusercontent.com/coereba/islands/master/skeletal_data.csv
- Downloaded and parsed raw CSV: 2,238 specimens, 109 island labels, 216 species labels BEFORE analysis eligibility. Published comparison uses 366 island population units. Do not substitute raw file counts for the analysis cohort.
- Verified columns include cranium.length, rostrum.length/width/depth, coracoid, sternum.length, keel.length/depth, humerus, ulna, carpometacarpus, femur, tibiotarsus, tarsometatarsus, island, landbird.spp.richness, island.area, elevation, nearest.continent, isolation, ecosystem.richness, raptor.spp, mammal.predators, location fields, age, mass, wing.ch., tail, subspecies, sex. mammal.predators is yes/no.
- The article defines the mammal flag as NATIVE mammals that might predate birds. It is not contemporary invasive-mammal status, and it is not a time-resolved capture-year field. Its population-level comparison uses museum specimens of island landbirds; it does not provide a penguin flightlessness replicate.
- Important correction: mammal.predators is in skeletal_data.csv, not ecological.variables.csv.
- Use: external benchmark of predator–skeletal shape/island-area associations. Palmer's bill depth/length, flipper, body mass cannot be silently pooled with skeletal keel/leg measurements. Even rostrum (bone) versus external bill measurement needs a protocol mapping. No keel/tarsus in standard Palmer dataset means the central flight-apparatus hypothesis cannot be tested in mina without new matching morphology.

## 2. AVONET: useful trait bridge, not island population data

- Archive verified: https://doi.org/10.6084/m9.figshare.16586228.v7 ; CC BY 4.0.
- Actual downloaded file: https://ndownloader.figshare.com/files/34480856 (AVONET Supplementary dataset 1.xlsx).
- Archive describes 90,020 measured individuals from 11,009 species. Workbook has taxonomy-specific species means (BirdLife, eBird, BirdTree), raw specimens, protocol metadata, source sheets and taxonomy crosswalks.
- Verified species columns: Beak.Length_Culmen, Beak.Length_Nares, Beak.Width, Beak.Depth, Tarsus.Length, Wing.Length, Kipps.Distance, Secondary1, Hand-Wing.Index, Tail.Length, Mass, Inference, Traits.inferred, Reference.species, Habitat, Habitat.Density, Migration, Trophic.Level, Trophic.Niche, Primary.Lifestyle, geographic range fields.
- Raw data include specimen/source, sex, age, Locality, Country, measurer and Protocol; not a clean island×year panel. Raw sheet max_row includes non-data/formatting rows and should not be used as individual sample count.
- Use: taxonomy harmonization, species covariates, broad ecological comparisons. Do not treat a species mean repeated across islands as independent within-species morphology. Do not map penguin flipper length onto flighted-bird wing chord or interpret hand-wing index identically across these locomotor systems. Exclude/flag inferred trait values for primary tests.

## 3. Hakai 100 Islands / Obrist 2020: strongest immediately accessible island environment–abundance reference

- Primary paper: https://pmc.ncbi.nlm.nih.gov/articles/PMC7126081/
- Actual data DOI: https://doi.org/10.21966/10tk-4956
- Live catalogue: https://catalogue.hakai.org/dataset/ca-cioos_12f951d4-4155-4c05-969d-a7158412f579
- DataCite and CKAN metadata verified: CC BY 4.0; raw 10-minute point counts on 99 islands in 2015–2017, paired vegetation, cleaned 2020 dataset, HMSC matrices/environment/traits for later community analysis.
- CKAN resolves public data package: https://drive.google.com/drive/folders/1cHxDcrHyzEXvG0YE53qr2vv8XcRJeskL
- Actual cleaned CSV downloaded: https://drive.google.com/uc?export=download&id=1O-ZyylIH_lsWP1AFnHBydREfhjBhc5A1
- 91 rows verified. Columns: year, year.std, island, node, S.chao1, l.S.chao1, n.birds.50, buf50_area, l.area.std, l.isolation.90.std, hab.het.std, rocky.prop.std, sqrt.wrack.std, soild15N, soild15N.std.
- Raw point-count CSV and metadata are visibly available in same folder; cleaned data alone omit species identity. Habitat heterogeneity and area are already standardized in cleaned file, so full raw physical units require metadata/source reconstruction.
- Author code: https://github.com/debobrist/avian-sib (also HakaiInstitute mirror). Figshare 10.6084/m9.figshare.11907969.v1 is only supplementary PDF; it must NOT be cited as the raw dataset.
- Use: compare environmental associations of bird abundance/density and area/habitat structure, with survey effort (buf50_area), year and island cluster (node). Their birds are terrestrial breeders with marine nutrient subsidy, not penguins foraging directly at sea. No mammal presence variable in cleaned table. Paper reports river-otter signs on >90% of surveyed islands, so it is not a balanced mammal-free/present experiment.
- Comparability: point-count birds per surveyed area vs penguin nests per breeding-site buffer are different observation processes and denominators. Analyze each system separately with matched ecological estimands, then compare coefficients cautiously; do not pool raw counts or claim any difference identifies flightlessness. Survey years span 2015–2017, but each island is not a 3-year longitudinal series.

## 4. DIISE / Spatz 2022: intervention chronology layer, not a control-island census

- Article: https://www.nature.com/articles/s41598-022-14982-5
- Frozen data+code: https://doi.org/10.5281/zenodo.6663551 ; Zenodo metadata verifies CC BY 4.0.
- Downloaded zip: https://zenodo.org/api/records/6663551/files/code-repository-SREP-2022-14982.zip/content
- Actual CSV inside zip: Spatz-et-al-2022/data/dataset-spatz-et-al-scirep-2022.csv. 2,166 raw event rows verified; publication filters to 1,550 attempts on 998 islands. Do not treat 2,166 as independent islands.
- Columns: Country, CountryTerritory, Island_GID_Code, Long_GID2, Area_GID2, Area_GID2_ha, Human_Habitation, Data_Quality, Invasive_Type_DIISE2, Scientific_Name, Island_Eradication_Type, Eradication_End_Date, Eradication_Status, Eradication_Status_Reinvaded, Invasive_Species_Type, Primary_Eradication_Method.
- This frozen CSV has GID and longitude but no island name/latitude; requires a GID crosswalk or independently verified spatial link. Species removal events must be grouped within island and aligned with bird observation years. Removing rats does not establish absence of cats or all other mammalian predators. Check reinvasion, restricted-range versus whole-island events, and quality.
- Use: find candidate within-island before/after removal studies, subsequently link to independent bird count series and comparable untreated controls. No record in DIISE means unknown, not mammal-free. DIISE alone has no bird abundance response and no full inventory of uninvaded islands.
- TIB is also not an unbiased comparison frame: prioritizes highly threatened island vertebrates; using threatened-only occurrences as all birds induces selection bias. Unconfirmed current bulk access should not be represented as downloaded.

## 5. SMP: biologically valuable but still a request-dependent lane

- Official portal: https://app.bto.org/seabirds/public/data.jsp ; allows viewing and email-request downloads; explicitly requests a Data Request form for large volumes.
- Terms: https://www.bto.org/sites/default/files/smp_data_request_guide_aug22.pdf ; attribution, restricted records, and no wholesale republication without permission. Not CC0/CC-BY unrestricted bulk data.
- Monitoring series begin 1986; species and units vary, so nest/pair/individual/apparently occupied site units and site hierarchy need auditing before matching mina. No email or form submitted in this work.

## Recommended design implication

The direct user question has three axes: predator regime, locomotion, and island setting. Current public sources do not create a balanced 2×2 experiment. A penguin-only vs terrestrial-bird contrast fully aliases clade, locomotion, trophic dependence and climate. Separate evidence lanes are more defensible:
1. mina + non-Antarctic penguins: shared locomotion; compare demography–breeding-environment correlations after independent predator-history coding. This controls flight state but cannot estimate its effect.
2. Wright morphology: estimate native predator/island associations in landbirds as a separate external benchmark, not a pooled Palmer morphology test.
3. Hakai island environment–abundance: accessible comparative benchmark for area/habitat/subsidy correlations, but different count process and trophic linkage.
4. A removal chronology + matched bird panel is the strongest natural/quasi-experimental design if adequate pre/post and controls exist; feasibility depends on actual geographic/time overlap, not database size.

Primary controls: same species where possible, multiple independent archipelagos/clades, year matching, real absence evidence, native versus introduced predator definitions, avian predators, observation effort, geography/climate, and shared physical denominators. Report associations; causal effect claims require a suitable design beyond simple cross-system differences.
