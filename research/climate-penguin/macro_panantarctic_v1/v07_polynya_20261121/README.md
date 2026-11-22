# Polynya manuscript v0.7.5 — current author-review candidate

This is the single current manuscript candidate in Draft PR #214 of `zuizui0223/mina`. It supersedes the nest-exposure-centred v0.6 presentation; earlier manuscripts and frozen analyses remain historical records. Original source analyses are pinned to `a1cf988df3501794e9add243a8c2be8ecbb7b43a`.

## Read the manuscript

1. [Main manuscript and 222-word abstract](MANUSCRIPT_POLYNYA_FOODWEB_WORKING.md)
2. [Supplementary methods and results](SUPPLEMENT_POLYNYA_FOODWEB.md)
3. [Figure sources and output](figures/), [alt text](figure_alt_text.json)
4. [Independent numerical reproduction](reproduction_receipt.json), [figure verification](figures/polynya_figure_verification_receipt.json)
5. [Publication-status notes](REVIEW_NOTES_JA.md), [MEPS preparation](submission_preparation/MEPS_REQUIREMENTS.md), [author input](submission_preparation/AUTHOR_INFORMATION.md)

The question is whether June–October coastal-polynya area fraction within 100 km is associated with the subsequent November–February optical Adélie δ¹⁵N signal, after measured summer conditions and fixed effects. This is a retrospective exploratory reanalysis of released source pixels, not direct dietary measurement or a new independent ecological sample.

## What changed in this revision

