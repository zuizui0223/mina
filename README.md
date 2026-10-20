# mina

Research program for **penguin breeding-island ecology**, linking a local
long-term discovery system at Palmer Station to Antarctic-wide comparative
macroecology.

## Research program

### Paper 1 — replicated breeding-space contraction

The current submission line is an **Ecology Report**:

**Breeding-space contraction recurs across declining Adélie and chinstrap penguins**

The paper asks whether declining colonial populations merely thin in fixed
proportion across monitored breeding components, or whether relative breeding
composition changes beyond the finite-count and observation-error consequences
of lower abundance.

Evidence is ordered as:

1. **Palmer Adélie discovery:** three stable-roster island populations;
2. **Signy Adélie prospective geographic replication:** frozen before the
   concentration effect was computed;
3. **Signy chinstrap prospective cross-species replication:** separately frozen
   before effect computation.

Across the five population units, effective monitored breeding-component number
declines by **19–83%**. The two prospectively frozen Signy tests remain extreme
under the most severe prespecified 20% multiplicative-CV sensitivity
(Adélie **p = 0.000010**; chinstrap **p = 0.000020**).

The broad abundance–space principle is not claimed as new. The paper's novelty
is the **within-colony fixed-composition count-error test of excess breeding-
component concentration**, followed by prospective geographic and cross-species
replication.

Canonical submission manifest:
`submission/ECOLOGY_REPORT_SUBMISSION_MANIFEST_V1.md`.

### Paper 2 lane — Antarctic-wide breeding-island macroecology

**V16 new, source-authenticated ASI cross-guild panel:** The distinct 2013
Antarctic Site Inventory Ecological Archives original CSV has 1,124 census
rows. A strictly same-site/date, ASI-source, nest-only and accuracy-filtered
join yields **99 penguin × flying-seabird same-day census events across
37 source site IDs and three regions**. Source Region collisions (two
original Site_ID labels, 12 rows) were conservatively dropped. Two-penguin
same-day comparisons have 53 events across three regions and FAIL their
prospectively frozen gate. This is source feasibility, **not** a fitted
cross-guild ecological mechanism or independently surveyed physical islands.
- [V16 original source result and decision](docs/ASI_ORIGINAL_COSURVEY_V16_RESULT_AND_DECISION.md)
- [V16 machine-readable source support](results/ASI_ORIGINAL_SAME_DAY_NEST_COSURVEY_V16.json)

**2026-10-20 V15 biotic-interaction feasibility is also CLOSED.** Original AADC
Adélie×south-polar-skua co-searches gave **1,061 same-site/season pairs
across 96 island geographic sites**, but only **8 pairs / 8 sites in one
region** had matching exact reported survey date; the fixed comparator
Adélie×snow-petrel had **701 pairs across 89 sites**, but one co-dated pair.
Matching source obs_number fields are not a validated shared visit/observer
identifier across independently compiled source books. Thus this is
**a sample-support STOP, not a fitted species-interaction effect**. The prior
Southwell paper created multiple species×sites×season records from heterogeneous
source references. No new Antarctic predator-resource mechanism follows.

- [V15 original co-survey support and decision](docs/AADC_PENGUIN_SKUA_COSEARCH_V15_RESULT_AND_DECISION.md)
- [V15 source-only numerical receipt](results/AADC_PENGUIN_SKUA_COSEARCH_SUPPORT_V15.json)

**Current result, 2026-10-20: the original-data V14 macroanalysis is complete
and reproduced, with no supported guild × island-area result.** Source access
is resolved. The previous statement that demographic outcomes were still
unopened is superseded by the executed V6, V8 and V14 analyses.

The new AADC source join contains **7,785 geographic sites and 33,107 original
eight-species search records**. V14 compares the seven flying seabird species:
**6,956 direct P/A records, 368 sites (295 islands + 73 continental outcrops),
1,581 site/species histories, and 8 held-out 250 km blocks**. Nonreporting is
never coded as absence; repeat seasons do not count as additional islands.

