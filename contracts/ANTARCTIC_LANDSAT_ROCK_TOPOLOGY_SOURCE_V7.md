# V7 — Landsat rock topology repair and original source genealogy (independent geography)

Frozen 2026-10-26 **after seeing only V6 source-geographical result** (366,106 source rock shapefile features; 1,344 invalid features overlapping at least one candidate-site 2km bounding box; 4,940 potentially affected AADC site IDs). **No animal P/A/NR, counts or colony outcomes are opened in V6 or this V7.** V6 original JSON remains unchanged.

## Why source-only V7 is needed

The V6 geographic QC used an intentionally cautious veto: ANY invalid polygon whose
bbox was within 2km of a site marked that site HOLD. This cannot quantify map coverage:
invalid shapes need not actually lie within the site radius, and pyshp/Shapely may
be able to recover the polygon topology. Source-quality failures must not be counted
as ecological habitat absences.

## Deterministic and source-blind geometry rule

- Read all 366,106 original v7.3 source features in published order; read actual DBF
  source attributes as well as geometry, verifying the original projection and ZIP
  SHA V6 **7eb0cae84016b758c98a61977c90d0a8c2c6450c4bf82433e08d03ef2e5a4a5a**.
- Candidate 7,785 original AADC 2025 reference points and 2021 source memberships
  frozen as before; only AADC original geographic workbooks downloaded.
- Use exact native Shapely Polygon/MultiPolygon for valid source geometries.
  For every invalid feature whose bbox intersects the original 2km candidate-site
  search envelope, apply exactly **shapely.make_valid** (no hand drawing, snap,
  buffer(0), radius tuning or manual source alias). Retain only polygonal area
  components when the result is GeometryCollection and separately count nonpolygon
  remnants. NEVER claim automatically repaired boundaries are verified field rock.
  If no valid area is recovered, hold all candidate sites possibly touched.
- Two output tiers PER SITE, always separate:
  A: source original **native-valid polygon** exact/near/gap counts;
  B: source original + topology-repaired candidate polygons exact/near/gap,
  recording whether a repaired feature influences the site result.
- Preserve original raw `Source` and `GRIDCODE` if present and discover possible
  MANUALLY-DERIVED vs LANDSAT-8-AUTOMATED provenance. **Do not assume every v7.3
  rock polygon is independent Landsat imagery**, because missing scenes were
  filled from manual ADD source maps. Where a source attribute cannot be
  unambiguously interpreted, flag provenance as UNKNOWN. No post-result
  preferential selection of one feature-origin category to make a pattern.
- Keep original coverage classes (exact inside 1/multiple; <=250m near; >250m
  and <=2000m near; >2km) and original-site geographic label/era strata.
  No biological observation rows, occurrence labels, image changes, drift rates
  or cross-ecosystem conclusion may be analyzed in this step.

## Scientific decision

V6 raw-source 694 unvetoed rock-point intersections were a **lower support
bound**, not map-wide exposed-rock coverage. V7 determines whether original
source-invalid polygons can be used under an explicit provenance-tagged
geometry-repair sensitivity. Even if more candidate geographic sites are
covered, this does not rescind the frozen previous biology sample-stop in V1–V5:
new biology requires an independent observed field programme and its own
source/date/precision support gate.

The source's Landsat 8 classification mapping generally covers areas north
of ~82.7 S; manually derived outcrops are used where remote scenes were
unavailable (Burton-Johnson et al. 2016, doi:10.5194/tc-10-1665-2016).
Dataset CC BY 4.0: https://data.bas.ac.uk/items/178ec50d-1ffb-42a4-a4a3-1145419da2bb/ .
