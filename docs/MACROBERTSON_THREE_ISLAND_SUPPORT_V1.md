# Mac.Robertson three-island route — data-access block

**Status:** DATA ACCESS BLOCKED; effect remains unopened.

The V1 contract was frozen before any three-island count magnitude was inspected.

## What is independently known

AADC metadata confirms that the dataset contains:

- Bechervaise Island counts;
- Verner Island counts;
- Petersen Island counts;
- year/date/season;
- occupied nests.

For post-1990/91 data, counts are occupied nests collected on or about 2 December during incubation.

This is well aligned with the Ross response variable.

## Retrieval result

The frozen GitHub Actions route requested:

    https://data.aad.gov.au/eds/1103/download

and completed successfully at the HTTP level.

However the artifact is not an Excel workbook.

It is a small HTML shell for the current AADC JavaScript download application.

The current AADC EDS workflow requires submission of an email address before file/S3 access is issued.

Therefore no workbook schema, missingness or magnitude has been opened through this route.

## Decision

This is **not** SUPPORT FAIL in the biological/data-design sense.

It is:

    DATA ACCESS BLOCKED
    effect unopened
    recovery gate unevaluated
    E unevaluated.

## Prohibited rescue

Do not:

- use the published Bechervaise-only table plus guessed Verner/Petersen values;
- infer three-island direction from Bechervaise's known positive trend;
- switch to an older pre-1990 interval;
- select a different period from public snippets;
- treat metadata as if it contained the count matrix.

## Allowed continuation

The V1 contract remains reusable if the exact AADC workbook is later obtained through a legitimate file-level delivery.

At that point:

1. inspect missingness only;
2. mechanically freeze endpoints under V1;
3. open magnitudes once;
4. evaluate N, E, proportional residuals and dominant identity exactly as written.
