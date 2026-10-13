# V13: independent 2011 digitization sensitivity (pre-result design)

The original 2011 historical source `mac_and_chinstrap_colony_boundaries_2011.dbf` was inspected only at HEADER level, yielding **506 records**, fields `species` (C, 50) and `area` (N, 19.11). Exact 2011 historic geometry and field values remain unread as of this design.

The source dictionary explicitly says CPE = chinstrap and MPE = macaroni. The same-image 2011 source is *Lynch et al. 2016*, a separately published interpretation, not a different survey. Freeze the label crosswalk strictly to CPE and MPE, normalized by whitespace and case only; stop if any other labels occur. No value-dependent remapping or threshold changes allowed.

Pre-committed diagnostics to run on the same source-projected geometry and common 2011/2016 original-image cloud-free mask:
1. Jaccard (intersection/union) separately for old vs updated 2011 chinstrap and macaroni polygons;
2. actual-year 2011→2016 E and reverse F under the updated 2011 map and the original Lynch 2011 map, holding **2016 polygons and the common union-based geographic evaluation support constant**;
3. original polygon counts by CPE/MPE, checked CRS and recorded SHA256 file provenance;
4. either alternative finding must be reported. There is no primary p-value, no reproductive outcome, and no inference that either interpretation represents actual colony recruitment.

If source original 2011 geometry disagrees sharply, withdraw exact-site inheritance claims until measurement/digitization bias is resolved. All tests are exploratory after the 2026-10-13 V10 E observation.
