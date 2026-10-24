# V38 — Official MAPPPD v5 independent published site-coordinate crosswalk

**Source-only post-V37 diagnostic, frozen 2026-10-24.** The V36 ecological results and the V37 high-resolution full-minute-location precision failure were already visible. This is NOT independent preregistration, and alternative source coordinates cannot retroactively upgrade V36's original geographically robust result.

The new Oceanites MAPPPD public read-only v5.0 API (release 2026-10-21; CC BY 4.0) publishes site_id, site_name, latitude and longitude at https://www.penguinmap.com/api/v1/sites/?region=Victoria%20Land&format=json and release information at https://www.penguinmap.com/api/v1/release/?format=json. Original observations are NEVER downloaded in V38. Numeric coordinate display precision (typically three decimals) is NOT original GPS accuracy; MAPPPD and the 2026 New Zealand Ross Sea census may share field source records/locations.

## Fixed names before any new SCAR high-resolution results
Only these ten V35 original colony sites enter. Seven are literally matching source names; three are frozen abbreviated-name comparisons and remain unconfirmed identities.
- Beaufort Island -> BEAU / Beaufort Island (exact), source original landmass Beaufort Island.
- Cape Anne -> ANNE / Cape Anne (exact), Coulman Island.
- Coulman Island Middle -> CMID / Coulman Middle (abbreviated).
- Coulman Island North -> CNOR / Coulman North (abbreviated).
- Coulman Island South -> CSOU / Coulman South (abbreviated).
- Cape Bird Middle -> BRDM / Cape Bird Middle (exact), Ross Island.
- Cape Bird North -> BRDN / Cape Bird North (exact), Ross Island.
- Cape Bird South -> BRDS / Cape Bird South (exact), Ross Island.
- Cape Royds -> ROYD / Cape Royds (exact), Ross Island.
- Inexpressible Island -> INEX / Inexpressible Island (exact), Inexpressible Island.

The original New Zealand source and exact 2026-10-24 V35 4 island-name/medium GIS IDs and 13 co-observed annual year starts are immutable. New sites, near-name fuzzy matches, site-count magnitudes, stronger coastline versions or selected years cannot be added after outcomes.

## Geographic support-only outputs
Download official source release + Victoria Land site metadata JSON over HTTPS, record SHA256 and version. Download exact SCAR ADD high-resolution coastline ZIP used by V37, DOI 10.5285/13c4d2f1-8903-4d7f-8977-592121975554, pinned source SHA256 66d82fa69f86eb8dbe8b04f01505cb2129feafec608455459ee4ed19d1dc38d4, EPSG:3031, only surface=land. Confirm exact contained one polygon / unique near within frozen 2000m / ambiguous/unmatched and distinguish Antarctic mainland largest polygon. Alternative groups must each occupy a separate original HIGHRES feature; nested colonies within Ross/Coulman are never extra independent islands.

Output (A) seven identical-name matches only, (B) all ten with three explicitly abbreviated-site aliases, (C) A exact-center plus hypothetical 250m and 1000m full circle containment. Recompute only V35 frozen original same-colony year-to-year OBSERVATION AVAILABILITY under each scenario. Support threshold for later **separately frozen** field-location validation: >=3 geographically distinct source-named polygons each with >=5 original adjacent years, plus >=8 V35 co-observed annual start years with >=2 islands. Even when this passes, no bird effect, statistical p-value or causal geographic mechanism can be claimed from coordinates with UNKNOWN original location error. A 250m/1000m circle is a diagnostic, not a verified field GPS uncertainty.

V36 original mixed Ross Sea response, V37 no-precision-robust conclusion, V27 negative broad synchrony gate and Ecology PR189 are unchanged.
