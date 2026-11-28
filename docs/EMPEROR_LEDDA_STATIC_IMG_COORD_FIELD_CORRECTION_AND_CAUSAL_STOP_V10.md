# V10: original LaRue img_lat/img_long repeats historical colony coordinates — not independent images

**2026-10-08 / PR195.** A correction to the previous image-georeference hypothesis, not a new biological effect.

## What the actual source says

The exact original LaRue et al. 2024 XLSX (git blob `a964360e2cc9bc6303199e0971a4e7d40f793752`) contains ten annual `LEDD` image records (2009–2018). In **all 10**:

- `img_lat = -74.228`
- `img_long = -130.784`

These coordinates **exactly equal** the fixed `LEDD` entry `lat=-74.228, lon=-130.784` in the separate original author `data/colony_attributes.csv`, pinned commit `13f71112da43c1fd082273677757b41c550457ed`.

GitHub Actions source-pinned original workbook reruns:
- [original ten row location values](https://github.com/zuizui0223/mina/actions/runs/37774997890) — success, 2014 site code no on Oct 13.
- [source static site table](https://github.com/davidiles/EMPE_Global/blob/13f71112da43c1fd082273677757b41c550457ed/data/colony_attributes.csv).

**Therefore this source has no independently varying dated per-image geographic coordinates for Ledda.** These columns may be repeated site lookups, fixed nominal image targets, or another form of coarsened location metadata. They cannot be promoted to verified image *scene footprint*, nesting area or penguin group position. Prior mention of them as '2014 scene center' was inaccurate; the actual scene-center role is **UNVERIFIED**. A static position field does not show ten-year penguin site fidelity, and inability to observe position change is not evidence of no movement.

The 14.692-km separation between this fixed source coordinate and Fretwell et al. 2021's `-74.272,-131.243` remains a cross-publication label discrepancy, but **cannot be resolved by repeating the LaRue img_lat/img_long columns**. Nor is it an observed 14.692-km animal movement event.

## How much this matters beyond Ledda

`contracts/EMPEROR_LARUE_GLOBAL_IMG_COORDINATE_IDENTITY_AUDIT_V1.json` fixes a **599 original row/2009–2018** crosswalk against the exact original author static colony coordinate table, to determine what fraction of the global `img_lat/img_long` pairs is reused stationary metadata and what fraction, if any, carries independent observation-level geographic variation. A source-pinned GitHub workflow reports all classes including NA/zero and site mismatch, without fitting ecological effects. Until it passes, DO NOT claim that ALL Antarctic colonies share the Ledda static-coordinate limitation.

The important generalizable study-design problem is source **spatial support** — not a newly discovered colony behavioral mechanism.

## Stop conditions for causal island ecology

- Do not reinterpret `bpresent=no` as an extinct local breeding patch; LaRue code includes no-ice conditions.
- Do not reinterpret `bpresent=yes` as verified successful fledging or confirmed nesting location.
- The independent physical MODIS class4 series at the two historically printed centroids is valid *for those geographic buffers* but does not identify annually chosen colony footprint.
- The source-mapped 2014 last-preimage class4 state is still LaRue 0/28 versus Fretwell 30/30 at 3km, and the discrepancy remains at 1/5km. However, which point represents actual nesting area remains **unknown**.
- The independent Zhang/Li 2020 '2014' site name has no confirmed original feature/date accessible through the currently audited official download route; geodoi archive access HOLDS. That list cannot prove 2014 same-day birds.
- The long-term core question — whether usable reproductive options remain vacant after perturbation due to social fidelity, movement cost or first-breeding limitation — still requires **actual dated breeding footprints, survival/success and ideally marked founders**. A site-georeference audit alone cannot establish cause.

Source-priority consequence: End the single Ledda Bay mechanism hunt after the global coordinate-role audit unless there is an independent dated 2014 breeding-location polygon, rather than repackage data aliasing as novel island biogeography. No change to frozen Ecology PR189.
