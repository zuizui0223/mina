# Ledda Bay is not a single fixed coordinate: pre-ice spatial-support audit

**2026-10-08 / PR #195 / exploratory, no ice-class outcomes or new penguin data in this audit.**

## Direct cross-publication inconsistency

- LaRue et al. (2024) author site table at pinned GitHub commit `13f71112da43c1fd082273677757b41c550457ed`, `data/colony_attributes.csv`, has `LEDD, Ledda Bay,-74.228,-130.784`.
- Fretwell et al. (2021), Table 2, doi:10.1002/rse2.176, lists Ledda Bay as **-74.272, -131.243**.
- Geodesic center-to-center distance (haversine Earth radius 6371.0088 km) is **~14.69 km**. The two closed radius-5-km footprints do not intersect; the existing PR195 primary ice extraction around LaRue's centroid cannot be assumed to characterize Fretwell's reported site.

**Do not assert that the colony actually moved 14.69 km.** Publication-level records may be based on different survey moments, changing aggregation footprints, site representations, geocoding conventions, or older reference databases. Neither printed coordinate is a digitized, 2011/2014 nest polygon.

## Why this matters for the new mechanism

The physical-ice-versus-bird-use question is vulnerable to **spatial support aliasing**: a positive class-4 pixel 3 km around a reference centroid is not evidence that the actual season's nesting footprint was accessible. Conversely, class-0 there cannot prove all of Ledda Bay lacked breeding platforms.

This is a more serious confound than measurement noise if colonies shift among local options. It distinguishes two claims:

1. Physical raster state at a predeclared geographic point (**measurable**).
2. Physical accessibility at the historical or contemporaneous breeding aggregation (**not identified without a dated nest polygon**).

Failure to match these would make a strong apparent environmental relationship biologically irrelevant, without any social avoidance being involved.

## Precommitted and non-optional sensitivity

The original PR195 `EMPEROR_LEDDA_2011_2014_INDEPENDENT_FASTICE_PIXELS_V1.json` primary analysis remains frozen at LaRue's centroid. This addendum, fixed **before ice values were inspected by this new audit route**, requires the same dated independent Fraser/Massom v2.2 composites (2011 primary index 16, 2014 primary index 18), same 1/3/5 km radii, using the separately published Fretwell centroid as a **secondary spatial sensitivity**. No sliding along shore, no re-centering on penguin guano, and no favorable-coordinate selection.

Interpretation by outcome:

| Independent physical-ice result | Allowed conclusion |
|---|---|
| Both centroids agree across fixed radii/composites | Raster **coordinate sensitivity** is reduced, but successful breeding, continuous ice and actual absence remain unknown |
| Centroids disagree | **HOLD:** spatial-support uncertainty, not demonstrated penguin relocation or social preference |
| Neither archive can sample both centroids under fixed rules | **HOLD:** no physical-vacancy conclusion |

Even a coordinate-robust image-scale fast-ice classification would not identify a cause. A causal social/colonization test additionally requires independently located nesting footprints, repeated within-season nondetections corrected for effort, breeding success, and ideally marked immigration or initial breeding origins. The original image “no” code conflates physical ice loss with no visible birds.

## Evidence and reproduction

- Frozen secondary sensitivity: `contracts/EMPEROR_LEDDA_TWO_CENTROID_SENSITIVITY_PRE_ICE_V1.json`
- CSV-backed audit: `scripts/audit_ledda_two_published_centroids_v1.py`
- Fail-closed tests and CI: `tests/test_ledda_two_published_centroids_v1.py` and `.github/workflows/emperor-ledda-centroid-source-audit-v1.yml`
- Source: https://github.com/davidiles/EMPE_Global/blob/13f71112da43c1fd082273677757b41c550457ed/data/colony_attributes.csv
- Independent printed site coordinate: https://doi.org/10.1002/rse2.176
- Physical dataset: https://doi.org/10.26179/5d267d1ceb60c

**Submission separation:** frozen Ecology PR #189 untouched. This is a measurement-validity advance, not a newly identified Antarctic island causal effect.
