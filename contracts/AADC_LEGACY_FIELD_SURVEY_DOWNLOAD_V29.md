# V29 — official EDS legacy download-source gate for Antarctic multi-island nest GIS

**2026-10-26 | Source-only, before new Cape Petrel GIS or actual nest count rows.**

The new EDS public API registered the following source metadata but returned
zero objects in the *modern /eds/api/dataset/<uuid>/objects?recursive=true*
endpoints. This is **not absence of data**. The original official AADC
metadata HTML still links directly to publisher legacy \`/eds/<id>/download\`
URLs, which may return a browser attachment rather than an HTML page.

Freeze three original official EDS IDs/URLs:
- **5210**: Vestfold Islands 1972/74 versus 2017 Cape Petrel surveyed
  island × year counts and original colony-polygons; source metadata
  \`AAS_4518_Cape_Petrel_population_estimates_VestfoldIslands\`.
  Original source is uniquely informative because **surveyed and
  nonobserved 0** is explicitly distinguished from **not surveyed NA**
  in the original author workbooks. The original 1974 compiled cohort
  carries *three 1972 counts substituted for unsearched 1974 islands*:
  this is NOT independent 1974 source observation. A valid test
  must retain true field season and observation-provenance columns,
  and not impute the compiled 1974 values as 1974 visits.
- **1354**: Bechervaise Island field Adélie nesting location ZIP,
  source \`bech_nest_locations\`. One taxon/one island, partial total
  station/high precision; NOT a multi-island replicate.
- **4670** (optional earlier EDS 1737 fallback recorded separately):
  Windmill 1998/99 Frazier/Ardery/Casey Adélie colony outlines and
  flying-bird original nest points, some GPS some eyed-in sketch
  sites. Quality flags Qinfo must remain independent precision strata.

Exact link authority: \`data.aad.gov.au/metadata/records/fulldisplay/<id>\`
publisher official HTML anchor, \`https://data.aad.gov.au/eds/<n>/download\`.
These are source-supported *links*, not invented S3 object paths.
Original links were returned from the canonical publisher full metadata,
not an unrelated paper's reproductions.

First program step V29 sends a **bounded HTTP streaming request** to
each fixed original official URL. Retrieve response final URL/host,
HTTP status, content-type, content-disposition, declared bytes,
up to **128 KiB of initial bytes** and source signature (ZIP/PDF/
HTML/CSV/XLSX or unknown). If file is compressed binary and >128KiB,
**do not** attempt a full download from this probe, or assume that a
successful 200 means source records were loaded. If accessible,
a separate staged V30 ZIP/file manifest gate can download only original
publisher blobs below a fixed bounded size and enumerate filenames,
before bird survey values are read.

No AADC animal population counts/occupancy values, source colony geometries,
photo imagery or ecological effects are read in V29. Any redirect to an
unapproved host, auth/login/HTML interstitial, 404/403 or unbounded response
is an explicit source access HOLD, not evidence no colony survey exists.
Any successfully accessible current original file edition must be
SHA256-receipted before ecological effect fitting.

The very important scientific advance is an original **multi-island
surveyed absence frame** independent of recent Adélie GIS source,
not another regression on already viewed BAS/SSI spatial clustering.
Do not revive the failed SSI universal DEM terrain model by retuning.
