# V9 — East Antarctic empty-habitat source search and island-colonization novelty gate

**2026-10-10.** Research PR193 source validation, no new biological estimate. Frozen Ecology PR189 and authenticated-resight PR142 unmodified.

## We found a different kind of true risk set, but at the WRONG ecological grain

The [Australian Antarctic Data Centre (AADC) coastal ice-free land reference system](https://doi.org/10.26179/53YK-8Z83), Southwell et al. (2021), maps discrete ice-free **islands and coastal rocky outcrops**, between 37°–160°E and covering candidate habitats whether currently used for Adélie breeding or not.

The linked [Southwell et al. (2016/2017) Adélie occupancy source](https://doi.org/10.4225/15/57590498D301C) provides site-by-season literature and field occupancy data, with coverage primarily 1950–2012 in 37°–160°E. The separate [Southwell & Emmerson (2025) eight-species presence/absence source](https://doi.org/10.26179/5n29-r073) contains search events for the Adélie penguin and seven other breeding seabird species, 1910–2020, 30°–150°E, with explicit presence, reported absence, and non-reporting.

**Scale incompatibility is definitive:** Cape Crozier's source nest GPS locations are at approximately 169°E, **outside the published East Antarctic source domain**. Cox's 50 `solo_nests` sources concern individual ~0.75m² nest territories and neighborhood rings a few metres wide, whereas the AADC coastal spatial reference defines entire islands or rocky outcrops. Therefore AADC map sites **CANNOT** be inserted as 'matched unoccupied 3–10m patches' for Cox's nest-scale failed-pioneer H1; nor do East Antarctic site-season occupancy events contain nest-specific egg/crèche outcomes or observed 2021–2022 pioneer identities.

The original [AADC spatial reference metadata and downloads](https://researchdata.edu.au/a-spatial-reference-east-antarctica/699038), [2016 occupancy](https://data.aad.gov.au/metadata/records/AAS_4088_Adelie_Occupancy), and [2025 eight-species source](https://researchdata.edu.au/mapping-knowledge-seabird-east-antarctica/3651223) have well-grounded dataset identifiers.

## Historical novelty vetoes already resolve several apparently promising "discoveries"

1. **Southwell et al. (2017), Ornithology, doi:10.1642/AUK-16-125.1**: Independent concurrent direct records were available for 16 of 19 potential satellite-implied Eastern Antarctic Adélie colonization/extinction events, and **NONE OF THOSE SIXTEEN** was confirmed to have actually occurred. False-negative satellites at small sites, other-species guano, physical features and historical locality mismatches were documented. Thus saying 'remote imagery overestimates colonization and local extinction' as a new mina discovery is untenable. This paper explicitly reported geographic precision/accuracy correction.
2. **Southwell et al. (2025), Diversity and Distributions, doi:10.1111/ddi.70066**: Published **33,297** original search-event records spanning eight Antarctic breeding seabird species: 5,014 direct presences, 11,701 direct absences and 16,582 search events where occupancy was not directly reported. It also already mapped **known / absent / ignorance** classes and differences in ascertainment by field/air effort. For Adélies, it enumerated **248** known presence sites, **1,633** conservative absence sites vs **3,762** optimistic inferred absence sites, with corresponding **36.1%–77.0%** estimated search effort. Therefore a new figure of candidate/occupied sites, simple ascertainment correction or "many empty islands" is not biologically novel.
3. **Fernández-Chacón et al. (2017), Scientific Reports, doi:10.1038/srep42866**: A separate long-lived colonially breeding seabird's 34-year natural-colonization study already addressed information barriers to new colony founding, personal experience and founders' reproductive advantage. Thus "colonization takes longer because prospectors require information" is also prior art.
4. **Boulinier et al. (2008), Royal Society Biology Letters, PMID PMC2610090**: Experimentally altered neighboring breeders' reproductive success in a colonial seabird (black-legged kittiwakes), showing performance-based information affects fidelity and recruitment. A purely correlational failed-successful pioneer site contrast cannot be sold as the first causal test of public information.

The *specific Antarctic micro-patch legacy* hypothesis remains unresolved only because the appropriate three-class, matched, dated patch cohorts (verified failed first attempts / verified success / truly never-used yet feasible) are missing, **not** because no Antarctica-wide habitat list exists.

## What the official raw file access check actually did (GitHub CI #38011136434)

The source-only action `.github/workflows/east-antarctic-unused-sites-source-availability-v1.yml` sent bounded HEAD requests and 32-byte GET signatures (Range-limited to 65,536 bytes requested) only to three exact official AADC download URLs:

- Potential coastal land: `https://data.aad.gov.au/eds/4344/download`
- 2016 direct occupancy: `https://data.aad.gov.au/eds/4345/download`
- 2025 multispecies occupancy: `https://data.aad.gov.au/eds/5959/download`

**All 3** returned 206/206 transport statuses but **HTML source signatures**, not a validated ZIP, CSV, XLSX or biological database. The workflow finished successfully as an honest source-access audit, but its scientific verdict is **HOLD_NO_VERIFIED_TABULAR_ARCHIVE for all three sources**. It read ZERO biological occupancy records, did not recover geographic polygons, and fitted ZERO ecological hypotheses. Never present the published paper's summary counts as original data rows newly measured by mina. This negative source result may reflect frontend routing, server configuration or access mechanism; it is NOT evidence that the data do not exist.

See `contracts/EAST_ANTARCTIC_UNUSED_SITE_SOURCE_NOVELTY_GATE_V1.json` and `scripts/probe_east_antarctic_unused_site_official_sources_v1.py`.

## Decision

**Do not repeat Cox 2021 post-hoc neighbor regressions and do not run a new AADC simple site-presence model.** Neither produces the mechanism the project is looking for. A future genuine mechanistic result would need a distinct independent perturbation in a marked, pre-censused **micro-patch** network or an explicit **island-to-island** founder movement test with independent individual histories plus expected chick output; current source classes do not meet that bar.

The theoretical possibility that a failed pioneer creates a residual attractive physical cue *without its own offspring* must be contrasted not only against successful colonies and good habitat, but against **public-information and pre-existing physical-site effects already proven in prior art**. The new AADC site risk sets cannot identify that novel effect at Cox's island.

**Status: HOLD_PREEXPOSURE_3_CLASS_NEST_PATCHES_AND_ORIGIN; EXTANT_ANTARCTIC_SITE_DATA_EXIST_BUT_WRONG_SCALE/DOMAIN.** Ecology PR189 frozen.
