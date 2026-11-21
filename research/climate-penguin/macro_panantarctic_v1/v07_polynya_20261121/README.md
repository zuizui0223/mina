# Polynya manuscript v0.7 — current author-review candidate

This is the single current manuscript candidate in Draft PR #214 of `zuizui0223/mina`. It supersedes the nest-exposure-centred v0.6 presentation; earlier manuscripts and frozen analyses remain historical records. Original source analyses are pinned to `a1cf988df3501794e9add243a8c2be8ecbb7b43a`.

## Read the manuscript

1. [Main manuscript and 218-word abstract](MANUSCRIPT_POLYNYA_FOODWEB_WORKING.md)
2. [Supplementary methods and results](SUPPLEMENT_POLYNYA_FOODWEB.md)
3. [Figure sources and output](figures/), [alt text](figure_alt_text.json)
4. [Independent numerical reproduction](reproduction_receipt.json), [figure verification](figures/polynya_figure_verification_receipt.json)
5. [Literature and publication-status notes](REVIEW_NOTES_JA.md)

The question is whether June–October coastal-polynya area fraction within 100 km is associated with the subsequent November–February optical Adélie δ¹⁵N signal, after measured summer conditions and fixed effects. This is a retrospective exploratory reanalysis of released source pixels, not direct dietary measurement or a new independent ecological sample.

## What changed in this revision

The main narrative now follows winter polynya association, temporal comparison, salinity distinction, measurement sensitivity and unresolved biological interpretation. Nest-weighted climate exposure is supplementary context. The negative direction contradicts the original positive hypothesis and is disclosed in the abstract. Failed forward prediction, weaker later-period point estimates, selective chlorophyll support, inconclusive Signy stomach-content evidence and the unsuccessful later-period guano-recovery gate remain visible.

An independent support audit found only eight informative regions: three single-colony regions are absorbed by the fixed effects. The full 439 panel remains the observational cohort. Dropping 14 non-informative records leaves 425 records/82 sites/8 regions, with unchanged slopes and residual SSE. The newly dated 21 November 2026 covariance sensitivity is the main displayed interval; the original frozen 11-region intervals are preserved in Supplement Table S1 and the numeric extracts. The matched temporal comparison uses 358 observations, or 347 informative observations in 8 regions for its uncertainty sensitivity. No radius, lag, threshold or favourable biological subset was searched during this revision.

## Reproduce offline

Run from this directory in Python 3.11 or later with the versions in `requirements-review.txt` (or equivalent compatible packages). No network request is made by these commands.

```bash
python verify_frozen_polynya_results.py --inputs-dir frozen_archives --temporal-csv verification_inputs/matched_temporal358.csv --out reproduced_numeric_receipt.json
python render_polynya_main_figures.py
python build_review_documents.py --out review_documents
```

The verifier independently projects explicit fixed-effect dummies and recalculates the archived fits, covariance contrasts, calibration-ensemble response sensitivity, information support and SSE reductions. It does not import the original fitting code. Expected result: `PASS_INDEPENDENT_REPRODUCTION_OF_EXISTING_FROZEN_POLYNYA_RESULTS`, 58 checks. Numerical equality is evaluated with declared tolerances, not a claim of byte-identical floating-point results across arbitrary hardware.

The figure renderer checks input SHA256 values, reconstructs the fixed 439 join, calculates descriptive site exposure means and the specified fixed-effect residual correlation, and plots the supplied coefficients. It does not refit ecological models. Cached verified projected coordinates permit offline rendering without pyproj. Recreating projection caches requires pyproj; the cache itself and its source attribution are supplied. The pale Antarctic land outline in Figure 1 is Natural Earth 1:110m cartographic context (public domain), not an exposure mask. Its source Git blob, checksum and projected cache are recorded in the manifest; adding the outline does not change any ecological input. Official terms: https://www.naturalearthdata.com/about/terms-of-use/.

Figures are 170 mm wide, with editable SVG, PNG previews and approximately 800 dpi TIFF exports. TIFFs and Word outputs are generated deliverables, not required inputs for reproduction.

`build_review_documents.py` uses python-docx to create the double-spaced, line-numbered manuscript, a supplementary document and a five-page figure packet. It also exports the abstract as plain text. Word is a review layout; authorship and submission declarations are not manufactured. Rendering to page images for visual review requires a separate DOCX renderer such as LibreOffice. Python dependencies alone do not supply that application.

## Included source-derived inputs

Four compact frozen analysis archives are included under `frozen_archives/`. These are derived project artifacts, not the original large provider archives.

| Archive | Original artifact ID | SHA256 |
|---|---:|---|
| polynya_main439.zip |14539734362|e413eab31b101c4a9a11c6dc7656d58906527a2146e6ccef442bb677ede6b233|
| polynya_physical.zip |14539723210|702ab3eeff9ed953c19a9e696492ba9bf5cddce204d40a9c7d9b1234d98f9f96|
| isotope860.zip |14328755565|dfbbe281e50e7d802c43f69255c02878a4c49c14185804acb7e15048189af205|
| author_R1000.zip |14680080746|be0234fef11a11b5b19129c8a84db0ab90dbe80b7cd6a71a3e733e36eaa1e342|

The exact temporal CSV is pinned separately in `verification_inputs/`; its SHA256 and original Git blob are checked by the numerical verifier. Small figure tables and projection caches are under `source_inputs/`, with source identity and content hashes in `source_manifest.json`. Provider data retain their authorship, DOI and original terms; this review bundle does not assign a new licence to those data.

## Reproduction scope and publication status

This package reproduces the frozen derived 439/358 models and the five main figures. It does not re-download or re-extract all original Landsat/DEEP-AA grids, refit the full published hierarchical diet model, independently validate the guano pixels, or evaluate 2013–2021 ecological outcomes. Its hashes support traceability within that scope.

The main inference remains limited by exploratory selection, only 8 informative regional clusters, an approximate archived CR1 convention, an optical rather than direct isotope response, and unsuccessful prediction/independent-mechanism checks. The broader 860-row salinity coefficient is not a same-sample second effect in the 439-row model. Selected CMIP6 outputs are not used to project this local polynya measure or future diet.

This is ready for author review, not certified as administratively ready for journal submission. Current MEPS instructions, author metadata/contributions, funding/competing-interest/AI-use statements, final redistribution conditions and a permanent public archival DOI require completion by the authors. No journal submission or DOI publication is part of this revision.
