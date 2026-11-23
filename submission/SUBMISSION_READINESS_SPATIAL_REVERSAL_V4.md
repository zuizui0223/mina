# PR189 spatial-reversal paper — Ecology Report submission readiness v4

## Target format

**Journal:** Ecology  
**Submission type:** Report

Current Ecology Author Guidelines were revised September 2026.

Report limits:
- maximum manuscript length: **20 pages**, including title page, References, figure captions and figures;
- abstract: **200 words maximum**;
- key words required;
- title: **120 characters maximum**.

Current preferred draft:
- title: **79 characters**;
- abstract: **173 words**;
- manuscript: `submission/MANUSCRIPT_SPATIAL_REVERSAL_ECOLOGY_V0_4.md`;
- dedicated bibliography: `submission/REFERENCES_SPATIAL_REVERSAL_V2.bib`;
- citation-key audit: **0 missing keys**.

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

    submission/MANUSCRIPT_SPATIAL_REVERSAL_ECOLOGY_V0_3.md

## Main claim

> A severe breeding disturbance was followed by rapid, largely reversible spatial recovery; near-complete numerical rebound left only a moderate, structured deviation from exact proportional reversal.

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

## Bibliography and citation status

Dedicated canonical bibliography:

    submission/REFERENCES_SPATIAL_REVERSAL_V2.bib

The preferred manuscript currently cites 12 keys, all present in the dedicated bibliography.

Coverage includes:
- spatial synchrony prior art;
- spatial-recovery theory;
- community abundance/composition recovery;
- Ross census and iceberg natural experiment;
- Bird Island dataset;
- global Emperor analysis;
- Signy dataset;
- Ross subcolony habitat study.

Reference rendering and DOI visual verification remain production QA only.

## Figure package

PR189-specific figure builder:

    scripts/build_spatial_reversal_figures.py

Workflow:

    .github/workflows/spatial-reversal-figures.yml

Main figures:

1. Ross disturbance/rebound path;
2. inverse-path expected versus observed rebound plus residual-allocation panel;
3. Bird + Emperor prospective sign tests.

Figure QA completed:
- Figure 1 uses categorical x positions so 2001/2002 labels no longer overlap;
- Figure 2 now makes both high overall reversibility and the Crozier West residual visible;
- Figure 3 is legible at review size.

Canonical caption source:

    submission/FIGURE_CAPTIONS_SPATIAL_REVERSAL_V0_2.md

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

## Final literature-positioning update

Foundational spatial-synchrony references have been added to the canonical bibliography and manuscript to make clear that shared forcing and dispersal can couple local trajectories; this is prior art, not claimed novelty.

A reviewer-defense dominance audit also shows that the high Ross loss/rebound alignment is not solely generated by Cape Crozier West (five-component normalized overlap 83.2% after removing that component). This diagnostic remains supplementary/post-result.

## Remaining submission blockers

There are **no scientific blockers requiring new ecological effects**.

Human-controlled fields still required:

1. final author list/order;
2. affiliations and present addresses;
3. exactly one corresponding author and email;
4. funding agencies and grant identifiers;
5. Acknowledgments;
6. Author Contributions / CRediT roles;
7. Conflict of Interest statement;
8. ORCIDs if requested;
9. complete AI-tool inventory;
10. dual-publication/preprint overlap statement;
11. immutable archive DOI/persistent identifier for the Open Research Statement.

Production steps after those fields are supplied:

1. generate the final Main Document;
2. insert title page and finalized Open Research Statement;
3. render the dedicated bibliography;
4. append grouped figure captions followed by one figure per page;
5. verify <=20 total pages;
6. visually inspect the generated Word/PDF;
7. make ScholarOne fields exactly match the Main Document.

Templates already available:

    submission/TITLE_PAGE_SPATIAL_REVERSAL_ECOLOGY_TEMPLATE_V1.md
    submission/ECOLOGY_SPATIAL_REVERSAL_COPY_FIELDS_V1.md

Transparency requirements that must remain:
- the focal 1999–2002 decomposition is explicitly post-result;
- the failed frozen 2001–2012 prediction remains in the audit trail.

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

**Scientific content is ready for an Ecology Report; remaining work is metadata, archival, and final document production.**

The paper should be sold as:
- quantified high spatial reversibility after a severe documented disturbance;
- a moderate residual deviation from exact proportional reversal;
- two prospectively frozen external sign tests showing that aggregate direction does not determine spatial direction;
- transparent measurement, post-result, and mechanism boundaries.

It should **not** be sold as:
- an unusually large Ross anomaly;
- a new mathematical framework;
- a confirmed mechanism;
- a universal penguin recovery law.
