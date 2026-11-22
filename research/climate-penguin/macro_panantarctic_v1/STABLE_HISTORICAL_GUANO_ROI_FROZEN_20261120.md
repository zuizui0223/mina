# Historical recurrent-guano fixed ROI specification

Frozen before evaluating post-2013 spectra or polynya outcomes for this ROI.
The previously inspected Ardley pixels and three-site QA pilot are known prior work.

- Historical breeding seasons 1996 through 2012 inclusive, original 88-site roster.
- Site support requires at least 10 distinct seasons with published good guano records.
- A coordinate is retained when good positive guano was recorded in at least 80% of those site seasons, with at least eight distinct positive seasons. Repeated images within a season count once.
- Coordinates come from original EPSG:3031 POINT geometry. The same site/cell identifier must not map to conflicting coordinates. Distinct IDs at an identical coordinate are deduplicated.
- A missing source pixel-year is unknown. Because the publication stores preselected positive pixels, the denominator is available site seasons, not independently verified clear observations of each pixel. This is recurrence of published detections, not estimated guano occupancy or classification accuracy.
- Retain and publish every original site's denominator and exclusion reason. No thresholds will be relaxed after looking at future responses. An additional 14/17-calendar-season count may be reported as descriptive stricter support, without replacing the primary rule.
- Post-2013 source support is assessed in November–following February, seasons 2013–2021. Use original Landsat 8 C2 source QA_PIXEL and QA_RADSAT, excluding fill/cloud/cirrus/shadow/snow/water/saturation/terrain occlusion. Multiple historical points landing in the same native scene pixel count once.
- First perform QA support on the fixed pixels. For ecological analysis, sites require repeated seasons; pixel counts are not independent ecological sample sizes. Historical recurrence does not prove present guano or present isotope accuracy.
- Any later optical index must use the separately established L8 calibration and retain measurement/coverage sensitivities. No selection of pixels, years, radii or thresholds by the sign or significance of the polynya coefficient.

This implements the user's proposed fixed-location test. The prior requirement for external new-year masks is not imposed as an absolute prerequisite to this sensitivity analysis. Its inference is explicitly conditional on the persistence of the historical guano footprint.