**Version 0.7.5 investigated the externally timed 2010 Mertz Glacier Tongue/B-09B iceberg event and failed a pre-outcome fixed biological sign test.** On the complete five-year 28-colony source panel, the 10 affected colonies had a winter coastal polynya contraction of **−5.551 percentage points relative to 18 distant controls**, while the original optical δ¹⁵N changed **−0.555‰**, versus a positive sign that would have been concordant with a naïve transfer of the known overall negative slope. The same-source author R1,000 optical version was −0.545‰; the 2010 optical shift was weaker than several pre-event placebo shifts, and source-region comparisons had opposing signs. Summer sea-ice concentration, temperature and source image support changed simultaneously. This is **NO_GO_EVENT_BIOLOGICAL_RESPONSE and NO_GO_CAUSAL_MEDIATION**. The test is still the same selected 439 optical data, not an independent dietary field study. [Event-date and source-ID freeze](FROZEN_MERTZ_2010_ICEBERG_EVENT_BIOLOGICAL_GATE_20261122_JA.md), [source script](test_mertz_iceberg_event_source439_20261122.py), [negative result](RESULT_MERTZ_2010_ICEBERG_EVENT_NOGO_20261122_JA.md), and [CI pass](https://github.com/zuizui0223/mina/actions/runs/45012884027) retain all 140 original event-site years and pre-period diagnostics. Manuscript §3.6 and Supplement S4 contain the negative result. All five original figures, the baseline 439 main slope and its CV3 interval remain unchanged.

**Current review deliverables:** combined manuscript **25 pages, 1,721,292 bytes, 5,535 visible body-paragraph words** (222-word abstract), Supplement **11 pages, 52,876 bytes**; the other four review Word documents have unchanged content, bringing six Word deliverables to **46 pages**. Main+supplement were freshly rendered (all 36 pages checked in contact sheets, changed pages reviewed at 100%); [QA scope](document_visual_qa_v075.json) and [exact Word hashes](document_build_receipt.json) record this. The v0.7.4 page counts below are historical.

Version 0.7.2 completed source/citation/figure accessibility edits. **Version 0.7.3 adds one post-result descriptive source-locked scale audit:** the original reported −1.003‰/10pp slope is also given as −0.161‰ per one standard deviation of the fully residualized polynya covariate (1.601pp across 439 original records); the salinity-adjusted slope corresponds to −0.146‰ per a 1.588pp residual SD. No response, coefficient, uncertainty interval, spatial radius, temporal window or figure changed. This is a rescaling of an exploratory association, not new ecological validation. [Scientific reviewer note](SCIENTIFIC_REVIEW_ESTIMAND_SCALE_V073_JA.md), [source-locked code](audit_polynya_estimand_scale_20261122.py), [fixed result](source_inputs/polynya_estimand_scale_audit_20261122.json) and [passing CI](https://github.com/zuizui0223/mina/actions/runs/45009422843) record the checks.

The version 0.7.2 [editorial verification](editorial_verification_20261122.json) remains a dated record. For v0.7.4, the combined Word has 23 pages/1,720,183 bytes and the supplementary document ten pages/50,651 bytes; both were freshly rendered. All 33 pages were surveyed in contact sheets, with the new main Results and new Supplement S4 table inspected at full size. The [current visual review](document_visual_qa_v074.json) states the scope explicitly; six author-review Word files total 43 pages. Original v0.7.3 [visual review](document_visual_qa_v073.json) remains as a dated record. The original 58-check numerical and 34-check regional CV3 receipts are retained unchanged, while the new descriptive-scale source calculation was separately rerun and checked. Nothing here claims a new ecological model or independent biological confirmation.

**Version 0.7.4 tested the pre-frozen ecological scale-inversion hypothesis and did not support it.** Collapsing the same 439 observed colony-seasons to 85 equal-weight colony means produced a raw between-colony estimate of −0.319‰/10pp and a region+summer+latitude+calendar-adjusted estimate of −1.295‰/10pp (eight-informative-region CV3 95% interval [−4.965,+2.376]). With the original R1,000 calibration, restriction to 82 colonies observed at least three times, and region×season standardization, the point estimates were also negative; the fully adjusted estimate changed sign when Wilkes Land was excluded. The positive spatial counterpart to the historical negative annual slope was therefore **not** found. The frozen [test design](FROZEN_SCALE_BETWEEN_WITHIN_COLONY_TEST_20261122_JA.md), [NO-GO verdict](RESULT_BETWEEN_WITHIN_POLYNYA_NO_GO_20261122_JA.md), [source-verified code](test_between_within_source439_20261122.py) and [passing CI](https://github.com/zuizui0223/mina/actions/runs/45011139260) make the unsuccessful test inspectable. Reaves et al. (2025) chick-bone comparisons cannot be treated as equivalent measures.

The main narrative now follows winter polynya association, temporal comparison, salinity distinction, measurement sensitivity and unresolved biological interpretation. Nest-weighted climate exposure is supplementary context. The negative direction contradicts the original positive hypothesis and is disclosed in the abstract. Failed forward prediction, weaker later-period point estimates, selective chlorophyll support, inconclusive Signy stomach-content evidence and the unsuccessful later-period guano-recovery gate remain visible.

An independent support audit found only eight informative regions: three single-colony regions are absorbed by the fixed effects. The full 439 panel remains the observational cohort. Dropping 14 non-informative records leaves 425 records/82 sites/8 regions, with unchanged slopes and residual SSE. A subsequent design audit found uneven information: Victoria Land supplies 55.0% and Wilkes Land 19.0% for M_P. We therefore added one explicitly dated delete-one-region CV3 diagnostic, centred at the full coefficient vector with t(7), on the unchanged models and support. It was selected before calculating its new intervals. Figures compare CV3 with the archived eight-region CR1 intervals; original nominal-eleven CR1 results remain in Table S1 and numeric extracts.

The M_P CV3 interval is [−1.675, −0.331]‰/10pp and the salinity-adjusted interval [−1.515, −0.328]. For the matched temporal comparison, the 347 informative rows from the 358-record cohort give a difference −0.688 with CV3 interval [−1.470, +0.095]. Thus the main negative association remains, but the difference between winters is uncertain. No radius, lag, threshold, outcome or favourable biological subset was searched. CV3 is not a guarantee of finite-cluster coverage or a correction for exploratory selection.

## Reproduce offline

Run from this directory in Python 3.11 or later with the versions in `requirements-review.txt` (or equivalent compatible packages). No network request is made by these commands.

```bash
python verify_frozen_polynya_results.py --inputs-dir frozen_archives --temporal-csv verification_inputs/matched_temporal358.csv --out reproduced_numeric_receipt.json
python diagnose_region_jackknife.py --out reproduced_jackknife_receipt.json
python audit_polynya_estimand_scale_20261122.py --out reproduced_estimand_scale_receipt.json
python test_between_within_source439_20261122.py
python test_mertz_iceberg_event_source439_20261122.py --out-dir mertz_2010_event_outputs
python render_polynya_main_figures.py
python build_review_documents.py --out review_documents
```

The verifier independently projects explicit fixed-effect dummies and recalculates the archived fits, covariance contrasts, calibration-ensemble response sensitivity, information support and SSE reductions. It does not import the original fitting code. Expected result: `PASS_INDEPENDENT_REPRODUCTION_OF_EXISTING_FROZEN_POLYNYA_RESULTS`, 58 checks. Numerical equality is evaluated with declared tolerances, not a claim of byte-identical floating-point results across arbitrary hardware.

The separate jackknife script uses the same pinned rows, slope definitions and verified fixed-effect projection. It refits the eight regional omissions for six original/ensemble model–contrast combinations and checks 34 identities against frozen coefficients, original regional omissions and direct scalar contrast calculations. The checked input used by the renderer is `source_inputs/region_jackknife_diagnostic.json`; the renderer does not compute new intervals. The audit does not claim to have run CR2/Satterthwaite.

The figure renderer checks input SHA256 values, reconstructs the fixed 439 join, calculates descriptive site exposure means and the specified fixed-effect residual correlation, and plots the supplied coefficients. It does not refit ecological models. Cached verified projected coordinates permit offline rendering without pyproj. Recreating projection caches requires pyproj; the cache itself and its source attribution are supplied. The pale Antarctic land outline in Figure 1 is Natural Earth 1:110m cartographic context (public domain), not an exposure mask. Its source Git blob, checksum and projected cache are recorded in the manifest; adding the outline does not change any ecological input. Official terms: https://www.naturalearthdata.com/about/terms-of-use/.

Figures are 169 mm wide, with at least 10 pt text for review, editable SVG, PNG previews and approximately 800 dpi TIFF exports. TIFFs and Word outputs are generated deliverables, not required inputs for reproduction.

`build_review_documents.py` uses python-docx to create a double-spaced, line-numbered combined manuscript containing all five figures and their captions at the end, below the current 5 MB initial-submission limit. It also creates a supplementary document, a compact figure packet, separate figure Alt text, a cover-letter draft and the author-information form. It exports the 222-word abstract as plain text. Author identities and required attestations remain explicit placeholders. Rendering for visual review requires a separate DOCX renderer such as LibreOffice; Python dependencies alone do not supply that application.

## Included source-derived inputs

Four compact frozen analysis archives are included under `frozen_archives/`. These are derived project artifacts, not the original large provider archives.

| Archive | Original artifact ID | SHA256 |
|---|---:|---|
| polynya_main439.zip |14539734362|e413eab31b101c4a9a11c6dc7656d58906527a2146e6ccef442bb677ede6b233|
| polynya_physical.zip |14539723210|702ab3eeff9ed953c19a9e696492ba9bf5cddce204d40a9c7d9b1234d98f9f96|
| isotope860.zip |14328755565|dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205|
| author_R1000.zip |14680080746|be0234fef11a11b5b19129c8a84db0ab90dbe80b7cd6a71a3e733e36eaa1e342|

The exact temporal CSV is pinned separately in `verification_inputs/`; its SHA256 and original Git blob are checked by the numerical verifier. Small figure tables and projection caches are under `source_inputs/`, with source identity and content hashes in `source_manifest.json`. Provider data retain their authorship, DOI and original terms; this review bundle does not assign a new licence to those data.

[Source notices](submission_preparation/SOURCE_NOTICES.md) and the [reuse register](submission_preparation/SOURCE_REUSE_REGISTER.json) document attribution, provider-specific licences and transformations. Both principal Zenodo deposits specify CC BY 4.0. The 22 November follow-up verifies unrestricted-access/use statements in NOAA's daily and monthly Version 4 distribution metadata, while recording their unresolved DOI mismatch with the original NSIDC release. This is not an assignment of CC0 or a blanket redistribution licence. The project's own code-licence choice remains an author decision. Generated using E.U. Copernicus Marine Service Information; https://doi.org/10.48670/moi-00021.

## Reproduction scope and publication status

This package reproduces the frozen derived 439/358 models and the five main figures. It does not re-download or re-extract all original Landsat/DEEP-AA grids, refit the full published hierarchical diet model, independently validate the guano pixels, or evaluate 2013–2021 ecological outcomes. Its hashes support traceability within that scope.

The main inference remains limited by exploratory selection, eight unevenly informative regional clusters, approximate covariance sensitivities, an optical rather than direct isotope response, and unsuccessful prediction/independent-mechanism checks. The reported 10pp slope unit is much larger than the observed 1.6pp conditional exposure SD; presenting the slope alone would obscure its typical supported scale. The same-sample salinity coefficient is now reported explicitly (+0.646; CV3 interval [−0.196,+1.488]); the broader 860-row +0.834 coefficient remains separate context. Selected CMIP6 outputs are not used to project this local polynya measure or future diet.

Current MEPS instructions and linked publisher policies were retrieved from official pages on 21 November 2026 and used for the initial-review file preparation. [The requirement matrix](submission_preparation/MEPS_REQUIREMENTS.md) separates verified requirements from author-dependent fields. This remains an author-review package: human scientific review, author metadata/contributions, funding/conflict/ethics statements, the accurate AI-use acknowledgement and release decisions need author completion. Generative assistance is disclosed as substantive drafting, code and checks, not just grammar correction; policy eligibility is not automatically certified. No journal submission, new DOI publication, licence assignment or merge is part of this revision.
