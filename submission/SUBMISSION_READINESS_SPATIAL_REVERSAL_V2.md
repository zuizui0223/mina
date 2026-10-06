# PR189 spatial-reversal paper — Ecology Report submission readiness v2

## Target format

**Journal:** Ecology  
**Submission type:** Report

Current Ecology Author Guidelines were revised September 2026.

Report limits:
- maximum manuscript length: **20 pages**, including title page, References, figure captions and figures;
- abstract: **200 words maximum**;
- key words required;
- title: **120 characters maximum**.

Current draft:
- title: **60 characters**;
- abstract: **197 words**;
- manuscript text: approximately **3,122 words before a completed References section**.

The Report format is therefore appropriate if figures and references are kept concise.

## Required initial-submission formatting

Before submission, convert the Markdown manuscript to the journal main-document format and ensure:

- Word main document unless using LaTeX/PDF;
- 12-point Times New Roman;
- double spacing;
- continuous line numbering after the title page;
- page numbering including title, figure and table pages;
- Letter-size portrait pages;
- 1-inch margins;
- left-aligned text;
- title and author list exactly match ScholarOne;
- key words: minimum 6, maximum 12, alphabetized.

Current key words: 8. Alphabetize them in the title-page version.

## Main scientific status

**Scientific analysis: CLOSED.**  
**Mechanism search: CLOSED for PR189.**

Preferred manuscript spine:

    docs/MANUSCRIPT_RECOVERY_REDUNDANCY_V0_12.md

Submission draft:

    submission/MANUSCRIPT_SPATIAL_REVERSAL_ECOLOGY_V0_1.md

## Main claim

> Near-complete numerical rebound can be accompanied by a moderate, structured failure of exact spatial reversal among persistent breeding nodes.

Broader prospective-test claim:

> Aggregate breeding change and spatial reallocation are not sign-locked.

## Evidence hierarchy

### Ross natural experiment

1999 -> 2001 -> 2002:

- shock loss: 112,613;
- rebound: 109,198;
- aggregate loss restored: 96.97%;
- cosine(loss, rebound): 0.99695;
- exact inverse-path allocation mismatch: 9.41%.

Boundaries:
- the sharper 1999–2002 decomposition is a transparent post-result refinement after the frozen 2001–2012 prediction failed;
- 9.41% is moderate and similar to other Ross down->up episodes;
- no formal CI can be attached because source-specific component count error is unavailable.

### Bird Island Gentoo prospective sign test

Frozen 1981 -> 2024 endpoint:

- N +34.2%;
- E +15.7%.

Preallowed annual audit contains all four N/E sign combinations.

Boundary:
- not a preidentified disturbance/recovery interval.

### Global emperor prospective decline test

Frozen 50-colony 2009 -> 2018 posterior-median endpoint:

- N -12.4%;
- E -12.8%;
- 30 colonies down, 20 up.

Predeclared regional sensitivity contains all four N/E quadrants.

Boundary:
- posterior-median point estimates only;
- no joint-posterior probability for E.

## Mechanism closure

Bird operational success:
- frozen statistical PASS;
- interpretation compromised by shared-denominator/monitoring geometry.

Port Lockroy:
- SUPPORT FAIL.

Signy ratio-free late output:
- beta -0.0225;
- p 0.6837;
- TERMINAL FAIL.

Ross subcolony perimeter-to-area:
- beta -0.0196;
- p 0.1514;
- TERMINAL FAIL.

No further mechanism search is allowed in PR189.

## Figure package

PR189-specific figure builder:

    scripts/build_spatial_reversal_figures.py

Workflow:

    .github/workflows/spatial-reversal-figures.yml

Planned main figures:

1. Ross disturbance/rebound path;
2. observed versus exact inverse-path rebound;
3. Bird + Emperor prospective sign tests.

Use the Report's page limit aggressively: do not add Heard/Beaufort/Palmer figures to the main document.

## Open Research requirements

ESA requires underlying data and novel statistical code pertinent to published results to be placed in a permanent public archive by acceptance.

Before initial submission:
- prepare the required **Open Research Statement** for the title page and ScholarOne;
- decide whether the current public GitHub repository is sufficient for reviewer access or create a permanent archival snapshot/DOI;
- ensure all public source datasets are fully cited;
- do not upload CSV/data files as manuscript supporting information when the Open Research policy requires external archiving.

Preferred path:
- archive the exact PR189 release in Zenodo or Dryad;
- cite the immutable archive rather than a moving branch.

## AI disclosure

ESA's current AI policy requires disclosure when generative AI was used in:
- manuscript writing;
- images;
- data collection or analysis.

Required for this paper:

1. retain section-specific disclosure where computational assistance is described;
2. add an explicit **Acknowledgments AI disclosure**;
3. disclose the same use in the ScholarOne submission form;
4. do not list an AI system as an author.

Suggested acknowledgment wording:

> OpenAI ChatGPT (GPT-5.6 Sol) was used to assist with code drafting and review, literature searching, statistical sensitivity-analysis scripting, and editorial drafting. All analyses, source verification, scientific decisions, interpretations, and final text were reviewed and remain the responsibility of the authors.

## Remaining editorial blockers

1. **Bibliography**
   - verify/add Bird Island dataset citation;
   - verify/add global emperor analysis citation;
   - add closest metapopulation-recovery and spatial-synchrony references;
   - ensure Ross iceberg/access references are complete;
   - verify all DOI metadata.

2. **Title page**
   - author list and affiliations;
   - corresponding author;
   - Open Research Statement;
   - alphabetized key words;
   - AI disclosure also repeated in Acknowledgments.

3. **Figures**
   - run and inspect the new figure workflow;
   - verify text remains readable at journal-page size;
   - ensure captions cite published datasets where required.

4. **Supplement**
   - count-uncertainty audit;
   - bounded-count sensitivity;
   - Ross mismatch context;
   - Bird temporal audit;
   - mechanism closure and failed routes.

5. **Transparency**
   - retain explicit statement that the focal 1999–2002 Ross decomposition is post-result;
   - retain the failed frozen 2001–2012 prediction in the audit trail.

## Scientific blockers

**None requiring new ecological effects.**

## Stop rules

Do not add:
- another species solely to increase case count;
- another predictor from opened datasets;
- alternate mechanism lags;
- alternative Schmidt terrain variables;
- new concentration metrics;
- tuned Ross anchor years;
- significance claims for the descriptive 9.41% mismatch.

Allowed:
- references;
- copyediting;
- figure construction from frozen outputs;
- archival packaging;
- journal formatting;
- reviewer stress testing without new effects.

## Submission assessment

**Ecology Report is now the appropriate target and format.**

The paper should be sold as:
- a documented disturbance/rebound natural experiment;
- a calibrated spatial-restoration effect;
- two prospective external sign tests;
- transparent measurement and mechanism boundaries.

It should **not** be sold as:
- an unusually large Ross anomaly;
- a new mathematical framework;
- a confirmed mechanism;
- a universal penguin recovery law.