Primary equal-region Brier scores (lower is better) are **0.310378** for the
survey/species/geography baseline, **0.356245** with area and land class,
and **0.359034** with nesting-guild interactions. Only **3/8** regions improve
with guild terms, below the frozen **6/8** requirement. CREVICE island and
continental area IQRs do not overlap. Thus predictive support failed and the
island-specific three-way interpretation fails the frozen overlap rule;
this is not a demonstrated zero ecological effect.

All five original workbooks were retrieved and verified again; V13 input CSVs,
included rows and all **115** original numerical result fields reproduce
exactly. Reporting now distinguishes ordinary-row, history-weighted and
equal-region scores. **27 focused V11–V14 tests pass.**

The broader programme still asks how marine resources and terrestrial or
sea-ice breeding substrate jointly structure Antarctic breeding populations.
The first V6 land/sea model and V8 habitat-mosaic test also failed their
frozen support criteria. V14 is closed without changing guilds, weights or
spatial thresholds to seek a positive result. The frozen Ecology manuscript
is separate; no positive Antarctic-wide mechanism is claimed.

Canonical current state and full numerical evidence:
- [V14 result, interpretation and next state](docs/AADC_GUILD_ISLAND_AREA_V14_RESULT_AND_DECISION.md)
- [V14 numerical result](results/AADC_GUILD_ISLAND_AREA_SPATIAL_CV_V14.json)
- [Exact source/model reproduction](results/AADC_V14_REPRODUCTION_20261020.json)

Earlier programme design and atlas provenance:
- `contracts/MINA_RESEARCH_PROGRAM_V1.json`
- `docs/ANTARCTIC_BREEDING_ISLAND_MACROECOLOGY_V1.md`

---

## Independent Palmer phenotype reassembly lane

A separate short-paper lane now asks where the conspicuous Palmer
breeding-site phenotype comes from.

The frozen ecological result is hierarchical:

- across the full assemblage, morphology-to-site predictability is dominated by
  species identity;
- within Adélie penguins, fixed island morphology effects are small;
- structural island contrasts repeatedly reverse among years;
- same-year island classification is modestly above chance
  (**balanced accuracy 0.448**), while leave-one-year-out transfer falls almost
  to the three-island chance reference (**0.342** vs **0.333**).

The biological interpretation is therefore **species sorting plus temporal
reassembly**, not a persistent within-species island ecotype.

This lane is independent of frozen Paper 1 and the Antarctic-wide Paper 2
programme. It does not reopen either paper and does not make an ODSP methods
claim.

Canonical files:

- `contracts/PALMER_PHENOTYPE_REASSEMBLY_PAPER_V1.json`
- `results/PALMER_PHENOTYPE_REASSEMBLY_RESULT_V1.json`
- `docs/PALMER_PHENOTYPE_REASSEMBLY_MANUSCRIPT_SPINE_V1.md`

---

## Current ecological claim

For a spatially structured breeding population, total abundance and relative
spatial composition are distinct state descriptions.

The null model uses each observed annual population total as the **latent
expected annual total**, fixes one time-invariant vector of breeding-component
shares, and then simulates counts under the frozen Poisson / Gamma–Poisson
observation-error family. It therefore includes both the finite-count tendency
for small components to disappear as abundance declines and independent count
noise.

The observed decline in effective breeding-component number is more negative
than that null in all five studied population units:

- Palmer Cormorant Adélie: **3.54 → 2.86** (**−19%**), CV20 p = **0.038**;
- Palmer Humble Adélie: **4.62 → 2.28** (**−51%**), CV20 p = **0.000010**;
- Palmer Litchfield Adélie: **5.78 → 1.00** (**−83%**), CV20 p = **0.000010**;
- Signy Adélie: **3.08 → 1.94** (**−37%**), CV20 p = **0.000010**;
- Signy chinstrap: **4.44 → 2.19** (**−51%**), CV20 p = **0.000020**.

