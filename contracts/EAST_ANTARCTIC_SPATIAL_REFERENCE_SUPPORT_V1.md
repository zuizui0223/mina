# East Antarctic coastal spatial-reference support v1

**Status:** structural pre-effect audit only.

## Source
Australian Antarctic Data Centre:
*A spatial reference system for coastal ice-free land in East Antarctica*
metadata ID: AAS_4088_Spatial_reference_system_coastal_east_Antarctica
DOI: 10.26179/53YK-8Z83.

## Purpose
Attach geographic coordinates and region structure to Geog_Site_ID in the direct
Adélie occupancy database without using occupancy outcomes.

## Gate
Support passes if the public package contains:
- a stable geographic-site identifier;
- latitude/longitude or geometry;
- at least 20 geographic sites;
- a deterministic identifier relation usable with Geog_Site_ID.

No occupancy values are read in this route.
