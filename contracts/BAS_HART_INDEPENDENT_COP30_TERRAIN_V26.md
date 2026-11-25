# V26 — independently mapped terrain at genuine South Sandwich penguin nests

**Freeze: 2026-10-26 after V20–V25 original nest-coordinate geography and
spatial-response results were already examined.** This is a new
**terrain-source acquisition**, not a preregistered biological test.
All subsequent species–terrain comparisons are **exploratory** and may not
be interpreted as independent prospective confirmation of the V21/V22
same-field-mosaic spatial segregation pattern.

## Why this can advance island ecology

The BAS Hart nest points (122,139 observed located nest-number records,
10 original species CSVs, four survey localities in three provisional named
physical islands) show very strong conspecific nearest-neighbour clusters
relative to an exchangeable-label null. V22 already showed that some of
this simply reflects 100m-scale original species patch mosaics. **Geographical
source and survey imagery artifacts remain plausible.** To evaluate an
independently measured candidate *environmental filter*, extract a global
surface elevation dataset rather than fitting additional random spatial
label shuffles to an assumed complete habitat survey.

## Fixed independent environment source and source geometry

Copernicus DEM GLO-30 Public (2021 static global DSM/COG), published by
Copernicus/ESA and mirrored under the official public AWS registry.
Source reference: https://registry.opendata.aws/copernicus-dem/ ;
licence/citation: Copernicus Digital Elevation Model, DOI
10.5270/ESA-c5d3d65. It is a **surface elevation model**, not mapped
nest-bearing bare rock or true surveyed vacant habitat.
Original COG tiles are 1x1 degree, WGS84 lat/lon, accessible through
https://copernicus-dem-30m.s3.eu-central-1.amazonaws.com/ .

Frozen original geographic tile candidates from observed original
source nest bounding boxes **prior to fitting terrain responses**:
- Ashen Hills, Saunders candidate island: \`Copernicus_DSM_COG_10_S58_00_W027_00_DEM\`.
- Bellingshausen, Beach Point and Hewison Point: \`Copernicus_DSM_COG_10_S60_00_W028_00_DEM\`.

Validate both actual tile names in the real AWS GLO30 publisher
\`tileList.txt\` source index before fetching. If missing/unpublished,
set SOURCE_TILE_HOLD, do not fabricate an alternate DEM value, dynamically
switch to another DEM provider post result or silently use ocean=0.

Use SHA256 of the actual two publisher COG source files plus tileList.
Read no nest CSVs again. Only original V20 signed original coordinate
NPZ and V20 receipt are allowed to localize sample cells. Preserve V20
ten exact original species source SHA receipts unchanged. Labelled species
are not used to choose COG spatial tiles or correct geographic points.

For every original unique located nest point, spatially sample
- original DSM pixel elevation metres (no filling nodata from sea/nearby);
- **approximately 30m-pixel-scale** terrain slope from centred 3x3
  DEM elevations using source lat/lon cell dimensions in metres.
Record nodata/off-tile/edge percentages by fixed four localities,
especially ocean-zero elevations that may indicate georegistration
disagreement. Never turn missing DEM raster into habitat absence.

Use original available **UTM EPSG:32726 nest coordinates** for site
geography, but sample Copernicus geographic COG in WGS84 EPSG:4326
after explicit CRS transformation. Compute horizontal metric scales
from local WGS84 geodesic one-cell x/y distances, not angle degrees as
if they were metres.

Output small original environmental QA JSON and per-locality
source-receipted **derived UTM nest + DSM elevation/slope arrays** NPZ.
No third-party source COG binary shall be checked into git.
No numerical species–habitat association is fitted in V26.

## Frozen next ecological question — only after exposure source gate

Condition on the **same physical source localities** and original
countable source taxa. Do original species within-locality elevation/slope
distributions differ consistently between geographically separated islands,
beyond mere geographic covariation? Fix the binary comparative subcohort to
Adélie vs Chinstrap at Ashen, Bellingshausen, Beach and Hewison *without*
discarding another species because of effect size. Multi-species Ashen's
Gentoo/Macaroni are separate exploratory species profiles.
Use local original source patch grid as holdout, not random nest-level CV;
each locality or provisional island is an effective replicate, never
tens of thousands of independent islands.

Even positive terrain association does not distinguish slope/nest preference
from availability without independently measured *all surveyed suitable
and unsuitable 2019/20 breeding substrate*, exact orthomosaic masks,
camera angle, or surveyed absence. V23–25 source imagery attempts have
not retrieved validated raster footprints. Do not label nesting co-location,
species spatial patches and DSM predictions as interspecific competition,
Allee mechanism, dispersal, or a global island-speciation law.

The South Sandwich islands are **sub-Antarctic** analogues north of 60°S
and NOT Antarctic Treaty-continent sampling blocks. Larger island
biogeography needs separate Antarctic source region/years and globally
harmonized physical-island and functional-habitat layers.