Palmer is explicitly the **discovery system**. Its public colony codes are
treated as monitored census components, not verified fixed GIS polygons. The
confirmatory weight rests on the two prospectively frozen Signy tests.

The endpoint is inverse-Simpson effective component number, a Hill-number
measure of relative concentration. It can fall while every monitored component
remains occupied. It is therefore **not** occupied-site richness, physical
breeding area, genetic effective population size (Ne), or genetic effective
number of breeders (Nb).

The closest general literature includes positive abundance–occupancy
relationships, geographic range contraction, and marine-fish
proportional-density versus basin models. Accordingly, mina does **not** claim
that abundance and spatial extent are newly separable. The transferable result
is narrower: a discrete breeding-component composition can depart systematically
from proportional thinning, and that departure can be tested conditional on
the observed abundance trajectory.

## Ecological framing

mina treats penguin breeding islands as **externally subsidized breeding
patches**. Food resources are primarily marine; breeding surfaces are discrete
and terrestrial. Regional marine processes can therefore impose a shared
demographic direction while local snow, geomorphology, colony history and
remaining nest-space organization shape vulnerability.

Direct biotic interactions are not assumed absent. They are treated as
localized and testable rather than as the default explanation for whole-island
trajectories.

## Submission status

The canonical submission is **Ecology Report v0.5**.

Current package:

- manuscript: `submission/MANUSCRIPT_ECOLOGY_REPORT_V0_5.md`
- cover letter: `submission/COVER_LETTER_ECOLOGY_REPORT_V3.md`
- main captions: `submission/FIGURE_CAPTIONS_ECOLOGY_REPORT_V0_4.md`
- supplementary caption: `submission/SUPPLEMENT_ECOLOGY_REPORT_V0_4.md`
- copy fields: `submission/ECOLOGY_SUBMISSION_COPY_FIELDS_V2.md`
- readiness audit: `submission/SUBMISSION_READINESS_ECOLOGY_REPORT_V3.md`
- reviewer stress test:
  `submission/PRE_SUBMISSION_REVIEWER_STRESS_TEST_ECOLOGY_V1.md`
- scientific freeze: `contracts/ECOLOGY_REPORT_SUBMISSION_V3.json`

The old Ecosphere, JBI and integrated manuscripts are **provenance only** and
must not be treated as parallel submissions. The integrated JBI line is formally
superseded.

## Development state

The Ecology Report scientific content is **frozen**. Before initial submission,
do not add:

- new ecological endpoints;
- alternative concentration metrics;
- tuned thresholds or time windows;
- additional error models selected after outcome inspection;
- extra species as post-result rescue analyses;
- new mechanism claims.

Allowed work is limited to reference completion, copyediting, journal
formatting, author metadata, archival metadata, figure QA, and clarification
from the Palmer data providers about colony-code continuity.

The remaining submission blockers are author-controlled metadata: author order,
affiliations, corresponding author, funding/acknowledgments, CRediT roles,
conflict-of-interest statement, complete AI-tool inventory, overlap statement,
and ORCIDs if requested.

## Reproduce

Install:

```bash
python -m pip install -e ".[dev,figures]"
```

Fetch the frozen census:

```bash
python scripts/fetch_lter_census.py build/adelie_census.csv
```

Primary analyses:

```bash
mina-lter --census build/adelie_census.csv --out build/lter.json
mina-colony-network --census build/adelie_census.csv --out build/colony.json
mina-hierarchical-variability --census build/adelie_census.csv --out build/hierarchy.json
mina-neff-momentum --census build/adelie_census.csv --out build/neff_momentum.json
```

The manuscript figure workflow additionally exports pinned APBP/MAPPPD site
metadata and regenerates Figure 1–5 data before rendering PNG and PDF outputs.

## Provenance

The project began as a biological follow-up to the frozen ODSP Palmer Penguins
audit. ODSP remains the methodological provenance source; all current biological
development and manuscript work belongs in `mina`.
