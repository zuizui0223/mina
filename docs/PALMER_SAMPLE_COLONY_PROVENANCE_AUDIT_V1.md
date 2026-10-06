# Palmer sample-colony source-provenance audit v1

**Status:** source-interpretation correction for the active Ecology submission. No numerical endpoint, null simulation, roster, p-value, or result is changed.

## Frozen source actually analysed

The Palmer analysis downloads the public ERDDAP table `AdeliePenguinCensus`, whose embedded DOI is:

- DOI: `10.6073/pasta/89dd52217ca37e3a72a67f7a9bc3c82e`
- EDI package revision resolved from that DOI: **knb-lter-pal.87.7**
- ERDDAP time coverage: 1991–2017
- fields: study name, island, colony code, breeding-pair count.

The active manuscript must therefore describe exactly this frozen table rather than a later EDI revision.

## What the table represents

A historical 1993/94 Palmer field-season report states that breeding population size was monitored by counting breeding pairs in **54 sample colonies** during the peak egg-laying census; those sample colonies contained **6,165 pairs** in 1993, versus 6,216 in 1992.

The frozen ERDDAP table for the 1993 season contains:

- 56 reported colony-code rows across CHR, COR, HUM, LIT and TOR;
- exactly **54 positive-count colony codes** plus two reported zeroes;
- summed count = **6,231 pairs**.

The near one-to-one match in number of positive monitored colonies, together with the similar total, identifies the frozen ERDDAP rows as the historical **sample-colony monitoring panel**, not an exhaustive enumeration of all physical sub-colonies on each island.

Independent published whole-island estimates make the distinction explicit. For example, Cimino et al. (2019) report Torgersen declining from 8,119 to 1,200 breeding pairs and Humble from 2,485 to 575 over 1991–2016, whereas the frozen ERDDAP sample-colony sums are substantially smaller. Cimino et al. (2025), using EDI revision 8, report 7,255 breeding pairs on Torgersen in 1993, versus 2,868 in the frozen ERDDAP sample panel.

## Consequence for existing analyses

### What remains valid

The Palmer concentration analysis is calculated entirely within fixed reported colony-code rosters. Its estimand is:

> whether relative breeding-pair allocation among the monitored sample-colony components changes more strongly than expected under a fixed component-share vector conditioned on the observed **summed monitored-panel abundance**.

That calculation, its count-error nulls, and its numerical results do not require the monitored components to exhaust the island population.

Therefore the frozen Palmer results remain numerically unchanged:

- Cormorant E −19.1%;
- Humble E −50.6%;
- Litchfield E −82.7%;
- same frozen Monte Carlo probabilities.

### What must be corrected

The active submission must not call the ERDDAP sum:

- a complete island population census;
- an island-wide population total;
- an exhaustive census of all physical breeding sub-colonies.

Use instead:

- **Palmer sample-colony monitoring network**;
- **monitored colony-code components**;
- **summed monitored-component abundance**.

Likewise, concentration among these components is a population-organization endpoint at the monitoring-unit level. It is not itself a direct measurement of total occupied nesting area.

## Relation to physical Torgersen evidence

Cimino et al. (2025) independently reconstruct 23 historical physical Torgersen sub-colonies and five active historical footprints by 2022. That physical evidence remains valuable as phenomenon-level triangulation, but the frozen ERDDAP colony codes are not one-to-one physical polygon identifiers.

A count-based attempt to crosswalk the two was rejected: the 1993 physical full-island total (7,255 pairs) and frozen ERDDAP Torgersen sample-panel total (2,868 pairs) are not the same sampling universe.

## Later EDI revisions

Cimino et al. (2025) cite EDI revision **knb-lter-pal.87.8** (1991–2021). The current EDI series has reached revision 10. As of July 30, 2026, EDI requires authentication for REST API access, so the historical revision-8 raw entity was not opened in this audit.

This does not justify silently substituting a newer revision into the already-frozen analysis. Any future reanalysis with revision 8/10 must be a separate source-version robustness route.

## Submission action

Correct observational-unit wording throughout the active Ecology package, regenerate the DOCX/SI, and repeat visual/structural QA.

No new ecological endpoint is authorized by this provenance correction.
