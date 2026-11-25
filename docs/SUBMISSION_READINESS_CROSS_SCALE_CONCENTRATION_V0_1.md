# Submission readiness — cross-scale concentration v0.1

**Date:** 2026-10-03  
**Status:** scientific analysis closed; journal-specific packaging not yet frozen.

## Active files

- Main manuscript: `docs/MANUSCRIPT_CROSS_SCALE_CONCENTRATION_V0_1.md`
- Supporting Information: `docs/SUPPLEMENT_CROSS_SCALE_CONCENTRATION_V0_1.md`
- Figure captions: `docs/FIGURE_CAPTIONS_CROSS_SCALE_CONCENTRATION_V0_1.md`
- Claim contract: `contracts/CROSS_SCALE_CONCENTRATION_MANUSCRIPT_V0_1.json`
- Reviewer audit: `docs/CROSS_SCALE_CONCENTRATION_REVIEWER_AUDIT_V0_1.md`
- Regional result receipt: `results/MAPPPD_REGIONAL_CONCENTRATION_RECEIPT_V2.json`
- Draft PR: #166

Approximate text length before journal formatting:

- main manuscript: ~4,370 whitespace-delimited words including headings, equations and data-availability text;
- supplement: ~1,580 words.

## Scientific claim ladder

### Confirmatory / strongest

1. **Within-system contraction beyond proportional thinning.**
   - Three Palmer Adélie discovery populations show concentration under the complete frozen count-error family.
   - Prospectively frozen Signy Adélie independently replicates the endpoint geographically.
   - Separately frozen Signy chinstrap replicates the endpoint across species.

2. **The endpoint is not a universal large-component refuge.**
   - Palmer and Signy reach concentration through contrasting component-dominance routes.
   - This is a descriptive mechanism boundary, not a causal mechanism test.

### Bounded extension / moderate

3. **Cross-scale directional recurrence within Antarctic Pygoscelis.**
   - Four of four estimable declining MAPPPD regional networks have positive observation-error-calibrated delta-kappa.
   - Two South Shetland panels are individually supported under both frozen regional nulls.
   - This is a scale-transfer test, not another independent geographic replication and not a family-wide regional rejection test.

### Descriptive only

4. **Direction transfers more consistently than magnitude.**
   - Local and regional raw kappas vary widely; the local ~0.25 value is not universal.

5. **Breeding-space structure may be slower than abundance.**
   - Local first-difference coupling is weak.
   - Three increasing regional panels end with lower E.
   - No formal regional hysteresis claim is allowed.

## Scientific issues that are closed, not pending

The following are limitations of the available evidence, not analysis tasks to be “fixed” using the same data:

- regional panels are taxonomically restricted to Pygoscelis;
- only two species contribute declining regional networks;
- regional panel counts are small and some have five complete seasons;
- the two individually supported regional declines share the South Shetland region;
- MAPPPD observation methods are heterogeneous;
- APBP regions are monitoring networks, not closed populations;
- component units are not equal-area habitat patches;
- local and regional primary statistics differ;
- aggregate counts cannot identify movement, recruitment, fidelity or habitat mechanisms.

These points are explicitly bounded in the manuscript and supplement. They do not authorize new thresholds, regions, lags, transformations or p-value rules.

## Technical readiness

- Regional analysis workflow: passing.
- Repository CI: passing on the active branch after manuscript-boundary tests.
- Cross-scale figure workflow: passing.
- Figures visually checked after label-overlap corrections.
- All manuscript citation keys are checked against `docs/REFERENCES_V6.bib`.
- Manuscript numbers are linked by tests to committed Palmer, Signy and MAPPPD receipts.
- Live BAS download dependency was removed from the cross-scale figure workflow by reusing the previously frozen source-checked Palmer/Signy figure-data artifact.

## Remaining work before submission

These are packaging decisions rather than additional ecological analyses:

1. choose one target journal and freeze journal-specific framing;
2. format title page, author affiliations, acknowledgements and contribution statement;
3. convert the active manuscript and supplement to the journal-required submission files;
4. freeze the final figure set and journal-specific dimensions;
5. check reference formatting and DOI completeness for that journal;
6. write a cover letter that leads with abundance-conditioned cross-scale concentration, not the post-hoc kappa value;
7. perform one final consistency audit of abstract, figures, SI and Data Availability;
8. archive the submitted commit/artifacts after the submission version is frozen.

## Current submission-level conclusion

> In Antarctic Pygoscelis, decline repeatedly redistributes breeding effort toward fewer effective monitored breeding components beyond proportional thinning. Prospectively frozen Signy tests establish geographic and cross-species replication within breeding systems, while a bounded MAPPPD extension shows that the same direction can remain visible when components are redefined as breeding sites within regional monitoring networks. The transferable feature is the direction of spatial reorganization, not a universal exponent or mechanism.

## Stop rule

Scientific analysis on these data is closed for this manuscript. Further strengthening of taxonomic or mechanistic generality requires a genuinely new independent data source.
