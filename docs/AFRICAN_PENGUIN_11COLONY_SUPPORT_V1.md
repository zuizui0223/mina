# African penguin 11-major-colony route — support result v1

**Status:** SUPPORT FAIL; effect remains unopened.

The contract `AFRICAN_PENGUIN_11COLONY_DECLINE_ALLOCATION_V1` froze 1989 and 2019 before colony magnitudes were inspected.

## Public JARA support audit

Audited source:

    Henning-Winker/JARA
    Afr_penguin/Fits_Afr_penguin_s1.csv

Columns:

    assessment
    scenario
    name
    year
    obs
    obs.err
    hat
    lci
    uci
    lpp
    upp
    residual

The file contains exactly 11 colony-series names:

- Bird.Island
- Boulders
- Dassen.Island
- Dyer.Island
- Halifax
- Ichaboe
- Mercury
- Possession
- Robben.Island
- St.Croix.Island
- Stony.Point

No count magnitude was summarized during support audit.

## Frozen-endpoint support

The fitted example spans:

    1979–2017.

Therefore:

    2019 rows = 0.

At the 1989 endpoint only six of the eleven series have rows in this fitted-output file.

Thus the frozen source hierarchy cannot supply one common 11-colony endpoint at both 1989 and 2019.

## Decision

    frozen endpoint support: FAIL
    decline gate: not evaluated
    N: not computed
    E: not computed
    effect: unopened.

Do not replace 2019 with 2017.

Do not restrict the roster to the six 1989-supported series after seeing support.

Do not use the fitted-output example as a substitute for the separate 22-colony Dryad raw-count contract.

## Meaning

This is a support failure of the frozen JARA route, not evidence for or against decline concentration.

The 22-colony Dryad raw-count route remains separately eligible if its exact CSV can be retrieved under its own frozen contract.
