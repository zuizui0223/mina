# Western Mac.Robertson Land 2009–2019 route — data-access block

**Status:** DATA ACCESS BLOCKED; effect remains unopened.

The pre-effect contract `MACROBERTSON_2009_2019_SPATIAL_REDUNDANCY_V1` was committed before any site-level standardized occupied-nest magnitude was inspected.

## Intended source

Australian Antarctic Division / Emmerson & Southwell dataset:

**Population counts, resights and demography of Adelie Penguins in Mac. Robertson Land, Antarctica, 1991–2019**

The public metadata describes a population-estimate workbook containing standardized occupied-nest estimates for 2009/10 and 2019/20 across western Mac.Robertson Land, with bootstrap uncertainty.

## Audited retrieval

After the contract was frozen, GitHub Actions requested:

    https://data.aad.gov.au/eds/5516/download

Workflow:

    MacRobertson 2009-2019 support package v1
    run 37460714587

Artifact:

    id 11411202908
    digest sha256:48910ce9d648d1d7b7abfce5894a8fbe87b9efe1290438e8839534229cc027b3

The returned object is **not** the population-estimate workbook or a data archive.

It is a 1,211-byte HTML shell for the current Australian Antarctic Data Centre web application.

No site names, paired-support roster, bootstrap indices, occupied-nest magnitudes, totals, shares or E values were exposed by this retrieval.

## Decision

The route is:

    DATA ACCESS BLOCKED
    effect unopened
    paired-site support gate unevaluated
    recovery gate unevaluated
    spatial-redundancy endpoint unevaluated.

This is not biological SUPPORT FAIL.

## Prohibited rescue

Do not:

- reconstruct site values from publication snippets;
- use regional totals in place of the frozen site-level endpoint;
- change years;
- switch to a favorable site subset;
- assume bootstrap draws are independent;
- use the older Bechervaise/Verner/Petersen route as a substitute after seeing metadata.

## Allowed continuation

The contract remains reusable if the exact population-estimate workbook is later available through a legitimate public/file-level delivery.

Then the sequence remains:

1. inspect schema, site IDs, paired support and bootstrap indexing only;
2. freeze the paired roster mechanically under the existing contract;
3. open standardized medians once;
4. evaluate N, E, TV, dominance, proportional residuals and local-count arithmetic exactly as written.

## Consequence for PR189

The Mac.Robertson system remains an unusually good **prospective external test**, but it contributes no outcome evidence to the current PR.

The Ross/Heard/Beaufort synthesis must not imply that Mac.Robertson has replicated any spatial-recovery pattern.
