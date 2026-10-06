# Torgersen physical crosswalk / Palmer EDI v8 retrieval audit — decision v1

**Status:** closed access/provenance route. No physical-polygon ↔ LTER colony_code crosswalk is claimed.

## What was resolved

Cimino et al. (2025) used Palmer LTER census revision:

- DOI: `10.6073/pasta/805f6b97593c60cfdfd02266db9ab4b6`
- package: `knb-lter-pal.87.8`
- uploaded: 2022-05-07
- title: *Adelie penguin area-wide breeding population census, 1991-2021*
- historical data entity:
  `https://pasta.lternet.edu/package/data/eml/knb-lter-pal/87/8/c64b0c7ef7fd2ff4404dd22c204239de`
- DataONE index metadata:
  - fileName: `D87_AdeliePenguinCensus.csv`
  - format: text/csv
  - size: 48,046 bytes
  - isPublic: true
  - readPermission includes public

## Retrieval outcome

Direct PASTA data-package and entity endpoints return HTTP 403 to public access.

DataONE indexes the historical entity and marks it public, but both direct object/meta retrieval and the DataONE resolve endpoint repeatedly return HTTP 500 service failures.

Therefore the v8 bytes cannot currently be recovered through the tested public programmatic routes.

## Current-version mismatch

The frozen current ERDDAP source used elsewhere in mina is not numerically interchangeable with the physical Torgersen reconstruction.

For 1993, the current ERDDAP source gives:

- Torgersen (TOR): **2,868 pairs**, 17 colony_code rows.

Cimino et al. (2025) report for the 23 physical historic Torgersen sub-colonies:

- north-facing: 5,018 pairs;
- south-facing: 2,237 pairs;
- total: **7,255 pairs**.

Other current ERDDAP island labels in 1993 do not account for this difference:
- Christine 1,169;
- Cormorant 661;
- Humble 1,048;
- Litchfield 485.

A count-based attempt to match the five 2022 active physical sub-colonies to current LTER colony_code values also failed.

## Interpretation

The evidence is sufficient to reject the shortcut:

> Palmer LTER `colony_code` = Cimino physical sub-colony polygon.

The public current census and the physical reconstruction have different observational/spatial units and/or historical data treatment.

## Decision

1. **Do not** merge current LTER colony_code trajectories with Cimino physical polygons.
2. **Do not** use count equality to construct a crosswalk.
3. Retain Cimino et al. (2025) only as **independent physical-patch evidence**:
   - 23 historic physical sub-colonies → 5 active in 2022;
   - extinction structured by size and snow-related topography/aspect.
4. If revision-8 raw bytes later become accessible, any crosswalk requires a fresh provenance audit before biological effects are tested.
5. No further endpoint or URL tuning is opened on this route now.

This closure does not affect the Palmer/Signy concentration analyses because they operate on their own frozen monitoring-component definitions.
