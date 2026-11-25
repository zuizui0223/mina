# V13 original polygon footprint × mapped physical landmass (correct namespace)

**Source-location-only correction after V12.** V12 original `IS_<id>` survey identifiers had **zero matches** to an entirely different AADC 2025 geographic-site registry's `geog_site_id`. Never fabricate an ID join, infer a missing island, or use a nearest-location matched biological observation.

Use the 28 original published AADC `IS_<id> × year` polygon-derived bounds already source-receipted in V10, without reading bird P/A/NR counts. Use the original v7.12 high-resolution SCAR land features, exact SHA `66d82fa69f86eb8dbe8b04f01505cb2129feafec608455459ee4ed19d1dc38d4`, EPSG3031.

- **Tier A (strict):** The full axis-aligned bounding rectangle of each authentic V10 mapped colony polygon union must be entirely covered by **exactly one** published land feature polygon. If so, the entire mapped colony geometry *must* lie in that same land feature. No spatial buffer, coastline adjustment or source ID inference.
- **Tier B (diagnostic only):** If Tier A fails, locate the bounding-rectangle centre in exactly one mapped land feature. Classify as *CENTER_ONLY_PROVISIONAL*; do not count as verified same-island assignment. If the box intersects multiple original land polygons or source land's ice front, remain unresolved.
- **Site-level strict assignment:** All seasons of the same `IS_<id>` must independently pass Tier A and have the same parent polygon ID. A single missing/mismatch season makes the site classification HOLD. If original feature coverage is geometrically questionable, do not tune tolerance to recover more sites.
- Report two survey groups HBE/HBW and source IDs; do not equate land feature to official named island or infer independent regional climate forcing. The largest land polygon is continental proxy, not isolated island.
- Original mapped colony boundaries are observational data and V10/V11 endpoints have been seen; **this is a post-outcome descriptive source-location check, not a new blind causal test**.
- No population counts, reoccupancy, movement, colonization, field GPS or AADC P/A models. Do not force any association from these 13 sites.
