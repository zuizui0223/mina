# Bird Island gentoo six-unit support audit v1

**Status:** SUPPORT PASS; endpoints frozen before count magnitudes are opened.

## Source

BAS / NERC Polar Data Centre, DOI `10.5285/8fedb5a0-b98c-4457-9d86-aae9c6d3ed8e`.

The public RAMADDA package was downloaded after the pre-effect contract was committed.

## Schema

The CSV contains:

- species;
- colony;
- nest-count date;
- incubating/occupied nest count;
- chick-count date;
- chick count;
- comments.

No nest-count magnitude was summarized during this audit.

## Fixed six-unit roster

Contract label -> CSV label:

- Johnson Beach -> `Johnson`
- Square Pond -> `Square Pond`
- Upper Natural Arch -> `Upper Natural Arch`
- Lower Natural Arch -> `Lower Natural Arch`
- Upper Mountain Cwm -> `Upper Mountain Cwm`
- Lower Mountain Cwm -> `Lower Mountain Cwm`

Provider metadata also contains `Landing Beach` and a generic `Mountain Cwm` record, but these are excluded exactly as frozen in the contract.

## Structural support

- Each fixed unit has at most one usable nest-count row per calendar breeding-season start year.
- Nest counts span calendar start years 1981–2024.
- Counts occur in October–December.
- There are 43 complete six-unit seasons.
- The only incomplete year in the span is 1982, missing Lower Natural Arch.

## Frozen endpoints

Under the pre-effect rule:

    start = earliest complete six-unit season
    end   = latest complete six-unit season

the endpoints are now irreversibly frozen as:

    1981 -> 2024

before any numerical nest magnitude is inspected.

The next step is allowed to open exactly the twelve endpoint counts, evaluate the recovery gate N2024 > N1981, and then compute E, proportional residuals, local signs and dominance turnover.

No subinterval search is allowed afterward.
