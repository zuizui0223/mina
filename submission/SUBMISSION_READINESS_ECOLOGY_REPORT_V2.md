# Ecology Report submission readiness v2

## Scientific status

**Frozen. No new ecological endpoint should be added before initial submission.**

Primary structure:
1. Palmer Adélie discovery system
2. prospectively frozen Signy Adélie external replication
3. prospectively frozen Signy chinstrap cross-species replication

Primary claim:
> Declining breeding populations in two Pygoscelis species and two Antarctic monitoring systems lost effective monitored breeding-component number faster than expected under proportional thinning plus frozen count-error models.

## Palmer code-semantics audit

Completed and recorded in docs/PALMER_COLONY_CODE_CONTINUITY_AUDIT_V1.md.

Public evidence supports interpreting colony_code as an island-specific colony identifier and shows historical colony-level mapping/monitoring. However, no public versioned spatial-boundary crosswalk was found for every code across 1991–2017.

Consequences already implemented:
- Palmer is explicitly the discovery system.
- Palmer units are called monitored census colonies/components, not fixed GIS polygons.
- confirmatory weight is placed on the prospectively frozen Signy tests.
- the Palmer-versus-Signy dominant-unit comparison is no longer part of the Abstract or central claim.
- dominant-unit trajectories are Supplementary Figure S1 only and described as nominal census-unit trajectories.

## Current manuscript package

- manuscript: submission/MANUSCRIPT_ECOLOGY_REPORT_V0_4.md
- rough manuscript word count: ~1,908 before full references
- abstract: 149 words
- title: 80 characters
- keywords: 8
- main figures: 2
- supplementary figures: 1
- tables: 0

## Main figures

1. figure1_replicated_trajectories.pdf
2. figure2_cross_population_summary.pdf

Supplement:
- figureS1_nominal_dominance_routes.pdf

## Journal-format items already implemented

- Ecology Report framing
- abstract under 200 words
- title under 120 characters
- Open Research Statement text
- AI-use disclosure in Methods
- AI-use disclosure text for Acknowledgments/submission form
- PDF figure export
- Word builder with title page separated from continuously line-numbered manuscript body
- Letter page size, 1-inch margins, Times New Roman 12 pt, double-spaced body, page numbers

## Human-confirmation items still required

- final author list/order
- affiliations and present addresses
- corresponding author and email
- funding/grant wording
- additional acknowledgments
- CRediT/Author Contributions
- Conflict of Interest Statement
- complete AI-tool inventory
- dual-publication/overlap confirmation
- ORCIDs if requested

Use submission/ECOLOGY_METADATA_TEMPLATE.json as the private metadata template. Do not commit completed contact metadata unless all authors agree.

## Palmer data-semantics inquiry

Draft: submission/PALMER_COLONY_CODE_CONTINUITY_INQUIRY_DRAFT.md

Recommended action before or during submission: send the inquiry to the official dataset scientific contributor/data team. A response confirming stable boundary/code semantics can strengthen the Supplementary interpretation, but the main confirmatory Signy result does not depend on that response.

## Stop rules

- no new concentration metric
- no new threshold
- no tuned time window
- no additional species used as post-result rescue
- no new mechanistic endpoint
- no promotion of Supplementary nominal-unit turnover into a causal mechanism without provider confirmation

Allowed before submission:
- copyediting
- reference completion
- formatting
- author metadata
- figure QA
- archival metadata
- clarification from data providers
