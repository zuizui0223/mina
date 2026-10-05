# Guillemot source-semantics audit v1

**Date:** 2026-10-05  
**Status:** metadata-only audit after preregistration freeze and before biological effect calculation.

## Source package

EIDC dataset:
- DOI: 10.5285/33b42f0a-12a5-47fe-aaaf-25f4ee5e13a5

The NERC Digital Solutions Hub public metadata mirror identifies the focal raw file as:

`JAE_Bennett_CommonGuillemot_sitequality_occupancy.csv`

## Frozen raw-to-standardized mapping

| Raw field | Standard field | Meaning |
|---|---|---|
| `Subcolony` | `subcolony` | stable sub-colony identifier |
| `Site.number` | `site_id` | breeding-site identifier |
| `Year` | `year` | study year |
| `Occupancy.status` | `occupied` | 1 = occupied; 0 = unoccupied |
| `Subcolony.size` | `subcolony_size` | annual number of occupied breeding sites in the sub-colony |

Null values in the source package are coded `NA`.

Rows with `NA` in any of these five required fields are omitted from the standardized table and therefore break calendar-consecutive site histories. Missing values are never converted to zero.

No use is made of:

- `Quality`;
- `Trend.phase`;
- `Trend.slope`;
- `Colonisation.phase`;
- whole-colony size;
- any scaled/derived trend field.

Those fields are deliberately excluded from the primary same-site test.

## Identity and observation semantics resolved from public documentation

The public study methods and NERC metadata establish that:

- 1,664 breeding sites were followed across five sub-colonies;
- each breeding site received a unique ID from the year it was first occupied;
- sites were mapped photographically for consistent multi-year monitoring;
- sub-colony boundaries remained constant;
- breeding sites were monitored during the breeding season;
- occupancy was analysed as an explicit binary site-year response: occupied versus unoccupied;
- sub-colony size is the number of occupied breeding sites in that sub-colony and year.

Therefore the primary adapter uses explicit `Occupancy.status`; it does **not** infer vacancy from absent rows.

## Important biological boundary

A year coded unoccupied is an annual breeding-site vacancy state. It is not assumed to imply:

- permanent abandonment;
- death of the previous breeder;
- emigration;
- inability of the same individual to breed;
- permanent local extinction.

Published work notes occasional skipped breeding, which is why the preregistered >=2-year-vacancy analysis remains a secondary sensitivity.

## Adapter invariants

The adapter must:

1. read only the five frozen raw fields;
2. preserve 0/1 occupancy exactly;
3. preserve the source `Subcolony.size`;
4. reject duplicate subcolony × site × year rows;
5. require one unique `Subcolony.size` within each subcolony × year;
6. drop required-field `NA` rows rather than impute;
7. perform no phase filtering and no outcome-dependent site selection.

No raw biological effect is calculated by the adapter.
